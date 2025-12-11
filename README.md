# Guayaquil-Energy-Prediction
Este proyecto predice el consumo de energía eléctrica mensual en la Unidad de Negocio CNEL - Guayaquil utilizando el modelo SARIMA (Seasonal ARIMA) basado en datos históricos de facturación y producción energética nacional.

## **Tecnologías utilizadas**
- **Python** (Pandas, NumPy, Statsmodels)
- **ARIMA/SARIMA** para predicción de series temporales

## **Objetivo del Proyecto**
El objetivo es crear un modelo predictivo para **predecir el consumo de energía eléctrica** en **Guayaquil** para el próximo mes. El modelo se entrena con datos históricos de **facturación de energía** y **producción nacional** de energía eléctrica.

## **Estructura de Archivos**
- **`clean_bnee.py`**: Script para limpiar y preprocesar los datos del Balance Nacional de Energía Eléctrica (BNEE).
- **`clean_facturacion.py`**: Script para limpiar y procesar los datos de facturación de energía de CNEL - Guayaquil.
- **`clean_functions.py`**: Script que contiene funciones generales para uso en ambas limpiezas.
- **`modelo_predictivo.py`**: Script para entrenar el modelo y generar las predicciones.
- **`interfaz_prediccion.py`**: Interfaz de usuario para ingresar un mes-año y obtener una predicción de consumo de energía.
- **`data_clean/`**: Carpeta con los datasets limpios listos para usar.
- **`data_raw/`**: Carpeta con los archivos originales descargados.
