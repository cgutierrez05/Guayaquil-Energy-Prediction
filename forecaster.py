from statsmodels.tsa.statespace.sarimax import SARIMAX

def entrenar_y_predecir(series_temporal):
    """
    Entrena SARIMA (1,1,1)x(1,1,1,12) y predice el siguiente mes.
    """
    print("\n>>> Entrenando modelo SARIMA...")
    
    model = SARIMAX(series_temporal, 
                    order=(1, 1, 1), 
                    seasonal_order=(1, 1, 1, 12),
                    enforce_stationarity=False,
                    enforce_invertibility=False)

    results = model.fit(disp=False)
    
    # Predicción
    forecast = results.get_forecast(steps=1)
    return forecast