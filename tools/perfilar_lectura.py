"""Compara lectores sin usar caché de Streamlit y comprueba los datos completos."""
import argparse
import cProfile
import hashlib
from importlib.metadata import version
from io import StringIO
import json
from pathlib import Path
import pstats
import sys
from time import perf_counter

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from openpyxl import load_workbook
import pandas as pd

from datos import buscar_reporte, detectar_materias
from procesamiento import resumir_trazabilidad

COLUMNAS = ["Fecha", "IP Usuario", "Usuario", "Apellido", "Nombre", "Aula",
            "Perfil", "Sección", "Acción", "Descripción"]


def leer(archivo, motor):
    if motor != "openpyxl_values":
        return pd.read_excel(archivo, header=5, usecols=COLUMNAS,
                             dtype={"Usuario": "string"}, engine=motor)
    libro = load_workbook(archivo, read_only=True, data_only=True)
    try:
        filas = libro.worksheets[0].iter_rows(min_row=6, values_only=True)
        encabezado = next(filas)
        tabla = pd.DataFrame.from_records(filas, columns=encabezado)[COLUMNAS]
        return tabla.astype({"Usuario": "string"})
    finally:
        libro.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, default=RAIZ / "mediciones/lectores.json")
    parser.add_argument("--rondas", type=int, default=2)
    opciones = parser.parse_args()
    archivos = {m: buscar_reporte(m, "trazabilidad") for m in detectar_materias()}
    hashes = {m: hashlib.sha256(p.read_bytes()).hexdigest() for m, p in archivos.items()}
    registros = []
    motores = ["openpyxl", "calamine", "openpyxl_values"]
    for materia, archivo in archivos.items():
        referencia = None
        for ronda in range(opciones.rondas):
            orden = motores if ronda % 2 == 0 else list(reversed(motores))
            for motor in orden:
                inicio = perf_counter()
                tabla = leer(archivo, motor)
                lectura = perf_counter() - inicio
                if referencia is None:
                    referencia = tabla
                equivalente, diferencia = True, None
                try:
                    pd.testing.assert_frame_equal(tabla, referencia)
                except AssertionError as error:
                    equivalente, diferencia = False, str(error)[:800]
                inicio = perf_counter()
                resumen = resumir_trazabilidad(tabla)
                agregacion = perf_counter() - inicio
                registro = {"materia": materia, "ronda": ronda + 1, "motor": motor,
                            "lectura_s": lectura, "resumen_s": agregacion,
                            "filas": len(tabla), "grupos": len(resumen["eventos"]),
                            "equivalente": equivalente, "diferencia": diferencia}
                registros.append(registro)
                print(json.dumps(registro, ensure_ascii=False), flush=True)
    materia_perfil = max(archivos, key=lambda m: archivos[m].stat().st_size)
    informes = []
    for motor in ["openpyxl", "calamine"]:
        perfil = cProfile.Profile()
        tabla = perfil.runcall(leer, archivos[materia_perfil], motor)
        salida = StringIO()
        pstats.Stats(perfil, stream=salida).strip_dirs().sort_stats("cumulative").print_stats(25)
        informes.append(f"LECTURA {motor}: {materia_perfil}\n{salida.getvalue()}")
        if motor == "calamine":
            perfil_resumen = cProfile.Profile()
            perfil_resumen.runcall(resumir_trazabilidad, tabla)
            salida = StringIO()
            pstats.Stats(perfil_resumen, stream=salida).strip_dirs().sort_stats("cumulative").print_stats(20)
            informes.append(f"CONSTRUCCIÓN DEL RESUMEN\n{salida.getvalue()}")
    assert hashes == {m: hashlib.sha256(p.read_bytes()).hexdigest() for m, p in archivos.items()}
    opciones.salida.parent.mkdir(parents=True, exist_ok=True)
    opciones.salida.write_text(json.dumps({
        "python": sys.version, "pandas": pd.__version__, "openpyxl": version("openpyxl"),
        "python_calamine": version("python-calamine"), "fuentes_sha256": hashes,
        "metodo": "Lecturas completas sin cache de aplicacion; orden invertido en la segunda ronda; cache del SO sin vaciar. El perfil no participa en los tiempos comparados.",
        "mediciones": registros,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    opciones.salida.with_suffix(".perfil.txt").write_text("\n\n".join(informes), encoding="utf-8")


if __name__ == "__main__":
    main()
