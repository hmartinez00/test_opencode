# Plan de Implementacion: Robustez y Coherencia del Flujo PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Decisiones**: [research.md](./research.md) | **Contrato**: [contracts/cli-contract.md](./contracts/cli-contract.md)

## 1. Enfoque TDD (red-green-refactor)

Esta iteracion se implementa con desarrollo guiado por pruebas:

1. **Rojo**: Se escriben primero las pruebas que reproducen los cuatro inconvenientes detectados (deben fallar con el codigo actual: lamina huerfana omitida, plan sin registros guardado sin aviso, backend opencode no resuelto, ambiguedad silenciosa).
2. **Verde**: Se implementan las funciones nuevas y se ajustan las existentes hasta que pasen.
3. **Refactor**: Se limpia el codigo sin cambiar comportamiento; la suite completa debe seguir en verde (133 pruebas actuales) y la cobertura de ambos modulos debe ser >= 85%.

El detalle de cada prueba se documenta en [test_plan.md](./test_plan.md).

## 2. Arquitectura propuesta

```text
pra_helper.py
  ├── _consolidate_project:     + oracle de coherencia (D1, D2, D3)
  ├── save_plan:                + validacion de calidad con umbral (D4)
  └── find_proyecto_activo:     + deteccion de ambiguedad (D6)

pra_orchestrator.py
  ├── OpenCodeBackend:          + resolucion robusta del binario (D5, D8)
  └── main/run:                 + diagnostico BACKEND_NO_DISPONIBLE
```

## 3. Cambios en `pra_helper.py`

### 3.1 Oracle de coherencia en consolidacion

Nueva funcion `_analizar_coherencia(plan, project_dir) -> dict` que, por sesion:

1. Lee el conjunto de `id` declarados: `{ lamina.get("id_kebab_case") or lamina.get("id") for lamina in sesion.get("laminas", []) }`.
2. Lee el conjunto de archivos reales: `{ p.stem for p in (project_dir / f"sesion{numero}").glob("*.blade.php") }` (si el dir existe).
3. Deteccion de `huerfanas`: archivos en FS no declarados.
4. Deteccion de `faltantes`: declarados no presentes en FS.
5. Deteccion de `duplicadas`: ids repetidos en todo el plan (conjunto de sesiones).

```python
def _analizar_coherencia(plan, project_dir):
    """Retorna {'huerfanas': [], 'faltantes': [], 'duplicadas': []} con info diagnostica."""
    ...

def _consolidate_project(project_dir):
    ...
    coherencia = _analizar_coherencia(plan, project_dir)
    incoherente = any(coherencia[k] for k in ("huerfanas", "faltantes", "duplicadas"))
    if incoherente:
        return {"ok": False, "error": "Incoherencia plan-vs-laminas",
                "coherencia": coherencia, ...}
    # ... consolidacion normal solo si es coherente
```

Las entradas de cada lista llevan forma `{"sesion": N, "id": "...", "sugerencia": "..."}`.

### 3.2 Validacion de calidad del plan en `save-plan`

Nueva funcion `_validar_calidad_plan(plan) -> list[advertencias]`:

1. Si `class_registry["clases"]` y `js_registry["comportamientos"]` quedarian vacios -> advertencia de registros vacios.
2. Por cada lamina, si `insumos` es vacio o nulo -> advertencia "lamina sin insumos".

En `cmd_save_plan`:
- Emitir advertencias (stderr y en el JSON de salida, campo `advertencias`).
- Si la variable de entorno `PRA_PLAN_ESTRICTO=1` y hay advertencias bloqueantes -> abortar con exit code y JSON de error.

### 3.3 Deteccion de ambiguedad del proyecto activo

En la funcion de seleccion de proyecto activo (`find_project_dir` o auxiliar):
- Enumerar candidatos validos bajo la ruta base, excluyendo directorios no-proyecto (`backup`, `themes`, etc.).
- Si `PRA_ACTIVE_PROJECT` esta definida: usarla (comportamiento actual de la iteracion 007).
- Si no, y hay >1 candidato: emitir advertencia (stderr) listando los candidatos antes de aplicar el criterio por defecto. Mantener determinismo.

## 4. Cambios en `pra_orchestrator.py`

### 4.1 Resolucion robusta del binario `opencode`

Nueva funcion (fuera de la clase o estatica) `_resolver_binario_opencode() -> str | None`:

1. `shutil.which("opencode")` -> si existe, retornar.
2. Rutas conocidas para el SO actual:
   - `Path.home() / ".opencode" / "bin" / ("opencode.exe" si win32 else "opencode")`
   - `Path.home() / "AppData" / "Roaming" / "npm" / "opencode.cmd"` (win32)
   - `shutil.which("opencode")` con el PATH de `os.environ` reforzado con rutas `.opencode/bin`.
3. Retornar la primera que exista y sea ejecutable, o `None`.

El backend `OpenCodeBackend` usa esta resolucion; si es `None`, en lugar de lanzar FileNotFoundError, el orquestador reporta `BACKEND_NO_DISPONIBLE` con las rutas intentadas y un fragmento de PATH, devolviendo el codigo de salida de error interno.

```python
def _resolver_binario_opencode():
    from shutil import which
    import os
    candidatos = []
    w = which("opencode")
    if w:
        return w
    home = Path.home()
    if os.name == "nt":
        candidatos += [home / ".opencode" / "bin" / "opencode.exe",
                       home / "AppData" / "Roaming" / "npm" / "opencode.cmd"]
    else:
        candidatos += [home / ".opencode" / "bin" / "opencode"]
    for c in candidatos:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)
    return None
```

### 4.2 Diagnostico `BACKEND_NO_DISPONIBLE`

En `run` (y `resume`), al validar el backend: si es `opencode` y `_resolver_binario_opencode()` es `None`, registrar en el estado y el log un error estructurado y salir con el codigo de error interno, sin traceback crudo.

## 5. Cambios en fixtures/conftest (no-regresion)

- `tests/conftest.py`: los fixtures `sample_plan_json_str` y `sample_llm_response_s1` deben permanecer coherentes (las laminas del plan coinciden con las escritas en `sesion1/`). Si se introducen nuevas laminas en fixtures, deben declararse en el plan correspondiente.

## 6. Validacion estructural post-consolidacion

- `manifest.blade.php` referencia exactamente las laminas preservadas en `session[N]/`.
- No hay laminas huerfanas ni faltantes en ninguna sesion consolidada.
- `save-plan` advierte de planes incompletos.
- El orquestador `--backend opencode` resuelve el binario o reporta diagnostico claro.
- Con varios proyectos y sin `PRA_ACTIVE_PROJECT`, se advierte la ambiguedad.

## 7. Pruebas TDD

Ver [test_plan.md](./test_plan.md) para la lista completa. Resumen por ubicacion:

- `tests/unit/`: `_analizar_coherencia` (huerfanas/faltantes/duplicadas), `_validar_calidad_plan`, `_resolver_binario_opencode`, ambiguedad de proyecto activo.
- `tests/integration/`: `consolidate` aborta ante lamina huerfana; `save-plan` advierte sin bloquear y bloquea con `PRA_PLAN_ESTRICTO`.
- `tests/constitutional/`: la consolidacion nunca entrega un manifest incompleto ante incoherencia.

## 8. Documentacion a actualizar despues de la implementacion

- `README.md`: documentar el oracle de coherencia, la validacion de calidad del plan (`PRA_PLAN_ESTRICTO`) y la resolucion robusta del backend `opencode`.
- `AGENTS.md`: actualizar el flujo y las notas de robustez (amarguedad de proyecto, backend).
- `specs/001.../contracts/cli-contract.md` y `specs/003.../contracts/orchestrator-contract.md`: reflejar los nuevos campos de reporte y el diagnostico del backend.
- `SESION_PRA_RESUMEN.md`: registrar la iteracion 009.

## 9. Secuencia de implementacion

1. Escribir pruebas rojas (test_plan.md -> archivos en `tests/`).
2. Implementar `_analizar_coherencia` + integracion en `_consolidate_project`.
3. Implementar `_validar_calidad_plan` + integracion en `cmd_save_plan` + umbral `PRA_PLAN_ESTRICTO`.
4. Implementar `_resolver_binario_opencode` + diagnostico en `pra_orchestrator.py`.
5. Implementar deteccion de ambiguedad del proyecto activo en `pra_helper.py`.
6. Refactorizar y ejecutar la suite + cobertura.

## 10. Criterios de finalizacion

- Suite completa en verde.
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
- Una lamina fuera del plan hace que `consolidate` devuelva `ok: false` con el bloque `coherencia`.
- `save-plan` advierte de planes sin registros/insumos y bloquea solo con `PRA_PLAN_ESTRICTO=1`.
- `--backend opencode` resuelve el binario o reporta `BACKEND_NO_DISPONIBLE` con diagnostico.
- Con proyectos ambiguos y sin `PRA_ACTIVE_PROJECT`, se advierte de la ambiguedad.
