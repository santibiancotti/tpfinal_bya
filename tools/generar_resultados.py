"""Recalcula RESULTADOS.md desde data/ con las funciones validadas de la app."""
import argparse
from datetime import date
from hashlib import sha256
from importlib.metadata import version
from numbers import Integral
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
import datos
import procesamiento as p
from estilos import formato_numero, nombre_materia
from tools.verificar_datos import hashes


def numero(valor, decimales=0):
    return "No disponible" if pd.isna(valor) else formato_numero(valor, decimales)


def porcentaje(numerador, denominador):
    return numero(100 * numerador / denominador, 2) + " %" if denominador else "No calculable"


def tabla(encabezados, filas):
    def celda(valor):
        if isinstance(valor, Integral):
            return numero(valor)
        return str(valor).replace("|", r"\|").replace("\n", " ")
    return "\n".join([
        "| " + " | ".join(encabezados) + " |",
        "| " + " | ".join("---" for _ in encabezados) + " |",
        *("| " + " | ".join(celda(c) for c in fila) + " |" for fila in filas),
    ])


def calcular():
    fuentes = hashes(datos.CARPETA_DATOS)
    manifiesto = dict(linea.split("  ", 1)[::-1] for linea in
                      (datos.CARPETA_DATOS / "SHA256SUMS").read_text(encoding="utf-8").splitlines())
    if fuentes != manifiesto:
        raise ValueError("Las fuentes no coinciden con SHA256SUMS; revisar antes de informar.")
    materias = {}
    for materia in datos.detectar_materias():
        reporte = datos.leer_participacion(materia)
        alumnos = p.preparar_participacion(reporte)
        inscripciones = datos.leer_matriculados(materia)
        matricula = p.consolidar_matricula(inscripciones)
        base = p.clasificar_alertas(p.cruzar_matricula_participacion(matricula, alumnos))
        notas = p.preparar_calificaciones(datos.leer_calificaciones(materia))
        resultados = p.resumir_resultados_alumnos(notas, materia)
        original = datos.leer_trazabilidad(materia)
        resumen = p.resumir_trazabilidad(original)
        eventos = resumen["eventos"]
        periodo = datos.leer_periodo_reporte(materia)
        if periodo != datos.leer_periodo_reporte(materia, "trazabilidad"):
            raise ValueError(f"Los períodos de las fuentes difieren en {materia}.")
        eventos = p.filtrar_trazabilidad(eventos, *periodo)
        # Los controles comparan poblaciones y recuentos antes y después de unir.
        assert base["Identificación"].is_unique and resultados["Usuario"].is_unique
        assert alumnos["Usuario"].is_unique
        assert eventos["Registros"].sum() == len(p.obtener_alumnos(original))
        assert p.resumir_condiciones(resultados)["Alumnos"].sum() == len(resultados)
        cruce = p.cruzar_resultados_participacion(base, resultados, materia)
        cruce = p.agregar_actividad_trazabilidad(cruce, p.resumir_actividad_alumnos(eventos))
        assert cruce["Identificación"].is_unique
        assert int(base["Con actividad"].sum()) == int(alumnos["Con actividad"].sum())
        assert base.groupby(["Situación de matrícula", "Situación de actividad"]).size().sum() == len(base)
        assert base["Alerta"].value_counts().sum() == len(base)
        assert resultados["Instrumentos con nota"].sum() == notas["Puntos obtenidos"].count()
        assert p.resumir_instrumentos(notas)["Notas informadas"].sum() == notas["Puntos obtenidos"].count()
        for campo in ["Día", "Semana", "Hora", "Día de semana", "Acción"]:
            assert eventos.groupby(campo, dropna=False)["Registros"].sum().sum() == eventos["Registros"].sum()
        for variable in ["Interacciones", "Tiempo de uso (minutos)", "Registros de trazabilidad",
                         "Días con eventos", "Resultado observado"]:
            assert not cruce[variable].dropna().isin([float("inf"), -float("inf")]).any()
        materias[materia] = dict(
            reporte=reporte, alumnos=alumnos, inscripciones=inscripciones, matricula=matricula,
            base=base, notas=notas, resultados=resultados, eventos=eventos, cruce=cruce,
            periodo=periodo, total_reporte=len(original),
        )
        print(f"Calculado: {materia}; {len(alumnos)} alumnos; {eventos['Registros'].sum()} eventos.", flush=True)
    assert fuentes == hashes(datos.CARPETA_DATOS), "Las fuentes cambiaron durante el cálculo."
    return materias, fuentes


def redactar(materias, fuentes):
    partes = []
    def agregar(texto):
        partes.append(texto.strip())
    def cuadro(encabezados, filas):
        agregar(tabla(encabezados, filas))
    alias = {m: nombre_materia(m) for m in materias}
    periodos = {v["periodo"] for v in materias.values()}
    assert len(periodos) == 1
    desde, hasta = next(iter(periodos))
    dias_reporte = (hasta - desde).days + 1
    agregar(f"""# Resultados observados para el informe técnico

Fecha de cálculo: {date.today():%d/%m/%Y}. Los nombres de las exportaciones de participación, trazabilidad y calificaciones corresponden al 24/10/2025.
Período declarado común de participación y trazabilidad: **{desde:%d/%m/%Y}–{hasta:%d/%m/%Y}, {dias_reporte} días inclusivos**.
Las calificaciones son las disponibles en los archivos exportados; sus nombres no permiten fechar cada evaluación.

## 1. Fuentes, población y reproducción

Se leyeron los {len(fuentes)} XLSX actuales de [data/](data/), sin modificarlos. La identidad exacta de cada fuente está en [data/SHA256SUMS](data/SHA256SUMS).
Los nombres abreviados de las tablas corresponden a Álgebra, Probabilidad y Estadística y Algoritmos y Estructuras de Datos.

Para recalcular este archivo desde la raíz, con las dependencias instaladas:

~~~bash
python tools/verificar_datos.py
python tools/generar_resultados.py
~~~

Se reutilizan los lectores de datos.py y las funciones de procesamiento.py. El script verifica hashes, unicidad de identificadores, cardinalidad de los cruces, sumas de condiciones, concordancia de actividad y recuentos completos de trazabilidad.
Las cantidades son enteros; porcentajes y promedios se presentan con dos decimales y Pearson con cuatro. Los cálculos usan los valores sin redondear; los porcentajes redondeados pueden no sumar exactamente 100 %.
""")
    hash_texto = lambda archivo: sha256(archivo.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    agregar(f"Entorno de cálculo: Python {sys.version.split()[0]}, pandas {version('pandas')}, "
            f"openpyxl {version('openpyxl')}, python-calamine {version('python-calamine')}. "
            f"SHA-256 de procesamiento.py (texto con saltos LF): {hash_texto(RAIZ / 'procesamiento.py')}. "
            f"SHA-256 del manifiesto (texto con saltos LF): {hash_texto(datos.CARPETA_DATOS / 'SHA256SUMS')}.")
    agregar("""## 2. Poblaciones y actividad

### Observado

Usuarios del reporte incluye todos los perfiles. Alumnos del aula conserva únicamente el perfil Alumnos.
Activo significa Interacciones > 0 durante el período completo; inactivo significa cero informado. El denominador de actividad es alumnos con dato, no matrícula vigente.""")
    cuadro(["Materia", "Usuarios del reporte", "Alumnos del aula", "Con dato", "Activos", "Inactivos", "Activos / con dato"],
           [[alias[m], len(v["reporte"]), len(v["alumnos"]), v["alumnos"]["Con actividad"].notna().sum(),
             v["alumnos"]["Con actividad"].sum(), v["alumnos"]["Con actividad"].eq(False).sum(),
             porcentaje(v["alumnos"]["Con actividad"].sum(), v["alumnos"]["Con actividad"].notna().sum())]
            for m, v in materias.items()])
    usuarios = set().union(*(set(v["alumnos"]["Usuario"]) for v in materias.values()))
    activos = set().union(*(set(v["alumnos"].loc[v["alumnos"]["Con actividad"].eq(True), "Usuario"])
                           for v in materias.values()))
    registros = sum(len(v["alumnos"]) for v in materias.values())
    activos_registros = sum(int(v["alumnos"]["Con actividad"].sum()) for v in materias.values())
    agregar(f"Consolidado: **{len(usuarios)} identificadores únicos**, {registros} registros alumno-materia y "
            f"{activos_registros} registros alumno-materia activos ({porcentaje(activos_registros, registros)}). "
            f"{len(activos)} identificadores tienen actividad en al menos una materia; "
            f"{len(usuarios - activos)} no presentan actividad en ninguna de las tres. "
            "Los identificadores se deduplican tras quitar espacios y convertir a mayúsculas.")
    cuadro(["Materia", "Interacciones totales", "Mediana por alumno", "Media de minutos estimados", "Con dato de tiempo / alumnos"],
           [[alias[m], numero(v["alumnos"]["Interacciones"].sum()), numero(v["alumnos"]["Interacciones"].median(), 2),
             numero(v["alumnos"]["Tiempo de uso (minutos)"].mean(), 2),
             f'{v["alumnos"]["Tiempo de uso (minutos)"].notna().sum()} / {len(v["alumnos"])}']
            for m, v in materias.items()])
    agregar("""### Interpretación y límites

La cobertura describe presencia de alguna interacción en el aula, no asistencia, aprendizaje o continuidad semanal.
Los minutos son estimaciones del reporte, no tiempo real cronometrado. Un usuario activo en dos materias aporta dos registros activos, pero un solo identificador al consolidado.
La deduplicación global supone que los identificadores anonimizados representan de forma consistente a la misma persona entre materias; no verifica identidad civil.""")
    agregar("""## 3. Matrícula, participación y alertas

### Observado

Se conserva el último movimiento por fecha de inscripción y número de transacción dentro de cada materia.
Aceptada se presenta como Vigente. La base completa es la unión de matrícula consolidada y alumnos del aula, con una fila por identificador.""")
    cuadro(["Materia", "Fechas de movimientos", "Movimientos originales", "IDs en matrícula", "Vigentes", "Bajas", "Base completa", "Fuera del aula"],
           [[alias[m], "–".join(f"{f:%d/%m/%Y}" for f in
                               pd.to_datetime(v["inscripciones"]["Fecha inscripción"], dayfirst=True).agg(["min", "max"])),
             len(v["inscripciones"]), len(v["matricula"]), v["base"]["Matrícula vigente"].sum(),
             v["base"]["Situación de matrícula"].eq("Baja").sum(), len(v["base"]), (~v["base"]["En aula"]).sum()]
            for m, v in materias.items()])
    filas = []
    for m, v in materias.items():
        for estado, grupo in v["base"].groupby("Situación de matrícula", sort=True):
            actividad = grupo["Situación de actividad"].value_counts()
            filas.append([alias[m], estado, int(actividad.get("Con actividad registrada", 0)),
                          int(actividad.get("Sin actividad registrada", 0)),
                          int(actividad.get("Sin registro en participación", 0) + actividad.get("Actividad sin determinar", 0)),
                          len(grupo)])
    cuadro(["Materia", "Situación de matrícula", "Con actividad", "Sin actividad", "Sin registro/dato", "Total"], filas)
    alertas = ["Vigente sin actividad registrada", "Vigente sin registro en participación",
               "Vigente con actividad sin determinar", "Actividad sin registro en matrícula",
               "Actividad con baja registrada", "Actividad con otro estado de matrícula",
               "Sin alerta con estos criterios"]
    cuadro(["Alerta (base completa)", *alias.values()],
           [[alerta, *(int(v["base"]["Alerta"].eq(alerta).sum()) for v in materias.values())] for alerta in alertas]
           + [["Total con alerta", *(int(v["base"]["Tiene alerta"].sum()) for v in materias.values())]])
    cuadro(["Materia", "Alertas / base completa", "Alertas en vigentes / vigentes"],
           [[alias[m], f'{int(v["base"]["Tiene alerta"].sum())} / {len(v["base"])} '
             f'({porcentaje(v["base"]["Tiene alerta"].sum(), len(v["base"]))})',
             f'{int(v["base"].loc[v["base"]["Matrícula vigente"], "Tiene alerta"].sum())} / '
             f'{int(v["base"]["Matrícula vigente"].sum())} '
             f'({porcentaje(v["base"].loc[v["base"]["Matrícula vigente"], "Tiene alerta"].sum(), v["base"]["Matrícula vigente"].sum())})']
            for m, v in materias.items()])
    agregar("""### Interpretación y límites

Las alertas son cruces descriptivos y mutuamente excluyentes de las reglas actuales, no un modelo de riesgo ni una nueva condición académica.
Actividad sin registro en matrícula no significa una baja: señala falta de correspondencia entre las fuentes.
Actividad con baja registrada puede haber ocurrido antes de la baja, porque participación resume todo el período y matrícula conserva el último estado disponible.
Las fechas de movimientos de matrícula no constituyen una fecha de exportación ni acreditan que el estado siga vigente fuera de los archivos recibidos.
Sin alerta solo significa que no se cumple ninguna de estas reglas; no certifica ausencia de dificultades.""")
    agregar("""## 4. Resultados académicos y cobertura de evaluaciones

### Observado

Las condiciones porcentuales se calculan sobre los identificadores presentes en archivos de calificaciones de cada materia.
La cobertura de resultado respecto del aula usa, separadamente, alumnos del aula como denominador.
Cada estudiante aporta un solo resultado; las notas faltantes no se convierten en cero. Un cero informado sí participa.
En Probabilidad y Estadística el recuperatorio se incluye como otro instrumento con nota; no sustituye automáticamente una evaluación anterior.""")
    filas = []
    for m, v in materias.items():
        r = v["resultados"]
        presentes = r["Resultado observado"].notna()
        aula = set(v["alumnos"]["Usuario"])
        con_resultado_aula = r.loc[presentes & r["Usuario"].isin(aula), "Usuario"].nunique()
        filas.append([alias[m], len(r), int(presentes.sum()), con_resultado_aula,
                      porcentaje(con_resultado_aula, len(aula)), int((~r["Usuario"].isin(aula)).sum()),
                      v["notas"]["Instrumento"].nunique()])
    cuadro(["Materia", "IDs en notas", "Con resultado", "Con resultado en aula", "% del aula", "IDs de notas fuera del aula", "Instrumentos disponibles"], filas)
    cuadro(["Materia", "Unidad del resultado observado", "Media", "Mediana", "Mínimo", "Máximo", "n con resultado"],
           [[alias[m], "Puntos acumulados parciales" if m == "Álgebra" else "Promedio sobre 100",
             *(numero(v["resultados"]["Resultado observado"].agg(op), 2) for op in ["mean", "median", "min", "max"]),
             int(v["resultados"]["Resultado observado"].notna().sum())] for m, v in materias.items()])
    filas = []
    for m, v in materias.items():
        for fila in p.resumir_condiciones(v["resultados"]).to_dict("records"):
            filas.append([alias[m] + (" · proyectada" if m == "Álgebra" else ""),
                          fila["Condición académica"], fila["Alumnos"], numero(fila["Porcentaje (%)"], 2) + " %", len(v["resultados"])])
    cuadro(["Materia", "Condición", "Estudiantes", "% de IDs en notas", "Denominador"], filas)
    agregar("""Criterios conservados: Probabilidad y Estadística regulariza desde 60/100 y promociona desde 85/100; Algoritmos, desde 60/100 y 90/100.
Álgebra proyecta proporcionalmente sobre 120 a partir de los puntos y del máximo de las evaluaciones con nota de cada estudiante: regular desde el equivalente a 60/120 y promoción desde 85/120.
Por ejemplo, 34/45 equivale a 90,67/120 y proyecta «Promociona».
La categoría de Álgebra es **Condición proyectada según notas informadas**, al momento de consultar, y se actualiza con nuevas calificaciones.""")
    a = materias["Álgebra"]
    maximos = a["notas"].groupby("Instrumento")["Puntos máximos"].first()
    agregar(f"Álgebra dispone de {len(maximos)} de los 8 instrumentos del esquema: "
            f"{numero(maximos.sum())}/120 puntos ({porcentaje(maximos.sum(), 120)} del esquema). "
            f"El promedio de los porcentajes individuales sobre notas informadas es "
            f'{numero(a["resultados"]["Rendimiento observado (%)"].mean(), 2)} % '
            f'(n={a["resultados"]["Rendimiento observado (%)"].notna().sum()}). '
            "Este promedio de porcentajes individuales no se obtiene dividiendo la media de puntos por un máximo común cuando la cobertura difiere entre estudiantes.")
    agregar("#### Cobertura por instrumento\n\nDenominador de la cobertura: IDs presentes en el conjunto de archivos de notas de la materia. "
            "Filas indica usuarios exportados en ese instrumento; notas informadas cuenta solo valores numéricos. "
            "Promedio (%) conserva la escala porcentual del instrumento.")
    filas = []
    for m, v in materias.items():
        for instrumento, grupo in v["notas"].groupby("Instrumento", sort=True):
            n = int(grupo["Puntos obtenidos"].count())
            filas.append([alias[m], instrumento, len(grupo), n, porcentaje(n, len(v["resultados"])),
                          numero(grupo["Puntos máximos"].dropna().iloc[0]),
                          numero(grupo["Porcentaje obtenido"].mean(), 2)])
    cuadro(["Materia", "Instrumento", "Filas", "Notas informadas", "Cobertura / IDs en notas", "Máximo informado", "Promedio (%)"], filas)
    agregar("#### Instrumentos con nota por alumno del aula\n\nBase: alumnos del aula. Cero incluye a quienes no tienen resultado en los archivos recibidos; "
            "no es una nota académica cero. Los instrumentos disponibles son los exportados, no necesariamente todos los del plan.")
    filas = []
    for m, v in materias.items():
        cantidades = v["alumnos"][["Usuario"]].merge(v["resultados"][["Usuario", "Instrumentos con nota"]], how="left", on="Usuario", validate="one_to_one")
        distribucion = cantidades["Instrumentos con nota"].fillna(0).astype(int).value_counts().sort_index()
        assert distribucion.sum() == len(v["alumnos"])
        for cantidad, n in distribucion.items():
            filas.append([alias[m], cantidad, int(n), porcentaje(n, len(v["alumnos"]))])
    cuadro(["Materia", "Instrumentos con nota", "Alumnos", "% de alumnos del aula"], filas)
    agregar("Máximo de las notas informadas de cada estudiante de Álgebra (base: IDs en sus archivos de notas):")
    cuadro(["Máximo individual (puntos)", "Estudiantes", "% de IDs en notas"],
           [[numero(maximo), int(n), porcentaje(n, len(a["resultados"]))]
            for maximo, n in a["resultados"]["Máximo de sus notas"].value_counts(dropna=False).sort_index().items()])
    agregar("""### Interpretación y límites

Las condiciones describen notas disponibles, no acreditación administrativa final. La concentración en promoción debe leerse junto con la cobertura: quienes no figuran en notas no integran el denominador de condiciones.
Los promedios usan solo instrumentos con nota; comparar materias sin considerar instrumentos y poblaciones puede inducir a error.
En Álgebra la suma parcial y la proyección normalizada son medidas diferentes. No se promedian globalmente sus puntos con promedios sobre 100 de las otras materias.
No se imputan evaluaciones futuras, fechas de evaluación, ponderaciones adicionales ni reglas de reemplazo no presentes en los cálculos validados.""")
    agregar("""## 5. Correlaciones de participación y rendimiento

### Observado

Pearson se calcula sobre pares completos por alumno y materia, con al menos tres pares y variación en ambas variables.
Y es porcentaje sobre el máximo de las notas informadas en Álgebra y promedio observado sobre 100 en las otras dos.
X corresponde al período completo: Interacciones y Tiempo de uso (minutos) provienen de participación; Registros de trazabilidad y Días con eventos, de eventos de Alumnos.
Para estos dos indicadores de trazabilidad, la app asigna cero a alumnos sin eventos en el reporte; las calificaciones faltantes permanecen faltantes.""")
    correlaciones = []
    for poblacion in ["Alumnos del aula", "Matrícula vigente"]:
        agregar(f"#### Población: {poblacion}")
        filas = []
        for m, v in materias.items():
            seleccion = p.seleccionar_poblacion(v["cruce"], poblacion)
            y = "Rendimiento observado (%)" if m == "Álgebra" else "Resultado observado"
            for x in ["Interacciones", "Tiempo de uso (minutos)", "Registros de trazabilidad", "Días con eventos"]:
                pares, r, motivo = p.calcular_correlacion(seleccion, x, y)
                if r is not None:
                    assert abs(r - pares[x].corr(pares[y])) < 1e-12
                filas.append([alias[m], x, len(seleccion), len(pares), len(seleccion) - len(pares),
                              numero(r, 4) if r is not None else motivo])
                correlaciones.append((poblacion, m, x, len(pares), r))
        cuadro(["Materia", "Variable X", "Población", "Pares completos", "Sin par", "r de Pearson"], filas)
    coincide = all(set(v["cruce"]["Identificación"]) == set(v["alumnos"]["Usuario"]) for v in materias.values())
    agregar("La base completa coincide en identificadores con alumnos del aula en las tres materias; sus correlaciones coinciden."
            if coincide else "La base completa puede incluir identificadores fuera del aula; las tablas anteriores conservan las poblaciones indicadas.")
    valores = [r for poblacion, _, _, _, r in correlaciones if poblacion == "Alumnos del aula" and r is not None]
    agregar(f"En alumnos del aula, los coeficientes observados abarcan de {numero(min(valores), 4)} a {numero(max(valores), 4)}.")
    for poblacion in ["Alumnos del aula", "Matrícula vigente"]:
        _, materia, variable, n, r = max(
            (c for c in correlaciones if c[0] == poblacion and c[4] is not None),
            key=lambda c: abs(c[4]),
        )
        agregar(f"Mayor magnitud absoluta en {poblacion}: {alias[materia]}, {variable}, "
                f"r={numero(r, 4)}, n={n} pares.")
    agregar("""### Interpretación y límites

Son asociaciones descriptivas. No permiten concluir que más actividad cause mejores notas, ni que una intervención cambie el rendimiento.
La exclusión de alumnos sin calificaciones condiciona los pares disponibles; las asociaciones no representan automáticamente a todos los matriculados.
Interacciones, minutos, eventos y días son variables diferentes. Los coeficientes dependen de la población, la cobertura, valores extremos y el carácter acumulado de las medidas.
No se realizaron pruebas de significación ni se estimaron intervalos de confianza, ajustes por confusores o modelos predictivos.
La ausencia de eventos antes del inicio efectivo de los registros limita cualquier lectura longitudinal.""")
    agregar("""## 6. Patrones temporales de trazabilidad

### Observado

Se incluyen todos los eventos del perfil Alumnos, normalizando espacios en Acción; se conservan repeticiones.
Accesos a secciones cuenta únicamente Acción = Acceder y no equivale a sesiones.
El reporte completo incluye otros perfiles y se informa por separado.""")
    filas = []
    for m, v in materias.items():
        e = v["eventos"]
        total = int(e["Registros"].sum())
        accesos = int(e.loc[e["Acción"].eq("Acceder"), "Registros"].sum())
        repeticiones = int(e["Repetición exacta adicional"].sum())
        primero, ultimo = e["Día"].min(), e["Día"].max()
        span = (ultimo - primero).days + 1
        filas.append([alias[m], v["total_reporte"], total, e["Usuario"].nunique(), accesos,
                      repeticiones, porcentaje(repeticiones, total), f"{primero:%d/%m/%Y}–{ultimo:%d/%m/%Y}", e["Día"].nunique()])
        assert p.resumir_accesos_diarios(e, *v["periodo"])["Accesos a secciones"].sum() == accesos
    cuadro(["Materia", "Eventos todos los perfiles", "Eventos Alumnos", "Alumnos con eventos", "Acceder", "Repeticiones adicionales", "% de eventos Alumnos", "Primer–último día", "Días con eventos"], filas)
    filas = []
    for m, v in materias.items():
        e = v["eventos"]
        span = (e["Día"].max() - e["Día"].min()).days + 1
        filas.append([alias[m], dias_reporte, span,
                      numero(e["Registros"].sum() / dias_reporte, 2),
                      numero(e["Registros"].sum() / span, 2),
                      (e["Día"].min().date() - desde).days])
    cuadro(["Materia", "Días declarados", "Días primer–último evento", "Eventos/día declarado", "Eventos/día del intervalo observado", "Días iniciales sin registros"], filas)
    agregar("El indicador diario de Trazabilidad usa el intervalo observado seleccionado, inclusive. "
            "La tendencia de General completa con cero los días del período declarado sin eventos; esos ceros describen el archivo, "
            "no prueban ausencia de actividad educativa en días no registrados.")
    agregar("**Concentraciones observadas.** Los siguientes porcentajes usan el total de eventos de Alumnos de cada materia:")
    for m, v in materias.items():
        e = v["eventos"]
        meses = e.groupby(e["Día"].dt.strftime("%Y-%m"))["Registros"].sum()
        dias = e.groupby("Día de semana")["Registros"].sum()
        horas = e.groupby("Hora")["Registros"].sum()
        mes, dia, hora = meses.idxmax(), int(dias.idxmax()), int(horas.idxmax())
        total = e["Registros"].sum()
        agregar(f"- {alias[m]}: mayor acumulado mensual en {mes}, {numero(meses.max())} eventos "
                f"({porcentaje(meses.max(), total)}); mayor concentración semanal en {p.DIAS_SEMANA[dia]}, "
                f"{numero(dias.max())} ({porcentaje(dias.max(), total)}); hora con más registros "
                f"{hora:02d}:00–{hora:02d}:59, {numero(horas.max())} ({porcentaje(horas.max(), total)}).")
    agregar("#### Distribución mensual\n\nAgosto y octubre son intervalos parciales del registro observado; los totales mensuales no ajustan por cantidad de días.")
    filas = []
    for m, v in materias.items():
        e = v["eventos"].assign(Mes=v["eventos"]["Día"].dt.strftime("%Y-%m"))
        for mes, grupo in e.groupby("Mes", sort=True):
            filas.append([alias[m], mes, int(grupo["Registros"].sum()),
                          porcentaje(grupo["Registros"].sum(), e["Registros"].sum()),
                          int(grupo.loc[grupo["Acción"].eq("Acceder"), "Registros"].sum())])
    cuadro(["Materia", "Mes", "Eventos Alumnos", "% de eventos de la materia", "Acceder"], filas)
    agregar("#### Picos diarios y semanales\n\nSe informa el máximo observado, conservando empates. "
            "Semana comienza el lunes; las semanas inicial y final pueden ser parciales.")
    filas = []
    for m, v in materias.items():
        e = v["eventos"]
        for tipo, grupo, campo in [("Todos los eventos diarios", e, "Día"),
                                   ("Acceder por día", e.loc[e["Acción"].eq("Acceder")], "Día"),
                                   ("Todos los eventos semanales", e, "Semana")]:
            serie = grupo.groupby(campo)["Registros"].sum()
            maximo = int(serie.max())
            fechas = ", ".join(f"{f:%d/%m/%Y}" for f in serie.index[serie.eq(maximo)])
            filas.append([alias[m], tipo, fechas, maximo, porcentaje(maximo, grupo["Registros"].sum())])
    cuadro(["Materia", "Medida", "Día / inicio de semana", "Eventos del pico", "% del total de esa medida"], filas)
    agregar("#### Día de semana y franjas horarias\n\nEl denominador de cada porcentaje es el total de eventos de Alumnos de la materia, no alumnos únicos ni sesiones.")
    filas = []
    for i, dia in enumerate(p.DIAS_SEMANA):
        filas.append([dia, *(f'{int(v["eventos"].loc[v["eventos"]["Día de semana"].eq(i), "Registros"].sum())} '
                              f'({porcentaje(v["eventos"].loc[v["eventos"]["Día de semana"].eq(i), "Registros"].sum(), v["eventos"]["Registros"].sum())})'
                              for v in materias.values())])
    cuadro(["Día de semana", *alias.values()], filas)
    filas = []
    for m, v in materias.items():
        horas = v["eventos"].groupby("Hora")["Registros"].sum().sort_values(ascending=False, kind="stable").head(3)
        for hora, n in horas.items():
            filas.append([alias[m], f"{int(hora):02d}:00–{int(hora):02d}:59", int(n), porcentaje(n, v["eventos"]["Registros"].sum())])
    cuadro(["Materia", "Tres horas con más eventos (hora del archivo)", "Eventos", "% del total"], filas)
    agregar("#### Acciones más frecuentes")
    filas = []
    for m, v in materias.items():
        acciones = v["eventos"].groupby("Acción")["Registros"].sum().sort_values(ascending=False, kind="stable").head(3)
        for accion, n in acciones.items():
            filas.append([alias[m], accion, int(n), porcentaje(n, v["eventos"]["Registros"].sum())])
    cuadro(["Materia", "Tres acciones con más eventos", "Eventos", "% del total"], filas)
    agregar("""### Interpretación y límites

Los picos identifican concentración de registros de uso del LMS. Sin fechas verificadas de evaluaciones o calendario de clases no se atribuyen a exámenes, entregas o estrategias docentes.
Los eventos de acceso no son sesiones y varias acciones pueden proceder de una misma interacción o estudiante. Las repeticiones exactas adicionales se señalan y se conservan, como en los dashboards.
La hora es la registrada en el archivo; no se documenta una zona horaria que permita convertirla de manera fundada.
Las diferencias entre materias pueden reflejar estructura del aula, tipo de acción registrada, volumen y cobertura de notas, además de comportamientos de uso.
La falta de eventos en el inicio del período declarado es una limitación de observación y no evidencia de abandono.

## 7. Alcance del resumen

Este archivo separa cantidades observadas e interpretación para servir de insumo al informe. No modifica las siete vistas, las poblaciones ni los criterios académicos.
Los datos constituyen una fotografía de los archivos exportados, no una comprobación administrativa o académica en tiempo real.
El estado de matrícula, actividad acumulada y resultados parciales provienen de fuentes distintas; ninguna de estas medidas por sí sola determina permanencia, aprobación definitiva o causalidad.
""")
    return "\n\n".join(partes) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RAIZ / "RESULTADOS.md")
    args = parser.parse_args()
    materias, fuentes = calcular()
    texto = redactar(materias, fuentes)
    args.salida.write_text(texto, encoding="utf-8", newline="\n")
    print(f"Generado {args.salida.name}: {len(fuentes)} fuentes verificadas.", flush=True)


if __name__ == "__main__":
    main()
