import streamlit as st

st.set_page_config(page_title="Metodología - Conjoint Analysis", layout="wide")

# --- ELEMENTO PUENTE: LA CONEXIÓN ---
st.title("🧪 La ruta metodológica del análisis conjunto")
st.markdown("""
### Del reto al estudio de mercado
En la página anterior definimos el problema: elegir, entre varias configuraciones posibles del smartphone, aquella que resulte más atractiva para el mercado.

Para tomar esa decisión no basta con intuición. Necesitamos un **estudio de mercado** que nos permita observar cómo reaccionan los consumidores ante distintos perfiles de producto.

Aquí entra el **análisis conjunto**: una metodología que representa cada alternativa como una combinación de atributos, captura evaluaciones de los consumidores y estima la utilidad asociada a cada nivel.
""")
st.divider()

st.subheader("1. La secuencia del estudio")
cols = st.columns(4)
steps = [
    "🎯 Definir atributos y niveles",
    "🃏 Construir perfiles",
    "⭐ Recoger evaluaciones",
    "🧠 Estimar utilidades"
]
for i, step in enumerate(steps):
    cols[i].markdown(f"**{step}**")
    cols[i].progress((i + 1) * 25)

st.divider()

# 2. Diseño de Perfiles (Smartphone - Consistencia Total)
st.subheader("2. Estímulos: ¿Qué le mostramos al consumidor?")
st.write("""
En lugar de preguntar por cada atributo de forma aislada, presentamos **perfiles completos de producto**.
Así observamos cómo evalúa el consumidor combinaciones realistas de marca, capacidad y precio.
""")

tab1, tab2, tab3 = st.tabs(["💎 Perfil Premium", "⚖️ Perfil Equilibrado", "🏷️ Perfil de Entrada"])

with tab1:
    with st.container(border=True):
        st.markdown("### 📱 Opción: El Flagship")
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.table({
                "Atributo": ["Marca", "Capacidad", "Precio"],
                "Especificación": ["Alpha (Líder) 🅰️", "256 GB 💾", "800 EUR 💶"]
            })
        with c2:
            st.metric(label="Inversión", value="800 EUR", delta="Máximo Nivel")
            st.write("**Simulación de Rating:**")
            st.select_slider("¿Qué tanto atrae este perfil?", options=list(range(1, 11)), value=9, key="p1_s")

with tab2:
    with st.container(border=True):
        st.markdown("### 📱 Opción: El Versátil")
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.table({
                "Atributo": ["Marca", "Capacidad", "Precio"],
                "Especificación": ["Beta 🅱️", "128 GB 💾", "600 EUR 💶"]
            })
        with c2:
            st.metric(label="Inversión", value="600 EUR", delta="-200 EUR", delta_color="normal")
            st.write("**Simulación de Rating:**")
            st.select_slider("¿Qué tanto atrae este perfil?", options=list(range(1, 11)), value=7, key="p2_s")

with tab3:
    with st.container(border=True):
        st.markdown("### 📱 Opción: El Económico")
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.table({
                "Atributo": ["Marca", "Capacidad", "Precio"],
                "Especificación": ["Gamma 🌀", "64 GB 💾", "450 EUR 💶"]
            })
        with c2:
            st.metric(label="Inversión", value="450 EUR", delta="-350 EUR vs Top", delta_color="inverse")
            st.write("**Simulación de Rating:**")
            st.select_slider("¿Qué tanto atrae este perfil?", options=list(range(1, 11)), value=4, key="p3_s")

st.caption("✨ **Nota para el Ejecutivo:** Cada slider representa un voto de confianza del mercado. Al moverlos, estamos 'alimentando' la regresión.")

st.divider()

# 3. El Motor: Diseño Factorial
st.subheader("🔬 3. ¿Cuántos perfiles?")
col_theory, col_practice = st.columns(2)

with col_theory:
    st.markdown("### 📚 El problema combinatorio")
    st.write("""
    Con 3 marcas, 3 capacidades y 3 precios, existen **27 configuraciones posibles**.
    Mostrar todas al consumidor no sería práctico, porque aumentaría la fatiga y reduciría la calidad de la respuesta.
    """)
    st.error("⚠️ **Riesgo metodológico:** demasiados perfiles pueden deteriorar la calidad del dato.")

with col_practice:
    st.markdown("### ✂️ La solución: diseño factorial fraccionado")
    st.write("""
    Por ello seleccionamos un subconjunto estructurado de perfiles que conserva balance entre atributos y niveles.
    Así podemos estimar utilidades de forma eficiente sin mostrar todas las combinaciones posibles.
    """)
    st.success("✅ **Resultado:** menos perfiles, pero información suficiente para el análisis.")

with st.expander("📊 Ver la matriz ortogonal (referencia técnica)"):
    st.write("""
    Esta matriz muestra el **subconjunto de perfiles** que será presentado a los consumidores.
    No se trata de una selección aleatoria, sino de un diseño factorial fraccionado construido
    para conservar **balance** entre los niveles de los atributos.

    Cada fila representa un perfil de producto. En conjunto, los perfiles buscan que los niveles
    de **marca, capacidad y precio** aparezcan en combinaciones variadas, de modo que podamos
    estimar con mayor claridad la contribución de cada atributo a la preferencia del consumidor.

    **Observa** que los niveles no siempre aparecen juntos de la misma manera: esa variación controlada
    es lo que hace posible el análisis.
    """)
    
    design_matrix = [
        {"Perfil": 1, "Marca": "Alpha", "Capacidad": "256GB", "Precio": "800€"},
        {"Perfil": 2, "Marca": "Beta", "Capacidad": "128GB", "Precio": "800€"},
        {"Perfil": 3, "Marca": "Gamma", "Capacidad": "64GB", "Precio": "600€"},
        {"Perfil": 4, "Marca": "Alpha", "Capacidad": "128GB", "Precio": "450€"},
    ]
    st.table(design_matrix)
st.divider()

# 4. Aplicación de la encuesta
st.subheader("📝 4. Aplicación de la encuesta")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### ¿A quién encuestar?")
    st.write("""
    La encuesta debe dirigirse a personas que formen parte del **mercado objetivo** del producto.
    En este caso, conviene incluir consumidores con interés real en smartphones y posibilidad de compra
    en el rango de precio analizado.

    Recomendaciones:
    - definir criterios mínimos de elegibilidad,
    - evitar respuestas de personas ajenas a la categoría,
    - y asegurar diversidad suficiente si después se compararán segmentos.
    """)

with c2:
    st.markdown("#### ¿Cómo levantar la información?")
    st.write("""
    El levantamiento puede realizarse mediante:
    - formulario en línea,
    - panel digital,
    - encuesta presencial con apoyo de tableta o laptop,
    - o campañas segmentadas por correo y redes.

    En la práctica, los canales digitales suelen ser los más eficientes cuando se busca rapidez,
    control del cuestionario y cobertura de un público amplio.
    """)

st.info("""
**Sugerencia para el tamaño de muestra:** en estudios conjoint suele trabajarse, como regla práctica,
con muestras del orden de **150 a 300 encuestados** como punto de partida. Si el estudio busca comparar
segmentos por separado, conviene planear alrededor de **200 o más casos por segmento**. En muchos proyectos,
**300 encuestados** funciona como una referencia razonable para obtener resultados estables.
""")

st.success("""
**Siguiente paso:** una vez definidos el público objetivo, el canal y el tamaño de muestra,
podemos diseñar el instrumento y comenzar el levantamiento de preferencias.
""")