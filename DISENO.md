# Presentación de Inicio y General

Entrega del 17/11/2026. El rediseño conserva las siete páginas independientes, los botones de navegación, los cálculos y las cachés. No agrega dependencias ni modifica fuentes.

## Jerarquía y navegación

Inicio presenta un acceso principal a General y seis tarjetas con categoría, título, descripción y el mismo botón. Dentro de cada dashboard, la barra compacta identifica la vista activa y permite cambiar de dashboard o volver a Inicio. Actualizar fuentes permanece disponible en el encabezado.

General organiza la lectura en este orden: título y propósito, selección y período de los reportes, tres indicadores, actividad y condiciones comparables, resumen de resultados y tendencia. El resumen tiene una fila por asignatura; la distribución se consulta para una asignatura elegida. Las tablas adicionales y los criterios se abren por separado.

Las comparaciones usan porcentajes con eje de 0 a 100 y el mismo orden de materias. Los tooltips indican materia completa, situación, porcentaje, cantidad de estudiantes, denominador y criterio. Los segmentos pequeños conservan su tooltip aunque no quepa una etiqueta dentro de la barra. La leyenda muestra las categorías presentes, respetando su orden académico.

Los resultados medios mantienen escalas explícitas: puntos acumulados parciales para Álgebra y promedios sobre 100 para las otras materias. La distribución conserva los intervalos calculados previamente; no equipara sumas y promedios. La tendencia representa eventos de acceso, con fechas, recuentos y colores estables por materia.

Álgebra conserva «Condición proyectada según notas informadas» en el gráfico de porcentajes, su tooltip y el detalle. La explicación completa se reutiliza desde `mostrar_criterio_academico` una sola vez en Criterios y denominadores. 34/45 sigue proyectando «Promociona».

## Estilo reutilizable

| Uso | Decisión |
| --- | --- |
| Fondo y superficies | Fondo `#F4F7FB`, paneles blancos, bordes claros y radios de 12–16 px |
| Títulos y texto | Azul profundo `#173653`, texto secundario `#526579`, tamaños y espaciado jerárquicos |
| Acento interactivo | Verde azulado `#0F766E` para botones principales y navegación activa |
| Condiciones académicas | Libre `#DC2626`, Regular `#EAB308`, Promociona `#15803D`; se conservan los círculos reales del semáforo |
| Materias | Álgebra violeta `#6D56A0`, Probabilidad verde azulado `#0F766E`, Algoritmos azul `#2563EB`, constantes entre tendencia y distribución |
| Números y fechas | Coma decimal, separador de miles cuando corresponde, porcentajes con una decimal y fechas `DD/MM/YYYY`; gráficos temporales con eje `DD/MM` |
| Tablas | Columnas breves y relevantes primero, índice oculto, unidades explícitas y detalle secundario desplegable |

El color de condición describe la categoría académica; el color de materia solo distingue series. El acento identifica acciones y selección. Las diferencias se expresan también con texto y leyendas.

Archivos y componentes para continuar:

- `.streamlit/config.toml`: tema claro nativo de Streamlit.
- `estilos.py`: paleta, nombres breves, formato numérico, `mostrar_encabezado`, configuración común `graficar` y CSS acotado mediante claves de contenedores. Las firmas de contenido de los gráficos mantienen su actualización al cambiar datos o filtros.
- `graficos.py`: porcentajes por materia, distribución y tendencia con escalas y tooltips explícitos; recibe resúmenes existentes.
- `vistas.py`: catálogo de dashboards, barra de navegación, tarjetas, paneles y detalle de General. Se reutilizan `st.container`, `st.columns`, `st.metric`, `st.dataframe`, selectores y desplegables de Streamlit.
- `app.py`: composición y carga existentes. El tema y la navegación no requieren lecturas adicionales.

Para las otras seis vistas ya están disponibles el tema, el encabezado y la barra. En su rediseño posterior se pueden repetir los paneles con clave `panel_…`, la jerarquía de indicadores y la configuración de gráficos, conservando las unidades y denominadores propios de cada vista.

## Adaptación y comprobaciones

En escritorio amplio, actividad y condición se muestran lado a lado. Por debajo de 950 px se apilan, al igual que las dos columnas del acceso destacado. La navegación se distribuye en filas cuando falta espacio. Las etiquetas de indicadores admiten saltos de línea y reservan una altura común; las tarjetas siguen el comportamiento adaptable de las columnas de Streamlit. Por debajo de 640 px se reducen márgenes y tamaños principales.

Se inspeccionó la app original antes de modificarla y se revisó el resultado en navegador real a 1440 y 780 px de ancho: Inicio, los siete accesos, regreso a Inicio, cambio entre dashboards, General con una y tres materias, distribución, tendencia, tooltips, fuentes con fechas y metodología. Se corrigieron etiquetas recortadas por el componente nativo de indicadores. No se observaron superposiciones, desplazamiento horizontal de la página ni errores de consola en esos anchos.

Las 27 pruebas del entorno virtual aprobaron, incluidas las nuevas comprobaciones de navegación y detalle, las seis pruebas de carga diferida y las reglas académicas. Los 34 escenarios conservan sus métricas y los 26 Excel sus hashes. Los tiempos y el límite de lectura en frío permanecen documentados en [RENDIMIENTO.md](RENDIMIENTO.md).

El CSS usa selectores `data-testid` y claves estables de contenedores, sin depender de clases generadas. Una actualización de Streamlit puede requerir revisar esos selectores. La revisión visual cubre los dos anchos indicados; las otras seis vistas conservan su composición específica para una entrega posterior.
