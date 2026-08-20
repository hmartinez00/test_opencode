# Contrato de Interfaz CLI: `pra_helper.py`

**Funcionalidad**: [Especificacion](../spec.md) | **Plan**: [Plan de Implementacion](../plan.md)

## Visión General

`pra_helper.py` es el punto unico de escritura de archivos del proyecto. Todos los agentes de IA y el usuario interactuan con el sistema exclusivamente a traves de los comandos CLI definidos en este contrato.

**Uso general**: `python pra_helper.py <comando> [argumentos]`

**Codificacion de salida**: Toda la salida de texto debe estar en UTF-8. Los archivos JSON generados deben usar indentacion de 2 espacios.

---

## Comandos

### 1. `--init`

**Proposito**: Inicializa la estructura de directorios del proyecto y genera el prompt de generacion del Plan Maestro.

**Sintaxis**: `python pra_helper.py --init <documento_fuente>`

**Argumentos**:
- `<documento_fuente>` (requerido): Ruta absoluta o relativa al documento fuente (PDF, .ipynb, .md, .txt, .docx, etc.)

**Comportamiento**:
1. Lee y extrae el contenido del documento fuente.
2. Crea la carpeta del proyecto en `carpeta_snake_case/` segun el contenido del documento.
3. Genera el prompt de generacion del Plan Maestro combinando el contenido del documento con la plantilla `presentation_plan_meta_prompt.md`.
4. Imprime el prompt generado en STDOUT para que el agente lo envie al LLM.

**Salida esperada (STDOUT)**: El prompt compilado en formato Markdown, listo para ser copiado y enviado al LLM.

**Archivos creados**:
- `carpeta_snake_case/` (directorio)

**Codigo de retorno**:
- `0`: Exito
- `1`: Error de lectura del documento fuente
- `2`: Error de creacion de directorio

---

### 2. `--save-plan`

**Proposito**: Guarda y valida el plan maestro generado por el LLM, inicializando los registros y estructura de sesiones.

**Sintaxis**: `python pra_helper.py --save-plan <json_plan>`

**Argumentos**:
- `<json_plan>` (requerido): Cadena JSON que contiene el plan maestro con la estructura definida en `data-model.md` (entidad `PresentationPlan`).

**Comportamiento**:
1. Parsea y valida el JSON recibido contra la estructura de `PresentationPlan`.
2. Escribe `presentation_plan.json` en la carpeta del proyecto.
3. Inicializa `class_registry.json` y `js_registry.json` con las entradas predefinidas del plan.
4. Crea las subcarpetas `sesion[N]/` por cada sesion definida.
5. Crea las carpetas `styles_additions/`, `scripts_additions/`, `manifest_additions/`.
6. Genera el borrador `manifest_draft.blade.php` con las entradas `<x-slide>` pendientes.

**Salida esperada (STDOUT)**: Resumen JSON con los archivos creados y el numero de sesiones inicializadas.

**Archivos creados/actualizados**:
- `presentation_plan.json`
- `class_registry.json`
- `js_registry.json`
- `manifest_draft.blade.php`
- `sesion[N]/` (directorios)
- `styles_additions/`, `scripts_additions/`, `manifest_additions/` (directorios)

**Codigo de retorno**:
- `0`: Exito
- `1`: Error de parseo JSON
- `2`: Error de validacion de esquema
- `3`: Error de escritura de archivos

---

### 3. `--prompt-session`

**Proposito**: Compila el prompt adaptado para la generacion de laminas de una sesion especifica, inyectando el contexto necesario (plan, registros, plantilla maestra).

**Sintaxis**: `python pra_helper.py --prompt-session <N>`

**Argumentos**:
- `<N>` (requerido): Numero de la sesion a compilar (entero positivo).

**Comportamiento**:
1. Verifica que la sesion N exista en `presentation_plan.json`.
2. Verifica que la sesion N-1 este en estado COMPLETADA (o que N=1).
3. Lee el estado actual de `class_registry.json` y `js_registry.json`.
4. Extrae las laminas de la sesion N del plan maestro.
5. Lee la plantilla `presentation_slide_meta_prompt.md`.
6. Compila el prompt inyectando: contexto de la sesion, laminas a generar, clases y comportamientos ya implementados, y la plantilla maestra.
7. Imprime el prompt compilado en STDOUT.

**Salida esperada (STDOUT)**: El prompt compilado en formato Markdown, listo para ser enviado al LLM.

**Codigo de retorno**:
- `0`: Exito
- `1`: Sesion no encontrada en el plan
- `2`: Sesion anterior no completada (violacion de construccion secuencial)
- `3`: Error de lectura de registros

---

### 4. `--process-session`

**Proposito**: Procesa la respuesta del LLM para una sesion, escribiendo los archivos Blade de laminas, acumulando estilos/scripts y actualizando los registros de forma determinista.

**Sintaxis**: `python pra_helper.py --process-session <N> <respuesta_llm>`

**Argumentos**:
- `<N>` (requerido): Numero de la sesion que se esta procesando (entero positivo).
- `<respuesta_llm>` (requerido): Cadena completa con la respuesta generada por el LLM, que contiene los bloques de laminas, estilos, scripts y actualizaciones de registros.

**Comportamiento**:
1. Parsea la respuesta del LLM identificando los bloques delimitados (laminas, estilos, scripts, actualizaciones de registros).
2. Para cada lamina:
   a. Genera el archivo `sesion[N]/[slide-id-kebab-case].blade.php`.
   b. Ejecuta validacion regex de Cero CSS inline (`style="..."`).
   c. Si detecta violacion, registra error y omite la lamina.
3. Acumula los estilos CSS nuevos en `styles.blade.php`.
4. Acumula los scripts JS nuevos en `scripts.blade.php`.
5. Escribe los archivos de respaldo aislados en `styles_additions/` y `scripts_additions/`.
6. Actualiza `class_registry.json` fusionando las nuevas entradas sin duplicar.
7. Actualiza `js_registry.json` fusionando las nuevas entradas sin duplicar.
8. Genera el archivo `manifest_additions/sesion[N].blade.php` con las entradas `<x-slide>` de la sesion.
9. Actualiza `manifest_draft.blade.php` marcando las laminas de la sesion como completadas.

**Salida esperada (STDOUT)**: Resumen JSON con archivos creados, clases registradas, scripts registrados y validaciones pasadas/fallidas.

**Archivos creados/actualizados**:
- `sesion[N]/[slide-id].blade.php` (cada lamina)
- `styles.blade.php` (acumulador)
- `scripts.blade.php` (acumulador)
- `styles_additions/sesion[N]_styles.css` (respaldo)
- `scripts_additions/sesion[N]_scripts.js` (respaldo)
- `class_registry.json` (fusionado)
- `js_registry.json` (fusionado)
- `manifest_additions/sesion[N].blade.php`
- `manifest_draft.blade.php` (actualizado)

**Codigo de retorno**:
- `0`: Exito (todas las laminas procesadas)
- `1`: Error de parseo de la respuesta LLM
- `2`: Violacion de Cero CSS inline detectada
- `3`: Error de fusion de registros
- `4`: Error de escritura de archivos

---

### 5. `--zip`

**Proposito**: Empaqueta todo el proyecto generado en un archivo `.zip` comprimido para descarga e integracion en Laravel.

**Sintaxis**: `python pra_helper.py --zip`

**Argumentos**: Ninguno.

**Comportamiento**:
1. Verifica que exista al menos una sesion completada en `presentation_plan.json`.
2. Recorre recursivamente toda la carpeta del proyecto generado.
3. Incluye en el ZIP: laminas Blade, registros JSON, estilos y scripts acumuladores, manifest, planes, estilos y scripts de respaldo.
4. Genera el archivo `outputs.zip` en la raiz del directorio de trabajo.

**Salida esperada (STDOUT)**: Ruta absoluta al archivo `outputs.zip` generado y tamano en bytes.

**Archivos creados**:
- `outputs.zip`

**Codigo de retorno**:
- `0`: Exito
- `1`: No hay sesiones completadas para empaquetar
- `2`: Error de creacion del archivo ZIP
