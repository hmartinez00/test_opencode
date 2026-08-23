# Guia de Validacion y Arranque Rapido: Sistema de Testing PRA (002-sistema-testing-pra)

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [Plan de Implementacion](./plan.md)

## Requisitos Previos

- Python 3.11+ en PATH.
- Dependencias instaladas: `python -m pip install pytest pytest-cov`
- Ejecutar siempre desde la raiz del repositorio (`C:\laragon\www\test_opencode\`).

---

## Comandos de Ejecucion

```bash
# Suite completa (30 pruebas)
pytest

# Suite con reporte de cobertura de pra_helper.py
pytest --cov=pra_helper --cov-report=term-missing

# Solo pruebas unitarias
pytest tests/unit/

# Solo pruebas de integracion CLI
pytest tests/integration/

# Solo pruebas constitucionales
pytest tests/constitutional/
```

**Resultados esperados**: `30 passed`, cobertura de `pra_helper.py` >= 85% (linea base actual: 88%), duracion total ~27 segundos.

---

## Que Valida Cada Categoria

### Pruebas Unitarias (`tests/unit/`)
- `normalize_plan()`: conversion bidireccional entre campos de plantillas maestras (`nro`, `folder_name`, `titulo_sesion`, `objetivos`, `id`) y del data-model (`numero`, `carpeta_snake_case`, etc.).
- `validate_no_inline_css()` / `validate_kebab_id()` / `validate_folder_name()` / `validate_plan_schema()`: reglas regex y esquema del plan.
- `parse_llm_response()`: extraccion de los 5 bloques (laminas, CSS, JS, manifest, registry updates) y robustez ante bloques vacios.
- `merge_registry()` / `load_json()` / `save_json()`: fusion sin duplicados y preservacion UTF-8.

### Pruebas de Integracion CLI (`tests/integration/`)
Cada comando se invoca via `main()` con `sys.argv` simulado, dentro de un directorio temporal aislado:
- `init`: prompt compilado con documento fuente; error 1 si el documento no existe.
- `save-plan`: creacion de plan, registros iniciales (`implementada: false`), manifest borrador, carpetas por sesion y acumuladores; errores 1 (JSON malformado) y 2 (esquema invalido).
- `prompt-session`: prompt con contexto de sesion; codigo 2 si la sesion previa no esta completada; codigo 1 si la sesion no existe.
- `process-session`: escritura de laminas Blade, acumulacion de estilos/scripts, respaldos por sesion, actualizacion de registros sin duplicados, manifest de adiciones; codigo 2 por secuencialidad.
- `zip`: generacion de `outputs.zip` con toda la estructura; codigo 1 sin proyecto o sin sesiones completadas.

### Pruebas Constitucionales (`tests/constitutional/`)
Violaciones intencionales verificando aborto seguro:
- **Regla I**: respuesta LLM con `style="..."` -> exit 2, lamina NO escrita, registros intactos. Positiva: laminas del flujo normal no contienen CSS inline.
- **Regla III**: JSON malformado no deja estructura parcial ni corrupta.
- **Regla IV**: construir Sesion 2 sin Sesion 1 completada -> exit 2 (en `prompt-session` y `process-session`).

---

## Fixtures Clave (`tests/conftest.py`)

| Fixture | Descripcion |
|---------|-------------|
| `isolated_dir` | Autouse: cambia CWD a `tmp_path` por prueba (aislamiento total del workspace). |
| `disable_setup_utf8` | Autouse: neutraliza `setup_utf8()` para compatibilidad con `capsys`. |
| `run_cli` | Invoca `main()` con argv simulado y retorna `(codigo_salida, stdout)`. |
| `sample_markdown_doc` | Documento fuente de prueba. |
| `sample_plan_json_str` | Plan maestro valido con 2 sesiones, clases y comportamientos requeridos. |
| `sample_llm_response_s1` | Respuesta LLM valida con los 5 bloques para la Sesion 1. |
| `sample_invalid_llm_response_inline_css` | Respuesta LLM contaminada con CSS inline (test negativo). |

---

## Bugs Detectados y Corregidos Durante Esta Iteracion

La suite detecto 3 defectos reales en `pra_helper.py`, todos corregidos:

1. **Regex de manifest ambiguo** (`parse_llm_response`): el patron original no capturaba `data-title` al contener espacios intermedios. Se ajustó a un grupo opcional no-greedy.
2. **Secuencialidad ausente en `process-session`** (Constitucion IV): solo `prompt-session` validaba la sesion previa. Se replico la validacion en `cmd_process_session`.
3. **Duplicados en registros** (FR-004/FR-005): `normalize_plan()` descartaba `clases_css_requeridas`/`comportamientos_js_requeridos` (registros quedaban vacios) y `cmd_process_session` agregaba entradas sin deduplicar. Ahora los campos se preservan y la fusion usa `merge_registry()`.
