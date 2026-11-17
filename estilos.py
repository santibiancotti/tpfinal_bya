"""Paleta y componentes visuales compartidos; no contiene cálculos académicos."""
from html import escape
from hashlib import sha256

import streamlit as st

AZUL = "#173653"
ACENTO = "#0F766E"
TEXTO_SECUNDARIO = "#526579"
COLORES_CONDICION = {
    "Libre": "#DC2626", "Regular": "#EAB308", "Promociona": "#15803D",
    "Pendiente": "#6B7280", "Sin notas informadas": "#6B7280",
}
NOMBRES_MATERIAS = {
    "Álgebra": "Álgebra",
    "Probabilidad y Estadística": "Prob. y Estadística",
    "Algoritmos y Estructuras de Datos": "Algoritmos",
}
COLORES_MATERIAS = {
    "Álgebra": "#6D56A0", "Probabilidad y Estadística": "#0F766E",
    "Algoritmos y Estructuras de Datos": "#2563EB",
}


def aplicar_estilos():
    st.html("""<style>
    [data-testid="stMainBlockContainer"] {max-width:1440px;padding:3.5rem 2.25rem 3rem;}
    h1,h2,h3 {color:#173653;letter-spacing:-.025em;}
    h1 {font-size:2.25rem;} h2 {font-size:1.35rem;} h3 {font-size:1.15rem;}
    [data-testid="stCaptionContainer"] {color:#526579;}
    .page-header {margin:.5rem 0 .75rem;}
    .page-header h1 {font-size:2.3rem;font-weight:720;line-height:1.18;margin:0;}
    .page-header p {color:#526579;font-size:1rem;line-height:1.55;margin:.6rem 0 0;max-width:750px;}
    .eyebrow {font-size:.72rem;font-weight:700;letter-spacing:.13em;color:#526579;margin:0 0 .7rem;}
    .marca {display:flex;gap:10px;align-items:center;color:#173653;font-size:.78rem;font-weight:700;letter-spacing:.08em;min-height:40px;}
    .marca-simbolo {display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:#173653;color:white;font-size:.75rem;}
    .st-key-barra_marca {padding-bottom:.8rem;border-bottom:1px solid #DEE6EF;}
    .st-key-navegacion {padding:.35rem 0 .8rem;}
    .st-key-navegacion button {font-size:.82rem;border-radius:8px;min-height:36px;padding:.35rem .7rem;}
    .st-key-inicio_general {background:white;border:1px solid #DCE5EF;border-left:5px solid #0F766E;border-radius:16px;padding:1.65rem;}
    .st-key-inicio_general h3 {font-size:1.9rem;margin:0;padding:0;}
    .st-key-inicio_general button[kind="primary"] p {color:white;}
    .st-key-inicio_general p {color:#526579;line-height:1.6;}
    .inicio-puntos {padding:1.1rem 1.3rem;border-radius:12px;background:#F0F5FA;color:#173653;}
    .inicio-puntos p {margin:0 0 .65rem;font-weight:600;}
    .inicio-puntos p:last-child {margin-bottom:0;}
    div[class*="st-key-inicio_tarjeta_"] {background:white;border:1px solid #DEE6EF;border-radius:14px;padding:1.2rem;min-height:240px;height:100%;}
    div[class*="st-key-inicio_tarjeta_"] h3 {font-size:1.15rem;line-height:1.3;min-height:2.6em;margin:0;padding:0;}
    div[class*="st-key-inicio_tarjeta_"] p {color:#526579;font-size:.94rem;line-height:1.5;}
    div[class*="st-key-inicio_tarjeta_"] [data-testid="stElementContainer"]:has(button) {margin-top:auto;}
    .st-key-inicio_catalogo [data-testid="stColumn"] > div {height:100%;}
    div[class*="st-key-panel_"] {background:white;border:1px solid #DEE6EF;border-radius:14px;padding:1.1rem 1.25rem;}
    div[class*="st-key-panel_"] [data-testid="stHeading"] h3 {font-size:1.25rem;line-height:1.35;padding:0;margin:0;}
    .st-key-general_kpis [data-testid="stMetric"] {background:white;border:1px solid #DEE6EF;border-radius:12px;padding:1rem 1.2rem;}
    .st-key-general_kpis [data-testid="stMetricLabel"] {color:#526579;font-size:.85rem;min-height:3em;}
    .st-key-general_kpis [data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"],
    .st-key-general_kpis [data-testid="stMetricLabel"] p {white-space:normal;overflow:visible;text-overflow:clip;}
    .st-key-general_kpis [data-testid="stMetricValue"] {color:#173653;font-size:2rem;font-weight:700;letter-spacing:-.035em;}
    [data-testid="stExpander"] {background:white;border-color:#DEE6EF;border-radius:12px;}
    [data-testid="stDataFrame"] {border-radius:9px;}
    @media(max-width:950px) {
      .st-key-general_comparaciones [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
      .st-key-general_comparaciones [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      .st-key-inicio_general [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;}
      .st-key-inicio_general [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
    }
    @media(max-width:640px) {
      [data-testid="stMainBlockContainer"] {padding:3.4rem 1rem 2rem;}
      .page-header h1 {font-size:1.9rem;}
      .st-key-inicio_general {padding:1.2rem;}
      div[class*="st-key-inicio_tarjeta_"] {min-height:0;}
      .st-key-navegacion button {font-size:.78rem;}
    }
    </style>""")


def mostrar_encabezado(titulo, descripcion, etiqueta=None):
    superior = f'<div class="eyebrow">{escape(etiqueta)}</div>' if etiqueta else ""
    st.html(f'<div class="page-header">{superior}<h1>{escape(titulo)}</h1>'
            f'<p>{escape(descripcion)}</p></div>')


def graficar(datos, especificacion, altura=230, descripcion=None):
    configuracion = {
        "font": "Segoe UI", "background": "transparent", "view": {"stroke": None},
        "axis": {"labelColor": TEXTO_SECUNDARIO, "titleColor": TEXTO_SECUNDARIO,
                 "labelFontSize": 12, "titleFontSize": 12, "titleFontWeight": 400,
                 "gridColor": "#E8EDF3", "domain": False, "ticks": False, "labelPadding": 9},
        "legend": {"labelColor": TEXTO_SECUNDARIO, "labelFontSize": 12,
                   "title": None, "orient": "bottom", "symbolType": "circle"},
    }
    firma = sha256(datos.to_json(orient="split", date_format="iso").encode("utf-8")).hexdigest()[:16]
    st.vega_lite_chart(datos, spec={"name": f"academico_{firma}", "config": configuracion, **especificacion},
                       width="stretch", height=altura, theme=None, alt=descripcion)


def nombre_materia(materia):
    return NOMBRES_MATERIAS.get(materia, materia)


def formato_numero(valor, decimales=1):
    return f"{valor:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")
