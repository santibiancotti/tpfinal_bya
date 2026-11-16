"""Contrasta los resúmenes optimizados con el procesamiento previo, sin editar fuentes."""
from pathlib import Path
import subprocess
import sys
import types

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
import datos
import procesamiento as actual


def main():
    anterior = types.ModuleType("procesamiento_anterior")
    fuente = subprocess.run(
        ["git", "show", "c025b17:procesamiento.py"], cwd=RAIZ,
        check=True, capture_output=True, encoding="utf-8",
    ).stdout
    exec(compile(fuente, "procesamiento_anterior.py", "exec"), anterior.__dict__)
    for materia in datos.detectar_materias():
        original = datos.leer_trazabilidad(materia)
        completos = anterior.preparar_trazabilidad(original)
        resumen = datos.leer_resumen_trazabilidad(materia)
        compactos = resumen["eventos"]
        assert resumen["total_reporte"] == len(original)
        assert compactos["Registros"].sum() == len(completos)
        pd.testing.assert_frame_equal(
            resumen["usuarios"], completos[["Usuario", "Apellido", "Nombre"]]
            .drop_duplicates("Usuario").sort_values("Usuario").reset_index(drop=True),
        )
        desde, hasta = datos.leer_periodo_reporte(materia, "trazabilidad")
        usuario = completos["Usuario"].iloc[0]
        casos = [(desde, hasta, None), (desde, hasta, usuario),
                 (completos["Fecha"].min().date(), completos["Fecha"].min().date(), None)]
        for inicio, fin, estudiante in casos:
            esperado = anterior.filtrar_trazabilidad(completos, inicio, fin, estudiante)
            agregado = actual.filtrar_trazabilidad(compactos, inicio, fin, estudiante)
            for campo in ["Día", "Semana", "Acción"]:
                pd.testing.assert_frame_equal(anterior.resumir_actividad(esperado, campo),
                                              actual.resumir_actividad(agregado, campo))
            pd.testing.assert_frame_equal(anterior.resumir_horarios(esperado),
                                          actual.resumir_horarios(agregado))
            pd.testing.assert_frame_equal(anterior.resumir_accesos_diarios(completos, inicio, fin, estudiante),
                                          actual.resumir_accesos_diarios(compactos, inicio, fin, estudiante))
        pd.testing.assert_frame_equal(
            datos.leer_tendencia_diaria(materia), anterior.resumir_accesos_diarios(completos, desde, hasta)
        )
        esperado = completos.groupby("Usuario", as_index=False).agg(
            **{"Registros de trazabilidad": ("Usuario", "size"), "Días con eventos": ("Día", "nunique")}
        )
        pd.testing.assert_frame_equal(datos.leer_actividad_por_alumno(materia), esperado)
        pd.testing.assert_frame_equal(datos.leer_historial(materia, usuario),
                                      anterior.preparar_trazabilidad(original, usuario))
        pd.testing.assert_frame_equal(
            datos.leer_detalle_trazabilidad(materia, desde, hasta, usuario).reset_index(drop=True),
            anterior.filtrar_trazabilidad(completos, desde, hasta, usuario).reset_index(drop=True),
        )
        calificaciones = datos.leer_calificaciones(materia)
        pd.testing.assert_frame_equal(actual.preparar_calificaciones(calificaciones),
                                      anterior.preparar_calificaciones(calificaciones))
        notas = actual.preparar_calificaciones(calificaciones)
        pd.testing.assert_frame_equal(actual.resumir_resultados_alumnos(notas, materia),
                                      anterior.resumir_resultados_alumnos(notas, materia))
        print(f"OK {materia}: {len(completos)} eventos, {len(compactos)} grupos; "
              "conteos, filtros, mapa, series, historial y calificaciones coinciden.", flush=True)


if __name__ == "__main__":
    main()
