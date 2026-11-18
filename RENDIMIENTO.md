# Rendimiento de la navegación y de la lectura en frío

Actualización del 16/11/2026: la primera apertura de la tendencia de General pasa de 26,354 s con openpyxl a 4,205 s con Calamine en una comparación controlada. La navegación y las cargas diferidas se conservan. El historial de Probabilidad pasa de 11,018 s a 1,600 s en frío.

## Decisión y alcance

Se agregó python-calamine==0.9.1 como motor de pandas para leer completamente los reportes de trazabilidad. El cambio productivo consiste en seleccionar ese motor en el lector existente; se mantienen las mismas columnas, encabezado, identificadores string y reglas de valores faltantes. Las cabeceras y fuentes pequeñas continúan con openpyxl, seleccionado explícitamente para conservar su comportamiento ante futuros cambios del motor predeterminado de pandas.

La dependencia se justifica por la mejora medida en lecturas completas sin caché y por la equivalencia de los DataFrames completos. La lectura directa con openpyxl y values_only también se probó: mejora menos y requeriría mantener un lector propio. No se cambiaron las funciones académicas ni las vistas.

Se evaluó la reutilización de los resúmenes existentes: la tendencia completa ya cacheada tarda aproximadamente 0,19 s con ambos lectores. Por eso se conservan esas cachés y no se agrega almacenamiento derivado en disco. Un archivo derivado necesitaría construirse leyendo la fuente en la primera consulta y agregaría otro mecanismo de invalidación; la lectura nativa reduce la espera inicial sin ese mecanismo.

Pandas admite Calamine como motor de read_excel: [documentación de pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html). Paquete usado: [python-calamine 0.9.1](https://pypi.org/project/python-calamine/0.9.1/).

## Método comparable

- Python 3.11.9, Streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5 y python-calamine 0.9.1 en el entorno virtual del proyecto.
- Lectores: dos rondas por cada una de las tres fuentes, sin caché de aplicación. Se invierte el orden en la segunda ronda. Se compara cada DataFrame completo con el lector anterior, incluyendo tipos y orden. La tabla presenta medianas de las dos rondas.
- El perfil cProfile se ejecuta por separado sobre la fuente más grande y sobre la construcción del resumen. Sus tiempos, afectados por la instrumentación, no se usan como tiempos de apertura.
- Aperturas de la app: se repite el mismo programa de 34 escenarios en procesos separados y consecutivos, forzando primero openpyxl y luego Calamine solo para la lectura completa de trazabilidad. Se vacía st.cache_data al iniciar cada vista en frío y mediante Actualizar fuentes. Las firmas y fuentes son las mismas.
- No se vacía la caché del sistema operativo. Frío significa cachés de la aplicación vacías; no se afirma una lectura desde disco físico sin caché. Los tiempos incluyen Streamlit/AppTest y la construcción de gráficos/tablas en el servidor, pero no la red ni el pintado del navegador.
- Las lecturas alternativas, los perfiles y las dos ejecuciones de la app no se midieron en paralelo. Los resultados varían con el equipo; los datos originales no se modifican.

## Primera lectura de los Excel: sin reutilizar datos derivados

| Materia | pandas/openpyxl (s) | openpyxl values_only (s) | pandas/Calamine (s) | Construir resumen después de Calamine (s) |
| --- | ---: | ---: | ---: | ---: |
| Algoritmos y Estructuras de Datos | 7,281 | 6,069 | 1,124 | 0,107 |
| Probabilidad y Estadística | 10,660 | 9,011 | 1,470 | 0,154 |
| Álgebra | 7,621 | 6,056 | 1,048 | 0,108 |

Las 18 lecturas comparadas producen datos completos idénticos. La mejora del lector es de aproximadamente 6,5 a 7,3 veces según la materia, sin utilizar la caché de Streamlit ni archivos derivados.

## Perfil y construcción de resúmenes

En Probabilidad, el perfil del lector anterior registra unos 45,1 millones de llamadas y concentra el costo en recorrer las filas, interpretar las celdas y reconstruir texto/XML con openpyxl. Calamine reduce las llamadas registradas a unos 3,6 millones. Construir el resumen compacto toma aproximadamente 0,15 s: no era el cuello de botella principal. El perfil detallado queda en mediciones/lectores.perfil.txt.

El resumen conserva sus dimensiones por día, hora, estudiante y acción; las repeticiones se identifican antes de agrupar. La tendencia de General sigue devolviendo 531 filas diarias, en lugar de transportar los 150.104 eventos individuales de las tres materias.

## Primeras aperturas de la app con caché vacía

| Escenario | Lector anterior (s) | Calamine (s) |
| --- | ---: | ---: |
| General: abrir tendencia de tres materias | 26,354 | 4,205 |
| General: abrir tendencia tras Actualizar fuentes | 26,039 | 4,224 |
| Participación: abrir evolución de Probabilidad | 11,297 | 1,730 |
| Trazabilidad: primera entrada de Algoritmos | 7,509 | 1,181 |
| Trazabilidad: cambiar a Probabilidad sin cargar | 11,171 | 1,748 |
| Notas y Participación: incorporar trazabilidad de Probabilidad | 11,290 | 1,839 |
| Individual: primer historial de Probabilidad | 11,018 | 1,600 |

La referencia histórica de 52,461 s para la tendencia y aproximadamente 14 s para Probabilidad corresponde a la medición anterior de la etapa de navegación. Se conserva en mediciones/despues.json. Para atribuir el cambio al lector se usa la repetición controlada actual (26,354 frente a 4,205 s), no una comparación directa entre mediciones realizadas en momentos diferentes.

## Reutilización y navegación habitual

| Escenario | Lector anterior (s) | Calamine (s) |
| --- | ---: | ---: |
| General: indicadores al entrar en frío | 1,570 | 1,485 |
| General: volver desde Matrícula | 0,147 | 0,145 |
| General: seleccionar una materia | 0,068 | 0,077 |
| General: seleccionar las tres materias | 0,125 | 0,125 |
| General: repetir tendencia con resumen cacheado | 0,188 | 0,193 |
| General: Actualizar fuentes con tendencia cerrada | 0,924 | 0,878 |
| Participación: entrar al resumen sin leer trazabilidad | 0,161 | 0,161 |
| Trazabilidad: segunda ejecución | 0,052 | 0,054 |
| Individual: repetir historial cacheado | 0,054 | 0,052 |

La diferencia de la primera apertura corresponde al lector. La reutilización de los resultados derivados ya existía y sigue evitando nuevas lecturas: repetir la tendencia ronda 0,19 s y repetir el historial ronda 0,05 s con ambos motores. No se atribuye esa rapidez al cambio de motor. La carga diferida real y el envío de tablas solo al abrirlas permanecen intactos.

## Equivalencia, actualización y pruebas

- 25 pruebas aprobadas en el entorno virtual: las 23 existentes y dos del lector. Se comprueban fechas reales y en texto, identificadores con ceros iniciales, celdas vacías, Unicode, valores NA, selección del motor y caché por ruta/modificación/tamaño.
- tools/comprobar_resumenes.py compara ahora también la lectura completa contra pandas/openpyxl, además del procesamiento previo: las tres materias coinciden en conteos, nombres, repeticiones, filtros, mapas, series, historiales y calificaciones.
- Las métricas completas de los 34 escenarios coinciden entre motores. Los SHA256 de los 26 XLSX coinciden antes/después.
- Las pruebas de carga diferida, cambio de fuente y Actualizar fuentes siguen pasando. No hay archivos derivados persistentes que deban invalidarse ni otro camino de lectura para el botón de actualización.
- Se reinició el servidor con el entorno virtual actualizado y se abrió la tendencia por primera vez en el navegador real: las tres series se mostraron sin errores. Los tiempos de la tabla corresponden a AppTest; esta comprobación visual no se usa como cronómetro.
- Se conserva la clasificación proporcional de Álgebra, incluidos 34/45 como Promociona, los colores del semáforo y la etiqueta de condición proyectada. Las siete vistas permanecen independientes.

## Límites actuales

Leer y resumir las tres trazabilidades en frío todavía requiere unos 4,2 s; un reporte grande o su primer historial requiere aproximadamente 1,6 a 1,8 s. Las cachés siguen siendo de memoria: al reiniciar el servidor, actualizar fuentes o cambiar un archivo se relee lo necesario con el lector rápido. El tamaño de las fuentes y la carga del equipo afectan estos tiempos.

El detalle completo de un aula sigue siendo una tabla grande cuando se solicita. Los filtros por estudiante y período reducen el contenido enviado. No se cambiaron las escalas, las ausencias, las reglas académicas ni las fuentes originales.

## Reproducir

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/perfilar_lectura.py
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --motor-trazabilidad openpyxl --salida mediciones/frio_openpyxl.json
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --motor-trazabilidad calamine --salida mediciones/frio_calamine.json
.\.venv\Scripts\python.exe tools/comprobar_resumenes.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

El selector de motor es exclusivo de la herramienta de medición; la app usa Calamine para la lectura completa de trazabilidad. Los JSON conservan los 34 escenarios, tiempos por etapa, llamadas, tamaños de tablas, métricas y firmas de las fuentes. Las mediciones de la etapa anterior permanecen en mediciones/antes.json y mediciones/despues.json.

## Anexo: los 34 escenarios de la comparación actual

| Escenario | openpyxl (s) | Calamine (s) |
| --- | ---: | ---: |
| general_frio | 1,570 | 1,485 |
| general_reentrada | 0,147 | 0,145 |
| general_seleccion_una | 0,068 | 0,077 |
| general_seleccion_tres | 0,125 | 0,125 |
| general_abrir_tendencia | 26,354 | 4,205 |
| general_tendencia_repetida | 0,188 | 0,193 |
| general_actualizar_fuentes | 0,924 | 0,878 |
| general_tendencia_tras_actualizar | 26,039 | 4,224 |
| participacion_frio | 0,161 | 0,161 |
| participacion_reentrada | 0,032 | 0,031 |
| participacion_cambio_materia | 0,180 | 0,145 |
| participacion_abrir_evolucion | 11,297 | 1,730 |
| trazabilidad_frio | 7,509 | 1,181 |
| trazabilidad_reentrada | 0,052 | 0,054 |
| trazabilidad_cambio_materia | 11,171 | 1,748 |
| trazabilidad_abrir_detalle | 0,289 | 0,287 |
| relacion_frio | 0,455 | 0,358 |
| relacion_reentrada | 0,076 | 0,083 |
| relacion_cambio_materia | 0,406 | 0,402 |
| relacion_abrir_trazabilidad | 11,290 | 1,839 |
| individual_frio | 0,322 | 0,330 |
| individual_reentrada | 0,038 | 0,040 |
| individual_cambio_materia | 0,380 | 0,401 |
| individual_seleccionar | 0,051 | 0,044 |
| individual_abrir_notas | 0,089 | 0,053 |
| individual_abrir_historial | 11,018 | 1,600 |
| individual_cambiar_estudiante | 0,096 | 0,110 |
| individual_historial_repetido | 0,054 | 0,052 |
| rendimiento_frio | 0,197 | 0,195 |
| rendimiento_reentrada | 0,071 | 0,078 |
| rendimiento_cambio_materia | 0,262 | 0,239 |
| matricula_frio | 0,219 | 0,223 |
| matricula_reentrada | 0,038 | 0,046 |
| matricula_cambio_materia | 0,200 | 0,201 |

## Comprobación del rediseño visual · 17/11/2026

Inicio y General se reorganizaron sin cambiar el lector, el procesamiento ni las cachés. La navegación interna ya no construye las siete tarjetas. General presenta dos gráficos agregados y una tabla de tres filas; la distribución de una materia, las tablas adicionales y la metodología se consultan en desplegables. La tendencia conserva su carga diferida real mediante `on_change="rerun"` y comprobación de `.open`.

Se ejecutó la misma herramienta de 34 escenarios desde el entorno virtual. Comparación con la última medición validada (`frio_calamine.json`); resultados nuevos en `mediciones/diseno_2026-11-17.json`:

| Escenario de General | Antes del rediseño (s) | Rediseño (s) |
| --- | ---: | ---: |
| Primera entrada, caché vacía | 1,485 | 1,291 |
| Segunda entrada | 0,145 | 0,108 |
| Seleccionar una materia | 0,077 | 0,059 |
| Volver a tres materias | 0,125 | 0,083 |
| Primera apertura de tendencia | 4,205 | 4,588 |
| Tendencia con caché | 0,193 | 0,098 |
| Actualizar fuentes, tendencia cerrada | 0,878 | 0,991 |
| Tendencia después de actualizar | 4,224 | 5,431 |

Son tiempos de ejecución con Streamlit AppTest, incluidos datos y construcción de la presentación; no miden la animación, transferencia ni pintura del navegador. Son ejecuciones individuales en el mismo equipo, no una comparación estadística. Las métricas de los 34 escenarios y los SHA256 de los 26 Excel coinciden con la versión anterior.

La navegación se mantiene por debajo de 0,15 s con caché en los escenarios de General. La primera lectura de tres trazabilidades sigue siendo el límite: el tiempo en Excel pasó de 3,492 a 3,892 s en la primera apertura y de 3,524 a 4,618 s después de actualizar. El código de lectura permanece intacto; esta variación de lectura explica el mayor total en frío. La etapa instrumentada de presentación de esas aperturas pasó de aproximadamente 0,134 s a 0,036 y 0,053 s. El rediseño no elimina la espera de lectura ni la oculta detrás de una carga anticipada: al abrir la tendencia se informa qué se está cargando.

Se aprobaron las 27 pruebas existentes y ampliadas, incluidas las comprobaciones de carga diferida y actualización manual y automática de fuentes. Se verificó además en el navegador real: las siete rutas, regreso a Inicio, cambio de dashboard, General con una y tres materias, apertura de tendencia, tooltips, fechas, escalas y explicaciones, en anchos de 1440 y 780 px. La condición proyectada de Álgebra y los colores del semáforo se conservan. Las decisiones de presentación están en [DISENO.md](DISENO.md).

```powershell
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --salida mediciones/diseno_2026-11-17.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```


## Siete vistas con gráficos primero · 17/11/2026

Se completó la jerarquía visual de las siete vistas. General cambia su tabla inicial por tarjetas, Participación y Trazabilidad abren sus tablas al solicitarlas, Rendimiento difiere sus pestañas y valores, Notas y participación muestra grupos visuales, Individual prioriza ficha y resultados, y Matrícula conserva una lista compacta de tres columnas. Los eventos, originales y resultados tabulares se preparan solo en su sección abierta.

La primera medición del rediseño resultó más lenta que la referencia histórica también dentro de las etapas de Excel. Para comparar en condiciones actuales se ejecutó la revisión anterior `79423a6` en un checkout aislado, con el mismo entorno virtual y las mismas fuentes. Se midieron secuencialmente los mismos 34 escenarios en procesos nuevos; la ejecución del rediseño precedió a la de referencia. No se cambiaron los lectores, los datos ni las reglas.

| Escenario | Anterior en el entorno actual (s) | Rediseño (s) |
| --- | ---: | ---: |
| General, primera entrada sin caché | 3,805 | 3,910 |
| General, segunda entrada | 0,341 | 0,315 |
| General, seleccionar una materia | 0,204 | 0,192 |
| General, seleccionar tres materias | 0,304 | 0,337 |
| General, primera tendencia sin caché | 14,311 | 14,636 |
| General, tendencia con caché | 0,385 | 0,375 |
| General, actualizar fuentes | 2,837 | 2,927 |
| General, tendencia tras actualizar | 14,942 | 14,457 |
| Participación, segunda entrada | 0,112 | 0,115 |
| Trazabilidad, segunda entrada | 0,168 | 0,192 |
| Notas y participación, segunda entrada | 0,371 | 0,192 |
| Individual, segunda entrada | 0,124 | 0,138 |
| Rendimiento, segunda entrada | 0,288 | 0,134 |
| Matrícula, segunda entrada | 0,131 | 0,179 |

La lectura de Excel en la primera tendencia consumió 12,241 s en la revisión anterior y 12,451 s en el rediseño. En la primera entrada de General, Excel consumió 2,895 y 2,988 s respectivamente. Los mayores tiempos respecto de mediciones históricas también se reproducen en la versión anterior: esta comparación no atribuye esa diferencia de entorno al diseño. Son ejecuciones individuales, no una estimación estadística, y AppTest no mide transferencia ni pintura del navegador. En ambas revisiones la navegación con caché se mantiene por debajo de 0,4 s en estos escenarios.

Las tablas enviadas al entrar se redujeron de 2.270 a 0 bytes en General, de 42.462 a 0 en Participación, de 4.684 a 0 en Rendimiento y de 2.052 a 0 en Notas y participación. Matrícula pasó de 49.996 a 15.878 bytes conservando su lista identificable. Son tamaños en memoria de las tablas instrumentadas, no medidas de transferencia total; los gráficos siguen enviando sus resúmenes necesarios.

Los 34 escenarios terminaron sin errores. Coinciden las 86 métricas con etiquetas comunes, normalizando solo el separador decimal de presentación; algunos indicadores secundarios se trasladaron a ayudas o criterios y se añadieron indicadores visibles. Los recuentos y porcentajes de los detalles se contrastaron en las pruebas de vistas. Los hashes de los 26 XLSX coinciden entre ambas revisiones y con la medición previa.

Evidencia: `mediciones/visual_base_comparable_2026-11-17.json` y `mediciones/visual_siete_vistas_2026-11-17.json`. Las 29 pruebas del entorno virtual aprobaron en 72,680 s, incluidas las seis de cargas diferidas y actualización de fuentes y las dos nuevas de tablas bajo demanda. La revisión del navegador abarcó las siete vistas a 1440 y 780 px, filtros, detalle, semáforo, tendencia, tooltips, actualización y regreso a Inicio. La lectura grande en frío sigue siendo costosa, muestra su estado de carga y no se anticipa al navegar. Las decisiones visuales y los accesos al detalle están en [DISENO.md](DISENO.md).


## General como entrada y jerarquía visual · 18/11/2026

Se midió la revisión anterior `d088d51` en un checkout aislado y el diseño final con el mismo entorno virtual y las mismas fuentes. Se conservaron los 34 escenarios. La herramienta se adaptó a la nueva entrada: General en frío incluye ahora la primera ejecución de la raíz y la inicialización de AppTest; antes se medía abrir General desde la landing ya inicializada. Para las otras vistas se vuelve al menú y se vacía la caché después de inicializar la app, de modo que la nueva entrada General no les precargue los datos del escenario frío.

| Escenario | Antes (s) | Después (s) |
| --- | ---: | ---: |
| General, primera consulta sin caché | 7,247 | 4,960 |
| General, segunda entrada | 0,410 | 0,413 |
| Seleccionar una materia | 0,257 | 0,259 |
| Seleccionar tres materias | 0,379 | 0,345 |
| Primera apertura de tendencia | 18,468 | 13,842 |
| Tendencia con caché | 0,361 | 0,388 |
| Actualizar fuentes, tendencia cerrada | 3,299 | 2,934 |
| Tendencia tras actualizar | 16,152 | 13,405 |
| Participación, segunda entrada | 0,147 | 0,153 |
| Trazabilidad, segunda entrada | 0,215 | 0,158 |
| Notas y participación, segunda entrada | 0,179 | 0,196 |
| Individual, segunda entrada | 0,154 | 0,132 |
| Rendimiento, segunda entrada | 0,135 | 0,157 |
| Matrícula, segunda entrada | 0,168 | 0,411 |

La navegación de General y los cambios de materias se mantienen comparables. Son mediciones individuales del servidor con AppTest; no incluyen pintura ni transferencia del navegador, ni permiten afirmar una mejora estadística. La comparación de primera consulta tiene el cambio de alcance indicado: el valor posterior incluye el arranque de AppTest.

La variación en frío se concentra en lectura: Excel pasó de 6,261 a 2,867 s en la primera consulta de General y de 15,948 a 11,847 s en la primera tendencia. La presentación de esas aperturas pasó de 0,163 a 0,166 s y de 0,176 a 0,169 s. No se cambiaron lectores ni cachés y no se atribuye al diseño la reducción de tiempos de Excel. El sistema operativo no se vació de caché y la carga del equipo afecta estas cifras. La primera tendencia sigue siendo una operación costosa, informa su carga y se ejecuta solo al abrirla.

Los 34 escenarios terminaron sin errores y coinciden todas sus métricas, aunque el indicador principal de General cambió de posición. Los 26 SHA256 de las fuentes también coinciden. Las tablas iniciales conservan sus tamaños: cero en General y otras cinco vistas, y la lista compacta de Matrícula. Se aprobó la suite de 30 pruebas, incluidas las seis de cargas diferidas y actualización. Las tres pruebas puntuales de materias, proyección y entrada aprobaron juntas tras explicitar la selección inicial del detalle.

La comprobación en navegador cubrió la raíz General, la redirección del enlace anterior `/general`, las siete vistas y su regreso a General, el menú secundario `/vistas`, una y tres materias, tooltips con recuentos y denominadores, distribuciones, tablas, tendencia y Actualizar fuentes. General se revisó y capturó a 1440 y 780 px, sin desbordamiento horizontal ni errores de renderizado.

Evidencia: `mediciones/general_diseno_antes_2026-11-18.json` y `mediciones/general_diseno_despues_2026-11-18.json`. Las decisiones visuales están en [DISENO.md](DISENO.md).

```powershell
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --salida mediciones/general_diseno_despues_2026-11-18.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
