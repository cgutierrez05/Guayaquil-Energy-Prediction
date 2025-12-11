import pandas as pd
import os
from clean_functions import *

DATA_PATH = "./data_raw/FACTURACION/"
OUTPUT_PATH = "./data_clean/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def clean_value(val):
    #Convierte texto 1.234,56 a float 1234.56
    if pd.isna(val): return 0.0
    s = str(val).strip()
    if not s: 
        return 0.0
    
    # Quitar caracteres que no son numeros
    s = s.replace("%", "").replace(" ", "")
    
    # Manejo de formatos con punto y coma
    if "." in s and "," in s:
        s = s.replace(".", "")  
        s = s.replace(",", ".")  
    elif "," in s:
        # Solo coma decimal
        s = s.replace(",", ".")
        
    try:
        return float(s)
    except:
        return 0.0

def process_facturacion(file):
    print(f"[PROCESANDO] {os.path.basename(file)}...", end=" ")
    
    ext = file.split(".")[-1].lower()

    if ext == "ods":
        df = pd.read_excel(file, engine="odf")
    else:
        df = pd.read_csv(file, sep=";", encoding='latin1', low_memory=False)

    df.columns = df.columns.str.strip()

    col_mwh = None
    for col in df.columns:
        if "MWh_GYE" in col:
            col_mwh = col
            break
        elif "MWh GYE" in col:
            col_mwh = col
            break
    
    if col_mwh is None:
        print(f"[ERROR] No se encontró columna MWh_GYE en {file}")
        return None

    df[col_mwh] = df[col_mwh].apply(clean_value)
    
    consumo = df[col_mwh].sum()
    
    # Extraer año y mes del nombre del archivo
    year, month = extract_year_month(os.path.basename(file))
    if year is None or month is None:
        print(f"[ALERTA] No se pudo extraer fecha de {file}")
        return None
    
    # Crear fecha como datetime
    date = pd.to_datetime(f"{year}-{month:02d}-01")
    
    print(f"[OK] Consumo: {consumo:,.0f} MWh")
    
    return pd.DataFrame({
        "date": [date],
        "consumo_mwh": [consumo]
    })

# --- BLOQUE PRINCIPAL ---
clean_list = []
if not os.path.exists(DATA_PATH):
    print(f"[ERROR] La carpeta {DATA_PATH} no existe.")
else:
    files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith((".csv", ".ods"))]
    print(f"--- Iniciando limpieza de {len(files)} archivos ---")

    for file in files:
        full_path = os.path.join(DATA_PATH, file)
        df = process_facturacion(full_path)
        if df is not None:
            clean_list.append(df)

    if clean_list:
        df_final = pd.concat(clean_list, ignore_index=True).sort_values("date")
        
        # Marcar datos atípicos por apagones (2024) y años incompletos (2021-2025)
        df_final["flag_atipico"] = (df_final["date"].dt.year >= 2024).astype(int)
        df_final["flag_atipico"] = (df_final["date"].dt.year == 2021).astype(int)

        # Guardar el archivo limpio
        output = os.path.join(OUTPUT_PATH, "facturacion_gye_clean.csv")
        df_final.to_csv(output, index=False)
        print(f"\n[EXITO] Archivo guardado en: {output}")
        print(f"Datos procesados: {len(df_final)} meses")
    else:
        print("\n[FALLO] No se generaron datos.")