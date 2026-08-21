# Continuación de Sesión: Implementación pra_helper.py

> **Fecha:** 2026-08-20  
> **Modelo:** opencode/big-pickle  
> **Rama:** `main`  
> **Último commit:** `53d235f`

---

## Objetivo del Proyecto

Sistema **Presentation Automator (PRA v1.0)**: automatizar la generación modular y progresiva de presentaciones **Reveal.js** empaquetadas en plantillas **Blade** para Laravel, usando la metodología Speckit.

**Filofía:** Plan Maestro → Construcción Progresiva por Sesiones → Empaquetado final.

---

## Lo Que Se Hizo en Esta Sesión

### 1. Análisis del PRA v1.0 (contexto previo)
- Se estudió el flujo completo del sistema PRA
- Se crearon las 5 tareas iniciales (completadas en sesiones anteriores):
  - Tarea 1: Research del sistema PRA
  - Tarea 2: Mapeo de comandos
  - Tarea 3: Especificación de plantillas
  - Tarea 4: Definición de la CLI
  - Tarea 5: Creación de AGENTS.md
- Se creó la junction `research_prompts_templates` → `C:\laragon\www\test\researchs\workflow\research_prompts_templates`
- Se creó `AGENTS.md` con las directrices contextuales para agentes

### 2. Fase Speckit (completada en sesiones anteriores)
- `/speckit-specify`: `spec.md` y `checklists/requirements.md`
- `/speckit-plan`: `plan.md`, `research.md`, `data-model.md`, `contracts/cli-contract.md`, `quickstart.md`
- `/speckit-tasks`: `tasks.md` con 19 tareas en 7 fases

### 3. Implementación de pra_helper.py (ESTA SESIÓN)
Se implementó el script completo `pra_helper.py` (718 líneas) con los 5 comandos:

| Comando | Función | Commit |
|---------|---------|--------|
| `init <doc>` | Lee documento fuente, genera prompt del Plan Maestro | `53d235f` |
| `save-plan <json>` | Guarda plan, inicializa registros, crea estructura | `53d235f` |
| `prompt-session <N>` | Compila prompt adaptado con contexto de sesión | `53d235f` |
| `process-session <N> <r>` | Procesa respuesta LLM, escribe Blade, acumula CSS/JS | `53d235f` |
| `zip` | Empaqueta proyecto en `outputs.zip` | `53d235f` |

### 4. Sistema de Testing (ITERACIÓN 002 - 2026-08-21)

Se implementó la iteración Speckit completa `002-sistema-testing-pra` (spec → plan → tasks → implementación):

**Suite de pruebas: 30 pruebas aprobadas, cobertura 88% (mínimo requerido: 85%)**

| Categoría | Archivo | Pruebas |
|-----------|---------|---------|
| Unitarias | `tests/unit/test_normalize_plan.py`, `test_validators.py`, `test_parsers.py`, `test_registries.py` | 12 |
| Integración CLI | `tests/integration/test_cli_init.py`, `test_cli_save_plan.py`, `test_cli_session.py`, `test_cli_zip.py` | 13 |
| Constitucionales | `tests/constitutional/test_constitution_rules.py` | 5 |

**Defectos reales detectados y corregidos en `pra_helper.py`:**
1. **D001**: Regex del manifest en `parse_llm_response()` no capturaba `data-title`.
2. **D002**: `cmd_process_session` NO validaba secuencialidad de sesiones (violación silenciosa de la Constitución IV). Se replicó la validación existente en `cmd_prompt_session`.
3. **D003**: `normalize_plan()` descartaba `clases_css_requeridas`/`comportamientos_js_requeridos` (registros quedaban vacíos) y `cmd_process_session` agregaba entradas duplicadas; ahora preserva los campos y usa `merge_registry()`.

---

## Estructura de Archivos del Proyecto

```
C:\laragon\www\test\test\test_opencode\
├── research_prompts_templates/        # Junction a plantillas maestras
│   ├── presentation_plan_meta_prompt.md
│   └── presentation_slide_meta_prompt.md
├── AGENTS.md                          # Directrices para agentes IA
├── pra_helper.py                      # Motor de automatización (718+ líneas)
├── pytest.ini                         # Configuración de la suite pytest
├── tests/                             # Suite automatizada (iteración 002)
│   ├── conftest.py                    # Fixtures: aislamiento tmp_path, run_cli, mocks LLM
│   ├── unit/                          # 12 pruebas unitarias
│   ├── integration/                   # 13 pruebas de integración CLI
│   └── constitutional/                # 5 pruebas constitucionales
├── specs/
│   ├── 001-sistema-automatizacion-presentations-pra/
│   │   ├── spec.md                    # Especificación funcional
│   │   ├── plan.md                    # Contexto técnico
│   │   ├── research.md                # Research de tecnologías
│   │   ├── data-model.md              # Modelo de datos y esquemas JSON
│   │   ├── quickstart.md              # Guía de validación E2E
│   │   ├── tasks.md                   # 19 tareas en 7 fases
│   │   ├── contracts/
│   │   │   └── cli-contract.md        # Especificación CLI de pra_helper.py
│   │   └── checklists/
│   │       └── requirements.md        # Checklist de requerimientos
│   └── 002-sistema-testing-pra/       # Especificación del sistema de testing
│       ├── spec.md / plan.md / research.md / quickstart.md / tasks.md
│       └── contracts/test-runner-contract.md
└── .specify/
    └── memory/
        └── constitution.md            # Constitución del proyecto
```

---

## Constitución del Proyecto (5 Principios No Negociables)

1. **Cero CSS Inline:** Prohibido `style="..."` dentro de `<x-slide>`
2. **JavaScript acotado por lámina:** Todo script debe encapsularse
3. **Preservación determinista del estado:** Solo `pra_helper.py` escribe archivos
4. **Construcción progresiva secuencial:** Sesión N requiere sesión N-1 completa
5. **Toda documentación técnica en español**

---

## Cómo Usar pra_helper.py

### Flujo completo paso a paso:

```bash
# 1. Inicializar proyecto con documento fuente
python pra_helper.py init documento_fuente.md > prompt_plan.txt

# (Enviar prompt_plan.txt al LLM para generar el JSON del plan)

# 2. Guardar plan maestro
python pra_helper.py save-plan '{"titulo":"...","carpeta_snake_case":"...","idioma":"es",...}'

# 3. Para cada sesión N (empezando por 1):
#    a. Compilar prompt de la sesión
python pra_helper.py prompt-session 1 > prompt_sesion1.txt

#    (Enviar prompt al LLM, recibir respuesta completa)

#    b. Procesar respuesta del LLM
python pra_helper.py process-session 1 "respuesta_completa_del_llm..."

# 4. Repetir paso 3 para cada sesión

# 5. Empaquetar proyecto final
python pra_helper.py zip
```

### Ejemplo de uso real:

```bash
# Crear documento fuente
echo "Contenido sobre automatización de presentaciones" > mi_documento.md

# Inicializar
python pra_helper.py init mi_documento.md > prompt.txt

# Guardar plan (ejemplo con JSON simplificado)
python pra_helper.py save-plan '{"titulo":"Mi Presentación","carpeta_snake_case":"mi_presentacion","idioma":"es","resumen_general":"Sistema para generar presentaciones","sesiones":[{"numero":1,"titulo":"Introducción","objetivo_pedagogico":"Comprender el sistema","laminas":[{"orden":1,"id_kebab_case":"portada","tipo":"portada","objetivo":"Presentar título"}]}]}'

# Generar prompt para sesión 1
python pra_helper.py prompt-session 1 > prompt_s1.txt

# Procesar respuesta del LLM
python pra_helper.py process-session 1 "respuesta_del_llm..."

# Empaquetar
python pra_helper.py zip
```

---

## Esquemas JSON Importantes

### PresentationPlan (guardado en `presentation_plan.json`)
```json
{
  "titulo": "string",
  "carpeta_snake_case": "string",
  "idioma": "es",
  "resumen_general": "string",
  "sesiones": [
    {
      "numero": 1,
      "titulo": "string",
      "objetivo_pedagogico": "string",
      "laminas": [
        {
          "orden": 1,
          "id_kebab_case": "string-kebab-case",
          "tipo": "portada|contenido|interactiva|cierre",
          "objetivo": "string",
          "insumos": []
        }
      ]
    }
  ]
}
```

### class_registry.json
```json
{
  "clases": [
    {
      "nombre": "clase-css",
      "descripcion": "Propósito de la clase",
      "implementada": true,
      "sesion_creacion": 1
    }
  ]
}
```

### js_registry.json
```json
{
  "comportamientos": [
    {
      "nombre": "comportamiento-js",
      "descripcion": "Propósito del comportamiento",
      "implementada": true,
      "sesion_creacion": 1
    }
  ]
}
```

---

## Discrepancia Conocida: Nombres de Campos

Las plantillas maestras en `research_prompts_templates/` usan:
- `nro` → data-model.md espera `numero`
- `folder_name` → data-model.md espera `carpeta_snake_case`
- `titulo_sesion` → data-model.md espera `titulo`
- `objetivos` → data-model.md espera `objetivo_pedagogico`
- `id` → data-model.md espera `id_kebab_case`

**Solución en pra_helper.py:** La función `normalize_plan()` convierte automáticamente los campos de un formato a otro.

---

## Formato de Respuesta LLM Esperado

El LLM debe generar 5 bloques delimitados:

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

## Comandos Útiles de Verificación

```bash
# Verificar entorno
python --version
python pra_helper.py --help

# EJECUTAR LA SUITE DE PRUEBAS (obligatorio tras cambios en pra_helper.py)
python -m pip install pytest pytest-cov   # solo la primera vez
pytest --cov=pra_helper --cov-report=term-missing
# Esperado: 30 passed, cobertura >= 85% (linea base: 88%), ~27s

# Verificar estructura creada por save-plan
ls -la [carpeta_proyecto]/
cat [carpeta_proyecto]/presentation_plan.json
cat [carpeta_proyecto]/class_registry.json
cat [carpeta_proyecto]/js_registry.json

# Verificar archivos generados por process-session
ls -la [carpeta_proyecto]/sesion[N]/
cat [carpeta_proyecto]/styles.blade.php
cat [carpeta_proyecto]/scripts.blade.php

# Verificar ZIP generado
ls -la outputs.zip
```

---

## Tareas Completadas (19/19)

| ID | Tarea | Estado |
|----|-------|--------|
| T001 | Verificar entorno Python | ✅ |
| T002 | Crear/verificar junction plantillas | ✅ |
| T003 | Leer/actualizar AGENTS.md y constitución | ✅ |
| T004 | Implementar punto entrada CLI | ✅ |
| T005 | Utilidades JSON y manejo UTF-8 | ✅ |
| T006 | Validación Cero CSS inline | ✅ |
| T007 | Comando `--init` | ✅ |
| T008 | Comando `--save-plan` | ✅ |
| T009 | Validación US1 | ✅ |
| T010 | Comando `--prompt-session` | ✅ |
| T011 | Comando `--process-session` | ✅ |
| T012 | Validación US2 (Cero CSS inline) | ✅ |
| T013 | Manejo de errores y validación E/S | ✅ |
| T014 | Integración --prompt-session con plantillas | ✅ |
| T015 | Parser regex de respuesta LLM | ✅ |
| T016 | Integración --process-session con registros | ✅ |
| T017 | Comando `--zip` | ✅ |
| T018 | Integración --init con presentacion_slide_meta_prompt | ✅ |
| T019 | Verificación end-to-end | ✅ |

---

## Cómo Continuar

1. **Para usar el sistema:** Seguir el flujo descrito arriba con un documento real
2. **Para modificar pra_helper.py:** Editar directamente el archivo y EJECUTAR la suite pytest antes de cerrar (ver `specs/002-sistema-testing-pra/quickstart.md`)
3. **Para agregar nuevas validaciones:** Agregar función en la sección "Validaciones" del script + pruebas correspondientes
4. **Para cambiar esquemas JSON:** Modificar `normalize_plan()` en pra_helper.py, actualizar `data-model.md` y ajustar las pruebas unitarias de `tests/unit/test_normalize_plan.py`

---

## Notas para el Próximo Modelo

- **NO tocar `pra_helper.py` sin entender el contrato CLI completo** (ver `contracts/cli-contract.md`)
- **El script es el ÚNICO punto de escritura** de archivos del proyecto generado
- **TODA modificación a `pra_helper.py` exige suite verde** (30 passed, cobertura >= 85%)
- **Las plantillas maestras están en** `research_prompts_templates/` (junction)
- **La constitución está en** `.specify/memory/constitution.md`
- **Los esquemas JSON están en** `specs/001-sistema-automatizacion-presentaciones-pra/data-model.md`
- **El contrato CLI está en** `specs/001-sistema-automatizacion-presentaciones-pra/contracts/cli-contract.md`
- **El contrato del ejecutor de pruebas está en** `specs/002-sistema-testing-pra/contracts/test-runner-contract.md`
- **Los tests usan fixtures aisladas (`tmp_path`) y nunca escriben en el workspace real**; `run_cli` en `conftest.py` invoca `main()` con argv simulado
