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
     

# --- FUNCIÓN DE GENERACIÓN DE DATOS UNIFICADA ---

@st.cache_data
def generar_datos_unificados(num_manzanas_por_colonia=15):
    """
    Actualiza los estatus operativos para el nuevo funnel.
    """
    # 1. UNIVERSO DE DATOS (ÚNICA FUENTE DE VERDAD)
    colonias_data = {
        "Barrio Norte": ["10350"], "Jalalpa": ["10400", "10401"], "Lomas de Becerra S1": ["10370"],
        "El Rodeo": ["10500"], "Golondrinas": ["10510"], "Tlacoyaque": ["10600"], "Santa Lucía": ["10700"]
    }
    programas = ["Beca Benito Juárez", "Pensión Adulto Mayor", "IMSS Bienestar", "Beca Rita Cetina", "Ninguno"]
    # --- LISTA DE ESTATUS ACTUALIZADA ---
    estatus_operativos = ["Por contactar", "Personas contactadas", "Personas con visita de promotor", "Personas con afiliación al programa"]
    
    
    # --- 2. GENERAR DATOS DE MANZANAS ---
    manzanas_list = []
    # (El código para generar df_manzanas se queda exactamente igual que en la versión anterior)
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

    # --- 3. GENERAR DATOS DE PERSONAS (CON NUEVOS CAMPOS) ---
    personas_list = []
    # (La inyección de datos para la narrativa también se actualiza)
    manzana_narrativa = df_manzanas[df_manzanas["Colonia"] == "Barrio Norte"].iloc[0]
    for i in range(20):
        personas_list.append({
            "ID": np.random.randint(9000, 9999), "Colonia": "Barrio Norte", "ID_Manzana": manzana_narrativa["ID_Manzana"],
            "ID_Vivienda": f"{manzana_narrativa['ID_Manzana']}-{i//3}", # Simula 3 personas por vivienda
            "Latitud": 19.38 + np.random.normal(0, 0.001), "Longitud": -99.18 + np.random.normal(0, 0.001),
            "Celular": f"55{np.random.randint(10000000, 99999999)}" if np.random.rand() > 0.1 else None,
            "Correo": f"persona.{np.random.randint(1,100)}@email.com" if np.random.rand() > 0.4 else None,
            "Edad": np.random.randint(24, 36), "Sexo": "Femenino", "Tiene_Bebes": 1, "Es_Adulto_Mayor": 0, "Rezago_Educativo": 0, "Acceso_Salud": 1,
            "Seguridad_Social": 1, "Calidad_Vivienda": 0, "Servicios_Vivienda": 0, "Acceso_Alimentacion": 0,
            "Programa_Asignado": np.random.choice(["IMSS Bienestar", "Ninguno"], p=[0.4, 0.6]),
            "Estatus_Operativo": np.random.choice(estatus_operativos)
        })

    # (El resto de la generación de personas también se actualiza)
    for _, manzana_row in df_manzanas.iterrows():
        for i in range(manzana_row["Viviendas Censadas"]):
            edad = np.random.randint(0, 90)
            rezago_edu = np.random.choice([0, 1], p=[0.7, 0.3])
            acceso_salud_rand = np.random.choice([0, 1], p=[0.6, 0.4])
            programa_asignado, estatus = "Ninguno", np.random.choice(estatus_operativos)
            if edad >= 65 and np.random.rand() > 0.3: programa_asignado, estatus = "Pensión Adulto Mayor", "Cubierto"
            elif rezago_edu == 1 and edad < 25 and np.random.rand() > 0.5: programa_asignado, estatus = np.random.choice(["Beca Benito Juárez", "Beca Rita Cetina"]), "Cubierto"
            elif acceso_salud_rand == 1 and np.random.rand() > 0.6: programa_asignado, estatus = "IMSS Bienestar", "Cubierto"
            
            personas_list.append({
                "ID": int(f"{manzana_row['AGEB']}{i}"), "Colonia": manzana_row["Colonia"], "ID_Manzana": manzana_row["ID_Manzana"],
                "ID_Vivienda": f"{manzana_row['ID_Manzana']}-{i//np.random.randint(1,4)}", # Simula de 1 a 3 personas por vivienda
                "Latitud": 19.35 + np.random.normal(0, 0.05), "Longitud": -99.22 + np.random.normal(0, 0.05),
                "Celular": f"55{np.random.randint(10000000, 99999999)}" if np.random.rand() > 0.1 else None, # 10% sin celular
                "Correo": f"user.{i}@{manzana_row['Colonia'].split()[0].lower()}.com" if np.random.rand() > 0.5 else None, # 50% sin correo
                "Edad": edad, "Sexo": np.random.choice(["Masculino", "Femenino"]),
                "Tiene_Bebes": 1 if 18 <= edad <= 45 and np.random.rand() > 0.8 else 0, "Es_Adulto_Mayor": 1 if edad >= 65 else 0,
                "Rezago_Educativo": rezago_edu, "Acceso_Salud": acceso_salud_rand,
                "Seguridad_Social": np.random.choice([0, 1], p=[0.5, 0.5]), "Calidad_Vivienda": np.random.choice([0, 1], p=[0.8, 0.2]),
                "Servicios_Vivienda": np.random.choice([0, 1], p=[0.85, 0.15]), "Acceso_Alimentacion": np.random.choice([0, 1], p=[0.75, 0.25]),
                "Programa_Asignado": programa_asignado, "Estatus_Operativo": estatus,
            })
            
    df_personas = pd.DataFrame(personas_list)
    df_personas['Tiene_Programa_Social'] = df_personas['Programa_Asignado'].apply(lambda x: 0 if x == 'Ninguno' else 1)
    
    return df_manzanas, df_personas



# --- CARGA DE DATOS ---
df_manzanas, df_personas = generar_datos_unificados()
CASAS_OBREGONENSES = {
    "Casa Comunitaria La Cebada": {"lat": 19.37961, "lon": -99.23361},
    "Biblioteca Pública José Revueltas": {"lat": 19.35257, "lon": -99.23525},
    "Gimnasio Torres de Potrero": {"lat": 19.33011, "lon": -99.25123}
}

# --- TÍTULO PRINCIPAL ---
st.title("📊 Seguimiento CENSO PAPE Álvaro Obregón")
st.markdown("Este es un ejemplo con **datos ficticios** para validar las funcionalidades clave en el taller de discovery.")

# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Pulso General",
    "🎯 Identificación",
    "☂️ Cobertura",
    "🗺️ Mapa Operativo",
    "🏘️ Casas Obregonenses"
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
        

# --- PESTAÑA 2: CÓDIGO CORREGIDO Y REORDENADO ---

# --- PESTAÑA 2: VISTA GENERAL FIJA + ANÁLISIS INTERACTIVO ---
with tab2:
    st.header("Análisis de Carencias Sociales")

    # --- SECCIÓN 1: VISTA GENERAL CON DATOS FIJOS (SIEMPRE VISIBLE) ---
    st.subheader("Vista General de Carencias (Muestra)")

    datos_fijos_carencias = {
        "Carencia en seguridad social": 12498,
        "Carencia en alimentación": 6936,
        "Carencia en educación": 4384,
        "Carencia de calidad de vivienda": 2122,
        "Carencia de servicios básicos": 936
    }
    conteo_carencias_fijas = pd.Series(datos_fijos_carencias)

    fig_ranking_fijo = px.bar(
        conteo_carencias_fijas,
        x=conteo_carencias_fijas.values,
        y=conteo_carencias_fijas.index,
        orientation='h',
        title="Ranking de Carencias Sociales",
        labels={'x': 'Número de Personas', 'y': 'Carencia Social'},
        text_auto=True,
        color=conteo_carencias_fijas.values,
        color_continuous_scale=['#f9e5e4', '#4d100d']
    )
    fig_ranking_fijo.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ranking_fijo, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: IDENTIFICACIÓN DE POBLACIÓN OBJETIVO (INTERACTIVA) ---
    st.header("Identificación y Análisis Detallado")
    
    # Diccionario de Nombres Amigables
    nombres_carencias = {
        "Rezago_Educativo": "Rezago Educativo", "Acceso_Salud": "Carencia de Acceso a la Salud",
        "Seguridad_Social": "Carencia de Acceso a la Seguridad Social", "Calidad_Vivienda": "Carencia por Calidad y Espacios de la Vivienda",
        "Servicios_Vivienda": "Carencia por Servicios Básicos en la Vivienda", "Acceso_Alimentacion": "Carencia por Acceso a la Alimentación"
    }
    lista_carencias = list(nombres_carencias.keys())

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        colonia_seleccionada = st.selectbox("1. Selecciona una Colonia:", options=["Todas"] + sorted(df_personas["Colonia"].unique()))
    with col2:
        sexo_seleccionado = st.selectbox("2. Selecciona Sexo:", options=["Ambos", "Masculino", "Femenino"])
    with col3:
        opcion_carencia_display = st.selectbox("3. Filtra por Carencia:", options=["Todas las carencias"] + list(nombres_carencias.values()))
        carencia_seleccionada = next((key for key, value in nombres_carencias.items() if value == opcion_carencia_display), "Todas las carencias")

    rango_edad = st.slider("4. Selecciona Rango de Edad:", min_value=0, max_value=90, value=(0, 90))
    st.divider()

    # Lógica de filtrado
    df_filtrado = df_personas.copy()
    if colonia_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Colonia"] == colonia_seleccionada]
    if sexo_seleccionado != "Ambos":
        df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo_seleccionado]
    df_filtrado = df_filtrado[df_filtrado["Edad"].between(rango_edad[0], rango_edad[1])]

    # Lógica de Visualización
    if df_filtrado.empty:
        st.warning("No se encontraron registros con los criterios seleccionados.")
    elif carencia_seleccionada != "Todas las carencias":
        nombre_amigable = nombres_carencias[carencia_seleccionada]
        st.subheader(f"Población Objetivo: {nombre_amigable}")
        
        df_objetivo = df_filtrado[df_filtrado[carencia_seleccionada] == 1]
        
        if df_objetivo.empty:
            st.info("No hay personas con esta carencia en la selección actual.")
        else:
            st.metric(label="Total de Personas Identificadas", value=len(df_objetivo))
            st.dataframe(df_objetivo[["ID", "Colonia", "ID_Vivienda", "Edad", "Sexo", "Celular", "Correo"]])
            st.markdown("---")
            st.markdown("#### Acciones")
            
            col_accion1, col_accion2, col_accion3 = st.columns(3)

            @st.cache_data
            def convertir_df_a_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            with col_accion1:
                csv_individual = convertir_df_a_csv(df_objetivo[["ID", "Colonia", "Edad", "Celular", "Correo", "Latitud", "Longitud"]])
                st.download_button(label="📥 Reporte Individual", data=csv_individual, file_name='reporte_individual_contacto.csv', mime='text/csv', help="Descarga la lista de personas con sus datos de contacto y ubicación.", use_container_width=True)

            with col_accion2:
                df_vivienda = df_objetivo.groupby('ID_Vivienda').agg(Colonia=('Colonia', 'first'), Latitud=('Latitud', 'mean'), Longitud=('Longitud', 'mean'), Miembros_en_Objetivo=('ID', 'count'), Miembros_Sin_Correo=('Correo', lambda x: x.isna().sum()), Miembros_Sin_Celular=('Celular', lambda x: x.isna().sum())).reset_index()
                csv_vivienda = convertir_df_a_csv(df_vivienda)
                st.download_button(label="🏘️ Reporte por Vivienda", data=csv_vivienda, file_name='reporte_agregado_vivienda.csv', mime='text/csv', help="Descarga un reporte agregado por vivienda para el enrolamiento en campo.", use_container_width=True)

            with col_accion3:
                st.link_button("📨 Gestionar Comunicación", "https://construir-comunidad.bubbleapps.io/version-test/dashboard-admin", help="Abre la plataforma de gestión para contactar a la población seleccionada.", type="primary", use_container_width=True)
    
    else: # Si están seleccionadas "Todas las carencias"
        st.info("👆 Utiliza los filtros de arriba para identificar y analizar un grupo específico de la población.")

    if colonia_seleccionada == "Todas":
        st.subheader("Mapa de Calor: Carencias por Colonia (Dinámico)")
        heatmap_data = df_filtrado.groupby("Colonia")[lista_carencias].mean()
        heatmap_data.columns = heatmap_data.columns.map(nombres_carencias)
        fig_heatmap = px.imshow(heatmap_data.sort_index(), text_auto=".0%", aspect="auto", color_continuous_scale="Reds")
        st.plotly_chart(fig_heatmap, use_container_width=True)    

# --- PESTAÑA 3: COBERTURA Y FUNNEL DE AFILIACIÓN ---
with tab3:
    st.header("Análisis de Cobertura y Seguimiento de Afiliación")

    # --- SECCIÓN 1: ANÁLISIS GENERAL DE COBERTURA ---
    st.subheader("Cobertura General por Programa")
    
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
    
    # Se eliminó la gráfica de barras de esta sección.

    st.divider()

    # --- SECCIÓN 2: FUNNEL DE SEGUIMIENTO CON NUEVA NARRATIVA ---
    st.subheader(f"Funnel de Afiliación para '{programa_cobertura}'")
    st.markdown(f"De las **{len(poblacion_sin_programa)}** personas sin programa en **{colonia_cobertura}**, este es el avance:")

    # Contamos cuántas personas hay en cada nuevo estatus
    conteo_estatus = poblacion_sin_programa["Estatus_Operativo"].value_counts()
    
    # Preparamos los datos para el funnel en el orden correcto
    afiliados = conteo_estatus.get("Personas con afiliación al programa", 0)
    con_visita = afiliados + conteo_estatus.get("Personas con visita de promotor", 0)
    contactados = con_visita + conteo_estatus.get("Personas contactadas", 0)
    total_por_cubrir = contactados + conteo_estatus.get("Por contactar", 0)
    
    data_funnel = {
        'Estatus': [
            "Total por cubrir",
            "Personas contactadas",
            "Personas con visita de promotor",
            "Personas con afiliación al programa"
        ],
        'Cantidad': [total_por_cubrir, contactados, con_visita, afiliados]
    }
    
    # Mostramos el funnel solo si hay personas por cubrir
    if total_por_cubrir > 0:
        fig_funnel = px.funnel(
            data_funnel,
            x='Cantidad',
            y='Estatus',
            title=f"Avance de Afiliación a {programa_cobertura} en {colonia_cobertura}"
        )
        fig_funnel.update_traces(marker={"color": ['#77100d', '#b22e28', '#d66058', '#f7b2ac']})
        st.plotly_chart(fig_funnel, use_container_width=True)
    else:
        st.success("¡No hay personas pendientes de afiliar en esta colonia!")    



# --- PESTAÑA 4: MAPA OPERATIVO (VINCULADO AL FUNNEL) ---
with tab4:
    st.header("Mapa de Seguimiento Operativo del Funnel")
    st.markdown("Visualización geográfica del avance de afiliación para la población sin programa.")
    
    # --- Filtros ---
    col1, col2 = st.columns(2)
    with col1:
        colonia_mapa = st.selectbox(
            "Colonia a visualizar:",
            options=sorted(df_personas["Colonia"].unique()),
            key="map_op_colonia",
            index=list(sorted(df_personas["Colonia"].unique())).index("Barrio Norte")
        )
    with col2:
        carencia_mapa = st.selectbox(
            "Carencia a analizar:",
            options=list(nombres_carencias.values()),
            key="map_op_carencia",
            index=list(nombres_carencias.values()).index("Carencia de Acceso a la Salud")
        )
        carencia_key_mapa = next((key for key, value in nombres_carencias.items() if value == carencia_mapa), None)

    st.divider()
    
    # Filtrar la población objetivo que NO está cubierta
    df_mapa_operativo = df_personas[
        (df_personas["Colonia"] == colonia_mapa) &
        (df_personas[carencia_key_mapa] == 1) &
        (df_personas["Programa_Asignado"] == "Ninguno")
    ]
    
    # --- Leyenda del Mapa (vinculada a los estatus del funnel) ---
    st.markdown("#### Leyenda de Estatus del Funnel")
    st.markdown("""
    - 🔴 **Por contactar** (Inicio del funnel)
    - 🟠 **Personas contactadas**
    - 🔵 **Personas con visita de promotor**
    - 🟢 **Personas con afiliación al programa** (Éxito del funnel)
    """)
    st.divider()

    if df_mapa_operativo.empty:
        st.info("No hay población pendiente de contactar en esta selección.")
    else:
        # Mapeo de los nuevos estatus a colores
        colors = {
            "Por contactar": [214, 39, 40], # Rojo
            "Personas contactadas": [255, 127, 14], # Naranja
            "Personas con visita de promotor": [31, 119, 180], # Azul
            "Personas con afiliación al programa": [44, 160, 44] # Verde
        }
        
        layers = []
        for estatus, df_group in df_mapa_operativo.groupby('Estatus_Operativo'):
            if estatus in colors: # Solo graficar los estatus que tenemos en el funnel
                layers.append(pdk.Layer(
                    'ScatterplotLayer', data=df_group, get_position='[Longitud, Latitud]',
                    get_fill_color=colors[estatus], get_radius=30,
                    radius_min_pixels=5, pickable=True,
                    tooltip={"text": "Estatus: {Estatus_Operativo}\nID: {ID}"}
                ))

        view_state = pdk.ViewState(latitude=df_mapa_operativo["Latitud"].mean(), longitude=df_mapa_operativo["Longitud"].mean(), zoom=14, pitch=50)
        
# --- CAMBIO DE ESTILO DEL MAPA (MÉTODO DIRECTO) ---
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v10",
            initial_view_state=view_state,
            layers=layers,
            # --- AÑADE ESTA LÍNEA CON TU CLAVE ---
            api_keys={'mapbox': 'pk.eyJ1Ijoib210ZWdvIiwiYSI6ImNtZGUwbnpjYjBhcjgyaXB4Y2F2aGd0YnIifQ.SsW2a_INxbQpciezR9FXww'}
        ))



# --- PESTAÑA 5: ANÁLISIS DE DEMANDA ALREDEDOR DE CASAS OBREGONENSES ---
# --- PESTAÑA 5: ANÁLISIS DE DEMANDA (CÓDIGO CORREGIDO) ---
with tab5:
    st.header("Análisis de Necesidades alrededor de Centros Comunitarios")
    st.markdown("Identifica la demanda potencial de servicios en el área de influencia de cada centro.")

    # (El diccionario CASAS_OBREGONENSES debe estar definido al principio del script)
    
    # --- FILTROS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        casa_seleccionada_nombre = st.selectbox("Selecciona un Centro Comunitario:", options=list(CASAS_OBREGONENSES.keys()))
    with col2:
        radio_km = st.slider("Selecciona un radio de búsqueda (km):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    with col3:
        carencia_seleccionada_casas = st.selectbox("Selecciona una Carencia a analizar:", options=list(nombres_carencias.values()), key="casas_carencia")
        carencia_key_casas = next((key for key, value in nombres_carencias.items() if value == carencia_seleccionada_casas), None)

    st.divider()

    # --- LÓGICA DE CÁLCULO DE PROXIMIDAD ---
    # (La función haversine y los cálculos de df_demanda no cambian)
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1; dlat = lat2 - lat1
        a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6371 * c

    casa_seleccionada_coords = CASAS_OBREGONENSES[casa_seleccionada_nombre]
    df_personas['distancia_km'] = haversine(casa_seleccionada_coords['lon'], casa_seleccionada_coords['lat'], df_personas['Longitud'], df_personas['Latitud'])
    df_cercanos = df_personas[df_personas['distancia_km'] <= radio_km]
    df_demanda = df_cercanos[df_cercanos[carencia_key_casas] == 1] if carencia_key_casas else pd.DataFrame()

    # --- RESULTADOS Y VISUALIZACIÓN ---
    st.subheader(f"Análisis para '{casa_seleccionada_nombre}'")
    if df_demanda.empty:
        st.warning(f"No se encontraron personas con '{carencia_seleccionada_casas}' en un radio de {radio_km} km.")
    else:
        st.metric(label=f"Personas con {carencia_seleccionada_casas}", value=f"{len(df_demanda)}", help=f"Dentro de un radio de {radio_km} km.")

        # --- CAMBIO IMPORTANTE: Crear un DataFrame solo para la casa seleccionada ---
        df_casa_seleccionada = pd.DataFrame([{
            "nombre": casa_seleccionada_nombre,
            "lat": casa_seleccionada_coords['lat'],
            "lon": casa_seleccionada_coords['lon']
        }])

        # Capa para la Casa Obregonense seleccionada (punto dorado)
        capa_casa = pdk.Layer(
            "ScatterplotLayer",
            data=df_casa_seleccionada, # Usamos el nuevo DataFrame
            get_position="[lon, lat]",
            get_color="[255, 215, 0, 255]",
            get_radius=100,
            pickable=True,
            tooltip={"text": "{nombre}"}
        )
        
        # Capa para las personas con la necesidad (puntos rojos)
        capa_demanda = pdk.Layer(
            "ScatterplotLayer",
            data=df_demanda,
            get_position="[Longitud, Latitud]",
            get_color="[214, 39, 40, 160]",
            get_radius=25,
            pickable=True,
            tooltip={"text": "ID: {ID}\nEdad: {Edad}"}
        )

        view_state = pdk.ViewState(latitude=casa_seleccionada_coords['lat'], longitude=casa_seleccionada_coords['lon'], zoom=14, pitch=50)
        
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=view_state,
            # --- CAMBIO IMPORTANTE: Dibujar la capa de la casa al final para que quede encima ---
            layers=[capa_demanda, capa_casa],
            api_keys={'mapbox': 'pk.eyJ1Ijoib210ZWdvIiwiYSI6ImNtZGUwbnpjYjBhcjgyaXB4Y2F2aGd0YnIifQ.SsW2a_INxbQpciezR9FXww'}
        ))