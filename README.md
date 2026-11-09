# Sistema de Gestión del Seminario Bíblico Nicaragüense

## Descripción

Sistema de gestión y control del Seminario Bíblico Nicaragüense, con tres áreas: admisión y cobranza, registro académico y biblioteca. Las reglas del negocio están documentadas en `.artifacts/shared-understanding-seminario.md`.

## Prerrequisitos

- **Python 3.11.x** (misma versión menor que el VPS; el parche puede diferir, porque python.org ya no publica instaladores de Windows para los parches de seguridad de 3.11). Verificar con:
  ```powershell
  py -3.11 --version
  ```
  Si falta, instalar con:
  ```powershell
  winget install Python.Python.3.11
  ```
  Después de instalar, abrir una terminal nueva para que el PATH se actualice.
- **Git**. Verificar con:
  ```powershell
  git --version
  ```

## Instalación

Desde la raíz del repositorio, en PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si PowerShell bloquea `Activate.ps1` por la política de ejecución, no es necesario activar el entorno: ejecutar los comandos directamente con `.\.venv\Scripts\python.exe -m ...` (por ejemplo, `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`).

## Base de datos (PostgreSQL 17 local)

1. **Instalar PostgreSQL 17**:
   ```powershell
   winget install --id PostgreSQL.PostgreSQL.17
   ```
   O usar el instalador oficial de [postgresql.org](https://www.postgresql.org/download/windows/). El asistente puede pedir un puerto (dejar el valor por defecto, `5432`) y una contraseña para el superusuario `postgres`: elegirla y recordarla. (Con la instalación silenciosa de `winget` puede que no aparezca ningún asistente; en ese caso, establecer la contraseña del superusuario con `ALTER ROLE postgres PASSWORD '...'` desde una PowerShell con permisos de administrador, tras poner temporalmente `trust` en `pg_hba.conf` y reiniciar el servicio `postgresql-x64-17`.)

2. **Crear el rol y la base de desarrollo.** Usar el rol `seminario_app` (no el superusuario `postgres`) con permiso `CREATEDB`, para que el ticket 3 pueda crear la base de pruebas sin usar el superusuario. **Nunca escribir la contraseña real en un comando `psql -c "..."`**: queda en el historial de PowerShell. Usar en su lugar la variable de entorno `PGPASSWORD` de la sesión y un archivo SQL temporal fuera del repo, borrado apenas se usa:
   ```powershell
   $env:PGPASSWORD = '<contraseña-del-superusuario>'
   $sqlPath = Join-Path $env:TEMP "seminario_dev_role.sql"
   @'
   CREATE ROLE seminario_app WITH LOGIN PASSWORD '<elegir-una-contraseña-nueva>' CREATEDB;
   CREATE DATABASE seminario_dev OWNER seminario_app;
   '@ | Set-Content -Path $sqlPath -Encoding utf8
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -f $sqlPath
   Remove-Item $sqlPath -Force
   Remove-Item Env:\PGPASSWORD
   ```

3. **Configurar las variables de entorno:**
   ```powershell
   Copy-Item .env.example .env
   ```
   Generar una `SECRET_KEY` nueva (no reutilizar la de `.env.example`):
   ```powershell
   .\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Completar en `.env`: la `SECRET_KEY` generada, y `DB_PASSWORD` con la contraseña real del rol `seminario_app` creado en el paso anterior. `.env` nunca se commitea (ya está en `.gitignore`).

### Variables de entorno nuevas

Copiar `.env.example` trae las variables nuevas. Si ya tenías un `.env` de antes, añade al menos `ADJUNTOS_ROOT`: sin ella el proyecto no arranca.

| Variable | Obligatoria | Valor por defecto | Para qué sirve |
|---|---|---|---|
| `ADJUNTOS_ROOT` | Sí | ninguno | Carpeta privada donde se guardan los adjuntos (soportes escaneados, certificados emitidos). Debe estar **fuera del repositorio y fuera de la raíz web**. |
| `ADJUNTO_TAMANO_MAX_MB` | No | `10` | Tamaño máximo de cada adjunto, en MB (provisional). |
| `URL_BASE_SITIO` | No | `http://localhost:8000` | URL pública del sitio, para los enlaces de los correos. |
| `EMAIL_BACKEND` | No | `django.core.mail.backends.smtp.EmailBackend` | Backend de correo. `.env.example` usa `django.core.mail.backends.console.EmailBackend`: en local los correos se imprimen en la consola y no se envían. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | No | `localhost`, `587`, vacío, vacío, `True`, `False` | Servidor SMTP. Valores provisionales hasta que el seminario elija proveedor. |
| `DEFAULT_FROM_EMAIL` | No | `webmaster@localhost` | Remitente de los correos. |
| `ENLACE_ACCESO_VIGENCIA_DIAS` | No | `3` | Días de vigencia del enlace de acceso que recibe un usuario nuevo (lo usa el servicio de acceso, #23). Provisional. |
| `ACCESO_REINTENTOS_MAX` | No | `3` | Intentos máximos del enlace de acceso (#23). Provisional. |

Son valores provisionales. Cuando exista `apps/configuracion/`, los parámetros del negocio se editarán desde ahí.

Crear la carpeta de adjuntos una vez, en PowerShell, y apuntar `ADJUNTOS_ROOT` a ella en `.env` (con `/`, no `\`):

```powershell
New-Item -ItemType Directory -Force C:\seminario-datos\adjuntos
```

### Recrear la base local

La base `seminario_dev` creada antes de este cambio tiene las tablas del usuario por defecto de Django (`auth.User`). El proyecto ahora usa `personas.Usuario` (ACC-05), así que esa base ya no es consistente y hay que recrearla **una sola vez**.

> **Atención:** esto borra todos los datos de `seminario_dev`. Hacerlo solo si la base tiene datos de prueba locales.

Con el rol `seminario_app` (dueño de la base, con permiso `CREATEDB`):

```powershell
$env:PGPASSWORD = '<contraseña-de-seminario_app>'
& "C:\Program Files\PostgreSQL\17\bin\dropdb.exe" -U seminario_app -h localhost seminario_dev
& "C:\Program Files\PostgreSQL\17\bin\createdb.exe" -U seminario_app -h localhost -O seminario_app seminario_dev
Remove-Item Env:\PGPASSWORD
```

Después, correr `migrate` y `createsuperuser` como se indica en la siguiente sección.

## Cómo levantar el servidor

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en el navegador. `/admin/` ya funciona y muestra la pantalla de inicio de sesión, que pide **correo** y contraseña (ACC-05).

`createsuperuser` pide solo correo y contraseña. El **superusuario es el Administrador del sistema** (sección 3, C39); puede ser una cuenta técnica sin Persona asociada.

## Roles y panel del Administrador

Al ejecutar `migrate`, la señal `post_migrate` crea los cuatro grupos que falten (ACC-03/04, sección 3):

| Grupo | Permisos iniciales |
|---|---|
| Admisión y cobranza | Ver, agregar y modificar Persona |
| Registro académico | Ver, agregar y modificar Persona |
| Maestro | Ninguno |
| Alumno | Ninguno |

La semilla asigna permisos **solo a grupos nuevos**. Migrar otra vez no duplica grupos ni restaura permisos que el Administrador haya quitado. Tampoco elimina grupos ajenos. No existen grupos de sistema Administrador, Biblioteca, Coordinador o Presidente (C24/C39). Una persona puede tener varios roles; la semilla no crea usuarios ni asigna membresías.

Solo un superusuario **activo y con acceso al panel** (`is_active`, `is_superuser` e `is_staff`) entra a `/admin/`. Los grupos operativos no entran, aunque tengan permisos o la marca de acceso al panel. El Administrador puede editar los permisos de cada grupo.

El panel permite registrar y editar personas. Su correo queda de solo lectura cuando tienen usuario, para evitar que diverja del correo de acceso (ACC-05, C42). En usuarios existentes solo se editan estado, acceso al panel y condición de superusuario. No hay alta directa, eliminación, edición de credenciales ni de membresías. Otorgar acceso y cambiar correo se integrará con el servicio #23; las pantallas de acceso pertenecen al #24. La baja disponible es la desactivación.

No se puede desactivar ni retirar la condición de superusuario o el acceso al panel al último Administrador operativo (C39), incluso con dos cambios simultáneos. Las escrituras soportadas usan `Usuario.save()`; `QuerySet.update()`, `bulk_update()` y SQL externo eluden validación e historial y no se deben usar para estos cambios.

Después de migrar, comprobar los grupos con:

```powershell
python manage.py check --database default --fail-level WARNING
```

`check` sin `--database` no consulta los grupos. La comprobación distingue grupos faltantes (`personas.W001`), tablas todavía sin crear (`W002`) y conexión inaccesible (`W003`). CI ejecuta esta verificación después de migrar.

Si un grupo fue renombrado, investigar primero cuál es y qué miembros tiene. Restaurar su nombre canónico conserva las membresías. Volver a migrar puede crear un grupo nuevo con el nombre faltante, pero **no transfiere miembros ni elimina el grupo renombrado**: esa reconciliación queda a cargo del Administrador.

## Pruebas

Instalar las dependencias de desarrollo (incluye las de producción):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Correr las pruebas:

```powershell
pytest
```

Las pruebas corren contra una base de datos de prueba separada (creada y destruida automáticamente por `pytest-django`); la base de desarrollo no se toca. Cada prueba que cubre una regla de negocio debe citar su ID con el marcador `regla`, por ejemplo `@pytest.mark.regla("COB-17")`; para ver qué regla cubre cada prueba, correr `pytest -v`.

El CI (`.github/workflows/ci.yml`) instala `requirements-dev.txt`, verifica que no falten migraciones, migra una base vacía y corre `pytest -v`.

## Estructura de carpetas

```
config/             Configuración técnica del proyecto Django (settings, urls, wsgi, asgi)
apps/
  personas/         Personas, usuarios, roles, semilla, checks y panel del Administrador
  admision_cobranza/   Admisión y cobranza
  registro_academico/  Registro académico
  biblioteca/          Biblioteca
  configuracion/       Parámetros del negocio editables por el Administrador
manage.py
requirements.txt
```

`apps/personas/` ya existe: modelos `Persona` y `Usuario`, `selectores.py`, `normalizacion.py` y `tests/`. Las otras cuatro carpetas de `apps/` siguen siendo marcadores (`.gitkeep`): cada app se crea con `startapp` en el ticket que la necesite.

**`config/` no es lo mismo que `apps/configuracion/`.** `config/` es la configuración técnica del proyecto Django (settings, URLs, WSGI/ASGI). `apps/configuracion/` es el futuro módulo de parámetros del negocio (montos, plazos, notas mínimas, etc., sección 9 del documento de reglas), editable por el Administrador. Los valores del negocio nunca van en `config/settings.py`.

## Gestión del proyecto

Tablero kanban de tareas: https://github.com/users/juanjchavez/projects/3/views/1
