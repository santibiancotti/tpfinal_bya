from datetime import timedelta
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import datos


@unittest.skipUnless(datos.CARPETA_DATOS.is_dir(), "Requiere las fuentes locales del TFI")
class VistasConFuentesReales(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.materias = datos.detectar_materias()
        cls.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"),
                                   default_timeout=90).run()

    def comprobar(self):
        self.assertFalse(self.app.exception, [e.message for e in self.app.exception])
        self.assertFalse(self.app.error, [e.value for e in self.app.error])

    def abrir(self, vista):
        self.app.button(key=f"abrir_{vista}").click().run()
        self.comprobar()

    def test_01_siete_vistas_tres_materias(self):
        for vista in ["participacion", "trazabilidad", "rendimiento", "relacion", "matricula", "individual"]:
            self.abrir(vista)
            firmas = []
            for materia in self.materias:
                with self.subTest(vista=vista, materia=materia):
                    self.app.selectbox(key="selector_materia").select(materia).run()
                    self.comprobar()
                    if vista == "relacion":
                        self.app.session_state[f"relacion_trazabilidad_{materia}"] = True
                        self.app.run()
                        self.comprobar()
                        for variable in ["Interacciones", "Tiempo de uso (minutos)",
                                         "Registros de trazabilidad", "Días con eventos"]:
                            self.app.selectbox(key=f"relacion_variable_{materia}").select(variable).run()
                            self.comprobar()
                    if vista == "trazabilidad":
                        graficos = self.app.get("vega_lite_chart")
                        self.assertTrue(graficos)
                        self.assertIn("mapa_horario_", graficos[0].proto.spec)
                        firmas.append(graficos[0].proto.spec)
            if vista == "trazabilidad":
                self.assertEqual(len(set(firmas)), len(self.materias))
        self.abrir("general")
        self.assertEqual(self.app.metric[0].value, str(len(self.materias)))
        self.assertEqual(len(self.app.dataframe[0].value), len(self.materias))
        for materia in self.materias:
            self.app.multiselect(key="general_materias").set_value([materia]).run()
            self.comprobar()
            self.assertEqual(self.app.dataframe[0].value["Materia"].tolist(), [materia])
        self.app.multiselect(key="general_materias").set_value([]).run()
        self.comprobar()
        self.assertTrue(self.app.info)

    def test_02_filtros_periodo_estudiante_y_cambio_materia(self):
        for vista in ["participacion", "trazabilidad"]:
            self.abrir(vista)
            for materia in self.materias:
                self.app.selectbox(key="selector_materia").select(materia).run()
                if vista == "participacion":
                    self.app.session_state[f"participacion_pestanas_{materia}"] = "Evolución de accesos"
                    self.app.run()
                    self.comprobar()
                fecha = self.app.date_input[0].value[0]
                self.app.date_input[0].set_value((fecha, fecha + timedelta(days=1))).run()
                self.comprobar()
                self.app.selectbox(key=f"{vista}_{materia}_estudiante").select_index(1).run()
                self.comprobar()
            self.app.date_input[0].set_value((fecha,)).run()
            self.comprobar()
            self.assertTrue(any("fecha de inicio" in i.value for i in self.app.info))

    def test_03_individual_historial_diferido_y_notas(self):
        with patch("datos.leer_trazabilidad", wraps=datos.leer_trazabilidad) as leer:
            self.abrir("individual")
            for materia in self.materias:
                self.app.selectbox(key="selector_materia").select(materia).run()
                clave = f"individual_pestanas_{materia}"
                self.app.session_state[clave] = "Matrícula y participación"
                antes = leer.call_count
                self.app.selectbox(key=f"individual_estudiante_{materia}").select_index(0).run()
                self.comprobar()
                self.assertEqual(leer.call_count, antes)
                self.app.session_state[clave] = "Notas"
                self.app.run()
                self.comprobar()
                self.assertEqual(leer.call_count, antes)
                self.app.session_state[clave] = "Historial de actividad"
                self.app.run()
                self.comprobar()
                self.assertGreater(leer.call_count, antes)
                self.app.selectbox(key=f"individual_estudiante_{materia}").select_index(1).run()
                self.comprobar()

    def test_04_matricula_poblaciones_y_grupos(self):
        self.abrir("matricula")
        for materia in self.materias:
            self.app.selectbox(key="selector_materia").select(materia).run()
            for poblacion in ["Matrícula vigente", "Alumnos del aula", "Base completa"]:
                self.app.radio(key="matricula_poblacion").set_value(poblacion).run()
                self.comprobar()
            for situacion in self.app.selectbox(key="matricula_filtro_Situación de matrícula").options:
                self.app.selectbox(key="matricula_filtro_Situación de matrícula").select(situacion).run()
                self.comprobar()
            self.app.selectbox(key="matricula_filtro_Situación de matrícula").select("Todas").run()


if __name__ == "__main__":
    unittest.main()
