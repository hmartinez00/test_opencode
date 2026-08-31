# Lista de Tareas: Calidad de Salida de Presentaciones PRA

**Fecha**: 2026-08-31

## Fase 0: Preparacion TDD (red)

- [ ] **T701** Escribir pruebas rojas para `titulo_legible()` (P6).
- [ ] **T702** Escribir pruebas rojas para interpolacion `{$presentation->folder_name}` en entry points (P1).
- [ ] **T703** Escribir pruebas rojas para envoltura `<style>`/`<script>` de fragmentos (P2, P3) y su idempotencia.
- [ ] **T704** Escribir pruebas rojas para `process-session --respuesta-file` (P4) con respuesta corta y larga (> 33000).
- [ ] **T705** Escribir pruebas rojas para `PRA_ACTIVE_PROJECT` con 2 proyectos (P5).
- [ ] **T706** Escribir pruebas rojas para `data-title` legible en el manifest (P6).

## Fase 1: Interpolacion de ruta (P1)

- [ ] **T707** Corregir la interpolacion en `assets/styles.blade.php` y `assets/scripts.blade.php`.
- [ ] **T708** Corregir la interpolacion en `manifest.blade.php` (include de styles y scripts).

## Fase 2: Envoltura de assets (P2, P3)

- [ ] **T709** Envolver fragmentos CSS finales con `<style>...</style>`.
- [ ] **T710** Envolver fragmentos JS finales con `<script>...</script>`.
- [ ] **T711** Garantizar idempotencia de la envoltura ante multiples `consolidate`.

## Fase 3: Respuesta por archivo (P4)

- [ ] **T712** Registrar `--respuesta-file` en el parser `process-session`.
- [ ] **T713** Implementar lectura de respuesta desde `--respuesta-file` en `cmd_process_session`.
- [ ] **T714** Aplicar precedencia documentada (archivo sobre posicional).
- [ ] **T715** Adaptar `pra_orchestrator.run_helper()` para usar archivo temporal en respuestas largas y limpiarlo en `finally`.

## Fase 4: Seleccion de proyecto activo (P5)

- [ ] **T716** Implementar `PRA_ACTIVE_PROJECT` en `find_project_dir()` de `pra_helper.py`.
- [ ] **T717** Replicar en `buscar_proyecto()` de `pra_orchestrator.py`.
- [ ] **T718** Verificar fallback seguro cuando la carpeta indicada no existe.

## Fase 5: Titulo legible (P6)

- [ ] **T719** Implementar la funcion `titulo_legible()`.
- [ ] **T720** Aplicar `data_title or titulo or titulo_legible(slide_id)` en `_consolidate_project`.

## Fase 6: Pruebas (verde y refactor)

- [ ] **T721** Ejecutar las pruebas de la Fase 0 y confirmar que pasan tras la implementacion (verde).
- [ ] **T722** Actualizar pruebas de integracion de `consolidate` para los nuevos asserts (interpolacion, envoltura, idempotencia, titulo).
- [ ] **T723** Agregar prueba de integracion E2E de `process-session --respuesta-file` largo.
- [ ] **T724** Agregar prueba de seleccion por `PRA_ACTIVE_PROJECT` en el orquestador.
- [ ] **T725** Refactorizar y eliminar deuda sin romper la suite.

## Fase 7: Documentacion y validacion final

- [ ] **T726** Actualizar `README.md`, `AGENTS.md` y `SESION_PRA_RESUMEN.md`.
- [ ] **T727** Actualizar contratos CLI de las especificaciones 001 y 003.
- [ ] **T728** Ejecutar `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
- [ ] **T729** Ejecutar una corrida mock E2E y validar `outputs.zip` renderizable.
- [ ] **T730** Confirmar cobertura minima de 85% en ambos modulos y cero regresiones.
