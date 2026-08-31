# Especificacion de Funcionalidad: Limpieza de Artefactos Residuales con Proteccion del Lote (008-limpieza-artefactos-residuales)

**Rama de Funcionalidad**: `008-limpieza-artefactos-residuales`

**Fecha de Creacion**: 2026-08-31

**Estado**: Borrador

**Entrada**: Una corrida completa de PRA (manual u orquestador) deja en el directorio del proyecto tanto los entregables finales (lote protegido) como artefactos internos de construccion (`sesion[N]/`, `manifest_draft.blade.php`, acumuladores, adiciones por sesion, `outputs.zip`). Esto duplicaba contenido (p.ej. `sesion1/` y `session1/` con las mismas laminas) y contaminaba el "source de verdad" que el usuario integra directamente en Laravel. Esta iteracion introduce una limpieza automatizada que elimina los artefactos residuales preservando el lote protegido y respaldando la fuente para re-consolidar.

---

## Objetivo

Garantizar que al terminar una corrida PRA, el directorio del proyecto contenga **unicamente** los archivos/directorios necesarios para levantar la presentacion en Laravel (el lote protegido) mas un respaldo de la fuente interna en `backup/fuente/`, eliminando todos los artefactos residuales (incluido `outputs.zip`).

Flujo objetivo (ahora omitiendo la fase `zip`):

```text
init -> save-plan -> sesiones -> consolidate -> pytest -> cleanup
```

## Lote protegido (whitelist) - se conserva

| Entregable | Rol en Laravel |
|---|---|
| `manifest.blade.php` | Manifest final consolidado |
| `presentation_plan.json` | Plan maestro normalizado |
| `class_registry.json` | Registro vivo de clases CSS |
| `js_registry.json` | Registro vivo de comportamientos JS |
| `session[N]/` | Vistas finales por sesion (referenciadas por `view="sessionN...."` en el manifest) |
| `assets/` | Entry points (`styles.blade.php`, `scripts.blade.php`) y fragmentos finales CSS/JS |

**Nota critica**: se preserva `session[N]/` (mayuscula) que es el que el manifest final referencia, NO `sesion[N]/` (minuscula) que es la fuente interna de construccion.

## Artefactos residuales - se eliminan del directorio

| Artefacto | Origen | Destino |
|---|---|---|
| `sesion[N]/` | Fuente de laminas | `backup/fuente/sesion[N]/` |
| `manifest_draft.blade.php` | Borrador inicial del manifest | `backup/fuente/` |
| `manifest_additions/` | Fragmentos `<x-slide>` por sesion | `backup/fuente/` |
| `styles.blade.php` | Acumulador global de estilos | eliminado |
| `scripts.blade.php` | Acumulador global de scripts | eliminado |
| `styles_additions/` | Estilos aislados por sesion | `backup/fuente/` |
| `scripts_additions/` | Scripts aislados por sesion | `backup/fuente/` |
| `outputs.zip` | Entregable empaquetado (decidido residual) | eliminado |

## Historias de Usuario y Pruebas

### Historia de Usuario 1 - Limpieza tras corrida (Prioridad: P1)

Como integrador Laravel, necesito que al terminar una corrida PRA el directorio del proyecto contenga solo el lote protegido, para poder copiar/linkear esos archivos directamente sin limpiar manualmente.

**Prueba Independiente**: Ejecutar una corrida completa (manual u orquestador), aplicar la limpieza y verificar que el directorio del proyecto contiene exactamente el lote protegido + `backup/fuente/`, sin `sesion[N]/`, sin `manifest_draft`, sin acumuladores, sin adiciones y sin `outputs.zip`.

**Escenarios de Aceptacion**:

1. `manifest.blade.php`, `presentation_plan.json`, `class_registry.json` y `js_registry.json` permanecen.
2. `session[N]/` y `assets/` permanecen intactos con su contenido.
3. `sesion[N]/`, `manifest_draft.blade.php`, `manifest_additions/`, `styles.blade.php`, `scripts.blade.php`, `styles_additions/`, `scripts_additions/` y `outputs.zip` NO existen.

### Historia de Usuario 2 - Respaldo de la fuente (Prioridad: P1)

Como desarrollador PRA, necesito que la fuente interna (`sesion[N]/`, adiciones, borrador) quede respaldada para poder re-consolidar sin perdida.

**Prueba Independiente**: Tras la limpieza, verificar que `backup/fuente/` contiene una copia integra de `sesion[N]/`, `styles_additions/`, `scripts_additions/`, `manifest_additions/` y `manifest_draft.blade.php`.

**Escenarios de Aceptacion**:

1. `backup/fuente/sesion[N]/` contiene las mismas laminas que tenia la fuente pre-limpieza.
2. Las adiciones CSS/JS y el manifest borrador se respaldan.
3. El respaldo es idempotente: una segunda limpieza no lo duplica ni lo corrompe.

### Historia de Usuario 3 - Omision de la fase zip (Prioridad: P2)

Como usuario del flujo automatico, necesito que la corrida NO genere `outputs.zip`, ya que integro la presentacion directamente desde el directorio del proyecto.

**Prueba Independiente**: Ejecutar `pra_orchestrator.py run <doc> --backend mock` y verificar que la corrida termina en estado OK **sin** generar `outputs.zip` y sin una fase `zip` en el estado.

**Escenarios de Aceptacion**:

1. La corrida completa exitosamente.
2. `outputs.zip` no existe en el directorio del proyecto.
3. El estado final no contiene fase `zip`; en su lugar contiene fase `cleanup` completada.
4. `resume` sobre un estado previo que aun contenía fase `zip` (retrocompatibilidad) no corrompe la corrida.

### Historia de Usuario 4 - Puerta protectora del lote (Prioridad: P1)

Como usuario, necesito que la limpieza NO borre nada si el lote protegido esta incompleto o el estado es invalido.

**Prueba Independiente**: Intentar limpiar un proyecto donde falta un archivo del lote (p.ej. `manifest.blade.php`) y verificar que la limpieza aborta sin eliminar ningun archivo.

**Escenarios de Aceptacion**:

1. Si falta algun archivo del lote, la limpieza aborta con error claro y exit code distinto de 0.
2. Ningun archivo es eliminado tras el aborto.
3. El respaldo no se corrompe en un intento fallido.

## Requisitos Funcionales

- **FR-801**: Tras la limpieza, el directorio del proyecto contiene unicamente el lote protegido y `backup/fuente/`.
- **FR-802**: La fuente interna se respalda en `backup/fuente/` de forma integra e idempotente.
- **FR-803**: El lote protegido (`manifest.blade.php`, `presentation_plan.json`, `class_registry.json`, `js_registry.json`, `session[N]/`, `assets/`) se conserva intacto.
- **FR-804**: La limpieza elimina `sesion[N]/`, `manifest_draft.blade.php`, `manifest_additions/`, `styles.blade.php`, `scripts.blade.php`, `styles_additions/`, `scripts_additions/` y `outputs.zip`.
- **FR-805**: La limpieza aborta (sin borrar) si falta algun archivo del lote protegido.
- **FR-806**: El orquestador omite la fase `zip`; su fase final es `cleanup`.
- **FR-807**: El orquestador ejecuta la limpieza de forma automatica y desatendida al final de la corrida.
- **FR-808**: `resume` soporta estados previos que contienen la fase `zip` (retrocompatibilidad).
- **FR-809**: `cmd_zip` queda como utilidad manual opcional, sin invocarse en el flujo automatico.
- **FR-810**: El respaldo es determinista (byte a byte) entre corridas para no romper la comparacion de determinismo mock.

## Criterios de Exito

- **SC-801**: Al terminar una corrida, el directorio del proyecto contiene solo el lote + `backup/fuente/`.
- **SC-802**: `backup/fuente/` contiene una copia integra de la fuente re-consolidable.
- **SC-803**: El manifest final referencia exactamente las laminas preservadas en `session[N]/`.
- **SC-804**: No se genera `outputs.zip` en el flujo automatico.
- **SC-805**: La puerta protectora evita borrados cuando falta el lote.
- **SC-806**: La suite completa permanece en verde y la cobertura de `pra_helper.py` y `pra_orchestrator.py` es >= 85%.

## Casos Extremos

- Lote incompleto (falta `manifest.blade.php`, `class_registry.json`, etc.): la limpieza aborta sin borrar.
- `sesion[N]/` no existe al limpiar (sin laminas procesadas): no se respalda esa sesion y no se elimina nada erroneo; aborta si el lote esta incompleto.
- `backup/fuente/` ya existe: la limpieza lo sobrescribe de forma idempotente sin duplicar.
- `outputs.zip` inexistente al limpiar: se maneja como "ya eliminado" sin error.
- Estado previo de `resume` con fase `zip`: se mapea a `cleanup` completada sin re-ejecutar.
- Corrida con sesion faltante de laminas en el lote: la puerta aborta antes de borrar.
- Archivos de control del orquestador (`orchestration_state.json`, `orchestration_log.txt`) viven en la raiz del workspace, no dentro del proyecto; no se ven afectados.

## Fuera de Alcance

- Rediseñar laminas o estilos visuales.
- Migrar retroactivamente proyectos ya consolidados.
- Cambiar la arquitectura general de `pra_helper.py` u orquestador mas alla del nuevo comando `limpiar` y la omision de la fase `zip`.
- Reintroducir la fase `zip` o el empaquetado como entregable final del flujo automatico.
- Modificar la constitucion del proyecto.
