# Plan de Pruebas TDD: Robustez y Coherencia del Flujo PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md)

Este documento detalla las pruebas que se escribiran primero (rojo) y serviran para evaluar los resultados de la implementacion. Cada prueba se mapea a sus requisitos funcionales (FR) y criterios de exito (SC).

## Convenciones y fixtures

- Use `conftest.py` existente: `run_cli`, `run_orchestrator`, `isolated_dir`, `salida_maestra_por_defecto`, `sample_plan_json_str`, `sample_llm_response_s1`, `sample_markdown_doc`, `entorno_e2e`.
- Todas las pruebas CLI se invocan via `python -m pytest` (nunca el ejecutable `pytest.exe`).
- Cada prueba aisla `PRA_OUTPUT_DIR` a un directorio temporal (fixtures autouse).
- Para construir un proyecto coherente de prueba se usara el flujo `save-plan` + `process-session` + `consolidate` con los fixtures de muestra, y luego se introduciran incoherencias a proposito.

---

## Grupo A: Pruebas unitarias del oracle de coherencia (pra_helper)

Archivo: `tests/unit/test_coherencia.py` (nuevo)

Helper de construccion: crea un proyecto con plan y laminas coherentes, y permite inyectar incoherencias.

```python
def construir_proyecto_coherente(isolated_dir):
    """save-plan + process-session + consolidate sobre intro_docker (coherente)."""
    code, _ = run_cli("save-plan", sample_plan_json_str())
    assert code == 0
    code, _ = run_cli("process-session", "1", sample_llm_response_s1())
    assert code == 0
    # sesion2 no procesada; para pruebas solo importa sesion1
    proyecto = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    return proyecto
```

### A1. Detecta laminas huerfanas (FR-902)

```python
def test_analizar_coherencia_detecta_huerfanas(isolated_dir):
    proyecto = construir_proyecto_coherente(isolated_dir)
    # escribir una lamina NO declarada en el plan
    (proyecto / "sesion1" / "extra-lo-que-sea.blade.php").write_text(
        "<div class='x'>ok</div>", encoding="utf-8")
    plan = load_json(proyecto / "presentation_plan.json")
    coh = pra_helper._analizar_coherencia(plan, proyecto)
    assert any("extra-lo-que-sea" == e["id"] for e in coh["huerfanas"])
    assert coh["faltantes"] == []
```

**Rojo esperado**: `AttributeError: module 'pra_helper' has no attribute '_analizar_coherencia'`.

### A2. Detecta laminas faltantes (FR-903)

```python
def test_analizar_coherencia_detecta_faltantes(isolated_dir):
    proyecto = construir_proyecto_coherente(isolated_dir)
    # borrar una lamina declarada en el plan
    (proyecto / "sesion1" / "arquitectura.blade.php").unlink()
    plan = load_json(proyecto / "presentation_plan.json")
    coh = pra_helper._analizar_coherencia(plan, proyecto)
    assert any("arquitectura" == e["id"] for e in coh["faltantes"])
```

### A3. Detecta laminas duplicadas (FR-904)

```python
def test_analizar_coherencia_detecta_duplicadas(isolated_dir):
    proyecto = construir_proyecto_coherente(isolated_dir)
    plan = load_json(proyecto / "presentation_plan.json")
    # duplicar un id dentro de la misma sesion
    plan["sesiones"][0]["laminas"].append(
        {"orden": 9, "id_kebab_case": "que-es-docker", "tipo": "contenido", "objetivo": "dup"})
    coh = pra_helper._analizar_coherencia(plan, proyecto)
    assert any("que-es-docker" == e["id"] for e in coh["duplicadas"])
```

### A4. Consolidate aborta ante incoherencia sin manifest incompleto (FR-906/907)

```python
def test_consolidate_ok_false_con_huerfana(isolated_dir):
    proyecto = construir_proyecto_coherente(isolated_dir)
    (proyecto / "sesion1" / "extra.blade.php").write_text("<div>x</div>", encoding="utf-8")
    code, out = run_cli("consolidate")
    assert code != 0                      # o check del JSON
    payload = json.loads(out)
    assert payload["ok"] is False
    assert "coherencia" in payload
    # el manifest NO queda incompleto con vista extra
    assert any(e["id"] == "extra" for e in payload["coherencia"]["huerfanas"])
```

### A5. Consolidate exitoso sin incoherencias (FR-907)

```python
def test_consolidate_ok_true_sin_incoherencias(isolated_dir):
    proyecto = construir_proyecto_coherente(isolated_dir)
    code, out = run_cli("consolidate")
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["coherencia"] == {"huerfanas": [], "faltantes": [], "duplicadas": []}
```

---

## Grupo B: Pruebas unitarias de validacion de calidad del plan

Archivo: `tests/unit/test_plan_validacion.py` (nuevo)

### B1. Advertencia por registros vacios (FR-909)

```python
def test_validar_calidad_advierte_registros_vacios():
    plan = {"sesiones": [{"numero": 1, "laminas": [
        {"id_kebab_case": "a", "insumos": [{"texto": "x"}]}]}],
        "class_registry": {"clases": []}, "js_registry": {"comportamientos": []}}
    warnings = pra_helper._validar_calidad_plan(plan)
    assert any("registro" in w.lower() for w in warnings)
```

**Rojo esperado**: `AttributeError: module 'pra_helper' has no attribute '_validar_calidad_plan'`.

### B2. Advertencia por lamina sin insumos (FR-910)

```python
def test_validar_calidad_advierte_lamina_sin_insumos():
    plan = {"sesiones": [{"numero": 1, "laminas": [
        {"id_kebab_case": "a", "insumos": []}]}],
        "class_registry": {"clases": [{"nombre": "x"}]}, "js_registry": {"comportamientos": [{"nombre": "y"}]}}
    warnings = pra_helper._validar_calidad_plan(plan)
    assert any("a" in w and "insumos" in w.lower() for w in warnings)
```

### B3. Umbral `PRA_PLAN_ESTRICTO` eleva advertencia a error (FR-911)

```python
def test_save_plan_estricto_aborta(monkeypatch, isolated_dir):
    monkeypatch.setenv("PRA_PLAN_ESTRICTO", "1")
    plan = {"titulo": "X", "carpeta_snake_case": "x", "sesiones": [
        {"numero": 1, "laminas": [{"id_kebab_case": "a", "insumos": []}]}]}
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code != 0
    payload = json.loads(out)
    assert payload["ok"] is False or "error" in payload
```

**Rojo esperado**: hoy `save-plan` no valida ni aborta -> code 0.

---

## Grupo C: Pruebas unitarias del backend `opencode` robusto

Archivo: `tests/unit/test_orchestrator_backends.py` (aumentar)

### C1. `_resolver_binario_opencode` resuelve via rutas conocidas (FR-912)

```python
def test_resolver_binario_opencode_ruta_conocida(monkeypatch, tmp_path):
    # crear un falso binario en ~/.opencode/bin
    bin_dir = tmp_path / ".opencode" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / ("opencode.exe" if os.name == "nt" else "opencode")).write_bytes(b"")
    monkeypatch.setenv("PRA_OUTPUT_DIR", str(tmp_path / "out"))
    # forzar home a tmp_path y PATH vacio
    r = pra_orchestrator._resolver_binario_opencode()
    assert r and ("opencode" in r)
```

**Rojo esperado**: `AttributeError: module 'pra_orchestrator' has no attribute '_resolver_binario_opencode'`.

### C2. Diagnostico `BACKEND_NO_DISPONIBLE` (FR-913)

```python
def test_backend_opencode_no_disponible_diagnostico(monkeypatch, run_orchestrator, ...):
    monkeypatch.setattr(po, "_resolver_binario_opencode", lambda: None)
    codigo, out = run_orchestrator("run", "doc.md", "--backend", "opencode")
    assert codigo == po.EXIT_INTERNO      # o el que corresponda
    assert "BACKEND_NO_DISPONIBLE" in out
    assert "opencode" in out
```

**Rojo esperado**: hoy el backend no resuelve y no hay diagnostico estructurado -> codigo/excepción distinto.

---

## Grupo D: Pruebas unitarias de ambiguedad del proyecto activo

Archivo: `tests/unit/test_output_base_dir.py` o `tests/unit/test_orchestrator_state.py` (aumentar)

### D1. Ambiguedad detectada y advertida con varios proyectos (FR-914/915)

```python
def test_ambiguedad_proyecto_advierte(monkeypatch, capsys, tmp_path):
    base = tmp_path / "slides"
    (base / "proy_a" / "presentation_plan.json").parent.mkdir(parents=True)
    (base / "proy_a" / "presentation_plan.json").write_text("{}")
    (base / "proy_b" / "presentation_plan.json").parent.mkdir(parents=True)
    (base / "proy_b" / "presentation_plan.json").write_text("{}")
    monkeypatch.setenv("PRA_OUTPUT_DIR", str(base))
    monkeypatch.delenv("PRA_ACTIVE_PROJECT", raising=False)
    # invocar la funcion de seleccion
    ...
    assert "proy_a" in capsys.readouterr().err or "ambig" in out
```

**Rojo esperado**: hoy no hay advertencia -> stderr vacio (assert falla).

### D2. `PRA_ACTIVE_PROJECT` desambigua deterministamente (FR-914)

```python
def test_active_project_desambigua(monkeypatch, tmp_path):
    # fixture con proy_a y proy_b
    monkeypatch.setenv("PRA_ACTIVE_PROJECT", "proy_b")
    # find_project_dir debe resolver proy_b
    assert (proyecto_resuelto.name == "proy_b")
```

---

## Grupo E: Pruebas de integracion CLI

Archivos: `tests/integration/test_cli_session.py` (aumentar), `tests/integration/test_cli_save_plan.py` (aumentar)

### E1. `consolidate` con lamina huerfana devuelve reporte `coherencia` (FR-902/906)

```python
def test_cli_consolidate_reporta_coherencia(run_cli, isolated_dir, sample_plan_json_str,
                                            sample_llm_response_s1):
    run_cli("save-plan", sample_plan_json_str())
    run_cli("process-session", "1", sample_llm_response_s1())
    (isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker" / "sesion1"
     / "huerfana.blade.php").write_text("<div>x</div>")
    code, out = run_cli("consolidate")
    payload = json.loads(out)
    assert payload["ok"] is False
    assert any(e["id"] == "huerfana" for e in payload["coherencia"]["huerfanas"])
```

### E2. `save-plan` emite advertencias sin bloquear (FR-909/910/911)

```python
def test_cli_save_plan_advierte_y_guarda(run_cli, isolated_dir):
    plan = {"titulo": "X", "carpeta_snake_case": "x", "sesiones": [
        {"numero": 1, "laminas": [{"id_kebab_case": "a", "insumos": []}]}]}
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code == 0
    payload = json.loads(out)
    assert payload.get("advertencias")  # existe campo
    # aun asi se guardo
    assert (isolated_dir / pra_helper.OUTPUT_BASE_DIR / "x" / "presentation_plan.json").exists()
```

**Rojo esperado**: hoy el JSON de salida no tiene campo `advertencias` -> assert falla.

---

## Grupo F: Pruebas constitucionales

Archivo: `tests/constitutional/test_coherencia_rules.py` (nuevo)

### F1. La consolidacion nunca entrega un manifest incompleto ante incoherencia (SC-901/902)

```python
def test_nunca_manifest_incompleto_ante_incoherencia(run_cli, ...):
    # construir, inyectar huerfana, consolidate -> ok:false
    # el manifest previo (si existe) no debe contener la lamina huerfana como si fuera valida
    ...
```

### F2. Toda mutacion de coherencia ocurre via el motor

```python
def test_coherencia_la_detecta_el_motor_no_el_orquestador(...):
    # la logica de deteccion vive en pra_helper (no en pra_orchestrator)
    # se verificara que _analizar_coherencia existe en pra_helper
    assert hasattr(pra_helper, "_analizar_coherencia")
```

---

## Grupo G: No-regresion del flujo desatendido

Archivo: `tests/integration/test_cli_orchestrator_run_mock.py` (verificar)

### G1. La corrida mock sigue consolidando sin incoherencias (SC-906/D7)

```python
def test_run_mock_flujo_completo_sin_incoherencias(run_orchestrator, entorno_e2e, isolated_dir):
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")
    assert codigo == 0
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    # el manifest final referencia las laminas de session1 que SÍ existen
    ... (sin cambios si fixtures coherentes)
```

Esta prueba documenta que la introduccion del oracle NO rompe el flujo cuando plan y laminas coinciden.

---

## Matriz de trazabilidad

| Prueba | FR | SC | Archivo destino |
|---|---|---|---|
| A1 huerfanas | FR-902 | SC-901 | `tests/unit/test_coherencia.py` |
| A2 faltantes | FR-903 | SC-901 | `tests/unit/test_coherencia.py` |
| A3 duplicadas | FR-904 | SC-901 | `tests/unit/test_coherencia.py` |
| A4 consolidate aborta | FR-906 | SC-902 | `tests/unit/test_coherencia.py` |
| A5 consolidate ok | FR-907 | SC-902 | `tests/unit/test_coherencia.py` |
| B1 registros vacios | FR-909 | SC-903 | `tests/unit/test_plan_validacion.py` |
| B2 lamina sin insumos | FR-910 | SC-903 | `tests/unit/test_plan_validacion.py` |
| B3 umbral estricto | FR-911 | SC-903 | `tests/unit/test_plan_validacion.py` |
| C1 resolver binario | FR-912 | SC-904 | `tests/unit/test_orchestrator_backends.py` |
| C2 diagnostico | FR-913 | SC-904 | `tests/unit/test_orchestrator_backends.py` |
| D1 ambiguedad | FR-914/915 | SC-905 | `tests/unit/test_orchestrator_state.py` |
| D2 desambiguacion | FR-914 | SC-905 | `tests/unit/test_orchestrator_state.py` |
| E1 CLI consolidate coherencia | FR-902/906 | SC-902 | `tests/integration/test_cli_session.py` |
| E2 CLI save-plan advertencias | FR-909/910/911 | SC-903 | `tests/integration/test_cli_save_plan.py` |
| F1 constitucional manifest | FR-906 | SC-902 | `tests/constitutional/test_coherencia_rules.py` |
| F2 mutacion via motor | Principio III | SC-906 | `tests/constitutional/test_coherencia_rules.py` |
| G1 no-regresion mock | FR-907/D7 | SC-906 | `tests/integration/test_cli_orchestrator_run_mock.py` |

## Verificacion final

Despues del "verde", ejecutar:

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

Requisitos:
- La suite completa en verde (133 pruebas actuales + nuevas / - ajustes de fixtures).
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.

**Nota**: las pruebas del Grupo A requieren que `_analizar_coherencia` no exista aun; su "rojo" esperado es `AttributeError`. Las del Grupo C requieren `_resolver_binario_opencode`; su rojo es `AttributeError` o la ausencia de diagnostico. Las de los Grupos B, D y E reproducen el comportamiento actual defectuoso (guardado sin aviso, ambiguedad silenciosa, manifest incompleto).
