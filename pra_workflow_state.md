# Estado del Proyecto: Presentation Automator (PRA) en OpenCode

Este documento sirve como registro de estado y diseño de arquitectura para la adaptación del flujo de trabajo de automatización de presentaciones interactivas Reveal.js (PRA v1.0) para ser ejecutado localmente utilizando OpenCode.

---

## 📋 Resumen del Cuaderno Original (Presentation_automator_PRA_v1.0.ipynb)

El cuaderno original automatiza el flujo de trabajo para construir presentaciones interactivas basadas en Reveal.js integradas en un módulo de Laravel/Blade. El proceso se basa en un enfoque de **Plan Maestro + Construcción Progresiva por Secciones** para mantener coherencia visual y funcional sin duplicar estilos ni scripts.

### Flujo de Trabajo Original (Jupyter Notebook / Google Colab)
1. **Clonación de Plantillas (Paso 0)**: Se clonan los prompts estructurados de investigación/presentaciones desde el repositorio de GitHub en la carpeta `templates/`.
2. **Generación de Metaprompt de Plan (Paso 1)**: Utiliza `presentation_plan_meta_prompt.md` inyectando el contenido fuente para generar un prompt maestro.
3. **Gestión de Plan (Paso 2)**: El usuario introduce la respuesta de la IA (que contiene tres JSONs: el plan, el registro inicial de clases y el registro de comportamientos JS) y la guarda como `presentation_plan.md`.
4. **Procesador del Plan (Paso 3)**: Un script de Python extrae los bloques JSON de `presentation_plan.md`, inicializa la estructura de carpetas por sesión (`sesion1/`, `sesion2/`, etc.), inicializa los archivos de registros vivos (`class_registry.json`, `js_registry.json`), y genera un borrador del archivo de integración `manifest_draft.blade.php`.
5. **Construcción Asistida por Sesión (Paso 4)**:
   - **4.1 Generador de Prompt de Sesión**: Genera prompts de construcción dinámica inyectando los objetivos, láminas planificadas y el estado actual de los registros de clases y comportamientos para que el LLM no duplique código preexistente.
   - **4.2 Procesador Directo**: Recibe la respuesta del LLM para una sesión, escribe los archivos `.blade.php` correspondientes de cada lámina, anexa de manera incremental los bloques de CSS (`styles.blade.php`) y JS (`scripts.blade.php`), y actualiza los registros JSON agregando las nuevas clases/comportamientos.
6. **Compresión y Descarga (Paso 5)**: Empaqueta todo el directorio de salida en un archivo `.zip` para ser descargado e integrado en el framework Laravel.

---

## 🏗️ Propuesta de Arquitectura Simplificada para OpenCode ("PRA-OpenCode Hybrid")

Para trasladar este flujo de trabajo interactivo a OpenCode y ejecutarlo localmente de forma automatizada y sin depender de APIs de pago externas, se plantea la siguiente infraestructura de dos componentes:

### 1. El Script de Soporte (`pra_helper.py`)
Un script en Python que encapsula toda la lógica de backend del flujo original para asegurar que la manipulación de archivos sea robusta, predecible y libre de errores de sintaxis de la IA.

Funcionalidades de `pra_helper.py`:
* `--init`: Lee el contenido fuente y genera el prompt del plan usando la plantilla de `research_prompts_templates/presentation_plan_meta_prompt.md`.
* `--save-plan`: Procesa el markdown generado para extraer e inicializar el plan y los registries JSON en el directorio de salida.
* `--prompt-session <n>`: Genera el prompt para una sesión específica cruzando la información de las láminas del plan con el estado vivo de `class_registry.json` and `js_registry.json`.
* `--process-session <n>`: Parsea la respuesta del LLM para escribir los archivos Blade de láminas, añadir CSS/JS, generar las adiciones del manifest, y actualizar los registries vivos sin duplicar elementos.
* `--zip`: Comprime el estado final del proyecto en un archivo `.zip`.

### 2. El Agente Personalizado de OpenCode (`.opencode/agent/pra.md`)
Un agente especializado dentro del entorno de OpenCode que interactúa con el usuario, lee los documentos de entrada, ejecuta las invocaciones necesarias de `pra_helper.py`, realiza las llamadas de LLM integradas en OpenCode usando los prompts generados por el script, y coordina todo el proceso de punta a punta.

#### Interfaz de comandos propuestos:
* `@pra iniciar "ruta/documento_fuente"`: Inicia el flujo del plan maestro.
* `@pra construir sesion <n>`: Genera e implementa de manera interactiva las láminas de la sesión `<n>`.
* `@pra empaquetar`: Empaqueta todo el proyecto final para su descarga o importación directa en Laravel.
