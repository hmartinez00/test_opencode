# Plan de Pruebas TDD: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md)

Este documento detalla las pruebas que se escribiran primero (rojo) y serviran para evaluar los resultados de la implementacion. Cada prueba se mapea a sus requisitos funcionales (FR) y criterios de exito (SC).

## Convenciones y fixtures

- Use `conftest.py` existente: `run_cli`, `run_orchestrator`, `isolated_dir`, `sample_plan_json_str`, `sample_llm_response_s1`, `salida_maestra_por_defecto`.
- Todas las pruebas CLI se invocan via `python -m pytest` (nunca el ejecutable `pytest.exe`).
- Cada prueba aísla `PRA_OUTPUT_DIR` a un directorio temporal.
- Para las pruebas del motor, se ejecutara un flujo real (`save-plan` + `process-session` + `consolidate`) y luego `limpiar`.

---

## Grupo A: Pruebas unitarias de `_limpiar_proyecto` (pra_helper)

Archivo: `tests/unit/test_limpieza.py`

Helper de construccion: crea un proyecto con lote completo mas artefactos residuales.

```python
def construir_proyecto_con_residuos(isolated_dir):
    """Crea un proyecto con lote protegido y artefactos residuales (previo a limpiar)."""
    plan = json.loads(sample_plan_json_str())
    plan["sesiones"] = plan["sesiones"][:1]
    # save-plan + process-session + consolidate generan toda la estructura
    ...
```

### A1. Preserva el lote protegido (FR-801/803)

```python
def test_limpieza_preserva_lote_protegido(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    reporte = pra_helper._limpiar_proyecto(proyecto)
    assert reporte["ok"] is True
    for protegido in ("manifest.blade.php", "presentation_plan.json",
                      "class_registry.json", "js_registry.json"):
        assert (proyecto / protegido).exists()
    assert (proyecto / "session1").is_dir()
    assert (proyecto / "assets").is_dir()
    assert (proyecto / "session1" / "que-es-docker.blade.php").exists()
```

**Rojo esperado**: `AttributeError: module 'pra_helper' has no attribute '_limpiar_proyecto'`.

### A2. Respala la fuente en `backup/fuente/` (FR-802)

```python
def test_limpieza_respalda_fuente(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    pra_helper._limpiar_proyecto(proyecto)
    assert (proyecto / "backup/fuente/sesion1/que-es-docker.blade.php").exists()
    assert (proyecto / "backup/fuente/styles_additions/sesion1_styles.css").exists()
    assert (proyecto / "backup/fuente/scripts_additions/sesion1_scripts.js").exists()
    assert (proyecto / "backup/fuente/manifest_draft.blade.php").exists()
```

### A3. Elimina artefactos residuales (FR-804)

```python
def test_limpieza_elimina_residuos(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    pra_helper._limpiar_proyecto(proyecto)
    for residuo in ("sesion1", "manifest_draft.blade.php", "manifest_additions",
                    "styles.blade.php", "scripts.blade.php", "styles_additions",
                    "scripts_additions", "outputs.zip"):
        assert not (proyecto / residuo).exists(), f"Residuo no eliminado: {residuo}"
```

### A4. Puerta protectora: aborta sin borrar si falta el lote (FR-805)

```python
def test_limpieza_aborta_sin_borrar_si_falta_lote(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    (proyecto / "manifest.blade.php").unlink()
    # guardar sumario antes
    antes = {p.name: p.exists() for p in proyecto.iterdir()}
    reporte = pra_helper._limpiar_proyecto(proyecto)
    assert reporte["ok"] is False
    for nombre, existe in antes.items():
        assert (proyecto / nombre).exists() == existe, f"Se borro algo: {nombre}"
```

### A5. Idempotencia y determinismo del respaldo (FR-810)

```python
def test_limpieza_idempotente_y_determinista(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    pra_helper._limpiar_proyecto(proyecto)
    backup_1 = {str(p.relative_to(proyecto)): p.read_bytes() for p in (proyecto/"backup").rglob("*") if p.is_file()}
    # segunda limpieza (no deberia haber residuos ya)
    pra_helper._limpiar_proyecto(proyecto)
    backup_2 = {str(p.relative_to(proyecto)): p.read_bytes() for p in (proyecto/"backup").rglob("*") if p.is_file()}
    assert backup_1 == backup_2
    assert (proyecto/"backup/fuente/sesion1/que-es-docker.blade.php").exists()
```

---

## Grupo B: Pruebas de integracion CLI del comando `limpiar`

Archivo: `tests/integration/test_cli_limpieza.py` (nuevo)

### B1. Comando `limpiar` deja el proyecto limpio (FR-801/804)

```python
def test_cli_limpiar_deja_solo_lote_y_backup(run_cli, ...):
    # save-plan + process-session + consolidate
    code, out = run_cli("save-plan", json.dumps(plan, ensure_ascii=False)); assert code == 0
    code, _ = run_cli("process-session", "1", sample_llm_response_s1); assert code == 0
    code, _ = run_cli("consolidate"); assert code == 0
    code, out = run_cli("limpiar")
    assert code == 0
    proyecto = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    # lote presente
    assert (proyecto/"manifest.blade.php").exists()
    assert (proyecto/"session1").is_dir()
    # residuos ausentes
    assert not (proyecto/"outputs.zip").exists()
    assert not (proyecto/"sesion1").exists()
    # backup presente
    assert (proyecto/"backup/fuente/sesion1").is_dir()
```

### B2. Comando `limpiar` con lote incompleto sale con codigo 2 (FR-805)

```python
def test_cli_limpiar_lote_incompleto_exit_2(run_cli, ...):
    # construir proyecto, borrar manifest, limpiar -> exit 2
    (proyecto/"manifest.blade.php").unlink()
    code, out = run_cli("limpiar")
    assert code == 2
    payload = json.loads(out)
    assert payload["ok"] is False
```

---

## Grupo C: Pruebas de integracion del orquestador (omision de zip + cleanup)

### C1. Actualizacion de `test_cli_orchestrator_run_mock.py`

Se REEMPLAZAN las aserciones del estado final para la nueva semantica:

```python
def test_run_mock_flujo_completo_exitoso(run_orchestrator, entorno_e2e, isolated_dir):
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")
    assert codigo == 0
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    # Lote protegido presente
    assert (proyecto / "presentation_plan.json").exists()
    assert (proyecto / "class_registry.json").exists()
    assert (proyecto / "js_registry.json").exists()
    assert (proyecto / "manifest.blade.php").exists()
    assert (proyecto / "session1" / "que-es-docker.blade.php").exists()
    assert (proyecto / "assets").is_dir()
    # Sin outputs.zip (fase zip omitida) ni artefactos residuales
    assert not (proyecto / "outputs.zip").exists()
    assert not (proyecto / "sesion1").exists()
    assert not (proyecto / "manifest_draft.blade.php").exists()
    # Respaldo de la fuente
    assert (proyecto / "backup/fuente/sesion1").is_dir()
    # Estado final: cleanup completada, sin zip
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert "cleanup" in estado["fases"]
    assert "zip" not in estado["fases"]
    assert estado["fases"]["cleanup"]["estado"] == "completada"
    assert all(s["estado"] == "completada" for s in estado["fases"]["sesiones"])
```

**Rojo esperado**: la corrida actual termina con `outputs.zip`, sin `cleanup`, dejando residuos -> fallan las nuevas aserciones.

### C2. Determinismo entre corridas (fr-810 / conserva `arbol_hashes`)

- Se mantiene `arbol_hashes` comparando dos corridas; el nuevo arbol incluye `backup/`, que debe ser identico entre corridas.

```python
def test_run_mock_determinismo_entre_corridas(run_orchestrator, entorno_e2e, isolated_dir):
    ...
    hashes.append(arbol_hashes(destino / po.OUTPUT_BASE_DIR / "intro_docker"))
    # ya NO se exige (destino / ... / "outputs.zip")
    assert hashes[0] == hashes[1]
```

### C3. Actualizacion de `test_cli_orchestrator_resume.py`

```python
def test_resume_continua_desde_sesion2_sin_reprocesar_la_1(run_orchestrator, entorno, isolated_dir):
    ...
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert all(f["estado"] == "completada" for f in (
        estado["fases"]["pytest"], estado["fases"]["cleanup"]))
    assert "zip" not in estado["fases"]
```

### C4. Retrocompatibilidad: `resume` con estado que contiene `zip` (FR-808)

Nueva prueba de unidad:

```python
def test_normalizar_estado_zip_a_cleanup():
    estado = po.nuevo_estado("doc.md", "mock", 3)
    # simular un estado viejo con zip
    estado["fases"].pop("cleanup")
    estado["fases"]["zip"] = {"estado": "completada", "intentos": 1, "ultimo_error": None}
    po.normalizar_fases(estado)   # funcion nueva
    assert "zip" not in estado["fases"]
    assert estado["fases"]["cleanup"]["estado"] == "completada"
```

---

## Grupo D: Pruebas constitucionales

Archivo: `tests/constitutional/test_limpieza_rules.py` (nuevo)

### D1. El lote protegido queda intacto y el respaldo conserva la fuente (SC-801/802)

```python
def test_cleanup_preserva_lote_y_fuente_por_sesion_corrida(...):
    # corrida completa E2E mock
    # verificar lote intacto + backup integro + sin residuos
    ...
```

### D2. La mutacion ocurre via el motor (escritura exclusiva via `pra_helper.py`)

```python
def test_orquestador_solo_delega_limpieza(...):
    # tras la corrida, los residuos fueron eliminados por el motor (no por el orquestador)
    # se verifica el reporte del motor en el log / ausencia de manipulacion directa
    ...
```

---

## Matriz de trazabilidad

| Prueba | FR | SC | Archivo destino |
|---|---|---|---|
| A1 preserva lote | FR-801/803 | SC-801/803 | `tests/unit/test_limpieza.py` |
| A2 respalda fuente | FR-802 | SC-802 | `tests/unit/test_limpieza.py` |
| A3 elimina residuos | FR-804 | SC-801 | `tests/unit/test_limpieza.py` |
| A4 puerta aborta | FR-805 | SC-805 | `tests/unit/test_limpieza.py` |
| A5 idempotencia/determinismo | FR-810 | SC-806 | `tests/unit/test_limpieza.py` |
| B1 CLI limpiar | FR-801/804 | SC-801 | `tests/integration/test_cli_limpieza.py` |
| B2 CLI lote incompleto exit 2 | FR-805 | SC-805 | `tests/integration/test_cli_limpieza.py` |
| C1 run_mock sin zip con cleanup | FR-806/807 | SC-804/806 | `tests/integration/test_cli_orchestrator_run_mock.py` |
| C2 determinismo | FR-810 | SC-806 | `tests/integration/test_cli_orchestrator_run_mock.py` |
| C3 resume cleanup | FR-806/807 | SC-806 | `tests/integration/test_cli_orchestrator_resume.py` |
| C4 retrocompatibilidad zip | FR-808 | SC-806 | `tests/unit/test_orchestrator_state.py` |
| D1 constitucional lote/fuente | FR-801/802 | SC-801/802 | `tests/constitutional/test_limpieza_rules.py` |
| D2 escritura via motor | Principio III | SC-806 | `tests/constitutional/test_limpieza_rules.py` |

## Verificacion final

Despues del "verde", ejecutar:

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

Requisitos:
- La suite completa en verde (121 pruebas actuales + nuevas / - ajustes de run_mock y resume).
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.

**Nota**: las pruebas del Grupo A requieren que `_limpiar_proyecto`/`limpiar` no existan aun; su "rojo" esperado es `AttributeError`/`ImportError`/exit code inesperado. Las de los Grupos B y C reproducen el comportamiento actual defectuoso (presencia de residuos y `outputs.zip`).
