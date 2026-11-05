import streamlit as st

from procesamiento import FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones

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