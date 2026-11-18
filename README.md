# Seguimiento académico del TFI

Aplicación de seguimiento académico con siete dashboards independientes. La URL raíz abre General. Cada dashboard tiene una navegación compacta para cambiar de vista o volver a General. Todas las vistas abre la landing secundaria con tarjetas, también disponible en `/vistas`; los enlaces anteriores a `/general` siguen funcionando. Las fuentes se incluyen en `data/` y se transforman en memoria; no se necesita ninguna carpeta externa.

## Datos incluidos

```text
app.py
datos.py / procesamiento.py / vistas.py / estilos.py / graficos.py
requirements.txt
.streamlit/config.toml
data/
  Matriculados/                         # 3 XLSX
  Algoritmos y Estructuras de Datos/     # 7 XLSX
  Probabilidad y Estadística/           # 11 XLSX
  Álgebra/                             # 5 XLSX
  SHA256SUMS                           # Integridad de las 26 fuentes
tests/
tools/
```

Los 26 XLSX son copias byte a byte de las fuentes anonimizadas: conservan nombres, carpetas y contenido interno. Los originales externos no se modificaron. `datos.py` resuelve `data/` con `Path(__file__).resolve().parent`, sin rutas absolutas ni dependencia del directorio de trabajo. Se conservan los acentos y mayúsculas de los nombres para Linux.

## Instalar y ejecutar

Versión local validada: **Python 3.11.9**. Para desplegar, seleccionar **Python 3.11**. `requirements.txt` fija las versiones del entorno validado, incluidas Streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5 y python-calamine 0.9.1, y sus dependencias resueltas.

Clonar [el repositorio](https://github.com/santibiancotti/tpfinal_bya) y entrar en su raíz. En Windows / PowerShell, con Python 3.11 instalado:

```powershell
git clone https://github.com/santibiancotti/tpfinal_bya.git
cd tpfinal_bya
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/verificar_datos.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

En Linux / macOS:

```bash
git clone https://github.com/santibiancotti/tpfinal_bya.git
cd tpfinal_bya
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verificar_datos.py
.venv/bin/python -m streamlit run app.py
```

Ejecutar Streamlit desde la raíz para que también tome `.streamlit/config.toml`. El entorno virtual, los archivos temporales y los secretos locales se excluyen mediante `.gitignore`. La app no requiere secretos, servicios externos ni archivos derivados persistentes. Los gráficos y cálculos usan las mismas versiones en ambos sistemas; los paquetes binarios se instalan para la plataforma correspondiente.

Abrir la dirección local que muestra Streamlit. Elegir una vista y una materia; General permite seleccionar varias materias. General destaca estudiantes únicos y deja asignaturas y registros alumno-materia como contexto. Después presenta las comparaciones de actividad y condición y las tarjetas de resultado, con color, unidad y escala de cada materia. **Explorar distribución y condiciones** permite elegir una asignatura; **Tendencia diaria de accesos a secciones** carga la evolución al abrirla. Las tablas de actividad y fuentes y los criterios metodológicos tienen sus propios desplegables. En Participación, abrir **Evolución de accesos**. En Notas y Participación, abrir **Incluir indicadores de trazabilidad** para agregarlos al selector del gráfico. En Individual, elegir un estudiante y abrir Notas o Historial de actividad.

Las lecturas y los resultados derivados se cachean por materia y firma de sus fuentes (ruta, fecha de modificación y tamaño). Las calificaciones incluyen la lista de todos sus instrumentos. El botón **Actualizar fuentes** vacía todas las cachés; las secciones abiertas se actualizan y las cerradas se leerán al abrirlas. El historial, los detalles y los reportes originales solo se preparan y envían cuando se abre la sección correspondiente. La primera lectura de un Excel grande puede tardar y se informa qué se está cargando.

La lectura completa de trazabilidad usa `python-calamine==0.9.1`, elegido mediante mediciones sin caché y comparación de los datos completos. Las fuentes pequeñas y cabeceras mantienen openpyxl. Se conserva el almacenamiento de caché en memoria; no se generan archivos derivados para ejecutar la aplicación. Los tiempos y la justificación están en [RENDIMIENTO.md](RENDIMIENTO.md).

La jerarquía visual de las siete vistas, sus accesos al detalle y los componentes compartidos están documentados en [DISENO.md](DISENO.md). El rediseño no incorpora dependencias. Las tablas se consultan a pedido; Matrícula mantiene visible una lista compacta de casos.

## Desplegar en Streamlit Community Cloud

Configurar una nueva app con estos valores:

| Campo | Valor |
| --- | --- |
| Repositorio | `santibiancotti/tpfinal_bya` |
| Rama | `main` |
| Archivo principal | `app.py` |
| Python, en Advanced settings | `3.11` |
| Dependencias | `requirements.txt`, en la raíz |
| Tema | `.streamlit/config.toml` |
| Fuentes | `data/`, incluido en Git |
| Secrets | Ninguno requerido |

Conectar la cuenta de GitHub en Community Cloud, autorizar el acceso al repositorio y pulsar **Deploy**. La versión de Python se elige en Advanced settings; no depende del entorno virtual local. No se necesita `packages.txt`: los lectores se instalan desde paquetes Python. Referencias oficiales: [organización de archivos](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [dependencias](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) y [configuración del despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

Tras desplegar, comprobar General en `/`, las siete vistas y la primera apertura de tendencias e historial. Esa apertura sigue leyendo Excel en frío; su duración y consumo dependen de los recursos del servidor. Las cargas diferidas y los mensajes de carga se mantienen. La ejecución real en Linux y los límites de memoria de Community Cloud deben confirmarse en ese primer despliegue.

## Actualizar las fuentes

1. Copiar las nuevas fuentes anonimizadas a las subcarpetas de `data/`, conservando el formato de cada reporte. La detección de materias parte de `data/Matriculados/<materia>.xlsx`; la carpeta de cada materia debe tener el mismo nombre. Mantener un solo reporte de participación y uno de trazabilidad por materia: reemplazar o retirar la versión anterior si cambió el nombre. Las calificaciones admiten un archivo por instrumento, sin duplicar instrumentos.
2. Revisar los cambios y regenerar el manifiesto: `python tools/verificar_datos.py --actualizar-manifiesto`. Verificar después con `python tools/verificar_datos.py` y ejecutar las pruebas. Este comando solo actualiza el manifiesto; no transforma los XLSX. Para cotejar una copia con una carpeta de originales, usar `--originales RUTA` (solo lectura).
3. Versionar las fuentes y `data/SHA256SUMS`, hacer commit y push a `main`. En otra instalación local, incorporar ese commit con `git pull`; en Cloud, esperar a que se incorpore el cambio del repositorio.
4. En la app con los archivos ya actualizados, pulsar **Actualizar fuentes**. Las cachés distinguen materia, ruta, modificación y tamaño; la lista completa de instrumentos forma parte de la firma de calificaciones. El botón vacía también los resultados derivados y las secciones cerradas se vuelven a leer al abrirlas.

**Publicar archivos y refrescar cachés son pasos distintos.** El botón no copia archivos, no hace `git pull` y no modifica GitHub. Un refresh sin archivos nuevos vuelve a leer las mismas fuentes.

## Criterios de cálculo

- Actividad: al menos una interacción durante el período del reporte. Usuarios del reporte, alumnos del aula, matrícula vigente y alumnos activos son poblaciones distintas. Sin registro de matrícula no significa baja.
- Matrícula vigente: último movimiento por fecha de inscripción y número de transacción, con estado Aceptada. Los cruces validan una fila por identificador dentro de cada materia.
- Álgebra: suma de puntos y porcentaje sobre el máximo de las notas informadas de cada estudiante. La condición proyectada al momento de consultar conserva las proporciones de la consigna: regular desde 60/120 y promociona desde 85/120. Por ejemplo, 34/45 equivale a 90,67/120 y proyecta promoción, conservando la categoría «Promociona». La proyección se actualiza al incorporar nuevas calificaciones. Con el esquema completo, los cortes vuelven a ser exactamente 60 y 85 puntos sobre 120.
- Probabilidad y Estadística: promedio de notas informadas sobre 100, incluido el recuperatorio. Regular desde 60 y promociona desde 85.
- Algoritmos: promedio de notas informadas sobre 100. Regular desde 60 y promociona desde 90.
- Una nota faltante queda faltante; no se convierte en cero. Un cero informado sí participa. Los formatos no numéricos desconocidos generan un mensaje de error para revisar la fuente.
- Los porcentajes de condición académica en Rendimiento y General usan estudiantes presentes en los archivos de calificaciones. Notas y Participación conserva también estudiantes sin notas y permite elegir la población.
- Las correlaciones usan pares completos por estudiante y materia, informan su cantidad y requieren al menos tres pares y variación en ambas variables. En Álgebra se utiliza el porcentaje sobre notas informadas. Son asociaciones descriptivas.
- General distingue estudiantes únicos de registros alumno-materia y conserva las escalas. No promedia globalmente sumas y promedios de materias diferentes.

## Validación local del 16 al 18/11/2026

Entorno comprobado: Python 3.11.9, Streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5 y python-calamine 0.9.1. La consigna local se contrastó con el código y las fuentes.

| Dashboard | Comprobado | Pendientes funcionales de esta etapa |
| --- | --- | --- |
| General | Tres materias, activos/inactivos, promedios, histogramas, condiciones, tendencia diaria y filtro de asignaturas | Ninguno |
| Participación | Resumen, cobertura, tiempo estimado, evolución por fecha y estudiante, cambio de materia y período | Ninguno |
| Trazabilidad | Filtros, resúmenes por acción/día/semana, detalle, mapa horario y promedio diario | Ninguno |
| Rendimiento académico | Comparación de instrumentos, histograma, condiciones y porcentajes con denominador explícito | Ninguno |
| Notas y Participación | Dispersión y Pearson para interacciones, tiempo estimado, registros y días con eventos; poblaciones y patrones descriptivos | Ninguno |
| Individual | Selección, matrícula, participación, notas, semáforo y callback de historial diferido | Ninguno |
| Matrícula y alertas | Poblaciones, estados administrativos y actividad separados, grupos y alertas por materia | Ninguno |

Pruebas reproducibles:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La suite incluye 32 pruebas. Quince verifican lectura, procesamiento y caché con casos controlados: fechas e identificadores del Excel, valores faltantes y textos, límites académicos, Álgebra parcial/completa, datos vacíos, faltantes y ceros, formatos desconocidos, duplicados, pares insuficientes/constantes, cardinalidad de uniones, fechas inclusivas, repeticiones y equivalencia de los resúmenes compactos. Nueve pruebas de Streamlit AppTest ejecutan las siete vistas con las tres materias y sus filtros, la navegación y el regreso a General, el detalle de General, las tablas opcionales de las siete vistas, el semáforo y la aclaración de proyección. Seis pruebas puntuales comprueban la carga diferida real, la reutilización del historial, la ausencia de tablas ocultas y la actualización automática y manual de fuentes. Dos pruebas de portabilidad verifican los hashes y la resolución de las fuentes desde otro directorio. Las fuentes necesarias ya forman parte del repositorio; una copia completa debe ejecutar toda la suite, sin omisiones.

Las herramientas de medición y lectura usan la misma carpeta `data/` resuelta por `datos.py`. `tools/comprobar_resumenes.py` contrasta además un commit histórico: requiere Git y el historial completo del clon, mientras que la app y las pruebas no dependen de Git.

La preparación portable del 18/11 se comprobó en un clon local limpio (solo contenido versionado e historial) ubicado en una carpeta temporal sin fuentes externas. Se creó un entorno nuevo de Python 3.11.9, sin paquetes del sistema ni del entorno anterior, y se instalaron las 38 versiones de `requirements.txt`; `pip check` no encontró conflictos. Las 32 pruebas pasaron en 27,669 s, sin omisiones. Un auditor de Python bloqueó el acceso al proyecto original y a la carpeta original de datos durante esa suite: no hubo intentos de acceso. General mantuvo 319 estudiantes únicos, 3 asignaturas y 957 registros, sin tablas iniciales. El servidor independiente respondió HTTP 200 en `/` y `ok` en `/_stcore/health`, con el tema conservado.

Se descargaron también los 38 paquetes binarios o universales para Linux x86_64 / Python 3.11 mediante `pip download --only-binary=:all:` y plataformas manylinux. Eso comprueba disponibilidad de instalación sin compilación; no constituye una ejecución en Linux. La máquina de validación es Windows y no tiene un entorno Linux instalado. Los resultados se registran en [la comprobación de portabilidad](mediciones/portabilidad_2026-11-18.json).

Además se inició el servidor real, se comprobó su endpoint de salud y se revisaron en navegador el cambio del mapa entre Algoritmos y Álgebra, el semáforo, las notas, la apertura del historial, la dispersión de Notas y Participación y la consolidación de las tres materias en General. La cobertura exhaustiva de materias y filtros corresponde a AppTest; los límites y casos sintéticos se comprobaron a nivel de procesamiento.

El 17/11 se revisó el rediseño en navegador real a 1440 y 780 píxeles de ancho: los siete accesos y el regreso a Inicio, General con una y tres materias, la tendencia, los tooltips, las tablas con fechas y los criterios desplegables. Se corrigió el recorte nativo de etiquetas de indicadores en el ancho menor; los valores quedaron alineados y no hubo desbordamiento horizontal de la página ni errores de consola. La pasada focalizada del 18/11 aprobó la suite de 30 pruebas y comprobó la entrada directa a General, el menú secundario y la nueva composición en ambos anchos.

Conteos observados en las fuentes del 01/05/2025 al 24/10/2025:

| Materia | Usuarios del reporte | Alumnos | Activos | Inactivos | Matrículas vigentes | Con resultado |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Algoritmos y Estructuras de Datos | 329 | 319 | 276 | 43 | 165 | 146 |
| Probabilidad y Estadística | 328 | 319 | 273 | 46 | 164 | 194 |
| Álgebra | 329 | 319 | 268 | 51 | 163 | 196 |

General consolida 319 estudiantes únicos y 957 registros alumno-materia, con 817 registros activos. El cruce histórico de Algoritmos coincide: vigentes 163 con actividad y 2 sin actividad; bajas 2 con actividad; sin registro de matrícula 111 con actividad y 41 sin actividad. Estos valores son resultados de la comprobación, no constantes del producto.

Se comprobó que las uniones no multiplican estudiantes. Los resúmenes optimizados se contrastaron con el procesamiento anterior en las tres materias: conteos, filtros, repeticiones, mapas, series, historiales y calificaciones coinciden. Las mediciones antes/después y sus condiciones están en [RENDIMIENTO.md](RENDIMIENTO.md). Los hashes de los 26 XLSX permanecieron iguales durante la validación.

## Limitaciones de las fuentes y alcance

Álgebra solo incluye Parcial 1 y dos autoevaluaciones (hasta 45 de los 120 puntos). Su condición se presenta como «Condición proyectada según notas informadas», también en los porcentajes y agrupaciones. En las otras materias se conserva el promedio observado, sin imputar evaluaciones ausentes.

Los reportes indican período mayo-octubre de 2025, pero los eventos presentes comienzan el 05/08/2025. Las tendencias de General incluyen días sin eventos dentro del período exportado. Los filtros detallados de actividad se limitan al intervalo con eventos y el resumen de participación permanece referido al reporte completo.

Las fuentes identifican eventos de acceso, no sesiones. No se inventó una definición de sesión ni un modelo o umbral nuevo de riesgo. Los grupos descriptivos usan actividad registrada y condición académica. La matrícula refleja el último estado disponible del archivo, no una verificación administrativa en tiempo real.

Las siete vistas comparten tema, encabezado, indicadores y gráficos como primera lectura, y detalle bajo demanda. El repositorio queda preparado para instalación independiente y despliegue; el informe técnico final y la puesta en marcha en Community Cloud son etapas posteriores.
