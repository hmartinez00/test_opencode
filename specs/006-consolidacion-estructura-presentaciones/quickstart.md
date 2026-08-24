# Quickstart: Consolidacion de Presentaciones PRA

**Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contrato**: [contracts/consolidation-contract.md](./contracts/consolidation-contract.md)

## Requisitos Previos

- Python 3.10 o superior.
- Dependencias de testing instaladas.
- Directorio `C:\laragon\www\product_samples\slides` existente, o `PRA_OUTPUT_DIR` apuntando a una ruta existente.
- Documento `ejemplos/introduccion_docker/documento_fuente.md`.

## Validacion Rapida en 3 Pasos

Desde la raiz del repositorio, ejecutar en PowerShell:

### 1. Configurar la ruta de salida

```powershell
$env:PRA_OUTPUT_DIR = 'C:\laragon\www\product_samples\slides'
```

### 2. Ejecutar la corrida consolidada

```powershell
python .\pra_orchestrator.py run .\ejemplos\introduccion_docker\documento_fuente.md --backend mock
```

El flujo debe ejecutar `init`, `save-plan`, las sesiones, `consolidate`, `pytest` y `zip`.

### 3. Verificar la estructura final

```powershell
$project = 'C:\laragon\www\product_samples\slides\intro_docker'
Test-Path "$project\manifest.blade.php"
Test-Path "$project\assets\styles.blade.php"
Test-Path "$project\assets\scripts.blade.php"
Test-Path "$project\outputs.zip"
```

Todos los resultados deben ser `True`. Tambien deben existir `session1/` y `session2/`, y no deben existir referencias `sesionN` en el manifest final.

## Validacion del ZIP

Comprobar que `outputs.zip` contiene `manifest.blade.php`, `assets/` y las vistas finales, pero no contiene otro `outputs.zip`, `orchestration_state.json` ni `orchestration_log.txt`.

## Validacion de Calidad

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

La suite debe terminar sin fallos y la cobertura de ambos modulos debe ser igual o superior a 85%.

## Escenario de Fallo Estructural

Introducir temporalmente una vista con `style="..."` o una referencia inexistente. La fase `consolidate` debe fallar, registrar el diagnostico y evitar la ejecucion de `zip`.
