import os
import etl
import visualizer

# --- CONFIGURACION DE RUTAS ABSOLUTAS ---
# Esto evita el error "File not found" si tu terminal esta en otra carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_BNEE = os.path.join(BASE_DIR, "data_clean", "bnee_clean.csv")
PATH_FACT = os.path.join(BASE_DIR, "data_clean", "facturacion_gye_clean.csv")

def main():
    print("\n" + "="*50)
    print(" INICIANDO VISUALIZADOR DE DATOS")
    print("="*50)
    
    # Diagnostico de rutas
    print(f"Directorio base: {BASE_DIR}")
    print(f"Buscando BNEE en: {PATH_BNEE}")
    
    if not os.path.exists(PATH_BNEE):
        print("[ERROR] No encuentro el archivo bnee_clean.csv")
        print("   -> Asegurate de ejecutar primero clean_bnee.py")
        input("Presiona ENTER para salir...")
        return

    if not os.path.exists(PATH_FACT):
        print("[ERROR] No encuentro el archivo facturacion_gye_clean.csv")
        print("   -> Asegurate de ejecutar primero clean_facturacion.py")
        input("Presiona ENTER para salir...")
        return

    try:
        # 1. Cargar Datos
        print("[OK] Archivos encontrados. Cargando...")
        df_bnee_raw, df_fact_raw = etl.cargar_datos(PATH_BNEE, PATH_FACT)
        
        # 2. Limpieza Tecnica
        df_fact_clean, df_bnee_clean = etl.limpiar_errores_tecnicos(df_fact_raw, df_bnee_raw)
        
        # 3. Logica de Negocio
        print("[PROCESANDO] Aplicando correccion de apagones...")
        df_model = etl.reparar_demanda_insatisfecha(df_fact_clean)
        df_bnee_ready = etl.preparar_bnee_mensual(df_bnee_clean)
        
        # 4. Grafico
        print("[GRAFICO] Abriendo ventana de graficos...")
        visualizer.graficar_comparativa(df_model, df_bnee_ready)
        print("[OK] Grafico cerrado exitosamente.")

    except Exception as e:
        print(f"\n[ERROR CRITICO] Ocurrio un error inesperado:\n{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*50)
    input("PROGRAMA FINALIZADO. Presiona ENTER para cerrar esta terminal...")

if __name__ == "__main__":
    main()