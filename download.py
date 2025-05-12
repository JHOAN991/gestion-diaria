import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO

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

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Renombrar columnas
    campos = {
        "BASE": "BASE", "Asesor": "Asesor", "Fecha": "Fecha", "Gestion": "Gestion",
        "Razón": "Razon", "Comentario": "Comentario", "NOMBRE_CLIENTE": "NOMBRE_CLIENTE",
        "CUENTA": "CUENTA", "SUSCRIPTOR": "SUSCRIPTOR", "Numero 1": "Numero 1",
        "EMAIL": "Fijo 2"
    }
    df = df.rename(columns=campos)

    # Asegurar columnas necesarias
    columnas_esperadas = ["BASE", "Asesor", "Fecha", "Gestion", "Razon", "Comentario",
                          "NOMBRE_CLIENTE", "CUENTA", "SUSCRIPTOR", "Numero 1", "Fijo 2"]
    for col in columnas_esperadas:
        if col not in df.columns:
            df[col] = ""

    # Convertir a string columnas necesarias
    for col in ["SUSCRIPTOR", "CUENTA", "Numero 1", "Fijo 2", "Comentario"]:
        df[col] = df[col].astype(str)

    # Filtro por base
    base_unicas = df["BASE"].dropna().unique().tolist()
    base_seleccionada = st.selectbox("📂 Selecciona la base", base_unicas)

    # Filtrar
    df_filtrado = df[df["BASE"] == base_seleccionada].copy()
    df_export = df_filtrado[columnas_esperadas]

    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name='BaseFiltrada')
    output.seek(0)

    # Descargar
    nombre_archivo = f"{base_seleccionada}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    st.download_button(
        label="📥 Descargar Excel",
        data=output,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Vista previa
    st.subheader("📋 Vista previa de la base filtrada")
    st.dataframe(df_export)
