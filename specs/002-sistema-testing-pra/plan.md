# Plan de Implementacion: Sistema de Testing y Calidad para PRA (002-sistema-testing-pra)

**Rama**: `002-sistema-testing-pra` | **Fecha**: 2026-08-21 | **Especificacion**: [spec.md](./spec.md)

---

## Resumen

Este plan establece la arquitectura y estrategia de pruebas automatizadas para el sistema Presentation Automator (PRA). El marco de pruebas utiliza `pytest` para verificar de forma aislada y determinista tanto las funciones internas del motor `pra_helper.py` como sus comandos CLI de cara al usuario/agente, garantizando el cumplimiento continuo de las 5 reglas constitucionales del proyecto sin contaminar el entorno de producción local.

---

## Contexto Tecnico

**Lenguaje/Version**: Python 3.11+
**Framework de Testing**: `pytest`
**Complementos y Librerías**:
- `pytest-cov`: Medición de cobertura de código.
- `unittest.mock`: Mapeo y monkeypatching de rutas/entorno si es necesario.
- `tmp_path` (fixture nativa de pytest): Aislamiento absoluto de archivos en sistema de archivos temporal por cada prueba.
- `capsys` (fixture nativa de pytest): Captura de salidas STDOUT y STDERR en pruebas de comandos CLI.
- `sys.argv` / `argparse`: Invocación directa del punto de entrada `main()` de `pra_helper.py`.

**Estructura de Archivos**:
```text
C:\laragon\www\test\test\test_opencode\
├── pytest.ini
├── pra_helper.py
├── tests/
│   ├── conftest.py                   # Fixtures compartidas (proyectos tmp, JSONs, mock LLM)
│   ├── unit/
│   │   ├── test_normalize_plan.py    # Pruebas de alias y normalización de esquemas JSON
│   │   ├── test_validators.py        # Pruebas de regla Cero CSS inline y validadores
│   │   ├── test_parsers.py           # Pruebas de extracción de bloques de respuesta LLM
│   │   └── test_registries.py        # Pruebas de fusión y actualización de registries
│   ├── integration/
│   │   ├── test_cli_init.py          # Pruebas del comando --init
│   │   ├── test_cli_save_plan.py     # Pruebas de --save-plan
│   │   ├── test_cli_session.py       # Pruebas de --prompt-session y --process-session
│   │   └── test_cli_zip.py           # Pruebas de --zip
│   └── constitutional/
│       └── test_constitution_rules.py # Pruebas de reglas de negocio y fallos intencionales
```

---

## Verificacion Constitucional

| Principio | Estado | Mecanismo de Cumplimiento en el Sistema de Testing |
|-----------|--------|---------------------------------------------------|
| I. Cero CSS Inline | CUMPLE | Tests en `test_validators.py` e `integration/` intentan inyectar `style="..."` y verifican rechazo estricto |
| II. JavaScript Acotado | CUMPLE | Tests de parsing aseguran que se capturen y etiqueten scripts acotados por lámina |
| III. Preservacion Determinista | CUMPLE | Pruebas verifican que `pra_helper.py` escriba de forma exacta y predecible todos los archivos |
| IV. Construccion Progresiva | CUMPLE | Tests constitucionales simulan salto de sesiones ($N$ sin $N-1$) y comprueban aborto de ejecución |
| V. Documentacion en Espanol | CUMPLE | Todos los docstrings, nombres de tests y especificaciones están en español |

---

## Estrategia de Aislamiento y Mapeo de Rutas

Para asegurar que las pruebas no alteren el directorio actual `C:\laragon\www\test\test\test_opencode\`:
1. **Fixture `isolated_env`:** Cada test de integración se ejecuta cambiando el directorio de trabajo actual (`os.chdir`) a un `tmp_path` limpio proporcionado por `pytest`.
2. **Plantillas maestras:** `conftest.py` provee copias de respaldo o mocks de `research_prompts_templates/` para que `init` y `prompt-session` encuentren las plantillas sin depender de la red o junction externa.
3. **Restauración de CWD:** Se utiliza una fixture con `yield` para restaurar `os.chdir(original_cwd)` al finalizar cada test.

---

## Métricas de Calidad y Criterios de Parada

- **Pasada del 100%:** `pytest` debe finalizar con código de retorno `0`.
- **Métrica de Cobertura:**
  - `pra_helper.py`: ≥ 85% de líneas cubiertas.
- **Comando de Verificación Recomendado:**
  ```bash
  pytest --cov=pra_helper --cov-report=term-missing
  ```
