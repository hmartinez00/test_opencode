# Sesión PRA: Iteración 003 Commiteada, Primera Corrida E2E Mock Exitosa y Pre-vuelo del Backend Real

> **Fecha:** 2026-08-22  
> **Modelo:** opencode/big-pickle  
> **Rama:** `main`  
> **Último commit:** `da18dff` (resumen de sesión + gitignore de artefactos de corridas; iteración 003 ya pusheada en `e260836` y `3731485`)

---

## Objetivo del Proyecto

Sistema **Presentation Automator (PRA v1.0)**: automatizar la generación modular y progresiva de presentaciones **Reveal.js** empaquetadas en plantillas **Blade** para Laravel, usando la metodología Speckit.

**Filosofía:** Plan Maestro → Construcción Progresiva por Sesiones → Empaquetado final.

---

## Última Compactación (2026-08-22): Commits + Primera Corrida E2E Mock EXITOSA + Pre-vuelo Opción B

### 1. Commits y push realizados
- `e260836`: Iteración 003 completa (`pra_orchestrator.py`, `specs/003-*`, `mocks_llm/`, `tests/conftest.py`, 7 tests nuevos) — 20 archivos, +2622 líneas.
- `3731485`: Limpieza de rutas hardcodeadas muertas (`C:\laragon\www\test\test\test_opencode\` eliminadas de `pra_helper.py` en `cmd_init`/`cmd_prompt_session`, `AGENTS.md`, este documento y specs/001+002) y documentación del junction restaurado.
- Ambos PUSHEADOS a `origin/main` (`c915ff8..3731485`). El código queda limpio; solo quedan artefactos generados sin trackear (ver abajo).

### 2. Primera corrida E2E desatendida REAL: ÉXITO TOTAL (valida T322)
Comando: `python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend mock`
- **exit 0 en ~23 s**, las 6 fases completadas al PRIMER intento (intentos=1 en todo el estado): init → save-plan → sesion 1 → sesion 2 → pytest (95 passed, cobertura 88.0%) → zip.
- Puertas constitucionales verdes: `sin_css_inline=true` y `laminas_faltantes=[]` en ambas sesiones; verificación independiente con grep confirmó cero `style="..."` en todo `intro_docker/`.
- Artefactos generados EN el workspace (aún presentes):
  - `intro_docker/` (**sin trackear**): `presentation_plan.json` normalizado (2 sesiones, 3 láminas), `class_registry.json` (4 clases; ojo: `text-center` queda `implementada=false` por diseño de la fixture), `js_registry.json` (ripple-effect), `manifest_draft.blade.php`, `styles/scripts.blade.php` acumulados, `sesion1/{que-es-docker,arquitectura}.blade.php`, `sesion2/comandos-basicos.blade.php`, carpetas `*_additions/`.
  - `outputs.zip` (15 archivos; **ignorado** por `.gitignore`).
  - `orchestration_state.json` y `orchestration_log.txt` (**sin trackear**): todas las fases `completada`.
- Conclusión: la maquinaria de orquestación funciona de punta a punta con backend mock.

### 3. Pre-vuelo Opción B (backend opencode REAL) — PENDIENTE de ejecutar
- CLI disponible: `opencode v1.18.21`; el orquestador invoca subprocess `["opencode", "run", "<prompt>"]`, timeout default 300 s (usar `--timeout-s 600` según quickstart de spec 003). El `OpenCodeBackend` NUNCA ha corrido E2E: sería su estreno real.
- ANTES de lanzar: archivar los artefactos de la corrida mock (propuesto: carpeta `backup_mock_corrida1/`) porque NO hay aislamiento entre corridas en el mismo workspace — `run` sobrescribe `orchestration_state.json` y los artefactos previos se mezclarían con los de la corrida real.
- Comando planeado: `python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend opencode --timeout-s 600 --max-retries 3`. Si una fase falla: `resume` retoma desde la última fase válida.

---

## Lo Que Se Hizo en Esta Sesión

### Contexto acumulado (iteraciones previas)
- **Iteración 001**: motor `pra_helper.py` (718+ líneas) con comandos `init`, `save-plan`, `prompt-session`, `process-session`, `zip`.
- **Iteración 002**: sistema de testing pytest (30 pruebas, cobertura 88%) y corrección de defectos D001-D003 del motor.

### Iteración 003 (ESTA SESIÓN): `specs/003-orquestador-automatizado-pra/` completa e implementada

#### Fase Speckit (borrador aprobado, 8 documentos)
- `spec.md`: 6 historias (US1-US6), FR-201..FR-212, SC-201..SC-205.
- `research.md`: decisiones D1-D7 (subprocess delegado en pra_helper, estado JSON plano atómico, backends ABC, regex de cobertura, mock con fixtures deterministas, reflexión de error en reintentos, zip excluye artefactos de orquestación).
- `data-model.md`, `plan.md`, `contracts/orchestrator-contract.md`, `quickstart.md` (7 escenarios E2E), `tasks.md` (T301-T322 en 6 fases, todas marcadas ✅), `checklists/requirements.md`.

#### Implementación: `pra_orchestrator.py` (792 líneas)
| Componente | Detalle |
|-----------|---------|
| CLI | Subcomandos `run <doc> [--backend mock\|opencode] [--max-retries N]`, `resume`, `status`. Error argparse → exit 4 |
| Códigos de salida | `0` éxito · `1` validación incumplida · `2` estado/secuencialidad · `3` backend no disponible · `4` uso incorrecto |
| Estado | `orchestration_state.json` con persistencia ATÓMICA (`tempfile.mkstemp` + `os.replace`); autómata `TRANSICIONES_VALIDAS` impide saltos ilegales; `resume` retoma desde fase pendiente/fallida |
| Auditoría | `orchestration_log.txt` append-only: fases, intentos, motivos de fallo, validaciones. Ambos archivos quedan FUERA del zip |
| Backends | `LLMBackend(ABC)` → `MockBackend(fixtures_dir, secuencia)` y `OpenCodeBackend(timeout_s, binario)` que invoca el CLI real de OpenCode; FileNotFoundError/TimeoutExpired/rc≠0 → `BackendError` → exit 3 |
| Reintentos | Bucle por sesión hasta `--max-retries`; ante fallo anexa al prompt un bloque de REFLEXIÓN con el motivo (violaciones CSS inline detectadas por el orquestador, o detalle JSON del motor si el exit code del helper fue ≠ 0) |
| Puertas constitucionales | Tras cada sesión valida: exit code 0 del motor, cero `style="..."` en láminas nuevas, laminas completas según plan (compara `<x-slide view="sesionN.id"` contra plan normalizado) |
| Fases pytest/zip | Ejecuta `pytest --cov=pra_helper --cov=pra_orchestrator` REAL vía subprocess; parsea resumen y fila de cobertura con `COVERAGE_ROW_PATTERN = r"pra_helper\.py\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)%"` (y análoga para orchestrator); exige passed > 0, failed == 0 y cobertura ≥ 85% antes de permitir zip |

**Regla clave save-plan**: si el motor sale con código 2 (JSON de plan inválido tras normalización) el orquestador ABORTA inmediatamente con exit 2 sin gastar reintentos; cualquier otro código ≠ 0 entra al bucle de reflexión.

**Fixtures mock** (`mocks_llm/plan.txt`, `sesion1.txt`, `sesion2.txt`): respuestas LLM deterministas del ejemplo `introduccion_docker` (2 sesiones). OJO: `MockBackend.secuencia` se aplica GLOBALMENTE en orden plan → sesion1 → sesion2; las fixtures de tests de retry deben cubrir toda la secuencia.

#### Pruebas nuevas (65) — suite total: 95 verdes, cobertura 88%/88%
| Categoría | Archivo | Pruebas |
|-----------|---------|---------|
| Unitarias | `test_orchestrator_state.py` (26), `test_orchestrator_validations.py` (9), `test_orchestrator_backends.py` (10) | 45 |
| Integración | `test_cli_orchestrator_run_mock.py` (5), `test_cli_orchestrator_retry.py` (5), `test_cli_orchestrator_resume.py` (5) | 15 |
| Constitucionales | `test_orchestrator_rules.py` (5): whitelist raíz `{documento_fuente.md, intro_docker/, outputs.zip, orchestration_state.json, orchestration_log.txt}`, plan sin sesiones→exit 2, pytest rojo impide zip, fallos simulados vía monkeypatch de `po.run_helper` | 5 |

Casos cubiertos: corrida E2E desatendida EXIT=0, determinismo entre dos corridas (hash SHA-256 del ÁRBOL del proyecto, no del zip), retry contaminada→válida, agotamiento→exit 1 y luego `resume` exitoso, backend inagotable→exit 3, binario inexistente→exit 3, transiciones inválidas→exit 2.

Fixtures nuevas en `tests/conftest.py`: `run_orchestrator(capsys)` (captura SystemExit de argparse y retorna `(codigo, stdout)`); `disable_setup_utf8` extendida para parchear también `pra_orchestrator.setup_utf8`.

#### Documentación actualizada
- `AGENTS.md`: estructura (orquestador + mocks_llm + spec 003), nueva "Fase de Orquestacion Desatendida", mandatos con 95 pruebas / doble cobertura ≥ 85%.
- `README.md`: sección "Orquestador Automático" con ejemplos run/resume/status, conteo de suite actualizado.
- `quickstart.md` Escenario 2 corregido: el determinismo se compara por árbol del proyecto porque el ZIP guarda timestamps y difiere byte a byte entre corridas.

---

## Ambiente y Línea Base (importante para reproducir)

- **Python 3.13.3**, Windows, bash shell. `pytest` NO venía instalado: se instaló `python -m pip install pytest pytest-cov` (pytest 9.1.1, pytest-cov 7.1.0).
- **Historial del junction `research_prompts_templates/`:** en la sesión anterior el junction apuntaba a una ruta inexistente y las plantillas se recrearon LOCALES para restaurar la línea base. En la sesión ACTUAL el junction fue RESTAURADO apuntando a `C:\laragon\www\researchs\workflow\research_prompts_templates` (plantillas originales con contenido correcto) y se eliminaron las copias locales, además de limpiar las rutas hardcodeadas muertas de `pra_helper.py`. Placeholders que reemplaza pra_helper: `{{session_number}}`, `{{session_title}}`, `{{project_title}}`, `{{folder_name}}`, `{{objetivos}}`, `{{laminas_json}}`, `{{class_registry_actual}}`, `{{js_registry_actual}}`.
- **Bug crítico corregido durante smoke test**: en Windows `Path("x.blade.php").stem` devuelve `"x.blade"` (doble sufijo). `validar_post_sesion` compara con `blade.name[: -len(".blade.php")]`.

---

## Estructura de Archivos del Proyecto

```
C:\laragon\www\test_opencode\
├── research_prompts_templates/        # Junction a C:\laragon\www\researchs\workflow\research_prompts_templates (RESTAURADO)
│   ├── presentation_plan_meta_prompt.md
│   └── presentation_slide_meta_prompt.md
├── AGENTS.md                          # Directrices para agentes IA (actualizado iteración 003)
├── README.md                          # Documentación pública (actualizada iteración 003)
├── SESION_PRA_RESUMEN.md              # Este documento
├── pra_helper.py                      # Motor de automatización (único escritor de artefactos del proyecto)
├── pra_orchestrator.py                # Orquestador automático (792 líneas, iteración 003)
├── mocks_llm/                         # Fixtures deterministas del MockBackend
│   ├── plan.txt / sesion1.txt / sesion2.txt
├── pytest.ini                         # testpaths=tests, pythonpath=.
├── tests/                             # Suite: 95 pruebas, cobertura 88%/88%
│   ├── conftest.py                    # run_cli, run_orchestrator, disable_setup_utf8, aislamiento tmp_path
│   ├── unit/                          # 12 motor + 45 orquestador
│   ├── integration/                   # 13 motor + 15 orquestador
│   └── constitutional/                # 5 motor + 5 orquestador
├── specs/
│   ├── 001-sistema-automatizacion-presentaciones-pra/   # Especificación del motor
│   ├── 002-sistema-testing-pra/                          # Especificación del testing
│   └── 003-orquestador-automatizado-pra/                 # ESTA ITERACIÓN (8 docs, T301-T322 ✅)
│       ├── spec.md / research.md / data-model.md / plan.md
│       ├── quickstart.md / tasks.md
│       ├── contracts/orchestrator-contract.md
│       └── checklists/requirements.md
├── ejemplos/introduccion_docker/documento_fuente.md      # Documento de prueba E2E real
├── backup/mock_corrida1/                # ARCHIVO: salida completa de la corrida mock E2E
│   ├── intro_docker/ / outputs.zip      #   (backup/ y outputs.zip ignorados por .gitignore)
│   └── orchestration_state.json / orchestration_log.txt
└── .specify/memory/constitution.md                       # Constitución (5 principios)
```

**Estado git:** último commit `da18dff`, pusheado a `origin/main`. La iteración 003 quedó commiteada en dos commits (`e260836` código+tests, `3731485` limpieza/docs) y `da18dff` actualizó este resumen e ignoró los artefactos de corridas en `.gitignore`. Los artefactos de la corrida mock están archivados en `backup/mock_corrida1/` (ignorado), por lo que el working tree queda limpio para lanzar la corrida con backend real.

---

## Constitución del Proyecto (5 Principios No Negociables)

1. **Cero CSS Inline:** Prohibido `style="..."` dentro de las láminas Blade
2. **JavaScript acotado por lámina:** Todo script debe encapsularse y comentarizarse
3. **Preservación determinista del estado:** Solo `pra_helper.py` escribe archivos del proyecto generado (el orquestador solo escribe sus 2 artefactos propios)
4. **Construcción progresiva secuencial:** Sesión N requiere sesión N-1 completa
5. **Toda documentación técnica en español**

---

## Contrato CLI Real de pra_helper.py (lo que el orquestador consume)

- SUBCOMANDOS: `init <doc>`, `save-plan '<json>'`, `prompt-session N`, `process-session N '<resp>'`, `zip` (NO flags `--`).
- Errores del motor salen como JSON por STDOUT (no stderr); el orquestador los usa como detalle para la reflexión.
- `save-plan` exige JSON CRUDO como argumento (sin cercos ```json``` ni prosa).
- Violaciones CSS inline → exit 2 ANTES de escribir estilos/scripts (el reintento parte limpio).
- `find_project_dir()` escanea el CWD buscando `presentation_plan.json`.

---

## Cómo Usar el Sistema

### Flujo manual (motor):
```bash
python pra_helper.py init documento_fuente.md > prompt_plan.txt
# (LLM genera JSON del plan)
python pra_helper.py save-plan '{"titulo":"...", "carpeta_snake_case":"...", ...}'
python pra_helper.py prompt-session 1 > prompt_sesion1.txt
# (LLM genera respuesta de 5 bloques)
python pra_helper.py process-session 1 "respuesta_completa_del_llm..."
python pra_helper.py zip
```

### Flujo desatendido (orquestador, iteración 003):
```bash
# Corrida completa con backend mock determinista
python pra_orchestrator.py run documento_fuente.md --backend mock

# Con backend real y reintentos configurables
python pra_orchestrator.py run documento_fuente.md --backend opencode --max-retries 3

# Reanudar corrida interrumpida / inspeccionar estado
python pra_orchestrator.py resume
python pra_orchestrator.py status
```

### Verificación obligatoria tras cualquier cambio:
```bash
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q
# Esperado: 95 passed, cobertura pra_helper >= 85% (actual 88%), pra_orchestrator >= 85% (actual 88%), ~20s
```

---

## Esquemas JSON Importantes

### PresentationPlan (`[carpeta]/presentation_plan.json`)
```json
{
  "titulo": "string",
  "carpeta_snake_case": "string",
  "idioma": "es",
  "resumen_general": "string",
  "sesiones": [{
    "numero": 1,
    "titulo": "string",
    "objetivo_pedagogico": "string",
    "laminas": [{
      "orden": 1,
      "id_kebab_case": "string-kebab-case",
      "tipo": "portada|contenido|interactiva|cierre",
      "objetivo": "string",
      "insumos": []
    }]
  }]
}
```

### class_registry.json / js_registry.json
```json
{
  "clases": [
    {"nombre": "clase-css", "descripcion": "...", "implementada": true, "sesion_creacion": 1}
  ],
  "comportamientos": [
    {"nombre": "comportamiento-js", "descripcion": "...", "implementada": true, "sesion_creacion": 1}
  ]
}
```

### Estado de orquestación (`orchestration_state.json`)
Esquema completo en `specs/003-orquestador-automatizado-pra/data-model.md`: documento, backend, max_reintentos, fases `{init, save_plan, sesiones[], pytest, zip}` cada una con `{estado: pendiente|en_progreso|completada|fallida, intentos, ...}`, sesiones además con `validaciones` y `motivo_ultimo_fallo`.

---

## Discrepancia Conocida: Nombres de Campos

Las plantillas maestras usan `nro`/`folder_name`/`titulo_sesion`/`objetivos`/`id`; el data-model espera `numero`/`carpeta_snake_case`/`titulo`/`objetivo_pedagogico`/`id_kebab_case`. `normalize_plan()` en pra_helper.py convierte automáticamente entre ambos formatos.

---

## Formato de Respuesta LLM Esperado (5 bloques)

```
{{- sesion1/slide-id.blade.php -}}
...contenido Blade...

**BLOQUE 2**
```css
...estilos CSS...
```

**BLOQUE 3**
```javascript
// ...scripts JavaScript...
```

**BLOQUE 4**
<x-slide view="sesion1.slide-id" data-title="Título" />

**BLOQUE 5**
```json
{
  "nuevas_clases": [{"nombre": "...", "proposito": "...", "implementada": true}],
  "clases_materializadas": ["nombre-clase"],
  "nuevos_comportamientos": [{"nombre": "...", "proposito": "...", "implementada": true}],
  "comportamientos_materializados": ["nombre-comportamiento"]
}
```
```

---

## Tareas Completadas de la Iteración 003 (T301-T322)

| Fase | Tareas | Contenido |
|------|--------|-----------|
| 1 | T301-T303 | Esqueleto CLI, estado atómico + transiciones, log auditoría |
| 2 | T304-T307 | Backends LLM + fixtures `mocks_llm/` |
| 3 | T308-T313 | Motor de orquestación: init/save_plan/session/retry/pytest/zip/status/resume |
| 4 | T314-T317 | Pruebas unitarias e integración del orquestador |
| 5 | T318-T320 | Pruebas constitucionales + suite completa verde con cobertura |
| 6 | T321-T322 | Documentación AGENTS/README + validación E2E real |

---

## Iteración 004: Subdirectorio Maestro de Proyectos Generados (2026-08-24)

**Spec**: `specs/004-subdirectorio-maestro-proyectos-pra/` (T401-T413). **Estado**: IMPLEMENTADA, suite 105/105 verde, cobertura 89% (motor) / 88% (orquestador).

- **Cambio central**: todo proyecto generado vive bajo el subdirectorio maestro `output_projects/` (overridable via env var `PRA_OUTPUT_DIR`); `outputs.zip` también se genera dentro (`output_projects/outputs.zip`). La raíz del repositorio queda limpia.
- **Motor (`pra_helper.py`)**: constante única `OUTPUT_BASE_DIR = Path(os.environ.get("PRA_OUTPUT_DIR", "output_projects"))`; `get_project_dir()` antepone la base; `find_project_dir()` busca PRIMERO en el maestro y aplica fallback sobre la raíz para proyectos legacy; `cmd_zip` crea el maestro si falta y escribe el zip dentro.
- **Orquestador (`pra_orchestrator.py`)**: misma constante y estrategia dual en `buscar_proyecto()`; `fase_zip` valida el zip bajo el maestro. Sin cambios de esquema de estado ni códigos de salida.
- **Compatibilidad legacy**: proyectos antiguos en la raíz siguen procesables vía fallback; NO hay migración automática. Ante colisión, precede el proyecto del maestro.
- **Tests**: aserciones actualizadas a `<tmp>/output_projects/intro_docker` usando `pra_helper.OUTPUT_BASE_DIR` / `pra_orchestrator.OUTPUT_BASE_DIR` como fuente de verdad; nuevos archivos `tests/unit/test_output_base_dir.py` (9 pruebas: default, igualdad motor/orquestador, precedencia dual, fallback) e `tests/integration/test_cli_output_dir_override.py` (subprocess real con `PRA_OUTPUT_DIR=custom_out`). `conftest.py` elimina `PRA_OUTPUT_DIR` antes de importar los módulos (inmunidad al entorno del host) + fixture autouse por prueba.
- **Constitucional reforzado**: whitelist de raíz tras corrida E2E = `{documento_fuente.md, output_projects/, orchestration_state.json, orchestration_log.txt}`; se verifica que NO existan `intro_docker/` ni `outputs.zip` sueltos en raíz.
- **`.gitignore`**: añadido `output_projects/`.
- **Docs**: árbol actualizado en AGENTS.md y README.md; umbral de suite actualizado a 105 pruebas.

---

## Cómo Continuar

1. **Para usar el sistema desatendido:** `python pra_orchestrator.py run <documento> --backend mock` (o `opencode` con CLI real disponible).
2. **Para modificar `pra_helper.py` o `pra_orchestrator.py`:** ejecutar SIEMPRE la suite completa antes de cerrar; mantener ≥ 105 pruebas y cobertura ≥ 85% en ambos módulos.
3. **Commits de esta iteración: YA REALIZADOS** — `e260836` (spec+implementación+tests) y `3731485` (limpieza de rutas+docs), ambos pusheados a `origin/main`.
4. **SIGUIENTE PASO ACORDADO (Opción B):** primera corrida real con `--backend opencode --timeout-s 600 --max-retries 3`, previo archivado de los artefactos mock (ver sección "Última Compactación"); luego evaluar la calidad del contenido generado por el LLM. Mejoras futuras adicionales: paralelización no aplica por constitución IV, soporte multi-documento.

---

## Notas para el Próximo Modelo

- **El orquestador delega TODA mutación de artefactos en `pra_helper.py` vía subprocess**: sus únicas escrituras propias son `orchestration_state.json` y `orchestration_log.txt`.
- **Contrato completo del orquestador:** `specs/003-orquestador-automatizado-pra/contracts/orchestrator-contract.md`; decisiones técnicas D1-D7 en `research.md`.
- **MockBackend.secuencia es global** (orden plan → s1 → s2): al escribir tests de retry, la secuencia debe cubrir todas las llamadas.
- **save-plan con exit 2 del motor = aborto inmediato** (JSON inválido no se reintenta); cualquier otro error entra al bucle de reflexión.
- **Determinismo SC-202 se verifica comparando el árbol del proyecto**, nunca los bytes del zip (timestamps).
- **Los tests usan tmp_path aislado y nunca escriben en el workspace real**; `run_cli`/`run_orchestrator` en `conftest.py` invocan las funciones main con argv simulado y capturan SystemExit.
- **La herramienta `write` falla con payloads > ~10KB** ("JSON Parse error"): dividir archivos largos en Write inicial + Edit appends.
- **La constitución está en** `.specify/memory/constitution.md`; los esquemas JSON en `specs/001-*/data-model.md` y `specs/003-*/data-model.md`.
