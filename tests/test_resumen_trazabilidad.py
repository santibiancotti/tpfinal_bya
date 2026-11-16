from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st

import datos
import procesamiento as p


def reporte():
    filas = [
        ["2025-05-01 23:59:59", "1", " a ", "Apellido", "Nombre", "Aula", "Alumnos", "Sitios", "Acceder", "Uno"],
        ["2025-05-01 23:59:59", "1", " a ", "Apellido", "Nombre", "Aula", "Alumnos", "Sitios", "Acceder", "Uno"],
        ["2025-05-01 23:59:59", "1", " a ", "Apellido", "Nombre", "Aula", "Alumnos", "Sitios", "Acceder", "Otro"],
        ["2025-05-03 00:00:00", "2", "B", "Segundo", "Nombre", "Aula", "Alumnos", "Foros", " Leer ", "Texto"],
        ["2025-05-03 00:00:00", "2", "D", "Docente", "Nombre", "Aula", "Docentes", "Foros", "Leer", "Texto"],
    ]
    return pd.DataFrame(filas, columns=["Fecha", "IP Usuario", "Usuario", "Apellido", "Nombre", "Aula",
                                        "Perfil", "Sección", "Acción", "Descripción"])


class ResumenCompacto(unittest.TestCase):
    def test_conserva_filtros_conteos_repeticiones_y_series(self):
        original = reporte()
        completos = p.preparar_trazabilidad(original)
        resumen = p.resumir_trazabilidad(original)
        self.assertEqual(resumen["total_reporte"], 5)
        self.assertEqual(len(resumen["eventos"]), 2)
        self.assertEqual(resumen["eventos"]["Registros"].sum(), 4)
        self.assertEqual(resumen["eventos"]["Repetición exacta adicional"].sum(), 1)
        self.assertNotIn("Descripción", resumen["eventos"])
        for inicio, fin, usuario in [("2025-05-01", "2025-05-03", None),
                                     ("2025-05-01", "2025-05-01", "A"),
                                     ("2025-05-02", "2025-05-02", "A")]:
            esperados = p.filtrar_trazabilidad(completos, inicio, fin, usuario)
            agregados = p.filtrar_trazabilidad(resumen["eventos"], inicio, fin, usuario)
            for campo in ["Día", "Semana", "Acción"]:
                pd.testing.assert_frame_equal(p.resumir_actividad(esperados, campo),
                                              p.resumir_actividad(agregados, campo))
            pd.testing.assert_frame_equal(p.resumir_horarios(esperados), p.resumir_horarios(agregados))
            pd.testing.assert_frame_equal(p.resumir_accesos_diarios(completos, inicio, fin, usuario),
                                          p.resumir_accesos_diarios(resumen["eventos"], inicio, fin, usuario))
        pd.testing.assert_frame_equal(original, reporte())

    def test_vacio(self):
        resumen = p.resumir_trazabilidad(reporte().iloc[:0])
        self.assertTrue(resumen["eventos"].empty)
        self.assertTrue(resumen["usuarios"].empty)
        self.assertEqual(p.resumir_horarios(resumen["eventos"])["Registros"].sum(), 0)

    def test_cache_derivada_distingue_fuentes_y_refresca(self):
        st.cache_data.clear()
        with TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "fuente"
            archivo.write_text("inicial")
            with patch("datos.buscar_reporte", return_value=archivo), \
                    patch("datos.leer_trazabilidad", return_value=reporte()) as leer:
                datos.leer_resumen_trazabilidad("Materia A")
                datos.leer_resumen_trazabilidad("Materia A")
                self.assertEqual(leer.call_count, 1)
                datos.leer_resumen_trazabilidad("Materia B")
                self.assertEqual(leer.call_count, 2)
                archivo.write_text("fuente actualizada")
                datos.leer_resumen_trazabilidad("Materia A")
                self.assertEqual(leer.call_count, 3)
                st.cache_data.clear()
                datos.leer_resumen_trazabilidad("Materia A")
                self.assertEqual(leer.call_count, 4)


if __name__ == "__main__":
    unittest.main()
