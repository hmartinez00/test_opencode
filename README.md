# Presentation Automator (PRA) v1.0

Sistema de automatización para la generación modular y progresiva de presentaciones interactivas basadas en **Reveal.js**, empaquetadas en plantillas **Blade** para integración en frameworks Laravel.

## Filosofía

El sistema opera bajo el principio de **Plan Maestro + Construcción Progresiva por Sesiones**:

1. **Plan Maestro**: Se analiza un documento fuente y se genera un plan estructurado en JSON que define la presentación completa.
2. **Construcción por Sesiones**: Cada sesión se construye de forma secuencial, generando laminas Blade individuales con sus estilos y scripts asociados.
3. **Empaquetado**: Las sesiones completadas se comprimen en un archivo ZIP listo para integración en Laravel.
4. **Consolidacion**: Antes del empaquetado, los artefactos internos se convierten en una estructura final con `manifest.blade.php`, `global/`, `sessionN/` y `assets/`.

## Estructura del Proyecto

```
test_opencode/
├── research_prompts_templates/     # Plantillas maestras de prompts (junction)
│   ├── presentation_plan_meta_prompt.md
│   └── presentation_slide_meta_prompt.md
├── AGENTS.md                       # Directrices para agentes de IA
├── pra_helper.py                   # Motor de automatización (CLI, único escritor de artefactos)
├── pra_orchestrator.py             # Orquestador automático del flujo completo (CLI)
├── mocks_llm/                      # Respuestas LLM deterministas para el backend mock
│   ├── plan.txt
│   ├── sesion1.txt
│   └── sesion2.txt
├── pytest.ini                      # Configuración del marco de pruebas
├── tests/                          # Suite de pruebas automatizadas (pytest)
│   ├── conftest.py                 # Fixtures compartidas (aislamiento, mocks LLM)
│   ├── unit/                       # Pruebas unitarias del motor
│   ├── integration/                # Pruebas de integración CLI
│   └── constitutional/             # Pruebas de reglas constitucionales
├── SESION_PRA_RESUMEN.md           # Documento de contexto de sesión
├── specs/                          # Especificaciones y documentación
│   ├── 001-sistema-automatizacion-presentaciones-pra/
│   │   ├── spec.md                 # Especificación funcional
│   │   ├── plan.md                 # Contexto técnico
│   │   ├── research.md             # Research de tecnologías
│   │   ├── data-model.md           # Modelo de datos y esquemas JSON
│   │   ├── quickstart.md           # Guía de validación E2E
│   │   ├── tasks.md                # 19 tareas en 7 fases
│   │   ├── contracts/
│   │   │   └── cli-contract.md     # Especificación CLI de pra_helper.py
│   │   └── checklists/
│   │       └── requirements.md     # Checklist de requerimientos
│   └── 002-sistema-testing-pra/
│       ├── spec.md                 # Especificación del sistema de testing
│       ├── plan.md                 # Plan técnico del marco de pruebas
│       ├── research.md             # Decisiones de testing
│       ├── quickstart.md           # Guía de ejecución de la suite
│       ├── tasks.md                # 14 tareas en 5 fases + defectos corregidos
│       └── contracts/
│           └── test-runner-contract.md  # Contrato del ejecutor de pruebas
├── specs/003-orquestador-automatizado-pra/   # (dentro de specs/)
│   ├── spec.md                     # Especificación del orquestador automático
│   ├── research.md                 # Decisiones técnicas D1-D7
│   ├── data-model.md               # Estado de orquestación y reportes
│   ├── plan.md                     # Arquitectura de pra_orchestrator.py
│   ├── quickstart.md               # Escenarios E2E del orquestador
│   ├── tasks.md                    # T301-T322 en 6 fases
│   ├── contracts/
│   │   └── orchestrator-contract.md  # CLI run/resume/status y códigos de salida
│   └── checklists/
│       └── requirements.md
├── specs/004-subdirectorio-maestro-proyectos-pra/   # (dentro de specs/)
│   ├── spec.md                     # Subdirectorio maestro output_projects/
│   ├── research.md                 # Decisiones técnicas D401-D408
│   ├── data-model.md               # Cambio de ubicación de artefactos
│   ├── plan.md                     # Puntos exactos de cambio en motor/orquestador
│   ├── quickstart.md               # Escenarios de validación de la nueva ruta
│   ├── tasks.md                    # T401-T413 en 4 fases
│   ├── contracts/
│   │   └── cli-contract-v2-deltas.md # Deltas de contrato CLI (rutas)
│   └── checklists/
│       └── requirements.md
├── specs/005-directorio-maestro-rutas-y-zip/       # (dentro de specs/)
│   ├── spec.md                     # Ruta maestra por defecto, prompt interactivo y zip autocontenido
│   ├── research.md                 # Decisiones técnicas D-501 a D-505
│   ├── data-model.md               # Modelo de rutas y salida del entregable
│   ├── plan.md                     # Puntos exactos de cambio en motor/orquestador/tests
│   ├── quickstart.md               # Escenarios interactivos y no interactivos
│   ├── tasks.md                    # T501-T521 en 5 fases
│   ├── contracts/
│   │   └── cli-contract-v3-deltas.md # Deltas de contrato CLI (rutas, stdin y zip)
│   └── checklists/
│       └── requirements.md
├── specs/006-consolidacion-estructura-presentaciones/ # Consolidacion de salida Laravel
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── contracts/consolidation-contract.md
├── [Ruta configurada en PRA_OUTPUT_DIR]/   # Subdirectorio maestro (default: C:\laragon\www\product_samples\slides)
│   └── <carpeta_snake_case>/       # Proyectos generados por el flujo PRA
│       └── outputs.zip             # Entregable empaquetado (pra_helper.py zip)
└── .specify/
    └── memory/
        └── constitution.md         # Constitución del proyecto
```

## Constitución del Proyecto

Cinco principios fundamentales que rigen el desarrollo:

1. **Cero CSS Inline**: Prohibido el uso de atributos `style="..."` dentro de las laminas Blade
2. **JavaScript Acotado**: Todo script debe estar encapsulado y acotado por lamina
3. **Preservación Determinista del Estado**: Solo `pra_helper.py` tiene permisos de escritura sobre archivos del proyecto generado
4. **Construcción Progresiva Secuencial**: La Sesión N no puede iniciarse hasta completar la Sesión N-1
5. **Documentación en Español**: Toda documentación técnica debe redactarse en español

## Instalación

### Prerrequisitos

- Python 3.10 o superior
- Git
- Acceso a un modelo LLM (GPT-4, Claude, etc.)

### Configuración

```bash
# Clonar el repositorio
git clone https://github.com/hmartinez00/test_opencode.git
cd test_opencode

# Verificar entorno
python --version
python pra_helper.py --help

# Instalar dependencias de desarrollo (testing)
python -m pip install pytest pytest-cov
```

## Testing y Calidad

El proyecto cuenta con una suite de pruebas automatizadas basada en **pytest**. El estado verificado actual es:

- 102 pruebas aprobadas
- Cobertura final: 88% en `pra_helper.py` y 87% en `pra_orchestrator.py`
- Verificación ejecutada en 2026-08-24 con la línea base actual del repositorio

```bash
# Suite completa (invocar siempre via python -m pytest; el ejecutable pytest.exe
# dispara falsos positivos en algunos antivirus)
python -m pytest

# Suite con reporte de cobertura
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing

# Por categorías
python -m pytest tests/unit/            # Pruebas unitarias del motor y del orquestador
python -m pytest tests/integration/     # Pruebas de integración CLI
python -m pytest tests/constitutional/  # Pruebas de reglas constitucionales
```

Las pruebas se ejecutan en directorios temporales aislados (`tmp_path`) y no modifican el workspace. Ver `specs/002-sistema-testing-pra/quickstart.md` para la guía completa.

**Regla obligatoria**: Toda modificación a `pra_helper.py` o `pra_orchestrator.py` debe mantener la suite en verde antes de considerarse completada. La verificación final del proyecto quedó exitosa con 102 pruebas aprobadas y cobertura ≥ 85%.

**Corrección documentada**: el bug del zip se resolvió normalizando la ruta interna del archivo a string y excluyendo el propio `outputs.zip` durante la compresión, sin afectar el flujo del orquestador ni la estructura del proyecto.

## Orquestador Automático

`pra_orchestrator.py` ejecuta el flujo PRA completo de forma desatendida, delegando toda mutación de artefactos en `pra_helper.py`:

```bash
# Corrida desatendida con backend mock determinista
python pra_orchestrator.py run documento_fuente.md --backend mock

# Con backend real (CLI de OpenCode) y reintentos configurables
python pra_orchestrator.py run documento_fuente.md --backend opencode --max-retries 3

# Reanudar una corrida interrumpida / inspeccionar estado
python pra_orchestrator.py resume
python pra_orchestrator.py status
```

Características clave:
- **Bucle de autocorrección**: ante respuestas LLM defectuosas (CSS inline, JSON malformado), reintenta hasta `--max-retries` veces anexando un diagnóstico al prompt.
- **Puertas constitucionales**: valida exit code, ausencia de CSS inline y completitud de láminas tras cada sesión; exige suite verde y cobertura ≥ 85% antes de empaquetar.
- **Estado reanudable**: persistencia atómica en `orchestration_state.json`; auditoría en `orchestration_log.txt`. Ambos quedan fuera de `outputs.zip`.
- **Subdirectorio maestro**: todo proyecto generado se aloja en `C:\laragon\www\product_samples\slides` (configurable via variable de entorno `PRA_OUTPUT_DIR`); la raíz del repositorio permanece limpia.
- **Consolidacion final**: genera `manifest.blade.php`, vistas bajo `global/` y `sessionN/`, y entrypoints de assets bajo `assets/` antes de empaquetar.
- **Códigos de salida**: `0` éxito | `1` validación incumplida | `2` estado/secuencialidad | `3` backend no disponible | `4` uso incorrecto.

## Uso

### Flujo Completo

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

# 5. Consolidar estructura final Laravel
python pra_helper.py consolidate

# 6. Empaquetar proyecto final
python pra_helper.py zip
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `init <doc>` | Lee documento fuente y genera prompt del Plan Maestro |
| `save-plan <json>` | Guarda plan maestro, inicializa registros y crea estructura |
| `prompt-session <N>` | Compila prompt adaptado para la generación de laminas de la sesión N |
| `process-session <N> <r>` | Procesa respuesta del LLM y escribe archivos Blade |
| `consolidate` | Consolida manifest, vistas y assets en la estructura final Laravel |
| `zip` | Empaqueta el proyecto en `<directorio_proyecto>/outputs.zip` |

> **Nota (iteración 005)**: los proyectos generados se crean bajo el subdirectorio maestro `C:\laragon\www\product_samples\slides`. La variable de entorno `PRA_OUTPUT_DIR` permite usar otra ruta; si la ruta configurada no existe, el sistema solicita interactivamente una ruta existente (en entornos no interactivos aborta con código 1). La búsqueda del proyecto activo prioriza ese subdirectorio y aplica un fallback sobre la raíz para proyectos legacy anteriores a esta iteración.

### Ejemplo Práctico

```bash
# Crear documento fuente
echo "Contenido sobre automatización de presentaciones" > mi_documento.md

# Inicializar
python pra_helper.py init mi_documento.md > prompt.txt

# Guardar plan (ejemplo con JSON simplificado)
python pra_helper.py save-plan '{
  "titulo": "Mi Presentación",
  "carpeta_snake_case": "mi_presentacion",
  "idioma": "es",
  "resumen_general": "Sistema para generar presentaciones",
  "sesiones": [{
    "numero": 1,
    "titulo": "Introducción",
    "objetivo_pedagogico": "Comprender el sistema",
    "laminas": [{
      "orden": 1,
      "id_kebab_case": "portada",
      "tipo": "portada",
      "objetivo": "Presentar título"
    }]
  }]
}'

# Generar prompt para sesión 1
python pra_helper.py prompt-session 1 > prompt_s1.txt

# Procesar respuesta del LLM
python pra_helper.py process-session 1 "respuesta_del_llm..."

# Empaquetar
python pra_helper.py zip
```

## Formato de Respuesta del LLM

El LLM debe generar una respuesta con 5 bloques delimitados:

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

## Esquemas JSON

### PresentationPlan

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

## Documentación

- **AGENTS.md**: Directrices contextuales para agentes de IA
- **SESION_PRA_RESUMEN.md**: Documento de contexto completo de la sesión de desarrollo
- **specs/001-sistema-automatizacion-presentaciones-pra/**: Especificación del motor PRA
- **specs/002-sistema-testing-pra/**: Especificación del sistema de testing y calidad
- **specs/003-orquestador-automatizado-pra/**: Especificación del orquestador automático

## Licencia

Proyecto privado - Uso interno.
