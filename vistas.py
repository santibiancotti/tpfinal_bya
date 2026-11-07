import streamlit as st

import pandas as pd

from hashlib import sha256

from procesamiento import (FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones, resumir_actividad, 
                           filtrar_trazabilidad, DIAS_SEMANA, resumir_horarios, resumir_accesos_diarios, resumir_participacion, resumir_instrumentos,
                           resumir_resultados_alumnos, resumir_distribucion_resultados)

def mostrar_inicio(paginas):
    st.title("Seguimiento académico")

    st.write(
        "Seleccioná una vista para consultar "
        "la información académica."
    )

    dashboards = [
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

    for inicio in range(0, len(dashboards), 3):
        columnas = st.columns(3)

        for columna, dashboard in zip(
            columnas,
            dashboards[inicio:inicio + 3],
        ):
            clave, titulo, descripcion = dashboard

            with columna:
                with st.container(border=True):
                    st.subheader(titulo)
                    st.write(descripcion)

                    disponible = clave in paginas

                    st.caption(
                        "Vista inicial disponible"
                        if disponible
                        else "En preparación"
                    )

                    if st.button(
                        "Abrir vista",
                        key=f"abrir_{clave}",
                        disabled=not disponible,
                        width="stretch",
                    ):
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

    with st.expander("Ver reporte con todos los perfiles"):
        reporte_visual = participacion.assign(
            Avance = participacion["Avance"].astype("string")
        )

        st.dataframe(
            reporte_visual,
            hide_index=True,
        )

def mostrar_participacion(
    participacion,
    participacion_alumnos,
    trazabilidad_alumnos,
):
    pestana_resumen, pestana_evolucion = st.tabs(
        ["Resumen del reporte completo", "Evolución de accesos"]
    )

    with pestana_resumen:
        mostrar_resumen_participacion(
            participacion,
            participacion_alumnos,
        )

    with pestana_evolucion:
        if trazabilidad_alumnos.empty:
            st.info("El reporte no contiene registros de alumnos.")
            return

        filtros = seleccionar_filtros_actividad(
            trazabilidad_alumnos,
            "participacion",
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
            "Incluye las repeticiones marcadas."
        )

        st.dataframe(datos_grafico, hide_index=True)

def seleccionar_filtros_actividad(eventos, prefijo):
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

    usuarios = (
        eventos[["Usuario", "Apellido", "Nombre"]]
        .drop_duplicates(subset="Usuario")
        .sort_values("Usuario")
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

def mostrar_trazabilidad(trazabilidad, trazabilidad_alumnos,):
    if trazabilidad_alumnos.empty:
        st.info(
            "El reporte no contiene registros de alumnos."
        )
        return

    filtros = seleccionar_filtros_actividad(
        trazabilidad_alumnos,
        "trazabilidad",
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
        len(trazabilidad),
    )

    col2.metric(
        "Registros seleccionados",
        len(trazabilidad_alumnos),
    )

    col3.metric(
        "Alumnos con eventos",
        cantidad_alumnos,
    )

    col4.metric(
        "Repeticiones exactas adicionales",
        cantidad_repeticiones,
    )

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
        + ["Detalle"]
    )

    with pestanas[0]:
        if not trazabilidad_alumnos.empty:
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

    with pestanas[-1]:
        st.dataframe(
            trazabilidad_alumnos,
            hide_index=True,
        )

    with st.expander(
        "Ver reporte original con todos los perfiles"
    ):
        st.dataframe(
            trazabilidad,
            hide_index=True,
        )

def mostrar_rendimiento(calificaciones, materia):
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
            resultados = resumir_resultados_alumnos(
                calificaciones,
                materia,
            )
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

def mostrar_semaforo(condicion):
    colores = {
        "Promociona": "#15803D",
        "Regular": "#EAB308",
        "Libre": "#DC2626",
        "Pendiente": "#6B7280",
        "Sin notas informadas": "#6B7280",
    }

    color = colores[condicion]

    st.html(
        f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span
                aria-hidden="true"
                style="width: 14px; height: 14px; flex-shrink: 0;
                       border-radius: 50%; background-color: {color};"
            ></span>
            <span>
                <strong>Condición según notas informadas</strong>
                · {condicion}
            </span>
        </div>
        """
    )

def mostrar_individual(base_alumnos, calificaciones, materia, cargar_historial):
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
            mostrar_semaforo("Sin notas informadas")
            return

        try:
            resultados = resumir_resultados_alumnos(calificaciones, materia)
        except ValueError as error:
            st.info(str(error))
        else:
            fila = resultados.set_index("Usuario").loc[usuario]
            valor = fila["Resultado observado"]
            maximo = fila.get("Máximo de sus notas", 100)

            mostrar_semaforo(fila["Condición académica"])

            if materia == "Álgebra" and pd.notna(valor):
                porcentaje = fila["Rendimiento observado (%)"]
                porcentaje_visible = f"{porcentaje:.2f}".replace(".", ",")

                st.caption(
                    f"Rendimiento sobre notas informadas {porcentaje_visible} %. "
                    f"Las evaluaciones con nota cubren {maximo:.0f} "
                    "de los 120 puntos del esquema."
                )

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