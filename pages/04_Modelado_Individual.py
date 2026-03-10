import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

from utils.conjoint import fit_respondent_ols, generate_synthetic_dataset, relative_importance

st.set_page_config(page_title="Modelado Individual - Part-worths", layout="wide")

st.title("🧠 Modelado de Preferencias Individuales")
st.markdown("""
En esta etapa descomponemos el rating total en la utilidad que el usuario asigna a cada nivel 
específico. Es el paso de **datos brutos** a **insights psicológicos**.
""")

# --- Sidebar ---
with st.sidebar:
    st.header("📊 Datos de Origen")
    n_resp = st.sidebar.slider("Tamaño de muestra", 15, 120, 40, 5)
    seed = st.sidebar.number_input("Semilla", 1, 9999, 42)

# Generación de datos base
df = generate_synthetic_dataset(n_respondents=int(n_resp), seed=int(seed))
respondents = sorted(df["RespondentID"].unique().tolist())

# Selector de encuestado con estilo
st.info("### 👤 Perfil del Consumidor")
c1, c2 = st.columns([1, 2])
with c1:
    selected_id = st.selectbox("Selecciona un ID de encuestado:", options=respondents)
    df_resp = df[df["RespondentID"] == selected_id].copy()
with c2:
    st.write(f"Filas de datos disponibles para el ID {selected_id}: **{len(df_resp)}**")
    st.caption("Cada una de estas 9 respuestas será usada para resolver el sistema de ecuaciones de la regresión.")


st.subheader("📋 Respuestas observadas del encuestado")
st.write(
    "La siguiente tabla muestra los perfiles evaluados por el encuestado seleccionado "
    "y el rating otorgado a cada uno. Estas observaciones constituyen la base del modelo individual."
)

cols_to_show = [col for col in ["Marca", "Capacidad", "Precio", "Rating"] if col in df_resp.columns]
st.dataframe(
    df_resp[cols_to_show].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Observa que el encuestado no calificó atributos por separado, sino perfiles completos. "
    "El modelo utilizará la variación entre estas evaluaciones para inferir cuánto valor asigna a cada nivel."
)


st.divider()


st.subheader("📐 Del perfil al modelo")
st.write(
    "Para cada encuestado, modelamos el **rating** otorgado a un perfil en función de tres atributos del producto: "
    "**marca**, **precio** y **capacidad de almacenamiento**."
)

st.write(
    "Como estos atributos son variables discretas, sus niveles se codifican mediante variables indicadoras "
    "para poder estimar un modelo de regresión lineal."
)

with st.container(border=True):
    st.latex(r"\text{Rating}_i = \beta_0 + \beta_1\text{Marca}_i + \beta_2\text{Precio}_i + \beta_3\text{Capacidad}_i + \varepsilon_i")
    st.caption(
        "El modelo descompone la evaluación total del perfil en la contribución asociada a cada atributo."
    )

st.divider()


try:
    # Ajuste del modelo
    model, partworths = fit_respondent_ols(df_resp)
    attr_color_map = {
        "Capacidad": px.colors.qualitative.Prism[0],
        "Precio": px.colors.qualitative.Prism[1],
        "Marca": px.colors.qualitative.Prism[2],
    }

    # 1. Visualización de Part-worths (Utilidades Parciales)
    st.subheader("🎯 Utilidades Parciales (Part-worths)")
    
    partworth_rows = []
    for attr, levels_map in partworths.items():
        for lvl, val in levels_map.items():
            partworth_rows.append({"Atributo": attr, "Nivel": lvl, "PartWorth": val})
    pw_df = pd.DataFrame(partworth_rows)

    col_pw, col_imp = st.columns([1.5, 1])

    # ... (código previo del modelo OLS y creación de pw_df)

    with col_pw:
        # Definimos el orden específico y lógico para cada atributo
        # Esto asegura que la gráfica no use un orden alfabético o arbitrario
        level_order = [
            # Capacidad (de menor a mayor)
            "64GB", "128GB", "256GB", 
            # Precio (de menor a mayor)
            "Bajo", "Medio", "Alto",   
            # Marca (un orden lógico o alfabético si aplica)
            "Alpha", "Beta", "Gamma"    
        ]

        # Convertimos la columna 'Nivel' en una categoría con el orden definido
        pw_df['Nivel'] = pd.Categorical(pw_df['Nivel'], categories=level_order, ordered=True)
        # Ordenamos el DataFrame para que el gráfico respete el orden de las categorías
        pw_df = pw_df.sort_values('Nivel')

        # Gráfico de barras horizontales divergentes con el orden aplicado
        fig_pw = px.bar(
            pw_df, x="PartWorth", y="Nivel", color="Atributo",
            orientation='h', title="¿Cuánto valor aporta cada nivel?",
            text_auto='.2f', color_discrete_map=attr_color_map,
            template="plotly_white"
        )
        
        # Añadimos la línea de referencia en cero
        fig_pw.add_vline(x=0, line_dash="dash", line_color="black")
        
        # Forzamos que el eje Y mantenga el orden del DataFrame (categories array)
        fig_pw.update_layout(
            height=450, # Un poco más de altura para acomodar todos los niveles cómodamente
            showlegend=False,
            yaxis={'categoryorder':'array', 'categoryarray':level_order}
        )
        st.plotly_chart(fig_pw, use_container_width=True)


    with col_imp:
        # 2. Importancia Relativa
        imp_df = relative_importance(partworths).sort_values("ImportanciaRelativa", ascending=True)
        fig_imp = px.pie(
            imp_df, values='ImportanciaRelativa', names='Atributo',
            title="Peso en la decisión", hole=.4,
            color='Atributo',
            color_discrete_map=attr_color_map,
        )
        fig_imp.update_layout(height=400, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_imp, use_container_width=True)

    st.divider()

    # 3. INTERACTIVO: El Producto "Calculado"
    st.subheader(f"🔮 Simulador de Utilidad para el Usuario {selected_id}")
    st.markdown("Configura un producto y predice qué rating le daría este usuario específico:")
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        s_marca = st.selectbox("Marca", pw_df[pw_df["Atributo"]=="Marca"]["Nivel"])
    with sc2:
        s_precio = st.selectbox("Precio", pw_df[pw_df["Atributo"]=="Precio"]["Nivel"])
    with sc3:
        s_cap = st.selectbox("Capacidad", pw_df[pw_df["Atributo"]=="Capacidad"]["Nivel"])
    
    # Cálculo de utilidad (Intercepto + Suma de PW correspondientes)
    intercept = model.params[0]
    u_marca = pw_df[(pw_df["Atributo"]=="Marca") & (pw_df["Nivel"]==s_marca)]["PartWorth"].values[0]
    u_precio = pw_df[(pw_df["Atributo"]=="Precio") & (pw_df["Nivel"]==s_precio)]["PartWorth"].values[0]
    u_cap = pw_df[(pw_df["Atributo"]=="Capacidad") & (pw_df["Nivel"]==s_cap)]["PartWorth"].values[0]
    total_utility = intercept + u_marca + u_precio + u_cap

    with sc4:
        st.metric("Rating Predicho", f"{total_utility:.2f}", delta=f"{total_utility - df_resp['Rating'].mean():.2f} vs promedio")

    # 4. Detalles técnicos
    with st.expander("🛠️ Ver Tripas del Modelo (Sumario Estadístico)"):
        st.markdown("Ajuste mediante Mínimos Cuadrados Ordinarios (OLS).")
        st.text(model.summary().as_text())

except Exception as e:
    st.error("No se pudo procesar el modelo. Verifica que el encuestado tenga variabilidad en sus respuestas.")
    st.exception(e)

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
if st.button("Siguiente: Simulación de Mercado ➜"):
    st.switch_page("pages/05_Simulacion_de_Mercado.py")
