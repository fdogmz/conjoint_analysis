import streamlit as st

st.set_page_config(
    page_title="Conjoint Analysis App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Aplicación de Análisis Conjunto (Conjoint Analysis)")
st.markdown(
    """
Esta app multipágina te guía por un flujo completo de análisis conjunto:

1. Introducción al problema y atributos.
2. Metodología de diseño y levantamiento.
3. Exploración de datos sintéticos.
4. Modelado individual de part-worths con OLS.
5. Simulación de mercado con regla First-Choice.
"""
)

st.info("Navega desde la barra lateral para abrir cada página del análisis.")

with st.expander("Detalles técnicos del proyecto"):
    st.markdown(
        """
- **Arquitectura:** `streamlit_app.py` + `pages/` numeradas.
- **Modelado:** `statsmodels` (OLS) y `pandas` para preprocesamiento.
- **Visualización:** `plotly` para gráficos interactivos.
- **Codificación:** variables categóricas con *dummy encoding* (`drop_first=True`).
"""
    )

st.markdown(
    """
<style>
div[data-testid="stButton"] > button {
  background-color: transparent;
  color: #1f77b4;
  border: 1px solid #1f77b4;
}
</style>
""",
    unsafe_allow_html=True,
)
st.divider()
if st.button("Comenzar: Motivación ➜"):
    st.switch_page("pages/01_Motivacion.py")
