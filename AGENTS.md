# Guia Maestra para Agentes de IA: Presentation Automator (PRA)

Este archivo define las directrices contextuales, arquitectonicas y las reglas de diseno para todos los agentes de IA (incluyendo agentes de OpenCode y Speckit) que participen en el desarrollo y mantenimiento de este proyecto.

---

## 1. Objetivo del Proyecto
El sistema tiene como objetivo automatizar la generacion modular y progresiva de presentaciones interactivas basadas en **Reveal.js** empaquetadas en plantillas **Blade** compatibles con un framework especifico de Laravel.

La filosofia del proyecto es de **Plan Maestro + Construccion Progresiva por Sesiones**.

---

## 2. Arquitectura de Archivos y Directorios
Todo agente que trabaje en este entorno debe respetar y utilizar la siguiente estructura de archivos:

```text
C:\laragon\www\test_opencode\
├── research_prompts_templates/     <-- Enlace de union (junction) a las plantillas maestras de prompts
│   ├── presentation_plan_meta_prompt.md
│   ├── presentation_slide_meta_prompt.md
│   └── ...
├── AGENTS.md                       <-- Guia maestra para agentes de IA
├── README.md                       <-- Documentacion publica del repositorio
├── SESION_PRA_RESUMEN.md           <-- Documento de contexto de sesion (para reanudar en otra sesion)
├── pra_helper.py                   <-- Motor de automatizacion (punto unico de escritura de archivos)
├── pra_orchestrator.py             <-- Orquestador automatico del flujo completo (iteracion 003)
├── mocks_llm/                      <-- Respuestas LLM deterministas del backend mock del orquestador
│   ├── plan.txt
│   ├── sesion1.txt
│   └── sesion2.txt
├── pra_workflow_state.md           <-- Registro del estado y propuesta de arquitectura del proyecto
├── pytest.ini                      <-- Configuracion del marco de pruebas pytest
├── tests/                          <-- Suite de pruebas automatizadas (iteraciones 002 y 003)
│   ├── conftest.py                 <-- Fixtures compartidas (aislamiento tmp_path, mocks LLM)
│   ├── unit/                       <-- Pruebas unitarias del motor y del orquestador
│   ├── integration/                <-- Pruebas de integracion de comandos CLI
│   └── constitutional/             <-- Pruebas de reglas constitucionales
├── specs/
│   ├── 001-sistema-automatizacion-presentaciones-pra/
│   │   ├── spec.md                 <-- Especificacion funcional
│   │   ├── plan.md                 <-- Contexto tecnico y arquitectura de codigo
│   │   ├── research.md             <-- Research de tecnologias
│   │   ├── data-model.md           <-- Modelo de datos y esquemas JSON
│   │   ├── quickstart.md           <-- Guia de validacion end-to-end
│   │   ├── tasks.md                <-- Lista de tareas en 7 fases
│   │   ├── contracts/
│   │   │   └── cli-contract.md     <-- Especificacion detallada de comandos CLI
│   │   └── checklists/
│   │       └── requirements.md     <-- Checklist de requerimientos
│   └── 003-orquestador-automatizado-pra/
│       ├── spec.md                 <-- Especificacion del orquestador automatico
│       ├── research.md             <-- Decisiones tecnicas D1-D7
│       ├── data-model.md           <-- Estado de orquestacion y log de auditoria
│       ├── plan.md                 <-- Arquitectura interna del orquestador
│       ├── quickstart.md           <-- Escenarios E2E desatendidos
│       ├── tasks.md                <-- Tareas T301-T322 en 6 fases
│       ├── contracts/
│       │   └── orchestrator-contract.md  <-- CLI run/resume/status y codigos de salida
│       └── checklists/
│           └── requirements.md
├── .specify/
│   └── memory/
│       └── constitution.md         <-- Constitucion del proyecto (5 principios no negociables)
├── ejemplos/
│   └── introduccion_docker/
│       └── documento_fuente.md     <-- Documento fuente de prueba para validar el flujo completo
└── [Ruta configurada en PRA_OUTPUT_DIR] <-- Subdirectorio maestro de proyectos generados (iteracion 005;
    |                                    default: C:\laragon\www\product_samples\slides)
    ├── [nombre_proyecto_snake_case]/   <-- Directorio generado del proyecto activo
        ├── outputs.zip                 <-- Entregable empaquetado (generado por `pra_helper.py zip`)
        ├── presentation_plan.json      <-- Plan maestro normalizado
        ├── class_registry.json         <-- Registro vivo de clases CSS implementadas
        ├── js_registry.json            <-- Registro vivo de comportamientos JavaScript implementados
        ├── manifest_draft.blade.php    <-- Estructura de integracion Laravel inicial
        ├── styles.blade.php            <-- Estilos globales acumulados del proyecto
        ├── scripts.blade.php           <-- Scripts interactivos acumulados del proyecto
        ├── styles_additions/           <-- Estilos aislados respaldados por sesion
        ├── scripts_additions/          <-- Scripts aislados respaldados por sesion
        ├── manifest_additions/         <-- Fragmentos de <x-slide> generados por sesion
        └── sesion[N]/                  <-- Subcarpetas que contienen los archivos .blade.php de cada lamina
            └── [slide-id-kebab-case].blade.php
        ├── manifest.blade.php          <-- Manifest final consolidado
        ├── global/                     <-- Vistas compartidas consolidadas
        ├── session[N]/                 <-- Vistas finales por sesion
        └── assets/                     <-- Entry points y fragmentos CSS/JS finales
```

---

## 3. Mandatos y Restricciones Estrictas para los Agentes

Para asegurar la consistencia visual y la integracion en Laravel, todos los agentes de IA deben cumplir rigurosamente con las siguientes reglas:

### Restricciones de CSS/Estilos:
* **PROHIBIDO el CSS inline:** No se permiten atributos `style="..."` dentro de las etiquetas HTML de las laminas.
* **Uso del Registry:** Cualquier clase CSS de utilidad o diseno nueva debe ser registrada en `class_registry.json`.
* **Centralizacion:** Los estilos se inyectan en `styles.blade.php` bajo nombres de clase unicos y descriptivos.

### Restricciones de JavaScript:
* **Scope por lamina:** Todo script interactivo debe estar acotado de forma segura y comentarizada al elemento de la lamina correspondiente para evitar colisiones entre diapositivas en Reveal.js.
* **Uso del Registry:** Los comportamientos interactivos nuevos deben documentarse en `js_registry.json`.

### Preservacion del Estado (Fuente de Verdad):
* **No escribir directamente en registries ni combinar archivos Blade manualmente:** Los agentes deben invocar siempre el script `pra_helper.py` con los argumentos apropiados para delegar la creacion y actualizacion del proyecto. Esto asegura que la logica regex y de fusion de JSONs sea 100% precisa y determinista.
* **Respetar el orden secuencial:** No se puede construir la Sesion $N$ si la Sesion $N-1$ no ha sido completada y sus cambios integrados con exito.
* **Subdirectorio maestro (iteracion 005):** Todo proyecto generado se aloja bajo `C:\laragon\www\product_samples\slides` (overridable via variable de entorno `PRA_OUTPUT_DIR`); el entregable `outputs.zip` tambien se genera dentro de cada subdirectorio de proyecto. La raiz del repositorio debe permanecer limpia. Detalles: `specs/005-directorio-maestro-rutas-y-zip/`.

### Garantia de Calidad (Suite de Pruebas):
* **Prohibido romper la suite:** Cualquier modificacion a `pra_helper.py` o `pra_orchestrator.py` DEBE mantener la suite `pytest` en verde (102 pruebas aprobadas en la verificacion final del repositorio) antes de dar por terminada la tarea. Ejecutar: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing` (invocar siempre via `python -m pytest` y nunca el ejecutable `pytest.exe`, que dispara falsos positivos del antivirus).
* **Cobertura minima:** El porcentaje de cobertura de `pra_helper.py` y de `pra_orchestrator.py` no debe descender del 85%. La verificacion final actual reporta 88% y 87% respectivamente.
* **Nuevas funcionalidades requieren nuevas pruebas:** Todo cambio o feature en el motor o el orquestador debe incluir pruebas unitarias, de integracion o constitucionales segun corresponda, siguiendo la especificacion de `specs/002-sistema-testing-pra/`.

---

## 4. Flujo de Trabajo del Agente

Cuando el usuario solicite acciones sobre el flujo PRA, el agente que intervenga debe actuar bajo las siguientes fases:

### Fase de Inicializacion (`@pra iniciar`):
1. Leer el documento fuente proporcionado por el usuario.
2. Invocar `python pra_helper.py init <documento>` para armar el prompt de generacion del Plan Maestro.
3. Solicitar la generacion al LLM interno y procesar la salida (el JSON de plan y registros iniciales) con `python pra_helper.py save-plan '<json>'`.

### Fase de Construccion de Sesion (`@pra construir sesion <N>`):
1. Consultar `class_registry.json` y `js_registry.json` vigentes.
2. Ejecutar `python pra_helper.py prompt-session <N>` para compilar el prompt adaptado.
3. Enviar el prompt compilado al LLM de OpenCode.
4. Tomar la respuesta completa del LLM y pasarla a `python pra_helper.py process-session <N> '<respuesta_llm>'`.
5. Confirmar al usuario los archivos Blade creados y los nuevos estilos/scripts agregados.

### Fase de Consolidacion (`python pra_helper.py consolidate`):
1. Leer el plan y los artefactos internos de todas las sesiones completadas.
2. Generar `manifest.blade.php`, `global/`, `session[N]/` y `assets/` sin duplicados ni CSS inline.
3. Validar referencias Blade y entry points antes de permitir el empaquetado.

### Fase de Cierre (`@pra empaquetar`):
1. Invocar `python pra_helper.py zip` para comprimir el proyecto y dejarlo listo para su descarga e integracion en Laravel.

### Fase de Orquestacion Desatendida (`@pra automatizar`, iteracion 003):
Alternativa a las fases manuales anteriores: `pra_orchestrator.py` ejecuta el flujo completo (init -> save-plan -> sesiones -> consolidate -> pytest -> zip) delegando TODA mutacion de artefactos en los comandos CLI de `pra_helper.py` via subprocess.
1. Corrida desatendida: `python pra_orchestrator.py run <documento> [--backend mock|opencode] [--max-retries N]`.
2. Reanudacion e inspeccion: `python pra_orchestrator.py resume` / `python pra_orchestrator.py status`.
3. El orquestador aplica puertas constitucionales por sesion (exit code, regex anti CSS inline, laminas completas) y un bucle de reintentos con prompt de reflexion de error; exige suite verde + cobertura >= 85% antes de empaquetar.
4. Sus unicos artefactos de escritura propios son `orchestration_state.json` y `orchestration_log.txt` (excluidos del zip). Contrato completo: `specs/003-orquestador-automatizado-pra/contracts/orchestrator-contract.md`.

### Fase de Verificacion (obligatoria tras cualquier cambio en el motor):
1. Ejecutar la suite completa: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
2. Verificar que las 105 pruebas pasen y que la cobertura de `pra_helper.py` y `pra_orchestrator.py` sea >= 85%.
3. Si se agregaron funcionalidades nuevas, incorporar las pruebas correspondientes antes de cerrar la tarea.

---

## 5. Plantillas de Prompts

Las plantillas maestras de prompts se encuentran en la carpeta `research_prompts_templates/` (enlace de union a `C:\laragon\www\researchs\workflow\research_prompts_templates`). Los archivos criticos para el flujo son:

* `presentation_plan_meta_prompt.md`: Genera el plan maestro con estructura JSON, clases CSS iniciales y comportamientos JS.
* `presentation_slide_meta_prompt.md`: Genera laminas Blade, estilos, scripts y actualizaciones de registros para sesiones individuales.

### Nota sobre Normalizacion de Campos JSON
El script `pra_helper.py` normaliza automaticamente los campos del plan maestro al guardar. Esto significa que puede recibir plan JSON con los nombres de campo de las plantillas maestras (`nro`, `folder_name`, `titulo_sesion`, `objetivos`, `id`) o con los nombres del data-model (`numero`, `carpeta_snake_case`, `titulo`, `objetivo_pedagogico`, `id_kebab_case`). En ambos casos el resultado sera el mismo.

---

## 6. Notas para Speckit

* Speckit puede operar en este entorno como agente de validacion y ejecucion de tareas.
* El script `pra_helper.py` debe ser el unico punto de escritura de archivos del proyecto generado.
* Cualquier cambio estructural en los registros o plantillas debe validarse antes de proceder a la siguiente sesion.
* Las especificaciones completas del sistema se encuentran en `specs/001-sistema-automatizacion-presentaciones-pra/`.
* La especificacion del sistema de testing y su guia de ejecucion se encuentran en `specs/002-sistema-testing-pra/`.
* La especificacion del orquestador automatico y su contrato CLI se encuentran en `specs/003-orquestador-automatizado-pra/`.
* La especificacion del subdirectorio maestro de proyectos generados se encuentra en `specs/004-subdirectorio-maestro-proyectos-pra/`.

---

## 7. Documentos de Referencia Rapida

* `README.md`: Documentacion publica del repositorio con guia de uso y esquemas JSON.
* `SESION_PRA_RESUMEN.md`: Documento de contexto completo para reanudar cualquier sesion de desarrollo.
* `ejemplos/introduccion_docker/documento_fuente.md`: Documento fuente de prueba para validar el flujo completo.
* `specs/002-sistema-testing-pra/quickstart.md`: Guia rapida para ejecutar la suite de pruebas automatizadas.
