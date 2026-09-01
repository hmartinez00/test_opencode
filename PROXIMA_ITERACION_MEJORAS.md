# Proxima Iteracion: Mejoras Detectadas al Levantar Modulos 5 y 6

## 1. Objetivo

Abordar en una iteracion dedicada los problemas encontrados al levantar las presentaciones `modulo5_archivos_excepciones` y `modulo6_oop` con el flujo PRA (init → save-plan → prompt-session → process-session → consolidate → limpiar). El documento separa las acciones en:

- **Grupo A: Correcciones al motor** (`pra_helper.py`) — requieren pruebas pytest nuevas y mantener la suite en verde con cobertura >= 85%.
- **Grupo B: Practicas operativas** — deben quedar documentadas en `AGENTS.md` (y este archivo como referencia) para no repetir los errores.

Regla transversal: no escribir directamente en los registries ni combinar Blade a mano; todo cambio de motor se valida con `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q`.

---

## 2. Grupo A: Correcciones al Motor (`pra_helper.py`)

Cada correccion incluye: problema, causa raiz, accion concreta y prueba requerida.

### A1 (P5) — Regex del BLOQUE 6 tolerante a linea en blanco

- **Problema**: el guion narrativo no se detectaba cuando habia una linea en blanco entre `**BLOQUE 6 — ...**` y el fence ```text.
- **Causa raiz**: la regex exige `\n` inmediatamente despues del encabezado y antes del fence; la convencion de Markdown de separar bloques con linea en blanco rompe el parser.
- **Accion**: relajar la regex para aceptar `\n` y opcionalmente `[ \t]*\n` (linea en blanco) antes del fence, manteniendo el ancla de apertura. Revisar tambien los bloques 1-5 por si la misma convencion afecta a otros separadores.
- **Pruebas**: en `tests/unit/`, refactorizar/agregar casos de la funcion de extraccion del guion: (a) con linea en blanco antes del fence (debe parsear), (b) sin linea en blanco (comportamiento actual, debe seguir parseando), (c) sin bloque 6 (debe devolver vacio sin excepcion).

### A2 (P6) — Deduplicacion de clases en `save-plan`

- **Problema**: repetir una misma clase en `clases_css_requeridas` de varias laminas generaba entradas duplicadas en `class_registry.json`.
- **Causa raiz**: `save-plan` siembra los registros sin deduplicar por `nombre` al consolidar las laminas del plan.
- **Accion**: deduplicar por `nombre` (primera ocurrencia gana) en las listas `clases_css_requeridas` y `comportamientos_js_requeridos` antes de sembrar los JSON. Mantener estable el orden de primera aparicion.
- **Pruebas**: en `tests/unit/`, un plan donde la misma clase aparece en 2 laminas debe producir un registro con 1 sola entrada; igual para comportamientos.
- **Opcional**: emitir advertencia en `prompt-session` cuando el plan contenga duplicados (para visibilidad del autor del plan).

### A3 (P7) — Auto-numerado de `orden` faltante

- **Problema**: laminas sin campo `orden` quedaban todas en 0.
- **Causa raiz**: `normalize_plan` no asigna numeracion por defecto; el orden dependia de un campo opcional.
- **Accion**: al normalizar, si alguna lamina carece de `orden`, asignar 1..N en el orden en que aparecen en el plan. Si todas lo traen, respetarlo. Elevar la falta de `orden` a advertencia de calidad del plan (y a error si `PRA_PLAN_ESTRICTO=1` esta activo).
- **Pruebas**: (a) plan sin `orden` → laminas numeradas 1..N; (b) plan con `orden` parcialmente presente → las faltantes completan la secuencia sin colisionar; (c) estricto sobre plan sin orden → falla con el codigo de error correspondiente.

### A4 (P8) — Preservar `data_title` en manifest/draft

- **Problema**: `normalize_plan` descarta `data_title`, y el manifest final usa el fallback `titulo_legible(id)` (p.ej. «S1 Portada») en vez del titulo real de la lamina.
- **Causa raiz**: el campo `data_title` del plan no se propaga al `manifest_draft`/`manifest.blade.php`.
- **Accion**: conservar `data_title` (o su equivalente normalizado) en el JSON del plan y en las entradas `<x-slide data-title="...">`. Si una lamina no trae `data_title`, mantener el fallback actual.
- **Pruebas**: en `tests/integration/` (o unit/consolidate), un plan con `data_title` definido debe reflejarlo en el manifest final (`manifest.blade.php`); sin el campo, usa fallback.

### A5 (P10) — Unificar prefijo `session1` vs `sesion1`

- **Problema**: la carpeta de laminas finales es `session1/` (ingles) pero los artefactos internos y el backup usan `sesion1/` (español); validar el manifest con el prefijo "incorrecto" da falsos negativos.
- **Causa raiz**: idioma distinto entre el lote protegido (`session[N]/`) y los artefactos internos (`sesion[N]/`).
- **Accion**: decidir y unificar el naming. Propuesta: conservar `session[N]/` en el lote final (contrato existente del manifest `view="session1.*"`) y documentarlo explicitamente en `AGENTS.md`; los artefactos internos/backup pueden conservar `sesion[N]/` por compatibilidad con data-model. Alternativa a evaluar: renombrar internos a `session[N]/` con migracion en `limpiar` si no rompe pruebas.
- **Pruebas**: consolidar un proyecto y validar que las vistas del manifest (prefijo `session{N}.`) resuelven contra la carpeta final; `limpiar` debe dejar el lote protegido consistente.

### A6 (P3-bonus) — `save-plan --plan-file <ruta>`

- **Problema**: pasar el JSON del plan por argv en Windows corrompe acentos / tropieza con el limite de linea de comando.
- **Causa raiz**: argumento CLI unico con JSON multilinea y no-ASCII.
- **Accion**: anadir subcomando/flag `save-plan --plan-file <ruta>` que lea el JSON desde archivo (UTF-8) y delegue al mismo pipeline de normalizacion/guardado. No romper la firma actual `save-plan '<json>'`.
- **Pruebas**: en `tests/integration/`, guardar un plan (con acentos) leido desde archivo y verificar campos normalizados identicos al flujo por argv; validar el mismo JSON por ambas vias.

---

## 3. Grupo B: Practicas Operativas (documentar en AGENTS.md)

Instrucciones de flujo para no repetir errores. No tocan codigo del helper; van a la seccion de flujo de trabajo del agente.

### B1 (P1) — `PRA_ACTIVE_PROJECT` obligatorio

- `prompt-session`, `process-session`, `consolidate` y `limpiar` deben ejecutarse con `PRA_ACTIVE_PROJECT=<carpeta_snake_case>` fijado. Sin la variable, la busqueda automatica puede tomar el primer proyecto alfabetico (le paso un `intro_docker` en `prompt-session`).
- Documentar en `AGENTS.md` seccion 4 (configuracion previa): "si hay mas de un proyecto en el directorio maestro, fijar SIEMPRE `PRA_ACTIVE_PROJECT` antes de `prompt-session`/`process-session`/`consolidate`/`limpiar`."

### B2 (P2) — `PRA_OUTPUT_DIR` explicito antes de `save-plan`

- Verificar que la ruta base existe y fijar `PRA_OUTPUT_DIR` de forma explicita antes del primer `save-plan` para evitar que el proyecto quede en una ruta temporal/incorrecta.
- Regla: "definir `PRA_OUTPUT_DIR` (y verificar su existencia) antes de `init`/`save-plan` cuando la ruta no sea la predeterminada."

### B3 (P3) — JSON del plan por archivo, sin acentos

- Escribir el plan en un `.json` temporal SIN acentos y pasarlo con `$(cat "archivo.json")` (Git Bash) en lugar de pegar el JSON en el argv.
- Cuando exista `save-plan --plan-file` (A6), usarlo en lugar del `$(cat ...)`.

### B4 (P4) — Respuestas de sesion por `--respuesta-file`

- Respuestas >= ~30.000 caracteres superan el limite de argv en Windows (`WinError 206`). Escribir la respuesta a un `.md` UTF-8 (acentos OK) y usar `process-session N --respuesta-file <ruta>`.

### B5 (P9) — Limpiar acumuladores antes de reprocesar

- `styles.blade.php` y `scripts.blade.php` acumulan contenido de todas las sesiones procesadas. Antes de REPROCESAR una sesion, borrar ambos acumuladores (o el proyecto entero) para evitar CSS/JS duplicados en el manifest consolidado.
- Alternativa a evaluar en motor: `process-session` resetea los acumuladores al inicio (cabria como A7 si se aprueba).

### B6 (P11) — Localizar el `.ipynb` real

- Si el usuario indica una ruta fuente sin extension (p.ej. `modulo6_oop`), localizar el archivo real (`modulo6_oop.ipynb`) antes de `init`; el helper debe recibir la ruta final del archivo.

---

## 4. Definicion de Hecho (DoD)

- [ ] Grupo A implementado en `pra_helper.py` sin romper la interfaz CLI existente.
- [ ] Pruebas nuevas presentes en `tests/` (unitarias/integracion segun especie) y la suite en verde: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q`.
- [ ] Cobertura de `pra_helper.py` y `pra_orchestrator.py` >= 85%.
- [ ] Grupo B reflejado en `AGENTS.md` (seccion 4, flujo de trabajo) y resumido en `SESION_PRA_RESUMEN.md`.
- [ ] Re-validacion end-to-end minima: construir una presentacion de 1 sesion con el flujo manual y verificar manifest/registries/audio.