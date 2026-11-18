# Resultados observados para el informe técnico

Fecha de cálculo: 18/11/2026. Los nombres de las exportaciones de participación, trazabilidad y calificaciones corresponden al 24/10/2025.
Período declarado común de participación y trazabilidad: **01/05/2025–24/10/2025, 177 días inclusivos**.
Las calificaciones son las disponibles en los archivos exportados; sus nombres no permiten fechar cada evaluación.

## 1. Fuentes, población y reproducción

Se leyeron los 26 XLSX actuales de [data/](data/), sin modificarlos. La identidad exacta de cada fuente está en [data/SHA256SUMS](data/SHA256SUMS).
Los nombres abreviados de las tablas corresponden a Álgebra, Probabilidad y Estadística y Algoritmos y Estructuras de Datos.

Para recalcular este archivo desde la raíz, con las dependencias instaladas:

~~~bash
python tools/verificar_datos.py
python tools/generar_resultados.py
~~~

Se reutilizan los lectores de datos.py y las funciones de procesamiento.py. El script verifica hashes, unicidad de identificadores, cardinalidad de los cruces, sumas de condiciones, concordancia de actividad y recuentos completos de trazabilidad.
Las cantidades son enteros; porcentajes y promedios se presentan con dos decimales y Pearson con cuatro. Los cálculos usan los valores sin redondear; los porcentajes redondeados pueden no sumar exactamente 100 %.

Entorno de cálculo: Python 3.11.9, pandas 3.1.0, openpyxl 3.1.5, python-calamine 0.9.1. SHA-256 de procesamiento.py (texto con saltos LF): 081117e09c36b594f25ddd9a5b20ffc0364271e1d81ec56b9d54dc0ebb328fad. SHA-256 del manifiesto (texto con saltos LF): 2702ae8e3c99d14cf17deeb14d92a2896abd4b45160db647393a6bb94b2f4ffc.

## 2. Poblaciones y actividad

### Observado

Usuarios del reporte incluye todos los perfiles. Alumnos del aula conserva únicamente el perfil Alumnos.
Activo significa Interacciones > 0 durante el período completo; inactivo significa cero informado. El denominador de actividad es alumnos con dato, no matrícula vigente.

| Materia | Usuarios del reporte | Alumnos del aula | Con dato | Activos | Inactivos | Activos / con dato |
| --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | 329 | 319 | 319 | 276 | 43 | 86,52 % |
| Prob. y Estadística | 328 | 319 | 319 | 273 | 46 | 85,58 % |
| Álgebra | 329 | 319 | 319 | 268 | 51 | 84,01 % |

Consolidado: **319 identificadores únicos**, 957 registros alumno-materia y 817 registros alumno-materia activos (85,37 %). 285 identificadores tienen actividad en al menos una materia; 34 no presentan actividad en ninguna de las tres. Los identificadores se deduplican tras quitar espacios y convertir a mayúsculas.

| Materia | Interacciones totales | Mediana por alumno | Media de minutos estimados | Con dato de tiempo / alumnos |
| --- | --- | --- | --- | --- |
| Algoritmos | 55.494 | 137,00 | 137,53 | 319 / 319 |
| Prob. y Estadística | 78.444 | 195,00 | 263,99 | 319 / 319 |
| Álgebra | 56.456 | 156,00 | 151,52 | 319 / 319 |

### Interpretación y límites

La cobertura describe presencia de alguna interacción en el aula, no asistencia, aprendizaje o continuidad semanal.
Los minutos son estimaciones del reporte, no tiempo real cronometrado. Un usuario activo en dos materias aporta dos registros activos, pero un solo identificador al consolidado.
La deduplicación global supone que los identificadores anonimizados representan de forma consistente a la misma persona entre materias; no verifica identidad civil.

## 3. Matrícula, participación y alertas

### Observado

Se conserva el último movimiento por fecha de inscripción y número de transacción dentro de cada materia.
Aceptada se presenta como Vigente. La base completa es la unión de matrícula consolidada y alumnos del aula, con una fila por identificador.

| Materia | Fechas de movimientos | Movimientos originales | IDs en matrícula | Vigentes | Bajas | Base completa | Fuera del aula |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | 28/07/2025–30/09/2025 | 175 | 167 | 165 | 2 | 319 | 0 |
| Prob. y Estadística | 28/07/2025–30/09/2025 | 171 | 167 | 164 | 3 | 319 | 0 |
| Álgebra | 28/07/2025–30/09/2025 | 167 | 165 | 163 | 2 | 319 | 0 |

| Materia | Situación de matrícula | Con actividad | Sin actividad | Sin registro/dato | Total |
| --- | --- | --- | --- | --- | --- |
| Algoritmos | Baja | 2 | 0 | 0 | 2 |
| Algoritmos | Sin registro en matrícula | 111 | 41 | 0 | 152 |
| Algoritmos | Vigente | 163 | 2 | 0 | 165 |
| Prob. y Estadística | Baja | 3 | 0 | 0 | 3 |
| Prob. y Estadística | Sin registro en matrícula | 109 | 43 | 0 | 152 |
| Prob. y Estadística | Vigente | 161 | 3 | 0 | 164 |
| Álgebra | Baja | 2 | 0 | 0 | 2 |
| Álgebra | Sin registro en matrícula | 105 | 49 | 0 | 154 |
| Álgebra | Vigente | 161 | 2 | 0 | 163 |

| Alerta (base completa) | Algoritmos | Prob. y Estadística | Álgebra |
| --- | --- | --- | --- |
| Vigente sin actividad registrada | 2 | 3 | 2 |
| Vigente sin registro en participación | 0 | 0 | 0 |
| Vigente con actividad sin determinar | 0 | 0 | 0 |
| Actividad sin registro en matrícula | 111 | 109 | 105 |
| Actividad con baja registrada | 2 | 3 | 2 |
| Actividad con otro estado de matrícula | 0 | 0 | 0 |
| Sin alerta con estos criterios | 204 | 204 | 210 |
| Total con alerta | 115 | 115 | 109 |

| Materia | Alertas / base completa | Alertas en vigentes / vigentes |
| --- | --- | --- |
| Algoritmos | 115 / 319 (36,05 %) | 2 / 165 (1,21 %) |
| Prob. y Estadística | 115 / 319 (36,05 %) | 3 / 164 (1,83 %) |
| Álgebra | 109 / 319 (34,17 %) | 2 / 163 (1,23 %) |

### Interpretación y límites

Las alertas son cruces descriptivos y mutuamente excluyentes de las reglas actuales, no un modelo de riesgo ni una nueva condición académica.
Actividad sin registro en matrícula no significa una baja: señala falta de correspondencia entre las fuentes.
Actividad con baja registrada puede haber ocurrido antes de la baja, porque participación resume todo el período y matrícula conserva el último estado disponible.
Las fechas de movimientos de matrícula no constituyen una fecha de exportación ni acreditan que el estado siga vigente fuera de los archivos recibidos.
Sin alerta solo significa que no se cumple ninguna de estas reglas; no certifica ausencia de dificultades.

## 4. Resultados académicos y cobertura de evaluaciones

### Observado

Las condiciones porcentuales se calculan sobre los identificadores presentes en archivos de calificaciones de cada materia.
La cobertura de resultado respecto del aula usa, separadamente, alumnos del aula como denominador.
Cada estudiante aporta un solo resultado; las notas faltantes no se convierten en cero. Un cero informado sí participa.
En Probabilidad y Estadística el recuperatorio se incluye como otro instrumento con nota; no sustituye automáticamente una evaluación anterior.

| Materia | IDs en notas | Con resultado | Con resultado en aula | % del aula | IDs de notas fuera del aula | Instrumentos disponibles |
| --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | 146 | 146 | 146 | 45,77 % | 0 | 5 |
| Prob. y Estadística | 194 | 194 | 194 | 60,82 % | 0 | 9 |
| Álgebra | 196 | 196 | 196 | 61,44 % | 0 | 3 |

| Materia | Unidad del resultado observado | Media | Mediana | Mínimo | Máximo | n con resultado |
| --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | Promedio sobre 100 | 92,41 | 95,00 | 50,00 | 100,00 | 146 |
| Prob. y Estadística | Promedio sobre 100 | 87,40 | 92,86 | 0,00 | 100,00 | 194 |
| Álgebra | Puntos acumulados parciales | 30,74 | 34,33 | 3,00 | 45,00 | 196 |

| Materia | Condición | Estudiantes | % de IDs en notas | Denominador |
| --- | --- | --- | --- | --- |
| Algoritmos | Libre | 1 | 0,68 % | 146 |
| Algoritmos | Regular | 27 | 18,49 % | 146 |
| Algoritmos | Promociona | 118 | 80,82 % | 146 |
| Algoritmos | Pendiente | 0 | 0,00 % | 146 |
| Algoritmos | Sin notas informadas | 0 | 0,00 % | 146 |
| Prob. y Estadística | Libre | 10 | 5,15 % | 194 |
| Prob. y Estadística | Regular | 37 | 19,07 % | 194 |
| Prob. y Estadística | Promociona | 147 | 75,77 % | 194 |
| Prob. y Estadística | Pendiente | 0 | 0,00 % | 194 |
| Prob. y Estadística | Sin notas informadas | 0 | 0,00 % | 194 |
| Álgebra · proyectada | Libre | 5 | 2,55 % | 196 |
| Álgebra · proyectada | Regular | 24 | 12,24 % | 196 |
| Álgebra · proyectada | Promociona | 167 | 85,20 % | 196 |
| Álgebra · proyectada | Pendiente | 0 | 0,00 % | 196 |
| Álgebra · proyectada | Sin notas informadas | 0 | 0,00 % | 196 |

Criterios conservados: Probabilidad y Estadística regulariza desde 60/100 y promociona desde 85/100; Algoritmos, desde 60/100 y 90/100.
Álgebra proyecta proporcionalmente sobre 120 a partir de los puntos y del máximo de las evaluaciones con nota de cada estudiante: regular desde el equivalente a 60/120 y promoción desde 85/120.
Por ejemplo, 34/45 equivale a 90,67/120 y proyecta «Promociona».
La categoría de Álgebra es **Condición proyectada según notas informadas**, al momento de consultar, y se actualiza con nuevas calificaciones.

Álgebra dispone de 3 de los 8 instrumentos del esquema: 45/120 puntos (37,50 % del esquema). El promedio de los porcentajes individuales sobre notas informadas es 82,77 % (n=196). Este promedio de porcentajes individuales no se obtiene dividiendo la media de puntos por un máximo común cuando la cobertura difiere entre estudiantes.

#### Cobertura por instrumento

Denominador de la cobertura: IDs presentes en el conjunto de archivos de notas de la materia. Filas indica usuarios exportados en ese instrumento; notas informadas cuenta solo valores numéricos. Promedio (%) conserva la escala porcentual del instrumento.

| Materia | Instrumento | Filas | Notas informadas | Cobertura / IDs en notas | Máximo informado | Promedio (%) |
| --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | Autoevaluación - Módulo 1 | 145 | 145 | 99,32 % | 100 | 93,24 |
| Algoritmos | Autoevaluación - Unidad 2 | 106 | 106 | 72,60 % | 100 | 92,92 |
| Algoritmos | Autoevaluación - Unidad 3 | 80 | 80 | 54,79 % | 100 | 91,75 |
| Algoritmos | Autoevaluación - Unidad 4 | 64 | 64 | 43,84 % | 100 | 93,75 |
| Algoritmos | Autoevaluación - Unidad 5 | 24 | 24 | 16,44 % | 100 | 95,83 |
| Prob. y Estadística | 👉  Actividad Rápida 1 | 147 | 147 | 75,77 % | 100 | 98,87 |
| Prob. y Estadística | 👉  Actividad Rápida 2 | 137 | 137 | 70,62 % | 100 | 98,54 |
| Prob. y Estadística | 👉  Actividad Rápida 3 | 112 | 112 | 57,73 % | 100 | 91,52 |
| Prob. y Estadística | 👉  Actividad Rápida 4 | 108 | 108 | 55,67 % | 100 | 82,29 |
| Prob. y Estadística | 👉  Actividad Rápida 5 | 54 | 54 | 27,84 % | 100 | 91,98 |
| Prob. y Estadística | 🚀Evaluación Semanal Nº1 | 136 | 136 | 70,10 % | 100 | 81,43 |
| Prob. y Estadística | 🚀Evaluación Semanal Nº2 | 13 | 13 | 6,70 % | 100 | 97,44 |
| Prob. y Estadística | 🚀Recuperatorio: Evaluación Semanal Nº1 | 21 | 21 | 10,82 % | 100 | 70,11 |
| Prob. y Estadística | 🧠 PARCIAL 1 | 167 | 167 | 86,08 % | 100 | 85,54 |
| Álgebra | 1° Parcial | 162 | 162 | 82,65 % | 25 | 79,51 |
| Álgebra | AUTOEVALUACION1 | 165 | 165 | 84,18 % | 10 | 88,79 |
| Álgebra | AUTOEVALUACION2 | 152 | 152 | 77,55 % | 10 | 88,22 |

#### Instrumentos con nota por alumno del aula

Base: alumnos del aula. Cero incluye a quienes no tienen resultado en los archivos recibidos; no es una nota académica cero. Los instrumentos disponibles son los exportados, no necesariamente todos los del plan.

| Materia | Instrumentos con nota | Alumnos | % de alumnos del aula |
| --- | --- | --- | --- |
| Algoritmos | 0 | 173 | 54,23 % |
| Algoritmos | 1 | 40 | 12,54 % |
| Algoritmos | 2 | 26 | 8,15 % |
| Algoritmos | 3 | 17 | 5,33 % |
| Algoritmos | 4 | 39 | 12,23 % |
| Algoritmos | 5 | 24 | 7,52 % |
| Prob. y Estadística | 0 | 125 | 39,18 % |
| Prob. y Estadística | 1 | 27 | 8,46 % |
| Prob. y Estadística | 2 | 27 | 8,46 % |
| Prob. y Estadística | 3 | 17 | 5,33 % |
| Prob. y Estadística | 4 | 15 | 4,70 % |
| Prob. y Estadística | 5 | 12 | 3,76 % |
| Prob. y Estadística | 6 | 44 | 13,79 % |
| Prob. y Estadística | 7 | 38 | 11,91 % |
| Prob. y Estadística | 8 | 13 | 4,08 % |
| Prob. y Estadística | 9 | 1 | 0,31 % |
| Álgebra | 0 | 123 | 38,56 % |
| Álgebra | 1 | 33 | 10,34 % |
| Álgebra | 2 | 43 | 13,48 % |
| Álgebra | 3 | 120 | 37,62 % |

Máximo de las notas informadas de cada estudiante de Álgebra (base: IDs en sus archivos de notas):

| Máximo individual (puntos) | Estudiantes | % de IDs en notas |
| --- | --- | --- |
| 10 | 26 | 13,27 % |
| 20 | 8 | 4,08 % |
| 25 | 7 | 3,57 % |
| 35 | 35 | 17,86 % |
| 45 | 120 | 61,22 % |

### Interpretación y límites

Las condiciones describen notas disponibles, no acreditación administrativa final. La concentración en promoción debe leerse junto con la cobertura: quienes no figuran en notas no integran el denominador de condiciones.
Los promedios usan solo instrumentos con nota; comparar materias sin considerar instrumentos y poblaciones puede inducir a error.
En Álgebra la suma parcial y la proyección normalizada son medidas diferentes. No se promedian globalmente sus puntos con promedios sobre 100 de las otras materias.
No se imputan evaluaciones futuras, fechas de evaluación, ponderaciones adicionales ni reglas de reemplazo no presentes en los cálculos validados.

## 5. Correlaciones de participación y rendimiento

### Observado

Pearson se calcula sobre pares completos por alumno y materia, con al menos tres pares y variación en ambas variables.
Y es porcentaje sobre el máximo de las notas informadas en Álgebra y promedio observado sobre 100 en las otras dos.
X corresponde al período completo: Interacciones y Tiempo de uso (minutos) provienen de participación; Registros de trazabilidad y Días con eventos, de eventos de Alumnos.
Para estos dos indicadores de trazabilidad, la app asigna cero a alumnos sin eventos en el reporte; las calificaciones faltantes permanecen faltantes.

#### Población: Alumnos del aula

| Materia | Variable X | Población | Pares completos | Sin par | r de Pearson |
| --- | --- | --- | --- | --- | --- |
| Algoritmos | Interacciones | 319 | 146 | 173 | 0,0766 |
| Algoritmos | Tiempo de uso (minutos) | 319 | 146 | 173 | 0,0557 |
| Algoritmos | Registros de trazabilidad | 319 | 146 | 173 | 0,0582 |
| Algoritmos | Días con eventos | 319 | 146 | 173 | 0,0544 |
| Prob. y Estadística | Interacciones | 319 | 194 | 125 | 0,0560 |
| Prob. y Estadística | Tiempo de uso (minutos) | 319 | 194 | 125 | 0,0841 |
| Prob. y Estadística | Registros de trazabilidad | 319 | 194 | 125 | 0,0424 |
| Prob. y Estadística | Días con eventos | 319 | 194 | 125 | 0,1206 |
| Álgebra | Interacciones | 319 | 196 | 123 | 0,1449 |
| Álgebra | Tiempo de uso (minutos) | 319 | 196 | 123 | 0,0764 |
| Álgebra | Registros de trazabilidad | 319 | 196 | 123 | 0,1206 |
| Álgebra | Días con eventos | 319 | 196 | 123 | 0,2036 |

#### Población: Matrícula vigente

| Materia | Variable X | Población | Pares completos | Sin par | r de Pearson |
| --- | --- | --- | --- | --- | --- |
| Algoritmos | Interacciones | 165 | 107 | 58 | -0,0299 |
| Algoritmos | Tiempo de uso (minutos) | 165 | 107 | 58 | -0,0321 |
| Algoritmos | Registros de trazabilidad | 165 | 107 | 58 | -0,0535 |
| Algoritmos | Días con eventos | 165 | 107 | 58 | -0,0385 |
| Prob. y Estadística | Interacciones | 164 | 142 | 22 | 0,0628 |
| Prob. y Estadística | Tiempo de uso (minutos) | 164 | 142 | 22 | 0,0689 |
| Prob. y Estadística | Registros de trazabilidad | 164 | 142 | 22 | 0,0426 |
| Prob. y Estadística | Días con eventos | 164 | 142 | 22 | 0,1388 |
| Álgebra | Interacciones | 163 | 142 | 21 | 0,1572 |
| Álgebra | Tiempo de uso (minutos) | 163 | 142 | 21 | 0,1051 |
| Álgebra | Registros de trazabilidad | 163 | 142 | 21 | 0,1206 |
| Álgebra | Días con eventos | 163 | 142 | 21 | 0,2043 |

La base completa coincide en identificadores con alumnos del aula en las tres materias; sus correlaciones coinciden.

En alumnos del aula, los coeficientes observados abarcan de 0,0424 a 0,2036.

Mayor magnitud absoluta en Alumnos del aula: Álgebra, Días con eventos, r=0,2036, n=196 pares.

Mayor magnitud absoluta en Matrícula vigente: Álgebra, Días con eventos, r=0,2043, n=142 pares.

### Interpretación y límites

Son asociaciones descriptivas. No permiten concluir que más actividad cause mejores notas, ni que una intervención cambie el rendimiento.
La exclusión de alumnos sin calificaciones condiciona los pares disponibles; las asociaciones no representan automáticamente a todos los matriculados.
Interacciones, minutos, eventos y días son variables diferentes. Los coeficientes dependen de la población, la cobertura, valores extremos y el carácter acumulado de las medidas.
No se realizaron pruebas de significación ni se estimaron intervalos de confianza, ajustes por confusores o modelos predictivos.
La ausencia de eventos antes del inicio efectivo de los registros limita cualquier lectura longitudinal.

## 6. Patrones temporales de trazabilidad

### Observado

Se incluyen todos los eventos del perfil Alumnos, normalizando espacios en Acción; se conservan repeticiones.
Accesos a secciones cuenta únicamente Acción = Acceder y no equivale a sesiones.
El reporte completo incluye otros perfiles y se informa por separado.

| Materia | Eventos todos los perfiles | Eventos Alumnos | Alumnos con eventos | Acceder | Repeticiones adicionales | % de eventos Alumnos | Primer–último día | Días con eventos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Algoritmos | 45.951 | 44.543 | 276 | 17.892 | 171 | 0,38 % | 05/08/2025–24/10/2025 | 81 |
| Prob. y Estadística | 68.136 | 63.578 | 273 | 24.391 | 285 | 0,45 % | 05/08/2025–24/10/2025 | 81 |
| Álgebra | 45.717 | 41.983 | 268 | 18.824 | 190 | 0,45 % | 05/08/2025–24/10/2025 | 81 |

| Materia | Días declarados | Días primer–último evento | Eventos/día declarado | Eventos/día del intervalo observado | Días iniciales sin registros |
| --- | --- | --- | --- | --- | --- |
| Algoritmos | 177 | 81 | 251,66 | 549,91 | 96 |
| Prob. y Estadística | 177 | 81 | 359,20 | 784,91 | 96 |
| Álgebra | 177 | 81 | 237,19 | 518,31 | 96 |

El indicador diario de Trazabilidad usa el intervalo observado seleccionado, inclusive. La tendencia de General completa con cero los días del período declarado sin eventos; esos ceros describen el archivo, no prueban ausencia de actividad educativa en días no registrados.

**Concentraciones observadas.** Los siguientes porcentajes usan el total de eventos de Alumnos de cada materia:

- Algoritmos: mayor acumulado mensual en 2025-08, 26.958 eventos (60,52 %); mayor concentración semanal en Martes, 16.895 (37,93 %); hora con más registros 20:00–20:59, 5.857 (13,15 %).

- Prob. y Estadística: mayor acumulado mensual en 2025-09, 27.707 eventos (43,58 %); mayor concentración semanal en Miércoles, 19.082 (30,01 %); hora con más registros 20:00–20:59, 8.851 (13,92 %).

- Álgebra: mayor acumulado mensual en 2025-08, 20.603 eventos (49,07 %); mayor concentración semanal en Lunes, 12.499 (29,77 %); hora con más registros 20:00–20:59, 6.194 (14,75 %).

#### Distribución mensual

Agosto y octubre son intervalos parciales del registro observado; los totales mensuales no ajustan por cantidad de días.

| Materia | Mes | Eventos Alumnos | % de eventos de la materia | Acceder |
| --- | --- | --- | --- | --- |
| Algoritmos | 2025-08 | 26.958 | 60,52 % | 10.231 |
| Algoritmos | 2025-09 | 11.712 | 26,29 % | 5.085 |
| Algoritmos | 2025-10 | 5.873 | 13,19 % | 2.576 |
| Prob. y Estadística | 2025-08 | 25.763 | 40,52 % | 9.218 |
| Prob. y Estadística | 2025-09 | 27.707 | 43,58 % | 10.697 |
| Prob. y Estadística | 2025-10 | 10.108 | 15,90 % | 4.476 |
| Álgebra | 2025-08 | 20.603 | 49,07 % | 9.140 |
| Álgebra | 2025-09 | 12.731 | 30,32 % | 6.032 |
| Álgebra | 2025-10 | 8.649 | 20,60 % | 3.652 |

#### Picos diarios y semanales

Se informa el máximo observado, conservando empates. Semana comienza el lunes; las semanas inicial y final pueden ser parciales.

| Materia | Medida | Día / inicio de semana | Eventos del pico | % del total de esa medida |
| --- | --- | --- | --- | --- |
| Algoritmos | Todos los eventos diarios | 05/08/2025 | 6.123 | 13,75 % |
| Algoritmos | Acceder por día | 05/08/2025 | 1.820 | 10,17 % |
| Algoritmos | Todos los eventos semanales | 04/08/2025 | 11.830 | 26,56 % |
| Prob. y Estadística | Todos los eventos diarios | 06/08/2025 | 5.097 | 8,02 % |
| Prob. y Estadística | Acceder por día | 06/08/2025 | 1.768 | 7,25 % |
| Prob. y Estadística | Todos los eventos semanales | 22/09/2025 | 13.812 | 21,72 % |
| Álgebra | Todos los eventos diarios | 11/08/2025 | 2.759 | 6,57 % |
| Álgebra | Acceder por día | 11/08/2025 | 1.275 | 6,77 % |
| Álgebra | Todos los eventos semanales | 18/08/2025 | 7.596 | 18,09 % |

#### Día de semana y franjas horarias

El denominador de cada porcentaje es el total de eventos de Alumnos de la materia, no alumnos únicos ni sesiones.

| Día de semana | Algoritmos | Prob. y Estadística | Álgebra |
| --- | --- | --- | --- |
| Lunes | 6603 (14,82 %) | 6416 (10,09 %) | 12499 (29,77 %) |
| Martes | 16895 (37,93 %) | 8584 (13,50 %) | 7606 (18,12 %) |
| Miércoles | 6652 (14,93 %) | 19082 (30,01 %) | 4911 (11,70 %) |
| Jueves | 3863 (8,67 %) | 8633 (13,58 %) | 4264 (10,16 %) |
| Viernes | 3856 (8,66 %) | 6792 (10,68 %) | 5614 (13,37 %) |
| Sábado | 3344 (7,51 %) | 6772 (10,65 %) | 4518 (10,76 %) |
| Domingo | 3330 (7,48 %) | 7299 (11,48 %) | 2571 (6,12 %) |

| Materia | Tres horas con más eventos (hora del archivo) | Eventos | % del total |
| --- | --- | --- | --- |
| Algoritmos | 20:00–20:59 | 5.857 | 13,15 % |
| Algoritmos | 18:00–18:59 | 5.015 | 11,26 % |
| Algoritmos | 19:00–19:59 | 4.337 | 9,74 % |
| Prob. y Estadística | 20:00–20:59 | 8.851 | 13,92 % |
| Prob. y Estadística | 19:00–19:59 | 6.122 | 9,63 % |
| Prob. y Estadística | 18:00–18:59 | 4.407 | 6,93 % |
| Álgebra | 20:00–20:59 | 6.194 | 14,75 % |
| Álgebra | 19:00–19:59 | 4.060 | 9,67 % |
| Álgebra | 18:00–18:59 | 3.962 | 9,44 % |

#### Acciones más frecuentes

| Materia | Tres acciones con más eventos | Eventos | % del total |
| --- | --- | --- | --- |
| Algoritmos | Acceder | 17.892 | 40,17 % |
| Algoritmos | Ver texto | 17.625 | 39,57 % |
| Algoritmos | Ver tema | 2.152 | 4,83 % |
| Prob. y Estadística | Acceder | 24.391 | 38,36 % |
| Prob. y Estadística | Ver texto | 13.244 | 20,83 % |
| Prob. y Estadística | Ver archivo | 9.564 | 15,04 % |
| Álgebra | Acceder | 18.824 | 44,84 % |
| Álgebra | Ver texto | 8.040 | 19,15 % |
| Álgebra | Ver archivo | 3.329 | 7,93 % |

### Interpretación y límites

Los picos identifican concentración de registros de uso del LMS. Sin fechas verificadas de evaluaciones o calendario de clases no se atribuyen a exámenes, entregas o estrategias docentes.
Los eventos de acceso no son sesiones y varias acciones pueden proceder de una misma interacción o estudiante. Las repeticiones exactas adicionales se señalan y se conservan, como en los dashboards.
La hora es la registrada en el archivo; no se documenta una zona horaria que permita convertirla de manera fundada.
Las diferencias entre materias pueden reflejar estructura del aula, tipo de acción registrada, volumen y cobertura de notas, además de comportamientos de uso.
La falta de eventos en el inicio del período declarado es una limitación de observación y no evidencia de abandono.

## 7. Alcance del resumen

Este archivo separa cantidades observadas e interpretación para servir de insumo al informe. No modifica las siete vistas, las poblaciones ni los criterios académicos.
Los datos constituyen una fotografía de los archivos exportados, no una comprobación administrativa o académica en tiempo real.
El estado de matrícula, actividad acumulada y resultados parciales provienen de fuentes distintas; ninguna de estas medidas por sí sola determina permanencia, aprobación definitiva o causalidad.
