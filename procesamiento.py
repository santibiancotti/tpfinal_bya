import pandas as pd

from math import ceil


def consolidar_matricula(matriculados):
    datos = matriculados.copy()

    datos["Identificación"] = (
        datos["Identificación"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    datos["_fecha_orden"] = pd.to_datetime(
        datos["Fecha inscripción"],
        dayfirst=True,
        errors="raise",
    )

    datos["_transaccion_orden"] = pd.to_numeric(
        datos["Nro de Transacción"],
        errors="raise",
    )

    datos = datos.sort_values(
        [
            "Identificación",
            "_fecha_orden",
            "_transaccion_orden",
        ]
    )

    actuales = datos.drop_duplicates(
        subset=["Identificación"],
        keep="last",
    )

    actuales = actuales.drop(
        columns=["_fecha_orden", "_transaccion_orden"]
    )

    return actuales.reset_index(drop=True)

def obtener_alumnos(reporte):
    perfil = (
        reporte["Perfil"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    alumnos = reporte.loc[
        perfil.eq("alumnos")
    ].copy()

    alumnos["Usuario"] = (
        alumnos["Usuario"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    return alumnos

def preparar_participacion(participacion):

    alumnos = obtener_alumnos(participacion)

    if alumnos["Usuario"].duplicated().any():
        raise ValueError(
            "Hay alumnos repetidos en el reporte de participación. "
            "Debemos revisar esos registros antes de continuar."
        )

    alumnos["Interacciones"] = pd.to_numeric(
        alumnos["Interacciones"],
        errors="raise",
    ).astype("Int64")

    alumnos["Avance"] = pd.to_numeric(
        alumnos["Avance"],
        errors="raise",
    )

    columnas_fecha = [
        "Fecha alta",
        "Primera interacción",
        "Última interacción",
    ]

    for columna in columnas_fecha:
        alumnos[columna] = pd.to_datetime(
            alumnos[columna],
            dayfirst=True,
            errors="raise",
        )

    tiempo = pd.to_timedelta(
        alumnos["Tiempo estimado de uso"].astype("string") + ":00",
        errors="raise",
    )

    alumnos["Tiempo de uso (minutos)"] = (
        tiempo.dt.total_seconds() / 60
    )

    alumnos["Con actividad"] = (
        alumnos["Interacciones"] > 0
    )

    return alumnos.reset_index(drop=True)

def cruzar_matricula_participacion(
    matricula_actual,
    participacion_alumnos,
):
    matricula = matricula_actual.copy()

    participacion = participacion_alumnos.rename(
        columns={"Usuario": "Identificación"}
    ).copy()

    matricula["En matrícula"] = True
    participacion["En aula"] = True

    alumnos = matricula.merge(
        participacion,
        on="Identificación",
        how="outer",
        validate="one_to_one",
    )

    alumnos["Estudiante"] = (
        alumnos["Alumno"]
        .astype("string")
        .combine_first(
            alumnos["Apellido"].astype("string")
            + ", "
            + alumnos["Nombre"].astype("string")
        )
    )

    for columna in ["En matrícula", "En aula"]:
        alumnos[columna] = (
            alumnos[columna]
            .astype("boolean")
            .fillna(False)
        )

    estado = (
        alumnos["Estado Insc."]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    alumnos["Matrícula vigente"] = (
        estado.eq("aceptada").fillna(False)
    )

    alumnos["Situación de matrícula"] = (
        alumnos["Estado Insc."]
        .astype("string")
        .str.strip()
        .fillna("Estado sin informar")
    )

    alumnos.loc[
        ~alumnos["En matrícula"],
        "Situación de matrícula",
    ] = "Sin registro en matrícula"

    alumnos.loc[
        estado.eq("baja").fillna(False),
        "Situación de matrícula",
    ] = "Baja"

    alumnos.loc[
        alumnos["Matrícula vigente"],
        "Situación de matrícula",
    ] = "Vigente"

    alumnos["Con actividad"] = (
        alumnos["Con actividad"].astype("boolean")
    )

    actividad = alumnos["Con actividad"]

    alumnos["Situación de actividad"] = (
        "Sin registro en participación"
    )

    alumnos.loc[
        alumnos["En aula"],
        "Situación de actividad",
    ] = "Actividad sin determinar"

    alumnos.loc[
        alumnos["En aula"]
        & actividad.eq(False).fillna(False),
        "Situación de actividad",
    ] = "Sin actividad registrada"

    alumnos.loc[
        alumnos["En aula"]
        & actividad.eq(True).fillna(False),
        "Situación de actividad",
    ] = "Con actividad registrada"

    return alumnos.sort_values(
        "Identificación"
    ).reset_index(drop=True)

FILTROS_POBLACION = {
    "Matrícula vigente": "Matrícula vigente",
    "Alumnos del aula": "En aula",
    "Base completa": None,
}


def seleccionar_poblacion(base_alumnos, poblacion):
    columna = FILTROS_POBLACION[poblacion]

    if columna is None:
        return base_alumnos.copy()

    return base_alumnos.loc[
        base_alumnos[columna]
    ].copy()

def clasificar_alertas(base_alumnos):
    alumnos = base_alumnos.copy()

    vigente = alumnos["Matrícula vigente"]
    en_matricula = alumnos["En matrícula"]
    en_aula = alumnos["En aula"]

    actividad = alumnos["Con actividad"]

    con_actividad = actividad.eq(True).fillna(False)
    sin_actividad = actividad.eq(False).fillna(False)

    baja = (
        alumnos["Situación de matrícula"]
        .eq("Baja")
        .fillna(False)
    )

    reglas = {
        "Vigente sin actividad registrada": (
            vigente & sin_actividad
        ),
        "Vigente sin registro en participación": (
            vigente & ~en_aula
        ),
        "Vigente con actividad sin determinar": (
            vigente & en_aula & actividad.isna()
        ),
        "Actividad sin registro en matrícula": (
            con_actividad & ~en_matricula
        ),
        "Actividad con baja registrada": (
            con_actividad & en_matricula & baja
        ),
        "Actividad con otro estado de matrícula": (
            con_actividad
            & en_matricula
            & ~vigente
            & ~baja
        ),
    }

    alumnos["Alerta"] = "Sin alerta con estos criterios"

    for etiqueta, condicion in reglas.items():
        alumnos.loc[condicion, "Alerta"] = etiqueta

    alumnos["Tiene alerta"] = (
        alumnos["Alerta"]
        .ne("Sin alerta con estos criterios")
    )

    return alumnos


def filtrar_situaciones(alumnos, filtros):
    datos = alumnos.copy()

    for columna, valor in filtros.items():
        if valor != "Todas":
            datos = datos.loc[
                datos[columna].eq(valor)
            ]

    return datos.copy()

def preparar_trazabilidad(trazabilidad, usuario=None):
    alumnos = obtener_alumnos(trazabilidad)

    if usuario is not None:
        alumnos = alumnos.loc[
            alumnos["Usuario"].eq(usuario)
        ].copy()
        
    alumnos["Repetición exacta adicional"] = (
        alumnos.duplicated(keep="first")
    )

    alumnos["Fecha"] = pd.to_datetime(
        alumnos["Fecha"],
        errors="raise",
    )

    alumnos["Acción"] = (
        alumnos["Acción"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Acción no informada")
    )

    alumnos["Día"] = (
        alumnos["Fecha"].dt.normalize()
    )

    alumnos["Semana"] = (
        alumnos["Fecha"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    alumnos["Hora"] = (
        alumnos["Fecha"]
        .dt.hour
        .astype("Int64")
    )

    alumnos["Día de semana"] = (
        alumnos["Fecha"]
        .dt.day_of_week
        .astype("Int64")
    )

    return alumnos.sort_values(
        "Fecha",
        kind="stable",
    ).reset_index(drop=True)

def resumir_actividad(eventos, campo):
    resumen = eventos.groupby(
        campo,
        as_index=False,
        dropna=False,
    ).agg(
        **{
            "Registros": (
                "Usuario",
                "size",
            ),
            "Alumnos con eventos": (
                "Usuario",
                "nunique",
            ),
            "Repeticiones adicionales": (
                "Repetición exacta adicional",
                "sum",
            ),
        }
    )

    if campo == "Acción":
        resumen = resumen.sort_values(
            "Registros",
            ascending=False,
            kind="stable",
        )

    return resumen.reset_index(drop=True)

def filtrar_trazabilidad(
    eventos,
    fecha_desde,
    fecha_hasta,
    usuario=None,
):
    inicio = pd.Timestamp(fecha_desde).normalize()
    hasta = pd.Timestamp(fecha_hasta).normalize()

    if inicio > hasta:
        raise ValueError(
            "La fecha inicial no puede ser "
            "posterior a la final."
        )

    fin_exclusivo = hasta + pd.Timedelta(days=1)

    condicion = (
        eventos["Fecha"].ge(inicio)
        & eventos["Fecha"].lt(fin_exclusivo)
    )

    if usuario is not None:
        condicion = (
            condicion
            & eventos["Usuario"].eq(usuario)
        )

    return eventos.loc[condicion].copy()


DIAS_SEMANA = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]


def resumir_horarios(eventos):
    resumen = resumir_actividad(
        eventos,
        ["Día de semana", "Hora"],
    )

    combinaciones = pd.MultiIndex.from_product(
        [range(7), range(24)],
        names=["Día de semana", "Hora"],
    )

    resumen = (
        resumen
        .set_index(["Día de semana", "Hora"])
        .reindex(combinaciones, fill_value=0)
        .reset_index()
    )

    resumen["Nombre del día"] = (
        resumen["Día de semana"].map(
            dict(enumerate(DIAS_SEMANA))
        )
    )

    return resumen

def resumir_accesos_diarios(
    eventos,
    fecha_desde,
    fecha_hasta,
    usuario=None,
):
    seleccion = filtrar_trazabilidad(
        eventos,
        fecha_desde,
        fecha_hasta,
        usuario,
    )

    accesos = seleccion.loc[
        seleccion["Acción"].eq("Acceder")
    ]

    resumen = resumir_actividad(accesos, "Día")

    dias = pd.date_range(
        fecha_desde,
        fecha_hasta,
        freq="D",
        normalize=True,
        name="Día",
    )

    return (
        resumen
        .set_index("Día")
        .reindex(dias, fill_value=0)
        .reset_index()
        .rename(columns={"Registros": "Accesos a secciones"})
    )

def resumir_participacion(alumnos):
    actividad = alumnos["Con actividad"]
    con_dato_actividad = int(actividad.notna().sum())
    con_actividad = int(actividad.sum())
    tiempos = alumnos["Tiempo de uso (minutos)"].dropna()

    return {
        "alumnos": len(alumnos),
        "con_actividad": con_actividad,
        "sin_actividad": con_dato_actividad - con_actividad,
        "con_dato_actividad": con_dato_actividad,
        "cobertura": (
            100 * con_actividad / con_dato_actividad
            if con_dato_actividad
            else None
        ),
        "con_tiempo": len(tiempos),
        "tiempo_promedio": (
            float(tiempos.mean()) if not tiempos.empty else None
        ),
    }

def preparar_calificaciones(calificaciones):
    datos = calificaciones.copy()

    datos["Usuario"] = (
        datos["Usuario"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    if datos.duplicated(subset=["Usuario", "Instrumento"]).any():
        raise ValueError(
            "Hay usuarios con más de una fila para el mismo instrumento."
        )

    notas = (
        datos["Nota"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    partes = notas.str.extract(
        r"^(?P<puntos>[0-9]+(?:[.,][0-9]+)?)"
        r"\s*/\s*(?P<maximo>[0-9]+(?:[.,][0-9]+)?)$"
    )

    invalidas = notas.notna() & partes["puntos"].isna()

    if invalidas.any():
        nota = datos.loc[invalidas, "Nota"].iloc[0]
        raise ValueError(f"Formato de nota inesperado: {nota}.")

    puntos = pd.to_numeric(
        partes["puntos"].str.replace(",", ".", regex=False)
    ).astype("Float64")

    maximos = pd.to_numeric(
        partes["maximo"].str.replace(",", ".", regex=False)
    ).astype("Float64")

    if (maximos.le(0) | puntos.gt(maximos)).any():
        raise ValueError(
            "Hay una nota con máximo no positivo "
            "o puntos por encima del máximo."
        )

    datos["Puntos obtenidos"] = puntos
    datos["Puntos máximos"] = maximos
    datos["Porcentaje obtenido"] = 100 * puntos / maximos

    return datos


def resumir_instrumentos(calificaciones):
    resumen = calificaciones.groupby(
        "Instrumento",
        as_index=False,
    ).agg(
        **{
            "Notas informadas": ("Porcentaje obtenido", "count"),
            "Promedio (%)": ("Porcentaje obtenido", "mean"),
        }
    )

    return resumen.sort_values(
        "Promedio (%)",
        ascending=False,
        ignore_index=True,
    )

def resumir_resultados_alumnos(calificaciones, materia):
    por_alumno = calificaciones.groupby("Usuario")

    resultado = por_alumno.agg(
        **{
            "Apellido": ("Apellido", "first"),
            "Nombre": ("Nombre", "first"),
            "Instrumentos con nota": ("Puntos obtenidos", "count"),
        }
    )

    if materia == "Álgebra":
        maximos = calificaciones.groupby("Instrumento")["Puntos máximos"]
        if maximos.nunique().gt(1).any():
            raise ValueError("Hay instrumentos de Álgebra con más de un máximo informado.")
        cantidades = maximos.first().dropna().value_counts()
        permitidas = {10: 5, 25: 2, 20: 1}
        if any(maximo not in permitidas or cantidad > permitidas[maximo]
               for maximo, cantidad in cantidades.items()):
            raise ValueError("Los máximos de Álgebra no coinciden con el esquema de 120 puntos.")
        resultado["Resultado observado"] = (
            por_alumno["Puntos obtenidos"].sum(min_count=1)
        )
        resultado["Máximo de sus notas"] = (
            por_alumno["Puntos máximos"].sum(min_count=1)
        )

    elif materia in (
        "Algoritmos y Estructuras de Datos",
        "Probabilidad y Estadística",
    ):
        maximos = calificaciones["Puntos máximos"].dropna()

        if not maximos.eq(100).all():
            raise ValueError(
                f"El promedio de {materia} requiere notas sobre 100 puntos."
            )

        resultado["Resultado observado"] = (
            por_alumno["Puntos obtenidos"].mean()
        )

    else:
        raise ValueError(
            f"Falta definir el cálculo del resultado para {materia}."
        )

    resultado["Instrumentos disponibles"] = (
        calificaciones["Instrumento"].nunique()
    )

    puntos = resultado["Resultado observado"]
    con_resultado = puntos.notna()
    clasificar = con_resultado.copy()
    umbral_promocion = 85

    if materia == "Álgebra":
        maximo = resultado["Máximo de sus notas"]
        resultado["Rendimiento observado (%)"] = 100 * puntos / maximo
        resultado["Resultado equivalente sobre 120"] = 120 * puntos / maximo
        # Con notas parciales se conservan las proporciones de 60/120 y 85/120.
        puntos = resultado["Resultado equivalente sobre 120"]
        clasificar &= maximo.gt(0).fillna(False)

    elif materia == "Algoritmos y Estructuras de Datos":
        umbral_promocion = 90

    resultado["Condición académica"] = "Sin notas informadas"
    resultado.loc[con_resultado, "Condición académica"] = "Pendiente"
    resultado.loc[clasificar, "Condición académica"] = "Libre"

    resultado.loc[
        clasificar & puntos.ge(60),
        "Condición académica",
    ] = "Regular"

    resultado.loc[
        clasificar & puntos.ge(umbral_promocion),
        "Condición académica",
    ] = "Promociona"

    return resultado.reset_index()

def resumir_distribucion_resultados(resultados):
    valores = resultados["Resultado observado"].dropna()

    if valores.empty:
        return pd.DataFrame(columns=["Intervalo", "Alumnos"])

    limite_superior = max(10, 10 * ceil(valores.max() / 10))
    limites = list(range(0, limite_superior + 1, 10))

    etiquetas = [
        f"{inicio} a {fin}"
        for inicio, fin in zip(limites, limites[1:])
    ]

    intervalos = pd.cut(
        valores,
        bins=limites,
        labels=etiquetas,
        include_lowest=True,
    )

    return (
        intervalos.value_counts(sort=False)
        .rename_axis("Intervalo")
        .reset_index(name="Alumnos")
    )


CONDICIONES_ACADEMICAS = [
    "Libre", "Regular", "Promociona", "Pendiente", "Sin notas informadas"
]


def resumir_condiciones(resultados):
    resumen = (
        resultados["Condición académica"].value_counts()
        .reindex(CONDICIONES_ACADEMICAS, fill_value=0)
        .rename_axis("Condición académica").reset_index(name="Alumnos")
    )
    resumen["Porcentaje (%)"] = (
        100 * resumen["Alumnos"] / len(resultados) if len(resultados) else float("nan")
    )
    return resumen


def cruzar_resultados_participacion(base_alumnos, resultados, materia, eventos=None):
    # El cruce se hace dentro de una materia y con una fila por estudiante.
    datos = base_alumnos.merge(
        resultados.drop(columns=["Apellido", "Nombre"]),
        left_on="Identificación", right_on="Usuario",
        how="outer", validate="one_to_one",
    )
    datos["Identificación"] = datos["Identificación"].combine_first(datos["Usuario"])
    datos["Condición académica"] = datos["Condición académica"].fillna("Sin notas informadas")
    datos["Situación de actividad"] = datos["Situación de actividad"].fillna(
        "Sin registro en participación"
    )
    if eventos is not None:
        resumen = eventos.groupby("Usuario").agg(
            **{"Registros de trazabilidad": ("Usuario", "size"),
               "Días con eventos": ("Día", "nunique")}
        ).reset_index().rename(columns={"Usuario": "Identificación"})
        datos = datos.merge(resumen, on="Identificación", how="left", validate="one_to_one")
        for columna in ["Registros de trazabilidad", "Días con eventos"]:
            datos[columna] = datos[columna].fillna(0).astype("Int64")
    datos["Materia"] = materia
    return datos


def calcular_correlacion(datos, variable, resultado="Resultado observado"):
    pares = datos[[variable, resultado]].dropna()
    if len(pares) < 3:
        return pares, None, "Se requieren al menos 3 observaciones emparejadas."
    if pares[variable].nunique() < 2 or pares[resultado].nunique() < 2:
        return pares, None, "No se calcula correlación porque una variable es constante."
    return pares, float(pares[variable].corr(pares[resultado])), None


def resumir_materia(materia, participacion, alumnos, resultados, periodo):
    actividad = resumir_participacion(alumnos)
    valores = resultados["Resultado observado"].dropna()
    return {
        "Materia": materia,
        "Desde": periodo[0], "Hasta": periodo[1],
        "Usuarios del reporte": len(participacion),
        "Alumnos del aula": len(alumnos),
        "Con dato de actividad": actividad["con_dato_actividad"],
        "Activos": actividad["con_actividad"],
        "Inactivos": actividad["sin_actividad"],
        "Activos (%)": actividad["cobertura"],
        "Inactivos (%)": (
            100 * actividad["sin_actividad"] / actividad["con_dato_actividad"]
            if actividad["con_dato_actividad"] else None
        ),
        "Con resultado observado": len(valores),
        "Resultado promedio": float(valores.mean()) if len(valores) else None,
        "Rendimiento promedio sobre notas informadas (%)": (
            resultados["Rendimiento observado (%)"].mean()
            if materia == "Álgebra" else valores.mean()
        ),
        "Escala": "Suma / 120 (parcial si faltan instrumentos)" if materia == "Álgebra" else "Promedio / 100",
        "Tiempo promedio estimado (min)": actividad["tiempo_promedio"],
    }
