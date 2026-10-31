import streamlit as st

from datos import detectar_materias, leer_matriculados

from procesamiento import consolidar_matricula


st.set_page_config(
    page_title="Seguimiento académico",
    layout="wide",
)

st.title("Seguimiento académico")

st.write(
    "Análisis de participación, rendimiento y matrícula "
    "de estudiantes."
)

try:
    materias = detectar_materias()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

if not materias:
    st.warning("No se encontraron archivos de matrícula.")
    st.stop()

materia_seleccionada = st.selectbox(
    "Selecciona una materia",
    options = materias,
)

try:
    matriculados = leer_matriculados(materia_seleccionada)
    matricula_actual = consolidar_matricula(matriculados)
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

vigentes = (
    matricula_actual["Estado Insc."]
    .astype("string")
    .str.strip()
    .str.casefold()
    .eq("aceptada")
    .sum()
)

st.subheader("Situación actual de matrícula")

col1, col2, col3 = st.columns(3)

col1.metric("Registros del archivo", len(matriculados))
col2.metric("Estudiantes únicos", len(matricula_actual))
col3.metric("Matrículas vigentes", int(vigentes))

st.dataframe(
    matricula_actual,
    hide_index=True,
)

with st.expander("Ver historial completo"):
    st.dataframe(
        matriculados,
        hide_index=True,
    )