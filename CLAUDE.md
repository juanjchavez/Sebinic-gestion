# Sistema de Gestión del Seminario Bíblico Nicaragüense

Sistema de gestión y control con tres áreas: **admisión y cobranza**, **registro académico** y **biblioteca**.

## Fuente de verdad del negocio

Las reglas del negocio viven en `.artifacts/shared-understanding-seminario.md`. **Léelo antes de tocar lógica de negocio** y cita las reglas por ID (`COB-03`, `REG-18`, `BIB-08`…) en planes, historias, commits y comentarios relevantes.

Estados de cada regla:
- **[CONFIRMADO]**: implementar tal cual.
- **[PROPUESTA]**: no implementar como regla firme; confirmar primero.
- **[PENDIENTE]**: **detenerse y preguntar**. No inventar la regla (ver sección 10 del documento).

Si el código y el documento se contradicen, el documento manda; si el documento está desactualizado, avisar al usuario en vez de corregirlo en silencio.

## Gestión del proyecto

Tablero kanban de tareas: https://github.com/users/juanjchavez/projects/3/views/1

## Stack (TEC-01 a TEC-05)

- Django 5.2 LTS, monolito con cinco apps dentro de `apps/`: `personas`, `admision_cobranza`, `registro_academico`, `biblioteca` y `configuracion` (TEC-11). Mantener esos nombres.
- `personas` es dueña de personas, usuarios, roles y login. Las demás apps dependen de ella y **ella no depende de ninguna**. Los usuarios se crean siempre mediante su servicio: los alumnos automáticamente al registrarlos (ACC-01) y los maestros a mano por registro académico o el administrador (ACC-02).
- Python 3.11 con entorno virtual por proyecto.
- Despliegue: VPS con Webuzo, gunicorn en el puerto interno 30000.
- Secretos y configuración sensible (`SECRET_KEY`, BD, `DEBUG`) **solo por variables de entorno**, nunca en el repo.
- Estáticos y adjuntos (soportes escaneados, certificados emitidos) se guardan como **archivos fuera de la BD** y se sirven fuera de Django.
- Tareas programadas (avisos de mora, ventanas de notas vencidas, notificaciones de cola) con **cron** del VPS, expuestas como management commands.
- Base de datos: **PostgreSQL 17** en el servidor (actualizado desde la 13.23; compatible con Django 5.2, que soporta PG 14+). Driver: `psycopg` (v3).
- Dominio, índice de búsqueda de biblioteca y respaldos siguen **[PENDIENTE]** (TEC-08, TEC-09).

## Reglas de oro

1. **Nada de valores fijos en el código.** Montos, plazos, notas mínimas, títulos, firmas, ventana de notas, parámetros de biblioteca y calendario van en el módulo de configuración (sección 9 del documento), editable por el Administrador. Los valores del documento ($150, $10, 20 días, etc.) son solo valores por defecto/iniciales.
2. **Persona y rol son conceptos separados.** Una persona puede tener varios roles (alumno + maestro). Modelar con roles/permisos, no con tipos de usuario excluyentes.
3. **Nadie se auto-registra.** El seminario crea los usuarios de todos los alumnos y el sistema les envía el acceso. La institución **no** tiene usuario, solo un correo de contacto.
4. **El sistema no factura.** El recibo oficial de caja es manual; el sistema solo registra su número (único), fecha y concepto (COB-17). Un recibo anulado se conserva y puede tener uno de reemplazo (COB-18).
5. **Quién paga:** institución solo si hay vínculo **y** marca "paga la institución"; en cualquier otro caso paga el alumno (COB-01/02). El vínculo por sí solo no implica pago.
6. **Mora** bloquea consulta de notas y acceso a biblioteca, **no** la emisión de certificados (MOR-03). La mora de una institución solo notifica, no bloquea a sus alumnos (COB-16). No hay recargos.
7. **Notas:** escala 0–100, mínima de aprobación configurable **por programa**. Tras el cierre del maestro solo registro corrige, con justificación obligatoria (REG-18). El prerrequisito exige materia **aprobada**.
8. **Ver notas ≠ emitir certificado** (REG-23). Solo la emisión se asocia a un pago; las emisiones sin pago (reimpresión, uso interno) deben registrar motivo (REG-26).
9. **Biblioteca sin rol propio:** la gestionan admisión y registro. La cola de préstamos respeta el orden estrictamente (BIB-08).
10. **Auditoría** (historial de cambios) en notas, recibos, becas y certificados (TEC-07, propuesta alineada con REG-18, COB-18, REG-26).

## Guías de Python y Django

Actúa como experto en Python, Django y aplicaciones web escalables. Respuestas claras y técnicas, con ejemplos precisos de Django.

**Principios**
- Usar las herramientas integradas de Django siempre que sea posible.
- Priorizar legibilidad y mantenibilidad; PEP 8 y la guía de estilo de Django.
- Nombres descriptivos; `snake_case` para funciones y variables.
- Estructura modular con apps de Django (separación de responsabilidades, reutilización).
- Convención sobre configuración: reducir boilerplate.
- Seguridad y rendimiento en cada etapa del desarrollo.

**Django / Python**
- CBVs para vistas complejas; FBVs para lógica simple.
- ORM para acceso a datos; SQL crudo solo si es necesario por rendimiento.
- Modelo de usuario y framework de autenticación de Django (roles vía grupos/permisos, ver reglas de oro).
- `Form` y `ModelForm` para formularios y validación.
- Patrón MVT estricto. **Lógica de negocio en modelos y formularios** (o servicios); vistas delgadas, solo manejo de request.
- Middleware con criterio, solo para temas transversales (autenticación, logging, caché, seguridad).
- URLs claras y RESTful en `urls.py`.
- Plantillas de Django para HTML; serializers de DRF para JSON solo si se llega a necesitar una API.

**Errores y validación**
- Manejo de errores a nivel de vista con los mecanismos de Django.
- Validación con el framework de Django (formularios y modelos).
- `try/except` en lógica de negocio y vistas, capturando excepciones específicas.
- Páginas de error personalizadas (404, 500) útiles para el usuario.
- Señales de Django para desacoplar logging y manejo de errores de la lógica central.

**Seguridad**
- CSRF, protección contra inyección SQL y XSS (no desactivar el autoescape sin motivo).

**Rendimiento**
- `select_related` / `prefetch_related` para evitar consultas N+1.
- Índices de base de datos y optimización de consultas.
- Framework de caché de Django para datos de lectura frecuente.
- Vistas asíncronas solo para operaciones I/O pesadas.

**Pruebas**
- `pytest-django` (o `unittest`) para calidad y fiabilidad.

**Ajustes frente a las decisiones del proyecto** (las decisiones técnicas del documento prevalecen sobre las guías genéricas)
- **Tareas en segundo plano:** cron + management commands (TEC-05), **no** Celery/Redis. Solo se reconsidera si el usuario lo decide.
- **Caché:** usar el backend que el VPS permita (locmem/archivos/BD); Redis no está disponible por defecto. No introducir infraestructura nueva sin confirmar.
- **Estáticos y adjuntos:** se sirven fuera de Django (TEC-04); no asumir WhiteNoise ni CDN.
- **Base de datos:** PostgreSQL 17 (ver Stack); MySQL/MariaDB queda descartado.
- **DRF:** no es parte del alcance actual; añadirlo solo si surge una necesidad de API.

## Fuera de alcance (no construir)

Facturación/recibo oficial, aviso de apertura de inscripción a alumnos, cupo mínimo de materias, gestión de archivos de libros digitales (solo se guardan enlaces; viven en Notion), rol de presidente.

## Convenciones

- Idioma: el dominio y la UI están en **español**. Usar términos del glosario del documento (alumno, institución, matrícula, arancel, trimestre, materia/módulo, certificado de notas vs. certificación/promoción, etc.) en nombres de modelos, campos y textos visibles. No traducirlos al inglés ni mezclar sinónimos.
- Código, identificadores técnicos y mensajes de commit pueden seguir la convención del proyecto una vez establecida; ser consistente con lo que ya exista.
- Cada regla de negocio implementada debe tener al menos una prueba que referencie su ID.
- Antes de implementar algo que toque un pendiente ★ (bloqueante), preguntar al usuario.

## Comandos

Instalación:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Verificación:

```powershell
python manage.py check
```

Ejecución local:

```powershell
python manage.py runserver
```

Migraciones:

```powershell
python manage.py migrate
```

Pruebas:

```powershell
pytest
```

Despliegue se documentará cuando exista.

Las cinco carpetas de `apps/` son marcadores `.gitkeep` hasta que se cree cada app con `startapp`.
