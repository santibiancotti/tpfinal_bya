import streamlit as st

from datos import detectar_materias, leer_matriculados,  leer_participacion, leer_trazabilidad, leer_calificaciones


from procesamiento import consolidar_matricula, preparar_participacion, cruzar_matricula_participacion, clasificar_alertas, preparar_trazabilidad, preparar_calificaciones


from vistas import mostrar_inicio, mostrar_matricula, mostrar_participacion, mostrar_trazabilidad, mostrar_rendimiento, mostrar_individual


st.set_page_config(
    page_title="Seguimiento académico",
    layout="wide",
)


def pagina_inicio():
    mostrar_inicio(paginas)


def pagina_matricula():
    materia = st.session_state["materia_actual"]

    try:
        matriculados = leer_matriculados(materia)

        matricula_actual = consolidar_matricula(
            matriculados
        )

        participacion = leer_participacion(materia)

        participacion_alumnos = preparar_participacion(
            participacion
        )

        base_alumnos = cruzar_matricula_participacion(
            matricula_actual,
            participacion_alumnos,
        )

        base_alumnos = clasificar_alertas(base_alumnos)
        
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_matricula(
        matriculados,
        matricula_actual,
        base_alumnos,
    )


def pagina_participacion():
    materia = st.session_state["materia_actual"]

    try:
        participacion = leer_participacion(materia)
        participacion_alumnos = preparar_participacion(
            participacion
        )

        trazabilidad_alumnos = preparar_trazabilidad(
            leer_trazabilidad(materia)
        )
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_participacion(
        participacion,
        participacion_alumnos,
        trazabilidad_alumnos,
    )

def pagina_trazabilidad():
    materia = st.session_state["materia_actual"]

    try:
        with st.spinner(
            "Leyendo y preparando trazabilidad..."
        ):
            trazabilidad = leer_trazabilidad(materia)

            trazabilidad_alumnos = preparar_trazabilidad(
                trazabilidad
            )
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_trazabilidad(
        trazabilidad,
        trazabilidad_alumnos,
    )

def pagina_rendimiento():
    materia = st.session_state["materia_actual"]

    try:
        calificaciones = preparar_calificaciones(leer_calificaciones(materia))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_rendimiento(calificaciones, materia)

def pagina_individual():
    materia = st.session_state["materia_actual"]

    try:
        matricula_actual = consolidar_matricula(
            leer_matriculados(materia)
        )
        participacion_alumnos = preparar_participacion(
            leer_participacion(materia)
        )
        base_alumnos = cruzar_matricula_participacion(
            matricula_actual,
            participacion_alumnos,
        )
        calificaciones = preparar_calificaciones(
            leer_calificaciones(materia)
        )
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    def cargar_historial(usuario):
        trazabilidad = leer_trazabilidad(materia)
        return preparar_trazabilidad(trazabilidad, usuario=usuario)

    mostrar_individual(
        base_alumnos,
        calificaciones,
        materia,
        cargar_historial,
    )

paginas = {
    "inicio": st.Page(
        pagina_inicio,
        title="Inicio",
        default=True,
    ),
    "matricula": st.Page(
        pagina_matricula,
        title="Matrícula y alertas",
        url_path="matricula",
    ),
    "participacion": st.Page(
        pagina_participacion,
        title="Participación",
        url_path="participacion",
    ),
    "trazabilidad": st.Page(
        pagina_trazabilidad,
        title="Trazabilidad",
        url_path="trazabilidad",
    ),
    "rendimiento": st.Page(
        pagina_rendimiento,
        title="Rendimiento académico",
        url_path="rendimiento",
    ),
    "individual": st.Page(
        pagina_individual,
        title="Individual",
        url_path="individual",
    ),
}


pagina_actual = st.navigation(
    list(paginas.values()),
    position="hidden",
)


if pagina_actual.url_path != paginas["inicio"].url_path:
    if st.button("Volver al inicio"):
        st.switch_page(paginas["inicio"])

    st.title(pagina_actual.title)

    try:
        materias = detectar_materias()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    if not materias:
        st.warning(
            "No se encontraron archivos de matrícula."
        )
        st.stop()

    materia_anterior = st.session_state.get(
        "materia_actual"
    )

    indice = (
        materias.index(materia_anterior)
        if materia_anterior in materias
        else 0
    )

    st.session_state["materia_actual"] = st.selectbox(
        "Seleccioná una materia",
        options=materias,
        index=indice,
        key="selector_materia",
    )


pagina_actual.run()