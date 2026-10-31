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