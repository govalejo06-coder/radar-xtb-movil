# app_radar.py
import os
import pandas as pd
import streamlit as st

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Radar Cuantitativo XTB",
    page_icon="📈",
    layout="wide",
)

# Carpeta actual del repositorio en la nube
CARPETA_SALIDA = "."


@st.cache_data
def cargar_ultima_matriz():
  """Busca y carga automáticamente la matriz Excel más reciente."""
  try:
    archivos = [
        os.path.join(CARPETA_SALIDA, f)
        for f in os.listdir(CARPETA_SALIDA)
        if f.startswith("Matriz_XTB_") and f.endswith(".xlsx")
    ]
    if not archivos:
      return None, None
    archivo_reciente = max(archivos, key=os.path.getmtime)
    xls = pd.ExcelFile(archivo_reciente)

    # Buscamos la hoja que contenga los datos principales de activos
    nombre_hoja = xls.sheet_names[0]
    for sheet in xls.sheet_names:
      if "Activos" in sheet or "Matriz" in sheet:
        nombre_hoja = sheet
        break

    df = pd.read_excel(archivo_reciente, sheet_name=nombre_hoja)
    return df, os.path.basename(archivo_reciente)
  except Exception as e:
    st.error(f"Error cargando la matriz: {e}")
    return None, None