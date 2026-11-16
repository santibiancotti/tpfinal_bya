import streamlit as st

import pandas as pd

from datos import (detectar_materias, leer_matriculados, leer_participacion,
                   leer_trazabilidad, leer_calificaciones, leer_periodo_reporte, buscar_reporte)


from procesamiento import (consolidar_matricula, preparar_participacion,
    cruzar_matricula_participacion, clasificar_alertas, preparar_trazabilidad,
    preparar_calificaciones, resumir_resultados_alumnos, resumir_materia,
    resumir_accesos_diarios, cruzar_resultados_participacion)


from vistas import (mostrar_inicio, mostrar_matricula, mostrar_participacion,
    mostrar_trazabilidad, mostrar_rendimiento, mostrar_individual,
    mostrar_general, mostrar_relacion)


st.set_page_config(
    page_title="Seguimiento académico",
    layout="wide",
)


def pagina_inicio():
    st.info("Abrí una de las siete vistas para comenzar.")


@st.cache_data(show_spinner=False, max_entries=6)
def cargar_trazabilidad_preparada(materia, modificacion_ns, tamano):
    return preparar_trazabilidad(leer_trazabilidad(materia))


def obtener_trazabilidad_preparada(materia):
    estado = buscar_reporte(materia, "trazabilidad").stat()
    return cargar_trazabilidad_preparada(materia, estado.st_mtime_ns, estado.st_size)


def cargar_base(materia):
    return clasificar_alertas(cruzar_matricula_participacion(
        consolidar_matricula(leer_matriculados(materia)),
        preparar_participacion(leer_participacion(materia)),
    ))


def pagina_general():
    try:
        disponibles = detectar_materias()
    except FileNotFoundError as error:
        st.error(str(error))
        return
    materias = st.multiselect(
        "Asignaturas a consolidar", disponibles, default=disponibles,
        key="general_materias",
    )
    if not materias:
        st.info("Seleccioná al menos una asignatura.")
        return
    resumenes, poblaciones, resultados, tendencias = [], [], [], []
    try:
        with st.spinner("Consolidando las asignaturas seleccionadas..."):
            for materia in materias:
                reporte = leer_participacion(materia)
                alumnos = preparar_participacion(reporte)
                notas = resumir_resultados_alumnos(
                    preparar_calificaciones(leer_calificaciones(materia)), materia
                )
                periodo = leer_periodo_reporte(materia)
                resumenes.append(resumir_materia(materia, reporte, alumnos, notas, periodo))
                poblaciones.append(alumnos.assign(Materia=materia))
                resultados.append(notas.assign(Materia=materia))
                periodo_eventos = leer_periodo_reporte(materia, "trazabilidad")
                resumenes[-1]["Trazabilidad desde"] = periodo_eventos[0]
                resumenes[-1]["Trazabilidad hasta"] = periodo_eventos[1]
                tendencias.append(resumir_accesos_diarios(
                    obtener_trazabilidad_preparada(materia), *periodo_eventos
                ).assign(Materia=materia))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return
    mostrar_general(pd.DataFrame(resumenes), pd.concat(poblaciones),
                    pd.concat(resultados), pd.concat(tendencias))


def pagina_relacion():
    materia = st.session_state["materia_actual"]
    try:
        resultados = resumir_resultados_alumnos(
            preparar_calificaciones(leer_calificaciones(materia)), materia
        )
        periodo = leer_periodo_reporte(materia)
        periodo_eventos = leer_periodo_reporte(materia, "trazabilidad")
        eventos = obtener_trazabilidad_preparada(materia) if periodo == periodo_eventos else None
        if eventos is None:
            st.warning("Los períodos de participación y trazabilidad difieren. No se cruzan sus recuentos.")
        datos = cruzar_resultados_participacion(cargar_base(materia), resultados, materia, eventos)
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return
    mostrar_relacion(datos, materia)


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

        trazabilidad_alumnos = obtener_trazabilidad_preparada(materia)
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

            trazabilidad_alumnos = obtener_trazabilidad_preparada(materia)
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
        base_alumnos = cargar_base(materia)
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
    "general": st.Page(pagina_general, title="General", url_path="general"),
    "relacion": st.Page(pagina_relacion, title="Notas y participación", url_path="relacion"),
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

mostrar_inicio(paginas)
if st.button("Actualizar fuentes", help="Vacía la caché y vuelve a leer los archivos originales."):
    st.cache_data.clear()
    st.rerun()
st.divider()

if pagina_actual.url_path != paginas["inicio"].url_path:
    st.title(pagina_actual.title)

if pagina_actual.url_path not in (paginas["inicio"].url_path, paginas["general"].url_path):

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
    try:
        desde, hasta = leer_periodo_reporte(st.session_state["materia_actual"])
        st.caption(f"Participación del reporte: {desde:%d/%m/%Y} al {hasta:%d/%m/%Y}. "
                   "Matrícula: último estado disponible en su archivo.")
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()


pagina_actual.run()
