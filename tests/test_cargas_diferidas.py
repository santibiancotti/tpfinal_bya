from pathlib import Path
import unittest
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

import datos
from test_resumen_trazabilidad import reporte


@unittest.skipUnless(datos.CARPETA_DATOS.is_dir(), "Requiere las fuentes pequeñas locales del TFI")
class CargasDiferidas(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        self.parche = patch("datos.leer_trazabilidad", side_effect=lambda materia: reporte())
        self.leer = self.parche.start()
        self.addCleanup(self.parche.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"),
                                    default_timeout=30).run()

    def comprobar(self):
        self.assertFalse(self.app.exception, [e.message for e in self.app.exception])
        self.assertFalse(self.app.error, [e.value for e in self.app.error])

    def abrir(self, vista):
        self.app.button(key=f"abrir_{vista}").click().run()
        self.comprobar()

    def cambiar_seccion(self, clave, valor):
        self.app.session_state[clave] = valor
        self.app.run()
        self.comprobar()

    def test_general_no_lee_trazas_hasta_abrir_y_refresca(self):
        self.abrir("general")
        self.assertEqual(self.leer.call_count, 0)
        materias = datos.detectar_materias()
        self.app.multiselect(key="general_materias").set_value(materias[:1]).run()
        self.app.multiselect(key="general_materias").set_value(materias).run()
        self.assertEqual(self.leer.call_count, 0)
        self.cambiar_seccion("general_tendencia", True)
        self.assertEqual(self.leer.call_count, len(materias))
        self.cambiar_seccion("general_tendencia", False)
        self.cambiar_seccion("general_tendencia", True)
        self.assertEqual(self.leer.call_count, len(materias))
        self.cambiar_seccion("general_tendencia", False)
        next(b for b in self.app.button if b.label == "Actualizar fuentes").click().run()
        self.comprobar()
        self.assertEqual(self.leer.call_count, len(materias))
        self.cambiar_seccion("general_tendencia", True)
        self.assertEqual(self.leer.call_count, 2 * len(materias))

    def test_participacion_carga_solo_la_evolucion_abierta(self):
        self.abrir("participacion")
        materia = self.app.selectbox(key="selector_materia").value
        self.assertEqual(self.leer.call_count, 0)
        self.cambiar_seccion(f"participacion_pestanas_{materia}", "Evolución de accesos")
        self.assertEqual(self.leer.call_count, 1)
        self.app.date_input[0].set_value(self.app.date_input[0].value).run()
        self.comprobar()
        self.assertEqual(self.leer.call_count, 1)

    def test_relacion_carga_trazabilidad_solo_al_solicitarla(self):
        self.abrir("relacion")
        materia = self.app.selectbox(key="selector_materia").value
        self.assertEqual(self.leer.call_count, 0)
        self.cambiar_seccion(f"relacion_trazabilidad_{materia}", True)
        self.assertEqual(self.leer.call_count, 1)
        self.app.selectbox(key=f"relacion_variable_{materia}").select("Registros de trazabilidad").run()
        self.comprobar()
        self.assertEqual(self.leer.call_count, 1)

    def test_trazabilidad_no_envia_detalle_ni_original_cerrados(self):
        self.abrir("trazabilidad")
        materia = self.app.selectbox(key="selector_materia").value
        self.assertEqual(self.leer.call_count, 1)
        self.assertEqual(len(self.app.dataframe), 0)
        self.cambiar_seccion(f"trazabilidad_pestanas_{materia}", "Detalle")
        self.assertEqual(self.leer.call_count, 2)
        self.assertEqual(len(self.app.dataframe), 1)
        self.app.run()
        self.comprobar()
        self.assertEqual(self.leer.call_count, 2)

    def test_individual_reutiliza_historial_y_no_lo_carga_en_notas(self):
        self.abrir("individual")
        materia = self.app.selectbox(key="selector_materia").value
        self.app.selectbox(key=f"individual_estudiante_{materia}").select_index(0).run()
        self.cambiar_seccion(f"individual_pestanas_{materia}", "Notas")
        self.assertEqual(self.leer.call_count, 0)
        self.cambiar_seccion(f"individual_pestanas_{materia}", "Historial de actividad")
        self.assertEqual(self.leer.call_count, 1)
        self.app.run()
        self.comprobar()
        self.assertEqual(self.leer.call_count, 1)

    def test_participacion_incorpora_cambios_de_fuente_y_actualizacion_manual(self):
        materia = datos.detectar_materias()[0]
        original = datos.leer_participacion(materia)
        actualizado = original.copy()
        alumnos = original["Perfil"].astype("string").str.strip().str.casefold().eq("alumnos")
        activos = alumnos & original["Interacciones"].gt(0)
        indice = original.index[activos][0]
        actualizado.loc[indice, "Interacciones"] = 0
        version = [1]
        contenido = [original]
        with patch("datos.firma_reporte", side_effect=lambda materia, tipo="trazabilidad": (materia, tipo, version[0])), \
                patch("datos.leer_participacion", side_effect=lambda materia: contenido[0]) as leer:
            self.abrir("participacion")
            buscar = lambda: int(next(m.value for m in self.app.metric if m.label == "Alumnos con actividad"))
            inicial = buscar()
            contenido[0] = actualizado
            version[0] = 2
            self.app.run()
            self.comprobar()
            self.assertEqual(buscar(), inicial - 1)
            self.assertEqual(leer.call_count, 2)
            contenido[0] = original
            next(b for b in self.app.button if b.label == "Actualizar fuentes").click().run()
            self.comprobar()
            self.assertEqual(buscar(), inicial)
            self.assertEqual(leer.call_count, 3)
if __name__ == "__main__":
    unittest.main()
