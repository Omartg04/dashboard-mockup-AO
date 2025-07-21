import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Bienestar Social A.O.",
    page_icon="🗺️",
    layout="wide",
)
     

# --- FUNCIÓN PARA GENERAR DATOS FICTICIOS ---

# --- FUNCIÓN DE GENERACIÓN DE DATOS UNIFICADA ---

@st.cache_data
def generar_datos_unificados(num_manzanas_por_colonia=15):
    """
    Crea y devuelve dos DataFrames consistentes: uno de manzanas y otro de personas.
    """
    # 1. UNIVERSO DE DATOS (ÚNICA FUENTE DE VERDAD)
    colonias_data = {
        "Barrio Norte": ["10350"],
        "Jalalpa": ["10400", "10401"],
        "Lomas de Becerra S1": ["10370"],
        "El Rodeo": ["10500"],
        "Golondrinas": ["10510"],
        "Tlacoyaque": ["10600"],
        "Santa Lucía": ["10700"]
    }
    programas = ["Beca Benito Juárez", "Pensión Adulto Mayor", "IMSS Bienestar", "Beca Rita Cetina", "Ninguno"]
    estatus_operativos = ["Por contactar", "Pre-registro completo", "Cita generada", "Visita programada"]
    
    # --- 2. GENERAR DATOS DE MANZANAS ---
    manzanas_list = []
    for colonia, agebs in colonias_data.items():
        for ageb in agebs:
            for i in range(num_manzanas_por_colonia):
                manzana_id = f"{ageb}-{i:02d}"
                total_viviendas = np.random.randint(10, 50)
                viviendas_censadas = np.random.randint(0, total_viviendas)
                porcentaje = (viviendas_censadas / total_viviendas) if total_viviendas > 0 else 0
                
                if porcentaje <= 0.25: estatus_censado = "0% - 25%"
                elif porcentaje <= 0.50: estatus_censado = "25.1% - 50%"
                elif porcentaje <= 0.75: estatus_censado = "50.1% - 75%"
                else: estatus_censado = "75.1% - 100%"

                manzanas_list.append({
                    "ID_Manzana": manzana_id, "AGEB": ageb, "Manzana": f"{i:02d}", "Colonia": colonia,
                    "Total de Viviendas Habitadas": total_viviendas, "Viviendas Censadas": viviendas_censadas,
                    "Viviendas Pendientes de Cita": np.random.randint(0, 5), "Entrevistas Rechazadas": np.random.randint(0, 2),
                    "Porcentaje de Censado": f"{porcentaje:.1%}", "Estatus de Censado": estatus_censado
                })
    df_manzanas = pd.DataFrame(manzanas_list)

    # --- 3. GENERAR DATOS DE PERSONAS BASADOS EN LAS MANZANAS ---
    personas_list = []
    # Inyectar casos de la narrativa en la primera manzana de Barrio Norte
    manzana_narrativa = df_manzanas[df_manzanas["Colonia"] == "Barrio Norte"].iloc[0]
    for _ in range(20):
        personas_list.append({
            "ID": np.random.randint(9000, 9999), "Colonia": "Barrio Norte", "ID_Manzana": manzana_narrativa["ID_Manzana"],
            "Latitud": 19.38 + np.random.normal(0, 0.001), "Longitud": -99.18 + np.random.normal(0, 0.001),
            "Edad": np.random.randint(24, 36), "Sexo": "Femenino", "Tiene_Bebes": 1, "Es_Adulto_Mayor": 0, "Rezago_Educativo": 0, "Acceso_Salud": 1,
            "Seguridad_Social": 1, "Calidad_Vivienda": 0, "Servicios_Vivienda": 0, "Acceso_Alimentacion": 0,
            "Programa_Asignado": np.random.choice(["IMSS Bienestar", "Ninguno"], p=[0.4, 0.6]),
            "Estatus_Operativo": np.random.choice(estatus_operativos)
        })

    # Generar el resto de las personas
    for _, manzana_row in df_manzanas.iterrows():
        # Generar personas para las viviendas censadas en cada manzana
        for i in range(manzana_row["Viviendas Censadas"]):
            edad = np.random.randint(0, 90)
            rezago_edu = np.random.choice([0, 1], p=[0.7, 0.3])
            acceso_salud_rand = np.random.choice([0, 1], p=[0.6, 0.4])
            programa_asignado = "Ninguno"
            estatus = np.random.choice(estatus_operativos)
            if edad >= 65 and np.random.rand() > 0.3: programa_asignado, estatus = "Pensión Adulto Mayor", "Cubierto"
            elif rezago_edu == 1 and edad < 25 and np.random.rand() > 0.5: programa_asignado, estatus = np.random.choice(["Beca Benito Juárez", "Beca Rita Cetina"]), "Cubierto"
            elif acceso_salud_rand == 1 and np.random.rand() > 0.6: programa_asignado, estatus = "IMSS Bienestar", "Cubierto"
            
            personas_list.append({
                "ID": int(f"{manzana_row['AGEB']}{i}"), "Colonia": manzana_row["Colonia"], "ID_Manzana": manzana_row["ID_Manzana"],
                "Latitud": 19.35 + np.random.normal(0, 0.05), "Longitud": -99.22 + np.random.normal(0, 0.05),
                "Edad": edad, "Sexo": np.random.choice(["Masculino", "Femenino"]),
                "Tiene_Bebes": 1 if 18 <= edad <= 45 and np.random.rand() > 0.8 else 0, "Es_Adulto_Mayor": 1 if edad >= 65 else 0,
                "Rezago_Educativo": rezago_edu, "Acceso_Salud": acceso_salud_rand,
                "Seguridad_Social": np.random.choice([0, 1], p=[0.5, 0.5]), "Calidad_Vivienda": np.random.choice([0, 1], p=[0.8, 0.2]),
                "Servicios_Vivienda": np.random.choice([0, 1], p=[0.85, 0.15]), "Acceso_Alimentacion": np.random.choice([0, 1], p=[0.75, 0.25]),
                "Programa_Asignado": programa_asignado, "Estatus_Operativo": estatus,
            })
            
    df_personas = pd.DataFrame(personas_list)
    df_personas['Tiene_Programa_Social'] = df_personas['Programa_Asignado'].apply(lambda x: 0 if x == 'Ninguno' else 1)
    
    # 4. Devolver AMBOS DataFrames
    return df_manzanas, df_personas



# --- CARGA DE DATOS ---
df_manzanas, df_personas = generar_datos_unificados()
# --- TÍTULO PRINCIPAL ---
st.title("📊 Seguimiento CENSO PAPE Álvaro Obregón")
st.markdown("Este es un ejemplo con **datos ficticios** para validar las funcionalidades clave en el taller de discovery.")

# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Pulso del Censo", 
    "🩺 Radiografía de Carencias", 
    "☂️ Cobertura de Programas Sociales", 
    "🗺️ Mapa Interactivo"
])


# --- PESTAÑA 1: PULSO DEL CENSO (Con Datos de Contacto Fijos) ---
with tab1:
    st.header("Pulso del Censo: Captura y Calidad")

    # --- Sección de Avance y Calidad (existente) ---
    meta_registros = 16601
    registros_limpios = 4269
    registros_crudos = int(registros_limpios / 0.956)

    avance_decimal = registros_crudos / meta_registros
    diferencia_registros = registros_limpios - registros_crudos
    calidad_porcentaje = registros_limpios / registros_crudos if registros_crudos > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Avance de Captura vs Meta")
        st.metric(label="Avance de Registros", value=f"{avance_decimal:.1%}")
        st.progress(avance_decimal)
        st.markdown(f"**{registros_crudos:,} / {meta_registros:,}**")
    with col2:
        st.subheader("Impacto del Proceso de Limpieza")
        st.metric(
            label="Registros en Base Limpia",
            value=f"{registros_limpios:,}",
            delta=f"{diferencia_registros} registros eliminados"
        )
        st.metric(
            label="Calidad de la Base",
            value=f"{calidad_porcentaje:.1%}"
        )
    
    st.divider()

    # --- SECCIÓN 2: INDICADORES CLAVE DE CAMPO (NUEVA SECCIÓN) ---
    st.subheader("Resumen de Cobertura en Campo")

    # Usamos 5 columnas para que los 5 indicadores se vean bien alineados
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    kpi1.metric(label="AGEB Visitadas", value="50")
    kpi2.metric(label="Manzanas Visitadas", value="427")
    kpi3.metric(label="Viviendas Visitadas", value="12,436")
    kpi4.metric(label="Viviendas Censadas", value="5,494")
    kpi5.metric(label="Personas Censadas", value="19,641")

# --- NUEVA SECCIÓN DENTRO DE UN DESPLEGABLE ---
    with st.expander("🏘️ Ver Detalle de Avance Territorial por Manzana"):
        
        # --- FILTROS ---
        st.markdown("##### Filtros de Análisis Territorial")
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            colonias_seleccionadas = st.multiselect(
                "Selecciona Colonias:",
                options=df_manzanas["Colonia"].unique(),
                default=df_manzanas["Colonia"].unique(),
                key="manzana_colonias"
            )
        with col_filtro2:
            estatus_seleccionado = st.multiselect(
                "Selecciona Estatus de Avance:",
                options=df_manzanas["Estatus de Censado"].unique(),
                default=df_manzanas["Estatus de Censado"].unique(),
                key="manzana_estatus"
            )
        
        df_filtrado_manzanas = df_manzanas[
            (df_manzanas["Colonia"].isin(colonias_seleccionadas)) &
            (df_manzanas["Estatus de Censado"].isin(estatus_seleccionado))
        ]
        
        # --- INDICADORES CLAVE (KPIs) ---
        kpi1, kpi2, kpi3 = st.columns(3)
        df_filtrado_manzanas['Porcentaje_Num'] = df_filtrado_manzanas['Porcentaje de Censado'].str.replace('%', '').astype(float) / 100
        avance_promedio = df_filtrado_manzanas['Porcentaje_Num'].mean()

        kpi1.metric("Manzanas en Selección", value=f"{len(df_filtrado_manzanas):,}")
        kpi2.metric("Total de Viviendas", value=f"{df_filtrado_manzanas['Total de Viviendas Habitadas'].sum():,}")
        kpi3.metric("Avance Promedio", value=f"{avance_promedio:.1%}")

        # --- GRÁFICO DE RESUMEN ---
        st.markdown("##### Distribución de Manzanas por Estatus")
        conteo_estatus = df_filtrado_manzanas["Estatus de Censado"].value_counts()
        fig_estatus = px.bar(
            conteo_estatus,
            x=conteo_estatus.index,
            y=conteo_estatus.values,
            labels={'x': 'Estatus de Censado', 'y': 'Número de Manzanas'},
            color=conteo_estatus.index,
            text_auto=True
        )
        fig_estatus.update_layout(showlegend=False)
        st.plotly_chart(fig_estatus, use_container_width=True)

        # --- TABLA DE DATOS DETALLADA ---
        st.markdown("##### Detalle de Manzanas Seleccionadas")
        st.dataframe(
            df_filtrado_manzanas.drop(columns=['Porcentaje_Num']),
            use_container_width=True
        )

    
    # --- NUEVA SECCIÓN: ANÁLISIS DE DATOS DE CONTACTO (CON DATOS FIJOS) ---
    st.subheader("Calidad de Datos de Contacto")

    # Definimos las variables con los números que nos proporcionaste
    total_registros = 4269
    con_celular = 4222
    porc_celular = 0.9890
    con_correo = 1744
    porc_correo = 0.4085
    estimacion_validos_porc = 0.875
    correos_validos = 1526

    st.markdown(f"Análisis sobre el total de **{total_registros:,}** registros en la base de datos.")
    
    col_contacto1, col_contacto2 = st.columns(2)

    with col_contacto1:
        st.markdown("##### 📱 Celular")
        st.metric(
            label="Porcentaje de registros con celular",
            value=f"{porc_celular:.2%}"
        )
        st.info(f"Observaciones con celular: **{con_celular:,}**")

    with col_contacto2:
        st.markdown("##### ✉️ Correo Electrónico")
        st.metric(
            label="Porcentaje de registros con correo",
            value=f"{porc_correo:.2%}"
        )
        st.info(f"Observaciones con correo: **{con_correo:,}**")
        st.success(f"Correos válidos (estimado {estimacion_validos_porc:.1%}): **{correos_validos:,}**")
        


# --- PESTAÑA 2: CÓDIGO COMPLETO Y CORREGIDO ---
with tab2:
    st.header("Identificación y Análisis de Población Objetivo")

    # --- Diccionario de Nombres Amigables ---
    nombres_carencias = {
        "Rezago_Educativo": "Rezago Educativo",
        "Acceso_Salud": "Carencia de Acceso a la Salud",
        "Seguridad_Social": "Carencia de Acceso a la Seguridad Social",
        "Calidad_Vivienda": "Carencia por Calidad y Espacios de la Vivienda",
        "Servicios_Vivienda": "Carencia por Servicios Básicos en la Vivienda",
        "Acceso_Alimentacion": "Carencia por Acceso a la Alimentación"
    }
    lista_carencias = list(nombres_carencias.keys())

    # --- Filtros ---
    col1, col2, col3 = st.columns(3)
    with col1:
        colonia_seleccionada = st.selectbox(
            "1. Selecciona una Colonia:",
            options=["Todas"] + sorted(df_personas["Colonia"].unique())
        )
    with col2:
        sexo_seleccionado = st.selectbox(
            "2. Selecciona Sexo:",
            options=["Ambos", "Masculino", "Femenino"]
        )
    with col3:
        opcion_carencia_display = st.selectbox(
            "3. Filtra por Carencia:",
            options=["Todas las carencias"] + list(nombres_carencias.values())
        )
        carencia_seleccionada = next((key for key, value in nombres_carencias.items() if value == opcion_carencia_display), "Todas las carencias")

    rango_edad = st.slider("4. Selecciona Rango de Edad:", min_value=0, max_value=90, value=(0, 90))
    st.divider()

    # --- Lógica de filtrado ---
    df_filtrado = df_personas.copy()
    if colonia_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Colonia"] == colonia_seleccionada]
    if sexo_seleccionado != "Ambos":
        df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo_seleccionado]
    df_filtrado = df_filtrado[df_filtrado["Edad"].between(rango_edad[0], rango_edad[1])]

    # --- Lógica de Visualización ---
    if df_filtrado.empty:
        st.warning("No se encontraron registros con los criterios seleccionados.")
# --- NUEVA SECCIÓN: GRÁFICA DE PROGRAMAS SOCIALES ---
    st.divider()
    st.subheader("Beneficiarios por Programa Social (Muestra)")

    # --- DATOS FIJOS PARA LA NUEVA GRÁFICA ---
    datos_fijos_programas = {
        "Jóvenes Construyendo el Futuro": 628,
        "Beca Benito Juárez": 386,
        "Beca Rita Cetina": 383,
        "Pensión 65+": 153,
        "Mujeres Bienestar": 88
    }

    conteo_programas = pd.Series(datos_fijos_programas)

    fig_programas = px.bar(
        conteo_programas,
        x=conteo_programas.values,
        y=conteo_programas.index,
        orientation='h',
        title="Personas Beneficiarias por Programa",
        labels={'x': 'Número de Beneficiarios', 'y': 'Programa Social'},
        text_auto=True
    )
    fig_programas.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
    fig_programas.update_traces(marker_color='#4d100d')
    st.plotly_chart(fig_programas, use_container_width=True)
        
        if df_objetivo.empty:
            st.info("No hay personas con esta carencia en la selección actual.")
        else:
            st.metric(label="Total de Personas Identificadas", value=len(df_objetivo))
            st.dataframe(df_objetivo[["ID", "Colonia", "Edad", "Sexo", "Programa_Asignado", "Estatus_Operativo"]])
            st.markdown("---")
            st.markdown("#### Acciones")
            col_accion1, col_accion2 = st.columns(2)
            with col_accion1:
                @st.cache_data
                def convertir_df_a_csv(df):
                    return df.to_csv(index=False).encode('utf-8')
                csv = convertir_df_a_csv(df_objetivo[["ID", "Colonia", "Edad", "Sexo", "Programa_Asignado", "Estatus_Operativo"]])
                st.download_button(label="📥 Descargar Reporte en CSV", data=csv, file_name=f'reporte.csv', mime='text/csv', use_container_width=True)
            with col_accion2:
                st.link_button("📨 Enviar Comunicación / Gestionar", "https://construir-comunidad.bubbleapps.io/version-test/dashboard-admin", help="Abre la plataforma de gestión.", type="primary", use_container_width=True)
    else:
        st.subheader("Vista General de Carencias")
        conteo_carencias = df_filtrado[lista_carencias].sum().sort_values(ascending=False)
        conteo_carencias.index = conteo_carencias.index.map(nombres_carencias)
        fig_ranking = px.bar(conteo_carencias, x=conteo_carencias.values, y=conteo_carencias.index, orientation='h', title=f"Ranking de Carencias en: {colonia_seleccionada}", labels={'x': 'Número de Personas', 'y': 'Carencia Social'}, text_auto=True, color=conteo_carencias.values, color_continuous_scale=['#f9e5e4', '#4d100d'])
        fig_ranking.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_ranking, use_container_width=True)

    if colonia_seleccionada == "Todas":
        st.subheader("Mapa de Calor: Carencias por Colonia")
        heatmap_data = df_filtrado.groupby("Colonia")[lista_carencias].mean()
        heatmap_data.columns = heatmap_data.columns.map(nombres_carencias)
        fig_heatmap = px.imshow(heatmap_data.sort_index(), text_auto=".0%", aspect="auto", color_continuous_scale="Reds", title="Porcentaje de Población con cada Carencia por Colonia")
        st.plotly_chart(fig_heatmap, use_container_width=True)

# --- PESTAÑA 3: Con Perfil Demográfico para el Grupo Sin Cobertura ---
with tab3:
    st.header("Análisis de Cobertura y Seguimiento")

    # --- NUEVA SECCIÓN: GRÁFICA DE PROGRAMAS SOCIALES ---
    st.divider()
    st.subheader("Personas sin Programa Social")

    # --- DATOS FIJOS PARA LA NUEVA GRÁFICA ---
    datos_fijos_programas = {
        "Jóvenes Construyendo el Futuro": 628,
        "Beca Benito Juárez": 386,
        "Beca Rita Cetina": 383,
        "Pensión 65+": 153,
        "Mujeres Bienestar": 88
    }

    conteo_programas = pd.Series(datos_fijos_programas)

    fig_programas = px.bar(
        conteo_programas,
        x=conteo_programas.values,
        y=conteo_programas.index,
        orientation='h',
        title="Personas Sin Apoyo Social",
        labels={'x': 'Número de Beneficiarios', 'y': 'Programa Social'},
        text_auto=True
    )
    fig_programas.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
    fig_programas.update_traces(marker_color='#4d100d')
    st.plotly_chart(fig_programas, use_container_width=True)
    
    
    # --- SECCIÓN 1: ANÁLISIS GENERAL DE COBERTURA ---
    st.subheader("Análisis General de Cobertura por Programa")
    
    col1, col2 = st.columns(2)
    with col1:
        colonia_cobertura = st.selectbox(
            "Selecciona una Colonia:",
            options=sorted(df_personas["Colonia"].unique()),
            key="coverage_colonia",
            index=list(sorted(df_personas["Colonia"].unique())).index("Barrio Norte")
        )
    with col2:
        programas_disponibles = sorted([p for p in df_personas["Programa_Asignado"].unique() if p != "Ninguno"])
        programa_cobertura = st.selectbox(
            "Selecciona un Programa:",
            options=programas_disponibles,
            key="coverage_programa",
            index=programas_disponibles.index("IMSS Bienestar")
        )
    
    # --- Lógica de la Sección 1 ---
    df_colonia = df_personas[df_personas["Colonia"] == colonia_cobertura]
    
    beneficiarios = df_colonia[df_colonia["Programa_Asignado"] == programa_cobertura]
    poblacion_sin_programa = df_colonia[df_colonia["Programa_Asignado"] == "Ninguno"]
    
    m1, m2 = st.columns(2)
    m1.metric(f"Beneficiarios de '{programa_cobertura}'", value=len(beneficiarios))
    m2.metric("Población Total SIN Programa", value=len(poblacion_sin_programa))
    
    # Perfil de la población sin programa
    if not poblacion_sin_programa.empty:
        st.markdown(f"**Perfil de las {len(poblacion_sin_programa)} personas sin programa en {colonia_cobertura}:**")
        
        # --- NUEVA SECCIÓN DE MÉTRICAS DE PERFIL ---
        # Calculamos las estadísticas demográficas
        num_mujeres = len(poblacion_sin_programa[poblacion_sin_programa['Sexo'] == 'Femenino'])
        num_hombres = len(poblacion_sin_programa[poblacion_sin_programa['Sexo'] == 'Masculino'])
        edad_promedio = poblacion_sin_programa['Edad'].mean()

        # Las mostramos en columnas
        m_perfil1, m_perfil2, m_perfil3 = st.columns(3)
        m_perfil1.metric("Mujeres", value=f"{num_mujeres}")
        m_perfil2.metric("Hombres", value=f"{num_hombres}")
        m_perfil3.metric("Edad Promedio", value=f"{edad_promedio:.1f} años")
        # ---------------------------------------------

        # Gráfico de carencias (existente)
        st.markdown("**Carencias más comunes en este grupo:**")
        conteo_estatus_sp = poblacion_sin_programa[lista_carencias].sum().sort_values(ascending=False)
        fig_bar_sp = px.bar(
            conteo_estatus_sp,
            title="Carencias del Grupo Sin Cobertura"
        )
        fig_bar_sp.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Num. de Personas")
        fig_bar_sp.update_traces(marker_color='#b22e28')
        st.plotly_chart(fig_bar_sp, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: FUNNEL DE SEGUIMIENTO OPERATIVO (Sin cambios) ---
    st.subheader("Funnel de Avance para un Programa Específico")
    
    # ... (El resto del código del funnel se queda exactamente igual) ...
    st.markdown(f"**Seguimiento para el programa '{programa_cobertura}' en la colonia '{colonia_cobertura}'**")
    df_seguimiento = df_personas[df_personas["Colonia"] == colonia_cobertura]
    conteo_estatus = df_seguimiento["Estatus_Operativo"].value_counts()
    data_funnel = {
        'Estatus': ["Por contactar", "Pre-registro completo", "Cita generada", "Visita programada"],
        'Cantidad': [ conteo_estatus.get("Por contactar", 0), conteo_estatus.get("Pre-registro completo", 0), conteo_estatus.get("Cita generada", 0), conteo_estatus.get("Visita programada", 0) ]
    }
    total_a_contactar = sum(data_funnel['Cantidad'])
    data_funnel['Cantidad'].insert(0, total_a_contactar)
    data_funnel['Estatus'].insert(0, 'Total Pendiente')
    fig_funnel = px.funnel( data_funnel, x='Cantidad', y='Estatus', title=f"Avance de Cobertura en {colonia_cobertura}" )
    fig_funnel.update_traces(marker={"color": ['#77100d', '#b22e28', '#d66058', '#f7b2ac', '#fdecea']})
    st.plotly_chart(fig_funnel, use_container_width=True)

# --- PESTAÑA 4: Mapa Operativo con Leyenda Mejorada ---
with tab4:
    st.header("Mapa de Seguimiento Operativo")
    st.markdown("Visualiza el estatus de contacto de la población objetivo en el territorio.")
    
    # ... (código de filtros sin cambios) ...
    col1, col2 = st.columns(2)
    with col1:
        colonia_mapa = st.selectbox( "Colonia a visualizar:", options=sorted(df_personas["Colonia"].unique()), key="map_colonia", index=list(sorted(df_personas["Colonia"].unique())).index("Barrio Norte") )
    with col2:
        carencia_mapa = st.selectbox( "Carencia a visualizar:", options=lista_carencias, key="map_carencia", index=lista_carencias.index("Acceso_Salud") )
    
    st.divider()
    
    df_mapa_operativo = df_personas[
        (df_personas["Colonia"] == colonia_mapa) &
        (df_personas[carencia_mapa] == 1) &
        (df_personas["Programa_Asignado"] == "Ninguno") # Solo mostramos a los pendientes en el mapa
    ]
    
    # --- LEYENDA DEL MAPA MEJORADA Y A PRUEBA DE FALLOS ---
    st.markdown("#### Leyenda de Estatus de Contacto")
    # Usamos Emojis y texto, que siempre se renderizan correctamente.
    st.markdown("""
    - 🔴 **Por contactar**
    - 🟠 **Pre-registro completo**
    - 🔵 **Cita generada**
    - 🟢 **Visita programada**
    """)
    st.divider()

    if df_mapa_operativo.empty:
        st.info("No hay población pendiente de contactar en esta selección.")
    else:
        # Mapeo de estatus a un color
        colors = {
            "Por contactar": [214, 39, 40], # Rojo
            "Pre-registro completo": [255, 127, 14], # Naranja
            "Cita generada": [31, 119, 180], # Azul
            "Visita programada": [44, 160, 44] # Verde
        }
        
        layers = []
        for estatus, df_group in df_mapa_operativo.groupby('Estatus_Operativo'):
            layers.append(pdk.Layer(
                'ScatterplotLayer',
                data=df_group,
                get_position='[Longitud, Latitud]',
                get_fill_color=colors.get(estatus, [128, 128, 128]), # Color gris si no se encuentra
                get_radius=30,
                radius_min_pixels=5,
                pickable=True,
                tooltip={"text": "Estatus: {Estatus_Operativo}\nID: {ID}"}
            ))

        view_state = pdk.ViewState( latitude=df_mapa_operativo["Latitud"].mean(), longitude=df_mapa_operativo["Longitud"].mean(), zoom=14, pitch=50 )
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10", initial_view_state=view_state, layers=layers))