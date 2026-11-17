import streamlit as st

import pandas as pd

from hashlib import sha256
from estilos import (mostrar_encabezado, nombre_materia, formato_numero,
                     COLORES_CONDICION, NOMBRES_MATERIAS)
from graficos import porcentajes_por_materia, distribucion_resultados, tendencia_accesos

from procesamiento import (FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones, resumir_actividad, 
                           filtrar_trazabilidad, DIAS_SEMANA, resumir_horarios, resumir_accesos_diarios, resumir_participacion, resumir_instrumentos,
                           resumir_resultados_alumnos, resumir_distribucion_resultados,
                           resumir_condiciones, calcular_correlacion, agregar_actividad_trazabilidad)

DASHBOARDS = [
        (
            "general",
            "General",
            "Resumen y comparación de indicadores entre materias.",
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
        if st.button("Inicio", key="abrir_inicio", type="tertiary", icon=":material/home:"):
            st.switch_page(paginas["inicio"])
        for clave, titulo, _ in DASHBOARDS:
            titulo = {"rendimiento": "Rendimiento", "matricula": "Matrícula y alertas"}.get(clave, titulo)
            activo = pagina_actual.url_path == paginas[clave].url_path
            if st.button(titulo, key=f"abrir_{clave}", type="primary" if activo else "tertiary"):
                st.switch_page(paginas[clave])


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

def mostrar_matricula(
    matriculados,
    matricula_actual,
    base_alumnos,
):
    poblacion = st.radio(
        "Población a consultar",
        options=list(FILTROS_POBLACION),
        horizontal=True,
        key="matricula_poblacion",
    )

    alumnos_seleccionados = seleccionar_poblacion(
        base_alumnos,
        poblacion,
    )

    campos_filtro = [
        "Situación de matrícula",
        "Situación de actividad",
        "Alerta",
    ]

    filtros = {}

    for contenedor, columna in zip(
        st.columns(3),
        campos_filtro,
    ):
        opciones = ["Todas"] + sorted(
            alumnos_seleccionados[columna]
            .dropna()
            .unique()
            .tolist()
        )

        with contenedor:
            filtros[columna] = st.selectbox(
                columna,
                options=opciones,
                key=f"matricula_filtro_{columna}",
            )

    alumnos_seleccionados = filtrar_situaciones(
        alumnos_seleccionados,
        filtros,
    )

    cantidad = len(alumnos_seleccionados)

    cantidad_alertas = int(alumnos_seleccionados["Tiene alerta"].sum())

    vigentes = int(
        alumnos_seleccionados["Matrícula vigente"].sum()
    )

    con_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .eq(True)
        .sum()
    )

    sin_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .eq(False)
        .sum()
    )

    sin_dato_actividad = int(
        alumnos_seleccionados["Con actividad"]
        .isna()
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Estudiantes seleccionados",
        cantidad,
    )

    col2.metric(
        "Con matrícula vigente",
        vigentes,
    )

    col3.metric(
        "Con actividad registrada",
        con_actividad,
    )

    col4.metric(
        "Sin actividad registrada",
        sin_actividad,
    )

    st.caption(
        f"Población seleccionada: {poblacion}. "
        "Los indicadores y la tabla corresponden "
        "a esa población. Con actividad significa "
        "al menos una interacción en el período del reporte."
    )

    if cantidad == 0:
        st.info(
            "No hay estudiantes que coincidan "
            "con la combinación de filtros."
        )
    elif cantidad_alertas:
        st.warning(
            f"{cantidad_alertas} estudiantes requieren "
            "revisión según los criterios de alerta "
            "y los filtros seleccionados."
        )

        st.caption(
            "La actividad corresponde al período completo "
            "del reporte y puede ser anterior a una baja."
        )

    if sin_dato_actividad:
        st.info(
            f"Hay {sin_dato_actividad} estudiantes cuya "
            "actividad no se puede determinar. "
            "Consultá su situación en la tabla."
        )

    columnas = [
        "Identificación",
        "Estudiante",
        "Situación de matrícula",
        "Situación de actividad",
        "Alerta",
        "Interacciones",
        "Última interacción",
    ]

    st.dataframe(
        alumnos_seleccionados[columnas],
        hide_index=True,
    )

    with st.expander("Ver historial de matrícula"):
        st.caption(
            f"{len(matriculados)} registros originales; "
            f"{len(matricula_actual)} estudiantes únicos "
            "después de consolidar el historial."
        )

        st.dataframe(
            matriculados,
            hide_index=True,
        )

def mostrar_resumen_participacion(participacion, participacion_alumnos):
    resumen = resumir_participacion(participacion_alumnos)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuarios en el reporte", len(participacion))
    col2.metric("Alumnos", resumen["alumnos"])
    col3.metric("Alumnos con actividad", resumen["con_actividad"])
    col4.metric("Alumnos sin actividad", resumen["sin_actividad"])

    cobertura = resumen["cobertura"]
    tiempo_promedio = resumen["tiempo_promedio"]

    col_cobertura, col_tiempo = st.columns(2)

    col_cobertura.metric(
        "Cobertura de participación",
        f"{cobertura:.1f} %".replace(".", ",")
        if cobertura is not None
        else "Sin datos",
    )

    col_tiempo.metric(
        "Tiempo promedio estimado por alumno",
        f"{tiempo_promedio:.1f} min".replace(".", ",")
        if tiempo_promedio is not None
        else "Sin datos",
    )

    st.caption(
        "Se considera con actividad a quien registró al menos "
        "una interacción durante el período del reporte. "
        f"La cobertura se calcula sobre {resumen['con_dato_actividad']} "
        "alumnos con dato de actividad. "
        f"El promedio utiliza {resumen['con_tiempo']} tiempos "
        "estimados, incluidos los ceros informados."
    )

    st.dataframe(
        participacion_alumnos,
        hide_index=True,
    )

    original = st.expander("Ver reporte con todos los perfiles", key="participacion_original", on_change="rerun")
    if original.open:
        with original:
            reporte_visual = participacion.assign(Avance=participacion["Avance"].astype("string"))
            st.dataframe(reporte_visual, hide_index=True)

def mostrar_participacion(
    participacion,
    participacion_alumnos,
    cargar_evolucion,
):
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
        trazabilidad_alumnos = resumen_eventos["eventos"]
        if trazabilidad_alumnos.empty:
            st.info("El reporte no contiene registros de alumnos.")
            return

        filtros = seleccionar_filtros_actividad(
            trazabilidad_alumnos,
            "participacion",
            resumen_eventos["usuarios"],
        )

        if filtros is None:
            return

        periodo, usuario = filtros

        resumen = resumir_accesos_diarios(
            trazabilidad_alumnos,
            periodo[0],
            periodo[1],
            usuario,
        )

        st.metric(
            "Accesos a secciones en el período",
            int(resumen["Accesos a secciones"].sum()),
        )

        datos_grafico = resumen.copy()
        datos_grafico["Día"] = resumen["Día"].dt.strftime("%Y-%m-%d")

        st.bar_chart(
            datos_grafico,
            x="Día",
            y="Accesos a secciones",
            sort="Día",
            height=280,
        )

        st.caption(
            "La serie usa la acción Acceder del reporte de trazabilidad. "
            "Incluye las repeticiones marcadas. Los accesos son eventos; "
            "las fuentes no identifican sesiones. Este filtro solo afecta la evolución; "
            "el resumen utiliza el período completo del reporte."
        )

        st.dataframe(datos_grafico, hide_index=True)

def seleccionar_filtros_actividad(eventos, prefijo, usuarios=None):
    prefijo = f"{prefijo}_{st.session_state.get('materia_actual', '')}"
    fecha_min = eventos["Fecha"].min().date()
    fecha_max = eventos["Fecha"].max().date()

    periodo = st.date_input(
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

    usuario = st.selectbox(
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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Registros del reporte (total)",
        resumen_eventos["total_reporte"],
    )

    col2.metric(
        "Registros seleccionados",
        int(trazabilidad_alumnos["Registros"].sum()),
    )

    col3.metric(
        "Alumnos con eventos",
        cantidad_alumnos,
    )

    col4.metric(
        "Repeticiones exactas adicionales",
        cantidad_repeticiones,
    )
    dias_periodo = (pd.Timestamp(periodo[1]) - pd.Timestamp(periodo[0])).days + 1
    cantidad_registros = int(trazabilidad_alumnos["Registros"].sum())
    st.metric("Interacciones promedio por día del período", f"{cantidad_registros / dias_periodo:.2f}")

    st.caption(
        "El total del reporte incluye todos los perfiles "
        "y no cambia con los filtros. "
        "Los otros indicadores, resúmenes y detalle "
        "corresponden al período y estudiante seleccionados. "
        "Las repeticiones marcadas permanecen incluidas."
    )

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
            horarios = resumir_horarios(
                trazabilidad_alumnos
            )

            firma_mapa = sha256(
                horarios.to_json(
                    orient="split"
                ).encode("utf-8")
            ).hexdigest()

            st.vega_lite_chart(
                horarios,
                spec={
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
                width="stretch",
                height=260,
            )

            st.caption(
                "Cada celda suma los registros de ese día "
                "de semana y esa hora dentro de la selección. "
                "Por ejemplo, la hora 20 comprende "
                "desde las 20:00 hasta antes de las 21:00. "
                "Las repeticiones marcadas están incluidas."
            )

    for pestana, configuracion_actual in zip(
        pestanas[1:],
        configuracion,
    ):
        titulo, campo = configuracion_actual
        if not pestana.open:
            continue

        with pestana:
            resumen = resumir_actividad(
                trazabilidad_alumnos,
                campo,
            )

            if campo == "Acción" and not resumen.empty:
                st.bar_chart(
                    resumen.head(10),
                    x="Acción",
                    y="Registros",
                    horizontal=True,
                    sort="-Registros",
                    height=350,
                )

                st.caption(
                    "El gráfico muestra hasta diez acciones "
                    "con más registros. "
                    "La tabla conserva todas las acciones."
                )

            st.dataframe(
                resumen,
                hide_index=True,
            )

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

def mostrar_rendimiento(calificaciones, materia, resultados=None):
    pestana_comparacion, pestana_distribucion = st.tabs(
        ["Comparación por instrumento", "Distribución de resultados"]
    )

    with pestana_comparacion:
        resumen = resumir_instrumentos(calificaciones)
        promedios = resumen.dropna(subset=["Promedio (%)"])

        if not promedios.empty:
            st.bar_chart(
                promedios,
                x="Instrumento",
                y="Promedio (%)",
                horizontal=True,
                sort="-Promedio (%)",
                height=320,
            )

        st.caption(
            "Cada promedio usa los porcentajes obtenidos en ese "
            "instrumento. La tabla indica cuántas notas informadas "
            "entran en el cálculo."
        )

        st.dataframe(
            resumen.round({"Promedio (%)": 2}),
            hide_index=True,
        )

    with pestana_distribucion:
        try:
            if resultados is None:
                resultados = resumir_resultados_alumnos(calificaciones, materia)
        except ValueError as error:
            st.info(str(error))
            return

        distribucion = resumir_distribucion_resultados(resultados)

        if distribucion.empty:
            st.info("La materia no tiene resultados observados.")
            return

        st.metric(
            "Alumnos con resultado observado",
            int(distribucion["Alumnos"].sum()),
        )

        st.bar_chart(
            distribucion,
            x="Intervalo",
            y="Alumnos",
            sort=False,
            height=320,
        )

        st.caption(
            "Cada alumno aporta un resultado calculado con sus notas "
            "informadas. En Álgebra se suman puntos. En Algoritmos y "
            "Probabilidad se usa el promedio. Los intervalos incluyen "
            "el límite superior y el primero también incluye el cero."
        )

        st.dataframe(distribucion, hide_index=True)

        etiqueta = etiqueta_condicion(materia, "Condición según notas informadas")
        st.subheader(etiqueta)
        condiciones = resumir_condiciones(resultados)
        condiciones = condiciones.rename(columns={"Condición académica": etiqueta_condicion(materia)})
        if materia == "Álgebra":
            condiciones = condiciones.rename(columns={"Porcentaje (%)": "Porcentaje por condición proyectada (%)"})
        st.bar_chart(condiciones, x=etiqueta_condicion(materia), y="Alumnos", sort=False)
        st.dataframe(condiciones.round(2), hide_index=True)
        st.caption(
            f"Denominador: {len(resultados)} estudiantes presentes en calificaciones. "
            "No incluye alumnos del aula sin filas en esos archivos. "
            "Las notas faltantes no se convierten en cero."
        )
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

    nombres_notas = (
        calificaciones
        .drop_duplicates(subset="Usuario")
        .set_index("Usuario")
    )
    nombres_notas = (
        nombres_notas["Apellido"] + ", " + nombres_notas["Nombre"]
    )

    nombres = (
        alumnos_por_id["Estudiante"]
        .combine_first(nombres_notas)
        .fillna("Nombre no informado")
        .sort_index()
    )

    usuario = st.selectbox(
        "Estudiante",
        options=nombres.index.tolist(),
        index=None,
        placeholder="Seleccioná un estudiante",
        format_func=lambda valor: f"{valor} - {nombres.loc[valor]}",
        key=f"individual_estudiante_{materia}",
    )

    if usuario is None:
        return

    st.subheader(nombres.loc[usuario])

    pestana_resumen, pestana_notas, pestana_actividad = st.tabs(
        ["Matrícula y participación", "Notas", "Historial de actividad"],
        key=f"individual_pestanas_{materia}",
        on_change="rerun",
    )

    with pestana_resumen:
        if usuario in alumnos_por_id.index:
            alumno = alumnos_por_id.loc[usuario]

            st.write(f"**Matrícula** · {alumno['Situación de matrícula']}")
            st.write(f"**Actividad** · {alumno['Situación de actividad']}")

            interacciones = alumno["Interacciones"]
            tiempo = alumno["Tiempo de uso (minutos)"]

            col1, col2 = st.columns(2)
            col1.metric(
                "Interacciones",
                int(interacciones) if pd.notna(interacciones) else None,
            )
            col2.metric(
                "Tiempo estimado",
                f"{tiempo:.0f} min" if pd.notna(tiempo) else None,
            )
        else:
            st.info("Este estudiante figura en los archivos de calificaciones.")

    if pestana_actividad.open:
        with pestana_actividad:
            try:
                with st.spinner("Cargando historial de actividad..."):
                    eventos = cargar_historial(usuario)
            except (FileNotFoundError, ValueError) as error:
                st.error(str(error))
                return

            if eventos.empty:
                st.info("Sin registros de trazabilidad para este estudiante.")
            else:
                col1, col2 = st.columns(2)

                col1.metric("Registros de trazabilidad", len(eventos))
                col2.metric(
                    "Accesos a secciones",
                    int(eventos["Acción"].eq("Acceder").sum()),
                )

                st.caption(
                    "Los recuentos corresponden al reporte de trazabilidad "
                    "e incluyen las repeticiones marcadas."
                )

                columnas_eventos = [
                    "Fecha",
                    "Sección",
                    "Acción",
                    "Descripción",
                    "Repetición exacta adicional",
                ]

                st.dataframe(
                    eventos[columnas_eventos].sort_values(
                        "Fecha",
                        ascending=False,
                    ),
                    hide_index=True,
                )

    if not pestana_notas.open:
        return

    with pestana_notas:
        notas = calificaciones.loc[
            calificaciones["Usuario"].eq(usuario)
        ]

        if notas.empty:
            mostrar_semaforo("Sin notas informadas", materia)
            return

        try:
            if resultados is None:
                resultados = resumir_resultados_alumnos(calificaciones, materia)
        except ValueError as error:
            st.info(str(error))
        else:
            fila = resultados.set_index("Usuario").loc[usuario]
            valor = fila["Resultado observado"]
            maximo = fila.get("Máximo de sus notas", 100)

            mostrar_semaforo(fila["Condición académica"], materia)

            if materia == "Álgebra" and pd.notna(valor):
                porcentaje = fila["Rendimiento observado (%)"]
                porcentaje_visible = f"{porcentaje:.2f}".replace(".", ",")

                st.caption(
                    f"Rendimiento sobre notas informadas {porcentaje_visible} %. "
                    f"Las evaluaciones con nota cubren {maximo:.0f} "
                    "de los 120 puntos del esquema."
                )
                mostrar_criterio_academico(materia)

            elif materia == "Probabilidad y Estadística":
                st.caption(
                    "El promedio incluye el recuperatorio cuando "
                    "hay una nota informada."
                )

            col1, col2 = st.columns(2)
            col1.metric(
                "Resultado observado",
                f"{valor:.2f} / {maximo:.0f}".replace(".", ",")
                if pd.notna(valor)
                else None,
            )
            col2.metric(
                "Instrumentos con nota",
                f"{fila['Instrumentos con nota']} "
                f"de {fila['Instrumentos disponibles']}",
            )

        columnas = [
            "Instrumento",
            "Nota",
            "Puntos obtenidos",
            "Puntos máximos",
            "Porcentaje obtenido",
            "Observaciones",
        ]

        st.dataframe(
            notas[columnas].round({"Porcentaje obtenido": 2}),
            hide_index=True,
        )


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
        col1, col2, col3 = st.columns(3)
        col1.metric("Asignaturas", len(resumen), help="Asignaturas incluidas en la selección actual.")
        col2.metric("Estudiantes únicos en las aulas", alumnos["Usuario"].nunique(),
                    help="Identificadores distintos entre las aulas seleccionadas; una persona se cuenta una sola vez.")
        col3.metric("Registros alumno-materia en las aulas", len(alumnos),
                    help="Cada estudiante se cuenta una vez por asignatura. Una persona puede participar en más de una.")

    actividad, condiciones = datos_graficos_general(resumen, resultados)
    with st.container(key="general_comparaciones"):
        izquierda, derecha = st.columns(2, gap="medium")
        with izquierda, st.container(key="panel_general_actividad"):
            st.subheader("Actividad del aula")
            st.caption("Participación registrada durante el período del reporte.")
            porcentajes_por_materia(actividad, {"Con actividad": "#285B8F", "Sin actividad": "#DCE5EF"}, orden)
        with derecha, st.container(key="panel_general_condiciones"):
            st.subheader("Condición según notas informadas")
            st.caption("Álgebra: Condición proyectada según notas informadas."
                       if "Álgebra" in materias else "Distribución sobre estudiantes presentes en calificaciones.")
            orden_condiciones = [m + " · proyectada" if m == "Álgebra" else m for m in orden]
            porcentajes_por_materia(condiciones, COLORES_CONDICION, orden_condiciones)

    with st.container(key="panel_general_rendimiento"):
        st.subheader("Rendimiento observado")
        st.caption("Álgebra: puntos acumulados parciales de un esquema de 120 puntos. Las otras materias usan promedios sobre 100.")
        vista = resumen.set_index("Materia").reindex(materias).reset_index()
        tabla = pd.DataFrame({
            "Asignatura": vista["Materia"].map(nombre_materia),
            "Resultado medio": [
                (formato_numero(valor, 2) + (" pts" if materia == "Álgebra" else " / 100"))
                if pd.notna(valor) else "Sin datos"
                for materia, valor in zip(vista["Materia"], vista["Resultado promedio"])
            ],
            "Escala": ["Acumulado parcial" if m == "Álgebra" else "Promedio / 100" for m in vista["Materia"]],
            "Con resultado": vista["Con resultado observado"],
        })
        st.dataframe(tabla, hide_index=True, row_height=38, width="stretch", column_config={
            "Asignatura": st.column_config.TextColumn(width=190),
            "Resultado medio": st.column_config.TextColumn(width=150, help="Media de los resultados observados, sin imputar notas faltantes."),
            "Escala": st.column_config.TextColumn(width=170, help="Álgebra conserva el esquema acumulativo de 120 puntos; el máximo informado varía según las evaluaciones con nota."),
            "Con resultado": st.column_config.NumberColumn(width=125, format="%d"),
        })
        explorar = st.expander("Explorar distribución y condiciones", key="general_distribucion", on_change="rerun")
        if explorar.open:
            with explorar:
                materia = st.selectbox("Asignatura para explorar", materias, format_func=nombre_materia,
                                       key="general_distribucion_materia")
                notas = resultados.loc[resultados["Materia"].eq(materia)]
                distribucion_resultados(resumir_distribucion_resultados(notas), materia)
                st.caption("Intervalos cerrados a la derecha; el primero incluye cero. "
                           f"{notas['Resultado observado'].notna().sum()} estudiantes con resultado observado.")
                st.markdown(f"**{etiqueta_condicion(materia, 'Condición según notas informadas')}**")
                detalle = resumir_condiciones(notas)
                detalle["Porcentaje"] = detalle["Porcentaje (%)"].map(
                    lambda valor: formato_numero(valor) + " %" if pd.notna(valor) else "Sin datos"
                )
                st.dataframe(detalle[["Condición académica", "Alumnos", "Porcentaje"]].rename(
                    columns={"Condición académica": "Condición", "Alumnos": "Estudiantes"}),
                    hide_index=True, width="stretch", column_config={"Condición": st.column_config.TextColumn(width=220)})
                st.caption(f"Denominador de los porcentajes: {len(notas)} estudiantes presentes en calificaciones.")

    with st.container(key="panel_general_tendencia"):
        st.subheader("Tendencias de participación")
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
            actividad_tabla, fuentes = st.tabs(["Actividad", "Fuentes y períodos"])
            datos = vista.assign(Asignatura=vista["Materia"].map(nombre_materia))
            with actividad_tabla:
                datos["Cobertura"] = datos["Activos (%)"].map(
                    lambda v: formato_numero(v) + " %" if pd.notna(v) else "Sin datos")
                st.dataframe(datos[["Asignatura", "Alumnos del aula", "Con dato de actividad", "Activos", "Inactivos", "Cobertura"]],
                             hide_index=True, width="stretch", column_config={
                    "Alumnos del aula": st.column_config.NumberColumn("Alumnos", format="%d"),
                    "Con dato de actividad": st.column_config.NumberColumn("Con dato", format="%d"),
                })
            with fuentes:
                st.dataframe(datos[["Asignatura", "Usuarios del reporte", "Desde", "Hasta"]], hide_index=True, width="stretch", column_config={
                    "Usuarios del reporte": st.column_config.NumberColumn("Usuarios del reporte", format="%d"),
                    "Desde": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    "Hasta": st.column_config.DateColumn(format="DD/MM/YYYY"),
                })

    criterios = st.expander("Criterios y denominadores", key="general_criterios", on_change="rerun")
    if criterios.open:
        with criterios:
            st.write("Los estudiantes únicos se deduplican por identificador entre materias. Los registros alumno-materia cuentan una fila por estudiante en cada aula, con independencia de su situación de matrícula.")
            st.write("Actividad: al menos una interacción durante el período del reporte. Los porcentajes usan alumnos del aula con dato de actividad. Los valores faltantes no se consideran inactivos.")
            st.write("Las condiciones usan estudiantes presentes en los archivos de calificaciones. El promedio usa solo resultados observados. Las notas faltantes no se convierten en cero.")
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
    st.caption(
        f"Población: {poblacion}, {len(seleccion)} registros estudiante-materia. "
        "Participación del período completo del reporte y notas disponibles al exportar. "
        "Cada estudiante aporta como máximo una observación a cada cruce."
    )
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
                    st.caption("Indicadores de trazabilidad incorporados a la selección del gráfico.")
    variables = ["Interacciones", "Tiempo de uso (minutos)"]
    if "Registros de trazabilidad" in seleccion:
        variables += ["Registros de trazabilidad", "Días con eventos"]
    variable = st.selectbox("Indicador de participación o trazabilidad", variables,
                            key=f"relacion_variable_{materia}")
    resultado = "Rendimiento observado (%)" if materia == "Álgebra" else "Resultado observado"
    pares, correlacion, motivo = calcular_correlacion(seleccion, variable, resultado)
    col1, col2 = st.columns(2)
    col1.metric("Observaciones emparejadas", len(pares))
    col2.metric("Correlación de Pearson", f"{correlacion:.3f}" if correlacion is not None else "No calculable")
    if not pares.empty:
        st.scatter_chart(pares, x=variable, y=resultado, height=350)
    if motivo:
        st.info(motivo)
    st.caption(
        f"Se excluyen {len(seleccion) - len(pares)} registros sin ambos valores. "
        "Tiempo de uso es una estimación en minutos. La correlación describe una asociación "
        "y no demuestra causalidad. No se estima una calificación final."
    )
    if materia == "Álgebra":
        st.caption("La dispersión usa el porcentaje sobre las notas informadas de cada estudiante, "
                   "para distinguirlo de la suma de puntos con máximos parciales diferentes.")
    mostrar_criterio_academico(materia)
    st.subheader("Patrones de actividad y condición proyectada" if materia == "Álgebra"
                 else "Patrones de actividad y condición académica")
    grupos = seleccion.groupby(
        ["Situación de actividad", "Condición académica"], as_index=False
    ).agg(Estudiantes=("Identificación", "size"))
    grupos["Porcentaje de la población (%)"] = 100 * grupos["Estudiantes"] / len(seleccion)
    grupos = grupos.rename(columns={"Condición académica": etiqueta_condicion(materia)})
    st.bar_chart(grupos, x=etiqueta_condicion(materia), y="Estudiantes", color="Situación de actividad", stack=False)
    st.dataframe(grupos.round(2), hide_index=True)
    st.caption(
        "Grupos descriptivos definidos por la actividad registrada (>0 interacciones) "
        f"y la condición {'proyectada' if materia == 'Álgebra' else 'calculada'} con las reglas académicas. Se conservan las categorías "
        "sin datos. Los porcentajes usan toda la población seleccionada. "
        "No se asigna una categoría nueva de riesgo. El detalle personal se consulta en Individual."
    )
