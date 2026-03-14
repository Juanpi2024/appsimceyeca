import streamlit as st
import importlib.util
import os
import sys

# Wrapper para asegurar que Streamlit Cloud encuentre el punto de entrada
# y para manejar posibles errores de importación de forma amigable.

try:
    # Intenta importar el módulo principal
    import streamlit_app
    streamlit_app.main()
except Exception as e:
    st.error(f"Error al iniciar la aplicación: {e}")
    st.info("Por favor, contacte con el administrador del sistema.")
