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
