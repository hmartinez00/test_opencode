# Quickstart: Calidad de Salida de Presentaciones PRA

**Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contrato**: [contracts/cli-contract.md](./contracts/cli-contract.md) | **Pruebas**: [test_plan.md](./test_plan.md)

## Requisitos Previos

- Python 3.10 o superior.
- Dependencias de testing instaladas.
- Directorio base de salida existente o `PRA_OUTPUT_DIR` valido.
- Es conveniente tener 2 proyectos distintos bajo el directorio base para validar P5.

## Validacion Rapida

### 1. Interpolacion y envoltura (P1-P3, P6)

Desde la raiz del repositorio, consolidar un proyecto y verificar la salida:

```powershell
$project = 'C:\laragon\www\product_samples\slides\modulo3_estructuras_datos'
$manifest = Get-Content "$project\manifest.blade.php" -Raw
$manifest -match '{$presentation->folder_name}'            # True
$manifest -notmatch '{{$presentation->folder_name}}'       # True
$css = Get-Content "$project\assets\styles_blade\css\sesion1_styles.blade.php" -Raw
$css.StartsWith('<style>')                                 # True
$css.EndsWith('</style>')
$js = Get-Content "$project\assets\styles_blade\js\sesion1_scripts.blade.php" -Raw
$js.StartsWith('<script>')                                 # True
```

### 2. Respuesta por archivo (P4)

```powershell
python .\pra_helper.py process-session 1 --respuesta-file .\respuesta_larga.txt
```

Verificar codigo de salida `0` y que las laminas se escribieron en `sesion1/`.

### 3. Proyecto activo (P5)

Con dos proyectos `A` y `B` bajo el base:

```powershell
$env:PRA_ACTIVE_PROJECT = 'B'
python .\pra_helper.py prompt-session 1   # debe operar sobre el proyecto B
```

### 4. Suite de pruebas TDD

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

La suite debe quedar en verde con cobertura >= 85% en ambos modulos.

## Verificacion E2E

1. Ejecutar `python .\pra_orchestrator.py run <doc> --backend mock`.
2. Consolidar y descargar `outputs.zip`.
3. Integrarlo en Laravel y confirmar que renderiza sin retoques manuales.
