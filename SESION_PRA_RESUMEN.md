# Continuación de Sesión: Orquestador Automatizado pra_orchestrator.py (Iteración 003)

> **Fecha:** 2026-08-22  
> **Modelo:** opencode/big-pickle  
> **Rama:** `main`  
> **Último commit:** `c915ff8` (los cambios de esta iteración están SIN commitear)

---

## Objetivo del Proyecto

Sistema **Presentation Automator (PRA v1.0)**: automatizar la generación modular y progresiva de presentaciones **Reveal.js** empaquetadas en plantillas **Blade** para Laravel, usando la metodología Speckit.

**Filosofía:** Plan Maestro → Construcción Progresiva por Sesiones → Empaquetado final.

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
├── pra_orchestrator.py                # Orquestador automático (792 líneas, iteración 003) — SIN COMMITEAR
├── mocks_llm/                         # Fixtures deterministas del MockBackend — SIN COMMITEAR
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
└── .specify/memory/constitution.md                       # Constitución (5 principios)
```

**Estado git:** último commit `c915ff8`. Cambios sin commitear: `pra_orchestrator.py`, `mocks_llm/`, `specs/003-*`, 7 archivos de test nuevos, modificaciones en `AGENTS.md`, `README.md`, `tests/conftest.py`.

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
# Esperado: 95 passed, cobertura pra_helper >= 85% (actual 88%), pra_orchestrator >= 85% (actual 88%), ~13s
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

## Cómo Continuar

1. **Para usar el sistema desatendido:** `python pra_orchestrator.py run <documento> --backend mock` (o `opencode` con CLI real disponible).
2. **Para modificar `pra_helper.py` o `pra_orchestrator.py`:** ejecutar SIEMPRE la suite completa antes de cerrar; mantener ≥ 95 pruebas y cobertura ≥ 85% en ambos módulos.
3. **Para commitear esta iteración:** los cambios están sin commitear (ver estado git arriba); sugerencia: un commit para spec+implementación+tests, otro para docs.
4. **Posibles mejoras futuras:** backend opencode real probado E2E (solo se probó mock), paralelización no aplica por constitución IV, soporte multi-documento.

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
