from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from openpyxl import Workbook
import pandas as pd

import datos


COLUMNAS = ["Fecha", "IP Usuario", "Usuario", "Apellido", "Nombre", "Aula",
            "Perfil", "Sección", "Acción", "Descripción"]


class LectorTrazabilidad(unittest.TestCase):
    def test_conserva_fechas_identificadores_vacios_y_textos(self):
        # Libro sintético de prueba; nunca se escribe sobre una fuente original.
        with TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "reporte.xlsx"
            libro = Workbook()
            hoja = libro.active
            for columna, nombre in enumerate(COLUMNAS, 1):
                hoja.cell(row=6, column=columna, value=nombre)
            hoja.append([datetime(2025, 5, 1, 23, 59, 59), "001.2", "0001", "Álvarez", "Ñandú",
                          "Aula", "Alumnos", "Sitios", " Acceder ", "NA"])
            hoja.append(["2025-05-02 10:00:00", None, 123, None, "Otro", "Aula", "Alumnos",
                          "Foros", "Leer", "#N/A"])
            hoja.append(["2025-05-03 10:00:00", "1.2", "ALU_1", "Apellido", "Nombre", "Aula",
                          "Alumnos", None, None, "Texto con á, ñ y saltos\nde línea"])
            libro.save(archivo)
            libro.close()
            esperado = pd.read_excel(archivo, header=5, usecols=COLUMNAS,
                                     dtype={"Usuario": "string"}, engine="openpyxl")
            estado = archivo.stat()
            actual = datos._leer_trazabilidad_cache(str(archivo), estado.st_mtime_ns, estado.st_size)
            pd.testing.assert_frame_equal(actual, esperado)
            self.assertEqual(actual.loc[0, "Usuario"], "0001")
            self.assertTrue(pd.isna(actual.loc[0, "Descripción"]))

    def test_usa_motor_elegido_y_preserva_cache_por_fuente(self):
        datos._leer_trazabilidad_cache.clear()
        with patch("datos.pd.read_excel", return_value=pd.DataFrame({"Usuario": ["A"]})) as leer:
            datos._leer_trazabilidad_cache("a.xlsx", 1, 10)
            datos._leer_trazabilidad_cache("a.xlsx", 1, 10)
            self.assertEqual(leer.call_count, 1)
            self.assertEqual(leer.call_args.kwargs["engine"], "calamine")
            self.assertEqual(leer.call_args.kwargs["dtype"], {"Usuario": "string"})
            datos._leer_trazabilidad_cache("a.xlsx", 2, 11)
            datos._leer_trazabilidad_cache("b.xlsx", 2, 11)
            self.assertEqual(leer.call_count, 3)


if __name__ == "__main__":
    unittest.main()
