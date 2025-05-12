def mostrar_informe():
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    import gspread
    from google.oauth2.service_account import Credentials

    # Título de la página
    st.title("📊 Informe Diario de Gestión")

    # Autenticación con Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    # Conexión y carga de datos
    try:
        sheet = client.open_by_key("1rXTfHNd2j2Nv7yWJzHfjcrAmq5bhh_DmyJXMbhe6d-M").worksheet("TOTAL")
        data = sheet.get_all_records()
    except Exception as e:
        st.error("❌ Error al conectar con Google Sheets. Verifica el ID del documento y el acceso compartido.")
        st.stop()

    # Carga y renombramiento de columnas
    df = pd.DataFrame(data)
    campos = {
        "BASE": "BASE", "SEGEMENTO REGIONAL": "BUNDLE", "SUSCRIPTOR": "SUSCRIPTOR",
        "CUENTA": "CUENTA", "NOMBRE_CLIENTE": "NOMBRE_CLIENTE", "Numero 1": "Numero 1",
        "EMAIL": "Fijo 2", "Asesor": "Asesor", "Fecha": "Fecha", "Hora": "Hora",
        "Gestion": "Gestion", "Razón": "Razon", "Comentario": "Comentario"
    }
    df = df.rename(columns=campos)

    # Conversión de tipos
    for col in ["SUSCRIPTOR", "CUENTA", "Numero 1", "Fijo 2"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)
    df["Hora"] = pd.to_datetime(df["Hora"], errors="coerce").dt.time

    # Mostrar todos los datos (opcional)
    st.dataframe(df)

    # Filtros
    base_disponible = df[(df["Asesor"].notna()) & (df["Gestion"] == "")].shape[0]
    fecha_seleccionada = st.date_input("📅 Selecciona la fecha", value=datetime.now().date())
    agentes_disponibles = sorted(df["Asesor"].dropna().unique().tolist())
    agente_seleccionado = st.selectbox("👤 Selecciona un agente", ["Todos"] + agentes_disponibles)

    # Aplicar filtros
    df_filtrado = df[df["Fecha"].dt.date == fecha_seleccionada]
    if agente_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Asesor"] == agente_seleccionado]
    if df_filtrado.empty:
        st.warning("⚠️ No se encontraron gestiones para este filtro.")
        st.stop()

    # Calcular intervalos entre gestiones
    df_filtrado = df_filtrado.sort_values(by="Hora")
    df_filtrado["HoraDatetime"] = pd.to_datetime(df_filtrado["Hora"].astype(str), format="%H:%M:%S", errors="coerce")
    df_filtrado["Intervalo"] = df_filtrado["HoraDatetime"].diff().apply(lambda x: x if pd.notnull(x) else pd.NaT)

    # Métricas
    total_gestiones = len(df_filtrado)
    horas_laborales = 9
    proyeccion_diaria = round((total_gestiones / datetime.now().hour) * horas_laborales, 2) if datetime.now().hour > 0 else total_gestiones

    # Mostrar resumen
    st.subheader("🧾 Resumen del Día")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Gestiones", total_gestiones)
    col2.metric("Proyección (9h)", proyeccion_diaria)
    col3.metric("Fecha", fecha_seleccionada.strftime("%d/%m/%Y"))
    col4.metric("Cantidad de Base Disponible", base_disponible)

    # Mostrar detalles
    st.subheader("📋 Gestiones del día")
    st.dataframe(df_filtrado[[
        "Asesor", "Fecha", "Hora", "Gestion", "Razon", "Comentario",
        "NOMBRE_CLIENTE", "CUENTA", "SUSCRIPTOR", "Numero 1", "Fijo 2", "Intervalo"
    ]])
