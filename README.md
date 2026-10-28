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

## Cómo levantar el servidor

```powershell
python manage.py check
python manage.py runserver
```

Abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en el navegador.

`/admin/` aún no funciona: no hay base de datos configurada todavía (se agrega en el ticket 2).

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
