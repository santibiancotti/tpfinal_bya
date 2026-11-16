from pathlib import Path
import pandas as pd
import streamlit as st
from html import unescape

from procesamiento import (resumir_trazabilidad, resumir_accesos_diarios,
                          preparar_trazabilidad, filtrar_trazabilidad)

CARPETA_PROYECTO = Path(__file__).resolve().parent

CARPETA_DATOS = (
    CARPETA_PROYECTO.parent / "Datos_LMS_Anonimizados"
)

@st.cache_data(show_spinner=False, max_entries=48)
def _leer_excel_cache(ruta, modificacion_ns, tamano, opciones):
    return pd.read_excel(ruta, **opciones)


def leer_excel(archivo, **opciones):
    estado = archivo.stat()
    return _leer_excel_cache(
        str(archivo), estado.st_mtime_ns, estado.st_size, opciones
    )


def leer_periodo_reporte(materia, tipo="participacion"):
    archivo = buscar_reporte(materia, tipo)
    cabecera = leer_excel(archivo, header=None, nrows=4)
    fechas = []
    for etiqueta in ("Fecha desde", "Fecha Hasta"):
        valores = [
            str(valor).partition(":")[2].strip()
            for valor in cabecera.iloc[3].dropna()
            if str(valor).casefold().startswith(etiqueta.casefold() + ":")
        ]
        if len(valores) != 1:
            raise ValueError(f"No se pudo identificar {etiqueta} en {archivo.name}.")
        fechas.append(pd.to_datetime(valores[0], dayfirst=True, errors="raise").date())
    if fechas[0] > fechas[1]:
        raise ValueError(f"Período inválido en {archivo.name}.")
    return tuple(fechas)

def detectar_materias():
    carpeta_matriculados = CARPETA_DATOS / "Matriculados"

    if not carpeta_matriculados.is_dir():
        raise FileNotFoundError(
            f"No se encuentra la carpeta: {carpeta_matriculados}"
        )

    archivos = [
        archivo
        for archivo in carpeta_matriculados.iterdir()
        if archivo.is_file()
        and archivo.suffix.lower() == ".xlsx"
        and not archivo.name.startswith("~$")
    ]

    return sorted(
        [archivo.stem for archivo in archivos],
        key=str.casefold,
    )

def leer_matriculados(materia):
    archivo = (
        CARPETA_DATOS
        / "Matriculados"
        / f"{materia}.xlsx"
    )

    if not archivo.is_file():
        raise FileNotFoundError(
            f"No se encuentra el archivo: {archivo}"
        )

    matriculados = leer_excel(
        archivo,
        header=1,
        dtype={"Identificación": "string"},
    )

    matriculados = matriculados.loc[
        matriculados["Identificación"].notna()
    ].copy()

    return matriculados

def buscar_reporte(materia, tipo):
    carpeta_materia = CARPETA_DATOS / materia

    if not carpeta_materia.is_dir():
        raise FileNotFoundError(
            f"No se encuentra la carpeta: {carpeta_materia}"
        )

    archivos = sorted(
        archivo
        for archivo in carpeta_materia.glob(
            f"reporte_{tipo}_*.xlsx"
        )
        if archivo.is_file()
    )

    if not archivos:
        raise FileNotFoundError(
            f"No se encontró un reporte de {tipo} "
            f"para {materia}."
        )

    if len(archivos) > 1:
        raise ValueError(
            f"Se encontró más de un reporte de {tipo} "
            f"para {materia}. Debemos definir cuál utilizar."
        )

    return archivos[0]

def leer_participacion(materia):

    archivo = buscar_reporte(materia, "participacion")

    columnas = [
        "Usuario",
        "Apellido",
        "Nombre",
        "Perfil",
        "Fecha alta",
        "Avance",
        "Interacciones",
        "Primera interacción",
        "Última interacción",
        "Tiempo estimado de uso",
    ]

    participacion = leer_excel(
        archivo,
        header=5,
        usecols=columnas,
        dtype={"Usuario": "string"},
    )

    participacion = participacion.loc[
        participacion["Usuario"].notna()
    ].copy()

    return participacion

@st.cache_data(
    show_spinner=False,
    max_entries=6,
)
def _leer_trazabilidad_cache(
    ruta,
    modificacion_ns,
    tamano,
):
    columnas = [
        "Fecha",
        "IP Usuario",
        "Usuario",
        "Apellido",
        "Nombre",
        "Aula",
        "Perfil",
        "Sección",
        "Acción",
        "Descripción",
    ]

    return pd.read_excel(
        ruta,
        header=5,
        usecols=columnas,
        dtype={"Usuario": "string"},
    )


def leer_trazabilidad(materia):
    archivo = buscar_reporte(
        materia,
        "trazabilidad",
    )

    estado = archivo.stat()

    return _leer_trazabilidad_cache(
        str(archivo),
        estado.st_mtime_ns,
        estado.st_size,
    )

def leer_calificaciones(materia):
    carpeta = CARPETA_DATOS / materia

    archivos = sorted(
        archivo
        for archivo in carpeta.glob("calificaciones_alumnos_*.xlsx")
        if archivo.is_file()
    )

    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos de calificaciones para {materia}."
        )

    columnas = [
        "Usuario",
        "Apellido",
        "Nombre",
        "Nota",
        "Observaciones",
        "Detalle",
    ]

    tablas = []
    instrumentos = set()

    for archivo in archivos:
        contenido = leer_excel(
            archivo,
            header=None,
            dtype="string",
        )

        if (
            len(contenido) < 7
            or contenido.iloc[6].fillna("").tolist() != columnas
        ):
            raise ValueError(
                f"Encabezado de calificaciones inesperado en {archivo.name}."
            )

        etiqueta, _, nombre = str(contenido.iat[2, 0]).partition(":")
        instrumento = unescape(nombre).strip()

        if etiqueta.strip() != "Calificación" or not instrumento:
            raise ValueError(
                f"No se pudo identificar el instrumento en {archivo.name}."
            )

        clave_instrumento = instrumento.casefold()

        if clave_instrumento in instrumentos:
            raise ValueError(
                f"Hay más de un archivo para {instrumento} en {materia}."
            )

        instrumentos.add(clave_instrumento)

        tabla = contenido.iloc[7:].copy()
        tabla.columns = columnas
        tabla = tabla.loc[tabla["Usuario"].notna()].copy()
        tabla.insert(0, "Instrumento", instrumento)
        tabla["Archivo de origen"] = archivo.name

        tablas.append(tabla)

    return pd.concat(tablas, ignore_index=True)


def firma_reporte(materia, tipo="trazabilidad"):
    archivo = buscar_reporte(materia, tipo)
    estado = archivo.stat()
    return str(archivo.resolve()), estado.st_mtime_ns, estado.st_size


@st.cache_data(show_spinner=False, max_entries=6)
def _resumen_trazabilidad_cache(materia, firma):
    return resumir_trazabilidad(leer_trazabilidad(materia))


def leer_resumen_trazabilidad(materia):
    return _resumen_trazabilidad_cache(materia, firma_reporte(materia))


@st.cache_data(show_spinner=False, max_entries=6)
def _tendencia_diaria_cache(materia, firma):
    periodo = leer_periodo_reporte(materia, "trazabilidad")
    resumen = _resumen_trazabilidad_cache(materia, firma)
    return resumir_accesos_diarios(resumen["eventos"], *periodo)


def leer_tendencia_diaria(materia):
    return _tendencia_diaria_cache(materia, firma_reporte(materia))
