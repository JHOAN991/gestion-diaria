import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def mostrar_descarga():
    st.title("⬇️ Descargar Bases por Filtro")

    # Autenticación con Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
    except KeyError:
        st.error("❌ No se encontraron las credenciales de Google Sheets en los secretos.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al autenticar con Google Sheets: {str(e)}")
        st.stop()

    # Cargar los datos desde Google Sheets
    try:
        sheet = client.open_by_key("1rXTfHNd2j2Nv7yWJzHfjcrAmq5bhh_DmyJXMbhe6d-M").worksheet("TOTAL")
        data = sheet.get_all_records()
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {str(e)}")
        st.stop()

    # Crear un DataFrame con los datos obtenidos
    df = pd.DataFrame(data)

    # Verificar si la columna 'BASE' existe
    if "BASE" not in df.columns:
        st.error("❌ La columna 'BASE' no está en los datos.")
        return


    # Obtener las bases disponibles
    base_unicas = df["BASE"].dropna().unique().tolist()
    base_seleccionada = st.selectbox("📂 Selecciona la base", base_unicas)

    # Filtrar los datos según la base seleccionada
    df_filtrado = df[df["BASE"] == base_seleccionada]

    # Especificar las columnas a exportar
    columnas_exportar = [
        "BASE", "Asesor", "Fecha", "Gestion", "Razón", "Comentario",
        "NOMBRE_CLIENTE", "CUENTA", "SUSCRIPTOR", "Numero 1"
    ]
    
    # Asegurarse de que todas las columnas estén disponibles antes de proceder
    if not all(col in df.columns for col in columnas_exportar):
        st.error("❌ Algunas columnas necesarias no están presentes en los datos.")
        return

    # Renombrar las columnas antes de la exportación
    df_export = df_filtrado[columnas_exportar].rename(columns={"EMAIL": "Fijo 2"})

    # Convertir el DataFrame filtrado a CSV
    csv = df_export.to_csv(index=False).encode("utf-8")

    # Botón para descargar el archivo CSV
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name=f"{base_seleccionada}_datos.csv",
        mime="text/csv"
    )

    # Mostrar los datos filtrados en una tabla
    st.dataframe(df_export)
