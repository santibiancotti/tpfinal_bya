"""Paleta y componentes visuales compartidos; no contiene cálculos académicos."""
from html import escape
from hashlib import sha256

import streamlit as st
from pandas import isna

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
    [data-testid="stMainBlockContainer"] {max-width:1440px;padding:3.75rem 2rem 3rem;}
    h1,h2,h3 {color:#173653;letter-spacing:-.025em;}
    h1 {font-size:2.25rem;} h2 {font-size:1.35rem;} h3 {font-size:1.15rem;}
    [data-testid="stCaptionContainer"] {color:#526579;}
    .page-header {margin:.15rem 0 .5rem;}
    .page-header h1 {font-size:2.5rem;font-weight:720;line-height:1.18;margin:0;}
    .page-header p {color:#526579;font-size:1.05rem;line-height:1.5;margin:.35rem 0 0;max-width:750px;}
    .eyebrow {font-size:.72rem;font-weight:700;letter-spacing:.13em;color:#526579;margin:0 0 .7rem;}
    .marca {display:flex;gap:10px;align-items:center;color:#173653;font-size:.78rem;font-weight:700;letter-spacing:.08em;min-height:40px;}
    .marca-simbolo {display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:#173653;color:white;font-size:.75rem;}
    .st-key-barra_marca {padding-bottom:.8rem;border-bottom:1px solid #DEE6EF;}
    .st-key-navegacion {padding:0 0 .4rem;}
    .st-key-navegacion button[kind="primary"] {background:#173653;border-color:#173653;}
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
    div[class*="st-key-kpis_"] {background:white;border:1px solid #DEE6EF;border-radius:16px;padding:.9rem 1.1rem;}
    :is(.st-key-general_kpis,div[class*="st-key-kpis_"]) [data-testid="stMetric"] {background:transparent;border:0;padding:0 .5rem;}
    :is(.st-key-general_kpis,div[class*="st-key-kpis_"]) [data-testid="stMetricLabel"] {color:#526579;font-size:.85rem;min-height:3em;}
    :is(.st-key-general_kpis,div[class*="st-key-kpis_"]) [data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"],
    :is(.st-key-general_kpis,div[class*="st-key-kpis_"]) [data-testid="stMetricLabel"] p {white-space:normal;overflow:visible;text-overflow:clip;}
    :is(.st-key-general_kpis,div[class*="st-key-kpis_"]) [data-testid="stMetricValue"] {color:#173653;font-size:2rem;font-weight:700;letter-spacing:-.035em;font-variant-numeric:tabular-nums;}
    div[class*="st-key-kpis_"] [data-testid="stColumn"] + [data-testid="stColumn"] {border-left:1px solid #E4EAF2;padding-left:.6rem;}
    .st-key-general_filtros {padding:.15rem 0 .25rem;}
    .st-key-general_filtros [data-testid="stCaptionContainer"] {font-size:.95rem;color:#173653;}
    .st-key-general_filtros .eyebrow {margin:0;font-size:.73rem;}
    .st-key-general_kpis {background:#173653;border-radius:18px;padding:1rem 1.25rem;}
    .st-key-general_kpis [data-testid="stColumn"] + [data-testid="stColumn"] {border-left:1px solid #476079;padding-left:1rem;}
    .st-key-general_kpis [data-testid="stColumn"] [data-testid="stMetricLabel"] {color:#D5E1ED;min-height:2.5em;}
    .st-key-general_kpis [data-testid="stMetricLabel"] p {font-size:.83rem;}
    .st-key-general_kpis [data-testid="stMetricLabel"] button {color:#D5E1ED;}
    .st-key-general_kpis [data-testid="stColumn"] [data-testid="stMetricValue"] {color:white;font-size:1.9rem;min-height:3rem;display:flex;align-items:flex-end;}
    .st-key-general_kpis [data-testid="stColumn"]:first-child [data-testid="stMetricValue"] {font-size:3rem;line-height:1;}
    .st-key-general_comparaciones {background:white;border:1px solid #DEE6EF;border-radius:18px;padding:1.25rem;}
    .st-key-general_comparaciones div[class*="st-key-panel_"] {background:transparent;border:0;border-radius:0;padding:0;}
    .st-key-general_comparaciones div.st-key-panel_general_condiciones {border-left:1px solid #E4EAF2;padding-left:1.5rem;}
    .st-key-general_comparaciones [data-testid="stCaptionContainer"] {min-height:2.7em;font-size:.84rem;}
    .st-key-panel_general_rendimiento {background:transparent!important;border:0!important;padding:.35rem 0 0!important;}
    .st-key-general_profundizar [data-testid="stHeading"] h3 {font-size:1.25rem;padding:.25rem 0;}
    .resultado-card {border:1px solid #DCE5EF;border-top:5px solid var(--materia-color);border-radius:14px;padding:1.15rem;background:white;min-height:235px;height:100%;display:flex;flex-direction:column;}
    .resultado-card h4 {font-size:1.05rem;font-weight:700;color:#173653;margin:0 0 1rem;line-height:1.3;min-height:2.6em;}
    .resultado-card .valor {font-size:2.8rem;font-weight:750;color:#173653;line-height:1;letter-spacing:-.035em;font-variant-numeric:tabular-nums;}
    .resultado-card .unidad {font-size:1rem;font-weight:500;letter-spacing:0;color:#526579;}
    .resultado-card .escala {font-size:.82rem;color:#526579;margin:.7rem 0 1rem;line-height:1.5;}
    .resultado-card .escala strong {font-weight:600;color:var(--materia-color);}
    .resultado-card footer {border-top:1px solid #E4EAF2;padding-top:.7rem;margin-top:auto;font-size:.8rem;color:#526579;line-height:1.5;}
    .resultado-card footer strong {font-size:1rem;color:#173653;font-weight:700;}
    .perfil-nombre {font-size:1.4rem;color:#173653;font-weight:700;margin-bottom:.3rem;}
    .perfil-contexto {color:#526579;font-size:.95rem;line-height:1.6;}
    [data-testid="stExpander"] {background:white;border-color:#DEE6EF;border-radius:12px;}
    [data-testid="stDataFrame"] {border-radius:9px;}
    @media(max-width:950px) {
      .st-key-general_comparaciones [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
      .st-key-general_comparaciones [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      .st-key-general_comparaciones div.st-key-panel_general_condiciones {border-left:0;border-top:1px solid #E4EAF2;padding:1.3rem 0 0;}
      .st-key-general_filtros [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
      .st-key-general_filtros [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      .resultado-card {padding:1rem .9rem;min-height:250px;}
      .resultado-card .valor {font-size:2.4rem;}
      div[class*="st-key-kpis_4_"] [data-testid="stColumn"]:nth-of-type(3) {border-left:0;padding-left:0;}
      div[class*="st-key-graficos_"] [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
      div[class*="st-key-graficos_"] [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      div[class*="st-key-kpis_4_"] [data-testid="stColumn"] {width:calc(50% - .5rem)!important;flex:1 1 calc(50% - .5rem)!important;min-width:0!important;}
      div[class*="st-key-kpis_4_"] [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      .st-key-inicio_general [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;}
      .st-key-inicio_general [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
    }
    @media(max-width:640px) {
      [data-testid="stMainBlockContainer"] {padding:3.75rem 1rem 2rem;}
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
                 "labelFontSize": 13, "titleFontSize": 13, "titleFontWeight": 400,
                 "gridColor": "#E8EDF3", "gridOpacity": .7, "domain": False, "ticks": False, "labelPadding": 9},
        "legend": {"labelColor": TEXTO_SECUNDARIO, "labelFontSize": 13, "symbolSize": 85,
                   "title": None, "orient": "bottom", "symbolType": "circle"},
    }
    firma = sha256(datos.to_json(orient="split", date_format="iso").encode("utf-8")).hexdigest()[:16]
    # Streamlit incorpora los datasets con nombre antes de inicializar Vega.
    # La tabla sin nombre se inserta después y provoca escalas vacías transitorias.
    st.vega_lite_chart(spec={"name": f"academico_{firma}", "config": configuracion,
                            **especificacion, "data": {"name": "datos_academicos"},
                            "datasets": {"datos_academicos": datos}},
                       width="stretch", height=altura, theme=None, alt=descripcion)


def nombre_materia(materia):
    return NOMBRES_MATERIAS.get(materia, materia)


def indicadores(items, clave):
    """Fila compacta de métricas nativas con ayudas opcionales."""
    with st.container(key=f"kpis_{len(items)}_{clave}"):
        for columna, item in zip(st.columns(len(items), vertical_alignment="bottom"), items):
            columna.metric(item[0], item[1], help=item[2] if len(item) > 2 else None)


def tarjeta_resultado(materia, valor, cantidad):
    algebra = materia == "Álgebra"
    numero = "Sin datos" if isna(valor) else formato_numero(valor, 2)
    unidad = "puntos" if algebra else "/ 100"
    escala = "Acumulado parcial" if algebra else "Promedio de notas informadas"
    referencia = "Esquema de 120 puntos" if algebra else "Escala de 0 a 100"
    color = COLORES_MATERIAS.get(materia, AZUL)
    st.html(f'<article class="resultado-card" style="--materia-color:{color}">'
            f'<h4 title="{escape(materia)}">{escape(nombre_materia(materia))}</h4>'
            f'<div class="valor">{numero} <span class="unidad">{unidad}</span></div>'
            f'<p class="escala"><strong>{escala}</strong><br>{referencia}</p>'
            f'<footer><strong>{int(cantidad)}</strong> estudiantes con resultado</footer></article>')


def formato_numero(valor, decimales=1):
    return f"{valor:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")
