import streamlit as st

from hashlib import sha256

from procesamiento import FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones, resumir_actividad, filtrar_trazabilidad, DIAS_SEMANA, resumir_horarios

def mostrar_inicio(paginas):
    st.title("Seguimiento académico")

    st.write(
        "Seleccioná una vista para consultar "
        "la información académica."
    )

    dashboards = [
        (
            "general",
            "General",
            "Resumen y comparación de indicadores entre materias.",
        ),
        (
            "participacion",
            "Participación",
            "Actividad, avance y tiempo de uso de los alumnos.",
        ),
        (
            "trazabilidad",
            "Trazabilidad",
            "Detalle de interacciones y distribución temporal.",
        ),
        (
            "rendimiento",
            "Rendimiento académico",
            "Calificaciones y situación académica por materia.",
        ),
        (
            "relacion",
            "Notas y participación",
            "Relación entre actividad y rendimiento académico.",
        ),
        (
            "individual",
            "Individual",
            "Información integrada de un estudiante.",
        ),
        (
            "matricula",
            "Matrícula y alertas",
            "Inscripciones y comparación con la actividad del aula.",
        ),
    ]

    for inicio in range(0, len(dashboards), 3):
        columnas = st.columns(3)

        for columna, dashboard in zip(
            columnas,
            dashboards[inicio:inicio + 3],
        ):
            clave, titulo, descripcion = dashboard

            with columna:
                with st.container(border=True):
                    st.subheader(titulo)
                    st.write(descripcion)

                    disponible = clave in paginas

                    st.caption(
                        "Vista inicial disponible"
                        if disponible
                        else "En preparación"
                    )

                    if st.button(
                        "Abrir vista",
                        key=f"abrir_{clave}",
                        disabled=not disponible,
                        width="stretch",
                    ):
                        st.switch_page(paginas[clave])

def mostrar_matricula(
    matriculados,
    matricula_actual,
    base_alumnos,
):
    poblacion = st.radio(
        "Población a consultar",
        options=list(FILTROS_POBLACION),
        horizontal=True,
        key="matricula_poblacion",
    )

    alumnos_seleccionados = seleccionar_poblacion(
        base_alumnos,
        poblacion,
    )

    campos_filtro = [
        "Situación de matrícula",
        "Situación de actividad",
        "Alerta",
    ]

    filtros = {}

    for contenedor, columna in zip(
        st.columns(3),
        campos_filtro,
    ):
        opciones = ["Todas"] + sorted(
            alumnos_seleccionados[columna]
            .dropna()
            .unique()
            .tolist()
        )

        with contenedor:
            filtros[columna] = st.selectbox(
                columna,
                options=opciones,
                key=f"matricula_filtro_{columna}",
            )

    alumnos_seleccionados = filtrar_situaciones(
        alumnos_seleccionados,
        filtros,
    )

    cantidad = len(alumnos_seleccionados)

    cantidad_alertas = int(alumnos_seleccionados["Tiene alerta"].sum())

    vigentes = int(
        alumnos_seleccionados["Matrícula vigente"].sum()
    )

    con_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .eq(True)
        .sum()
    )

    sin_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .eq(False)
        .sum()
    )

    sin_dato_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .isna()
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Estudiantes seleccionados",
        cantidad,
    )

    col2.metric(
        "Con matrícula vigente",
        vigentes,
    )

    col3.metric(
        "Con actividad registrada",
        con_actividad,
    )

    col4.metric(
        "Sin actividad registrada",
        sin_actividad,
    )

    st.caption(
        f"Población seleccionada: {poblacion}. "
        "Los indicadores y la tabla corresponden "
        "a esa población. Con actividad significa "
        "al menos una interacción en el período del reporte."
    )

    if cantidad == 0:
        st.info(
            "No hay estudiantes que coincidan "
            "con la combinación de filtros."
        )
    elif cantidad_alertas:
        st.warning(
            f"{cantidad_alertas} estudiantes requieren "
            "revisión según los criterios de alerta "
            "y los filtros seleccionados."
        )

        st.caption(
            "La actividad corresponde al período completo "
            "del reporte y puede ser anterior a una baja."
        )

    if sin_dato_actividad:
        st.info(
            f"Hay {sin_dato_actividad} estudiantes cuya "
            "actividad no se puede determinar. "
            "Consultá su situación en la tabla."
        )

    columnas = [
        "Identificación",
        "Estudiante",
        "Situación de matrícula",
        "Situación de actividad",
        "Alerta",
        "Interacciones",
        "Última interacción",
    ]

    st.dataframe(
        alumnos_seleccionados[columnas],
        hide_index=True,
    )

    with st.expander("Ver historial de matrícula"):
        st.caption(
            f"{len(matriculados)} registros originales; "
            f"{len(matricula_actual)} estudiantes únicos "
            "después de consolidar el historial."
        )

        st.dataframe(
            matriculados,
            hide_index=True,
        )

def mostrar_participacion(participacion, participacion_alumnos):
    cantidad_alumnos = len(participacion_alumnos)

    con_actividad = int(
        participacion_alumnos["Con actividad"].sum()
    )

    sin_actividad = cantidad_alumnos - con_actividad

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Usuarios en el reporte",
        len(participacion),
    )

    col2.metric(
        "Alumnos",
        cantidad_alumnos,
    )

    col3.metric(
        "Alumnos con actividad",
        con_actividad,
    )

    col4.metric(
        "Alumnos sin actividad",
        sin_actividad,
    )

    st.caption(
        "Con actividad: al menos una interacción registrada "
        "en el período del reporte."
    )

    st.dataframe(
        participacion_alumnos,
        hide_index=True,
    )

    with st.expander("Ver reporte con todos los perfiles"):
        reporte_visual = participacion.assign(
            Avance = participacion["Avance"].astype("string")
        )

        st.dataframe(
            reporte_visual,
            hide_index=True,
        )

def mostrar_trazabilidad(trazabilidad, trazabilidad_alumnos,):
    if trazabilidad_alumnos.empty:
        st.info(
            "El reporte no contiene registros de alumnos."
        )
        return

    fecha_min = (
        trazabilidad_alumnos["Fecha"].min().date()
    )

    fecha_max = (
        trazabilidad_alumnos["Fecha"].max().date()
    )

    periodo = st.date_input(
        "Período a consultar",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        format="DD/MM/YYYY",
        key=(
            f"trazabilidad_periodo_"
            f"{fecha_min}_{fecha_max}"
        ),
    )

    usuarios = (
        trazabilidad_alumnos[
            ["Usuario", "Apellido", "Nombre"]
        ]
        .drop_duplicates(subset="Usuario")
        .sort_values("Usuario")
    )

    etiquetas = {
        usuario: f"{usuario} - {apellido}, {nombre}"
        for usuario, apellido, nombre
        in usuarios.itertuples(
            index=False,
            name=None,
        )
    }

    usuario_seleccionado = st.selectbox(
        "Estudiante",
        options=[None] + list(etiquetas),
        format_func=lambda usuario: (
            "Todos"
            if usuario is None
            else etiquetas[usuario]
        ),
        key="trazabilidad_estudiante",
        help=(
            "La lista incluye a los alumnos con registros "
            "en el reporte completo de esta materia."
        ),
    )

    if len(periodo) != 2:
        st.info(
            "Seleccioná la fecha de inicio y la fecha final."
        )
        return

    trazabilidad_alumnos = filtrar_trazabilidad(
        trazabilidad_alumnos,
        periodo[0],
        periodo[1],
        usuario_seleccionado,
    )

    if trazabilidad_alumnos.empty:
        st.info(
            "No hay registros para el período "
            "y estudiante seleccionados."
        )

    cantidad_repeticiones = int(
        trazabilidad_alumnos[
            "Repetición exacta adicional"
        ].sum()
    )

    cantidad_alumnos = (
        trazabilidad_alumnos["Usuario"].nunique()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Registros del reporte (total)",
        len(trazabilidad),
    )

    col2.metric(
        "Registros seleccionados",
        len(trazabilidad_alumnos),
    )

    col3.metric(
        "Alumnos con eventos",
        cantidad_alumnos,
    )

    col4.metric(
        "Repeticiones exactas adicionales",
        cantidad_repeticiones,
    )

    st.caption(
        "El total del reporte incluye todos los perfiles "
        "y no cambia con los filtros. "
        "Los otros indicadores, resúmenes y detalle "
        "corresponden al período y estudiante seleccionados. "
        "Las repeticiones marcadas permanecen incluidas."
    )

    configuracion = [
        ("Por día", "Día"),
        ("Por semana", "Semana"),
        ("Por acción", "Acción"),
    ]

    pestanas = st.tabs(
        ["Mapa horario"]
        + [
            titulo
            for titulo, campo in configuracion
        ]
        + ["Detalle"]
    )

    with pestanas[0]:
        if not trazabilidad_alumnos.empty:
            horarios = resumir_horarios(
                trazabilidad_alumnos
            )

            firma_mapa = sha256(
                horarios.to_json(
                    orient="split"
                ).encode("utf-8")
            ).hexdigest()

            st.vega_lite_chart(
                horarios,
                spec={
                    "name": f"mapa_horario_{firma_mapa}",
                    "mark": "rect",
                    "encoding": {
                        "x": {
                            "field": "Hora",
                            "type": "ordinal",
                            "title": "Hora del día",
                            "sort": list(range(24)),
                        },
                        "y": {
                            "field": "Nombre del día",
                            "type": "ordinal",
                            "title": None,
                            "sort": DIAS_SEMANA,
                        },
                        "color": {
                            "field": "Registros",
                            "type": "quantitative",
                            "title": "Registros",
                            "scale": {
                                "scheme": "blues",
                                "zero": True,
                            },
                        },
                        "tooltip": [
                            {
                                "field": "Nombre del día",
                                "type": "nominal",
                                "title": "Día",
                            },
                            {
                                "field": "Hora",
                                "type": "ordinal",
                                "title": "Hora",
                            },
                            {
                                "field": "Registros",
                                "type": "quantitative",
                                "title": "Registros",
                                "format": ",.0f",
                            },
                        ],
                    },
                },
                width="stretch",
                height=260,
            )

            st.caption(
                "Cada celda suma los registros de ese día "
                "de semana y esa hora dentro de la selección. "
                "Por ejemplo, la hora 20 comprende "
                "desde las 20:00 hasta antes de las 21:00. "
                "Las repeticiones marcadas están incluidas."
            )

    for pestana, configuracion_actual in zip(
        pestanas[1:],
        configuracion,
    ):
        titulo, campo = configuracion_actual

        with pestana:
            resumen = resumir_actividad(
                trazabilidad_alumnos,
                campo,
            )

            if campo == "Acción" and not resumen.empty:
                st.bar_chart(
                    resumen.head(10),
                    x="Acción",
                    y="Registros",
                    horizontal=True,
                    sort="-Registros",
                    height=350,
                )

                st.caption(
                    "El gráfico muestra hasta diez acciones "
                    "con más registros. "
                    "La tabla conserva todas las acciones."
                )

            st.dataframe(
                resumen,
                hide_index=True,
            )

    with pestanas[-1]:
        st.dataframe(
            trazabilidad_alumnos,
            hide_index=True,
        )

    with st.expander(
        "Ver reporte original con todos los perfiles"
    ):
        st.dataframe(
            trazabilidad,
            hide_index=True,
        )