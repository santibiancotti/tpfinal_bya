from datetime import timedelta
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import datos
import procesamiento
from estilos import nombre_materia


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
        self.assertFalse(self.app.dataframe)
        for materia in self.materias:
            self.app.multiselect(key="general_materias").set_value([materia]).run()
            self.comprobar()
            self.assertEqual(self.app.metric[0].value, "1")
            tarjetas = [e.proto.body for e in self.app.get("html") if 'class="resultado-card"' in e.proto.body]
            self.assertEqual(len(tarjetas), 1)
            self.assertIn(nombre_materia(materia), tarjetas[0])
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

    def test_05_navegacion_compacta_y_regreso_a_inicio(self):
        for vista in ["general", "participacion", "trazabilidad", "rendimiento", "relacion", "individual", "matricula"]:
            self.abrir(vista)
            self.assertFalse(any(b.label == "Abrir vista" for b in self.app.button))
            self.app.button(key="abrir_general").click().run()
            self.comprobar()
            self.assertTrue(self.app.multiselect(key="general_materias"))
            self.assertEqual(self.app.button(key="abrir_general").proto.type, "primary")
            self.app.button(key="abrir_inicio").click().run()
            self.comprobar()
            self.assertEqual(self.app.button(key="abrir_general").label, "Abrir General")
            self.assertEqual(sum(b.label == "Abrir vista" for b in self.app.button), 6)

    def test_09_general_es_la_entrada_de_la_aplicacion(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.multiselect(key="general_materias"))
        self.assertEqual(app.button(key="abrir_general").proto.type, "primary")
        self.assertFalse(any(b.label == "Abrir vista" for b in app.button))
        self.assertFalse(app.dataframe)

    def test_06_general_detalles_y_proyeccion(self):
        self.abrir("general")
        self.assertEqual(len(self.app.dataframe), 0)
        self.app.session_state["general_distribucion"] = True
        self.app.run()
        self.assertFalse(self.app.dataframe)
        self.app.session_state["general_distribucion_valores"] = True
        for materia in self.materias:
            self.app.selectbox(key="general_distribucion_materia").select(materia).run()
            self.comprobar()
            etiqueta = "Condición proyectada según notas informadas" if materia == "Álgebra" else "Condición según notas informadas"
            self.assertTrue(any(etiqueta in m.value for m in self.app.markdown))
            detalle = self.app.dataframe[0].value
            esperados = datos.leer_calificaciones(materia)["Usuario"].astype("string").str.strip().str.upper().nunique()
            self.assertEqual(detalle["Alumnos"].sum(), esperados)
        self.app.session_state["general_criterios"] = True
        self.app.run()
        self.comprobar()
        self.assertEqual(sum("En Álgebra, la condición se proyecta" in c.value for c in self.app.caption), 1)

    def test_07_graficos_primero_y_tablas_solo_al_solicitarlas(self):
        self.abrir("participacion")
        materia = self.app.selectbox(key="selector_materia").value
        self.app.session_state[f"participacion_pestanas_{materia}"] = "Resumen del reporte completo"
        self.app.run()
        self.comprobar()
        self.assertFalse(self.app.dataframe)
        self.assertTrue(self.app.get("vega_lite_chart"))
        self.app.session_state["participacion_alumnos"] = True
        self.app.run()
        self.comprobar()
        esperados = procesamiento.preparar_participacion(datos.leer_participacion(materia))
        self.assertEqual(len(self.app.dataframe[0].value), len(esperados))

        self.abrir("rendimiento")
        self.assertFalse(self.app.dataframe)
        self.assertTrue(self.app.get("vega_lite_chart"))
        self.app.session_state["rendimiento_instrumentos_valores"] = True
        self.app.run()
        self.comprobar()
        notas = procesamiento.preparar_calificaciones(datos.leer_calificaciones(materia))
        self.assertEqual(self.app.dataframe[0].value["Notas informadas"].sum(), notas["Puntos obtenidos"].count())

        self.abrir("relacion")
        self.app.radio(key=f"relacion_poblacion_{materia}").set_value("Alumnos del aula").run()
        self.assertFalse(self.app.dataframe)
        self.assertEqual(len(self.app.get("vega_lite_chart")), 2)
        self.app.session_state["relacion_grupos_valores"] = True
        self.app.run()
        self.comprobar()
        self.assertEqual(self.app.dataframe[0].value["Estudiantes"].sum(), len(esperados))
        self.assertAlmostEqual(self.app.dataframe[0].value["Porcentaje de la población (%)"].sum(), 100, places=1)

    def test_08_individual_y_matricula_detalle_opcional(self):
        self.abrir("individual")
        materia = self.app.selectbox(key="selector_materia").value
        self.app.selectbox(key=f"individual_estudiante_{materia}").select_index(0).run()
        self.comprobar()
        self.assertFalse(self.app.dataframe)
        self.assertTrue(any("border-radius: 50%" in h.proto.body for h in self.app.get("html")))
        self.app.session_state[f"individual_pestanas_{materia}"] = "Notas"
        self.app.run()
        self.comprobar()
        self.assertFalse(self.app.dataframe)
        self.app.session_state["individual_notas_detalle"] = True
        self.app.run()
        self.comprobar()
        self.assertEqual(len(self.app.dataframe), 1)

        self.abrir("matricula")
        self.assertEqual(len(self.app.dataframe), 1)
        self.assertEqual(self.app.dataframe[0].value.columns.tolist(), ["Estudiante", "Identificación", "Alerta"])
        self.app.session_state["matricula_historial"] = True
        self.app.run()
        self.comprobar()
        self.assertEqual(len(self.app.dataframe), 2)
        self.assertEqual(len(self.app.dataframe[1].value), len(datos.leer_matriculados(materia)))


if __name__ == "__main__":
    unittest.main()
