# Guia de Validacion y Arranque Rapido: Orquestador Automatico PRA

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contrato**: [orchestrator-contract.md](./contracts/orchestrator-contract.md)

## Requisitos Previos

- Python 3.11+ en PATH.
- Suite `pytest` del repositorio operativa (30 pruebas base en verde).
- Para backend real: CLI de OpenCode disponible en modo no interactivo. (No requerido para `--backend mock`).
- Documento fuente de prueba: `ejemplos/introduccion_docker/documento_fuente.md`.

## Corrida Rapida en 3 Pasos

Desde la raiz del repositorio, ejecutar en PowerShell:

### 1. Configurar el directorio maestro

```powershell
$env:PRA_OUTPUT_DIR = 'C:\laragon\www\product_samples\slides'
```

### 2. Ejecutar el flujo completo

```powershell
python .\pra_orchestrator.py run .\ejemplos\introduccion_docker\documento_fuente.md --backend mock
```

El proceso ejecuta `init`, `save-plan`, todas las sesiones, `pytest` y `zip` de forma secuencial.

### 3. Verificar el entregable

Comprobar que existe:

```text
C:\laragon\www\product_samples\slides\intro_docker\outputs.zip
```

La corrida es correcta cuando termina con codigo de salida `0`, muestra `pytest OK` y `zip OK`, y el archivo `outputs.zip` esta dentro del directorio del proyecto.

---

## Escenario 1: Flujo Completo Desatendido con Backend Mock

```bash
python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend mock
```

**Resultado esperado**:
- Codigo de salida `0`.
- STDOUT muestra el progreso: `init OK` -> `save-plan OK` -> `sesion 1 OK (intentos=1)` -> ... -> `pytest OK (cobertura >= 85%)` -> `zip OK`.
- Existe el directorio del proyecto (`introduccion_docker/`) con:
  - `presentation_plan.json`, `class_registry.json`, `js_registry.json`
  - `sesion[N]/[slide-id].blade.php` por cada lamina del plan
  - `styles.blade.php`, `scripts.blade.php`, `manifest_draft.blade.php`
- Existe `outputs.zip` y NO incluye `orchestration_state.json` ni `orchestration_log.txt`.

---

## Escenario 2: Determinismo de la Corrida Mock

```bash
# En dos directorios temporales distintos, repetir el Escenario 1 y comparar
# el arbol del proyecto generado (el zip se excluye: guarda timestamps de empaquetado)
python - <<'PY'
import hashlib, pathlib
raiz = pathlib.Path("intro_docker")
for p in sorted(raiz.rglob("*")):
    if p.is_file():
        print(p.relative_to(raiz).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
PY
```

**Resultado esperado**: ambos arboles identicos archivo por archivo (SC-202). Las pruebas automatizadas lo verifican en `tests/integration/test_cli_orchestrator_run_mock.py::test_run_mock_determinismo_entre_corridas`.

---

## Escenario 3: Bucle de Autocorreccion (Retry Loop)

Preparar `MockBackend` con secuencia programada (primera respuesta contaminada con `style="color:red;"`, segunda valida) via pruebas automatizadas:

```bash
pytest tests/integration/test_cli_orchestrator_retry.py -v
```

**Resultado esperado**:
- La sesion afectada se completa en el intento 2.
- `orchestration_log.txt` registra intento 1 como `FALLO` con motivo "CSS inline detectado..." e intento 2 como `OK`.
- Estado final: codigo `0`.

---

## Escenario 4: Reanudacion tras Interrupcion

```bash
# 1) Correr y abortar manualmente tras completar la sesion 1 (Ctrl+C durante sesion 2)
python pra_orchestrator.py run <documento> --backend mock
# 2) Reanudar
python pra_orchestrator.py resume
```

**Resultado esperado**: `resume` continua desde la sesion 2 sin regenerar la 1; estado final codigo `0`.

Complemento de inspeccion:

```bash
python pra_orchestrator.py status
```

---

## Escenario 5: Puertas Constitucionales Post-Corrida

```bash
grep -r 'style="' introduccion_docker/sesion*/ || echo "SIN CSS INLINE"
```

**Resultado esperado**: sin coincidencias.

---

## Escenario 6: Backend Real (opcional)

```bash
python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend opencode --timeout-s 600
```

**Resultado esperado**: mismo contrato que el Escenario 1, con respuestas generadas por el LLM real; ante respuestas defectuosas se observan reintentos con reflexion de error hasta `--max-retries`.

---

## Escenario 7: Verificacion Final de Calidad

```bash
pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

**Resultado esperado**: 0 fallos; cobertura `pra_helper.py` >= 85% y `pra_orchestrator.py` >= 85%.