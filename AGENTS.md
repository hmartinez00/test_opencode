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
├── pra_orchestrator.py             <-- Orquestador automatico del flujo completo (iteraciones 003, 009 y 010)
├── mocks_llm/                      <-- Respuestas LLM deterministas del backend mock del orquestador
│   ├── plan.txt
│   ├── sesion1.txt
│   └── sesion2.txt
├── pra_workflow_state.md           <-- Registro del estado y propuesta de arquitectura del proyecto
├── pytest.ini                      <-- Configuracion del marco de pruebas pytest
├── tests/                          <-- Suite de pruebas automatizadas (iteraciones 002, 003, 009 y 010)
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
│   ├── 003-orquestador-automatizado-pra/
│   ├── 009-robustez-coherencia-pra/
│   └── 010-guion-narrativo-coherencia-audiovisual/
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
        ├── manifest.blade.php          <-- Manifest final consolidado (lote protegido)
        ├── presentation_plan.json      <-- Plan maestro normalizado (lote protegido)
        ├── class_registry.json         <-- Registro vivo de clases CSS (lote protegido)
        ├── js_registry.json            <-- Registro vivo de comportamientos JS (lote protegido)
        ├── session[N]/                 <-- Vistas finales por sesion (referenciadas por el manifest)
        ├── assets/                     <-- Entry points y fragmentos CSS/JS finales
        └── backup/
            └── fuente/                 <-- Fuente interna re-consolidable (iteracion 008)
                ├── sesion[N]/          <-- Laminas fuente originales
                ├── styles_additions/   <-- CSS aislado por sesion
                ├── scripts_additions/  <-- JS aislado por sesion
                ├── manifest_additions/ <-- Fragmentos de <x-slide> por sesion
                ├── manifest_draft.blade.php
                └── presentation_plan.json
```

> **Nota (iteracion 008)**: Durante la construccion interna el proyecto contiene artefactos residuales (`sesion[N]/`, `manifest_draft.blade.php`, `styles.blade.php`, `scripts.blade.php`, `styles_additions/`, `scripts_additions/`, `manifest_additions/`, `outputs.zip`). El comando `pra_helper.py limpiar` (o la fase `cleanup` del orquestador) los elimina al final, dejando solo el lote protegido + `backup/fuente/`.

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
* **Subdirectorio maestro (iteracion 005):** Todo proyecto generado se aloja bajo `C:\laragon\www\product_samples\slides` por defecto. La variable de entorno `PRA_OUTPUT_DIR` permite sobreescribir esta ruta base (NO es el nombre del proyecto; el nombre proviene de `carpeta_snake_case` en el plan JSON). El sistema crea el proyecto en `<PRA_OUTPUT_DIR>/<carpeta_snake_case>/`. Si la ruta configurada (o la predeterminada) no existe, el sistema solicita interactivamente una ruta valida (max. 3 intentos) o aborta con exit code 1 en entornos no interactivos. Sintaxis:
    * PowerShell: `$env:PRA_OUTPUT_DIR = "C:\ruta\base"`
    * Bash/Linux/Git Bash: `export PRA_OUTPUT_DIR="/ruta/base"`
    * El proyecto generado se aloja en el subdirectorio maestro. La raiz del repositorio debe permanecer limpia. Detalles: `specs/005-directorio-maestro-rutas-y-zip/`. Al terminar, el directorio del proyecto contiene solo el lote protegido + `backup/fuente/` (la fase `cleanup` del orquestador elimina `outputs.zip` y los demas residuales; ver iteracion 008).
* **Proyecto activo (iteracion 007):** La variable de entorno `PRA_ACTIVE_PROJECT` permite seleccionar explicita y deterministicamente el proyecto activo entre varios alojados en el directorio maestro. Debe contener el valor `carpeta_snake_case` del proyecto (ej. `modulo3_estructuras_datos`). Si la carpeta indicada no existe, se cae al comportamiento actual (busqueda automatica). Sintaxis:
    * PowerShell: `$env:PRA_ACTIVE_PROJECT = "nombre_proyecto"`
    * Bash/Linux/Git Bash: `export PRA_ACTIVE_PROJECT="nombre_proyecto"`

### Garantia de Calidad (Suite de Pruebas):
* **Prohibido romper la suite:** Cualquier modificacion a `pra_helper.py` o `pra_orchestrator.py` DEBE mantener la suite `pytest` en verde (151 pruebas verificadas el 2026-09-01) antes de dar por terminada la tarea. Ejecutar: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q` (invocar siempre via `python -m pytest` y nunca el ejecutable `pytest.exe`, que dispara falsos positivos del antivirus).
* **Cobertura minima:** El porcentaje de cobertura de `pra_helper.py` y de `pra_orchestrator.py` no debe descender del 85%. La verificacion actual reporta 89% y 85% respectivamente.
* **Nuevas funcionalidades requieren nuevas pruebas:** Todo cambio o feature en el motor o el orquestador debe incluir pruebas unitarias, de integracion o constitucionales segun corresponda, siguiendo la especificacion de `specs/002-sistema-testing-pra/`.

---

## 4. Flujo de Trabajo del Agente

Cuando el usuario solicite acciones sobre el flujo PRA, el agente que intervenga debe actuar bajo las siguientes fases:

### Configuracion del Directorio de Salida (previo a cualquier fase):

Antes de ejecutar cualquier comando del flujo PRA, el agente DEBE verificar y configurar el directorio donde se alojara el proyecto:

1. **Ruta por defecto**: `C:\laragon\www\product_samples\slides`. Si esta ruta existe, no se requiere accion adicional.
2. **Override manual**: Si el usuario indica una ubicacion diferente, configurar `PRA_OUTPUT_DIR` antes de ejecutar comandos:
   * PowerShell: `$env:PRA_OUTPUT_DIR = "C:\ruta\a\directorio"`
   * Bash/Linux/Git Bash: `export PRA_OUTPUT_DIR="/ruta/a/directorio"`
3. **Comportamiento si la ruta no existe**: El sistema solicitara interactivamente una ruta valida (max. 3 intentos) o abortara con exit code 1 en entornos no interactivos.
4. **Importante**: `PRA_OUTPUT_DIR` define la ruta **base** (contenedora); el nombre del proyecto proviene del campo `carpeta_snake_case` en el JSON del plan. El proyecto se creara en `<PRA_OUTPUT_DIR>/<carpeta_snake_case>/`.
5. **Proyecto activo (opcional)**: Si hay varios proyectos bajo la ruta base, se puede fijar el activo con `PRA_ACTIVE_PROJECT=<carpeta_snake_case>` (PowerShell: `$env:PRA_ACTIVE_PROJECT = "proyecto"`; Bash: `export PRA_ACTIVE_PROJECT="proyecto"`). Sin la variable, se usa la busqueda automatica (directorio actual si es proyecto, luego el primero alfabetico del base).

### Fase de Inicializacion (`@pra iniciar`):
1. Leer el documento fuente proporcionado por el usuario.
2. Invocar `python pra_helper.py init <documento>` para armar el prompt de generacion del Plan Maestro.
3. Solicitar la generacion al LLM interno y procesar la salida (el JSON de plan y registros iniciales) con `python pra_helper.py save-plan '<json>'`.

### Fase de Construccion de Sesion (`@pra construir sesion <N>`):
1. Consultar `class_registry.json` y `js_registry.json` vigentes.
2. Ejecutar `python pra_helper.py prompt-session <N>` para compilar el prompt adaptado.
3. Enviar el prompt compilado al LLM de OpenCode.
4. Tomar la respuesta completa del LLM y pasarla a `python pra_helper.py process-session <N> '<respuesta_llm>'`. Si la respuesta supera ~30000 caracteres (limite de argv en Windows / `WinError 206`), escribirla a un archivo y usar `python pra_helper.py process-session <N> --respuesta-file <ruta>` en su lugar.
5. Confirmar al usuario los archivos Blade creados y los nuevos estilos/scripts agregados.

### Fase de Consolidacion (`python pra_helper.py consolidate`):
1. Leer el plan y los artefactos internos de todas las sesiones completadas.
2. Generar `manifest.blade.php`, `global/`, `session[N]/` y `assets/` sin duplicados ni CSS inline.
3. Validar referencias Blade y entry points antes de permitir la consolidacion.

### Fase de Limpieza (`python pra_helper.py limpiar`, iteracion 008):
1. Respalda la fuente interna en `backup/fuente/` de forma idempotente y determinista.
2. Verifica la integridad del lote protegido; si falta alguno, aborta sin borrar nada.
3. Elimina los artefactos residuales (`sesion[N]/`, `manifest_draft.blade.php`, acumuladores, adiciones y `outputs.zip`), dejando el proyecto con solo el lote protegido + `backup/fuente/`.

### Fase de Empaquetado opcional (`pra_helper.py zip`):
1. `zip` queda como utilidad manual opcional; NO se invoca en el flujo automatico (la integracion se hace desde el directorio del proyecto).

### Fase de Orquestacion Desatendida (`@pra automatizar`, iteracion 003):
Alternativa a las fases manuales anteriores: `pra_orchestrator.py` ejecuta el flujo completo (init -> save-plan -> sesiones -> consolidate -> pytest -> cleanup) delegando TODA mutacion de artefactos en los comandos CLI de `pra_helper.py` via subprocess.
1. Corrida desatendida: `python pra_orchestrator.py run <documento> [--backend mock|opencode] [--max-retries N]`.
2. Reanudacion e inspeccion: `python pra_orchestrator.py resume` / `python pra_orchestrator.py status`.
3. El orquestador aplica puertas constitucionales por sesion (exit code, regex anti CSS inline, laminas completas) y un bucle de reintentos con prompt de reflexion de error; exige suite verde + cobertura >= 85% antes de entrar a la fase `cleanup`.
4. Sus unicos artefactos de escritura propios son `orchestration_state.json` y `orchestration_log.txt` (excluidos del directorio del proyecto). Contrato completo: `specs/003-orquestador-automatizado-pra/contracts/orchestrator-contract.md`.

### Reglas de coherencia y narracion (iteraciones 009 y 010):
1. La consolidacion bloquea laminas faltantes, huerfanas o duplicadas y reporta el bloque `coherencia`.
2. `PRA_PLAN_ESTRICTO=1` convierte advertencias de calidad del plan en error.
3. Las respuestas de sesion pueden incluir el **BLOQUE 6 — Guion de narracion**, con marcas `[slide: N]` basadas en cero.
4. El helper escribe cada guion en `assets/audio/guion_sesionN.txt` y lo conserva en `backup/fuente/assets/audio/`.
5. `PRA_AUDIO_ESTRICTO=1` exige el BLOQUE 6 y bloquea referencias invalidas, duplicadas, vacias o faltantes.
6. La validacion semantica del guion genera advertencias; no debe inventar narracion ni modificar silenciosamente las laminas.
7. El backend `opencode` y la fase interna de pytest tienen timeout defensivo. El backend manual/Copilot aun no esta implementado.

### Fase de Verificacion (obligatoria tras cualquier cambio en el motor):
1. Ejecutar la suite completa: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
2. Verificar que las 151 pruebas pasen y que la cobertura de `pra_helper.py` y `pra_orchestrator.py` sea >= 85%.
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
* La especificacion de la limpieza de artefactos residuales (fase `cleanup` y comando `limpiar`) se encuentra en `specs/008-limpieza-artefactos-residuales/`.
* La especificacion de robustez y coherencia se encuentra en `specs/009-robustez-coherencia-pra/`.
* La especificacion de guion narrativo y coherencia audiovisual se encuentra en `specs/010-guion-narrativo-coherencia-audiovisual/`.

---

## 7. Documentos de Referencia Rapida

* `README.md`: Documentacion publica del repositorio con guia de uso y esquemas JSON.
* `SESION_PRA_RESUMEN.md`: Documento de contexto completo para reanudar cualquier sesion de desarrollo.
* `ejemplos/introduccion_docker/documento_fuente.md`: Documento fuente de prueba para validar el flujo completo.
* `specs/002-sistema-testing-pra/quickstart.md`: Guia rapida para ejecutar la suite de pruebas automatizadas.
