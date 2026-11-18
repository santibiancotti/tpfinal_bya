import streamlit as st

import pandas as pd

from hashlib import sha256
from html import escape
from estilos import (mostrar_encabezado, nombre_materia, formato_numero,
                     COLORES_CONDICION, NOMBRES_MATERIAS, indicadores, tarjeta_resultado, graficar)
from graficos import (porcentajes_por_materia, distribucion_resultados, tendencia_accesos,
                      barras, condiciones_academicas, serie_eventos, COLORES_ACTIVIDAD,
                      cruce_categorias, dispersion)

from procesamiento import (FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones, resumir_actividad, 
                           filtrar_trazabilidad, DIAS_SEMANA, resumir_horarios, resumir_accesos_diarios, resumir_participacion, resumir_instrumentos,
                           resumir_resultados_alumnos, resumir_distribucion_resultados,
                           resumir_condiciones, calcular_correlacion, agregar_actividad_trazabilidad)

DASHBOARDS = [
        (
            "general",
            "General",
            "Actividad y resultados de las materias.",
        ),
        (
            "participacion",
            "Participación",
            "Actividad, avance y tiempo de uso de los alumnos.",
        ),
        (
            "trazabilidad",
            "Trazabilidad",
            "Detalle de interacciones y distribución temporal.",
        ),
        (
            "rendimiento",
            "Rendimiento académico",
            "Calificaciones y situación académica por materia.",
        ),
        (
            "relacion",
            "Notas y participación",
            "Relación entre actividad y rendimiento académico.",
        ),
        (
            "individual",
            "Individual",
            "Información integrada de un estudiante.",
        ),
        (
            "matricula",
            "Matrícula y alertas",
            "Inscripciones y comparación con la actividad del aula.",
        ),
]


def mostrar_barra_navegacion(paginas, pagina_actual):
    with st.container(key="barra_marca"):
        marca, acciones = st.columns([4, 1.3], vertical_alignment="center")
        with marca:
            st.html('<div class="marca"><span class="marca-simbolo" aria-hidden="true">BI</span>'
                    '<span>SEGUIMIENTO ACADÉMICO</span></div>')
        with acciones:
            if st.button("Actualizar fuentes", key="actualizar_fuentes", type="tertiary",
                         icon=":material/refresh:", width="stretch", wrap=True,
                         help="Vuelve a leer las fuentes y actualiza los resultados. Las secciones cerradas se cargarán al abrirlas."):
                st.cache_data.clear()
                st.rerun()
    if pagina_actual.url_path == paginas["inicio"].url_path:
        return
    with st.container(horizontal=True, wrap=True, key="navegacion", gap="small"):
        for clave, titulo, _ in DASHBOARDS:
            titulo = {"rendimiento": "Rendimiento", "matricula": "Matrícula y alertas"}.get(clave, titulo)
            activo = pagina_actual.url_path == paginas[clave].url_path
            if st.button(titulo, key=f"abrir_{clave}", type="primary" if activo else "tertiary",
                         icon=":material/home:" if clave == "general" else None):
                st.switch_page(paginas[clave])
        if st.button("Todas las vistas", key="abrir_inicio", type="primary" if pagina_actual.url_path == paginas["inicio"].url_path else "tertiary"):
            st.switch_page(paginas["inicio"])


def mostrar_inicio(paginas):
    mostrar_encabezado("Seguimiento académico", "Participación, rendimiento y matrícula en un mismo lugar.",
                        "TRABAJO FINAL INTEGRADOR · BI & ANALYTICS")
    with st.container(key="inicio_general"):
        principal, alcance = st.columns([2.3, 1], gap="large", vertical_alignment="center")
        with principal:
            st.html('<div class="eyebrow">VISIÓN CONSOLIDADA</div>')
            st.subheader("General")
            st.write("Empezá por el panorama de la cursada. Compará la actividad y los resultados de las asignaturas y explorá su evolución.")
            if st.button("Abrir General", key="abrir_general", type="primary",
                         icon=":material/arrow_forward:", icon_position="right"):
                st.switch_page(paginas["general"])
        with alcance:
            st.html('<div class="inicio-puntos"><p>Actividad y cobertura</p>'
                    '<p>Resultados por asignatura</p><p>Tendencias de participación</p></div>')
    st.subheader("Explorá cada dimensión")
    st.caption("Seis vistas para profundizar en los indicadores y consultar trayectorias individuales.")
    categorias = ["ACTIVIDAD", "INTERACCIONES", "EVALUACIONES", "ANÁLISIS CRUZADO", "ESTUDIANTES", "INSCRIPCIONES"]
    with st.container(key="inicio_catalogo"):
        for inicio in range(0, 6, 3):
            for columna, dashboard, categoria in zip(st.columns(3, gap="medium"),
                                                     DASHBOARDS[inicio + 1:inicio + 4], categorias[inicio:inicio + 3]):
                clave, titulo, descripcion = dashboard
                with columna, st.container(key=f"inicio_tarjeta_{clave}"):
                    st.html(f'<div class="eyebrow">{categoria}</div>')
                    st.subheader(titulo)
                    st.write(descripcion)
                    if st.button("Abrir vista", key=f"abrir_{clave}", width="stretch",
                                 icon=":material/arrow_forward:", icon_position="right"):
                        st.switch_page(paginas[clave])

def mostrar_matricula(matriculados, matricula_actual, base_alumnos):
    with st.container(key="panel_matricula_filtros"):
        poblacion = st.radio("Población a consultar", list(FILTROS_POBLACION), horizontal=True, key="matricula_poblacion")
        seleccion = seleccionar_poblacion(base_alumnos, poblacion)
        filtros = {}
        for contenedor, campo in zip(st.columns(3), ["Situación de matrícula", "Situación de actividad", "Alerta"]):
            filtros[campo] = contenedor.selectbox(campo, ["Todas"] + sorted(seleccion[campo].dropna().unique().tolist()),
                                                 key=f"matricula_filtro_{campo}")
    seleccion = filtrar_situaciones(seleccion, filtros)
    cantidad = len(seleccion)
    alertas = int(seleccion["Tiene alerta"].sum())
    con_actividad = int(seleccion["Con actividad"].eq(True).sum())
    sin_actividad = int(seleccion["Con actividad"].eq(False).sum())
    sin_dato = int(seleccion["Con actividad"].isna().sum())
    indicadores([
        ("Estudiantes seleccionados", cantidad, "Población y filtros actuales; una fila por estudiante."),
        ("Con matrícula vigente", int(seleccion["Matrícula vigente"].sum())),
        ("Con actividad registrada", con_actividad, "Una o más interacciones durante el período del reporte."),
        ("Sin actividad registrada", sin_actividad, "Cero interacciones informadas. No incluye los datos faltantes."),
    ], "matricula")
    if not cantidad:
        st.info("No hay estudiantes para esta selección.")
    if alertas:
        st.warning(f"{alertas} estudiantes con alertas en la selección.")
    if sin_dato:
        st.info(f"{sin_dato} estudiantes sin dato de actividad; no se cuentan como inactivos.")
    with st.container(key="panel_matricula_comparacion"):
        st.subheader("Matrícula y actividad")
        grupos = seleccion.groupby(["Situación de matrícula", "Situación de actividad"], as_index=False).agg(Estudiantes=("Identificación", "size"))
        colores = {"Con actividad registrada": "#285B8F", "Sin actividad registrada": "#DCE5EF",
                   "Actividad sin determinar": "#A59AB5", "Sin registro en participación": "#7D8FA3"}
        if cantidad:
            cruce_categorias(grupos, "Situación de matrícula", "Situación de actividad", colores, cantidad,
                             orden=["Vigente", "Baja", "Sin registro en matrícula", "Estado sin informar"])
        st.caption("Actividad del período completo; puede ser anterior a una baja.")
    with st.container(key="panel_matricula_casos"):
        st.subheader("Casos de la selección")
        st.dataframe(seleccion[["Estudiante", "Identificación", "Alerta"]], hide_index=True, width="stretch", height=310,
                     column_config={"Estudiante": st.column_config.TextColumn(width=170),
                                    "Identificación": st.column_config.TextColumn("ID", width=130),
                                    "Alerta": st.column_config.TextColumn(width=350)})
        secundarias = st.expander("Ver situaciones e interacciones", key="matricula_columnas", on_change="rerun")
        if secundarias.open:
            with secundarias:
                st.dataframe(seleccion[["Identificación", "Estudiante", "Situación de matrícula", "Situación de actividad",
                                         "Alerta", "Interacciones", "Última interacción"]], hide_index=True,
                    column_config={"Última interacción": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")})
    historial = st.expander("Ver historial de matrícula", key="matricula_historial", on_change="rerun")
    if historial.open:
        with historial:
            st.caption(f"{len(matriculados)} registros originales; {len(matricula_actual)} estudiantes tras consolidar.")
            st.dataframe(matriculados, hide_index=True, height=350)
    metodo = st.expander("Criterios de matrícula y alertas", key="matricula_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            st.write("Matrícula vigente: último movimiento por fecha de inscripción y transacción con estado Aceptada. "
                     "Sin registro en matrícula no significa baja. La actividad procede del reporte completo; una ausencia de dato no es cero. "
                     "Los indicadores, el gráfico y la lista respetan la población y los tres filtros seleccionados.")
            st.write("Alertas: vigente sin actividad, sin registro en participación o con actividad sin determinar; "
                     "actividad sin registro en matrícula, con baja registrada o con otro estado de matrícula. "
                     "Las alertas describen cruces entre fuentes; no determinan una nueva condición académica.")


def mostrar_resumen_participacion(participacion, participacion_alumnos):
    resumen = resumir_participacion(participacion_alumnos)
    materia = st.session_state["materia_actual"]
    cobertura, tiempo = resumen["cobertura"], resumen["tiempo_promedio"]
    indicadores([
        ("Alumnos", resumen["alumnos"], "Perfil Alumnos del reporte completo."),
        ("Alumnos con actividad", resumen["con_actividad"], "Una o más interacciones en el período del reporte."),
        ("Cobertura de participación", formato_numero(cobertura) + " %" if cobertura is not None else "Sin datos",
         f"Denominador: {resumen['con_dato_actividad']} alumnos con dato de actividad."),
        ("Tiempo promedio estimado", formato_numero(tiempo) + " min" if tiempo is not None else "Sin datos",
         f"Media de {resumen['con_tiempo']} tiempos informados, incluidos los ceros."),
    ], "participacion")
    base = resumen["con_dato_actividad"]
    with st.container(key="panel_participacion_actividad"):
        st.subheader("Actividad durante el período")
        filas = []
        for orden, (grupo, n) in enumerate([("Con actividad", resumen["con_actividad"]), ("Sin actividad", resumen["sin_actividad"])]):
            porcentaje = 100 * n / base if base else float("nan")
            filas.append({"Materia": materia, "Asignatura": nombre_materia(materia), "Grupo": grupo,
                          "Estudiantes": n, "Porcentaje": porcentaje, "Porcentaje visible": formato_numero(porcentaje) + " %",
                          "Base": base, "Orden": orden, "Texto oscuro": grupo == "Sin actividad",
                          "Criterio": "Una o más interacciones" if orden == 0 else "Cero interacciones informadas"})
        porcentajes_por_materia(pd.DataFrame(filas), COLORES_ACTIVIDAD, [nombre_materia(materia)])
        st.caption(f"Base: {base} alumnos con dato de actividad.")
        if resumen["alumnos"] > base:
            st.info(f"{resumen['alumnos'] - base} alumnos sin dato de actividad; no se consideran inactivos.")
    listado = st.expander("Ver alumnos", key="participacion_alumnos", on_change="rerun")
    if listado.open:
        with listado:
            columnas = [c for c in ["Usuario", "Apellido", "Nombre", "Interacciones", "Tiempo de uso (minutos)", "Avance"] if c in participacion_alumnos]
            st.dataframe(participacion_alumnos[columnas].assign(Avance=participacion_alumnos["Avance"].astype("string")),
                         hide_index=True, width="stretch", height=350)
    original = st.expander("Ver reporte con todos los perfiles", key="participacion_original", on_change="rerun")
    if original.open:
        with original:
            st.dataframe(participacion.assign(Avance=participacion["Avance"].astype("string")), hide_index=True, height=350)
    metodo = st.expander("Criterios de participación", key="participacion_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            st.write(f"El reporte contiene {len(participacion)} usuarios de todos los perfiles y {resumen['alumnos']} alumnos. "
                     f"La cobertura usa {base} alumnos con actividad informada. El tiempo medio es una estimación sobre "
                     f"{resumen['con_tiempo']} valores, incluidos los ceros. El resumen siempre usa el período completo del reporte.")


def mostrar_participacion(participacion, participacion_alumnos, cargar_evolucion):
    materia = st.session_state["materia_actual"]
    pestana_resumen, pestana_evolucion = st.tabs(
        ["Resumen del reporte completo", "Evolución de accesos"],
        key=f"participacion_pestanas_{materia}", on_change="rerun",
    )
    if pestana_resumen.open:
        with pestana_resumen:
            mostrar_resumen_participacion(participacion, participacion_alumnos)
    if not pestana_evolucion.open:
        return
    with pestana_evolucion:
        try:
            with st.spinner(f"Cargando evolución de {materia}; la primera lectura puede tardar..."):
                resumen_eventos = cargar_evolucion()
        except (FileNotFoundError, ValueError) as error:
            st.error(str(error))
            return
        eventos = resumen_eventos["eventos"]
        if eventos.empty:
            st.info("El reporte no contiene registros de alumnos.")
            return
        filtros = seleccionar_filtros_actividad(eventos, "participacion", resumen_eventos["usuarios"])
        if filtros is None:
            return
        periodo, usuario = filtros
        resumen = resumir_accesos_diarios(eventos, periodo[0], periodo[1], usuario)
        indicadores([("Accesos a secciones en el período", int(resumen["Accesos a secciones"].sum()),
                      "Eventos Acceder, incluidas las repeticiones; no son sesiones.")], "evolucion")
        with st.container(key="panel_participacion_evolucion"):
            st.subheader("Accesos diarios a secciones")
            tendencia_accesos(resumen.assign(Materia=materia), [materia])
            st.caption("Eventos de acceso, no sesiones. El filtro afecta solo esta evolución.")
        detalle = st.expander("Ver valores diarios", key=f"participacion_valores_{materia}", on_change="rerun")
        if detalle.open:
            with detalle:
                st.dataframe(resumen, hide_index=True, column_config={"Día": st.column_config.DateColumn(format="DD/MM/YYYY")})


def seleccionar_filtros_actividad(eventos, prefijo, usuarios=None):
    prefijo = f"{prefijo}_{st.session_state.get('materia_actual', '')}"
    fecha_min = eventos["Fecha"].min().date()
    fecha_max = eventos["Fecha"].max().date()

    columna_fecha, columna_usuario = st.columns(2)
    periodo = columna_fecha.date_input(
        "Período a consultar",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        format="DD/MM/YYYY",
        key=f"{prefijo}_periodo_{fecha_min}_{fecha_max}",
    )

    if usuarios is None:
        usuarios = (
            eventos[["Usuario", "Apellido", "Nombre"]]
            .drop_duplicates(subset="Usuario").sort_values("Usuario")
        )

    etiquetas = {
        usuario: f"{usuario} - {apellido}, {nombre}"
        for usuario, apellido, nombre
        in usuarios.itertuples(index=False, name=None)
    }

    usuario = columna_usuario.selectbox(
        "Estudiante",
        options=[None] + list(etiquetas),
        format_func=lambda valor: (
            "Todos" if valor is None else etiquetas[valor]
        ),
        key=f"{prefijo}_estudiante",
        help="La lista incluye alumnos con registros en el reporte completo.",
    )

    if len(periodo) != 2:
        st.info("Seleccioná la fecha de inicio y la fecha final.")
        return None

    return periodo, usuario

def mostrar_trazabilidad(resumen_eventos, cargar_detalle, cargar_original):
    materia = st.session_state["materia_actual"]
    trazabilidad_alumnos = resumen_eventos["eventos"]
    if trazabilidad_alumnos.empty:
        st.info(
            "El reporte no contiene registros de alumnos."
        )
        return

    filtros = seleccionar_filtros_actividad(
        trazabilidad_alumnos,
        "trazabilidad",
        resumen_eventos["usuarios"],
    )

    if filtros is None:
        return

    periodo, usuario_seleccionado = filtros

    trazabilidad_alumnos = filtrar_trazabilidad(
        trazabilidad_alumnos,
        periodo[0],
        periodo[1],
        usuario_seleccionado,
    )

    if trazabilidad_alumnos.empty:
        st.info(
            "No hay registros para el período "
            "y estudiante seleccionados."
        )

    cantidad_repeticiones = int(
        trazabilidad_alumnos[
            "Repetición exacta adicional"
        ].sum()
    )

    cantidad_alumnos = (
        trazabilidad_alumnos["Usuario"].nunique()
    )

    dias_periodo = (pd.Timestamp(periodo[1]) - pd.Timestamp(periodo[0])).days + 1
    cantidad_registros = int(trazabilidad_alumnos["Registros"].sum())
    indicadores([
        ("Registros seleccionados", cantidad_registros, "Eventos de alumnos de la selección, incluidas las repeticiones."),
        ("Alumnos con eventos", cantidad_alumnos),
        ("Interacciones promedio por día del período", formato_numero(cantidad_registros / dias_periodo, 2), "Incluye todos los días del período seleccionado."),
        ("Repeticiones exactas adicionales", cantidad_repeticiones, "Permanecen incluidas en los recuentos."),
    ], "trazabilidad")

    configuracion = [
        ("Por día", "Día"),
        ("Por semana", "Semana"),
        ("Por acción", "Acción"),
    ]

    pestanas = st.tabs(
        ["Mapa horario"]
        + [
            titulo
            for titulo, campo in configuracion
        ]
        + ["Detalle"], key=f"trazabilidad_pestanas_{materia}", on_change="rerun",
    )

    with pestanas[0]:
        if pestanas[0].open and not trazabilidad_alumnos.empty:
            with st.container(key="panel_trazabilidad_mapa"):
                horarios = resumir_horarios(
                    trazabilidad_alumnos
                )

                firma_mapa = sha256(
                    horarios.to_json(
                        orient="split"
                    ).encode("utf-8")
                ).hexdigest()

                st.subheader("Actividad por día y hora")
                graficar(
                    horarios,
                    especificacion={
                        "name": f"mapa_horario_{firma_mapa}",
                        "mark": "rect",
                        "encoding": {
                            "x": {
                                "field": "Hora",
                                "type": "ordinal",
                                "title": "Hora del día",
                                "sort": list(range(24)),
                            },
                            "y": {
                                "field": "Nombre del día",
                                "type": "ordinal",
                                "title": None,
                                "sort": DIAS_SEMANA,
                            },
                            "color": {
                                "field": "Registros",
                                "type": "quantitative",
                                "title": "Registros",
                                "scale": {
                                    "scheme": "blues",
                                    "zero": True,
                                },
                            },
                            "tooltip": [
                                {
                                    "field": "Nombre del día",
                                    "type": "nominal",
                                    "title": "Día",
                                },
                                {
                                    "field": "Hora",
                                    "type": "ordinal",
                                    "title": "Hora",
                                },
                                {
                                    "field": "Registros",
                                    "type": "quantitative",
                                    "title": "Registros",
                                    "format": ",.0f",
                                },
                            ],
                        },
                    },
                    altura=280,
                )

                st.caption("Registros de la selección, incluidas las repeticiones.")

    for pestana, (titulo, campo) in zip(pestanas[1:], configuracion):
        if not pestana.open:
            continue
        with pestana:
            resumen = resumir_actividad(trazabilidad_alumnos, campo)
            with st.container(key=f"panel_trazabilidad_{campo}"):
                st.subheader({"Día": "Eventos por día", "Semana": "Eventos por semana", "Acción": "Acciones con más eventos"}[campo])
                if campo == "Acción":
                    barras(resumen.head(10), campo, "Registros", "Eventos")
                    st.caption("Hasta diez acciones con más eventos.")
                else:
                    serie_eventos(resumen, campo)
            valores = st.expander("Ver valores del resumen", key=f"trazabilidad_valores_{campo}_{materia}", on_change="rerun")
            if valores.open:
                with valores:
                    st.dataframe(resumen, hide_index=True, column_config={campo: st.column_config.DateColumn(format="DD/MM/YYYY")} if campo != "Acción" else {})

    if pestanas[-1].open:
        with pestanas[-1]:
            try:
                with st.spinner("Cargando el detalle de la selección..."):
                    detalle = cargar_detalle(periodo[0], periodo[1], usuario_seleccionado)
            except (FileNotFoundError, ValueError) as error:
                st.error(str(error))
            else:
                st.dataframe(detalle, hide_index=True)

    original = st.expander("Ver reporte original con todos los perfiles",
                           key=f"trazabilidad_original_{materia}", on_change="rerun")
    if original.open:
        with original:
            try:
                with st.spinner("Cargando el reporte original completo..."):
                    st.dataframe(cargar_original(), hide_index=True)
            except (FileNotFoundError, ValueError) as error:
                st.error(str(error))
    metodo = st.expander("Criterios de trazabilidad", key="trazabilidad_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            st.metric("Registros del reporte (total)", resumen_eventos["total_reporte"])
            st.write("El total del reporte incluye todos los perfiles y no cambia con los filtros. "
                     "Los gráficos y los otros indicadores usan el período y el estudiante seleccionados. "
                     "Las repeticiones marcadas permanecen incluidas. En el mapa, cada celda suma un día de semana y una hora; "
                     "la hora 20 comprende desde las 20:00 hasta antes de las 21:00.")


def mostrar_rendimiento(calificaciones, materia, resultados=None):
    try:
        if resultados is None:
            resultados = resumir_resultados_alumnos(calificaciones, materia)
    except ValueError as error:
        st.info(str(error))
        return
    observados = resultados["Resultado observado"].dropna()
    media = observados.mean() if not observados.empty else None
    indicadores([
        ("Alumnos con resultado observado", len(observados), "Estudiantes con al menos una nota informada."),
        ("Resultado medio", formato_numero(media, 2) + (" pts" if materia == "Álgebra" else " / 100") if media is not None else "Sin datos",
         "Media de puntos acumulados parciales de un esquema de 120." if materia == "Álgebra" else "Promedio de notas informadas sobre 100."),
        ("Instrumentos disponibles", calificaciones["Instrumento"].nunique()),
    ], "rendimiento")
    if materia == "Álgebra":
        st.caption("Álgebra · puntos acumulados parciales / esquema de 120 · condición proyectada.")
    comparacion, distribucion = st.tabs(["Comparación por instrumento", "Distribución de resultados"],
        key=f"rendimiento_pestanas_{materia}", on_change="rerun")
    if comparacion.open:
        with comparacion, st.container(key="panel_rendimiento_instrumentos"):
            st.subheader("Rendimiento medio por instrumento")
            resumen = resumir_instrumentos(calificaciones)
            barras(resumen.dropna(subset=["Promedio (%)"]), "Instrumento", "Promedio (%)", "Promedio obtenido (%)", porcentaje=True,
                tooltip=[{"field": "Instrumento", "type": "nominal"},
                         {"field": "Promedio (%)", "type": "quantitative", "format": ".2f"},
                         {"field": "Notas informadas", "type": "quantitative", "format": ".0f"}])
            valores = st.expander("Ver valores por instrumento", key="rendimiento_instrumentos_valores", on_change="rerun")
            if valores.open:
                with valores:
                    st.dataframe(resumen.round({"Promedio (%)": 2}), hide_index=True)
    if distribucion.open:
        with distribucion, st.container(key="graficos_rendimiento"):
            histograma, condicion = st.columns(2, gap="medium")
            with histograma, st.container(key="panel_rendimiento_histograma"):
                st.subheader("Distribución de resultados")
                hist = resumir_distribucion_resultados(resultados)
                distribucion_resultados(hist, materia)
            with condicion, st.container(key="panel_rendimiento_condicion"):
                st.subheader("Condición proyectada" if materia == "Álgebra" else "Condición académica")
                condiciones = resumir_condiciones(resultados)
                condiciones_academicas(condiciones, materia, len(resultados))
                st.caption(f"Base: {len(resultados)} estudiantes presentes en calificaciones.")
            valores = st.expander("Ver valores de resultados y condiciones", key="rendimiento_resultados_valores", on_change="rerun")
            if valores.open:
                with valores:
                    st.dataframe(hist, hide_index=True)
                    st.markdown(f"**{etiqueta_condicion(materia)}**")
                    st.dataframe(condiciones.round(2), hide_index=True)
    metodo = st.expander("Criterios de rendimiento", key="rendimiento_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            st.write("Los promedios por instrumento usan porcentajes y solo notas informadas. Cada estudiante aporta un resultado "
                     "a la distribución. Los intervalos incluyen su límite superior; el primero incluye el cero. "
                     f"Las condiciones usan {len(resultados)} estudiantes presentes en los archivos de calificaciones. "
                     "Las notas faltantes no se convierten en cero.")
            mostrar_criterio_academico(materia)


def etiqueta_condicion(materia, habitual="Condición académica"):
    if materia == "Álgebra":
        return "Condición proyectada según notas informadas"
    return habitual


def mostrar_semaforo(condicion, materia):
    color = COLORES_CONDICION[condicion]

    st.html(
        f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span
                aria-hidden="true"
                style="width: 14px; height: 14px; flex-shrink: 0;
                       border-radius: 50%; background-color: {color};"
            ></span>
            <span>
                <strong>{etiqueta_condicion(materia, "Condición según notas informadas")}</strong>
                · {condicion}
            </span>
        </div>
        """
    )

def mostrar_individual(base_alumnos, calificaciones, materia, cargar_historial, resultados=None):
    alumnos_por_id = base_alumnos.set_index("Identificación")
    nombres_notas = calificaciones.drop_duplicates(subset="Usuario").set_index("Usuario")
    nombres_notas = nombres_notas["Apellido"] + ", " + nombres_notas["Nombre"]
    nombres = alumnos_por_id["Estudiante"].combine_first(nombres_notas).fillna("Nombre no informado").sort_index()
    usuario = st.selectbox("Estudiante", nombres.index.tolist(), index=None, placeholder="Seleccioná un estudiante",
                          format_func=lambda valor: f"{valor} - {nombres.loc[valor]}", key=f"individual_estudiante_{materia}")
    if usuario is None:
        st.info("Seleccioná un estudiante para consultar su situación.")
        return
    if resultados is None:
        resultados = resumir_resultados_alumnos(calificaciones, materia)
    coincidencias = resultados.loc[resultados["Usuario"].eq(usuario)]
    fila = coincidencias.iloc[0] if not coincidencias.empty else None
    alumno = alumnos_por_id.loc[usuario] if usuario in alumnos_por_id.index else None
    condicion = fila["Condición académica"] if fila is not None else "Sin notas informadas"
    valor = fila["Resultado observado"] if fila is not None else None
    maximo = fila.get("Máximo de sus notas", 100) if fila is not None else None
    estado = alumno["Situación de matrícula"] if alumno is not None else "Sin registro en matrícula"
    actividad = alumno["Situación de actividad"] if alumno is not None else "Sin registro en participación"
    with st.container(key="panel_individual_identidad"):
        st.html(f'<div class="perfil-nombre">{escape(nombres.loc[usuario])}</div>'
                f'<div class="perfil-contexto">{escape(usuario)} · {escape(estado)} · {escape(actividad)}</div>')
        mostrar_semaforo(condicion, materia)
    resultado_visible = (formato_numero(valor, 2) + " / " + formato_numero(maximo, 0) + (" pts" if materia == "Álgebra" else "")) if pd.notna(valor) else "Sin datos"
    interacciones = alumno["Interacciones"] if alumno is not None else None
    indicadores([
        ("Resultado observado", resultado_visible, "Puntos obtenidos sobre el máximo de las evaluaciones con nota." if materia == "Álgebra" else "Promedio sobre 100; incluye el recuperatorio informado en Probabilidad."),
        ("Instrumentos con nota", f"{int(fila['Instrumentos con nota'])} de {int(fila['Instrumentos disponibles'])}" if fila is not None else "Sin notas"),
        ("Interacciones", int(interacciones) if pd.notna(interacciones) else "Sin datos"),
    ], "individual")
    resumen, notas_tab, historial = st.tabs(["Matrícula y participación", "Notas", "Historial de actividad"],
        key=f"individual_pestanas_{materia}", on_change="rerun")
    if resumen.open:
        with resumen, st.container(key="panel_individual_resultado"):
            st.subheader("Resultado y participación")
            if pd.notna(valor):
                porcentaje = fila["Rendimiento observado (%)"] if materia == "Álgebra" else valor
                st.progress(float(porcentaje) / 100, text=("Rendimiento sobre notas informadas" if materia == "Álgebra" else "Promedio observado") + f" · {formato_numero(porcentaje, 1)} %")
                if materia == "Álgebra":
                    st.caption(f"Las notas informadas cubren {formato_numero(maximo, 0)} de los 120 puntos del esquema. Condición proyectada.")
            tiempo = alumno["Tiempo de uso (minutos)"] if alumno is not None else None
            st.caption("Tiempo estimado: " + (formato_numero(tiempo, 0) + " min" if pd.notna(tiempo) else "sin datos") + ". Actividad del período completo del reporte.")
    if notas_tab.open:
        with notas_tab, st.container(key="panel_individual_notas"):
            st.subheader("Resultados por instrumento")
            notas = calificaciones.loc[calificaciones["Usuario"].eq(usuario)]
            barras(notas.dropna(subset=["Porcentaje obtenido"]), "Instrumento", "Porcentaje obtenido", "Porcentaje obtenido (%)", porcentaje=True,
                tooltip=[{"field": "Instrumento", "type": "nominal"}, {"field": "Nota", "type": "nominal"},
                         {"field": "Porcentaje obtenido", "type": "quantitative", "format": ".2f"}])
            st.caption("Porcentajes por instrumento; una evaluación sin nota no equivale a cero.")
            detalle = st.expander("Ver notas y observaciones", key="individual_notas_detalle", on_change="rerun")
            if detalle.open:
                with detalle:
                    st.dataframe(notas[["Instrumento", "Nota", "Puntos obtenidos", "Puntos máximos", "Porcentaje obtenido", "Observaciones"]].round({"Porcentaje obtenido": 2}), hide_index=True)
    if historial.open:
        with historial:
            try:
                with st.spinner("Cargando historial de actividad..."):
                    eventos = cargar_historial(usuario)
            except (FileNotFoundError, ValueError) as error:
                st.error(str(error))
                return
            if eventos.empty:
                st.info("Sin registros de trazabilidad para este estudiante.")
            else:
                indicadores([("Registros de trazabilidad", len(eventos)), ("Accesos a secciones", int(eventos["Acción"].eq("Acceder").sum()))], "individual_historial")
                with st.container(key="panel_individual_historial"):
                    st.subheader("Actividad diaria del estudiante")
                    diarios = eventos.groupby(eventos["Fecha"].dt.normalize()).size().rename_axis("Día").reset_index(name="Registros")
                    serie_eventos(diarios)
                    st.caption("Eventos del reporte de trazabilidad; repeticiones incluidas.")
                    detalle = st.expander("Ver eventos del estudiante", key="individual_historial_detalle", on_change="rerun")
                    if detalle.open:
                        with detalle:
                            st.dataframe(eventos[["Fecha", "Sección", "Acción", "Descripción", "Repetición exacta adicional"]].sort_values("Fecha", ascending=False),
                                hide_index=True, column_config={"Fecha": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")})
    metodo = st.expander("Criterios del resultado individual", key="individual_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            mostrar_criterio_academico(materia)
            st.write("Las notas faltantes no se convierten en cero. Matrícula muestra el último estado disponible; "
                     "participación corresponde al período completo y el tiempo es estimado.")


def mostrar_criterio_academico(materia):
    if materia == "Álgebra":
        st.caption(
            "En Álgebra, la condición se proyecta proporcionalmente a partir de los puntos "
            "obtenidos y el máximo de las evaluaciones con nota. Por ejemplo, 34/45 equivale "
            "a 90,67/120 y proyecta promoción. La proyección se actualiza al incorporar "
            "nuevas calificaciones."
        )
    else:
        promocion = 90 if materia == "Algoritmos y Estructuras de Datos" else 85
        st.caption(
            f"Promedio sobre 100 de las notas informadas, incluido el recuperatorio si existe. "
            f"Libre: <60; regular: desde 60 y <{promocion}; promociona: desde {promocion}. "
            "El resultado es observado y puede cambiar con nuevas notas."
        )


def mostrar_general(resumen, alumnos, resultados, cargar_tendencias):
    materias = [m for m in NOMBRES_MATERIAS if m in resumen["Materia"].values]
    materias += [m for m in resumen["Materia"] if m not in materias]
    orden = [nombre_materia(m) for m in materias]
    with st.container(key="general_kpis"):
        principal, asignaturas, registros = st.columns([1.5, 1, 1.2], vertical_alignment="bottom")
        principal.metric("Estudiantes únicos en las aulas", alumnos["Usuario"].nunique(),
                    help="Identificadores distintos entre las aulas seleccionadas; una persona se cuenta una sola vez.")
        asignaturas.metric("Asignaturas", len(resumen), help="Asignaturas incluidas en la selección actual.")
        registros.metric("Registros alumno-materia en las aulas", len(alumnos),
                    help="Cada estudiante se cuenta una vez por asignatura. Una persona puede participar en más de una.")

    actividad, condiciones = datos_graficos_general(resumen, resultados)
    with st.container(key="general_comparaciones"):
        izquierda, derecha = st.columns(2, gap="medium")
        with izquierda, st.container(key="panel_general_actividad"):
            st.subheader("Actividad por materia")
            st.caption("Porcentaje sobre alumnos con dato de actividad.")
            porcentajes_por_materia(actividad, {"Con actividad": "#285B8F", "Sin actividad": "#DCE5EF"}, orden)
        with derecha, st.container(key="panel_general_condiciones"):
            st.subheader("Condición académica")
            st.caption("Estudiantes en archivos de notas · Álgebra: proyectada."
                       if "Álgebra" in materias else "Estudiantes presentes en los archivos de notas.")
            orden_condiciones = [m + " · proyectada" if m == "Álgebra" else m for m in orden]
            porcentajes_por_materia(condiciones, COLORES_CONDICION, orden_condiciones)

    with st.container(key="panel_general_rendimiento"):
        st.subheader("Resultados por materia")
        vista = resumen.set_index("Materia").reindex(materias).reset_index()
        for columna, fila in zip(st.columns(len(materias)), vista.to_dict("records")):
            with columna:
                tarjeta_resultado(fila["Materia"], fila["Resultado promedio"], fila["Con resultado observado"])
    with st.container(key="general_profundizar"):
        st.subheader("Explorar en detalle")
        explorar = st.expander("Explorar distribución y condiciones", key="general_distribucion", on_change="rerun")
        if explorar.open:
            with explorar:
                materia = st.selectbox("Asignatura para explorar", materias, format_func=nombre_materia,
                                       key="general_distribucion_materia")
                notas = resultados.loc[resultados["Materia"].eq(materia)]
                distribucion_resultados(resumir_distribucion_resultados(notas), materia)
                st.caption(f"{notas['Resultado observado'].notna().sum()} estudiantes con resultado observado.")
                st.markdown(f"**{etiqueta_condicion(materia, 'Condición según notas informadas')}**")
                detalle = resumir_condiciones(notas)
                condiciones_academicas(detalle, materia, len(notas))
                valores = st.expander("Ver valores de la distribución", key="general_distribucion_valores", on_change="rerun")
                if valores.open:
                    with valores:
                        st.dataframe(detalle.round(2), hide_index=True, width="stretch")

    with st.container(key="general_tendencia_bloque"):
        tendencia = st.expander("Tendencia diaria de accesos a secciones", key="general_tendencia", on_change="rerun")
        if tendencia.open:
            with tendencia:
                st.caption("La primera carga lee los reportes de trazabilidad de las asignaturas seleccionadas.")
                try:
                    tendencias = cargar_tendencias()
                except (FileNotFoundError, ValueError) as error:
                    st.error(str(error))
                else:
                    tendencia_accesos(tendencias, materias)
                    st.caption("Eventos con acción Acceder; incluye repeticiones y días sin accesos dentro del período de cada reporte. Los accesos son eventos, no sesiones.")

    tablas = st.expander("Ver tablas de actividad y fuentes", key="general_tablas", on_change="rerun")
    if tablas.open:
        with tablas:
            actividad_tabla, fuentes, resultados_tabla = st.tabs(["Actividad", "Fuentes y períodos", "Resultados"],
                key="general_tablas_pestanas", on_change="rerun")
            datos = vista.assign(Asignatura=vista["Materia"].map(nombre_materia))
            if actividad_tabla.open:
                with actividad_tabla:
                    datos["Cobertura"] = datos["Activos (%)"].map(
                        lambda v: formato_numero(v) + " %" if pd.notna(v) else "Sin datos")
                    st.dataframe(datos[["Asignatura", "Alumnos del aula", "Con dato de actividad", "Activos", "Inactivos", "Cobertura"]],
                                 hide_index=True, width="stretch", column_config={
                        "Alumnos del aula": st.column_config.NumberColumn("Alumnos", format="%d"),
                        "Con dato de actividad": st.column_config.NumberColumn("Con dato", format="%d"),
                    })
            if fuentes.open:
                with fuentes:
                    st.dataframe(datos[["Asignatura", "Usuarios del reporte", "Desde", "Hasta"]], hide_index=True, width="stretch", column_config={
                        "Usuarios del reporte": st.column_config.NumberColumn("Usuarios del reporte", format="%d"),
                        "Desde": st.column_config.DateColumn(format="DD/MM/YYYY"),
                        "Hasta": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    })
            if resultados_tabla.open:
                with resultados_tabla:
                    st.dataframe(datos[["Asignatura", "Resultado promedio", "Con resultado observado"]], hide_index=True,
                        column_config={"Resultado promedio": st.column_config.NumberColumn(format="%.2f")})
                    st.caption("Álgebra: puntos acumulados parciales de un esquema de 120. Otras materias: promedio sobre 100.")

    criterios = st.expander("Criterios y denominadores", key="general_criterios", on_change="rerun")
    if criterios.open:
        with criterios:
            st.write("Los estudiantes únicos se deduplican por identificador entre materias. Los registros alumno-materia cuentan una fila por estudiante en cada aula, con independencia de su situación de matrícula.")
            st.write("Actividad: al menos una interacción durante el período del reporte. Los porcentajes usan alumnos del aula con dato de actividad. Los valores faltantes no se consideran inactivos.")
            st.write("Las condiciones usan estudiantes presentes en los archivos de calificaciones. El promedio usa solo resultados observados. Las notas faltantes no se convierten en cero. Los intervalos de los histogramas incluyen su límite superior; el primero incluye el cero.")
            for materia in materias:
                st.markdown(f"**{materia}**")
                mostrar_criterio_academico(materia)


def datos_graficos_general(resumen, resultados):
    """Adapta los resúmenes validados al formato visual; conserva sus denominadores."""
    actividad, condiciones = [], []
    for fila in resumen.to_dict("records"):
        materia = fila["Materia"]
        for orden, (grupo, cantidad, porcentaje) in enumerate([
            ("Con actividad", fila["Activos"], fila["Activos (%)"]),
            ("Sin actividad", fila["Inactivos"], fila["Inactivos (%)"]),
        ]):
            actividad.append({"Materia": materia, "Asignatura": nombre_materia(materia), "Grupo": grupo,
                              "Estudiantes": cantidad, "Porcentaje": porcentaje,
                              "Porcentaje visible": formato_numero(porcentaje) + " %" if pd.notna(porcentaje) else "Sin datos",
                              "Base": fila["Con dato de actividad"], "Orden": orden,
                              "Texto oscuro": grupo == "Sin actividad",
                              "Criterio": "Una o más interacciones en el período" if grupo == "Con actividad" else "Cero interacciones informadas en el período"})
        notas = resultados.loc[resultados["Materia"].eq(materia)]
        for orden, fila_condicion in enumerate(resumir_condiciones(notas).to_dict("records")):
            grupo, porcentaje = fila_condicion["Condición académica"], fila_condicion["Porcentaje (%)"]
            condiciones.append({"Materia": materia,
                                "Asignatura": nombre_materia(materia) + (" · proyectada" if materia == "Álgebra" else ""),
                                "Grupo": grupo, "Estudiantes": fila_condicion["Alumnos"], "Porcentaje": porcentaje,
                                "Porcentaje visible": formato_numero(porcentaje) + " %" if pd.notna(porcentaje) else "Sin datos",
                                "Base": len(notas), "Orden": orden, "Texto oscuro": grupo == "Regular",
                                "Criterio": etiqueta_condicion(materia, "Condición según notas informadas")})
    return pd.DataFrame(actividad), pd.DataFrame(condiciones)


def mostrar_relacion(datos, materia, cargar_indicadores=None):
    poblacion = st.radio("Población a consultar", list(FILTROS_POBLACION),
                         index=1, horizontal=True, key=f"relacion_poblacion_{materia}")
    seleccion = seleccionar_poblacion(datos, poblacion)
    if seleccion.empty:
        st.info("No hay estudiantes en esta población.")
        return
    if cargar_indicadores is not None:
        trazabilidad = st.expander("Incluir indicadores de trazabilidad",
                                  key=f"relacion_trazabilidad_{materia}", on_change="rerun")
        if trazabilidad.open:
            with trazabilidad:
                try:
                    with st.spinner(f"Cargando indicadores de trazabilidad de {materia}..."):
                        resumen = cargar_indicadores()
                except (FileNotFoundError, ValueError) as error:
                    st.error(str(error))
                    return
                if resumen is None:
                    st.warning("Los períodos de participación y trazabilidad difieren. No se cruzan sus recuentos.")
                else:
                    seleccion = agregar_actividad_trazabilidad(seleccion, resumen)
                    st.caption("Indicadores disponibles en el selector.")
    variables = ["Interacciones", "Tiempo de uso (minutos)"]
    if "Registros de trazabilidad" in seleccion:
        variables += ["Registros de trazabilidad", "Días con eventos"]
    variable = st.selectbox("Indicador de participación o trazabilidad", variables, key=f"relacion_variable_{materia}")
    resultado = "Rendimiento observado (%)" if materia == "Álgebra" else "Resultado observado"
    pares, correlacion, motivo = calcular_correlacion(seleccion, variable, resultado)
    indicadores([
        ("Observaciones emparejadas", len(pares), "Pares con ambos valores informados, uno como máximo por estudiante."),
        ("Correlación de Pearson", formato_numero(correlacion, 3) if correlacion is not None else "No calculable", "De −1 a 1. Describe asociación, no causalidad."),
        ("Sin par completo", len(seleccion) - len(pares)),
    ], "relacion")
    with st.container(key="panel_relacion_dispersion"):
        st.subheader("Actividad y rendimiento observado")
        if not pares.empty:
            dispersion(pares, variable, resultado, materia)
        if motivo:
            st.info(motivo)
        st.caption("Asociación descriptiva; no demuestra causalidad." +
                   (" Álgebra: porcentaje sobre las notas informadas." if materia == "Álgebra" else ""))
    with st.container(key="panel_relacion_grupos"):
        st.subheader("Actividad y condición proyectada" if materia == "Álgebra" else "Actividad y condición académica")
        grupos = seleccion.groupby(["Situación de actividad", "Condición académica"], as_index=False).agg(Estudiantes=("Identificación", "size"))
        cruce_categorias(grupos, "Situación de actividad", "Condición académica", COLORES_CONDICION, len(seleccion))
        st.caption(f"Base: {len(seleccion)} estudiantes de la población seleccionada.")
        detalle = st.expander("Ver valores de los grupos", key="relacion_grupos_valores", on_change="rerun")
        if detalle.open:
            with detalle:
                tabla = grupos.assign(**{"Porcentaje de la población (%)": 100 * grupos["Estudiantes"] / len(seleccion)})
                st.dataframe(tabla.rename(columns={"Condición académica": etiqueta_condicion(materia)}).round(2), hide_index=True)
    metodo = st.expander("Criterios de la comparación", key="relacion_criterios", on_change="rerun")
    if metodo.open:
        with metodo:
            st.write(f"Población: {poblacion}, {len(seleccion)} registros estudiante-materia. Participación del período completo y "
                     "notas disponibles al exportar. La dispersión excluye registros sin ambos valores; tiempo de uso es una estimación en minutos. "
                     "Los grupos usan actividad registrada (>0 interacciones) y condición académica, conservan las categorías sin datos y sus porcentajes usan toda "
                     "la población seleccionada. Son grupos descriptivos, no categorías nuevas de riesgo.")
            mostrar_criterio_academico(materia)
