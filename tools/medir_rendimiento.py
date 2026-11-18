"""Medición del servidor con AppTest; no incluye el pintado del navegador.

Ejemplo: .venv/Scripts/python tools/medir_rendimiento.py --salida mediciones/antes.json
La caché de Streamlit se vacía por escenario frío; no se vacía la del sistema operativo.
"""
import argparse
from collections import defaultdict
from contextlib import ExitStack
from functools import wraps
import hashlib
import inspect
import json
from pathlib import Path
import sys
import threading
from time import perf_counter
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.testing.v1 import AppTest
import datos
import procesamiento
import vistas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--motor-trazabilidad", choices=["openpyxl", "calamine"],
                        help="Fuerza solo la lectura completa de trazabilidad para comparar lectores.")
    opciones = parser.parse_args()
    tiempos, llamadas = defaultdict(float), defaultdict(int)
    pila = threading.local()
    inicio, primera_metrica = 0, None

    def instrumentar(funcion, categoria):
        @wraps(funcion)
        def medir(*args, **kwargs):
            if not hasattr(pila, "marcos"):
                pila.marcos = []
            marco = [perf_counter(), 0]
            pila.marcos.append(marco)
            try:
                return funcion(*args, **kwargs)
            finally:
                duracion = perf_counter() - marco[0]
                pila.marcos.pop()
                tiempos[categoria] += duracion - marco[1]
                llamadas[categoria] += 1
                if pila.marcos:
                    pila.marcos[-1][1] += duracion
        return medir

    metrica_original = DeltaGenerator.metric

    def medir_primera_metrica(*args, **kwargs):
        nonlocal primera_metrica
        if primera_metrica is None:
            primera_metrica = perf_counter() - inicio
        return metrica_original(*args, **kwargs)

    resultados = []
    app = None

    def medir(nombre, accion):
        nonlocal inicio, primera_metrica
        tiempos.clear()
        llamadas.clear()
        primera_metrica = None
        inicio = perf_counter()
        accion()
        total = perf_counter() - inicio
        if app.exception or app.error:
            raise RuntimeError((nombre, [e.message for e in app.exception],
                                [e.value for e in app.error]))
        resultado = {
            "escenario": nombre, "total_s": total,
            "primera_metrica_s": primera_metrica,
            "etapas_s": dict(tiempos), "llamadas": dict(llamadas),
            "otros_s": total - sum(tiempos.values()),
            "bytes_tablas": sum(x.proto.ByteSize() for x in app.dataframe),
            "metricas": {x.label: x.value for x in app.metric},
        }
        resultados.append(resultado)
        print(json.dumps(resultado, ensure_ascii=False), flush=True)

    def nuevo(desde_menu=False):
        nonlocal app
        st.cache_data.clear()
        app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=180).run()
        if desde_menu:
            # General ahora es la raíz. Para comparar las otras vistas en frío,
            # sale al menú y descarta los datos que cargó esa entrada inicial.
            app.button(key="abrir_inicio").click().run()
            st.cache_data.clear()

    def abrir(vista):
        app.button(key=f"abrir_{vista}").click().run()

    def pestana(clave, titulo):
        if clave in app.session_state:
            app.session_state[clave] = titulo
        app.run()

    def tendencia(abierta):
        # Antes de la optimización, toda la tendencia se calcula en la entrada.
        if "general_tendencia" in app.session_state:
            app.session_state["general_tendencia"] = abierta
        app.run()

    with ExitStack() as parches:
        envueltas = {}
        for modulo in (procesamiento, datos, vistas):
            for nombre, funcion in list(vars(modulo).items()):
                if not inspect.isfunction(funcion) or funcion.__module__ != modulo.__name__:
                    continue
                if modulo is procesamiento:
                    categoria = "agregaciones" if nombre.startswith(("resumir", "cruzar", "calcular")) else "preparacion"
                else:
                    categoria = "presentacion" if modulo is vistas else "fuentes_cache"
                envueltas[id(funcion)] = instrumentar(funcion, categoria)
        for modulo in (procesamiento, datos, vistas):
            for nombre, funcion in list(vars(modulo).items()):
                if id(funcion) in envueltas:
                    parches.enter_context(patch.object(modulo, nombre, envueltas[id(funcion)]))
        leer_excel_original = pd.read_excel

        def leer_excel_comparado(*args, **kwargs):
            ruta = args[0] if args else kwargs.get("io", "")
            if (opciones.motor_trazabilidad
                    and Path(str(ruta)).name.startswith("reporte_trazabilidad_")
                    and kwargs.get("header") == 5):
                kwargs["engine"] = opciones.motor_trazabilidad
            return leer_excel_original(*args, **kwargs)

        parches.enter_context(patch.object(pd, "read_excel", instrumentar(leer_excel_comparado, "excel")))
        parches.enter_context(patch.object(DeltaGenerator, "metric", medir_primera_metrica))
        materias = datos.detectar_materias()

        medir("general_frio", nuevo)
        abrir("matricula")
        medir("general_reentrada", lambda: abrir("general"))
        medir("general_seleccion_una", lambda: app.multiselect(key="general_materias").set_value(materias[:1]).run())
        medir("general_seleccion_tres", lambda: app.multiselect(key="general_materias").set_value(materias).run())
        medir("general_abrir_tendencia", lambda: tendencia(True))
        medir("general_tendencia_repetida", app.run)
        tendencia(False)
        medir("general_actualizar_fuentes", lambda: next(b for b in app.button if b.label == "Actualizar fuentes").click().run())
        medir("general_tendencia_tras_actualizar", lambda: tendencia(True))

        for vista in ("participacion", "trazabilidad", "relacion", "individual", "rendimiento", "matricula"):
            nuevo(desde_menu=True)
            medir(f"{vista}_frio", lambda: abrir(vista))
            medir(f"{vista}_reentrada", app.run)
            medir(f"{vista}_cambio_materia", lambda: app.selectbox(key="selector_materia").select(materias[1]).run())
            materia = materias[1]
            if vista == "participacion":
                medir("participacion_abrir_evolucion", lambda: pestana(f"participacion_pestanas_{materia}", "Evolución de accesos"))
            if vista == "trazabilidad":
                medir("trazabilidad_abrir_detalle", lambda: pestana(f"trazabilidad_pestanas_{materia}", "Detalle"))
            if vista == "relacion":
                if f"relacion_trazabilidad_{materia}" in app.session_state:
                    app.session_state[f"relacion_trazabilidad_{materia}"] = True
                medir("relacion_abrir_trazabilidad", app.run)
            if vista == "individual":
                medir("individual_seleccionar", lambda: app.selectbox(key=f"individual_estudiante_{materia}").select_index(0).run())
                medir("individual_abrir_notas", lambda: pestana(f"individual_pestanas_{materia}", "Notas"))
                medir("individual_abrir_historial", lambda: pestana(f"individual_pestanas_{materia}", "Historial de actividad"))
                medir("individual_cambiar_estudiante", lambda: app.selectbox(key=f"individual_estudiante_{materia}").select_index(1).run())
                medir("individual_historial_repetido", app.run)

    fuentes = {str(p.relative_to(datos.CARPETA_DATOS)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in datos.CARPETA_DATOS.rglob("*.xlsx")}
    opciones.salida.parent.mkdir(parents=True, exist_ok=True)
    opciones.salida.write_text(json.dumps({"python": sys.version, "streamlit": st.__version__,
        "motor_trazabilidad": opciones.motor_trazabilidad or "configurado_en_app",
        "fuentes_sha256": fuentes, "mediciones": resultados}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
