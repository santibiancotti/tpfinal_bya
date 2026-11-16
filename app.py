import streamlit as st

import pandas as pd

from datos import (detectar_materias, leer_matriculados, leer_participacion,
                   leer_trazabilidad, leer_calificaciones, leer_periodo_reporte,
                   leer_tendencia_diaria, leer_resumen_trazabilidad, leer_actividad_por_alumno,
                   leer_historial, leer_detalle_trazabilidad, firma_reporte,
                   firma_calificaciones, firma_matricula)


from procesamiento import (consolidar_matricula, preparar_participacion,
    cruzar_matricula_participacion, clasificar_alertas,
    preparar_calificaciones, resumir_resultados_alumnos, resumir_materia,
    cruzar_resultados_participacion)


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
def cargar_participacion(materia, firma):
    reporte = leer_participacion(materia)
    return reporte, preparar_participacion(reporte)


@st.cache_data(show_spinner=False, max_entries=6)
def cargar_rendimiento(materia, firmas):
    notas = preparar_calificaciones(leer_calificaciones(materia))
    return notas, resumir_resultados_alumnos(notas, materia)


@st.cache_data(show_spinner=False, max_entries=6)
def cargar_matricula(materia, firma_inscripciones, firma_participacion):
    matriculados = leer_matriculados(materia)
    actual = consolidar_matricula(matriculados)
    _, alumnos = cargar_participacion(materia, firma_participacion)
    base = clasificar_alertas(cruzar_matricula_participacion(actual, alumnos))
    return matriculados, actual, base


def cargar_base(materia):
    return cargar_matricula(materia, firma_matricula(materia), firma_reporte(materia, "participacion"))[2]


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
    resumenes, poblaciones, resultados = [], [], []
    try:
        with st.spinner("Consolidando las asignaturas seleccionadas..."):
            for materia in materias:
                reporte, alumnos = cargar_participacion(materia, firma_reporte(materia, "participacion"))
                _, notas = cargar_rendimiento(materia, firma_calificaciones(materia))
                periodo = leer_periodo_reporte(materia)
                resumenes.append(resumir_materia(materia, reporte, alumnos, notas, periodo))
                poblaciones.append(alumnos.assign(Materia=materia))
                resultados.append(notas.assign(Materia=materia))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return
    def cargar_tendencias():
        tendencias = []
        for indice, materia in enumerate(materias, start=1):
            with st.spinner(f"Cargando tendencia de {materia} ({indice}/{len(materias)})..."):
                tendencias.append(leer_tendencia_diaria(materia).assign(Materia=materia))
        return pd.concat(tendencias, ignore_index=True)

    mostrar_general(pd.DataFrame(resumenes), pd.concat(poblaciones),
                    pd.concat(resultados), cargar_tendencias)


def pagina_relacion():
    materia = st.session_state["materia_actual"]
    try:
        _, resultados = cargar_rendimiento(materia, firma_calificaciones(materia))
        periodo = leer_periodo_reporte(materia)
        datos = cruzar_resultados_participacion(cargar_base(materia), resultados, materia)
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return
    def cargar_indicadores():
        if periodo != leer_periodo_reporte(materia, "trazabilidad"):
            return None
        return leer_actividad_por_alumno(materia)

    mostrar_relacion(datos, materia, cargar_indicadores)


def pagina_matricula():
    materia = st.session_state["materia_actual"]

    try:
        matriculados, matricula_actual, base_alumnos = cargar_matricula(
            materia, firma_matricula(materia), firma_reporte(materia, "participacion")
        )
        
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
        participacion, participacion_alumnos = cargar_participacion(
            materia, firma_reporte(materia, "participacion")
        )
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_participacion(
        participacion,
        participacion_alumnos,
        lambda: leer_resumen_trazabilidad(materia),
    )

def pagina_trazabilidad():
    materia = st.session_state["materia_actual"]

    try:
        with st.spinner(
            "Leyendo y preparando trazabilidad..."
        ):
            resumen = leer_resumen_trazabilidad(materia)
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_trazabilidad(
        resumen,
        lambda desde, hasta, usuario: leer_detalle_trazabilidad(materia, desde, hasta, usuario),
        lambda: leer_trazabilidad(materia),
    )

def pagina_rendimiento():
    materia = st.session_state["materia_actual"]

    try:
        calificaciones, resultados = cargar_rendimiento(materia, firma_calificaciones(materia))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    mostrar_rendimiento(calificaciones, materia, resultados)

def pagina_individual():
    materia = st.session_state["materia_actual"]

    try:
        base_alumnos = cargar_base(materia)
        calificaciones, resultados = cargar_rendimiento(materia, firma_calificaciones(materia))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    def cargar_historial(usuario):
        return leer_historial(materia, usuario)

    mostrar_individual(
        base_alumnos,
        calificaciones,
        materia,
        cargar_historial,
        resultados,
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
