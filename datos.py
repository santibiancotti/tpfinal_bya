from pathlib import Path
import pandas as pd

CARPETA_PROYECTO = Path(__file__).resolve().parent

CARPETA_DATOS = (
    CARPETA_PROYECTO.parent / "Datos_LMS_Anonimizados"
)

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

    matriculados = pd.read_excel(
        archivo,
        header=1,
        dtype={"Identificación": "string"},
    )

    matriculados = matriculados.loc[
        matriculados["Identificación"].notna()
    ].copy()

    return matriculados
