import streamlit as st

# ✅ Esto debe ir primero y solo una vez
st.set_page_config(page_title="Informe Diario de Gestión", layout="wide")

from streamlit_option_menu import option_menu

# Menú de navegación
with st.sidebar:
    seleccion = option_menu(
        menu_title="Navegación",
        options=["Informe Diario", "Descargar Bases"],
        icons=["bar-chart", "download"],
        menu_icon="cast",
        default_index=0,
    )

# Navegación condicional
if seleccion == "Informe Diario":
    from informe_diario import mostrar_informe
    mostrar_informe()
else:
    from download import mostrar_descarga  # ✅ Aquí estaba el error (era 'dowload')
    mostrar_descarga()
