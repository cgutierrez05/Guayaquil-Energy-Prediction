import pandas as pd

month_map = {
    "enero":1, "febrero":2, "marzo":3, "abril":4, "mayo":5, "junio":6,
    "julio":7, "agosto":8, "septiembre":9, "octubre":10, "noviembre":11, "diciembre":12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

def extract_year_month(filename):
    name = filename.lower()
    try:
        year = [y for y in range(2018,2030) if str(y) in name][0]
        month = [month_map[m] for m in month_map if m in name][0]
        return year, month
    except:
        return None, None
    
def clean_value(val):
    #Convierte texto 1.234,56 a float 1234.56
    if pd.isna(val): return 0.0
    s = str(val).strip()
    if not s: return 0.0
    
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