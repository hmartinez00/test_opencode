# Actualizacion de Contrato CLI: 004-subdirectorio-maestro-proyectos-pra

**Fecha**: 2026-08-24

Este documento registra los DELTAS del contrato CLI vigente (`specs/001-*/contracts/cli-contract.md` y `specs/003-*/contracts/orchestrator-contract.md`) derivados del subdirectorio maestro. Todo lo no listado aqui permanece intacto.

---

## pra_helper.py

### Variable de entorno (nueva)

| Variable | Default | Aplica a |
|---|---|---|
| `PRA_OUTPUT_DIR` | `output_projects` | Todos los comandos que crean o localizan proyectos |

### save-plan

- **Cambio**: el directorio del proyecto se crea en `<cwd>/output_projects/<carpeta_snake_case>/` en lugar de `<cwd>/<carpeta_snake_case>/`.
- **Salida JSON**: campos `proyecto` y `archivos_creados[]` reportan las rutas nuevas. Sin cambios de esquema ni codigos de salida.

### prompt-session / process-session

- **Cambio**: la busqueda del proyecto activo prioriza `<cwd>/output_projects/*/presentation_plan.json`; fallback al escaneo de la raiz solo si no hay proyecto en el maestro (compatibilidad legacy).
- Sin cambios de argumentos, salidas ni codigos.

### zip

- **Cambio**: el entregable se escribe en `<cwd>/output_projects/outputs.zip` (el subdirectorio maestro se crea si falta).
- Se conservan: recorrido recursivo del proyecto, `arcname` relativo y exclusiones de artefactos de orquestacion.
- Sin proyecto: error con codigo distinto de 0 (igual que antes).

---

## pra_orchestrator.py

### run / resume / status

- **Sin cambios** de argumentos, fases, esquema de estado ni codigos de salida (0/1/2/3/4).
- **Cambio de comportamiento interno**: `buscar_proyecto()` aplica la misma estrategia dual; las puertas post-sesion escanean laminas bajo `<maestro>/sesion[N]/`; la fase final valida `outputs.zip` dentro del maestro.
- `orchestration_state.json`: mismas claves; los valores de ruta referencian el arbol bajo el subdirectorio maestro.

---

## Matriz de codigos de salida (sin cambios)

| Codigo | Significado |
|---|---|
| 0 | Exito |
| 1 | Fallo de fase/sesion o aborto por reintentos agotados |
| 2 | Estado ausente/corrupto o plan invalido |
| 3 | Error de subprocess/backend |
| 4 | Argumento invalido |
