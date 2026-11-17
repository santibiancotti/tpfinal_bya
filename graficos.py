"""Gráficos de presentación con escalas, orden y tooltips explícitos."""
import streamlit as st

from estilos import AZUL, ACENTO, COLORES_MATERIAS, COLORES_CONDICION, graficar, nombre_materia, formato_numero

COLORES_ACTIVIDAD = {"Con actividad": "#285B8F", "Sin actividad": "#DCE5EF",
                     "Sin dato de actividad": "#A59AB5", "Sin registro en participación": "#7D8FA3"}


def barras(datos, categoria, valor, unidad, *, colores=None, orden=None, porcentaje=False, tooltip=None):
    """Comparación horizontal de un resumen; no construye tablas de detalle."""
    if datos.empty:
        st.info("Sin datos para esta selección.")
        return
    encoding = {
        "y": {"field": categoria, "type": "nominal", "sort": orden or "-x",
              "axis": {"title": None, "labelLimit": 260}},
        "x": {"field": valor, "type": "quantitative", "scale": {"zero": True, **({"domain": [0, 100]} if porcentaje else {})},
              "axis": {"title": unidad, **({"labelExpr": "datum.value + '%'"} if porcentaje else {"format": ".0f", "tickMinStep": 1})}},
        "tooltip": tooltip or [{"field": categoria, "type": "nominal"}, {"field": valor, "type": "quantitative", "format": ".1f" if porcentaje else ".0f"}],
    }
    if colores:
        encoding["color"] = {"field": categoria, "type": "nominal", "legend": None,
                             "scale": {"domain": list(colores), "range": list(colores.values())}}
    graficar(datos, {"mark": {"type": "bar", "color": ACENTO, "cornerRadiusEnd": 3, "size": 24},
                     "encoding": encoding}, altura=max(200, 44 * len(datos) + 50), descripcion=unidad)


def condiciones_academicas(condiciones, materia, base):
    datos = condiciones.assign(
        Porcentaje=condiciones["Porcentaje (%)"].map(lambda x: formato_numero(x) + " %" if x == x else "Sin datos"),
        Denominador=base,
    )
    barras(datos, "Condición académica", "Alumnos", "Estudiantes", colores=COLORES_CONDICION,
           orden=list(COLORES_CONDICION), tooltip=[
               {"field": "Condición académica", "type": "nominal", "title": "Condición proyectada" if materia == "Álgebra" else "Condición"},
               {"field": "Alumnos", "type": "quantitative", "title": "Estudiantes", "format": ".0f"},
               {"field": "Porcentaje", "type": "nominal"},
               {"field": "Denominador", "type": "quantitative", "format": ".0f"},
           ])


def serie_eventos(datos, fecha="Día", valor="Registros"):
    graficar(datos, {"mark": {"type": "bar", "color": ACENTO, "cornerRadiusTopLeft": 2, "cornerRadiusTopRight": 2},
                     "encoding": {
        "x": {"field": fecha, "type": "temporal", "scale": {"type": "utc"}, "axis": {"title": "Fecha", "format": "%d/%m", "tickCount": 7}},
        "y": {"field": valor, "type": "quantitative", "scale": {"zero": True}, "axis": {"title": "Eventos", "format": ".0f", "tickMinStep": 1}},
        "tooltip": [{"field": fecha, "type": "temporal", "format": "%d/%m/%Y"}, {"field": valor, "type": "quantitative", "format": ".0f"}],
    }}, altura=280, descripcion="Eventos registrados por fecha en la selección.")


def porcentajes_por_materia(datos, colores, orden):
    datos = datos.dropna(subset=["Porcentaje"])
    categorias = [grupo for grupo in colores if datos.loc[datos["Grupo"].eq(grupo), "Estudiantes"].sum() > 0]
    datos = datos.loc[datos["Grupo"].isin(categorias)]
    if datos.empty:
        st.info("No hay datos suficientes para calcular los porcentajes.")
        return
    canales = {
        "x": {"field": "Porcentaje", "type": "quantitative", "stack": "zero",
              "scale": {"domain": [0, 100]},
              "axis": {"title": "Estudiantes (%)", "values": [0, 25, 50, 75, 100],
                       "labelExpr": "datum.value + '%'"}},
        "y": {"field": "Asignatura", "type": "nominal", "sort": orden,
              "axis": {"title": None, "labelLimit": 190, "grid": False}},
        "color": {"field": "Grupo", "type": "nominal",
                  "scale": {"domain": categorias, "range": [colores[c] for c in categorias]},
                  "legend": {"columns": min(3, len(categorias))}},
        "order": {"field": "Orden", "type": "quantitative"},
        "tooltip": [
            {"field": "Materia", "type": "nominal", "title": "Asignatura"},
            {"field": "Grupo", "type": "nominal", "title": "Situación"},
            {"field": "Porcentaje visible", "type": "nominal", "title": "Porcentaje"},
            {"field": "Estudiantes", "type": "quantitative", "title": "Estudiantes", "format": ".0f"},
            {"field": "Base", "type": "quantitative", "title": "Denominador", "format": ".0f"},
            {"field": "Criterio", "type": "nominal", "title": "Criterio"},
        ],
    }
    especificacion = {
        "encoding": canales,
        "layer": [
            {"mark": {"type": "bar", "size": 30, "cornerRadius": 3}},
            {"transform": [{"filter": "datum.Porcentaje >= 8"}],
             "mark": {"type": "text", "align": "right", "dx": -6, "fontSize": 12, "fontWeight": 600},
             "encoding": {"text": {"field": "Porcentaje visible"},
                          "color": {"condition": {"test": "datum['Texto oscuro']", "value": AZUL}, "value": "white"}}},
        ],
    }
    graficar(datos, especificacion, altura=max(170, 43 * datos["Asignatura"].nunique() + 100),
             descripcion="Porcentajes de estudiantes por asignatura. El tooltip informa recuentos y denominador.")


def distribucion_resultados(distribucion, materia):
    if distribucion.empty:
        st.info("Sin resultados observados para esta asignatura.")
        return
    unidad = "Puntos acumulados informados" if materia == "Álgebra" else "Promedio observado sobre 100"
    graficar(distribucion, {
        "mark": {"type": "bar", "color": COLORES_MATERIAS.get(materia, AZUL), "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
        "encoding": {
            "x": {"field": "Intervalo", "type": "ordinal", "sort": distribucion["Intervalo"].astype(str).tolist(),
                  "axis": {"title": unidad, "labelAngle": 0, "labelOverlap": "greedy"}},
            "y": {"field": "Alumnos", "type": "quantitative", "scale": {"zero": True},
                  "axis": {"title": "Estudiantes", "format": ".0f", "tickMinStep": 1}},
            "tooltip": [{"field": "Intervalo", "type": "nominal", "title": unidad},
                        {"field": "Alumnos", "type": "quantitative", "title": "Estudiantes", "format": ".0f"}],
        },
    }, altura=230, descripcion=f"Distribución de resultados de {materia}, conservando su escala académica.")


def tendencia_accesos(tendencias, materias):
    datos = tendencias.assign(
        Asignatura=tendencias["Materia"].map(nombre_materia),
        Fecha=tendencias["Día"].dt.strftime("%d/%m/%Y"),
    )
    datos["Accesos visibles"] = datos["Accesos a secciones"].map(lambda n: formato_numero(n, 0))
    graficar(datos, {
        "mark": {"type": "line", "strokeWidth": 2.2, "point": {"filled": True, "size": 16}},
        "encoding": {
            "x": {"field": "Día", "type": "temporal", "scale": {"type": "utc"},
                  "axis": {"title": "Fecha", "format": "%d/%m", "tickCount": 7}},
            "y": {"field": "Accesos a secciones", "type": "quantitative", "scale": {"zero": True},
                  "axis": {"title": "Eventos de acceso", "format": ".0f", "tickCount": 5}},
            "color": {"field": "Asignatura", "type": "nominal",
                      "scale": {"domain": [nombre_materia(m) for m in materias],
                                "range": [COLORES_MATERIAS.get(m, AZUL) for m in materias]},
                      "legend": {"columns": 1}},
            "tooltip": [{"field": "Materia", "title": "Asignatura"}, {"field": "Fecha", "title": "Fecha"},
                        {"field": "Accesos visibles", "title": "Eventos de acceso"}],
        },
    }, altura=300, descripcion="Evolución diaria de los eventos de acceso de las asignaturas seleccionadas.")
