# Plan: Proyecto Django y estructura de carpetas (issue #13)

**Branch**: main (el plan manda crear una rama de trabajo en el Paso 1)  
**Date**: 2026-10-28  
**Executing agent**: Claude Haiku  
**Issue**: https://github.com/juanjchavez/Sebinic-gestion/issues/13 (labels: `setup`, `tarea`; sin dependencias)

---

## Summary
Dejar un proyecto Django 5.2 que arranque en local (`manage.py check` y `runserver` sin errores), con el paquete de configuración `config/`, la carpeta `apps/` con las cinco carpetas marcadas con `.gitkeep`, ajustes de idioma/zona horaria, `.gitignore`, README y la sección "Comandos" de `CLAUDE.md` completada. Referencias: TEC-01, TEC-03, TEC-11.

## Context & Assumptions
- El repo hoy contiene solo `CLAUDE.md` (sin trackear) y `.artifacts/shared-understanding-seminario.md` (modificado, sin commitear). **No son parte de este ticket salvo la sección "Comandos" de `CLAUDE.md`.**
- Entorno de la máquina: **Windows 11, PowerShell**. Usar rutas con `\` y comandos PowerShell. **No activar el venv** (evita problemas de ExecutionPolicy): invocar siempre `.\.venv\Scripts\python.exe` directamente.
- Verificación previa hecha por quien planeó: el lanzador `py` **no está** en el PATH y `python.exe` es el stub de la Microsoft Store (`C:\Users\juan_\AppData\Local\Microsoft\WindowsApps\python.exe`). Es muy probable que **Python 3.11 no esté instalado**; `winget` sí existe. Git 2.56 ya está instalado.
- Reglas de negocio: este ticket **no toca lógica de negocio** (ninguna regla COB/REG/BIB/ACC, ningún pendiente ★). Solo estructura técnica: TEC-01 (Django 5.2 LTS, monolito), TEC-03 (Python 3.11, venv por proyecto), TEC-11 (las cinco apps y sus nombres exactos).
- Nombres de apps (inmutables): `personas`, `admision_cobranza`, `registro_academico`, `biblioteca`, `configuracion`.
- Fuera de alcance (NO hacer): `startapp`, variables de entorno / `.env` / `SECRET_KEY` por entorno, PostgreSQL / `DATABASES` / `psycopg`, pruebas (`pytest`), despliegue / gunicorn, migraciones, `createsuperuser`.
- Las dependencias de `requirements.txt` son **solo** `Django>=5.2,<5.3` (según el issue). En Windows, Django instala `tzdata` automáticamente (necesario para `America/Managua`); no agregarlo a mano.
- Supuesto: nombre de rama `feature/13-proyecto-django` (el repo no tiene convención definida todavía).
- Commit: los criterios "las cinco carpetas existen en git" y "un clon limpio funciona" solo se pueden demostrar con lo que está en git. Por eso el plan hace **un commit en la rama** (Paso 12), **solo con confirmación previa del usuario** y agregando archivos por nombre, y luego valida con un `git clone` real (Paso 13). Sin push ni PR. Si el usuario no autoriza el commit, los Pasos 12 y 13 no se ejecutan y esos dos criterios se reportan como **pendientes del commit**, no como cumplidos.

## Execution Steps

### Step 1 — Crear la rama de trabajo
**Goal:** no escribir nada en `main`. Debe ocurrir antes de crear cualquier archivo.  
**Actions:**
- `git status --short` (anotar lo que ya aparece: `M .artifacts/shared-understanding-seminario.md` y `?? CLAUDE.md`; son cambios previos del usuario, no tuyos).
- `git switch -c feature/13-proyecto-django` (los cambios sin commitear viajan con la rama; es lo esperado).

**Verification:** `git branch --show-current` imprime `feature/13-proyecto-django`.  
**If it fails:** si el nombre de rama ya existe, usar `git switch feature/13-proyecto-django`. Si falla por otra razón, detenerse y reportar el error textual.  
**Depends on:** none

### Step 2 — Agregar `.gitignore`
**Goal:** que `.venv/`, cachés y futuros archivos sensibles nunca entren a git; hacerlo antes de crear el venv para que `git status` quede limpio.  
**Actions:**
- Crear `.gitignore` en la raíz del repo con exactamente estas líneas (una por línea):
  ```
  .venv/
  __pycache__/
  .env
  media/
  staticfiles/
  ```
- No agregar nada más (ni `db.sqlite3`, ni `claude/`, ni `*.pyc`): el issue lista solo esas cinco entradas.

**Verification:** `Get-Content .gitignore` muestra las 5 líneas. `git check-ignore -v .venv/x __pycache__/x .env media/x staticfiles/x` devuelve una línea por cada ruta (todas ignoradas).  
**If it fails:** corregir el archivo (verificar que no tenga BOM raro: si se escribe con `Set-Content` usar `-Encoding utf8`; mejor usar la herramienta Write).  
**Depends on:** Step 1

### Step 3 — Verificar o instalar prerrequisitos (Python 3.11 y Git)
**Goal:** tener exactamente Python 3.11 (misma versión que el VPS, TEC-03) y Git antes de crear el entorno virtual.  
**Actions:**
- `git --version` (debe imprimir una versión; ya existe en esta máquina).
- `py -3.11 --version`.
- Si `py` no se reconoce o no existe 3.11: ejecutar `winget install Python.Python.3.11` (es un paso real, previsto por el issue; **pedir confirmación al usuario antes de instalar** porque descarga e instala software). El instalador de python.org trae el lanzador `py`.
- Tras instalar, **abrir un shell nuevo** (el PATH no se refresca en el shell actual) o llamar al lanzador con ruta completa: `& "$env:LOCALAPPDATA\Programs\Python\Launcher\py.exe" -3.11 --version` o `& "C:\Windows\py.exe" -3.11 --version`.
- No usar el `python.exe` de `WindowsApps` (es un stub de la Store, no sirve).

**Verification:** `py -3.11 --version` (o la ruta completa al lanzador) imprime `Python 3.11.x`.  
**If it fails:** si `winget` falla o el usuario no autoriza la instalación, **detenerse** y pedirle al usuario que instale Python 3.11 desde python.org; no continuar con otra versión de Python.  
**Depends on:** Step 1

### Step 4 — Crear el entorno virtual
**Goal:** aislar dependencias en `.venv/` (ignorado por git).  
**Actions:**
- En la raíz del repo: `py -3.11 -m venv .venv` (usar la ruta completa del lanzador si el Paso 3 lo requirió).

**Verification:** `.\.venv\Scripts\python.exe --version` imprime `Python 3.11.x`.  
**If it fails:** si ya existe `.venv` con otra versión, **no borrarla sin preguntar**; reportar al usuario.  
**Depends on:** Step 3

### Step 5 — Crear `requirements.txt` e instalar Django
**Goal:** dependencias declaradas y Django 5.2 instalado en el venv.  
**Actions:**
- Crear `requirements.txt` en la raíz con una sola línea: `Django>=5.2,<5.3`
- `.\.venv\Scripts\python.exe -m pip install --upgrade pip` (opcional, solo si pip avisa de versión antigua).
- `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

**Verification:** `.\.venv\Scripts\python.exe -m django --version` imprime una versión `5.2.x`.  
**If it fails:** si falla la descarga por red, reintentar una vez; si persiste, detenerse y reportar. No cambiar el rango de versión.  
**Depends on:** Step 4

### Step 6 — Crear el proyecto `config` en la raíz
**Goal:** generar `manage.py` y el paquete `config/` (settings, urls, wsgi, asgi) en la raíz del repo, **no** en una subcarpeta.  
**Actions:**
- `.\.venv\Scripts\python.exe -m django startproject config .` (el punto final es obligatorio).

**Verification:** existen `manage.py`, `config\settings.py`, `config\urls.py`, `config\wsgi.py`, `config\asgi.py`, `config\__init__.py`. NO existe `config\config\`.  
**If it fails:** si creó una carpeta anidada por olvidar el punto, borrar solo lo que acabas de crear (`manage.py` y `config\` generados) y repetir correctamente. Si hay otro error, reportar.  
**Depends on:** Step 5

### Step 7 — Ajustar `config/settings.py`
**Goal:** quitar el bloque SQLite (la base de datos se define en el ticket 2) y fijar idioma y zona horaria.  
**Actions:** editar `config\settings.py` con la herramienta Edit (cambios exactos):
1. **Eliminar** el bloque completo `DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3', } }` junto con sus dos líneas de comentario previas (`# Database` y la URL de docs). En su lugar dejar un único comentario: `# DATABASES se define en el ticket 2 (PostgreSQL, por variables de entorno).`
2. `LANGUAGE_CODE = 'en-us'` → `LANGUAGE_CODE = 'es-ni'`
3. `TIME_ZONE = 'UTC'` → `TIME_ZONE = 'America/Managua'`
4. Dejar `USE_TZ = True` (ya viene así; confirmar que está).
5. Mantener el estilo de comillas que genera `startproject` (comillas simples) para no ensuciar el diff.
6. **No tocar** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `INSTALLED_APPS`, `MIDDLEWARE` ni lo demás.

**Verification:**
- `Select-String -Path config\settings.py -Pattern "sqlite3|DATABASES"` solo debe encontrar el comentario nuevo (no `sqlite3`).
- `Select-String -Path config\settings.py -Pattern "LANGUAGE_CODE|TIME_ZONE|USE_TZ"` muestra `es-ni`, `America/Managua`, `True`.
- `.\.venv\Scripts\python.exe manage.py check` imprime `System check identified no issues (0 silenced).`

**If it fails:** si `check` reporta un error mencionando `DATABASES` o `ImproperlyConfigured`, **no reintroducir SQLite**; detenerse y reportar el mensaje textual. Si reporta un error de idioma (`translation.E004`), verificar que el valor sea exactamente `es-ni` (minúsculas, guion).  
**Depends on:** Step 6

### Step 8 — Crear `apps/` con las cinco carpetas y sus `.gitkeep`
**Goal:** dejar marcada la estructura de TEC-11 en git, sin generar apps todavía.  
**Actions:**
- Crear estos cinco archivos vacíos (cada uno crea su carpeta):
  - `apps\personas\.gitkeep`
  - `apps\admision_cobranza\.gitkeep`
  - `apps\registro_academico\.gitkeep`
  - `apps\biblioteca\.gitkeep`
  - `apps\configuracion\.gitkeep`
- PowerShell: `foreach ($a in 'personas','admision_cobranza','registro_academico','biblioteca','configuracion') { New-Item -ItemType Directory -Force "apps\$a" | Out-Null; New-Item -ItemType File "apps\$a\.gitkeep" -Force | Out-Null }`
- **No** crear `__init__.py` ni `apps.py` (no se usa `startapp`; cada app nace en el primer ticket que la necesite). **No** crear `apps\.gitkeep` ni `apps\__init__.py`.

**Verification:** `Get-ChildItem apps -Recurse -Force | Select-Object FullName` lista exactamente las 5 carpetas y los 5 `.gitkeep`, nada más. Luego `git status --short -uall` muestra las cinco rutas `apps/<nombre>/.gitkeep` como no trackeadas (es decir, git las ve; no están ignoradas).  
**If it fails:** si algún nombre quedó mal escrito, renombrar/borrar solo lo que creaste en este paso. Los nombres deben coincidir letra por letra con TEC-11.  
**Depends on:** Step 1

### Step 9 — Escribir el `README.md`
**Goal:** que alguien con una máquina Windows limpia pueda levantar el proyecto solo con el README (criterio del issue).  
**Actions:** crear `README.md` en la raíz, **en español**, con estas secciones (usar términos del proyecto: "Seminario Bíblico Nicaragüense"):
1. **Descripción**: una o dos líneas (sistema de gestión del seminario: admisión y cobranza, registro académico y biblioteca). Mencionar que las reglas del negocio están en `.artifacts/shared-understanding-seminario.md`.
2. **Prerrequisitos**: Python 3.11.x (misma versión menor que el VPS; el parche puede diferir, porque python.org ya no publica instaladores de Windows para los parches de seguridad de 3.11), verificar con `py -3.11 --version`, instalar con `winget install Python.Python.3.11` si falta (abrir una terminal nueva después); Git, verificar con `git --version`.
3. **Instalación** (PowerShell, desde la raíz del repo, en este orden):
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   Añadir una nota: si PowerShell bloquea `Activate.ps1`, ejecutar los comandos con `.\.venv\Scripts\python.exe -m ...` sin activar el entorno.
4. **Cómo levantar el servidor**: `python manage.py check` y `python manage.py runserver`, abrir `http://127.0.0.1:8000/`. Aclarar que `/admin/` aún no funciona hasta el ticket 2 (no hay base de datos configurada).
5. **Estructura de carpetas**: árbol corto con `config/`, `apps/` (las cinco carpetas con una línea que diga qué es cada una según el glosario/TEC-11: `personas` = personas, usuarios, roles y login; `admision_cobranza`; `registro_academico`; `biblioteca`; `configuracion` = parámetros editables por el Administrador), `manage.py`, `requirements.txt`. Aclarar que las carpetas de `apps/` son marcadores (`.gitkeep`) y cada app se crea con `startapp` en el primer ticket que la necesite.
   - Incluir una línea explícita que distinga `config/` de `apps/configuracion/`: `config/` es la configuración técnica del proyecto Django (settings, URLs, WSGI/ASGI); `apps/configuracion/` es el módulo de parámetros del negocio (montos, plazos, notas mínimas, etc., sección 9 del documento), editables por el Administrador. Los valores del negocio **nunca** van en `config/settings.py`.
6. **Gestión del proyecto**: enlace al tablero https://github.com/users/juanjchavez/projects/3/views/1

No inventar comandos que aún no existen (pruebas, despliegue, PostgreSQL).

**Verification:** `README.md` existe, es UTF-8 con acentos correctos (`Get-Content README.md -Encoding utf8 | Select-String "Seminario Bíblico"` encuentra la línea), y las cinco apps aparecen escritas exactamente como en TEC-11.  
**If it fails:** si los acentos salen corruptos, reescribir con la herramienta Write (UTF-8) en lugar de redirecciones de PowerShell.  
**Depends on:** Step 7, Step 8

### Step 10 — Completar la sección "Comandos" de `CLAUDE.md`
**Goal:** que `CLAUDE.md` deje de decir "Aún no hay código" y documente los comandos reales.  
**Actions:**
- Leer `CLAUDE.md` y localizar la sección `## Comandos` (es la última). Reemplazar **solo** su cuerpo (el párrafo "Aún no hay código en el repositorio. Cuando se cree el proyecto Django, documentar aquí…") por comandos en un bloque `powershell`, en español, solo los que ya funcionan:
  - Instalación: `py -3.11 -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`
  - Verificación: `python manage.py check`
  - Ejecución local: `python manage.py runserver`
  - Una línea indicando que migraciones, pruebas y despliegue se documentarán cuando existan (tickets 2 y 3), y que las cinco carpetas de `apps/` son marcadores `.gitkeep` hasta que se cree cada app con `startapp`.
- No modificar ninguna otra sección de `CLAUDE.md` (stack, reglas de oro, convenciones).

**Verification:** `Select-String -Path CLAUDE.md -Pattern "Aún no hay código"` no devuelve nada, y al releer la sección `## Comandos` los comandos coinciden con los del README.  
**If it fails:** si no encuentras el texto exacto para el Edit, leer el archivo otra vez y copiar la cadena literalmente; no reescribir el archivo entero.  
**Depends on:** Step 7, Step 9

### Step 11 — Verificación local
**Goal:** comprobar `check`, `runserver` y el estado del árbol de trabajo antes de commitear.  
**Actions:**
1. `.\.venv\Scripts\python.exe manage.py check` → debe decir `no issues`.
2. `.\.venv\Scripts\python.exe manage.py runserver 8000` **en segundo plano** (run_in_background); esperar ~5 s; revisar su salida: no debe haber `Traceback` ni `Error`. Comprobar con `Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing | Select-Object -ExpandProperty StatusCode` (esperado `200`; es la página por defecto de Django, que aparece porque `DEBUG = True` y solo existe la ruta `admin/`). **Detener el servidor** al terminar (parar la tarea en segundo plano / `Stop-Process` solo del proceso que arrancaste).
3. Confirmar las cinco carpetas: `git status --short -uall` lista `apps/<nombre>/.gitkeep` para las cinco, con los nombres de TEC-11 y de `CLAUDE.md`.
4. `git status --short -uall`: además de los cambios previos del usuario (`.artifacts/…` y `claude/…`), deben aparecer solo los archivos esperados (ver Success Criteria). No deben aparecer `.venv/`, `__pycache__/` ni `db.sqlite3`.

**Verification:** los cuatro puntos anteriores pasan.  
**If it fails:** si falla por algo del entorno (red, Python), reportar sin parchear. No resolver fallos agregando dependencias o settings fuera del alcance (en particular, no reintroducir SQLite).  
**Depends on:** Step 2, Step 8, Step 9, Step 10

### Step 12 — Commit en la rama (con confirmación del usuario)
**Goal:** que los entregables existan en git, requisito de los criterios "las cinco carpetas existen en git" y "un clon limpio funciona".  
**Actions:**
1. **Pedir confirmación al usuario** antes de commitear, mostrándole la lista exacta de archivos del punto 2. Si no la da, **no ejecutar este paso ni el 13**: saltar al reporte final y marcar esos dos criterios como "pendientes del commit".
2. Agregar **por nombre** (nunca `git add -A` ni `git add .`):
   `git add .gitignore README.md requirements.txt manage.py config/__init__.py config/settings.py config/urls.py config/wsgi.py config/asgi.py apps/personas/.gitkeep apps/admision_cobranza/.gitkeep apps/registro_academico/.gitkeep apps/biblioteca/.gitkeep apps/configuracion/.gitkeep CLAUDE.md`
   (`CLAUDE.md` va incluido porque "CLAUDE.md actualizado" es un entregable del issue. **No** agregar `.artifacts/` ni `claude/`.)
3. `git diff --cached --name-only` debe listar exactamente esos 15 archivos. Si aparece otro, quitarlo con `git restore --staged <ruta>`.
4. Commit con este mensaje (here-string de PowerShell, `'@` en la columna 0):
   ```
   Crea el proyecto Django y la estructura de apps (#13)

   Proyecto config/ con Django 5.2, idioma es-ni y zona America/Managua,
   sin base de datos hasta el ticket 2. Carpetas de las cinco apps de
   TEC-11 marcadas con .gitkeep, README y comandos en CLAUDE.md.

   Refs: TEC-01, TEC-03, TEC-11

   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
   ```
5. **No** hacer push ni abrir PR.

**Verification:** `git log -1 --stat` muestra el commit con los 15 archivos en la rama `feature/13-proyecto-django`; `git status --short` ya no lista ninguno de ellos.  
**If it fails:** si un hook de pre-commit falla, reportar el error textual; no usar `--no-verify`.  
**Depends on:** Step 11

### Step 13 — Validar con un clon limpio siguiendo solo el README
**Goal:** comprobar el criterio "un clon limpio funciona siguiendo solo el README" contra lo que realmente está en git.  
**Actions:**
1. Verificar que `$env:TEMP\seminario-clean-check` **no exista**; si existe, detenerse y preguntar (no la creaste tú).
2. `git clone --branch feature/13-proyecto-django C:\Users\juan_\repos\Python\seminario-management "$env:TEMP\seminario-clean-check"`
3. Dentro de esa carpeta, ejecutar **solo los comandos que dice el README**, en su orden (prerrequisitos, venv, `pip install -r requirements.txt`, `check`, `runserver`). Si el README propone activar el venv y PowerShell lo bloquea, usar la alternativa que el propio README documenta. Usar el puerto `8001` para `runserver` (para no chocar con otro servidor) y comprobar `200` en `http://127.0.0.1:8001/`; detener ese servidor.
4. Confirmar que existen las cinco rutas `apps\<nombre>\.gitkeep` en el clon.
5. Borrar `$env:TEMP\seminario-clean-check` (solo esa carpeta, que creaste en este paso).

**Verification:** en el clon, `check` dice `no issues`, `/` responde `200` y las cinco carpetas existen.  
**If it fails:** si falla porque el README omite o equivoca algo, **corregir el README** (y la sección "Comandos" de `CLAUDE.md` si aplica), hacer un **commit nuevo** en la rama agregando esos archivos por nombre (sin `--amend`; la confirmación del Paso 12 cubre este arreglo) y repetir este paso desde el punto 1. Si falla por el entorno (red, Python), reportar sin parchear.  
**Depends on:** Step 12

## Available Skills
- Step 1 → no skill needed
- Step 2 → no skill needed
- Step 3 → no skill needed (pedir confirmación al usuario antes de `winget install`)
- Step 4 → no skill needed
- Step 5 → no skill needed
- Step 6 → no skill needed
- Step 7 → no skill needed
- Step 8 → no skill needed
- Step 9 → no skill needed
- Step 10 → no skill needed
- Step 11 → no skill needed
- Step 12 → no skill needed (no usar `git-commit`: infiere un código `KTC-###` de la rama, que no aplica a este repo; usar el mensaje del paso)
- Step 13 → no skill needed

## Project Checklist
- [ ] Nombres de las cinco apps idénticos a TEC-11: `personas`, `admision_cobranza`, `registro_academico`, `biblioteca`, `configuracion`.
- [ ] Django en `>=5.2,<5.3` (TEC-01) y venv con Python 3.11 (TEC-03).
- [ ] `startproject` ejecutado con punto final: `manage.py` y `config/` en la raíz.
- [ ] No hay bloque `DATABASES`, ni SQLite, ni `db.sqlite3` en el repo (la BD es PostgreSQL 17, ticket 2).
- [ ] No se usó `startapp`; no hay `apps.py` ni `__init__.py` en `apps/`.
- [ ] Regla de oro 1 (sin valores fijos): este ticket no introduce montos ni parámetros de negocio. `settings.py` solo recibe idioma, zona horaria y `USE_TZ`.
- [ ] UI/textos en español; README y `CLAUDE.md` consistentes entre sí en los comandos.
- [ ] `.gitignore` con exactamente las 5 entradas del issue.

## Success Criteria
- `.\.venv\Scripts\python.exe manage.py check` termina con `System check identified no issues (0 silenced).`
- `runserver` arranca sin `Traceback` y `http://127.0.0.1:8000/` responde HTTP 200.
- Antes del commit, `git status --short -uall` muestra (además de los cambios previos del usuario en `.artifacts/` y `claude/`) únicamente: `CLAUDE.md`, `.gitignore`, `README.md`, `requirements.txt`, `manage.py`, `config/*` (5 archivos) y las cinco rutas `apps/<nombre>/.gitkeep`. No aparecen `.venv/`, `__pycache__/`, `db.sqlite3` ni `staticfiles/`.
- `Select-String config\settings.py -Pattern "es-ni","America/Managua"` encuentra ambos; `USE_TZ = True`.
- El commit de la rama `feature/13-proyecto-django` contiene exactamente esos 15 archivos (Paso 12).
- Un `git clone` de la rama levanta siguiendo solo el README (Paso 13).
- Si el usuario no autorizó el commit: el reporte final marca "existen en git" y "clon limpio" como **pendientes del commit**.
- `CLAUDE.md` ya no contiene "Aún no hay código" y su sección "Comandos" coincide con el README.

## Potential Risks & Blockers
- **Blocker:** Python 3.11 no instalado (probable) → **Resolution:** `winget install Python.Python.3.11` con autorización del usuario; abrir shell nuevo para refrescar PATH. Si no se autoriza, detenerse.
- **Risk:** el `python.exe` de WindowsApps (stub de la Store) se usa por error → **Mitigation:** usar siempre `py -3.11` y luego `.\.venv\Scripts\python.exe`.
- **Risk:** `Activate.ps1` bloqueado por la ExecutionPolicy → **Mitigation:** el plan nunca activa el venv; el README deja la nota alternativa.
- **Risk:** `startproject` genera una `SECRET_KEY` (`django-insecure-…`) que entraría al historial de git, contra la regla "secretos solo por variables de entorno" → **Mitigation:** el issue difiere las variables de entorno al ticket 2, y es una clave de desarrollo que no se usará en producción. Dejarla tal cual aquí. El ticket 2 (#14) ya exige que `SECRET_KEY` sea obligatoria y que el arranque falle si falta; además debe generar una clave **nueva** y no reutilizar esta (ni como valor por defecto, ni en `.env`, ni en `.env.example`), porque queda publicada en el historial de git. Mencionarlo en el reporte final.
- **Risk:** `runserver` sin `DATABASES` falla en rutas que usan sesiones/BD (p. ej. `/admin/`) → **Mitigation:** es esperado y está documentado en el issue; `/admin/` se valida en el ticket 2. Solo se prueba `/`. (No aparece el aviso de migraciones sin aplicar: Django lo omite cuando no hay base de datos configurada.)
- **Risk:** confundir `config/` (settings de Django) con `apps/configuracion/` (parámetros del negocio) y terminar poniendo montos o plazos en `settings.py` → **Mitigation:** el README los distingue explícitamente (Paso 9).
- **Risk (futuro, no actuar):** al ejecutar `startapp` en un ticket posterior sobre una carpeta que ya contiene `.gitkeep`, funciona (la carpeta debe existir), pero hay que borrar el `.gitkeep` y ajustar `AppConfig.name` a `apps.<nombre>`. Decidir ese día si `apps/` lleva `__init__.py`. Fuera del alcance de este ticket.
- **Risk:** `git add -A` / `git add .` arrastraría `claude/plans/` o `.artifacts/` sin intención → **Mitigation:** el Paso 12 agrega los 15 archivos por nombre y verifica el staging con `git diff --cached --name-only`.

## Notes for Executing Agent
- DO: trabajar siempre desde la raíz del repo (`C:\Users\juan_\repos\Python\seminario-management`) con PowerShell; invocar Python vía `.\.venv\Scripts\python.exe`.
- DO: pedir confirmación al usuario antes de `winget install`, antes del commit del Paso 12 y antes de borrar cualquier cosa que no hayas creado tú.
- DO: usar las herramientas Write/Edit para crear y modificar archivos (UTF-8, acentos correctos).
- DO: reportar al final qué quedó commiteado y qué no (`.artifacts/` y `claude/` quedan fuera a propósito), y recordar que `SECRET_KEY` por entorno es trabajo del ticket 2 (#14).
- DO NOT: hacer push ni abrir PR. Nunca `git add -A` ni `git add .`; nunca `--amend` ni `--no-verify`.
- DO NOT: ejecutar `startapp`, `migrate`, `makemigrations`, `createsuperuser`; instalar `psycopg`, `pytest`, `gunicorn` o cualquier paquete que no sea Django; crear `.env`.
- DO NOT: modificar `.artifacts/shared-understanding-seminario.md`, ni otras secciones de `CLAUDE.md`, ni `INSTALLED_APPS`.
- DO NOT: renombrar o traducir los nombres de las apps ni "mejorar" la estructura (por ejemplo `src/`, `settings/` dividido, `apps/__init__.py`).
- If uncertain at any point: stop and report to the user rather than guessing.
