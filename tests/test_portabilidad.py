from hashlib import file_digest
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import datos


RAIZ = Path(__file__).resolve().parents[1]


class FuentesPortables(unittest.TestCase):
    def test_fuentes_versionadas_coinciden_con_manifiesto(self):
        carpeta = RAIZ / "data"
        esperados = dict(linea.split("  ", 1)[::-1]
                         for linea in (carpeta / "SHA256SUMS").read_text(encoding="utf-8").splitlines())
        actuales = {}
        for archivo in carpeta.rglob("*.xlsx"):
            if not archivo.name.startswith("~$"):
                with archivo.open("rb") as contenido:
                    actuales[archivo.relative_to(carpeta).as_posix()] = file_digest(contenido, "sha256").hexdigest()
        self.assertTrue(esperados)
        self.assertEqual(actuales, esperados)

    def test_detecta_materias_y_fuentes_desde_otro_directorio(self):
        self.assertEqual(datos.CARPETA_DATOS, RAIZ / "data")
        anterior = Path.cwd()
        with TemporaryDirectory() as temporal:
            try:
                os.chdir(temporal)
                materias = datos.detectar_materias()
                self.assertEqual(set(materias), {"Álgebra", "Probabilidad y Estadística",
                                                "Algoritmos y Estructuras de Datos"})
                for materia in materias:
                    fuentes = [datos.CARPETA_DATOS / "Matriculados" / f"{materia}.xlsx",
                               datos.buscar_reporte(materia, "participacion"),
                               datos.buscar_reporte(materia, "trazabilidad"),
                               *datos.buscar_calificaciones(materia)]
                    for fuente in fuentes:
                        self.assertTrue(fuente.is_file(), fuente)
                        self.assertTrue(fuente.is_relative_to(RAIZ / "data"), fuente)
            finally:
                os.chdir(anterior)


if __name__ == "__main__":
    unittest.main()
