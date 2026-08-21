# Plan de Implementacion: Sistema de Automatizacion Progresiva de Presentaciones Reveal.js (PRA)

**Rama**: `001-sistema-automatizacion-presentaciones-pra` | **Fecha**: 2026-08-20 | **Especificacion**: [spec.md](./spec.md)

**Entrada**: Especificacion funcional de `/specs/001-sistema-automatizacion-presentaciones-pra/spec.md`

## Resumen

Sistema automatizado para la construccion modular y progresiva de presentaciones interactivas basadas en Reveal.js, empaquetadas en plantillas Blade compatibles con un framework especifico de Laravel. El enfoque centraliza la logica de creacion y mutacion de archivos en un script de Python determinista (`pra_helper.py`) que actua como punto unico de escritura, mientras que un LLM de OpenCode genera el contenido creativo de laminas, estilos y scripts bajo la guia de prompts maestros versionados.

## Contexto Tecnico

**Lenguaje/Version**: Python 3.11+
**Dependencias Principales**: Python stdlib (`json`, `argparse`, `re`, `os`, `pathlib`, `zipfile`), LLM de OpenCode (generacion de contenido)
**Almacenamiento**: Archivos JSON locales (`class_registry.json`, `js_registry.json`, `presentation_plan.json`), archivos Blade (`.blade.php`), Markdown
**Testing**: pytest (IMPLEMENTADO en la iteracion `002-sistema-testing-pra`: 30 pruebas, cobertura 88%. Ver `specs/002-sistema-testing-pra/` y `tests/`)
**Plataforma Objetivo**: Windows 10+ (Laragon, entorno de desarrollo local)
**Tipo de Proyecto**: CLI / Herramienta de automatizacion de codigo
**Objetivos de Rendimiento**: Procesamiento por sesion < 2 minutos en CLI interactiva
**Restricciones**: Cero CSS inline, JavaScript acotado por lamina, construccion secuencial por sesiones
**Alcance**: Maximo 10 sesiones por presentacion, maximo 15 laminas por sesion

## Verificacion Constitucional

*GATE: Debe pasar antes de la investigacion de Fase 0. Re-verificar despues del diseno de Fase 1.*

| Principio | Estado | Mecanismo de Cumplimiento |
|-----------|--------|---------------------------|
| I. Cero CSS Inline | CUMPLE | Validacion regex en `pra_helper.py --process-session` que rechaza `style="..."` en archivos Blade de laminas |
| II. JavaScript Acotado | CUMPLE | Plantilla de prompt obliga a encapsular scripts en `document.addEventListener('DOMContentLoaded', ...)` con comentario de lamina |
| III. Preservacion Determinista | CUMPLE | `pra_helper.py` es el unico punto de escritura; el LLM solo genera contenido que es delegado al script |
| IV. Construccion Progresiva | CUMPLE | Secuencia de comandos impuesta: `--init` -> `--save-plan` -> `--prompt-session N` -> `--process-session N` (secuencial) |
| V. Documentacion en Espanol | CUMPLE | Todos los artefactos de especificacion, planificacion y contratos redactados en espanol |

**Resultado Post-Diseno**: Sin violaciones pendientes. Todos los principios se cumplen sin necesidad de justificaciones de excepcion.

## Estructura del Proyecto (Codigo Fuente)

```text
C:\laragon\www\test\test\test_opencode\
├── research_prompts_templates/         # Junction a plantillas maestras de prompts
│   ├── presentation_plan_meta_prompt.md
│   ├── presentation_slide_meta_prompt.md
│   └── ...
├── pra_helper.py                       # Motor de automatizacion determinista
├── pra_workflow_state.md               # Registro de estado del proyecto
├── AGENTS.md                           # Guia de directrices para agentes
│
└── [nombre_proyecto_snake_case]/       # Directorio generado del proyecto activo
    ├── presentation_plan.json          # Plan maestro de la presentacion
    ├── class_registry.json             # Registro vivo de clases CSS
    ├── js_registry.json                # Registro vivo de comportamientos JS
    ├── manifest_draft.blade.php        # Estructura de integracion Blade
    ├── styles.blade.php                # Estilos globales acumulados
    ├── scripts.blade.php               # Scripts interactivos acumulados
    ├── styles_additions/               # Estilos aislados respaldados por sesion
    │   └── sesion[N]_styles.css
    ├── scripts_additions/              # Scripts aislados respaldados por sesion
    │   └── sesion[N]_scripts.js
    ├── manifest_additions/             # Fragmentos <x-slide> por sesion
    │   └── sesion[N].blade.php
    └── sesion[N]/                      # Laminas Blade de cada sesion
        ├── [slide-id-1].blade.php
        ├── [slide-id-2].blade.php
        └── ...
```

**Decision de Estructura**: Se adopta la estructura de proyecto unico con separacion por sesiones dentro del directorio del proyecto activo. Los registros JSON y archivos acumuladores (styles, scripts, manifest) se mantienen en la raiz del proyecto generado para facilitar la delegacion de escritura via `pra_helper.py`.

## Seguimiento de Complejidad

> No hay violaciones constitucionales que justificar. La arquitectura se diseña desde el cumplimiento de los 5 principios fundamentales.
