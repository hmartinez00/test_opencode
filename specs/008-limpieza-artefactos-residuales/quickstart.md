# Quickstart: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

Guia rapida de validacion end-to-end de la iteracion 008 (documentacion previa a la implementacion).

## Escenario 1: Limpieza manual via CLI

```powershell
# 1) Inicializar un proyecto desde el documento fuente
python pra_helper.py init ejemplos/introduccion_docker/documento_fuente.md

# 2) (intermedio) save-plan + process-session + consolidate -> se genera la estructura con residuos

# 3) Limpiar
python pra_helper.py limpiar

# 4) Verificar: solo lote protegido + backup/fuente/
Get-ChildItem <PRA_OUTPUT_DIR>\intro_docker
#   manifest.blade.php, presentation_plan.json, class_registry.json,
#   js_registry.json, session1/, assets/, backup/fuente/
#   (sin sesion1/, manifest_draft, styles.blade.php, scripts.blade.php,
#    *_additions/, outputs.zip)
```

## Escenario 2: Corrida automatica completa (orquestador)

```powershell
# Corrida E2E: ya NO genera outputs.zip; termina con cleanup
python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend mock

# Estado final esperado: exit code 0, estado con fase 'cleanup' completada, sin 'zip'
python pra_orchestrator.py status
```

### Validacion del estado final

```python
import json, pathlib
estado = json.loads(pathlib.Path("orchestration_state.json").read_text(encoding="utf-8"))
assert "cleanup" in estado["fases"]
assert "zip" not in estado["fases"]
assert estado["fases"]["cleanup"]["estado"] == "completada"
```

### Validacion del directorio final

```python
import pathlib
proyecto = pathlib.Path("<PRA_OUTPUT_DIR>") / "intro_docker"
lote = ["manifest.blade.php", "presentation_plan.json", "class_registry.json", "js_registry.json"]
for nombre in lote:
    assert (proyecto / nombre).exists()
assert (proyecto / "session1").is_dir()
assert (proyecto / "assets").is_dir()
assert (proyecto / "backup/fuente/sesion1").is_dir()
for residuo in ["sesion1", "manifest_draft.blade.php", "outputs.zip",
                "styles.blade.php", "scripts.blade.php", "styles_additions",
                "scripts_additions", "manifest_additions"]:
    assert not (proyecto / residuo).exists(), residuo
```

## Escenario 3: Reanudacion con retrocompatibilidad

```powershell
# Simular un estado viejo con fase 'zip' y reanudar
python pra_orchestrator.py resume
# Debe completar sin re-generar outputs.zip y normalizar zip -> cleanup
```

## Suite de pruebas

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

- La suite completa debe quedar en verde.
- Cobertura de `pra_helper.py` y `pra_orchestrator.py` >= 85%.

## Referencia de la documentacion

| Documento | Proposito |
|---|---|
| [spec.md](./spec.md) | Requisitos funcionales y criterios de exito |
| [plan.md](./plan.md) | Arquitectura y secuencia de implementacion |
| [research.md](./research.md) | Decisiones tecnicas D1-D7 |
| [data-model.md](./data-model.md) | Estructura final, reporte JSON y codigos de salida |
| [test_plan.md](./test_plan.md) | Pruebas TDD (rojo-verde-refactor) |
| [tasks.md](./tasks.md) | Lista de tareas T8## por fase |
| [contracts/cli-contract.md](./contracts/cli-contract.md) | Contrato del comando `limpiar` y la fase `cleanup` |
| [checklists/requirements.md](./checklists/requirements.md) | Checklist de requerimientos |
