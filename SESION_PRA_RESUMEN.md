# Resumen de Sesion PRA — Contexto para Reanudar

Este documento registra el estado del proyecto Presentation Automator (PRA) y el contexto necesario para reanudar cualquier sesion de desarrollo. Es la fuente de verdad operativa para agentes de IA y desarrolladores.

---

## Sistema en Sintesis

**Objetivo**: Automatizar la generacion modular y progresiva de presentaciones interactivas basadas en **Reveal.js** empaquetadas en plantillas **Blade** compatibles con un framework Laravel. Filosofia: **Plan Maestro + Construccion Progresiva por Sesiones**.

**Documentos maestros**:
- `AGENTS.md`: guia maestra para agentes (arquitectura, mandatos, flujo).
- `.specify/memory/constitution.md`: 5 principios no negociables (Cero CSS Inline, JS acotado, Preservacion via `pra_helper.py`, Plan-First, Documentacion en espanol).

---

## Arquitectura de Archivos

- `pra_helper.py` — **Unico punto de escritura** de artefactos del proyecto (CLI: `init`, `save-plan`, `prompt-session`, `process-session`, `consolidate`, `limpiar`, `zip`).
- `pra_orchestrator.py` — Orquestador desatendido (`run`, `resume`, `status`); delega toda mutacion en `pra_helper.py`; propios artefactos: `orchestration_state.json` y `orchestration_log.txt`.
- `mocks_llm/` — Respuestas LLM deterministas del backend mock (`plan.txt`, `sesion1.txt`, `sesion2.txt`).
- `tests/` — Suite pytest en `unit/`, `integration/` y `constitutional/`.
- `specs/` — Especificaciones por iteracion (001-011).
- `research_prompts_templates/` — Enlace de union a plantillas maestras de prompts.
- `PRA_OUTPUT_DIR` (default `C:\laragon\www\product_samples\slides`) — Directorio maestro de proyectos generados.
- `ejemplos/introduccion_docker/documento_fuente.md` — Documento fuente de prueba.

---

## Varables de Entorno Relevantes

| Variable | Proposito |
|----------|-----------|
| `PRA_OUTPUT_DIR` | Ruta base (contenedora) de proyectos generados. No es el nombre del proyecto. |
| `PRA_ACTIVE_PROJECT` | `carpeta_snake_case` del proyecto activo entre varios (iteracion 007). |
| `PRA_PLAN_ESTRICTO=1` | Convierte advertencias de calidad del plan en error. |
| `PRA_AUDIO_ESTRICTO=1` | Exige el BLOQUE 6 y bloquea incoherencias audiovisuales. |

Sintaxis: PowerShell `$env:X = "valor"`; Bash `export X="valor"`.

---

## Estado de la Suite de Pruebas

> Ultima verificacion: **2026-09-02** (iteracion 011 completada)

- **173 pruebas** en verde (`python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q`).
- Cobertura: `pra_helper.py` **90%**, `pra_orchestrator.py` **85%** (umbral minimo: 85%).
- Invocar siempre via `python -m pytest` (nunca `pytest.exe`, que dispara falsos positivos del antivirus).

### Mapa de la Suite

- `tests/unit/` — Parser de guion, normalizacion de plan (orden, data_title), bloque 6 regex, deduplicacion, registries, validadores, calidad de salida, limpieza, base de salida, orquestador (state, validations, backends).
- `tests/integration/` — CLI: init, save-plan (incl. dedup y --plan-file), session, consolidate, limpieza, zip, audio narracion, orquestador (run mock, resume, retry), robustez/coherencia, output dir override.
- `tests/constitutional/` — Audio rules, constitution rules, limpieza rules, orchestrator rules.

---

## Iteraciones Completadas

### 001 — Sistema de automatizacion de presentaciones PRA
Cimientos: contrato CLI `pra_helper.py`, normalizacion de plan, registries (`class_registry.json`, `js_registry.json`), manifest draft, estructura por sesiones, consolidacion.

### 002 — Sistema de testing PRA
Framework pytest, fixtures compartidas, aislamiento `tmp_path`, mocks LLM, cobertura minima.

### 003 — Orquestador automatizado PRA
`pra_orchestrator.py` con `run`/`resume`/`status`, backend mock/opencode, puertas constitucionales por sesion y bucle de reintentos.

### 004 — Subdirectorio maestro de proyectos
Proyectos bajo `<PRA_OUTPUT_DIR>/<carpeta_snake_case>/`; `PRA_OUTPUT_DIR` para override; prompt interactivo o abort con exit 1.

### 005 — Directorio maestro, rutas y zip
Resolucion/validacion de ruta base, utilidad `zip` manual (no invocada en flujo automatico).

### 006 — Consolidacion de estructura de presentaciones
`manifest.blade.php` por `session[N]/`, `assets/`, `global/`, sin duplicados ni CSS inline.

### 007 — Calidad de salida de presentaciones
`PRA_ACTIVE_PROJECT`, validaciones de contenido, entry points de framework Laravel.

### 008 — Limpieza de artefactos residuales
Fase `cleanup`: respaldo `backup/fuente/` idempotente, verificacion del lote protegido, eliminacion de residuales.

### 009 — Robustez y coherencia
Coherencia plan-vs-disco (faltantes, huerfanas, duplicadas), `PRA_PLAN_ESTRICTO`, reporte `coherencia`.

### 010 — Guion narrativo y coherencia audiovisual
BLOQUE 6 en respuestas de sesion, `[slide: N]` en base cero, `assets/audio/guion_sesionN.txt`, validacion estructural/semantica, `PRA_AUDIO_ESTRICTO`.

### 011 — Mejoras P5-P11 y correcciones de planes
Seis correcciones al motor + practicas operativas. **Ver seccion siguiente.**

---

## Iteracion 011 — Correcciones al Motor (detalle)

**Especificacion**: `specs/011-mejoras-p5-p11-correcciones-planes/` (`spec.md`, `plan.md`, `tasks.md`, `test_plan.md`).

### Grupo A — Correcciones en `pra_helper.py` (implementadas)

| ID | Correccion | Evidencia |
|----|-----------|-----------|
| **A1 (P5)** | Regex BLOQUE 6 tolerante a linea en blanco antes del fence | `parse_llm_response` (regex `\n\s*````) |
| **A2 (P6)** | Deduplicacion de clases/JS por nombre en `save-plan` | `_deduplicar_por_nombre` + seeding registries |
| **A3 (P7)** | Auto-numerado de `orden` faltante (1..N) con advertencia/error estricto | `normalize_plan`, `_validar_calidad_plan` |
| **A4 (P8)** | Preservar `data_title` en plan y manifest final (fallback `titulo_legible`) | `normalize_plan`, `cmd_save_plan` |
| **A5 (10)** | Unificar prefijo: lote `session[N]/` (ingles), internos/backup `sesion[N]/` (espanol) | Convencion documentada en AGENTS.md |
| **A6 (P3-bonus)** | `save-plan --plan-file <ruta>` (UTF-8) | Nuevo flag; `json_plan` opcional |

### Grupo B — Practicas operativas (documentadas en AGENTS.md, seccion 4)

- **B1**: `PRA_ACTIVE_PROJECT` obligatorio ante varios proyectos.
- **B2**: `PRA_OUTPUT_DIR` explicito antes del primer `save-plan`.
- **B3**: JSON de plan por archivo (preferir `--plan-file`).
- **B4**: Respuestas de sesion por `--respuesta-file` (limitacion argv Windows).
- **B5**: Limpiar acumuladores (`styles`/`scripts.blade.php`) antes de reprocesar.
- **B6**: Localizar ruta real del `.ipynb` antes de `init`.

### Pruebas nuevas (22)
- `tests/unit/test_bloque6_regex.py` (5)
- `tests/unit/test_normalize_plan_orden.py` (4)
- `tests/unit/test_normalize_plan_data_title.py` (4)
- `tests/integration/test_cli_save_plan_dedup.py` (4)
- `tests/integration/test_cli_save_plan_file.py` (5)

---

## Definicion de Hecho (DoD) — Iteracion 011

- [x] Grupo A implementado en `pra_helper.py` sin romper la interfaz CLI existente.
- [x] Pruebas nuevas presentes en `tests/` y suite en verde.
- [x] Cobertura `pra_helper.py` (90%) y `pra_orchestrator.py` (85%) >= 85%.
- [x] Grupo B reflejado en `AGENTS.md` (seccion 4).
- [x] Re-validacion E2E manual confirmada (orden, data_title, dedup, --plan-file).

---

## Notas y Pendientes

- `SESION_PRA_RESUMEN.md` creado en esta iteracion (documento vivo, actualizar tras cada iteracion).
- `specs/011` mantiene los 4 archivos de planificacion (spec, plan, tasks, test_plan) como trazabilidad; la implementacion ya quedo cerrada.
- Al reanudar una nueva iteracion: leer `PROXIMA_ITERACION_MEJORAS.md` (si existe) y `AGENTS.md`, confirmar baseline verde, luego escribir spec/plan/tasks/test_plan antes de tocar codigo.
