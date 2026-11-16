import streamlit as st

import pandas as pd

from hashlib import sha256

from procesamiento import (FILTROS_POBLACION, seleccionar_poblacion, filtrar_situaciones, resumir_actividad, 
                           filtrar_trazabilidad, DIAS_SEMANA, resumir_horarios, resumir_accesos_diarios, resumir_participacion, resumir_instrumentos,
                           resumir_resultados_alumnos, resumir_distribucion_resultados,
                           resumir_condiciones, calcular_correlacion)

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
            "Incluye las repeticiones marcadas. Los accesos son eventos; "
            "las fuentes no identifican sesiones. Este filtro solo afecta la evolución; "
            "el resumen utiliza el período completo del reporte."
        )

        st.dataframe(datos_grafico, hide_index=True)

def seleccionar_filtros_actividad(eventos, prefijo):
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
    dias_periodo = (pd.Timestamp(periodo[1]) - pd.Timestamp(periodo[0])).days + 1
    st.metric("Interacciones promedio por día del período", f"{len(trazabilidad_alumnos) / dias_periodo:.2f}")

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
                <strong>{etiqueta_condicion(materia, "Condición según notas informadas")}</strong>
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
            mostrar_semaforo("Sin notas informadas", materia)
            return

        try:
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


def mostrar_general(resumen, alumnos, resultados, tendencias):
    col1, col2, col3 = st.columns(3)
    col1.metric("Asignaturas", len(resumen))
    col2.metric("Estudiantes únicos en las aulas", alumnos["Usuario"].nunique())
    col3.metric("Registros alumno-materia en las aulas", len(alumnos))
    st.caption(
        "Los estudiantes únicos se deduplican por identificador entre materias. "
        "Los indicadores por materia y sus sumas cuentan registros alumno-materia."
    )
    st.dataframe(resumen.round(2), hide_index=True)
    actividad = resumen.melt(
        id_vars="Materia", value_vars=["Activos (%)", "Inactivos (%)"],
        var_name="Actividad", value_name="Porcentaje (%)",
    )
    st.bar_chart(actividad, x="Materia", y="Porcentaje (%)", color="Actividad", stack=False)
    st.caption(
        "Activo: al menos una interacción durante el período completo indicado por materia. "
        "Denominador de ambos porcentajes: alumnos del aula con dato de actividad. "
        "Los valores faltantes no se consideran inactivos."
    )
    st.subheader("Resultados por asignatura")
    for materia in resumen["Materia"]:
        notas = resultados.loc[resultados["Materia"].eq(materia)]
        with st.expander(materia, expanded=True):
            distribucion = resumir_distribucion_resultados(notas)
            if distribucion.empty:
                st.info("Sin resultados observados.")
            else:
                st.bar_chart(distribucion, x="Intervalo", y="Alumnos", sort=False, height=200)
            condiciones = resumir_condiciones(notas).rename(
                columns={"Condición académica": etiqueta_condicion(materia)}
            )
            if materia == "Álgebra":
                condiciones = condiciones.rename(columns={"Porcentaje (%)": "Porcentaje por condición proyectada (%)"})
            st.dataframe(condiciones.round(2), hide_index=True)
            st.caption(
                f"Denominador de las condiciones: {len(notas)} estudiantes en calificaciones. "
                "Histograma del resultado observado: suma en Álgebra, promedio en las otras materias. "
                "Intervalos cerrados a derecha; el primero incluye cero."
            )
            mostrar_criterio_academico(materia)
    st.caption(
        "Las sumas parciales de Álgebra tienen distinto máximo según las notas informadas. "
        "No se calcula un promedio global de resultados con escalas diferentes. "
        "El promedio por materia usa solo estudiantes con resultado observado."
    )
    st.subheader("Tendencia diaria de accesos a secciones")
    st.line_chart(tendencias, x="Día", y="Accesos a secciones", color="Materia")
    st.caption(
        "Acción Acceder de trazabilidad; incluye repeticiones y días sin accesos dentro "
        "del período de cada reporte. Los accesos son eventos; las fuentes no identifican sesiones."
    )


def mostrar_relacion(datos, materia):
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
