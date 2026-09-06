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

CARPETA_SALIDA = r"C:\ECONOMETRIA_BVC"


@st.cache_data
def cargar_ultima_matriz():
  """Busca y carga automáticamente la matriz Excel más reciente."""
  try:
    archivos = [
        os.path.join(CARPETA_SALIDA, f)
        for f in os.listdir(CARPETA_SALIDA)
        if f.startswith("Matriz_XTB_2") and f.endswith(".xlsx")
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


# Título principal
st.title("🚀 Radar Cuantitativo de Oportunidades - XTB")
st.markdown(
    "Panel interactivo para la gestión de ingresos adicionales y análisis"
    " multitemporal (1D + 4H + 1H)."
)

# Cargar datos
df, nombre_archivo = cargar_ultima_matriz()

if df is None:
  st.warning(
      "⚠️ No se encontró ningún archivo de matriz en la carpeta"
      f" {CARPETA_SALIDA}. Ejecuta tu script generador primero."
  )
else:
  st.sidebar.success(f"📁 Archivo activo: **{nombre_archivo}**")

  # Detectar dinámicamente la columna de decisión o dirección
  col_decision = None
  for c in ["Decisión Final", "Dirección", "Tipo Movimiento"]:
    if c in df.columns:
      col_decision = c
      break

  # --- FILTROS EN LA BARRA LATERAL ---
  st.sidebar.header("🔍 Filtros de Visualización")

  # Filtro por Categoría
  cat_col = "Categoría" if "Categoría" in df.columns else df.columns[0]
  categorias = ["Todas"] + list(df[cat_col].unique())
  cat_seleccionada = st.sidebar.selectbox("Seleccionar Categoría", categorias)

  # Filtro por Tipo de Decisión / Oportunidad
  if col_decision:
    decisiones = ["Todas"] + list(df[col_decision].unique())
    dec_seleccionada = st.sidebar.selectbox("Tipo de Decisión / Dirección", decisiones)
  else:
    dec_seleccionada = "Todas"

  # Aplicar filtros
  df_filtrado = df.copy()
  if cat_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado[cat_col] == cat_seleccionada]
  if dec_seleccionada != "Todas" and col_decision:
    df_filtrado = df_filtrado[df_filtrado[col_decision] == dec_seleccionada]

  # --- MÉTRICAS SUPERIORES (KPIs) ---
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Activos Analizados", len(df))
  col2.metric("Activos Filtrados", len(df_filtrado))
  
  if col_decision:
    compras_count = len(df[df[col_decision].astype(str).str.contains("COMPRA", case=False, na=False)])
    ventas_count = len(df[df[col_decision].astype(str).str.contains("VENTA", case=False, na=False)])
  else:
    compras_count, ventas_count = 0, 0

  col3.metric("Oportunidades Compra", compras_count)
  col4.metric("Oportunidades Venta", ventas_count)

  st.markdown("---")

  # --- PESTAÑAS DE VISUALIZACIÓN ---
  tab1, tab2, tab3 = st.tabs([
      "🎯 Radar Operativo",
      "📈 Tabla Completa de Matriz",
      "💡 Gestión de Riesgo ($3 USD)",
  ])

  with tab1:
    st.subheader("Clasificación de Oportunidades en Tiempo Real")

    # Columnas clave adaptadas
    cols_radar = [c for c in [cat_col, "Activo", "Ticker", "Precio Actual", col_decision, "RSI 1H", "Lotes ($3 Risk) EST."] if c in df.columns]

    if col_decision:
      # Cuadrante 1: Compras
      st.markdown("### 🟢 Oportunidades de Compra")
      df_compras = df_filtrado[df_filtrado[col_decision].astype(str).str.contains("COMPRA", case=False, na=False)]
      if not df_compras.empty:
        st.dataframe(df_compras[cols_radar], use_container_width=True)
      else:
        st.info("No hay compras en los filtros seleccionados.")

      # Cuadrante 2: Ventas
      st.markdown("### 🔴 Oportunidades de Venta")
      df_ventas = df_filtrado[df_filtrado[col_decision].astype(str).str.contains("VENTA", case=False, na=False)]
      if not df_ventas.empty:
        st.dataframe(df_ventas[cols_radar], use_container_width=True)
      else:
        st.info("No hay ventas en los filtros seleccionados.")
    else:
      st.dataframe(df_filtrado, use_container_width=True)

  with tab2:
    st.subheader("Matriz Completa de Datos Técnicos")
    busqueda = st.text_input("Buscar Activo o Ticker:", "")
    if busqueda and "Activo" in df.columns:
      df_busqueda = df_filtrado[
          df_filtrado["Activo"].str.contains(busqueda, case=False, na=False)
          | df_filtrado["Ticker"].str.contains(busqueda, case=False, na=False)
      ]
      st.dataframe(df_busqueda, use_container_width=True)
    else:
      st.dataframe(df_filtrado, use_container_width=True)

  with tab3:
    st.subheader("Calculadora de Posición y Riesgo")
    lote_col = [c for c in df.columns if "Lote" in c or "Risk" in c]
    activo_col = "Activo" if "Activo" in df.columns else df.columns[1]
    
    if not df_filtrado.empty and lote_col:
      st.markdown("##### Resumen de Lotes Sugeridos por Activo")
      st.bar_chart(df_filtrado.set_index(activo_col)[lote_col[0]].head(15))
    else:
      st.warning("No hay suficientes datos de lotes para mostrar el gráfico.")