# Seguimiento académico del TFI

Aplicación local con siete dashboards independientes. La landing conserva sus botones y muestra la vista elegida debajo. Las fuentes originales se leen desde `../Datos_LMS_Anonimizados` y se transforman en memoria.

## Abrir

Desde PowerShell, en la carpeta de este proyecto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir la dirección local que muestra Streamlit. Elegir una vista y una materia; General permite seleccionar varias materias. En Individual, elegir un estudiante y abrir Notas o Historial de actividad. El historial se carga únicamente cuando su pestaña está abierta.

Las lecturas se cachean por ruta, fecha de modificación y tamaño. La trazabilidad preparada también distingue la materia. El botón **Actualizar fuentes** vacía todas las cachés y vuelve a leer los archivos.

## Criterios de cálculo

- Actividad: al menos una interacción durante el período del reporte. Usuarios del reporte, alumnos del aula, matrícula vigente y alumnos activos son poblaciones distintas. Sin registro de matrícula no significa baja.
- Matrícula vigente: último movimiento por fecha de inscripción y número de transacción, con estado Aceptada. Los cruces validan una fila por identificador dentro de cada materia.
- Álgebra: suma de puntos y porcentaje sobre el máximo de las notas informadas de cada estudiante. Por decisión del usuario, la condición con notas parciales conserva las proporciones de la consigna: regular desde 60/120 y promociona desde 85/120. Por ejemplo, 34/45 equivale a 90,67/120 y promociona. Con el esquema completo, los cortes vuelven a ser exactamente 60 y 85 puntos sobre 120.
- Probabilidad y Estadística: promedio de notas informadas sobre 100, incluido el recuperatorio. Regular desde 60 y promociona desde 85.
- Algoritmos: promedio de notas informadas sobre 100. Regular desde 60 y promociona desde 90.
- Una nota faltante queda faltante; no se convierte en cero. Un cero informado sí participa. Los formatos no numéricos desconocidos generan un mensaje de error para revisar la fuente.
- Los porcentajes de condición académica en Rendimiento y General usan estudiantes presentes en los archivos de calificaciones. Notas y Participación conserva también estudiantes sin notas y permite elegir la población.
- Las correlaciones usan pares completos por estudiante y materia, informan su cantidad y requieren al menos tres pares y variación en ambas variables. En Álgebra se utiliza el porcentaje sobre notas informadas. Son asociaciones descriptivas.
- General distingue estudiantes únicos de registros alumno-materia y conserva las escalas. No promedia globalmente sumas y promedios de materias diferentes.

## Validación local del 16/11/2026

Entorno comprobado: Python 3.11.9, Streamlit 1.66.1, pandas 3.1.0 y openpyxl 3.1.5. No se agregaron dependencias. La consigna local se contrastó con el código y las fuentes.

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

Se ejecutaron 14 pruebas. Diez verifican procesamiento y caché con casos controlados: límites académicos, Álgebra parcial/completa, datos vacíos, faltantes y ceros, formatos desconocidos, duplicados, pares insuficientes/constantes, cardinalidad de uniones, fechas inclusivas y repeticiones. Cuatro pruebas de Streamlit AppTest ejecutan las siete vistas con las tres materias, cambian filtros, indicadores y estudiante, verifican que el mapa reciba datos diferentes por materia y que Individual no lea trazabilidad antes de abrir el historial. Las pruebas de la app requieren las fuentes locales; se omiten si no está esa carpeta.

Además se inició el servidor real, se comprobó su endpoint de salud y se revisaron en navegador el cambio del mapa entre Algoritmos y Álgebra, el semáforo, las notas, la apertura del historial, la dispersión de Notas y Participación y la consolidación de las tres materias en General. La cobertura exhaustiva de materias y filtros corresponde a AppTest; los límites y casos sintéticos se comprobaron a nivel de procesamiento.

Conteos observados en las fuentes del 01/05/2025 al 24/10/2025:

| Materia | Usuarios del reporte | Alumnos | Activos | Inactivos | Matrículas vigentes | Con resultado |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Algoritmos y Estructuras de Datos | 329 | 319 | 276 | 43 | 165 | 146 |
| Probabilidad y Estadística | 328 | 319 | 273 | 46 | 164 | 194 |
| Álgebra | 329 | 319 | 268 | 51 | 163 | 196 |

General consolida 319 estudiantes únicos y 957 registros alumno-materia, con 817 registros activos. El cruce histórico de Algoritmos coincide: vigentes 163 con actividad y 2 sin actividad; bajas 2 con actividad; sin registro de matrícula 111 con actividad y 41 sin actividad. Estos valores son resultados de la comprobación, no constantes del producto.

Se comprobó que las uniones no multiplican estudiantes. La carga de matrícula, participación y calificaciones para Individual tardó entre 0,35 y 0,70 s sin caché y entre 0,03 y 0,06 s con caché en esta máquina; estas cifras no incluyen renderizado ni primera lectura del historial. La primera lectura de los XLSX grandes de trazabilidad sigue siendo el paso más costoso. Los hashes de los 26 XLSX permanecieron iguales durante la validación.

## Limitaciones de las fuentes y alcance

Álgebra solo incluye Parcial 1 y dos autoevaluaciones (hasta 45 de los 120 puntos). La condición es provisional según las notas informadas y se actualiza al incorporar instrumentos. En las otras materias también se conserva el promedio observado, sin imputar evaluaciones ausentes.

Los reportes indican período mayo-octubre de 2025, pero los eventos presentes comienzan el 05/08/2025. Las tendencias de General incluyen días sin eventos dentro del período exportado. Los filtros detallados de actividad se limitan al intervalo con eventos y el resumen de participación permanece referido al reporte completo.

Las fuentes identifican eventos de acceso, no sesiones. No se inventó una definición de sesión ni un modelo o umbral nuevo de riesgo. Los grupos descriptivos usan actividad registrada y condición académica. La matrícula refleja el último estado disponible del archivo, no una verificación administrativa en tiempo real.

Quedan para etapas posteriores la mejora estética integral, el informe técnico final, el remoto y el despliegue. No hay publicación ni cambios de remotos en esta etapa.
