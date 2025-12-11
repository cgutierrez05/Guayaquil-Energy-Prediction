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
    