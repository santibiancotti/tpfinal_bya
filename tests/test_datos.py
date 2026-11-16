from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from datos import leer_excel, _leer_excel_cache


class CacheFuentes(unittest.TestCase):
    def test_distingue_rutas_y_actualiza_al_cambiar_archivo(self):
        _leer_excel_cache.clear()
        with TemporaryDirectory() as carpeta:
            primera, segunda = Path(carpeta) / "a", Path(carpeta) / "b"
            primera.write_text("a")
            segunda.write_text("b")
            with patch("datos.pd.read_excel", return_value=pd.DataFrame({"valor": [1]})) as leer:
                leer_excel(primera, header=5)
                copia = leer_excel(primera, header=5)
                self.assertEqual(leer.call_count, 1)
                copia.loc[0, "valor"] = 99
                self.assertEqual(leer_excel(primera, header=5).loc[0, "valor"], 1)
                leer_excel(segunda, header=5)
                self.assertEqual(leer.call_count, 2)
                primera.write_text("archivo modificado")
                leer_excel(primera, header=5)
                self.assertEqual(leer.call_count, 3)


if __name__ == "__main__":
    unittest.main()
