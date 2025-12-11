import pandas as pd
import os
from clean_functions import *

DATA_PATH = "./data_raw/BNEE/"
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
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
        
    try:
        return float(s)
    except:
        return 0.0

def process_bnee(file):
    print(f"[PROCESANDO] {os.path.basename(file)}...", end=" ")
    
    try:
        # Intentar leer con punto y coma (comun en estos reportes)
        df = pd.read_csv(file, sep=";", header=None, engine='python', encoding='latin1')
    except:
        try:
            # Intentar con coma
            df = pd.read_csv(file, sep=",", header=None, engine='python', encoding='latin1')
        except:
            print("[ERROR] No se pudo leer el archivo.")
            return None

    prod_total = 0.0
    fact_total = 0.0
    
    # Banderas de control (Maquina de Estados)
    buscando_prod = False
    buscando_fact = False
    
    for i, row in df.iterrows():
        # Convertir fila a texto para buscar palabras clave
        texto_fila = " ".join([str(x).lower() for x in row.values if pd.notna(x)])
        
        # 1. Detectar inicio de Seccion Produccion (aprox Seccion 3)
        if "3." in texto_fila and ("produccion" in texto_fila or "producción" in texto_fila):
            buscando_prod = True
            buscando_fact = False
            continue 

        # 2. Detectar inicio de Seccion Facturacion (aprox Seccion 6)
        if "6." in texto_fila and ("facturada" in texto_fila or "servicio electrico" in texto_fila):
            buscando_fact = True
            buscando_prod = False
            continue

        # 3. Buscar el valor 'Total' dentro de la seccion activa
        if "total" in texto_fila:
            # Extraer numeros de la fila
            valores = [clean_value(x) for x in row.values]
            # Nos quedamos con el mayor valor de la fila (el total suele ser la suma)
            posibles = [v for v in valores if v > 10] # Filtro de ruido
            
            if posibles:
                valor_hallado = max(posibles)
                
                if buscando_prod and prod_total == 0:
                    prod_total = valor_hallado
                    buscando_prod = False # Ya lo tenemos, dejar de buscar
                
                if buscando_fact and fact_total == 0:
                    fact_total = valor_hallado
                    buscando_fact = False

    # Validar fecha
    year, month = extract_year_month(os.path.basename(file))
    if year is None:
        print("[ALERTA] Nombre de archivo sin fecha valida.")
        return None
        
    date = pd.to_datetime(f"{year}-{month:02d}-01")
    
    print(f"[OK] (Prod: {prod_total:.2f} | Fact: {fact_total:.2f})")
    
    return pd.DataFrame({
        "date": [date],
        "prod_total_gwh": [prod_total],
        "energia_facturada_gwh": [fact_total]
    })

# --- BLOQUE PRINCIPAL ---
clean_list = []
if not os.path.exists(DATA_PATH):
    print(f"[ERROR] La carpeta {DATA_PATH} no existe.")
else:
    files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(".csv")]
    print(f"--- Iniciando limpieza de {len(files)} archivos ---")

    for file in files:
        df = process_bnee(os.path.join(DATA_PATH, file))
        if df is not None:
            clean_list.append(df)

    if clean_list:
        df_final = pd.concat(clean_list, ignore_index=True).sort_values("date")
        
        # Convertir GWh a MWh
        df_final["prod_total_mwh"] = df_final["prod_total_gwh"] * 1000
        df_final["energia_facturada_mwh"] = df_final["energia_facturada_gwh"] * 1000
        
        output = os.path.join(OUTPUT_PATH, "bnee_clean.csv")
        df_final.to_csv(output, index=False)
        print(f"\n[EXITO] Archivo guardado en: {output}")
    else:
        print("\n[FALLO] No se generaron datos.")