import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

from utils.conjoint import (
    ATTRIBUTES,
    first_choice_share,
    fit_respondent_ols,
    generate_synthetic_dataset,
    utility_for_profile,
)

st.set_page_config(page_title="Simulador de Mercado", layout="wide")

st.title("🔮 Simulador de Escenarios de Mercado")
st.markdown("""
Supongamos un mercado simplificado con **dos retailers relevantes**.  
Un competidor ya tiene en oferta un smartphone con una configuración determinada, y nosotros queremos evaluar
si conviene responder con una alternativa propia.

A partir de las utilidades individuales estimadas, este simulador permite aproximar cómo se repartiría
la demanda entre ambas ofertas bajo la regla de **First-Choice**.
""")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuración")
    n_resp = st.slider("Tamaño de muestra", 15, 120, 40, 5)
    seed = st.number_input("Semilla", 1, 9999, 42)
    st.divider()
    st.caption("La regla **First-Choice** asume que el consumidor siempre elige la opción que maximiza su utilidad total.")

# Carga de datos
df = generate_synthetic_dataset(n_respondents=int(n_resp), seed=int(seed))

# --- Configuración de Escenarios ---
st.subheader("🛠️ Configuración de las ofertas en competencia")
n_products = st.radio("¿Cuántos productos compiten en este mercado?", options=[2, 3], horizontal=True)


scenario_names = ["Competidor", "Nuestra oferta", "Oferta 3"]

scenario_profiles = {}
selector_cols = st.columns(n_products)

icons = ["🟦", "🟥", "🟩"]

for idx in range(n_products):
    with selector_cols[idx]:
        with st.container(border=True):
            st.markdown(f"### {icons[idx]} {scenario_names[idx]}")
            selected_levels = {}
            for attr, levels in ATTRIBUTES.items():
                selected_levels[attr] = st.selectbox(
                    f"{attr}:",
                    options=levels,
                    index=0,
                    key=f"{attr}_prod_{idx + 1}",
                )
            scenario_profiles[scenario_names[idx]] = selected_levels



st.divider()

# --- Motor de Simulación ---
with st.spinner("Calculando cuotas de mercado..."):
    models = {}
    failed = []
    # Iteramos por cada encuestado para ajustar su modelo individual
    for rid, df_resp in df.groupby("RespondentID"):
        try:
            model, _ = fit_respondent_ols(df_resp)
            models[rid] = model
        except Exception:
            failed.append(rid)

    if not models:
        st.error("Error crítico: No se pudieron generar modelos para la simulación.")
        st.stop()

    # Cálculo de utilidades cruzadas
    utility_rows = []
    for rid, model in models.items():
        row = {"RespondentID": rid}
        for pname, profile in scenario_profiles.items():
            row[pname] = utility_for_profile(profile, model.params, ATTRIBUTES)
        utility_rows.append(row)

    utility_df = pd.DataFrame(utility_rows).set_index("RespondentID")
    
    # Aplicación de regla First-Choice
    share = first_choice_share(utility_df)
    share_df = share.reset_index()
    share_df.columns = ["Producto", "MarketShare"]

# --- Resultados Visuales ---
st.subheader("📊 Resultado de la Simulación")

col_chart, col_stats = st.columns([2, 1])

with col_chart:
    # Gráfico de barras con anotaciones
    fig = px.bar(
        share_df, x="Producto", y="MarketShare",
        color="Producto", text=share_df["MarketShare"].map(lambda x: f"{x:.1f}%"),
        color_discrete_sequence=px.colors.qualitative.Safe,
        title="Participación de Mercado Estimada"
    )
    fig.update_layout(yaxis_range=[0, 100], showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.write("**Resumen de la Simulación**")
    winner = share_df.loc[share_df['MarketShare'].idxmax()]
    st.success(f"🏆 **Ganador:** {winner['Producto']}\n\nCon una cuota del **{winner['MarketShare']:.1f}%**")
    
    st.metric("Total Modelados", f"{len(models)} pers.")
    if failed:
        st.warning(f"Omitidos: {len(failed)} por inconsistencias.")

# --- Detalles Pro ---
st.divider()
tab1, tab2 = st.tabs(["📄 Matriz de Utilidades", "⚙️ Metodología Técnica"])

with tab1:
    st.write("Utilidad total predicha para cada encuestado en cada escenario:")
    st.dataframe(utility_df.style.highlight_max(axis=1, color='lightgreen').format("{:.2f}"), use_container_width=True)

with tab2:
    st.latex(r"U_{total, i} = \beta_0 + \beta_{Marca} + \beta_{Precio} + \beta_{Capacidad}")
    st.markdown("""
    **Reglas de la Simulación:**
    1.  **Modelo Individual:** Se corre una regresión OLS única por cada persona.
    2.  **First-Choice:** Se asume que el 100% de la probabilidad de compra va al producto con mayor utilidad.
    3.  **Empates:** Si hay empate técnico en utilidades, la cuota se divide equitativamente.
    """)

if failed:
    with st.expander("Ver IDs omitidos"):
        st.write(failed)