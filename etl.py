import pandas as pd
import numpy as np
import os

def cargar_datos(path_bnee, path_fact):
    """Carga los CSVs y valida su existencia."""
    if not os.path.exists(path_bnee) or not os.path.exists(path_fact):
        raise FileNotFoundError("No se encuentran los archivos en data_clean/")
    
    print(">>> Cargando datos...")
    df_bnee = pd.read_csv(path_bnee, parse_dates=['date'])
    df_fact = pd.read_csv(path_fact, parse_dates=['date'])
    return df_bnee, df_fact

def limpiar_errores_tecnicos(df_fact, df_bnee):
    """Corrige errores de dedo, decimales y valores nulos técnicos."""
    # Corrección decimal (4.7M -> 470k)
    df_fact.loc[df_fact['consumo_mwh'] > 4000000, 'consumo_mwh'] /= 10
    
    # Valores absurdamente bajos (< 50k) a NaN
    df_fact.loc[df_fact['consumo_mwh'] < 50000, 'consumo_mwh'] = np.nan
    
    # BNEE absurdamente bajos (< 1000 GWh) a NaN
    df_bnee.loc[df_bnee['prod_total_gwh'] < 1000, 'prod_total_gwh'] = np.nan
    
    return df_fact, df_bnee

def reparar_demanda_insatisfecha(df_fact):
    """
    Business Logic: Imputa la demanda real en periodos de apagones.
    """
    df_model = df_fact.copy()
    
    # --- 1. PRIMERO: ARREGLAR DUPLICADOS ---
    # Esto modifica el tamaño del DataFrame, por eso debe ir antes de crear máscaras
    if df_model['date'].duplicated().any():
        print("   [ALERTA] Fechas duplicadas detectadas. Unificando datos...")
        # Agrupamos por fecha y sacamos el promedio de consumo y el máximo del flag
        df_model = df_model.groupby('date', as_index=False).agg({
            'consumo_mwh': 'mean',
            'flag_atipico': 'max'
        })
    
    # --- 2. SEGUNDO: CREAR MÁSCARA ---
    # Ahora que la tabla tiene el tamaño final, creamos la máscara
    mask_cortes = (df_model['flag_atipico'] == 1)
    
    # Solo intentamos calcular promedios si existen datos marcados como atípicos
    if mask_cortes.any():
        promedio_real = df_model.loc[mask_cortes, 'consumo_mwh'].mean()
        print(f"   > Promedio con cortes (Real): {promedio_real:,.2f} MWh")
        
        # Convertimos a NaN para recalcular
        df_model.loc[mask_cortes, 'consumo_mwh'] = np.nan
        
        # Configurar índice y rellenar
        df_model = df_model.set_index('date').asfreq('MS')
        df_model['consumo_mwh'] = df_model['consumo_mwh'].interpolate(method='time')
        
        # Volvemos a calcular la máscara porque al hacer set_index pudo cambiar el orden o estructura levemente
        # Pero como ya es un TimeSeries, usamos el índice temporal para ubicar los huecos que acabamos de llenar
        # Nota: Simplemente usamos la lógica de interpolación ya aplicada.
        
        # Para imprimir el promedio estimado, usamos los mismos índices que eran atípicos
        # (Requerimos re-alinear la mascara al nuevo índice si asfreq agregó meses vacíos)
        # Simplificación para visualización:
        print(f"   > Datos interpolados y corregidos exitosamente.")
        
    else:
        print("   > No se detectaron periodos atípicos (Flag=1).")
        df_model = df_model.set_index('date').asfreq('MS')
    
    return df_model

def preparar_bnee_mensual(df_bnee):
    """Asegura frecuencia mensual para el gráfico."""
    # También protegemos BNEE contra duplicados
    if df_bnee['date'].duplicated().any():
        df_bnee = df_bnee.groupby('date', as_index=False).mean()
        
    df = df_bnee.set_index('date').asfreq('MS')
    df['prod_total_gwh'] = df['prod_total_gwh'].interpolate(method='time')
    return df