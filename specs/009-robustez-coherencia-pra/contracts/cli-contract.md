# Contrato CLI - Iteracion 009 (Robustez y Coherencia del Flujo PRA)

**Especificacion**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

Este contrato describe los cambios en la interfaz CLI y en los reportes JSON de `pra_helper.py` y `pra_orchestrator.py` introducidos por la iteracion 009. No altera los comandos existentes ni sus argumentos; solo extiende los reportes de salida y endurece la resolucion del backend.

## `pra_helper.py consolidate`

**Comando**: `python pra_helper.py consolidate`

**Salida** (JSON en stdout) - campos nuevos:

```json
{
  "ok": true,
  "manifest": "manifest.blade.php",
  "sesiones": [1],
  "laminas_materializadas": 12,
  "includes_css": 1,
  "includes_js": 1,
  "coherencia": {"huerfanas": [], "faltantes": [], "duplicadas": []},
  "errores": []
}
```

**Condiciones**:

- `coherencia.huerfanas`: archivos `sesion[N]/*.blade.php` no declarados en el plan de esa sesion.
- `coherencia.faltantes`: ids del plan sin archivo en `sesion[N]/`.
- `coherencia.duplicadas`: ids repetidos en el plan.
- Si cualquier lista es no vacia: `ok` pasa a `false`, el campo `error` se fija a `"Incoherencia plan-vs-laminas"` y NO se genera el manifest incompleto.
- Exit code: `0` en exito, `2` ante incoherencia bloqueante (o el que se acuerde en T912; se documenta aqui al implementar).

## `pra_helper.py save-plan`

**Comando**: `python pra_helper.py save-plan '<plan_json>'`

**Salida** - campo nuevo `advertencias`:

```json
{
  "status": "exito",
  "proyecto": "...",
  "advertencias": ["..."],
  "archivos_creados": ["..."]
}
```

**Condiciones**:

- Si `class_registry["clases"]` y `js_registry["comportamientos"]` resultan vacios: advertencia de registros vacios.
- Si alguna lamina tiene `insumos` vacio/nulo: advertencia por lamina.
- Default: las advertencias no bloquean (`status: exito`).
- Con `PRA_PLAN_ESTRICTO=1`: las advertencias bloqueantes abortan el guardado (`status: error`, `PLAN_INCOMPLETO_ESTRICTO`).

## `pra_orchestrator.py run|resume --backend opencode`

**Comportamiento**:

- El backend resuelve el binario via `_resolver_binario_opencode()` (PATH + rutas conocidas).
- Si no se resuelve, NO se lanza `FileNotFoundError` crudo; se reporta `BACKEND_NO_DISPONIBLE`.

**Salida en estado/log**:

```json
{
  "backend": "opencode",
  "error": "BACKEND_NO_DISPONIBLE",
  "detalle": {
    "binarios_intentados": ["..."],
    "path_relevante": "..."
  }
}
```

## Seleccion del proyecto activo (ambiguedad)

- `find_project_dir` filtra directorios no-proyecto (`backup`, `themes`, etc.) al enumerar candidatos.
- Sin `PRA_ACTIVE_PROJECT` y con >1 candidato: advertencia en stderr listando los candidatos.
- Con `PRA_ACTIVE_PROJECT` valida: seleccion determinista sin advertencia.

## Resumen de cambios de contrato

| Comando | Cambio |
|---|---|
| `consolidate` | + campo `coherencia`; `ok:false` + exit != 0 ante incoherencia |
| `save-plan` | + campo `advertencias`; aborto con `PRA_PLAN_ESTRICTO=1` |
| `run`/`resume` backend opencode | resolucion robusta + diagnostico `BACKEND_NO_DISPONIBLE` |
| seleccion de proyecto activo | advertencia de ambiguedad |

## Retrocompatibilidad

- Consumidores previos de `consolidate` que lean `ok`/`manifest`/`sesiones` siguen funcionando (campos nuevos son aditivos).
- Consumidores previos de `save-plan` que lean `status`/`proyecto` siguen funcionando.
- Los comandos y argumentos existentes no cambian.
