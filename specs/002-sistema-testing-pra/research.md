# Research y Decisiones Técnicas: Sistema de Testing PRA (002-sistema-testing-pra)

## Decisiones Principales de Diseño

### 1. Framework de Testing: `pytest`
- **Alternativas consideradas**: `unittest` (stdlib), `pytest`.
- **Decisión**: `pytest`.
- **Justificación**: `pytest` ofrece mejor manejo de fixtures (`tmp_path`, `capsys`), sintaxis asertiva limpia y soporte nativo para reportes de cobertura vía `pytest-cov`.

### 2. Estrategia de Invocación CLI: Importación e Invocación Directa vs `subprocess`
- **Alternativas consideradas**:
  - Opción A: Invocación vía `subprocess.run(["python", "pra_helper.py", ...])`.
  - Opción B: Invocación directa importando `pra_helper` y ejecutando `pra_helper.main(sys_args)` con `capsys` y `monkeypatch`.
- **Decisión**: Combinación (Principalmente Opción B para rapidez y cobertura exacta de líneas, comprobando Opción A para aislamiento completo en casos límite).
- **Justificación**: La invocación directa mediante `main()` permite que `pytest-cov` registre exactamente qué líneas de `pra_helper.py` fueron ejecutadas en cada comando.

### 3. Manejo de Aislamiento de Archivos (`tmp_path`)
- **Estrategia**:
  - Cada test que interactúe con el sistema de archivos operará en su propio directorio `tmp_path`.
  - La fixture `run_in_tmp_path` se encargará de cambiar temporalmente el directorio de trabajo (`os.chdir(tmp_path)`) y crear la estructura base o copiar la plantilla si es necesario.
  - Al terminar el test, se restaura el directorio de trabajo original, previniendo cualquier efecto secundario sobre el workspace local.

### 4. Mocks para Plantillas Maestras (`research_prompts_templates/`)
- **Estrategia**:
  - `pra_helper.py` busca plantillas en `research_prompts_templates/`.
  - En `conftest.py`, la fixture `setup_prompt_templates` se asegura de que exista un directorio de plantillas con contenido dummy/plantilla en el `tmp_path` o en la ruta esperada, de modo que los tests no fallen si el junction local no estuviese disponible.
