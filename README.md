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

## Cómo levantar el servidor

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```

Abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en el navegador. `/admin/` ya funciona y muestra la pantalla de inicio de sesión.

## Estructura de carpetas

```
config/             Configuración técnica del proyecto Django (settings, urls, wsgi, asgi)
apps/
  personas/         Personas, usuarios, roles y login
  admision_cobranza/   Admisión y cobranza
  registro_academico/  Registro académico
  biblioteca/          Biblioteca
  configuracion/       Parámetros del negocio editables por el Administrador
manage.py
requirements.txt
```

Las carpetas de `apps/` son por ahora marcadores (`.gitkeep`): cada app se crea con `startapp` en el primer ticket que la necesite.

**`config/` no es lo mismo que `apps/configuracion/`.** `config/` es la configuración técnica del proyecto Django (settings, URLs, WSGI/ASGI). `apps/configuracion/` es el futuro módulo de parámetros del negocio (montos, plazos, notas mínimas, etc., sección 9 del documento de reglas), editable por el Administrador. Los valores del negocio nunca van en `config/settings.py`.

## Gestión del proyecto

Tablero kanban de tareas: https://github.com/users/juanjchavez/projects/3/views/1
