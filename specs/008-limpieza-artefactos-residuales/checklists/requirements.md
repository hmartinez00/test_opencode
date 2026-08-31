# Checklist de Requerimientos: Limpieza de Artefactos Residuales con Proteccion del Lote

## Requisitos Funcionales

- [ ] **FR-801**: Tras la limpieza, el directorio del proyecto contiene unicamente el lote protegido y `backup/fuente/`.
- [ ] **FR-802**: La fuente interna se respalda en `backup/fuente/` de forma integra e idempotente.
- [ ] **FR-803**: El lote protegido (`manifest.blade.php`, `presentation_plan.json`, `class_registry.json`, `js_registry.json`, `session[N]/`, `assets/`) se conserva intacto.
- [ ] **FR-804**: La limpieza elimina `sesion[N]/`, `manifest_draft.blade.php`, `manifest_additions/`, `styles.blade.php`, `scripts.blade.php`, `styles_additions/`, `scripts_additions/` y `outputs.zip`.
- [ ] **FR-805**: La limpieza aborta (sin borrar) si falta algun archivo del lote protegido.
- [ ] **FR-806**: El orquestador omite la fase `zip`; su fase final es `cleanup`.
- [ ] **FR-807**: El orquestador ejecuta la limpieza de forma automatica y desatendida al final de la corrida.
- [ ] **FR-808**: `resume` soporta estados previos que contienen la fase `zip` (retrocompatibilidad).
- [ ] **FR-809**: `cmd_zip` queda como utilidad manual opcional, sin invocarse en el flujo automatico.
- [ ] **FR-810**: El respaldo es determinista (byte a byte) entre corridas.

## Criterios de Exito

- [ ] **SC-801**: Al terminar una corrida, el directorio del proyecto contiene solo el lote + `backup/fuente/`.
- [ ] **SC-802**: `backup/fuente/` contiene una copia integra de la fuente re-consolidable.
- [ ] **SC-803**: El manifest final referencia exactamente las laminas preservadas en `session[N]/`.
- [ ] **SC-804**: No se genera `outputs.zip` en el flujo automatico.
- [ ] **SC-805**: La puerta protectora evita borrados cuando falta el lote.
- [ ] **SC-806**: La suite completa permanece en verde y la cobertura de `pra_helper.py` y `pra_orchestrator.py` es >= 85%.

## Reglas Constitucionales (sin cambios)

- [ ] **Principio I**: `pra_helper.py` sigue siendo el unico punto de escritura de archivos del proyecto (la mutacion reside en el comando `limpiar`).
- [ ] **Principio II**: `pra_orchestrator.py` delega la limpieza en `run_helper("limpiar")`; no manipula el FS del proyecto directamente.
- [ ] **Principio III**: No se genera CSS inline ni se viola la separacion de estilos/scripts.
- [ ] **Principio IV**: No se rompe la suite; las pruebas nuevas se agregan antes de cerrar la tarea.
- [ ] **Principio V**: Se documenta la iteracion 008 en el repositorio.
