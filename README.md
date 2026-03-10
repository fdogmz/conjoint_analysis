# Conjoint Analysis App (Streamlit)

Aplicación multipágina en Streamlit para Análisis Conjunto:
- Introducción
- Metodología
- Exploración de datos sintéticos
- Modelado individual (OLS)
- Simulación de mercado (First-Choice)

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Despliegue en Streamlit Community Cloud

1. Sube este repo a GitHub.
2. En Streamlit Community Cloud, crea una nueva app desde el repo.
3. Configura:
   - **Main file path**: `streamlit_app.py`
   - **Branch**: la rama donde esté este código
4. Deploy.

No requiere `secrets` ni `packages.txt` para esta versión.
