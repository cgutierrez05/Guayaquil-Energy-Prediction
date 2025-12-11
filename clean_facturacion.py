import pandas as pd
import os
from clean_functions import *  # Suponiendo que tienes otras funciones de limpieza aquí

DATA_PATH = "./data_raw/FACTURACION/"
OUTPUT_PATH = "./data_clean/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def clean_value(val):
    # Convierte texto 1.234,56 a float 1234.56
    if pd.isna(val): 
        return 0.0
    
    s = str(val).strip()
    
    # Si la cadena está vacía, retornar 0.0
    if not s: 
        return 0.0
    
    # Quitar caracteres que no son números o punto
    s = s.replace("%", "").replace(" ", "").replace("€", "").replace("$", "")  # Se pueden añadir otros caracteres no numéricos
    
    # Si contiene punto y coma, asumir que el punto es separador de miles y la coma es decimal
    if "." in s and "," in s:
        s = s.replace(".", "")  # Eliminar el punto (separador de miles)
        s = s.replace(",", ".")  # Convertir coma a punto (separador decimal)
    
    # Si solo tiene coma, convertirla en punto decimal
    elif "," in s:
        s = s.replace(",", ".")
    
    # Intentar convertir a float
    try:
        return float(s)
    except ValueError:  # Si no puede convertir, devolver 0.0
        return 0.0

def process_facturacion(file):
    ext = file.split(".")[-1].lower()

    if ext == "ods":
        df = pd.read_excel(file, engine="odf")
    else:
        df = pd.read_csv(file, encoding="ISO-8859-1", sep=";")

    df.columns = df.columns.str.lower().str.strip()

    # Buscar columna de Consumo GYE
    col_mwh = next((c for c in df.columns if "MWh_GYE" in c), None)
    if col_mwh is None:
        return None

    # Limpiar y convertir los valores de la columna
    df[col_mwh] = df[col_mwh].apply(clean_value)  # Usamos la función clean_value aquí
    
    consumo = df[col_mwh].sum()
    date = extract_year_month(os.path.basename(file))

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
        df = process_facturacion(os.path.join(DATA_PATH, file))
        if df is not None:
            clean_list.append(df)

    if clean_list:
        df_final = pd.concat(clean_list, ignore_index=True).sort_values("date")
        
        # Marcar datos atípicos por apagones (2024–2025)
        df_final["flag_atipico"] = (df_final["date"].dt.year >= 2024).astype(int)

        # Guardar el archivo limpio
        output = os.path.join(OUTPUT_PATH, "facturacion_gye_clean.csv")
        df_final.to_csv(output, index=False)
        print(f"\n[EXITO] Archivo guardado en: {output}")
    else:
        print("\n[FALLO] No se generaron datos.")