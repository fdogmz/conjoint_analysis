import streamlit as st
import pandas as pd
import plotly.express as px
# Asumiendo que tu función genera ahora 9 perfiles ortogonales en lugar de 27
from utils.conjoint import generate_synthetic_dataset 

st.set_page_config(page_title="Exploración de Datos | Conjoint", layout="wide")

# Estilo personalizado para las métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Exploración del Dataset de Preferencias")
st.markdown("Antes de modelar, validamos la calidad y la estructura de las respuestas capturadas.")

# --- Sidebar para Control de Datos ---
with st.sidebar:
    st.header("⚙️ Configuración")
    n_resp = st.slider("Número de encuestados", 15, 150, 60, 5)
    seed = st.number_input("Semilla aleatoria", 1, 9999, 42)
    
    st.divider()
    st.info("💡 **Dato:** En un diseño fraccionado, usamos menos perfiles pero mantenemos el balance estadístico.")

# Generación de datos
df = generate_synthetic_dataset(n_respondents=int(n_resp), seed=int(seed))

# --- Sección de Métricas Clave ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("👥 Encuestados", df["RespondentID"].nunique())
with m2:
    perfiles_n = df.groupby("RespondentID").size().iloc[0]
    st.metric("📋 Perfiles/Persona", perfiles_n, delta="-18 vs Full Factorial", delta_color="normal")
with m3:
    st.metric("📈 Total Observaciones", len(df))
with m4:
    st.metric("⭐ Rating Promedio", f"{df['Rating'].mean():.2f}")

st.divider()

# --- Visualización y Tabla ---
col_tabla, col_viz = st.columns([1, 1.2])

with col_tabla:
    st.subheader("🔍 Inspección de Respuestas")
    user_id = st.selectbox("Selecciona un Encuestado para auditar:", df["RespondentID"].unique())
    
    filtered_df = df[df["RespondentID"] == user_id].copy()
    
    # Resaltamos la tabla para que parezca una hoja de respuestas
    st.dataframe(
        filtered_df[["PerfilID", "Marca", "Precio", "Capacidad", "Rating"]], 
        use_container_width=True, 
        hide_index=True
    )
    st.caption(f"Auditando el set de datos del informante #{user_id}.")

with col_viz:
    st.subheader("🎯 Cobertura y Sesgo")
    tab_dist, tab_balance = st.tabs(["Distribución de Ratings", "Balance del Diseño"])
    
    with tab_dist:
        fig_hist = px.histogram(
            df, x="Rating", nbins=10, 
            color_discrete_sequence=['#636EFA'],
            labels={'Rating': 'Calificación (1-10)'},
            template="plotly_white"
        )
        fig_hist.update_layout(bargap=0.1, margin=dict(t=10, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Un histograma balanceado indica que los usuarios usaron toda la escala de preferencia.")

    with tab_balance:
        # Mapa de calor para mostrar que todas las combinaciones clave están cubiertas
        ct = pd.crosstab(df['Marca'], df['Precio'])
        fig_heat = px.imshow(
            ct, text_auto=True, 
            color_continuous_scale='Blues',
            labels=dict(x="Nivel de Precio", y="Marca", color="Frecuencia")
        )
        fig_heat.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption("Verificación de Ortogonalidad: ¿Están todas las celdas cubiertas equitativamente?")

st.divider()

# --- Análisis por Atributo ---
st.subheader("💡 Tendencias Agregadas (Lectura Rápida)")
st.write("Promedio de Rating por cada nivel de atributo:")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("**Preferencia de Marca**")
        avg_marca = df.groupby("Marca")["Rating"].mean().reset_index()
        fig_m = px.bar(avg_marca, x="Marca", y="Rating", color="Marca", text_auto='.1f', range_y=[0,10])
        fig_m.update_layout(showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_m, use_container_width=True)

with c2:
    with st.container(border=True):
        st.markdown("**Sensibilidad al Precio**")
        precio_order = ["Bajo", "Medio", "Alto"]
        avg_precio = df.groupby("Precio")["Rating"].mean().reset_index()
        avg_precio["Precio"] = pd.Categorical(avg_precio["Precio"], categories=precio_order, ordered=True)
        avg_precio = avg_precio.sort_values("Precio")
        fig_p = px.line(
            avg_precio, x="Precio", y="Rating", markers=True, range_y=[0,10],
            category_orders={"Precio": precio_order}
        )
        fig_p.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_p, use_container_width=True)

with c3:
    with st.container(border=True):
        st.markdown("**Valor de Capacidad**")
        capacidad_order = ["64GB", "128GB", "256GB"]
        avg_cap = df.groupby("Capacidad")["Rating"].mean().reset_index()
        avg_cap["Capacidad"] = pd.Categorical(avg_cap["Capacidad"], categories=capacidad_order, ordered=True)
        avg_cap = avg_cap.sort_values("Capacidad")
        fig_c = px.bar(
            avg_cap, x="Capacidad", y="Rating", color_discrete_sequence=['#00CC96'], text_auto='.1f', range_y=[0,10],
            category_orders={"Capacidad": capacidad_order}
        )
        fig_c.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_c, use_container_width=True)

# --- Documentación ---
with st.expander("📝 Notas Metodológicas sobre este Dataset"):
    st.markdown("""
    **¿Por qué 9 perfiles y no 27?**
    Al utilizar un **Diseño Factorial Fraccionado**, hemos seleccionado las combinaciones que maximizan la información obtenida. 
    Esto permite que la matriz de datos no tenga colinealidad perfecta, requisito indispensable para la regresión OLS que realizaremos en la siguiente etapa.
    
    **Calidad del Dato:**
    Si observas una línea de precio muy plana, significa que en este grupo de analítica el precio no es un factor determinante, o que hay mucho 'ruido' en las respuestas.
    """)

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
if st.button("Siguiente: Modelado Individual ➜"):
    st.switch_page("pages/04_Modelado_Individual.py")
