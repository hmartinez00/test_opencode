# Lista de Tareas: Sistema de Testing y Calidad para PRA (002-sistema-testing-pra)

## Fase 1: Configuración Inicial del Entorno de Pruebas
- [x] T101 [P] Crear archivo de configuración `pytest.ini` en la raíz del proyecto.
- [x] T102 [P] Crear directorio `tests/` y subdirectorios (`tests/unit/`, `tests/integration/`, `tests/constitutional/`).
- [x] T103 Implementar `tests/conftest.py` con fixtures compartidas (`isolated_dir`, `sample_markdown_doc`, `sample_plan_json_str`, `sample_llm_response_s1`, `sample_invalid_llm_response_inline_css`, `run_cli`, `disable_setup_utf8`).

## Fase 2: Pruebas Unitarias (`tests/unit/`)
- [x] T104 [P] Implementar `tests/unit/test_normalize_plan.py` para verificar conversión de alias y campos del plan.
- [x] T105 [P] Implementar `tests/unit/test_validators.py` para verificar función `validate_no_inline_css()`.
- [x] T106 [P] Implementar `tests/unit/test_parsers.py` para verificar `parse_llm_response()` y extracción de 5 bloques.
- [x] T107 [P] Implementar `tests/unit/test_registries.py` para verificar `merge_registry()` y actualización sin duplicación.

## Fase 3: Pruebas de Integración CLI (`tests/integration/`)
- [x] T108 [P] Implementar `tests/integration/test_cli_init.py` para verificar comando `--init`.
- [x] T109 [P] Implementar `tests/integration/test_cli_save_plan.py` para verificar comando `--save-plan` y creación de directorios.
- [x] T110 [P] Implementar `tests/integration/test_cli_session.py` para verificar `--prompt-session` y `--process-session`.
- [x] T111 [P] Implementar `tests/integration/test_cli_zip.py` para verificar comando `--zip` y generación de `outputs.zip`.

## Fase 4: Pruebas de Reglas Constitucionales y Casos Límite (`tests/constitutional/`)
- [x] T112 [P] Implementar `tests/constitutional/test_constitution_rules.py` (rechazo CSS inline, secuencialidad, JSON malformado, respuesta sin láminas).

## Fase 5: Verificación de Cobertura y Documentación
- [x] T113 Ejecutar suite completa con `pytest --cov=pra_helper`: 30/30 aprobadas, cobertura 88% (>= 85% requerido).
- [x] T114 Crear guía rápida de testing en `specs/002-sistema-testing-pra/quickstart.md`.

## Defectos Corregidos en pra_helper.py (detectados por la suite)
- [x] D001 Regex de manifest no capturaba `data-title` (`parse_llm_response`).
- [x] D002 `cmd_process_session` no validaba secuencialidad de sesiones (Constitución IV).
- [x] D003 Registros duplicados/vacíos: `normalize_plan()` descartaba clases/comportamientos requeridos y `cmd_process_session` no deduplicaba al fusionar.
