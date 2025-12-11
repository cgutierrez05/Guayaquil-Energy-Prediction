import pandas as pd
import os
from clean_functions import *

DATA_PATH = "./data_raw/FACTURACION/"
OUTPUT_PATH = "./data_clean/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def process_facturacion(file):
    ext = file.split(".")[-1].lower()

    if ext == "ods":
        df = pd.read_excel(file, engine="odf")
    else:
        df = pd.read_csv(file, encoding="latin1")

    df.columns = df.columns.str.lower().str.strip()

    # Buscar columna de Consumo GYE
    col_mwh = next((c for c in df.columns if "MWh_GYE" in c), None)
    if col_mwh is None:
        return None

    consumo = df[col_mwh].astype(str).str.replace(",", ".").astype(float).sum()
    date = extract_year_month(os.path.basename(file))

    return pd.DataFrame({
        "date": [date],
        "consumo_mwh": [consumo]
    })

clean_data = []

for file in os.listdir(DATA_PATH):
    if file.lower().endswith((".csv", ".ods")):
        df = process_facturacion(os.path.join(DATA_PATH, file))
        if df is not None:
            clean_data.append(df)

df_final = pd.concat(clean_data, ignore_index=True).sort_values("date")

# Marcar datos atípicos por apagones (2024–2025)
df_final["flag_atipico"] = (df_final["date"].dt.year >= 2024).astype(int)

output = os.path.join(OUTPUT_PATH, "facturacion_gye_clean.csv")
df_final.to_csv(output, index=False)

print("Archivo de facturación limpio generado:", output)
