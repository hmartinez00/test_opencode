# Plan de Pruebas TDD: Calidad de Salida de Presentaciones PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md)

Este documento detalla las pruebas que se escribiran primero (rojo) y serviran para evaluar los resultados de la implementacion. Cada prueba se mapea a sus problemas (P1-P6), requisitos funcionales (FR) y criterios de exito (SC) de la especificacion.

## Convenciones y fixtures

- Use `conftest.py` existente: `run_cli`, `initialized_project`, `sample_llm_response_s1`, `sample_plan_json_str`, `sample_markdown_doc`, `isolated_dir`, `salida_maestra_por_defecto`.
- Todas las pruebas de CLI se invocan via `python -m pytest` (nunca el ejecutable `pytest.exe`).
- Cada prueba aísla `PRA_OUTPUT_DIR` a un directorio temporal (defecto de `conftest.py`).

---

## Grupo A: Pruebas unitarias

### A1. `titulo_legible` (P6, FR-710, SC-706)

Archivo: `tests/unit/test_calidad_salida.py`

```python
def test_titulo_legible_convierte_guiones_en_espacios():
    assert pra_helper.titulo_legible("s1-listas-teoria") == "S1 Listas Teoria"

def test_titulo_legible_plural_y_numeros():
    assert pra_helper.titulo_legible("s1-retofinal-contactos") == "S1 Retofinal Contactos"
```

**Rojo esperado**: `AttributeError: module 'pra_helper' has no attribute 'titulo_legible'`.

### A2. Envoltura de fragmentos (P2, P3, FR-702/703/704, SC-703)

Archivo: `tests/unit/test_calidad_salida.py`

```python
def test_envolver_css_con_style():
    css = ".docker-blue { color: red; }"
    envuelto = pra_helper._envolver_fragmento("css", css)
    assert envuelto.startswith("<style>")
    assert envuelto.endswith("</style>")
    assert ".docker-blue" in envuelto

def test_envolver_js_con_script():
    js = "console.log('hola');"
    envuelto = pra_helper._envolver_fragmento("js", js)
    assert envuelto.startswith("<script>")
    assert envuelto.endswith("</script>")
    assert "console.log" in envuelto

def test_no_duplica_envoltura_css():
    css = "<style>\n.x { }\n</style>"
    envuelto = pra_helper._envolver_fragmento("css", css)  # ya viene envuelto (defensivo)
    assert envuelto.count("<style>") == 1

def test_no_duplica_envoltura_js():
    js = "<script>\nfoo()\n</script>"
    envuelto = pra_helper._envolver_fragmento("js", js)
    assert envuelto.count("<script>") == 1
```

**Rojo esperado**: `AttributeError` (funcion no existe).

### A3. Interpolacion de ruta (P1, FR-701, SC-702)

Archivo: `tests/unit/test_calidad_salida.py`

```python
def test_constante_entrypoint_usa_llave_unica():
    # Verifica la cadena literal que se usara en los entry points
    esperado = 'presentation.slides.{$presentation->folder_name}.assets'
    assert pra_helper.ENTRYPOINT_PREFIX == esperado
    assert "{{$presentation->folder_name}}" not in pra_helper.ENTRYPOINT_PREFIX
```

**Rojo esperado**: `AttributeError` (constante no definida aun).

---

## Grupo B: Pruebas de integracion

### B1. `consolidate` genera interpolacion valida (P1, FR-701, SC-702)

Archivo: `tests/integration/test_cli_session.py` (ampliar)

```python
def test_cli_consolidate_interpolacion_valida(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    for rel in ["manifest.blade.php", "assets/styles.blade.php", "assets/scripts.blade.php"]:
        content = (project_dir / rel).read_text(encoding="utf-8")
        assert "{$presentation->folder_name}" in content
        assert "{{$presentation->folder_name}}" not in content
        assert "{{{$presentation->folder_name}}}" not in content
```

**Rojo esperado**: la asercion de `{$presentation->folder_name}` falla con el codigo actual (`{{$presentation->folder_name}}` esta presente).

### B2. `consolidate` envuelve fragmentos e idempotencia (P2, P3, FR-702/703/704, SC-703)

Archivo: `tests/integration/test_cli_session.py` (ampliar)

```python
def test_cli_consolidate_envuelve_assets_y_es_idempotente(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    css_file = project_dir / "assets/styles_blade/css/sesion1_styles.blade.php"
    js_file = project_dir / "assets/styles_blade/js/sesion1_scripts.blade.php"
    assert css_file.exists() and js_file.exists()

    css = css_file.read_text(encoding="utf-8")
    js = js_file.read_text(encoding="utf-8")
    assert css.startswith("<style>") and css.endswith("</style>")
    assert js.startswith("<script>") and js.endswith("</script>")

    # idempotencia
    assert run_cli("consolidate")[0] == 0
    css2 = css_file.read_text(encoding="utf-8")
    js2 = js_file.read_text(encoding="utf-8")
    assert css2.count("<style>") == 1 and css2.count("</style>") == 1
    assert js2.count("<script>") == 1 and js2.count("</script>") == 1
```

**Rojo esperado**: los asserts `startswith("<style>")`/`startswith("<script>")` fallan (contenido crudo sin envoltura).

### B3. `process-session --respuesta-file` (P4, FR-705/706, SC-704)

Corto:

Archivo: `tests/integration/test_cli_session.py` (nuevo)

```python
def test_cli_process_session_respuesta_file(run_cli, initialized_project, sample_llm_response_s1, isolated_dir):
    resp_file = isolated_dir / "respuesta.txt"
    resp_file.write_text(sample_llm_response_s1, encoding="utf-8")
    code, out = run_cli("process-session", "1", "--respuesta-file", str(resp_file))
    assert code == 0
    assert json.loads(out)["laminas_escritas"] == 2

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    assert (project_dir / "sesion1/que-es-docker.blade.php").exists()
```

Largo (reproduce el caso `WinError 206`):

Archivo: `tests/integration/test_cli_session.py` (nuevo)

```python
def test_cli_process_session_respuesta_larga_por_archivo(run_cli, initialized_project, sample_llm_response_s1, isolated_dir):
    # Construye una respuesta > 33000 chars reutilizando las laminas muestrales
    base = sample_llm_response_s1
    lamina = "{{- sesion1/que-es-docker.blade.php -}}\n<div class='x'>todos</div>\n"
    grande = "**BLOQUE 1**\n" + (lamina * 400)  # > 33000 chars (~800 divisores)
    grande += "\n**BLOQUE 5**\n```json\n{\"nuevas_clases\": [], \"clases_materializadas\": [], \"nuevos_comportamientos\": [], \"comportamientos_materializados\": []}\n```\n"

    resp_file = isolated_dir / "respuesta_larga.txt"
    resp_file.write_text(grande, encoding="utf-8")

    code, out = run_cli("process-session", "1", "--respuesta-file", str(resp_file))
    assert code == 0
    assert json.loads(out)["laminas_escritas"] >= 1
```

**Rojo esperado**: con el codigo actual no existe `--respuesta-file`; el parser de argparse lo rechaza. Además, la variante posicional con 33k chars seria imposible en Windows (documentado como razon del fix).

### B4. `PRA_ACTIVE_PROJECT` (P5, FR-708/709, SC-705)

Archivo: `tests/integration/test_cli_output_dir_override.py` (nuevo o ampliado)

```python
def test_cli_activo_por_pra_active_project(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir, monkeypatch):
    base = isolated_dir / pra_helper.OUTPUT_BASE_DIR
    (base / "proyecto_a").mkdir(parents=True)
    (base / "proyecto_b").mkdir(parents=True)

    # crea proyecto a
    plan_a = json.loads(sample_plan_json_str)
    plan_a["carpeta_snake_case"] = "proyecto_a"
    # ... guardar plan en proyecto_a (via import directo o save-plan con entorno)
    plan_b = json.loads(sample_plan_json_str)
    plan_b["carpeta_snake_case"] = "proyecto_b"

    import json as _json
    # Guardar ambos planes directamente (solo para configurar el fixture)
    for proy, plan in [("proyecto_a", plan_a), ("proyecto_b", plan_b)]:
        pdir = base / proy
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "presentation_plan.json").write_text(_json.dumps(plan, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setenv("PRA_ACTIVE_PROJECT", "proyecto_b")
    code, out = run_cli("prompt-session", "1")
    # Debe operar sobre proyecto_b (titulo en prompt coincide con proyecto_b), no proyecto_a
    assert code == 0
    assert "proyecto_b" in out or "Uso Práctico" in out  # titulo de la sesion 2 es diferente
```

**Rojo esperado**: sin `PRA_ACTIVE_PROJECT`, `find_project_dir` devuelve `proyecto_a` (primer alfabetico), por lo que el prompt no corresponde a `proyecto_b`.

---

## Grupo C: Pruebas constitucionales

### C1. Escritura exclusiva via `pra_helper.py` y salida final (FR-701/702/703, Principio III)

Archivo: `tests/constitutional/test_constitution_rules.py` (ampliar)

```python
def test_consolidate_entrypoints_usan_interpolacion_valida(run_cli, ...):
    # Ejecuta save-plan + process-session + consolidate y verifica nodes:
    # - manifest/assets usan {$presentation->folder_name}
    # - no quedan referencias `sesionN.` en el manifest
    # - envolturas presentes
    ...
```

### C2. ZIP autocontenido con producto corregido (SC-701)

Archivo: `tests/integration/test_cli_zip.py` (ampliar)

```python
def test_zip_contiene_fragmentos_envueltos(...):
    # tras consolidate + zip, abrir outputs.zip y verificar que
    # assets/styles_blade/css/*.blade.php esta envuelto y el manifest usa llave unica
    ...
```

---

## Matriz de trazabilidad

| Prueba | Problema | FR | SC | Archivo destino |
|---|---|---|---|---|
| A1 `titulo_legible` | P6 | FR-710 | SC-706 | `tests/unit/test_calidad_salida.py` |
| A2 envoltura css/js | P2, P3 | FR-702/703/704 | SC-703 | `tests/unit/test_calidad_salida.py` |
| A3 interpolacion constante | P1 | FR-701 | SC-702 | `tests/unit/test_calidad_salida.py` |
| B1 consolidate interpolacion | P1 | FR-701 | SC-702 | `tests/integration/test_cli_session.py` |
| B2 consolidate envoltura+idemp | P2, P3 | FR-702/703/704 | SC-703 | `tests/integration/test_cli_session.py` |
| B3 respuesta-file corto/largo | P4 | FR-705/706 | SC-704 | `tests/integration/test_cli_session.py` |
| B4 PRA_ACTIVE_PROJECT | P5 | FR-708/709 | SC-705 | `tests/integration/test_cli_output_dir_override.py` |
| C1 salida final constitucional | P1-P3 | FR-701/702/703 | SC-701/702 | `tests/constitutional/test_constitution_rules.py` |
| C2 ZIP autocontenido | P1-P3 | FR-702/703 | SC-701 | `tests/integration/test_cli_zip.py` |

## Verificacion final

Despues del "verde", ejecutar:

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

Requisitos:
- La suite completa en verde (104 pruebas actuales + nuevas).
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.

**Nota**: las pruebas del Grupo A requieren helpers/constantes que hoy no existen en `pra_helper.py`; su "rojo" esperado es `AttributeError`/`ImportError`. Las de los Grupos B y C reproducen fallos reales de salida con el codigo actual.
