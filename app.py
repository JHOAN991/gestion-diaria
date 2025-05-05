import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="Informe Diario de Gestión", layout="wide")
st.title("📊 Informe Diario de Gestión")

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)

# Cargar datos desde la hoja
try:
    sheet = client.open_by_key("1rXTfHNd2j2Nv7yWJzHfjcrAmq5bhh_DmyJXMbhe6d-M").worksheet("TOTAL")
    data = sheet.get_all_records()
except Exception as e:
    st.error("❌ Error al conectar con Google Sheets. Verifica el ID del documento y el acceso compartido.")
    st.stop()

# Convertir a DataFrame
df = pd.DataFrame(data)

# Diccionario de campos
campos = {
    "BASE": "BASE",
    "SEGEMENTO REGIONAL": "BUNDLE",
    "SUSCRIPTOR": "SUSCRIPTOR",
    "CUENTA": "CUENTA",
    "NOMBRE_CLIENTE": "NOMBRE_CLIENTE",
    "Numero 1": "Numero 1",
    "EMAIL": "Fijo 2",
    "Asesor": "Asesor",
    "Fecha": "Fecha",
    "Hora": "Hora",
    "Gestion": "Gestion",
    "Razón": "Razon",
    "Comentario": "Comentario"
}

# Renombrar columnas
df = df.rename(columns=campos)

# Convertir columnas numéricas a string (para evitar errores con pyarrow)
cols_to_convert = ["SUSCRIPTOR", "CUENTA", "Numero 1", "Fijo 2"]
for col in cols_to_convert:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Normalizar fechas y horas con formatos definidos
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d/%m/%Y", errors="coerce")
df["Hora"] = pd.to_datetime(df["Hora"].astype(str), format="%H:%M", errors="coerce").dt.time

# Mostrar tabla completa
st.dataframe(df)

# Cantidad de base disponible: Asesor asignado y Gestion vacía
base_disponible = df[(df["Asesor"].notna()) & (df["Gestion"] == "")].shape[0]

# Filtros
fecha_seleccionada = st.date_input("📅 Selecciona la fecha", value=datetime.now().date())
agentes_disponibles = sorted(df["Asesor"].dropna().unique().tolist())
agente_seleccionado = st.selectbox("👤 Selecciona un agente", ["Todos"] + agentes_disponibles)

# Filtrar por fecha
df_filtrado = df[df["Fecha"].dt.date == fecha_seleccionada]

# Filtrar por agente
if agente_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Asesor"] == agente_seleccionado]

# Si no hay datos
if df_filtrado.empty:
    st.warning("⚠️ No se encontraron gestiones para este filtro.")
    st.stop()

# Ordenar por hora
df_filtrado = df_filtrado.sort_values(by="Hora")

# Calcular intervalo entre gestiones
df_filtrado["HoraDatetime"] = pd.to_datetime(df_filtrado["Hora"].astype(str), format="%H:%M:%S", errors="coerce")
df_filtrado["Intervalo"] = df_filtrado["HoraDatetime"].diff().apply(lambda x: x if pd.notnull(x) else pd.NaT)

# Mini informe
total_gestiones = len(df_filtrado)
horas_laborales = 9
proyeccion_diaria = round((total_gestiones / datetime.now().hour) * horas_laborales, 2) if datetime.now().hour > 0 else total_gestiones

st.subheader("🧾 Resumen del Día")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Gestiones", total_gestiones)
col2.metric("Proyección (9h)", proyeccion_diaria)
col3.metric("Fecha", fecha_seleccionada.strftime("%d/%m/%Y"))
col4.metric("Cantidad de Base Disponible", base_disponible)

# Mostrar tabla filtrada
st.subheader("📋 Gestiones del día")
st.dataframe(df_filtrado[[
    "Asesor", "Fecha", "Hora", "Gestion", "Razon", "Comentario", 
    "NOMBRE_CLIENTE", "CUENTA", "SUSCRIPTOR", "Numero 1", "Fijo 2", "Intervalo"
]])
