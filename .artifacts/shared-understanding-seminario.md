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
- El modelo de datos derivado de este documento está en `.artifacts/modelo-datos-inicial.md`. Si se contradicen, manda este documento.

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
- Los libros digitales viven por completo en **Notion**. El sistema **no guarda nada digital**, ni archivos ni enlaces (ver `BIB-04`). Su paso al índice de búsqueda es una automatización externa.
- El presidente del seminario **no tiene rol** en el sistema (ver `COB-12`).
- La **creación de cuentas de correo** para los alumnos que no tienen se hace fuera del sistema (ver `ACC-06`).
- Las **horas clase** no se registran ni se validan. Las gobierna registro al armar horarios y encuentros.

## 3. Actores y roles

El acceso se maneja con **roles y permisos**. **Persona y rol son conceptos separados**: una misma persona puede tener varios (un alumno de licenciatura puede ser maestro de un diplomado).

| Rol | Qué hace |
|---|---|
| **Administrador** | Actúa **a nivel de sistema**: configura el sistema (sección 9), crea usuarios de cualquier rol (incluidos maestros), reasigna roles, restablece contraseñas. **No participa en lo operativo.** Es el **superusuario** del sistema, no un grupo de permisos aparte. |
| **Admisión y cobranza** | Un solo rol. Registra alumnos e instituciones, gestiona cobros, pagos, becas y recibos. Aprueba o cancela préstamos de biblioteca y recibe devoluciones. Puede crear solo usuarios de **alumno**. |
| **Registro académico** | **Un solo rol**: todo usuario de registro es coordinador y tiene todas sus funciones. Gestiona pensums, calendario, horarios, inscripciones, notas, certificados y promociones. También aprueba préstamos y recibe devoluciones. Junto al administrador, **crea o designa maestros**. |
| **Maestro** | Registra notas de los alumnos de sus materias o módulos. |
| **Alumno** | Se inscribe a materias, consulta sus notas, solicita préstamos de libros. |

- **Biblioteca no tiene rol propio.** Admisión y registro asumen su gestión (`BIB-02`).
- **"Administración"** en las reglas operativas de este documento significa el rol **Admisión y cobranza**, no el Administrador.
- La **institución no tiene usuario**. Tiene un **correo de contacto** para recibir notificaciones.
- **Nadie se auto-registra.** El seminario crea el usuario de **todos** los alumnos (presenciales y de diplomado) y el sistema les envía su acceso para que completen su perfil.

### Reglas de acceso

- **ACC-01 [CONFIRMADO]** Todo alumno recibe **automáticamente** un usuario con el rol **Alumno** al **finalizar su admisión** (ver `ACC-06`), con un **correo de bienvenida** con orientaciones y su acceso (deriva de `ADM-07`). Nadie crea a mano el usuario de un alumno.
- **ACC-02 [CONFIRMADO]** Los **maestros se crean manualmente** por registro académico o por el administrador (deriva de `REG-07`). Un maestro puede ser también alumno: la misma persona suma el rol.
- **ACC-03 [CONFIRMADO]** Cada persona tiene **un solo usuario** y puede tener **varios roles**. La institución no tiene usuario.
- **ACC-04 [CONFIRMADO]** El rol Alumno se **asigna al crear el usuario**, igual que cualquier otro rol; no se deriva de tener una ficha de alumno.
- **ACC-05 [CONFIRMADO]** El usuario **inicia sesión con su correo**. El teléfono es solo un dato de contacto.
- **ACC-06 [CONFIRMADO]** Si el alumno no tiene correo, el seminario se lo crea **fuera del sistema**. Mientras tanto, la ficha se registra con la admisión **pendiente de finalizar**. Al cargar el correo se finaliza la admisión y se crea el usuario (`ACC-01`). Con la admisión pendiente, el alumno **sí se inscribe y genera cobros**; solo espera su acceso.

## 4. Glosario

| Término | Definición acordada |
|---|---|
| **Persona** | Natural (alumnos, maestros, personal) o jurídica (instituciones). Se identifica con tipo y número de identificación (cédula, RUC, pasaporte u otro). |
| **Alumno** | Persona natural inscrita en un programa. Una ficha por alumno. Está en **un solo programa** a la vez. |
| **Institución** | Persona **jurídica**: iglesia, seminario o escuela teológica que contrata un diplomado por extensión o patrocina alumnos. No tiene usuario. |
| **Vínculo** | Asociación de un alumno a una institución. |
| **Paga la institución** | Marca que indica que el cobro de ese alumno lo asume la institución. El vínculo por sí solo **no** implica que pague. |
| **Matrícula** | Pago **anual** de los programas presenciales, equivalente a un mes de arancel. También se llamó "carga impositiva". No aplica al diplomado. |
| **Arancel / mensualidad** | Cuota mensual de los presenciales. Varía por programa. |
| **Trimestre** | Período académico de tres meses calendario. Hay 4 por año. Una materia dura un trimestre. |
| **Materia** | Unidad académica identificada por el **código interno** del seminario. La misma materia puede estar en el pensum de varios programas, presenciales o diplomado. |
| **Módulo** | Nombre de la materia cuando se imparte en el diplomado. Tiene fechas propias y 1, 2 o 4 encuentros, según lo acordado con la institución. |
| **Materia individual** | Caso en que un alumno cursa **una sola** materia en el trimestre. Se cobra con tarifa propia. |
| **Recuperación de módulo** | Un alumno de diplomado cursa en **otra institución** un módulo atrasado o reprobado. Se le cobra a él (`COB-21`). |
| **Mora** | Estado del alumno con **un mes completo sin pagar**. Para instituciones, ver `COB-16`. |
| **Solvente** | Alumno sin mora. |
| **Beca** | Descuento porcentual variable autorizado por el presidente. |
| **Certificado de notas** | Documento PDF con la tabla de notas del alumno, impreso en papel membretado y sellado. Se paga. |
| **Certificación / promoción** | Acto en que el seminario otorga un título (bachiller, profesor, licenciado, etc.) a un grupo de alumnos. **No confundir con certificado de notas.** |
| **Diploma** | Documento que se otorga al concluir un diplomado. |
| **Pensum** | Plan de materias de un programa, con sus relaciones de dependencia. |
| **Prerrequisito** | Materia que debe estar **aprobada** para poder inscribir otra. Es propio de la materia, no del pensum (`REG-02`). |
| **Recibo oficial de caja** | Comprobante manual con número único. El sistema solo registra su número, fecha y concepto. |
| **Alumno activo** | Alumno con programa vigente cuya **última clase cursada** (aprobada o no) terminó dentro de los últimos **3 años** (configurable). Es el universo desde el que se elige quién se promociona. |
| **Hoja de matrícula** | Formato de admisión firmado, **único para todos los programas**. Se sube como adjunto a la ficha. No confundir con el pago de matrícula. |

## 5. Modelo conceptual

- **Persona**: natural o jurídica, con datos básicos y **adjuntos**. Una persona natural puede tener varios roles (alumno, maestro, etc.).
- **Alumno / ficha**: datos generales (nombre, correo, teléfono, identificación), hoja de matrícula y soportes escaneados como adjuntos, becas, pagos, recibos, certificados emitidos, notas y observaciones.
- **Institución**: persona jurídica con datos de contacto, correo, convenio y carta de solicitud adjuntos.
- **Programa → Pensum → Materia/Módulo**. Las materias son un catálogo compartido entre programas, con prerrequisitos propios.
- **Trimestre**: calendario, distribución de materias, horarios y maestros asignados.
- **Inscripción**: alumno + materia/módulo + trimestre.
- **Cobro / Pago / Recibo**: un pago se asocia a un concepto y a un número de recibo único.
- **Recurso de biblioteca**: solo **físicos** (con copias). **Préstamo** con **cola**. Los digitales viven en Notion.

---

## 6. Admisión y cobranza

### 6.1 Admisión

- **ADM-01 [CONFIRMADO]** Cada alumno tiene una **ficha** digital que reemplaza a la hoja de matrícula impresa. La hoja tiene un **formato único para todos los programas** y se sube firmada como adjunto; la ficha guarda los datos generales (nombre, correo, teléfono, identificación).
- **ADM-02 [CONFIRMADO]** Se debe poder **adjuntar el documento físico escaneado** como soporte.
- **ADM-03 [CONFIRMADO]** Requisitos de los presenciales: fotocopia del **diploma de bachiller**, **cédula** y **carta firmada del pastor**.
- **ADM-04 [CONFIRMADO]** Requisitos del diplomado: **cédula** y **carta del pastor**. **No** se exige diploma de bachiller por el nivel académico del programa.
- **ADM-05 [CONFIRMADO]** Para el diplomado, la **institución** aporta un **convenio** y una **carta de solicitud**, adjuntos a su registro.
- **ADM-06 [CONFIRMADO]** El vínculo alumno–institución y la marca "paga la institución" los define Admisión y cobranza. En el diplomado, todo alumno está **vinculado** a la institución donde cursa, aunque tenga arreglo particular.
- **ADM-07 [CONFIRMADO]** Toda inscripción se registra desde el seminario. El sistema crea el usuario del alumno y le envía el acceso para completar su perfil (ver `ACC-01` y `ACC-06`).
- **ADM-08 [CONFIRMADO]** Cada **adjunto** lo ve **solo el área que lo agrega**. El alumno **no** ve sus propios adjuntos. Los adjuntos no son públicos: se descargan solo con permiso.

### 6.2 Quién paga (regla central)

- **COB-01 [CONFIRMADO]** Si el alumno está vinculado a una institución **y** marcado "paga la institución", cobra la institución.
- **COB-02 [CONFIRMADO]** En cualquier otro caso (sin vínculo, o vinculado pero no marcado), el alumno paga directamente al seminario.
- **COB-03 [CONFIRMADO]** Una institución, iglesia o misión puede **patrocinar** a alumnos, incluso de los presenciales. Es el mismo mecanismo de vínculo.
- **COB-04 [PROPUESTA]** La marca "paga la institución" debería vivir en la **inscripción** y no en la persona, por si el arreglo cambia por programa. Es decisión de diseño.

### 6.3 Presenciales

- **COB-05 [CONFIRMADO]** **Matrícula anual**: se paga una vez al año, al inicio, **completa**, sin importar cuánto estudie el alumno. Equivale a un mes de arancel. Se genera **solo** con la **primera inscripción del año académico**.
- **COB-06 [CONFIRMADO]** El año de la matrícula coincide con el año académico (en 2026 paga matrícula y los meses estudiados, en 2027 vuelve a pagarla).
- **COB-07 [CONFIRMADO]** **Mensualidad**: el monto es el **arancel mensual del programa** del alumno (configurable por programa), no por materia. Se paga mes a mes. Vence en los **primeros 5 días** del mes (configurable).
- **COB-08 [CONFIRMADO]** La carga del trimestre ajusta ese cobro: con **0 materias no se cobra** el trimestre (no se exige baja formal), con **1 materia** se cobra la tarifa de materia individual (`COB-09`) y con **2 o más** el arancel completo.
- **COB-09 [CONFIRMADO]** **Materia individual**: si el alumno inscribe **una sola** materia, el sistema lo detecta y **notifica a Admisión y cobranza**, que aprueba manualmente el cobro como materia individual. La tarifa es **fija y la misma para los tres programas** (configurable).
- **COB-10 [PROPUESTA]** El sistema solo admite pagar por adelantado **hasta el trimestre en curso**, para evitar reversiones si el alumno se retira. El propio usuario la marcó como discutible.
- **COB-11 [CONFIRMADO]** Un trimestre acortado **siempre cobra los tres meses** (ver `REG-14`).

### 6.4 Becas

- **COB-12 [CONFIRMADO]** Solo el **presidente** autoriza becas, pero no tiene rol en el sistema. Quien registra la beca (Admisión y cobranza) **debe adjuntar el soporte de la autorización**. Hasta ahí llega el control del sistema.
- **COB-13 [CONFIRMADO]** La beca es un **porcentaje variable** (10 %, 20 %, 50 %, 100 %, etc.), vale **todo el año** y aplica a las **mensualidades**.
- **COB-13b [PENDIENTE]** Si cubre también la matrícula y los gastos de promoción (ver sección 10).

### 6.5 Diplomado por Extensión

- **COB-14 [CONFIRMADO]** Se cobra **por módulo completo** a la institución que lo aloja, sin importar cuántos alumnos tenga (monto configurable en córdobas; la referencia original era $150). **No hay matrícula anual.**
- **COB-15 [CONFIRMADO]** Excepción: si un alumno tiene arreglo particular con el seminario, paga su parte directamente (monto configurable en córdobas; la referencia original era $10).
- **COB-16 [CONFIRMADO]** El cobro del módulo **vence en la fecha de fin del módulo**. La **institución** entra en mora **un mes después de ese vencimiento**. De momento esto **no tiene consecuencias**, solo notificación al correo de contacto. Los **alumnos de una institución morosa no se bloquean**.
- **COB-21 [CONFIRMADO]** **Recuperación de módulo**: si registro inscribe a un alumno de diplomado en un módulo de **otra institución** (`REG-33`), se le genera un cobro **a él**, con monto propio (configurable). Es el **único** cobro de esa inscripción y se le cobra aunque su institución pague o tenga arreglo particular: es una excepción que se le concede. Si su institución le da el dinero, es asunto de ellos. El cobro del intento anterior no aprobado se mantiene.

### 6.6 Pagos, recibos y otros cobros

- **COB-17 [CONFIRMADO]** Cada pago registrado exige: **número de recibo oficial**, **fecha** y **concepto**. El número es **único**, propio del recibo.
- **COB-18 [CONFIRMADO]** El recibo puede **anularse**. Si el pago sí se realizó, se emite **uno nuevo que lo reemplaza**, y el recibo anulado **se conserva** en el sistema. No se adjunta copia escaneada del recibo.
- **COB-19 [CONFIRMADO]** Además de matrícula y mensualidades se registran con trazabilidad: **certificados de notas** y **gastos de graduación (promoción)**.
- **COB-20 [CONFIRMADO]** Admisión y cobranza tiene una **vista de alumnos con pagos pendientes**.
- **COB-22 [CONFIRMADO]** **Todo se cobra en córdobas.** Si hay que convertir, lo hace la persona fuera del sistema.
- **COB-23 [CONFIRMADO]** **No hay pagos parciales.** Un recibo puede cubrir **varios cobros completos** (por ejemplo, varios meses o conceptos).

### 6.7 Mora

- **MOR-01 [CONFIRMADO]** Un alumno entra en mora al completar **un mes sin pagar**.
- **MOR-02 [CONFIRMADO]** No hay recargo económico.
- **MOR-03 [CONFIRMADO]** La mora **bloquea la consulta en línea de notas y los préstamos físicos de biblioteca** (los recursos digitales se descargan, no se prestan). **No** bloquea la emisión de certificados (el alumno puede pagar por esa vía individualmente).

---

## 7. Registro académico

### 7.1 Pensum y calendario

- **REG-01 [CONFIRMADO]** Registro administra el **catálogo de materias** (con el código interno del seminario), el **pensum de cada programa** y las **relaciones de prerrequisito** entre materias. El pensum de un alumno puede cambiar; el cambio se hace a mano en su ficha.
- **REG-02 [CONFIRMADO]** El **prerrequisito exige materia aprobada** (no basta con cursada). Ejemplo: no se cursa Exégesis de Romanos sin aprobar Principios de Exégesis. El prerrequisito es **de la materia** y vale en todos los programas. Si la materia requerida **no está en el pensum del alumno**, no se le aplica; al guardar un pensum con esa omisión, el sistema avisa a registro y le pide confirmarla.
- **REG-03 [CONFIRMADO]** **No hay convalidaciones** hoy. Si existieran, registro las incluye en las notas del alumno con una **nota explicativa**.
- **REG-04 [CONFIRMADO]** Registro define el **calendario**: 4 trimestres al año y sus fechas.
- **REG-05 [CONFIRMADO]** Cada trimestre registro genera la **distribución de materias y el horario** de los presenciales, y la **distribución de maestros** de los módulos de diplomado.
- **REG-06 [CONFIRMADO]** Los diplomados tienen periodicidad distinta: cada módulo tiene **fechas propias** y **1, 2 o 4 encuentros**, que registro acuerda con la institución. El sistema no registra horas.
- **REG-07 [CONFIRMADO]** Los **maestros** los crean o designan el administrador y registro académico. Un maestro puede ser también alumno. Cada oferta de una materia o módulo tiene **un solo maestro**; el mismo módulo puede tener otro maestro en otra institución o fecha.

### 7.2 Inscripción

- **REG-08 [CONFIRMADO]** El alumno se inscribe **desde el sistema** a las materias disponibles del trimestre, dentro de una **fecha habilitada**. Se le avisa fuera del sistema.
- **REG-09 [CONFIRMADO]** Registro académico **puede inscribir por el alumno** (por ejemplo, quien tiene poco acceso a tecnología).
- **REG-10 [CONFIRMADO]** El sistema **valida los prerrequisitos** y la disponibilidad antes de permitir la inscripción.
- **REG-11 [CONFIRMADO]** El sistema **impide inscribir dos materias en el mismo horario**.
- **REG-12 [CONFIRMADO]** Si inscribe una sola materia, se dispara el aviso de materia individual (`COB-09`).
- **REG-33 [CONFIRMADO]** Registro puede inscribir a un alumno de diplomado en un módulo de **otra institución** para que recupere una materia atrasada o reprobada (ver `COB-21`).

### 7.3 Trimestre recortado

- **REG-13 [CONFIRMADO]** Si un trimestre pierde días (feriados, fuerza mayor), se ofrecen **menos materias** (por ejemplo 2 en lugar de 3) y se alargan los plazos.
- **REG-14 [CONFIRMADO]** Se mantienen las **horas clase**, pero los **bloques son más largos** (de 1.5 h a unas 2–2.5 h). El trimestre sigue abarcando tres meses y **se cobran los tres**. Ejemplo: el cuarto trimestre de 2026 va del 17 de octubre al primer sábado de diciembre y cobra octubre, noviembre y diciembre. Lo gestiona registro académico; el sistema no registra las horas.

### 7.4 Notas

- **REG-15 [CONFIRMADO]** Escala de **0 a 100**. La **nota mínima de aprobación es configurable por programa**. Cada inscripción tiene **una sola nota final**.
- **REG-32 [CONFIRMADO]** Una materia aprobada vale en **todos los programas** que la tengan, con el resultado que quedó al cerrar las notas en el programa donde se cursó, aunque otro programa tenga una mínima más alta. No es una convalidación (`REG-03`): es la misma materia.
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
- **REG-25 [CONFIRMADO]** En la ficha del alumno se ve el pago, su recibo y el certificado emitido, y Admisión y cobranza puede **descargarlo e imprimirlo**.
- **REG-26 [CONFIRMADO]** Se puede emitir un certificado **sin pago activo** solo por **reimpresión** o **uso interno**. No existe exoneración. Estas emisiones deben dejar **motivo registrado** (el motivo es una recomendación de diseño).

### 7.6 Promoción y diploma

- **REG-27 [CONFIRMADO]** Registro tiene una pantalla para **registrar una promoción** (por ejemplo, de bachillerato): elige, entre los alumnos **activos** (ver glosario), quiénes se promocionan.
- **REG-28 [CONFIRMADO]** El sistema **valida** que cada alumno tenga **todas las materias aprobadas, solvencia y gastos de graduación pagados**.
- **REG-29 [CONFIRMADO]** El **título que recibe cada programa es configurable** (no se fija en código).
- **REG-30 [CONFIRMADO]** La promoción guarda el **registro de certificación** y deja una **nota en la ficha de cada alumno** con el título recibido.
- **REG-31 [CONFIRMADO]** Los alumnos de diplomado reciben un **diploma** al terminar. Notas y certificados funcionan igual que en los presenciales. El flujo detallado del diploma no se ha definido.

---

## 8. Biblioteca

- **BIB-01 [CONFIRMADO]** Biblioteca tiene dos tipos de recurso: **digitales** (en Notion) y **físicos** (hoy en Excel). **Solo los físicos** se gestionan en el sistema, cada uno con su **ficha**.
- **BIB-02 [CONFIRMADO]** Admisión y registro asumen la gestión de la biblioteca. No hay rol propio.
- **BIB-03 [CONFIRMADO]** Ficha física: **una sola ficha por título** con su **número de copias**. Campos actuales: **título, autor, n.° de copias, código, n.° de vitrina**.
- **BIB-04 [CONFIRMADO]** Libros digitales: viven por completo en **Notion**. El sistema **no guarda nada digital** (ni archivos, ni enlaces, ni catálogo), para no mantener dos fuentes. Llegan al índice por una **automatización externa** con Notion.
- **BIB-05 [CONFIRMADO]** Un **índice centralizado y buscable** es la **vía de navegación** de la biblioteca para alumnos, con físicos y digitales: sin índice no hay vistas de biblioteca. El sistema publica en él los recursos físicos. La disponibilidad de copias y la solicitud de préstamo se consultan al sistema al abrir el detalle de un recurso físico. Se mencionó Algolia como idea. **La herramienta no está decidida** (`TEC-08`).
- **BIB-06 [CONFIRMADO]** Puede pedir préstamo **cualquier alumno o maestro**.
- **BIB-07 [CONFIRMADO]** Flujo: el alumno **solicita** desde el sistema, admisión o registro **aprueba** (aprobar = **entregar** el libro), y al devolver, admisión o registro **marcan la recepción** y se cierra el préstamo.
- **BIB-08 [CONFIRMADO]** **Cola**: si todas las copias están prestadas, el solicitante entra a una cola. Al devolverse, se **notifica al siguiente**. **No se puede aprobar un préstamo saltándose el orden.**
- **BIB-09 [CONFIRMADO]** El siguiente en cola tiene **una semana** desde la devolución para retirar el libro.
- **BIB-10 [CONFIRMADO]** La solicitud la pueden **cancelar el alumno, admisión o registro**.
- **BIB-11 [CONFIRMADO]** **No devolución**: se bloquean nuevos préstamos y el alumno debe **reponer el libro**. **Admisión y cobranza** da la sanción por saldada. Mientras no se salde, no puede pedir otro.
- **BIB-12 [CONFIRMADO]** **Mora de pago**: el alumno **conserva** los libros que ya tiene. Si está en cola, **conserva su lugar**, se le notifica que los préstamos dependen de estar solvente y **no se le aprueba** hasta ponerse al día. Si llega su turno y sigue en mora, **pierde el turno**. No se le saca antes de tiempo, por si paga a tiempo.

---

## 9. Configuración (módulo del Administrador)

Nada de esto va fijo en el código. Todos los montos van en **córdobas** (`COB-22`):

- Arancel mensual **por programa**
- Matrícula anual (equivale a un mes de arancel, ver pendiente 8)
- Tarifa de materia individual (única para los tres programas)
- Precio del módulo de diplomado y monto del alumno con arreglo particular (sin valor inicial: se cargan en córdobas; la referencia original era $150 y $10)
- Monto de la recuperación de módulo (`COB-21`, sin valor inicial)
- Arancel del certificado de notas y monto de gastos de graduación
- Años que un alumno sigue **activo** desde su última clase (inicial: **3**)
- Nota mínima de aprobación **por programa**
- Ventana de registro de notas (20 días)
- Firmas que lleva el certificado de notas
- Títulos que otorga cada programa
- Calendario trimestral y fecha de inscripción (también lo edita registro académico, `REG-04`)
- Parámetros de biblioteca (plazo de retiro, y los que defina el negocio: plazo de préstamo, máximo de libros)

## 10. Pendientes con el negocio

★ = bloquea el diseño.

**Biblioteca**
1. ★ **Plazo de préstamo**, si se renueva y **máximo de libros a la vez**. *(Esperando información del seminario.)*
2. **Sanción por pérdida**: ¿se repone el mismo libro o se acepta su valor en dinero?
3. ~~**Mora y biblioteca digital**~~ **Resuelto (2026-10-29):** solo bloquea préstamos físicos (`MOR-03`).

**Cobranza**
4. **Beca**: ¿cubre matrícula y gastos de promoción? *(Probablemente sí, por confirmar.)*
5. **Mora**: ¿desde qué fecha se cuenta el mes (desde el día 5, desde el último pago)?
6. **Pago anticipado**: ¿se confirma el límite del trimestre en curso? (`COB-10`)
7. **Marca "paga la institución"**: ¿a nivel de inscripción o de alumno? (`COB-04`)
8. **Matrícula**: ¿se calcula automáticamente como un mes de arancel o es un monto independiente?

**Registro académico y transversales**
9. **Diploma del diplomado**: ¿cómo se emite y qué requisitos tiene?
10. **Notificaciones del sistema**: ¿por qué canal (correo, WhatsApp, dentro del sistema)? Hoy los avisos de inscripción se hacen fuera del sistema. *(La bienvenida al alumno ya va por correo, `ACC-01`; el resto sigue abierto.)*
11. **Recibo anulado**: ¿se registra el motivo?

**Infraestructura** (ver sección 12)
12. ~~**Base de datos**~~ **Resuelto:** PostgreSQL 17 en el VPS.
13. **Dominio**: ¿subdominio dedicado (recomendado) o raíz?

## 11. Historial de aclaraciones

- "Carga impositiva" = otra forma de nombrar la matrícula anual (resuelto).
- La creación de usuarios por parte del seminario aplica a **todos** los programas, no solo al diplomado.
- Ver notas y emitir certificado son acciones independientes; solo la emisión se asocia a un pago.
- En trimestres recortados se mantienen las horas clase, no la duración de los bloques.
- **2026-10-29, revisión del modelo de datos** (detalle en `.artifacts/modelo-datos-inicial.md`, sección 4.2):
  - "Administración" en lo operativo = Admisión y cobranza; el Administrador actúa a nivel de sistema.
- **2026-10-29, historias de la app `personas`:** el Administrador es el **superusuario** del sistema y no un grupo aparte. Los demás roles son grupos (Admisión y cobranza, Registro académico, Maestro, Alumno). El Administrador **no** descarga adjuntos (`ADM-08`).
  - La institución es una persona jurídica; persona e institución comparten el manejo de adjuntos.
  - El cobro parte del arancel del programa y la carga del trimestre lo ajusta (`COB-07`, `COB-08`).
  - Todo en córdobas, sin pagos parciales (`COB-22`, `COB-23`).
  - La materia es un catálogo con código interno, compartido entre programas (`REG-01`, `REG-32`).
  - Nada digital en la base de datos (`BIB-04`); el índice es la vía de navegación (`BIB-05`).
  - Admisión en dos pasos cuando falta el correo (`ACC-06`).
  - Recuperación de módulo en otra institución, cobrada al alumno (`REG-33`, `COB-21`).

---

## 12. Decisiones técnicas

Estas decisiones no cambian las reglas de negocio. Fijan el terreno donde se construye el sistema.

- **TEC-01 [CONFIRMADO]** **Framework: Django 5.2 (LTS)**, arquitectura de **monolito** con una app por área (admisión y cobranza, registro académico, biblioteca) más un módulo de configuración y un módulo de personas y accesos (ver `TEC-11`). Se eligió por traer autenticación, roles y permisos, panel de administración (útil para la sección 9), ORM con migraciones y buen soporte para PDFs, auditoría y tareas programadas.
- **TEC-02 [CONFIRMADO]** **Alojamiento: VPS con panel Webuzo.** La app corre con **gunicorn** en un puerto interno (30000) y se publica desde el *Application Manager* de Webuzo (tipo Python 3, entorno *Production*). Las variables sensibles (`SECRET_KEY`, base de datos, `DEBUG=False`) van como **variables de entorno**, nunca en el repositorio.
- **TEC-03 [CONFIRMADO]** **Python 3.11.3** instalado en el VPS (`/usr/local/apps/python3/bin/python3`), compatible con Django 5.2. Se usa un **entorno virtual** por proyecto.
- **TEC-04 [CONFIRMADO]** Los archivos estáticos y los **adjuntos** (soportes escaneados, certificados emitidos) se sirven **fuera de Django** y se almacenan como archivos, no dentro de la base de datos. Se deben incluir en los respaldos. **Provisional:** mientras no se confirme con el servidor del VPS si puede entregar los adjuntos directamente, los entrega **Django** tras verificar el permiso del área; el cambio a servirlos fuera de Django sería solo de configuración, sin tocar la vista de descarga.
- **TEC-05 [CONFIRMADO]** Los procesos programados (avisos de mora, ventanas de notas vencidas, notificaciones de cola) se ejecutan con **cron** del VPS.
- **TEC-06 [PROPUESTA]** Generación de PDF (certificado de notas) con una librería que **no** dependa de paquetes del sistema (por ejemplo ReportLab), salvo que se decida instalar dependencias en el VPS.
- **TEC-07 [CONFIRMADO]** **Auditoría** (historial de cambios) en notas, recibos, becas, certificados y pensums, por exigirlo las reglas `REG-18`, `COB-18`, `REG-26` y `REG-02`. Se implementa con **`django-simple-history`**.
- **TEC-08 [PENDIENTE]** Dominio (ver pendiente 13). La base de datos ya está decidida (PostgreSQL 17). La herramienta del índice de biblioteca (`BIB-05`) sigue **sin decidir** y bloquea las vistas de biblioteca para alumnos.
- **TEC-09 [PENDIENTE]** **Respaldos**: frecuencia, ubicación y responsable (base de datos y adjuntos). Definirlos antes de salir a producción.
- **TEC-10 [CONFIRMADO]** Alternativa descartada por ahora: **Laravel**. Solo se retomaría si Django no se pudiera desplegar en el VPS.
- **TEC-11 [CONFIRMADO]** Existe una quinta app, **`personas`**, dueña de personas, usuarios, roles, login y adjuntos. Las demás apps dependen de ella; ella **no** depende de ninguna. `admision_cobranza` y `registro_academico` crean usuarios llamando a su servicio (ver `ACC-01` y `ACC-02`). Los nombres de las apps son: `personas`, `admision_cobranza`, `registro_academico`, `biblioteca`, `configuracion`.
