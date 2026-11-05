import pandas as pd


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

def preparar_participacion(participacion):
    perfil_normalizado = (
        participacion["Perfil"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    alumnos = participacion.loc[
        perfil_normalizado.eq("alumnos")
    ].copy()

    alumnos["Usuario"] = (
        alumnos["Usuario"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

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