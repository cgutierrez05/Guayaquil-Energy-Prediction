import pandas as pd
import os

DATA_PATH = "./data_raw/FACTURACION/"
OUTPUT_PATH = "./data_clean/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

month_map = {
    "enero":1, "ene":1,
    "febrero":2, "feb":2,
    "marzo":3, "mar":3,
    "abril":4, "abr":4,
    "mayo":5, "may":5,
    "junio":6, "jun":6,
    "julio":7, "jul":7,
    "agosto":8, "ago":8,
    "septiembre":9, "sep":9, "set":9,
    "octubre":10, "oct":10,
    "noviembre":11, "nov":11,
    "diciembre":12, "dic":12
}

def extract_date(filename):
    name = filename.lower()
    year = [y for y in range(2018,2030) if str(y) in name][0]
    month = [month_map[m] for m in month_map if m in name][0]
    return pd.to_datetime(f"{year}-{month:02d}-01")

def process_file(file):
    ext = file.split(".")[-1].lower()

    if ext == "ods":
        df = pd.read_excel(file, engine="odf")
    else:
        df = pd.read_csv(file, encoding="latin1")

    df.columns = df.columns.str.lower().str.strip()

    col_mwh = next((c for c in df.columns if "mwh_gye" in c), None)
    if col_mwh is None:
        return None

    consumo = df[col_mwh].astype(str).str.replace(",", ".").astype(float).sum()
    date = extract_date(os.path.basename(file))

    return pd.DataFrame({
        "date": [date],
        "consumo_mwh": [consumo]
    })

clean_data = []

for file in os.listdir(DATA_PATH):
    if file.lower().endswith((".csv",".ods",".xlsx")):
        df = process_file(os.path.join(DATA_PATH, file))
        if df is not None:
            clean_data.append(df)

df_final = pd.concat(clean_data, ignore_index=True).sort_values("date")

# Marcar atípicos por apagones
df_final["flag_atipico"] = (df_final["date"].dt.year >= 2024).astype(int)

output = os.path.join(OUTPUT_PATH, "facturacion_gye_clean.csv")
df_final.to_csv(output, index=False)

print("Archivo generado:", output)
