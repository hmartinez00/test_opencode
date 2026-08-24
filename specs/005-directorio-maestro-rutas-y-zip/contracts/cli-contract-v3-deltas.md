# Actualizacion de Contrato CLI: Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento registra los DELTAS del contrato CLI vigente (`specs/001-*/contracts/cli-contract.md` y `specs/003-*/contracts/orchestrator-contract.md`) derivados de la Iteracion 005. Todo lo no listado aqui permanece intacto.

---

## pra_helper.py

### Variable de entorno `PRA_OUTPUT_DIR` (Preexistente, con nuevo impacto)

| Variable | Default | Aplica a | Impacto Nuevo |
|---|---|---|---|
| `PRA_OUTPUT_DIR` | `C:\laragon\www\product_samples\slides` | Todos los comandos que crean o localizan proyectos | Si la ruta no existe, dispara prompt interactivo (TTY) o error (no-TTY). |

### Nueva Funcion Interna: `resolve_output_base_dir()`

- **Proposito**: Resuelve la ruta base de proyectos (`OUTPUT_BASE_DIR`), aplicando el valor por defecto, el override por `PRA_OUTPUT_DIR`, y la logica de validacion de existencia con interaccion CLI si es necesario.
- **Comportamiento**: 
    - Si la ruta no existe y `sys.stdin.isatty()` es `True`: muestra prompt por consola, solicita ruta, valida `os.path.isdir()`, reintenta 3 veces. 
    - Si la ruta no existe y `sys.stdin.isatty()` es `False`: emite un error JSON a STDOUT/STDERR y termina el proceso con `exit code 1`.

### save-plan

- **Cambio**: Antes de crear el directorio del proyecto, invoca `resolve_output_base_dir()` para obtener la ruta base real. El directorio del proyecto se crea en `<ruta_base_resuelta>/<carpeta_snake_case>/`.
- **Salida JSON**: campos `proyecto` y `archivos_creados[]` reportan las rutas actualizadas. Sin cambios de esquema.
- **Codigos de Salida**: `exit code 1` si `resolve_output_base_dir()` aborta por directorio base inexistente en entorno no-TTY o tras reintentos fallidos en TTY.

### prompt-session / process-session / status

- **Cambio**: La busqueda del proyecto activo (`find_project_dir()`) ahora utiliza la ruta resuelta por `resolve_output_base_dir()` como punto de partida prioritario para la busqueda, antes de aplicar el fallback a CWD para compatibilidad legacy.
- Sin cambios de argumentos, salidas ni codigos de error mas alla de los de `resolve_output_base_dir()`.

### zip

- **Cambio**: El entregable `outputs.zip` se escribe en `<project_dir>/outputs.zip` (ej. `C:\laragon\www\product_samples\slides\intro_docker\outputs.zip`), en lugar de directamente en `<OUTPUT_BASE_DIR>/outputs.zip`.
- **Cambio**: Durante la compresion, se excluye explicitamente cualquier archivo llamado `outputs.zip` dentro del arbol del proyecto para evitar la inclusion recursiva. 
- **Salida JSON**: el campo `archivo` en el JSON de exito (`{"status": "exito", "archivo": ...}`) reportara la nueva ruta absoluta del zip.
- **Codigos de Salida**: `exit code 1` si `resolve_output_base_dir()` aborta (como en `save-plan`). `exit code 2` en caso de error de compresion (`Error creando ZIP`).

---

## pra_orchestrator.py

### run / resume / status

- **Sin cambios** de argumentos, fases ni esquema de estado.
- **Cambio de comportamiento interno**: 
    - Al inicio de la fase `init`, se invoca una funcion interna (`_resolve_orchestrator_base_dir()`) que usa la logica de `resolve_output_base_dir()` de `pra_helper.py` pero forzando el modo no-interactivo. Si la ruta base no existe, el orquestador aborta con `exit code 1` (error de validacion) antes de comenzar cualquier fase de generacion.
    - `buscar_proyecto()` aplica la misma estrategia dual usando la ruta base resuelta.
    - La fase final `zip` valida la existencia de `outputs.zip` en la nueva ubicacion (`<project_dir>/outputs.zip`) y actualiza `orchestration_state.json` con esta ruta.
- `orchestration_state.json`: los valores de ruta para `proyecto_activo` y `ultimo_zip` referencian el arbol bajo la ruta base resuelta y la ubicacion del zip dentro del proyecto.

---

## Matriz de Codigos de Salida (Actualizacion)

| Codigo | Significado | Ejemplos |
|--------|-------------|----------|
| `0` | Exito | Corrida/resume completo; status impreso |
| `1` | Fallo de fase/sesion; aborto por reintentos agotados; **directorio maestro de salida inexistente en entorno no-TTY o tras reintentos interactivos** | CSS inline persistente; suite pytest fallida; JSON de plan malformado persistente; **error al resolver el directorio base en `pra_helper.py` o `pra_orchestrator.py`** |
| `2` | Error de estado/secuencialidad; **error de compresion ZIP** | `resume` sin corrida activa; estado corrupto; plan con 0 sesiones; **Error creando ZIP en `pra_helper.py`** |
| `3` | Backend LLM no disponible | `opencode` no encontrado; timeout del backend real |
| `4` | Uso incorrecto de la CLI | Backend desconocido; documento fuente inexistente; argumentos invalidos |
