# Rendimiento de la navegación

Medición local del 16/11/2026. General muestra sus indicadores antes de cargar la tendencia: primera entrada de 96,642 s a 1,916 s; primer indicador emitido de 95,372 s a 1,132 s. Se conservaron los siete dashboards, los cálculos y la condición proyectada de Álgebra.

## Método

- Mismo entorno virtual: Python 3.11.9 y Streamlit 1.66.1, mismas fuentes y mismo programa de medición antes y después.
- Antes: revisión c025b17. Después: revisión 7471553. No se ejecutaron mediciones antes/después en paralelo.
- AppTest ejecuta Streamlit y sus reruns reales. Se vacía st.cache_data al iniciar cada vista en frío y con el botón Actualizar fuentes. No se vacía la caché del sistema operativo.
- General se mide al entrar, volver desde Matrícula, seleccionar una materia, recuperar las tres, abrir la tendencia y actualizar fuentes. Las otras vistas se miden en frío, en una segunda ejecución y al cambiar de Algoritmos a Probabilidad.
- Los tiempos de las funciones se atribuyen de forma exclusiva a lectura de Excel, preparación, agregaciones, presentación o acceso a fuentes/caché; el tiempo de hijos no se suma dos veces. Otros incluye la ejecución de Streamlit/AppTest y sus cachés fuera de esas funciones.
- Presentación incluye construir gráficos, tablas y mensajes del servidor. Estos tiempos no incluyen la red ni el pintado del navegador. También se comprobó General en el navegador real.
- Son observaciones de una ejecución por caso, no un promedio estadístico. La duración de leer Excel varió entre las ejecuciones. El lector de Excel no se cambió: la mejora principal se demuestra evitando sus llamadas al entrar y reutilizando resúmenes después.

## General: desglose de la primera entrada

| Etapa | Antes (s) | Después (s) |
| --- | ---: | ---: |
| Lectura de Excel | 93,037 | 0,890 |
| Preparación | 1,169 | 0,067 |
| Agregaciones | 0,451 | 0,062 |
| Presentación | 1,261 | 0,773 |
| Fuentes y caché | 0,478 | 0,080 |
| Otros | 0,245 | 0,044 |
| Total | 96,642 | 1,916 |

Antes, pagina_general esperaba la lectura y preparación de los tres reportes completos de trazabilidad. Ahora carga participación y calificaciones, y difiere la tendencia hasta abrir su desplegable. La tendencia devuelve 531 filas diarias para las tres materias, en lugar de preparar y transportar sus 150.104 eventos.

## Todos los escenarios

| Escenario | Antes (s) | Después (s) |
| --- | ---: | ---: |
| general_frio | 96,642 | 1,916 |
| general_reentrada | 1,282 | 0,263 |
| general_seleccion_una | 0,676 | 0,137 |
| general_seleccion_tres | 1,312 | 0,305 |
| general_abrir_tendencia | 1,317 | 52,461 |
| general_tendencia_repetida | 1,349 | 0,327 |
| general_actualizar_fuentes | 96,927 | 1,654 |
| general_tendencia_tras_actualizar | 1,356 | 34,988 |
| participacion_frio | 28,099 | 0,245 |
| participacion_reentrada | 0,341 | 0,041 |
| participacion_cambio_materia | 39,320 | 0,171 |
| participacion_abrir_evolucion | 0,346 | 14,419 |
| trazabilidad_frio | 27,599 | 9,666 |
| trazabilidad_reentrada | 0,845 | 0,064 |
| trazabilidad_cambio_materia | 43,127 | 14,501 |
| trazabilidad_abrir_detalle | 1,070 | 0,389 |
| relacion_frio | 28,105 | 0,502 |
| relacion_reentrada | 0,509 | 0,094 |
| relacion_cambio_materia | 42,958 | 0,556 |
| relacion_abrir_trazabilidad | 0,547 | 14,237 |
| individual_frio | 1,095 | 0,447 |
| individual_reentrada | 0,303 | 0,052 |
| individual_cambio_materia | 1,304 | 0,448 |
| individual_seleccionar | 0,351 | 0,065 |
| individual_abrir_notas | 0,404 | 0,078 |
| individual_abrir_historial | 41,752 | 14,539 |
| individual_cambiar_estudiante | 0,703 | 0,113 |
| individual_historial_repetido | 0,476 | 0,077 |
| rendimiento_frio | 0,708 | 0,286 |
| rendimiento_reentrada | 0,344 | 0,086 |
| rendimiento_cambio_materia | 0,933 | 0,427 |
| matricula_frio | 0,727 | 0,306 |
| matricula_reentrada | 0,232 | 0,051 |
| matricula_cambio_materia | 0,727 | 0,278 |

En la versión anterior, abrir tendencia/evolución/indicadores de trazabilidad no disparaba una lectura nueva: ese costo ya se había pagado al entrar, aunque la sección estuviera oculta. Después, las filas de apertura de esas secciones incluyen su primera lectura. Por eso no deben interpretarse como una regresión ni sumarse como trabajo que antes no existía. Los indicadores de General se emiten antes de esa espera.

## Cambios y cuellos de botella

- General: tendencia con carga diferida real mediante expander.open y on_change="rerun". La tendencia diaria tiene su propia caché por materia y firma de la fuente.
- Participación: la pestaña Resumen abre sin leer trazabilidad. Evolución se calcula al abrirla. Los filtros consultan un resumen por día, hora, estudiante y acción, sin descripciones ni tablas originales.
- Trazabilidad: el mapa y los resúmenes usan grupos con conteos ponderados. Se mantienen las repeticiones exactas identificadas antes de agrupar. Detalle y reporte original solo se preparan y envían al abrirlos. En el mapa de Algoritmos, las tablas enviadas pasan de 26.471.252 bytes a cero; el gráfico sigue recibiendo sus 168 celdas. Esta cifra mide tablas, no todo el tráfico de la página.
- Notas y Participación: los cruces con interacciones y tiempo estimado se muestran primero. Los indicadores derivados de trazabilidad se incorporan a pedido y utilizan una tabla por estudiante.
- Individual: se filtra el estudiante antes de copiar y preparar el historial. La caché distingue fuente, estudiante y período; volver a consultar no recorre ni copia el aula completa.
- Participación, calificaciones, resultados académicos y base de matrícula preparada también se reutilizan entre vistas. Las claves incluyen las fuentes que intervienen y la lista de instrumentos disponibles.
- Las firmas incluyen materia, ruta, modificación en nanosegundos y tamaño. Actualizar fuentes limpia tanto lecturas como resultados derivados. Las secciones cerradas mantienen su carga diferida después de actualizar.

## Comprobaciones

- 23 pruebas aprobadas desde el entorno virtual: las 14 existentes, tres de resúmenes compactos y seis de ejecución diferida y actualización.
- Las pruebas instrumentan las llamadas reales de Streamlit: no hay lectura de eventos al entrar a General, Participación o Notas y Participación. General y Evolución tampoco llaman a la preparación de tablas completas al abrirse. Detalle sí lo hace cuando corresponde.
- Se comprobó reutilización al reabrir secciones e historiales, cambio de materia y período, ausencia de tablas ocultas, cambio automático de la firma de una fuente y actualización manual. Las simulaciones modifican copias en memoria o archivos temporales de prueba, nunca los XLSX originales.
- tools/comprobar_resumenes.py carga el procesamiento de la revisión c025b17 y compara las tres materias con los resultados nuevos: conteos, repeticiones, nombres de estudiantes, filtros diarios y por estudiante, mapas, series diarias/semanales/por acción, historial y calificaciones. Todos coinciden. En Detalle se compara el contenido con el índice de presentación reiniciado, ya que ese índice no se muestra al usuario.
- Se compararon los indicadores comunes de los 34 escenarios antes/después. No hubo diferencias. Los SHA256 de los 26 XLSX coinciden antes/después.
- Se reinició el servidor del proyecto con su entorno virtual y se comprobó General en el navegador: tres asignaturas, 319 estudiantes únicos, 957 registros alumno-materia y tendencia inicialmente cerrada, sin errores.

## Límites que persisten

La primera lectura de un reporte grande sigue necesitando descomprimir y recorrer su Excel con el lector existente. En las ejecuciones nuevas, la tendencia de las tres materias tardó 52,461 s al abrirse por primera vez y 34,988 s después de vaciar caché; la apertura de un reporte de Probabilidad tardó aproximadamente 14 s. Esos tiempos varían con la ejecución y el equipo. La app muestra qué se está cargando y los indicadores de General ya quedan disponibles.

Las cachés son de memoria: reiniciar el servidor o Actualizar fuentes obliga a releer lo necesario. El detalle completo de un aula sigue siendo una tabla grande cuando se solicita; filtrar por estudiante o período reduce lo que se envía. No se cambiaron las fuentes, no se agregó una dependencia ni se creó una copia persistente de los datos.

## Reproducir

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/comprobar_resumenes.py
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --salida mediciones/nueva_medicion.json
```

Las mediciones originales se conservan en mediciones/antes.json y mediciones/despues.json, con tiempos por etapa, número de llamadas, tamaño de tablas, indicadores y hashes de las fuentes.
