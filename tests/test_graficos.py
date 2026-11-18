import json
import unittest

import pandas as pd
from streamlit.dataframe_util import convert_arrow_bytes_to_pandas_df
from streamlit.testing.v1 import AppTest


class DatosDeGraficos(unittest.TestCase):
    def test_dataset_disponible_al_inicializar_sin_alterar_valores_ni_escalas(self):
        app = AppTest.from_string('''
import pandas as pd
from estilos import graficar
datos = pd.DataFrame({"Día": pd.to_datetime(["2025-08-05", "2025-08-06"]),
                      "Valor": pd.Series([0, 34 / 45 * 100], dtype="Float64")})
graficar(datos, {"mark": "line", "encoding": {
    "x": {"field": "Día", "type": "temporal", "scale": {"type": "utc"}},
    "y": {"field": "Valor", "type": "quantitative", "scale": {"domain": [0, 100]}}
}})
''').run()
        self.assertFalse(app.exception)
        proto = app.get("vega_lite_chart")[0].proto
        spec = json.loads(proto.spec)
        self.assertEqual(spec["data"], {"name": "datos_academicos"})
        self.assertFalse(proto.data.data, "La tabla no debe insertarse después del embed")
        self.assertEqual(len(proto.datasets), 1)
        self.assertEqual(proto.datasets[0].name, spec["data"]["name"])
        self.assertTrue(proto.datasets[0].has_name)
        recibido = convert_arrow_bytes_to_pandas_df(proto.datasets[0].data.data)
        esperado = pd.DataFrame({"Día": pd.to_datetime(["2025-08-05", "2025-08-06"]),
                                 "Valor": pd.Series([0, 34 / 45 * 100], dtype="Float64")})
        pd.testing.assert_frame_equal(recibido, esperado)
        self.assertEqual(spec["encoding"]["x"]["scale"], {"type": "utc"})
        self.assertEqual(spec["encoding"]["y"]["scale"], {"domain": [0, 100]})

    def test_cambio_de_datos_conserva_identidad_distinta_y_conteos_exactos(self):
        app = AppTest.from_string('''
import pandas as pd
import streamlit as st
from estilos import graficar
materia = st.selectbox("Materia", ["A", "B"])
graficar(pd.DataFrame({"Grupo": ["Activos", "Inactivos"],
                       "Estudiantes": [268, 51] if materia == "A" else [273, 46]}),
         {"mark": "bar", "encoding": {
             "x": {"field": "Estudiantes", "type": "quantitative"},
             "y": {"field": "Grupo", "type": "nominal"}}})
''').run()
        primero = app.get("vega_lite_chart")[0].proto
        nombre_anterior = json.loads(primero.spec)["name"]
        app.selectbox[0].select("B").run()
        self.assertFalse(app.exception)
        segundo = app.get("vega_lite_chart")[0].proto
        self.assertNotEqual(json.loads(segundo.spec)["name"], nombre_anterior)
        datos = convert_arrow_bytes_to_pandas_df(segundo.datasets[0].data.data)
        self.assertEqual(datos["Estudiantes"].tolist(), [273, 46])
        self.assertEqual(datos["Estudiantes"].sum(), 319)


if __name__ == "__main__":
    unittest.main()
