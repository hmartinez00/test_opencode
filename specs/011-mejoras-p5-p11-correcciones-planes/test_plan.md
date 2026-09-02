# Plan de pruebas TDD: correcciones al motor PRA (iteracion 011)

**Fecha**: 2026-09-02
**Especificacion**: [spec.md](./spec.md)
**Estado**: En planificacion (pre-implementacion)

Este documento define las pruebas que deberan escribirse primero. En esta etapa no se crean archivos bajo `tests/` ni se modifica codigo de produccion.

## Convenciones

- Usar `python -m pytest`, nunca el ejecutable `pytest.exe`.
- Reutilizar `isolated_dir`, `run_cli`, `run_orchestrator`, `sample_plan_json_str` y los fixtures de `tests/conftest.py`.
- Mantener `PRA_OUTPUT_DIR` aislado por prueba.
- Usar respuestas mock deterministas.
- Cada prueba nueva debe indicar el requisito funcional y el criterio de exito que cubre.
- La primera ejecucion de cada grupo debe demostrar el estado rojo.

## Grupo A: pruebas de regex BLOQUE 6 (A1)

Archivo previsto: `tests/unit/test_bloque6_regex.py`

### A1-01. BLOQUE 6 con linea en blanco antes del fence

```python
def test_parse_llm_response_bloque6_con_linea_en_blanco():
    respuesta = (
        "otro contenido\n"
        "**BLOQUE 6 — Guion de narracion**\n"
        "\n"  # linea en blanco
        "```text\n"
        "[slide: 0] Apertura.\n"
        "[slide: 1] Primer concepto.\n"
        "```\n"
    )
    bloques = pra_helper.parse_llm_response(respuesta)
    assert "guion_narrativo" in bloques
    assert "[slide: 0]" in bloques["guion_narrativo"]
```

Cubre RF-A1-001, CSE-001.

**Rojo esperado**: la regex actual no captura el bloque con linea en blanco.

### A1-02. BLOQUE 6 sin linea en blanco (regression)

```python
def test_parse_llm_response_bloque6_sin_linea_en_blanco():
    respuesta = (
        "**BLOQUE 6 — Guion de narracion**\n"
        "```text\n"
        "[slide: 0] Apertura.\n"
        "```\n"
    )
    bloques = pra_helper.parse_llm_response(respuesta)
    assert "[slide: 0]" in bloques["guion_narrativo"]
```

Cubre RF-A1-001 (regression), CSE-001.

### A1-03. Respuesta sin BLOQUE 6

```python
def test_parse_llm_response_sin_bloque6():
    respuesta = (
        "```blade\n"
        "{{- sesion1/slide1.blade.php -}}\n"
        "```\n"
    )
    bloques = pra_helper.parse_llm_response(respuesta)
    assert bloques.get("guion_narrativo", "") == ""
```

Cubre RF-A1-003.

### A1-04. BLOQUE 6 con multiples espacios en la linea en blanco

```python
def test_parse_llm_response_bloque6_con_espacios_en_blanco():
    respuesta = (
        "**BLOQUE 6 — Guion**\n"
        "   \t\n"  # linea con espacios/tabs
        "```text\n"
        "[slide: 0] Texto.\n"
        "```\n"
    )
    bloques = pra_helper.parse_llm_response(respuesta)
    assert "[slide: 0]" in bloques["guion_narrativo"]
```

Cubre RF-A1-001.

### A1-05. BLOQUE 6 con fence sin etiqueta (sin `text`)

```python
def test_parse_llm_response_bloque6_fence_sin_etiqueta():
    respuesta = (
        "**BLOQUE 6 — Guion**\n"
        "\n"
        "```\n"
        "[slide: 0] Texto.\n"
        "```\n"
    )
    bloques = pra_helper.parse_llm_response(respuesta)
    assert "[slide: 0]" in bloques["guion_narrativo"]
```

Cubre RF-A1-001.

## Grupo B: pruebas de deduplicacion de registros (A2)

Archivo previsto: `tests/integration/test_cli_save_plan_dedup.py`

### B-01. Clase CSS duplicada en 2 laminas -> 1 entrada en registry

```python
def test_save_plan_deduplica_clases_css(isolated_dir, run_cli):
    plan = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dedup",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "clases_css_requeridas": [{"nombre": "cls-duplicada", "descripcion": "primera"}]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "clases_css_requeridas": [{"nombre": "cls-duplicada", "descripcion": "segunda"}]
                }
            ]
        }]
    }
    result = run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan)])
    registry = load_json(Path(isolated_dir) / "test_dedup" / "class_registry.json")
    entradas = [c for c in registry["clases"] if c["nombre"] == "cls-duplicada"]
    assert len(entradas) == 1
```

Cubre RF-A2-001, CSE-002.

**Rojo esperado**: actualmente se crean 2 entradas.

### B-02. Comportamiento JS duplicado -> 1 entrada

```python
def test_save_plan_deduplica_comportamientos_js(isolated_dir, run_cli):
    plan = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dedup_js",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "comportamientos_js_requeridos": [{"nombre": "js-dup", "descripcion": "primera"}]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "comportamientos_js_requeridos": [{"nombre": "js-dup", "descripcion": "segunda"}]
                }
            ]
        }]
    }
    result = run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan)])
    registry = load_json(Path(isolated_dir) / "test_dedup_js" / "js_registry.json")
    entradas = [j for j in registry["comportamientos"] if j["nombre"] == "js-dup"]
    assert len(entradas) == 1
```

Cubre RF-A2-002, CSE-002.

### B-03. Orden de primera aparicion se mantiene

```python
def test_save_plan_mantiene_orden_primera_aparicion(isolated_dir, run_cli):
    # Usar el plan de B-01 y verificar que la descripcion es "primera"
    ...
    registry = load_json(...)
    entrada = [c for c in registry["clases"] if c["nombre"] == "cls-duplicada"][0]
    assert entrada["descripcion"] == "primera"
```

Cubre RF-A2-003.

## Grupo C: pruebas de auto-numerado de `orden` (A3)

Archivo previsto: `tests/unit/test_normalize_plan_orden.py`

### C-01. Plan sin `orden` -> laminas numeradas 1..N

```python
def test_normalize_plan_asigna_orden_auto():
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_orden",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": []},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": []},
                {"id_kebab_case": "c", "tipo": "contenido", "objetivo": "o3", "insumos": []}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert [l["orden"] for l in laminas] == [1, 2, 3]
```

Cubre RF-A3-001, RF-A3-002, CSE-003.

**Rojo esperado**: actualmente quedan todas en 0.

### C-02. Plan con `orden` parcial -> faltantes completan

```python
def test_normalize_plan_orden_parcial():
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_orden_parcial",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": [], "orden": 1},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": []},
                {"id_kebab_case": "c", "tipo": "contenido", "objetivo": "o3", "insumos": [], "orden": 3}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert laminas[1]["orden"] == 2  # auto-asignado
    assert laminas[0]["orden"] == 1  # conservado
    assert laminas[2]["orden"] == 3  # conservado
```

Cubre RF-A3-003.

### C-03. Plan con `orden` explicito en todas -> se respeta

```python
def test_normalize_plan_orden_explicito_se_respeta():
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_orden_ok",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": [], "orden": 5},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": [], "orden": 10}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert [l["orden"] for l in laminas] == [5, 10]
```

Cubre RF-A3-002.

### C-04. `PRA_PLAN_ESTRICTO=1` con plan sin orden -> error

```python
def test_save_plan_estricto_sin_orden_falla(monkeypatch, isolated_dir, run_cli):
    monkeypatch.setenv("PRA_PLAN_ESTRICTO", "1")
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_orden_err",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": []}
            ]
        }]
    }
    result = run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan_raw)])
    assert result.returncode == 2
```

Cubre RF-A3-005, CSE-007.

## Grupo D: pruebas de preservacion de `data_title` (A4)

Archivo previsto: `tests/unit/test_normalize_plan_data_title.py` y `tests/integration/test_cli_manifest_data_title.py`

### D-01. `normalize_plan` conserva `data_title`

```python
def test_normalize_plan_conserva_data_title():
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dt",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": [], "data_title": "Titulo Real"}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    lamina = plan["sesiones"][0]["laminas"][0]
    assert lamina.get("data_title") == "Titulo Real"
```

Cubre RF-A4-001.

**Rojo esperado**: actualmente `data_title` se descarta en `normalize_plan`.

### D-02. Sin `data_title` -> no crea campo fantasma

```python
def test_normalize_plan_sin_data_title_no_crea_campo():
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dt2",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": []}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    lamina = plan["sesiones"][0]["laminas"][0]
    assert "data_title" not in lamina
```

Cubre RF-A4-004.

### D-03. `manifest_draft` usa `data_title`

```python
def test_save_plan_manifest_draft_usa_data_title(isolated_dir, run_cli):
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dt_draft",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": [], "data_title": "Mi Titulo Real"}
            ]
        }]
    }
    run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan_raw)])
    draft = (Path(isolated_dir) / "test_dt_draft" / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert 'data-title="Mi Titulo Real"' in draft
```

Cubre RF-A4-002.

### D-04. Sin `data_title` -> fallback a `titulo_legible`

```python
def test_save_plan_manifest_draft_fallback(isolated_dir, run_cli):
    plan_raw = {
        "titulo": "Test",
        "carpeta_snake_case": "test_dt_fb",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": []}
            ]
        }]
    }
    run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan_raw)])
    draft = (Path(isolated_dir) / "test_dt_fb" / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert 'data-title="Lamina 1"' in draft
```

Cubre RF-A4-004.

### D-05. Consolidacion usa `data_title` en manifest final

```python
def test_consolidate_usa_data_title_en_manifest(isolated_dir, run_cli):
    # Preparar proyecto con data_title, procesar sesion, consolidar
    # Verificar que manifest.blade.php contiene data-title="Titulo Real"
    ...
```

Cubre RF-A4-003, CSE-004.

## Grupo E: pruebas de unificacion de prefijo (A5)

Archivo previsto: `tests/integration/test_cli_consolidate_session_prefix.py`

### E-01. Consolidar crea `session{N}/` en lote final

```python
def test_consolidate_crea_session_dir(isolated_dir, run_cli):
    # Preparar proyecto minimo, consolidar
    project_dir = Path(isolated_dir) / "test_prefix"
    assert (project_dir / "session1").is_dir()
```

Cubre RF-A5-001, CSE-005.

**Nota**: Esta prueba puede ya pasar si la consolidacion actual funciona. El objetivo es registrarla como regresion.

### E-02. Manifest usa `session{N}.*`

```python
def test_manifest_usa_prefijo_session(isolated_dir, run_cli):
    # Preparar proyecto, consolidar
    manifest = (project_dir / "manifest.blade.php").read_text(encoding="utf-8")
    assert 'view="session1.' in manifest
    assert 'view="sesion1.' not in manifest
```

Cubre RF-A5-001, CSE-005.

### E-03. `limpiar` elimina `sesion*/` y preserva `session*/`

```python
def test_limpiar_elimina_sesion_preserva_session(isolated_dir, run_cli):
    # Preparar proyecto, consolidar, limpiar
    project_dir = Path(isolated_dir) / "test_prefix_clean"
    assert (project_dir / "session1").is_dir()
    assert not any(d.name.startswith("sesion") for d in project_dir.iterdir() if d.is_dir())
```

Cubre RF-A5-004.

### E-04. `backup/fuente/` conserva `sesion*/`

```python
def test_backup_conserva_sesion_interna(isolated_dir, run_cli):
    # Preparar proyecto, consolidar, limpiar
    backup_dir = project_dir / "backup" / "fuente"
    assert any(d.name.startswith("sesion") for d in backup_dir.iterdir() if d.is_dir())
```

Cubre RF-A5-002.

## Grupo F: pruebas de `save-plan --plan-file` (A6)

Archivo previsto: `tests/integration/test_cli_save_plan_file.py`

### F-01. `--plan-file` con JSON valido -> plan guardado

```python
def test_save_plan_file_json_valido(isolated_dir, run_cli, tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps({
        "titulo": "Test File",
        "carpeta_snake_case": "test_file_plan",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": []}
            ]
        }]
    }), encoding="utf-8")
    result = run_cli(["python", "pra_helper.py", "save-plan", "--plan-file", str(plan_file)])
    assert result.returncode == 0
    project_dir = Path(isolated_dir) / "test_file_plan"
    assert (project_dir / "presentation_plan.json").exists()
```

Cubre RF-A6-001, RF-A6-002, CSE-006.

**Rojo esperado**: el flag `--plan-file` aun no existe.

### F-02. `--plan-file` con archivo inexistente -> error

```python
def test_save_plan_file_inexistente(isolated_dir, run_cli):
    result = run_cli(["python", "pra_helper.py", "save-plan", "--plan-file", "/no/existe.json"])
    assert result.returncode == 1
    assert "PLAN_FILE_NOT_FOUND" in result.stdout
```

Cubre RF-A6-003.

### F-03. Resultado identico entre `--plan-file` y argv

```python
def test_save_plan_file_vs_argv_identico(isolated_dir, run_cli, tmp_path):
    plan_dict = {
        "titulo": "Test",
        "carpeta_snake_case": "test_equiv",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": []}
            ]
        }]
    }
    # Via argv
    run_cli(["python", "pra_helper.py", "save-plan", json.dumps(plan_dict)])
    plan_argv = load_json(Path(isolated_dir) / "test_equiv" / "presentation_plan.json")

    # Limpiar y via archivo
    shutil.rmtree(Path(isolated_dir) / "test_equiv")
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan_dict), encoding="utf-8")
    run_cli(["python", "pra_helper.py", "save-plan", "--plan-file", str(plan_file)])
    plan_file_result = load_json(Path(isolated_dir) / "test_equiv" / "presentation_plan.json")

    assert plan_argv == plan_file_result
```

Cubre RF-A6-005, CSE-006.

### F-04. JSON con acentos via `--plan-file`

```python
def test_save_plan_file_con_acentos(isolated_dir, run_cli, tmp_path):
    plan_file = tmp_path / "plan_acentos.json"
    plan_file.write_text(json.dumps({
        "titulo": "Presentacion con acentos: informacion y comunicacion",
        "carpeta_snake_case": "test_acentos",
        "idioma": "es",
        "resumen_general": "Contenido con acentos: aeiou",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion de introduccion",
            "objetivo_pedagogico": "Comprender la importancia de la informacion",
            "laminas": [
                {"orden": 1, "id_kebab_case": "intro", "tipo": "portada", "objetivo": "Presentar", "insumos": []}
            ]
        }]
    }, ensure_ascii=False), encoding="utf-8")
    result = run_cli(["python", "pra_helper.py", "save-plan", "--plan-file", str(plan_file)])
    assert result.returncode == 0
    plan = load_json(Path(isolated_dir) / "test_acentos" / "presentation_plan.json")
    assert "acentos" in plan["titulo"]
```

Cubre RF-A6-001.

### F-05. Sin argumentos -> error de uso

```python
def test_save_plan_sin_argumentos_falla(run_cli):
    result = run_cli(["python", "pra_helper.py", "save-plan"])
    assert result.returncode != 0
```

Cubre RF-A6-004 (retrocompatibilidad: sin argumentos no funciona).

## Grupo G: pruebas de integracion end-to-end

Archivo previsto: `tests/integration/test_iteracion011_e2e.py`

### G-01. Flujo completo con todas las correcciones

```python
def test_flujo_completo_correcciones(isolated_dir, run_cli, tmp_path):
    """Flujo: save-plan (con --plan-file, sin orden, con data_title, con duplicados)
    -> prompt-session -> process-session -> consolidate -> verificar"""
    # 1. Crear plan con todas las condiciones:
    #    - Sin campo orden (auto-numerado)
    #    - Con data_title en algumas laminas
    #    - Con clase CSS duplicada
    # 2. save-plan --plan-file
    # 3. Verificar: class_registry sin duplicados, plan con orden auto-asignado,
    #    manifest_draft con data_title
    # 4. Procesar sesion con respuesta que tenga BLOQUE 6 con linea en blanco
    # 5. Verificar: guion creado en assets/audio/
    # 6. Consolidar
    # 7. Verificar: manifest usa data_title, session1/ existe, vistas session1.*
    ...
```

Cubre CSE-001 a CSE-008.

## Matriz de trazabilidad

| Requisito | Pruebas |
|---|---|
| RF-A1-001 | A1-01, A1-02, A1-04, A1-05 |
| RF-A1-002 | A1-01, A1-02 |
| RF-A1-003 | A1-03 |
| RF-A1-004 | A1-01 a A1-05 (regression) |
| RF-A2-001 | B-01 |
| RF-A2-002 | B-02 |
| RF-A2-003 | B-03 |
| RF-A3-001 | C-01 |
| RF-A3-002 | C-03 |
| RF-A3-003 | C-02 |
| RF-A3-004 | C-01 (advertencia implícita) |
| RF-A3-005 | C-04 |
| RF-A4-001 | D-01 |
| RF-A4-002 | D-03 |
| RF-A4-003 | D-05 |
| RF-A4-004 | D-02, D-04 |
| RF-A5-001 | E-01, E-02 |
| RF-A5-002 | E-04 |
| RF-A5-004 | E-03 |
| RF-A6-001 | F-01, F-04 |
| RF-A6-002 | F-01 |
| RF-A6-003 | F-02 |
| RF-A6-004 | F-05 |
| RF-A6-005 | F-03 |
| CSE-001 | A1-01, A1-02 |
| CSE-002 | B-01, B-02 |
| CSE-003 | C-01, C-02 |
| CSE-004 | D-05 |
| CSE-005 | E-01, E-02 |
| CSE-006 | F-01, F-03 |
| CSE-007 | C-04, suite completa |
| CSE-008 | F-03, F-05 |

## Secuencia de ejecucion TDD

1. Escribir Grupo A y confirmar fallo (regex actual no tolera linea en blanco).
2. Escribir Grupo B y confirmar fallo (duplicados en registry).
3. Escribir Grupo C y confirmar fallo (orden queda en 0).
4. Escribir Grupo D y confirmar fallo (data_title descartado).
5. Escribir Grupo E y confirmar que pasan (regression, ya implementado).
6. Escribir Grupo F y confirmar fallo (--plan-file no existe).
7. Escribir Grupo G como prueba de integracion completa.
8. Implementar A1, ejecutar Grupo A.
9. Implementar A2, ejecutar Grupo B.
10. Implementar A3, ejecutar Grupo C.
11. Implementar A4, ejecutar Grupo D.
12. Verificar Grupo E sigue pasando.
13. Implementar A6, ejecutar Grupo F.
14. Ejecutar Grupo G y suite completa.
15. Confirmar cobertura >= 85%.

## Criterio de aceptacion del plan de pruebas

El plan queda listo para implementacion cuando:
- Cada requisito funcional tiene al menos una prueba prevista.
- Los casos rojos estan definidos y documentados.
- Los fixtures necesarios estan identificados.
- Ninguna prueba requiere servicios externos o audio binario.
- La matriz de trazabilidad cubre el 100% de los requisitos.
