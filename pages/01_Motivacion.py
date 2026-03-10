import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Motivación - Conjoint Analysis", layout="wide")

# --- 1. EL RETO DEL EJECUTIVO ---
st.title("🚀 El Desafío del Lanzamiento")

col_narrativa, col_metrics = st.columns([2, 1])

with col_narrativa:
    st.markdown("""
    ### La situación
    
Eres responsable de estrategia de producto en un retailer de tecnología que planea lanzar un smartphone exclusivo para su canal.

Para ello, puedes negociar con diferentes marcas fabricantes. Antes de cerrar el acuerdo, necesitas identificar qué combinación de atributos resultaría más atractiva para los consumidores.

En este caso, analizaremos tres atributos clave:

* Marca

* Capacidad de almacenamiento

* Precio

El objetivo es estimar qué configuración de producto tendría mayor preferencia en el mercado.
""")

with col_metrics:
    st.container(border=True).metric("Objetivo", "Max. Market Share", "+15%")
    st.container(border=True).metric("KPI Clave", "ROI de Atributos", "Optimizado")

st.divider()

# --- 2. LA RADIOGRAFÍA DE LA MENTE (ÁRBOL) ---
st.header("🌳 El Árbol de Decisión del Producto")
st.write(
    """Para estudiar el lanzamiento, modelaremos el smartphone como un conjunto de decisiones sobre atributos clave.
Cada combinación de marca, precio y capacidad genera una alternativa de producto dentro del espacio de búsqueda. """
)

# El HTML del árbol (mantenemos tu diseño que es excelente)
tree_html = """
<style>
.tree-wrap { padding: 1rem 0.5rem; }
.root-pill {
  margin: 0 auto 1.3rem auto; width: fit-content; min-width: 320px;
  padding: 0.8rem 2rem; border-radius: 999px; background: #0d56a3;
  color: #ffffff; text-align: center; font-size: 1.8rem; font-weight: 700;
  box-shadow: 0 6px 14px rgba(0,0,0,0.18);
}
.attrs-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.4rem; }
.attr-col { display: flex; flex-direction: column; align-items: center; }
.attr-pill {
  width: 90%; border-radius: 999px; color: white; font-weight: 700;
  text-align: center; padding: 0.5rem; box-shadow: 0 5px 12px rgba(0,0,0,0.1);
}
.attr-red { background: #d60000; }
.attr-green { background: #71b148; }
.attr-purple { background: #7436a6; }
.down-arrow { font-size: 1.5rem; margin: 0.3rem 0; color: #444; }
.levels {
  width: 90%; border: 2px dashed #b9bcc2; border-radius: 14px;
  padding: 0.6rem; background: rgba(250,250,250,0.8);
}
.level-item { font-weight: 600; padding: 0.3rem 0; border-bottom: 1px solid #eee; }
</style>

<div class="tree-wrap">
  <div class="root-pill">Árbol del producto</div>
  <div class="attrs-grid">
    <div class="attr-col">
      <div class="attr-pill attr-red">Marca</div>
      <div class="down-arrow">↓</div>
      <div class="levels">
        <div class="level-item">🅰️ Alpha (Líder)</div>
        <div class="level-item">🅱️ Beta</div>
        <div class="level-item">🌀 Gamma</div>
      </div>
    </div>
    <div class="attr-col">
      <div class="attr-pill attr-green">Precio</div>
      <div class="down-arrow">↓</div>
      <div class="levels">
        <div class="level-item">💶 450 EUR</div>
        <div class="level-item">💶💶 600 EUR</div>
        <div class="level-item">💶💶💶 800 EUR</div>
      </div>
    </div>
    <div class="attr-col">
      <div class="attr-pill attr-purple">Capacidad</div>
      <div class="down-arrow">↓</div>
      <div class="levels">
        <div class="level-item">💾 64GB</div>
        <div class="level-item">💾 128GB</div>
        <div class="level-item">💾 256GB</div>
      </div>
    </div>
  </div>
</div>
"""
components.html(tree_html, height=450, scrolling=False)

st.info("""
En este ejemplo, el número total de configuraciones posibles es el producto del número de niveles de cada atributo.
""")



st.divider()

# --- 3. PREGUNTAS CLAVE ---
st.header("🎯 Del reto al método")
st.write(
    "Para enfrentar este desafío no basta con intuición. "
    "Necesitamos un **estudio de mercado** que nos permita medir cómo valoran los consumidores "
    "las distintas configuraciones del smartphone."
)

q1, q2, q3 = st.columns(3)

with q1:
    with st.container(border=True):
        st.markdown("### ⚖️ ¿Qué atributo pesa más?")
        st.write(
            "¿Qué genera mayor preferencia en el consumidor: "
            "cambiar de **Beta a Alpha** o aumentar de **128GB a 256GB**?"
        )

with q2:
    with st.container(border=True):
        st.markdown("### 💶 ¿Cuánto vale un mejor atributo?")
        st.write(
            "¿Cuánto más estaría dispuesto a pagar un cliente "
            "por una mayor capacidad de almacenamiento sin cambiar de marca?"
        )

with q3:
    with st.container(border=True):
        st.markdown("### 🏆 ¿Cuál es la mejor configuración?")
        st.write(
            "¿Qué combinación de **marca, precio y capacidad** "
            "maximiza la preferencia del mercado frente a la competencia?"
        )

st.success(
    "**Conclusión:** Para responder estas preguntas realizaremos un **estudio de mercado** "
    "mediante **análisis conjunto**, con el fin de estimar utilidades y sustentar el diseño del producto."
)