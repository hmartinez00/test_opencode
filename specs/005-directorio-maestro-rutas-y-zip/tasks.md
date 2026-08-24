# Lista de Tareas: Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento desglosa la implementacion de la Iteracion 005 en tareas especificas, organizadas por fases y con referencias a los requisitos y decisiones tecnicas.

---

## Fase 1: Refactorizacion del Motor (`pra_helper.py`)

- [ ] **T501** Definir `DEFAULT_OUTPUT_BASE_DIR = Path(r"C:\laragon\www\product_samples\slides")` en `pra_helper.py` (cerca de `OUTPUT_BASE_DIR`). (D-501, FR-501)
- [ ] **T502** Implementar `resolve_output_base_dir(interactive=True, stdin=sys.stdin, max_retries=3)` en `pra_helper.py`:
    - Prioriza `PRA_OUTPUT_DIR` de `os.environ`.
    - Si la ruta no existe:
        - Si `stdin.isatty()` (o el parametro `interactive` es `True`), solicita `input()` al usuario con 3 reintentos. (D-502, FR-503)
        - Si no es `isatty()`, aborta con `sys.exit(1)` y JSON de error `PRA_OUTPUT_DIR_INVALID`. (D-502, FR-504)
    - Retorna `Path` del directorio base validado. (D-501, FR-502)
- [ ] **T503** Modificar `get_project_dir(plan)` para usar `resolve_output_base_dir()` al obtener la base. (FR-508)
- [ ] **T504** Modificar `find_project_dir()` para usar `resolve_output_base_dir()` para la busqueda inicial, manteniendo el fallback a CWD. (FR-508)
- [ ] **T505** Modificar `cmd_zip(args)`:
    - Cambiar `zip_path = Path.cwd() / OUTPUT_BASE_DIR / "outputs.zip"` a `zip_path = project_dir / "outputs.zip"`. (D-503, FR-505)
    - Asegurar que `project_dir` exista antes de crear el zip (`project_dir.mkdir(parents=True, exist_ok=True)`). (FR-505)
    - Modificar el bucle `os.walk` para excluir recursivamente el propio `outputs.zip` de la compresion (FR-506).
- [ ] **T506** Modificar `cmd_save_plan(args)` para invocar `resolve_output_base_dir(interactive=True)` al inicio de la funcion para obtener la ruta base real donde se creara el proyecto. (FR-502)

## Fase 2: Adaptacion del Orquestador (`pra_orchestrator.py`)

- [ ] **T507** Replicar `DEFAULT_OUTPUT_BASE_DIR` en `pra_orchestrator.py` para mantener el desacoplamiento. (FR-501)
- [ ] **T508** Implementar `_resolve_orchestrator_base_dir()` en `pra_orchestrator.py` utilizando la logica de `resolve_output_base_dir` pero siempre en modo no-interactivo (`interactive=False`) para las fases `run`/`resume`. En caso de error, emitir error JSON y `sys.exit(1)`. (FR-504, FR-507)
- [ ] **T509** Modificar la fase `init` en `run_orchestration()` para llamar a `_resolve_orchestrator_base_dir()` y abortar si hay un error. (FR-507)
- [ ] **T510** Modificar `buscar_proyecto()` para usar `_resolve_orchestrator_base_dir()` para la base de busqueda inicial, manteniendo el fallback a CWD. (FR-508)
- [ ] **T511** Actualizar la fase `zip` en `run_orchestration()` para validar la existencia de `project_dir / "outputs.zip"` y actualizar `orchestration_state.json` con la nueva ruta de `ultimo_zip`. (FR-507)

## Fase 3: Desarrollo y Actualizacion de la Suite de Pruebas

- [ ] **T512** En `tests/conftest.py`, crear un fixture `mock_stdin_and_isatty(monkeypatch, capsys)` que permita:
    - Simular el retorno de `sys.stdin.isatty()`.
    - Mockear `input()` para devolver secuencias de strings predefinidas.
    - Capturar `sys.stdout` y `sys.stderr` para inspeccionar mensajes de prompt/error. (D-505, FR-509)
- [ ] **T513** Crear o modificar `tests/unit/test_output_base_dir.py` con los siguientes tests: (FR-509)
    - Asercion de `DEFAULT_OUTPUT_BASE_DIR`.
    - `resolve_output_base_dir()`: test de exito con directorio existente.
    - `resolve_output_base_dir()`: test de exito interactivo (con `mock_stdin_and_isatty`) con una ruta valida.
    - `resolve_output_base_dir()`: test de reintentos interactivos (con `mock_stdin_and_isatty`) con rutas invalidas.
    - `resolve_output_base_dir()`: test de aborto no-interactivo (con `mock_stdin_and_isatty`) con directorio inexistente.
    - Test de sobreescritura de `DEFAULT_OUTPUT_BASE_DIR` por `PRA_OUTPUT_DIR`.
    - Test de precedencia de busqueda en `find_project_dir()` (base resuelta > CWD).
- [ ] **T514** Modificar `tests/unit/test_zip_command.py` (o similar) para: (FR-509)
    - Test de la nueva ubicacion de `outputs.zip` dentro de `project_dir`.
    - Test de exclusion de `outputs.zip` del propio archivo comprimido. (SC-504)
- [ ] **T515** Actualizar aserciones de rutas en tests de integracion existentes (`test_cli_orchestrator_run.py`, etc.) y crear un test de integracion E2E para el escenario no-TTY con directorio inexistente, verificando el exit code y el mensaje de error JSON. (FR-509, SC-503)
- [ ] **T516** En `tests/constitutional/test_root_cleanup.py`, actualizar la whitelist para incluir la nueva ruta base por defecto (`C:\laragon\www\product_samples\slides`) y verificar que `outputs.zip` no aparece en la raiz de la base de salida. (FR-509)

## Fase 4: Actualizacion de Documentacion

- [ ] **T517** Actualizar `AGENTS.md` para reflejar la nueva ruta base por defecto y la ubicacion del `outputs.zip`. (FR-510)
- [ ] **T518** Actualizar `README.md` con las nuevas rutas y el comportamiento de la CLI (interactivo/no-interactivo). (FR-510)
- [ ] **T519** Actualizar `SESION_PRA_RESUMEN.md` con el resumen de la Iteracion 005. (FR-510)

---

## Verificacion Final

- [ ] **T520** Ejecutar `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing` y asegurar 100% de tests aprobados y cobertura >= 85% para ambos modulos. (SC-505)
- [ ] **T521** Validar manualmente los escenarios del `quickstart.md`.
