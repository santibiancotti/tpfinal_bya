import unittest

import pandas as pd

from procesamiento import (
    preparar_calificaciones, resumir_resultados_alumnos, resumir_condiciones,
    calcular_correlacion, cruzar_resultados_participacion, preparar_trazabilidad,
    filtrar_trazabilidad, resumir_horarios, resumir_accesos_diarios,
)


def notas(valores):
    return preparar_calificaciones(pd.DataFrame([
        {"Usuario": usuario, "Instrumento": instrumento, "Nota": nota,
         "Apellido": "Apellido", "Nombre": "Nombre"}
        for usuario, instrumento, nota in valores
    ], columns=["Usuario", "Instrumento", "Nota", "Apellido", "Nombre"]))


class ReglasAcademicas(unittest.TestCase):
    def test_limites_promedios(self):
        for materia, promocion in [("Probabilidad y Estadística", 85),
                                   ("Algoritmos y Estructuras de Datos", 90)]:
            valores = [59.99, 60, promocion - .01, promocion, 100]
            datos = notas([(str(i), "Examen", f"{v}/100") for i, v in enumerate(valores)])
            resultado = resumir_resultados_alumnos(datos, materia)
            self.assertEqual(resultado["Condición académica"].tolist(),
                             ["Libre", "Regular", "Regular", "Promociona", "Promociona"])

    def test_algebra_parcial_conserva_proporciones(self):
        datos = notas([("A", "P1", "20/25"), ("A", "AE1", "7/10"),
                       ("A", "AE2", "7/10")])
        fila = resumir_resultados_alumnos(datos, "Álgebra").iloc[0]
        self.assertEqual(fila["Resultado observado"], 34)
        self.assertEqual(fila["Máximo de sus notas"], 45)
        self.assertAlmostEqual(fila["Resultado equivalente sobre 120"], 34 / 45 * 120)
        self.assertEqual(fila["Condición académica"], "Promociona")

    def test_algebra_limites_con_esquema_completo(self):
        for total, condicion in [(59.99, "Libre"), (60, "Regular"),
                                 (84.99, "Regular"), (85, "Promociona"), (120, "Promociona")]:
            maximos = [25, 25, 10, 10, 10, 10, 10, 20]
            datos = notas([("A", str(i), f"{total * maximo / 120}/{maximo}")
                           for i, maximo in enumerate(maximos)])
            self.assertEqual(resumir_resultados_alumnos(datos, "Álgebra").iloc[0]
                             ["Condición académica"], condicion)

    def test_no_imputa_ausencias_y_conserva_ceros(self):
        datos = notas([("A", "P1", "80/100"), ("A", "P2", None),
                       ("B", "P1", None), ("C", "P1", "0/100")])
        resultado = resumir_resultados_alumnos(datos, "Probabilidad y Estadística").set_index("Usuario")
        self.assertEqual(resultado.loc["A", "Resultado observado"], 80)
        self.assertTrue(pd.isna(resultado.loc["B", "Resultado observado"]))
        self.assertEqual(resultado.loc["B", "Condición académica"], "Sin notas informadas")
        self.assertEqual(resultado.loc["C", "Resultado observado"], 0)
        self.assertEqual(resumir_condiciones(resultado)["Alumnos"].sum(), 3)

    def test_rechaza_formatos_desconocidos_y_duplicados(self):
        with self.assertRaisesRegex(ValueError, "Formato"):
            notas([("A", "P1", "Ausente")])
        with self.assertRaisesRegex(ValueError, "más de una fila"):
            notas([("A", "P1", "80/100"), ("a ", "P1", "90/100")])
        with self.assertRaisesRegex(ValueError, "120 puntos"):
            resumir_resultados_alumnos(notas([("A", "P1", "80/100")]), "Álgebra")

    def test_vacio(self):
        resultado = resumir_resultados_alumnos(notas([]), "Álgebra")
        self.assertTrue(resultado.empty)
        self.assertTrue(resumir_condiciones(resultado)["Porcentaje (%)"].isna().all())


class CrucesYCorrelaciones(unittest.TestCase):
    def test_pares_insuficientes_constantes_y_validos(self):
        datos = pd.DataFrame({"x": [1, 2, None, 4], "Resultado observado": [2, 4, 8, 8]})
        pares, r, motivo = calcular_correlacion(datos, "x")
        self.assertEqual(len(pares), 3)
        self.assertAlmostEqual(r, 1)
        self.assertIsNone(motivo)
        self.assertIsNone(calcular_correlacion(datos.head(2), "x")[1])
        datos["x"] = 1
        self.assertIn("constante", calcular_correlacion(datos, "x")[2])

    def test_cruce_unico_preserva_sin_datos(self):
        base = pd.DataFrame({"Identificación": ["A", "B"],
                             "Situación de actividad": ["Con actividad registrada", "Sin actividad registrada"]})
        resultados = resumir_resultados_alumnos(notas([("A", "P1", "80/100"),
                                                      ("C", "P1", "90/100")]), "Probabilidad y Estadística")
        cruce = cruzar_resultados_participacion(base, resultados, "Probabilidad y Estadística")
        self.assertEqual(len(cruce), 3)
        self.assertTrue(cruce["Identificación"].is_unique)
        self.assertEqual(cruce.set_index("Identificación").loc["B", "Condición académica"], "Sin notas informadas")
        with self.assertRaises(pd.errors.MergeError):
            cruzar_resultados_participacion(pd.concat([base, base]), resultados, "Probabilidad y Estadística")


class FiltrosActividad(unittest.TestCase):
    def test_fechas_inclusivas_ceros_y_repeticiones(self):
        eventos = preparar_trazabilidad(pd.DataFrame({
            "Usuario": ["a", "a", "a"], "Perfil": ["Alumnos"] * 3,
            "Fecha": ["2025-05-01 23:59:59", "2025-05-01 23:59:59", "2025-05-03 00:00:00"],
            "Acción": ["Acceder"] * 3,
        }))
        seleccion = filtrar_trazabilidad(eventos, "2025-05-01", "2025-05-02", "A")
        self.assertEqual(len(seleccion), 2)
        self.assertEqual(seleccion["Repetición exacta adicional"].sum(), 1)
        self.assertEqual(len(resumir_horarios(seleccion)), 168)
        self.assertEqual(resumir_horarios(seleccion)["Registros"].sum(), 2)
        serie = resumir_accesos_diarios(eventos, "2025-05-01", "2025-05-03")
        self.assertEqual(serie["Accesos a secciones"].tolist(), [2, 0, 1])
        with self.assertRaises(ValueError):
            filtrar_trazabilidad(eventos, "2025-05-03", "2025-05-01")


if __name__ == "__main__":
    unittest.main()
