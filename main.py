import etl
import visualizer
import forecaster

# Rutas de archivos
PATH_BNEE = "./data_clean/bnee_clean.csv"
PATH_FACT = "./data_clean/facturacion_gye_clean.csv"

def main():
    try:
        # 1. ETL: Carga y Limpieza Técnica
        df_bnee_raw, df_fact_raw = etl.cargar_datos(PATH_BNEE, PATH_FACT)
        df_fact_clean, df_bnee_clean = etl.limpiar_errores_tecnicos(df_fact_raw, df_bnee_raw)
        
        # 2. ETL: Lógica de Negocio (Reparar Apagones)
        print(">>> Aplicando corrección por apagones (2024-2025)...")
        df_model = etl.reparar_demanda_insatisfecha(df_fact_clean)
        df_bnee_ready = etl.preparar_bnee_mensual(df_bnee_clean)
        
        # 3. Visualización
        visualizer.graficar_comparativa(df_model, df_bnee_ready)
        
        # 4. Modelado y Predicción
        forecast = forecaster.entrenar_y_predecir(df_model['consumo_mwh'])
        
        # 5. Reporte Final
        pred_date = forecast.predicted_mean.index[0]
        pred_value = forecast.predicted_mean.iloc[0]
        conf_int = forecast.conf_int().iloc[0]

        print(f"\n{'='*40}")
        print(f" RESULTADO DEL MODELO PREDICTIVO")
        print(f"{'='*40}")
        print(f" Fecha a predecir:      {pred_date.strftime('%B %Y')}")
        print(f" Demanda Estimada:      {pred_value:,.2f} MWh")
        print(f" Rango probable:        [{conf_int.iloc[0]:,.0f} - {conf_int.iloc[1]:,.0f}] MWh")
        print(f"{'='*40}")

    except Exception as e:
        print(f"[ERROR CRÍTICO]: {e}")

if __name__ == "__main__":
    main()