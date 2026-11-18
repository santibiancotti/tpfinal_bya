# Presentación de las siete vistas

Actualizado el 18/11/2026. General es la entrada de la aplicación. Las siete vistas mantienen su independencia y comparten estilos, encabezados, indicadores y gráficos. El rediseño no agrega dependencias ni modifica fuentes, cálculos o cachés.

## Entrada y navegación

La URL raíz `/` abre General. La barra compacta empieza por General, con icono de inicio y estado activo azul profundo; permite acceder a los otros seis dashboards y regresar a General. El título del navegador identifica cada vista. El enlace anterior `/general` redirige a la raíz sin repetir la carga de datos. La landing sigue disponible en `/vistas`, mediante Todas las vistas, y su botón principal vuelve a General.

## Composición final de General

- Encabezado breve, selector de asignaturas y período del reporte. El período queda junto al selector en escritorio y debajo en el ancho menor.
- Una sola franja azul profundo reúne el contexto: estudiantes únicos es el dato principal, con mayor tamaño; asignaturas y registros alumno-materia quedan como contexto secundario. Las ayudas conservan sus definiciones y los valores proceden de los cálculos existentes.
- Actividad por materia y Condición académica comparten una superficie blanca. Se presentan lado a lado a 1440 px y apiladas a 780 px, separadas por una línea discreta. Los títulos, unidades, bases por fila y leyendas permiten leer cada comparación sin abrir la metodología.
- Resultados por materia presenta tres tarjetas de proporción común. Cada una tiene acento superior con el color de la materia, nombre, resultado dominante, unidad y escala, y cantidad de estudiantes en un pie secundario. No hay una caja exterior adicional que compita con ellas.
- Explorar en detalle agrupa el acceso a distribuciones, tendencia, tablas y criterios. Se conserva la carga diferida real de las secciones costosas.

Los porcentajes conservan su escala completa de 0 a 100. Se redujeron las marcas principales a 0, 50 y 100, se ampliaron las filas y se centraron las etiquetas dentro de los segmentos que tienen espacio. Las categorías pequeñas conservan su segmento y su tooltip. Las posiciones de las etiquetas se calculan sobre todos los segmentos, de modo que ocultar una etiqueta pequeña no desplaza las demás. Los tooltips muestran porcentaje con dos decimales, recuento y denominador, materia completa y criterio.

## Pregunta y primera lectura

Antes de modificar cada vista se definieron su pregunta y su prioridad:

| Vista | Pregunta principal | Se ve primero | Acceso al detalle |
| --- | --- | --- | --- |
| General | ¿Cómo se comparan la actividad y los resultados entre materias? | Contexto con estudiantes únicos destacado, comparaciones protagonistas y tarjetas con resultado, unidad y escala | Explorar distribución y condiciones; tendencia; Ver tablas de actividad y fuentes |
| Participación | ¿Cuántos alumnos participan y cómo evoluciona la actividad? | Alumnos, actividad, cobertura y tiempo estimado; gráfico de actividad | Evolución de accesos; Ver alumnos; Ver valores diarios; reporte original |
| Trazabilidad | ¿Cuándo y en qué acciones se concentra la actividad? | Indicadores de la selección y mapa horario | Pestañas por día, semana y acción con gráficos; Ver valores del resumen; Detalle; reporte original |
| Rendimiento | ¿Cómo se comparan los instrumentos y se distribuyen los resultados? | Indicadores y comparación visual por instrumento | Distribución de resultados muestra histograma y condiciones; desplegables con sus valores |
| Notas y participación | ¿Cómo se asocian la actividad y el rendimiento? | Pares completos, Pearson, dispersión y grupos visuales | Ver valores de los grupos; Criterios de la comparación; trazabilidad opcional |
| Individual | ¿Cuál es la situación actual del estudiante? | Identidad, matrícula, actividad, semáforo y resultado; resumen visual al elegir estudiante | Notas muestra barras; Ver notas y observaciones; Historial de actividad y Ver eventos del estudiante |
| Matrícula y alertas | ¿Cómo se cruza la situación administrativa con la actividad? | Indicadores, barras de matrícula y actividad y lista compacta de casos | Tres filtros de casos; Ver situaciones e interacciones; Ver historial de matrícula |

La jerarquía común es encabezado y filtros, indicadores compactos, gráficos, detalle solicitado y criterios desplegables. La pantalla inicial no muestra tablas en seis vistas. Matrícula conserva una lista de tres columnas (estudiante, ID y alerta), necesaria para identificar los casos; las situaciones e interacciones quedan como profundidad adicional.

No se adjunta automáticamente la tabla a cada gráfico. Las notas de instrumentos, distribuciones, recuentos de grupos, alumnos y eventos se preparan y envían cuando se solicita su sección. Las explicaciones completas están en Criterios de cada vista, con unidades, bases y avisos breves donde afectan la interpretación.

## Estilo y componentes reutilizados

| Uso | Decisión |
| --- | --- |
| Fondo y superficies | Fondo `#F4F7FB`, paneles blancos, bordes claros y radios de 12–16 px |
| Títulos y texto | Azul profundo `#173653`, texto secundario `#526579`, jerarquía de tamaños y espaciado |
| Acento interactivo | Verde azulado `#0F766E` para acciones, selección y gráficos sin categoría académica |
| Condiciones académicas | Libre `#DC2626`, Regular `#EAB308`, Promociona `#15803D`; se conservan los círculos reales del semáforo |
| Materias | Álgebra violeta `#6D56A0`, Probabilidad verde azulado `#0F766E`, Algoritmos azul `#2563EB` |
| Actividad | Azul para actividad, gris claro para ausencia informada; categorías sin datos diferenciadas |
| Indicadores | Agrupación en una superficie común, jerarquía de tamaños, ayudas nativas y alineación inferior; General reserva el azul profundo para su contexto |
| Números y fechas | Coma decimal en indicadores y tarjetas, unidades explícitas, fechas de detalle `DD/MM/YYYY` y ejes temporales `DD/MM` |
| Tarjetas de resultado | Superficie blanca, acento por materia, resultado de mayor tamaño, unidad y escala junto al dato, recuento secundario |
| Tablas | Índice oculto, columnas prioritarias y altura limitada; valores secundarios bajo demanda |

Los colores identifican materias, actividad o condición según la leyenda de cada gráfico. La condición académica conserva sus colores y su orden Libre → Regular → Promociona; el estado sigue escrito. Los gráficos omiten categorías sin casos cuando no aportan información, y los valores tabulares conservan todas las categorías, incluidos ceros.

Se reutilizan los componentes nativos de Streamlit y las funciones existentes de procesamiento. Los ajustes compartidos agrupan los indicadores de las otras seis vistas, mejoran sus encabezados y aumentan la legibilidad de ejes y leyendas, conservando su composición específica. Los archivos de presentación son:

- `.streamlit/config.toml`: tema claro nativo.
- `estilos.py`: paleta, encabezado, `indicadores`, `tarjeta_resultado`, formato numérico, configuración común `graficar` y CSS acotado a claves de contenedores.
- `graficos.py`: porcentajes, distribución, tendencia, barras de resúmenes, series de eventos, cruces de categorías y dispersión. Las firmas de contenido mantienen la actualización de gráficos al cambiar datos o filtros.
- `vistas.py`: composición de las siete vistas, navegación, secciones y tablas opcionales.
- `app.py`: páginas y cargas existentes; el contexto visible se reduce al período del reporte.

## Escalas, poblaciones y avisos

General conserva tarjetas separadas: Álgebra muestra la media de puntos acumulados parciales en un esquema de 120; las otras materias muestran promedios sobre 100. No se obtiene un promedio global entre esas escalas. El histograma conserva los intervalos calculados previamente.

La condición de Álgebra siempre se identifica como proyectada: en General, Rendimiento, los grupos de Notas y participación y la ficha Individual. La explicación completa se reutiliza con `mostrar_criterio_academico`, una vez por materia y vista, dentro de sus criterios. 34/45 equivale a 90,67/120 y sigue clasificando como «Promociona».

Los porcentajes académicos de General y Rendimiento conservan como base los estudiantes presentes en los archivos de calificaciones. Participación usa los alumnos con dato de actividad, sin convertir los faltantes en inactivos. Los grupos de Notas y participación y el cruce de Matrícula usan toda la población seleccionada y filtrada: el tooltip identifica su denominador. Las correlaciones usan solo pares completos, muestran su cantidad y advierten que no demuestran causalidad.

Las tendencias representan eventos, no sesiones. Las repeticiones se conservan. La actividad de matrícula se refiere al período completo y puede ser anterior a una baja; sin registro administrativo no significa baja. Los avisos de datos insuficientes o períodos incompatibles siguen visibles cuando corresponden.

## Carga y adaptación

Se conservan los `st.tabs` y desplegables con `on_change="rerun"` y comprobación de `.open`. La evolución de Participación, la tendencia de General, los indicadores adicionales de Notas y participación y el historial Individual siguen cargándose al solicitarlos. Las tablas opcionales, incluidos el historial de matrícula y los valores de cada resumen, se construyen dentro de su sección abierta. Actualizar fuentes conserva el vaciado de cachés y las firmas por materia, ruta, modificación y tamaño.

En escritorio amplio los gráficos comparables pueden verse en dos columnas. Por debajo de 950 px se apilan y las filas de cuatro indicadores pasan a dos columnas. Las tres tarjetas de General siguen compactas a 780 px. Navegación y etiquetas se acomodan al espacio disponible. Por debajo de 640 px se reducen márgenes y títulos; se conserva el comportamiento adaptable de Streamlit.

## Validación

Se inspeccionó la composición original antes de editar. En la pasada del 18/11 se revisó General a 1440 y 780 px, se capturaron su entrada y sus resultados en ambos anchos y se comprobó el retorno a General desde las seis vistas y el menú secundario. También se comprobaron el enlace /general, los títulos y el estado activo. La revisión acumulada de las siete vistas abarca: lectura de gráficos, etiquetas y escalas, selección de materias, General con una y tres, filtros de casos, notas e historial, tablas opcionales, tendencia, navegación y regreso a Inicio. El filtro de alerta de Matrícula redujo correctamente indicadores y lista a dos casos. Se comprobaron tooltips y denominadores. No se observaron superposiciones, desbordamiento horizontal de la página ni errores de renderizado; las desconexiones de los reinicios controlados del servidor se distinguieron de errores de la aplicación.

La suite del entorno virtual aprobó sus 30 pruebas: 15 de lectura, reglas y procesamiento, 9 de vistas y 6 de cargas diferidas y actualización. Se comprobó la entrada directa a General y su retorno desde las siete vistas, el menú secundario, los detalles opcionales y sus poblaciones. Las tres pruebas puntuales de materias, proyección y entrada también aprobaron al ejecutarse juntas; la de distribución restablece explícitamente su selección inicial para no depender del estado dejado por otra prueba.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/medir_rendimiento.py --salida mediciones/visual_siete_vistas_2026-11-17.json
```

Los 34 escenarios conservan todas sus métricas y los hashes de los 26 Excel coinciden con la revisión anterior. En la pasada del 18/11, volver a General tarda 0,413 s frente a 0,410 s; cambiar entre una y tres materias tarda 0,259 y 0,345 s. La primera consulta de la raíz registra 4,960 s y la primera tendencia 13,842 s. La variación de lectura en frío también se distingue de la presentación; no se atribuye al diseño una aceleración del lector. Los resultados, el alcance de cada medida y sus límites están en [RENDIMIENTO.md](RENDIMIENTO.md).

El CSS utiliza claves de contenedores y selectores `data-testid`, sin clases generadas. Una actualización de Streamlit puede requerir revisar esos selectores. La validación visual cubre los dos anchos indicados.
