# Especificacion funcional: correcciones al motor PRA (iteracion 011)

**Rama funcional**: `011-mejoras-p5-p11-correcciones-planes`
**Estado**: En planificacion (pre-implementacion)
**Fecha**: 2026-09-02
**Origen**: `PROXIMA_ITERACION_MEJORAS.md`

## 1. Resumen

Esta iteracion aborda seis correcciones al motor `pra_helper.py` detectadas al levantar los modulos 5 y 6 del curso. Cada correccion (A1-A6) resuelve un bug o limitacion que provoca datos incorrectos, duplicados, perdida de informacion o friccion operativa en Windows. Las correcciones no rompen la interfaz CLI existente; se extienden sin alterar el contrato de retrocompatibilidad.

Las practicas operativas documentadas en el Grupo B del documento de origen se reflejan en `AGENTS.md` pero no forman parte del codigo del motor; se validan documentalmente.

## 2. Objetivos

1. Relajar la regex del BLOQUE 6 para tolerar lineas en blanco entre encabezado y fence (A1).
2. Deduplicar clases CSS y comportamientos JS por nombre al sembrar registros en `save-plan` (A2).
3. Auto-numerar el campo `orden` cuando falta en laminas del plan (A3).
4. Preservar el campo `data_title` en el plan normalizado y en el manifest final (A4).
5. Unificar el prefijo de carpetas de laminas finales a `session[N]` (ingles) de forma consistente (A5).
6. Anadir soporte `save-plan --plan-file <ruta>` para evitar corrupcion de acentos en Windows (A6).

## 3. Alcance

### Incluido

- Modificaciones a `pra_helper.py`: regex BLOQUE 6, deduplicacion de registros, auto-numerado de `orden`, preservacion de `data_title`, unificacion de prefijos, flag `--plan-file`.
- Pruebas TDD nuevas (unitarias, integracion, constitucionales) para cada correccion.
- Mantenimiento de la suite existente en verde con cobertura >= 85%.
- Documentacion actualizada en `AGENTS.md` y `SESION_PRA_RESUMEN.md`.

### Fuera de alcance

- Cambios en `pra_orchestrator.py` (excepto verificacion de compatibilidad).
- Cambios en plantillas de prompts.
- Nuevos comandos CLI fuera de `--plan-file`.
- Renombrar archivos internos `sesion[N]/` a `session[N]/` (se documenta la convencion; migracion diferida).

## 4. Historias de usuario

### HU-001: narracion con formato markdown limpio (A1)

Como creador de contenido, quiero que mi guion narrativo se detecte correctamente aunque el LLM ponga una linea en blanco despues del encabezado del BLOQUE 6, para que no tenga que reeditar manualmente la respuesta.

**Aceptacion**:
- La regex del BLOQUE 6 acepta una linea en blanco entre `**BLOQUE 6...**` y el fence.
- Sin linea en blanco, el comportamiento es identico al actual.
- Sin BLOQUE 6, se devuelve vacio sin excepcion.

### HU-002: registros sin duplicados (A2)

Como operador, quiero que si el plan declara la misma clase CSS en dos laminas, `class_registry.json` contenga una sola entrada, para que el registro refleje la realidad del proyecto.

**Aceptacion**:
- `clases_css_requeridas` duplicadas producen una sola entrada en `class_registry.json`.
- `comportamientos_js_requeridos` duplicados producen una sola entrada en `js_registry.json`.
- Se mantiene estable el orden de primera aparicion.

### HU-003: plan sin orden explicito (A3)

Como autor de planes, quiero que el sistema asigne numeracion automatica si no indico `orden` en las laminas, para que el flujo no falle por un campo opcional.

**Aceptacion**:
- Si ninguna lamina trae `orden`, se asigna 1..N en orden de aparicion.
- Si todas traen `orden`, se respeta el valor existente.
- Si falta parcialmente, las faltantes completan la secuencia sin colisionar.
- `PRA_PLAN_ESTRICTO=1` convierte la ausencia total de `orden` en error.

### HU-004: titulo real en el manifest (A4)

Como estudiante, quiero que la diapositiva muestre el titulo real definido en el plan y no un titulo generico, para que la presentacion sea mas clara.

**Aceptacion**:
- Si el plan declara `data_title`, el manifest usa ese valor.
- Si no lo declara, se mantiene el fallback actual (`titulo_legible(id)`).
- La informacion se conserva a traves de `normalize_plan` y consolidacion.

### HU-005: prefijo unificado de carpetas (A5)

Como operador, quiero que las vistas Blade del manifest resuelvan contra la carpeta real sin ambiguedad de prefijo, para que la integracion en Laravel funcione sin ajustes manuales.

**Aceptacion**:
- El lote protegido usa `session[N]/` (ingles) de forma consistente.
- Los artefactos internos/backup conservan `sesion[N]/` por compatibilidad.
- `limpiar` deja el lote protegido consistente con el prefijo ingles.

### HU-006: plan por archivo en Windows (A6)

Como operador en Windows, quiero pasar un archivo JSON al `save-plan` en lugar de pegar el JSON en la linea de comandos, para evitar corrupcion de acentos y errores de longitud.

**Aceptacion**:
- `save-plan --plan-file <ruta>` lee el JSON desde archivo UTF-8.
- El resultado es identico al flujo por argv.
- La firma actual `save-plan '<json>'` no se rompe.

## 5. Requisitos funcionales

### A1 — Regex BLOQUE 6 tolerante

- **RF-A1-001**: La regex del BLOQUE 6 debe aceptar cero o una linea en blanco (con o sin espacios/tabs) entre el encabezado `**BLOQUE 6...**` y el fence de apertura.
- **RF-A1-002**: La regex debe mantener el ancla de apertura y cierre existente.
- **RF-A1-003**: Si no hay BLOQUE 6, la extraccion debe devolver cadena vacia sin lanzar excepcion.
- **RF-A1-004**: Los bloques 1-5 no deben afectarse por el cambio (revision de robustez).

### A2 — Deduplicacion de registros

- **RF-A2-001**: `save-plan` debe deduplicar `clases_css_requeridas` por campo `nombre` antes de sembrar `class_registry.json`.
- **RF-A2-002**: `save-plan` debe deduplicar `comportamientos_js_requeridos` por campo `nombre` antes de sembrar `js_registry.json`.
- **RF-A2-003**: Se mantiene el orden de primera aparicion de cada entrada unica.

### A3 — Auto-numerado de `orden`

- **RF-A3-001**: `normalize_plan` debe detectar si alguna lamina carece de `orden` (valor `0` o ausente).
- **RF-A3-002**: Si todas las laminas traen `orden` distinto de 0, respetarlos.
- **RF-A3-003**: Si falta `orden` total o parcialmente, asignar secuencia 1..N por orden de aparicion, evitando colisiones con valores existentes.
- **RF-A3-004**: La falta total de `orden` debe elevarse como advertencia de calidad.
- **RF-A3-005**: Con `PRA_PLAN_ESTRICTO=1`, la ausencia total de `orden` debe producir error (exit 2).

### A4 — Preservacion de `data_title`

- **RF-A4-001**: `normalize_plan` debe conservar el campo `data_title` si existe en la lamina original.
- **RF-A4-002**: `cmd_save_plan` debe usar `data_title` en el `manifest_draft.blade.php`.
- **RF-A4-003**: `_consolidate_project` debe usar `data_title` en el `manifest.blade.php` final.
- **RF-A4-004**: Si `data_title` no existe, mantener el fallback actual (`titulo_legible(id)`).

### A5 — Unificacion de prefijo

- **RF-A5-001**: El lote protegido debe contener carpetas `session[N]/` (ingles).
- **RF-A5-002**: Los artefactos internos y backup pueden conservar `sesion[N]/` (espanol).
- **RF-A5-003**: `_lote_protegido_completo` debe buscar `session*` (ya lo hace).
- **RF-A5-004**: `_limpiar_proyecto` debe eliminar `sesion*/` internas y preservar `session*/`.
- **RF-A5-005**: `AGENTS.md` debe documentar la convencion de nombrado.

### A6 — `save-plan --plan-file`

- **RF-A6-001**: El subcomando `save-plan` debe aceptar `--plan-file <ruta>`.
- **RF-A6-002**: Si `--plan-file` se provee, el JSON se lee desde el archivo (UTF-8).
- **RF-A6-003**: Si el archivo no existe, retornar error `PLAN_FILE_NOT_FOUND` (exit 1).
- **RF-A6-004**: La firma actual `save-plan '<json>'` no se rompe; `--plan-file` es opcional.
- **RF-A6-005**: El resultado de normalizacion/guardado debe ser identico independientemente de la via de entrada.

## 6. Restricciones constitucionales

- Las correcciones no deben permitir CSS inline, escritura directa del orquestador ni archivos fuera del contrato.
- El orquestador no se modifica en esta iteracion (excepto verificacion de compatibilidad).
- Toda mutacion de artefactos sigue pasando exclusivamente por `pra_helper.py`.
- La suite de pruebas debe mantenerse en verde con cobertura >= 85%.

## 7. Criterios de éxito

- **CSE-001**: La regex del BLOQUE 6 parsea correctamente con y sin linea en blanco.
- **CSE-002**: `class_registry.json` y `js_registry.json` no contienen entradas duplicadas tras `save-plan`.
- **CSE-003**: Un plan sin `orden` produce laminas numeradas 1..N de forma determinista.
- **CSE-004**: `data_title` del plan aparece en el manifest final; sin el campo, usa fallback.
- **CSE-005**: Las vistas `session{N}.*` del manifest resuelven contra las carpetas reales.
- **CSE-006**: `save-plan --plan-file` produce resultado identico a `save-plan '<json>'`.
- **CSE-007**: La suite completa pasa sin regresiones y cobertura >= 85%.
- **CSE-008**: La interfaz CLI existente no se rompe (retrocompatibilidad total).
