# Shared Understanding: Sistema de Gestión del Seminario Bíblico Nicaragüense

## 0. Cómo usar este documento

Este documento es la referencia de las **reglas del juego y la lógica del negocio** para quien construya el sistema (Claude, CLAUDE.md y subagentes).

- Cada regla lleva un ID (ej. `COB-03`) para poder citarla en planes, historias y código.
- Estados:
  - **[CONFIRMADO]**: validado con el negocio. Se implementa tal cual.
  - **[PROPUESTA]**: planteada durante el descubrimiento, no validada. No implementar como regla firme.
  - **[PENDIENTE]**: se desconoce la respuesta. Ver sección 10. No asumir nada.
- **Nada de valores fijos en el código.** Todo monto, plazo, título, firma o umbral marcado como *configurable* vive en el módulo de configuración (sección 9).
- Si una tarea toca algo marcado [PENDIENTE], detenerse y preguntar en lugar de inventar la regla.

---

## 1. Contexto

El Seminario Bíblico Nicaragüense tiene más de 60 años de existencia y se dedica a la formación teológica a través de varios programas. El proyecto es un **sistema de gestión y control** con tres áreas:

1. **Admisión y cobranza**
2. **Registro académico**
3. **Biblioteca**

### Programas

| Programa | Tipo | Dónde se imparte | Unidad académica |
|---|---|---|---|
| Bachillerato | Sabatino presencial | Seminario | Materia (1 trimestre) |
| Profesorado | Sabatino presencial | Seminario | Materia (1 trimestre) |
| Licenciatura en Teología | Sabatino presencial | Seminario | Materia (1 trimestre) |
| Diplomado por Extensión | Por módulos | Instalaciones de la institución solicitante (iglesia, seminario, escuela teológica independiente, etc.) | Módulo |

En adelante, "**presenciales**" son Bachillerato, Profesorado y Licenciatura.

## 2. Alcance

**Dentro:** control de alumnos, instituciones, cobros y pagos, pensums, inscripción, notas, certificados, promociones y biblioteca.

**Fuera (decisiones tomadas):**
- **No es un sistema de facturación.** El recibo oficial de caja se sigue haciendo **a mano** por razones de infraestructura, logística y legales. El sistema solo **registra y controla** (ver `COB-17`).
- El aviso a los alumnos de que se abrió la inscripción se hace **fuera del sistema** (WhatsApp u otro medio).
- El cupo mínimo para abrir una materia es un asunto administrativo, **no se modela**.
- Los archivos de libros digitales se gestionan en **Notion**. El sistema solo guarda enlaces.
- El presidente del seminario **no tiene rol** en el sistema (ver `COB-12`).

## 3. Actores y roles

El acceso se maneja con **roles y permisos**. **Persona y rol son conceptos separados**: una misma persona puede tener varios (un alumno de licenciatura puede ser maestro de un diplomado).

| Rol | Qué hace |
|---|---|
| **Administrador** | Configura el sistema (sección 9). Crea usuarios de cualquier rol, reasigna roles, restablece contraseñas. **No participa en lo operativo.** |
| **Admisión y cobranza** | Un solo rol. Registra alumnos e instituciones, gestiona cobros, pagos, becas y recibos. Aprueba o cancela préstamos de biblioteca y recibe devoluciones. Puede crear solo usuarios de **alumno**. |
| **Registro académico** | Tiene su propio rol y un **coordinador**. Gestiona pensums, calendario, horarios, inscripciones, notas, certificados y promociones. También aprueba préstamos y recibe devoluciones. Junto al administrador, **crea o designa maestros**. |
| **Maestro** | Registra notas de los alumnos de sus materias o módulos. |
| **Alumno** | Se inscribe a materias, consulta sus notas, solicita préstamos de libros. |

- **Biblioteca no tiene rol propio.** Admisión y registro asumen su gestión (`BIB-02`).
- La **institución no tiene usuario**. Tiene un **correo de contacto** para recibir notificaciones.
- **Nadie se auto-registra.** El seminario crea el usuario de **todos** los alumnos (presenciales y de diplomado) y el sistema les envía su acceso para que completen su perfil.

## 4. Glosario

| Término | Definición acordada |
|---|---|
| **Alumno** | Persona natural inscrita en un programa. Una ficha por alumno. |
| **Institución** | Iglesia, seminario o escuela teológica que contrata un diplomado por extensión. Entidad distinta del alumno. |
| **Vínculo** | Asociación de un alumno a una institución. |
| **Paga la institución** | Marca que indica que el cobro de ese alumno lo asume la institución. El vínculo por sí solo **no** implica que pague. |
| **Matrícula** | Pago **anual** de los programas presenciales, equivalente a un mes de arancel. También se llamó "carga impositiva". No aplica al diplomado. |
| **Arancel / mensualidad** | Cuota mensual de los presenciales. Varía por programa. |
| **Trimestre** | Período académico de tres meses calendario. Hay 4 por año. Una materia dura un trimestre. |
| **Materia** | Unidad académica de los presenciales. |
| **Módulo** | Unidad académica del diplomado. Puede tener 1, 2 o 4 encuentros según sus horas. |
| **Materia individual** | Caso en que un alumno cursa **una sola** materia en el trimestre. Se cobra con tarifa propia. |
| **Mora** | Estado del alumno con **un mes completo sin pagar**. Para instituciones, ver `COB-14`. |
| **Solvente** | Alumno sin mora. |
| **Beca** | Descuento porcentual variable autorizado por el presidente. |
| **Certificado de notas** | Documento PDF con la tabla de notas del alumno, impreso en papel membretado y sellado. Se paga. |
| **Certificación / promoción** | Acto en que el seminario otorga un título (bachiller, profesor, licenciado, etc.) a un grupo de alumnos. **No confundir con certificado de notas.** |
| **Diploma** | Documento que se otorga al concluir un diplomado. |
| **Pensum** | Plan de materias de un programa, con sus relaciones de dependencia. |
| **Prerrequisito** | Materia que debe estar **aprobada** para poder inscribir otra. |
| **Recibo oficial de caja** | Comprobante manual con número único. El sistema solo registra su número, fecha y concepto. |
| **Alumno activo** | Alumno vigente en el sistema. Es el universo desde el que se elige quién se promociona. |

## 5. Modelo conceptual

- **Persona**: datos básicos. Puede tener varios roles (alumno, maestro, etc.).
- **Alumno / ficha**: hoja de matrícula (formato único para todos los programas + anexo específico por programa), soportes escaneados, becas, pagos, recibos, certificados emitidos, notas y observaciones.
- **Institución**: datos de contacto, correo, convenio y carta de solicitud adjuntos.
- **Programa → Pensum → Materia/Módulo**, con relaciones de prerrequisito.
- **Trimestre**: calendario, distribución de materias, horarios y maestros asignados.
- **Inscripción**: alumno + materia/módulo + trimestre.
- **Cobro / Pago / Recibo**: un pago se asocia a un concepto y a un número de recibo único.
- **Recurso de biblioteca**: físico (con copias) o digital (con enlace). **Préstamo** con **cola**.

---

## 6. Admisión y cobranza

### 6.1 Admisión

- **ADM-01 [CONFIRMADO]** Cada alumno tiene una **ficha** digital que reemplaza a la hoja de matrícula impresa. El formato es el mismo para todos los programas, con información adicional específica de cada programa.
- **ADM-02 [CONFIRMADO]** Se debe poder **adjuntar el documento físico escaneado** como soporte.
- **ADM-03 [CONFIRMADO]** Requisitos de los presenciales: fotocopia del **diploma de bachiller**, **cédula** y **carta firmada del pastor**.
- **ADM-04 [CONFIRMADO]** Requisitos del diplomado: **cédula** y **carta del pastor**. **No** se exige diploma de bachiller por el nivel académico del programa.
- **ADM-05 [CONFIRMADO]** Para el diplomado, la **institución** aporta un **convenio** y una **carta de solicitud**, adjuntos a su registro.
- **ADM-06 [CONFIRMADO]** El vínculo alumno–institución y la marca "paga la institución" los define la responsable de admisiones o de administración.
- **ADM-07 [CONFIRMADO]** Toda inscripción se registra desde el seminario. El sistema crea el usuario del alumno y le envía el acceso para completar su perfil.

### 6.2 Quién paga (regla central)

- **COB-01 [CONFIRMADO]** Si el alumno está vinculado a una institución **y** marcado "paga la institución", cobra la institución.
- **COB-02 [CONFIRMADO]** En cualquier otro caso (sin vínculo, o vinculado pero no marcado), el alumno paga directamente al seminario.
- **COB-03 [CONFIRMADO]** Una institución, iglesia o misión puede **patrocinar** a alumnos, incluso de los presenciales. Es el mismo mecanismo de vínculo.
- **COB-04 [PROPUESTA]** La marca "paga la institución" debería vivir en la **inscripción** y no en la persona, por si el arreglo cambia por programa. Es decisión de diseño.

### 6.3 Presenciales

- **COB-05 [CONFIRMADO]** **Matrícula anual**: se paga una vez al año, al inicio, **completa**, sin importar cuánto estudie el alumno. Equivale a un mes de arancel.
- **COB-06 [CONFIRMADO]** El año de la matrícula coincide con el año académico (en 2026 paga matrícula y los meses estudiados, en 2027 vuelve a pagarla).
- **COB-07 [CONFIRMADO]** **Mensualidad**: cubre una materia que dura un trimestre. Se paga mes a mes. Vence en los **primeros 5 días** del mes. El monto varía por programa (configurable).
- **COB-08 [CONFIRMADO]** Si el alumno **no inscribe materias** en un trimestre, **no se cobra** ese trimestre. No se exige baja formal. El cobro se deriva del registro académico.
- **COB-09 [CONFIRMADO]** **Materia individual**: si el alumno inscribe **una sola** materia, el sistema lo detecta y **notifica a administración**, que aprueba manualmente el cobro como materia individual. La tarifa es **fija y la misma para los tres programas** (configurable).
- **COB-10 [PROPUESTA]** El sistema solo admite pagar por adelantado **hasta el trimestre en curso**, para evitar reversiones si el alumno se retira. El propio usuario la marcó como discutible.
- **COB-11 [CONFIRMADO]** Un trimestre acortado **siempre cobra los tres meses** (ver `REG-14`).

### 6.4 Becas

- **COB-12 [CONFIRMADO]** Solo el **presidente** autoriza becas, pero no tiene rol en el sistema. Quien registra la beca (administración) **debe adjuntar el soporte de la autorización**. Hasta ahí llega el control del sistema.
- **COB-13 [CONFIRMADO]** La beca es un **porcentaje variable** (10 %, 20 %, 50 %, 100 %, etc.), vale **todo el año** y aplica a las **mensualidades**.
- **COB-13b [PENDIENTE]** Si cubre también la matrícula y los gastos de promoción (ver sección 10).

### 6.5 Diplomado por Extensión

- **COB-14 [CONFIRMADO]** Se cobra **por módulo completo**: **$150 por módulo** a la institución, sin importar cuántos alumnos tenga (configurable). **No hay matrícula anual.**
- **COB-15 [CONFIRMADO]** Excepción: si un alumno tiene arreglo particular con el seminario, paga **$10** directamente (configurable).
- **COB-16 [CONFIRMADO]** La **institución** entra en mora **un mes después del vencimiento del módulo**. De momento esto **no tiene consecuencias**, solo notificación al correo de contacto. Los **alumnos de una institución morosa no se bloquean**.

### 6.6 Pagos, recibos y otros cobros

- **COB-17 [CONFIRMADO]** Cada pago registrado exige: **número de recibo oficial**, **fecha** y **concepto**. El número es **único**, propio del recibo.
- **COB-18 [CONFIRMADO]** El recibo puede **anularse**. Si el pago sí se realizó, se emite **uno nuevo que lo reemplaza**, y el recibo anulado **se conserva** en el sistema. No se adjunta copia escaneada del recibo.
- **COB-19 [CONFIRMADO]** Además de matrícula y mensualidades se registran con trazabilidad: **certificados de notas** y **gastos de graduación (promoción)**.
- **COB-20 [CONFIRMADO]** Administración tiene una **vista de alumnos con pagos pendientes**.

### 6.7 Mora

- **MOR-01 [CONFIRMADO]** Un alumno entra en mora al completar **un mes sin pagar**.
- **MOR-02 [CONFIRMADO]** No hay recargo económico.
- **MOR-03 [CONFIRMADO]** La mora **bloquea la consulta en línea de notas y el acceso a biblioteca**. **No** bloquea la emisión de certificados (el alumno puede pagar por esa vía individualmente).

---

## 7. Registro académico

### 7.1 Pensum y calendario

- **REG-01 [CONFIRMADO]** Registro administra el **pensum de cada programa** y las **relaciones de prerrequisito** entre materias.
- **REG-02 [CONFIRMADO]** El **prerrequisito exige materia aprobada** (no basta con cursada). Ejemplo: no se cursa Exégesis de Romanos sin aprobar Principios de Exégesis.
- **REG-03 [CONFIRMADO]** **No hay convalidaciones** hoy. Si existieran, registro las incluye en las notas del alumno con una **nota explicativa**.
- **REG-04 [CONFIRMADO]** Registro define el **calendario**: 4 trimestres al año y sus fechas.
- **REG-05 [CONFIRMADO]** Cada trimestre registro genera la **distribución de materias y el horario** de los presenciales, y la **distribución de maestros** de los módulos de diplomado.
- **REG-06 [CONFIRMADO]** Los diplomados tienen periodicidad distinta: **1, 2 o 4 encuentros** por módulo para cubrir sus horas.
- **REG-07 [CONFIRMADO]** Los **maestros** los crean o designan el administrador y el coordinador de registro. Un maestro puede ser también alumno.

### 7.2 Inscripción

- **REG-08 [CONFIRMADO]** El alumno se inscribe **desde el sistema** a las materias disponibles del trimestre, dentro de una **fecha habilitada**. Se le avisa fuera del sistema.
- **REG-09 [CONFIRMADO]** Registro académico **puede inscribir por el alumno** (por ejemplo, quien tiene poco acceso a tecnología).
- **REG-10 [CONFIRMADO]** El sistema **valida los prerrequisitos** y la disponibilidad antes de permitir la inscripción.
- **REG-11 [CONFIRMADO]** El sistema **impide inscribir dos materias en el mismo horario**.
- **REG-12 [CONFIRMADO]** Si inscribe una sola materia, se dispara el aviso de materia individual (`COB-09`).

### 7.3 Trimestre recortado

- **REG-13 [CONFIRMADO]** Si un trimestre pierde días (feriados, fuerza mayor), se ofrecen **menos materias** (por ejemplo 2 en lugar de 3) y se alargan los plazos.
- **REG-14 [CONFIRMADO]** Se mantienen las **horas clase**, pero los **bloques son más largos** (de 1.5 h a unas 2–2.5 h). El trimestre sigue abarcando tres meses y **se cobran los tres**. Ejemplo: el cuarto trimestre de 2026 va del 17 de octubre al primer sábado de diciembre y cobra octubre, noviembre y diciembre. Lo gestiona registro académico.

### 7.4 Notas

- **REG-15 [CONFIRMADO]** Escala de **0 a 100**. La **nota mínima de aprobación es configurable por programa**.
- **REG-16 [CONFIRMADO]** El **maestro registra** las notas de sus alumnos dentro de una **ventana configurable** (por defecto **20 días** tras concluir la materia).
- **REG-17 [CONFIRMADO]** La ventana **no cierra sola**. Si vence sin notas, el sistema **notifica al maestro y a registro**.
- **REG-18 [CONFIRMADO]** Cuando el maestro **cierra el módulo/materia**, **ya no puede editar**. Si hay un error u olvido, **solo registro corrige**, con **justificación obligatoria**, sin deshacer el cierre del maestro.
- **REG-19 [CONFIRMADO]** **Reprobar**: el alumno debe **repetir** la materia. No hay cobro adicional ni examen de rescate. La vuelve a inscribir cuando se abra, si no choca con otras. Si choca, prioriza.
- **REG-20 [CONFIRMADO]** Registro puede **ver las notas de cualquier alumno en cualquier momento**.
- **REG-21 [CONFIRMADO]** El **alumno** ve sus notas de materias ya cursadas (**aprobadas y reprobadas**) y las materias **en curso** señalizadas o agrupadas aparte. Esta consulta se bloquea por mora (`MOR-03`).

### 7.5 Certificado de notas

- **REG-22 [CONFIRMADO]** Es un **PDF** con la tabla de todas las notas, pensado para imprimirse en **papel membretado** y sellarse. Las **firmas que lleva son configurables**.
- **REG-23 [CONFIRMADO]** **Ver notas y emitir certificado son acciones distintas.** Ver notas nunca requiere pago.
- **REG-24 [CONFIRMADO]** El proceso suele iniciar con el **pago del arancel del certificado** en admisión. Al generar el certificado, el sistema **pregunta si corresponde al pago activo** del alumno. Si es así, el PDF se **almacena y queda vinculado a ese pago y a su recibo**.
- **REG-25 [CONFIRMADO]** En la ficha del alumno se ve el pago, su recibo y el certificado emitido, y administración puede **descargarlo e imprimirlo**.
- **REG-26 [CONFIRMADO]** Se puede emitir un certificado **sin pago activo** solo por **reimpresión** o **uso interno**. No existe exoneración. Estas emisiones deben dejar **motivo registrado** (el motivo es una recomendación de diseño).

### 7.6 Promoción y diploma

- **REG-27 [CONFIRMADO]** Registro tiene una pantalla para **registrar una promoción** (por ejemplo, de bachillerato): elige, entre los alumnos **activos**, quiénes se promocionan.
- **REG-28 [CONFIRMADO]** El sistema **valida** que cada alumno tenga **todas las materias aprobadas, solvencia y gastos de graduación pagados**.
- **REG-29 [CONFIRMADO]** El **título que recibe cada programa es configurable** (no se fija en código).
- **REG-30 [CONFIRMADO]** La promoción guarda el **registro de certificación** y deja una **nota en la ficha de cada alumno** con el título recibido.
- **REG-31 [CONFIRMADO]** Los alumnos de diplomado reciben un **diploma** al terminar. Notas y certificados funcionan igual que en los presenciales. El flujo detallado del diploma no se ha definido.

---

## 8. Biblioteca

- **BIB-01 [CONFIRMADO]** Biblioteca maneja dos tipos de recurso: **digitales** (hoy en Notion) y **físicos** (hoy en Excel). Cada recurso tiene una **ficha**.
- **BIB-02 [CONFIRMADO]** Admisión y registro asumen la gestión de la biblioteca. No hay rol propio.
- **BIB-03 [CONFIRMADO]** Ficha física: **una sola ficha por título** con su **número de copias**. Campos actuales: **título, autor, n.° de copias, código, n.° de vitrina**.
- **BIB-04 [CONFIRMADO]** Libros digitales: el sistema guarda el **enlace** (lectura en línea o descarga). Los archivos **se gestionan en Notion** y el catálogo digital **se sincroniza desde Notion**.
- **BIB-05 [CONFIRMADO]** Se necesita un **índice centralizado y buscable** para que los alumnos encuentren recursos. Se mencionó Algolia como idea. **La herramienta no está decidida** (decisión técnica posterior).
- **BIB-06 [CONFIRMADO]** Puede pedir préstamo **cualquier alumno o maestro**.
- **BIB-07 [CONFIRMADO]** Flujo: el alumno **solicita** desde el sistema, admisión o registro **aprueba**, y al devolver, admisión o registro **marcan la recepción** y se cierra el préstamo.
- **BIB-08 [CONFIRMADO]** **Cola**: si todas las copias están prestadas, el solicitante entra a una cola. Al devolverse, se **notifica al siguiente**. **No se puede aprobar un préstamo saltándose el orden.**
- **BIB-09 [CONFIRMADO]** El siguiente en cola tiene **una semana** desde la devolución para retirar el libro.
- **BIB-10 [CONFIRMADO]** La solicitud la pueden **cancelar el alumno, admisión o registro**.
- **BIB-11 [CONFIRMADO]** **No devolución**: se bloquean nuevos préstamos y el alumno debe **reponer el libro**. **Administración** da la sanción por saldada. Mientras no se salde, no puede pedir otro.
- **BIB-12 [CONFIRMADO]** **Mora de pago**: el alumno **conserva** los libros que ya tiene. Si está en cola, **conserva su lugar**, se le notifica que los préstamos dependen de estar solvente y **no se le aprueba** hasta ponerse al día. Si llega su turno y sigue en mora, **pierde el turno**. No se le saca antes de tiempo, por si paga a tiempo.

---

## 9. Configuración (módulo del Administrador)

Nada de esto va fijo en el código:

- Arancel mensual **por programa**
- Matrícula anual (equivale a un mes de arancel, ver pendiente 8)
- Tarifa de materia individual (única para los tres programas)
- Precio del módulo de diplomado ($150) y monto del alumno con arreglo particular ($10)
- Arancel del certificado de notas y monto de gastos de graduación
- Nota mínima de aprobación **por programa**
- Ventana de registro de notas (20 días)
- Firmas que lleva el certificado de notas
- Títulos que otorga cada programa
- Calendario trimestral y fecha de inscripción
- Parámetros de biblioteca (plazo de retiro, y los que defina el negocio: plazo de préstamo, máximo de libros)

## 10. Pendientes con el negocio

★ = bloquea el diseño.

**Biblioteca**
1. ★ **Plazo de préstamo**, si se renueva y **máximo de libros a la vez**. *(Esperando información del seminario.)*
2. **Sanción por pérdida**: ¿se repone el mismo libro o se acepta su valor en dinero?
3. **Mora y biblioteca digital**: ¿el bloqueo por mora incluye el acceso a los enlaces digitales o solo los préstamos físicos?

**Cobranza**
4. **Beca**: ¿cubre matrícula y gastos de promoción? *(Probablemente sí, por confirmar.)*
5. **Mora**: ¿desde qué fecha se cuenta el mes (desde el día 5, desde el último pago)?
6. **Pago anticipado**: ¿se confirma el límite del trimestre en curso? (`COB-10`)
7. **Marca "paga la institución"**: ¿a nivel de inscripción o de alumno? (`COB-04`)
8. **Matrícula**: ¿se calcula automáticamente como un mes de arancel o es un monto independiente?

**Registro académico y transversales**
9. **Diploma del diplomado**: ¿cómo se emite y qué requisitos tiene?
10. **Notificaciones del sistema**: ¿por qué canal (correo, WhatsApp, dentro del sistema)? Hoy los avisos de inscripción se hacen fuera del sistema.
11. **Recibo anulado**: ¿se registra el motivo?

**Infraestructura** (ver sección 12)
12. **Base de datos**: ¿qué motores trae el VPS (MariaDB/MySQL, PostgreSQL)? Se prefiere PostgreSQL, pero no es obligatorio.
13. **Dominio**: ¿subdominio dedicado (recomendado) o raíz?

## 11. Historial de aclaraciones

- "Carga impositiva" = otra forma de nombrar la matrícula anual (resuelto).
- La creación de usuarios por parte del seminario aplica a **todos** los programas, no solo al diplomado.
- Ver notas y emitir certificado son acciones independientes; solo la emisión se asocia a un pago.
- En trimestres recortados se mantienen las horas clase, no la duración de los bloques.

---

## 12. Decisiones técnicas

Estas decisiones no cambian las reglas de negocio. Fijan el terreno donde se construye el sistema.

- **TEC-01 [CONFIRMADO]** **Framework: Django 5.2 (LTS)**, arquitectura de **monolito** con una app por área (admisión y cobranza, registro académico, biblioteca) más un módulo de configuración. Se eligió por traer autenticación, roles y permisos, panel de administración (útil para la sección 9), ORM con migraciones y buen soporte para PDFs, auditoría y tareas programadas.
- **TEC-02 [CONFIRMADO]** **Alojamiento: VPS con panel Webuzo.** La app corre con **gunicorn** en un puerto interno (30000) y se publica desde el *Application Manager* de Webuzo (tipo Python 3, entorno *Production*). Las variables sensibles (`SECRET_KEY`, base de datos, `DEBUG=False`) van como **variables de entorno**, nunca en el repositorio.
- **TEC-03 [CONFIRMADO]** **Python 3.11.3** instalado en el VPS (`/usr/local/apps/python3/bin/python3`), compatible con Django 5.2. Se usa un **entorno virtual** por proyecto.
- **TEC-04 [CONFIRMADO]** Los archivos estáticos y los **adjuntos** (soportes escaneados, certificados emitidos) se sirven **fuera de Django** y se almacenan como archivos, no dentro de la base de datos. Se deben incluir en los respaldos.
- **TEC-05 [CONFIRMADO]** Los procesos programados (avisos de mora, ventanas de notas vencidas, notificaciones de cola) se ejecutan con **cron** del VPS.
- **TEC-06 [PROPUESTA]** Generación de PDF (certificado de notas) con una librería que **no** dependa de paquetes del sistema (por ejemplo ReportLab), salvo que se decida instalar dependencias en el VPS.
- **TEC-07 [PROPUESTA]** **Auditoría** (historial de cambios) en notas, recibos, becas y certificados, por exigirlo las reglas `REG-18`, `COB-18` y `REG-26`.
- **TEC-08 [PENDIENTE]** Base de datos y dominio (ver pendientes 12 y 13). El índice de búsqueda de biblioteca (`BIB-05`) sigue **sin decidir**.
- **TEC-09 [PENDIENTE]** **Respaldos**: frecuencia, ubicación y responsable (base de datos y adjuntos). Definirlos antes de salir a producción.
- **TEC-10 [CONFIRMADO]** Alternativa descartada por ahora: **Laravel**. Solo se retomaría si Django no se pudiera desplegar en el VPS.
