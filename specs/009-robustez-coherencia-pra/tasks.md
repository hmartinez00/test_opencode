# Lista de Tareas: Robustez y Coherencia del Flujo PRA

**Fecha**: 2026-08-31

## Fase 0: Preparacion TDD (red)

- [ ] **T901** Escribir pruebas rojas de `_analizar_coherencia` que detectan laminas huerfanas (FR-902).
- [ ] **T902** Escribir pruebas rojas de deteccion de laminas faltantes (FR-903).
- [ ] **T903** Escribir pruebas rojas de deteccion de laminas duplicadas (FR-904).
- [ ] **T904** Escribir prueba roja de `consolidate` que aborta (`ok: false`) ante incoherencia y no genera manifest incompleto (FR-906/907).
- [ ] **T905** Escribir prueba roja de `_validar_calidad_plan` que advierte de registros vacios (FR-909).
- [ ] **T906** Escribir prueba roja de advertencia por lamina sin insumos (FR-910).
- [ ] **T907** Escribir prueba roja del umbral `PRA_PLAN_ESTRICTO` (advertencia -> error) (FR-911).
- [ ] **T908** Escribir prueba roja de `_resolver_binario_opencode` que resuelve via rutas conocidas (FR-912).
- [ ] **T909** Escribir prueba roja del diagnostico `BACKEND_NO_DISPONIBLE` (FR-913).
- [ ] **T910** Escribir prueba roja de deteccion de ambiguedad del proyecto activo (FR-914/915).

## Fase 1: Oracle de coherencia en consolidacion (`pra_helper.py`)

- [ ] **T911** Implementar `_analizar_coherencia(plan, project_dir)` (D1, D3).
- [ ] **T912** Integrar el oracle en `_consolidate_project`: abortar con `ok: false` ante huerfanas/faltantes/duplicadas (D2).
- [ ] **T913** Asegurar la no-regresion: flujos coherentes (mocks) siguen consolidando igual (D7).
- [ ] **T914** Ajustar la salida JSON de `consolidate` con el bloque `coherencia`.

## Fase 2: Validacion de calidad del plan (`pra_helper.py`)

- [ ] **T915** Implementar `_validar_calidad_plan(plan)` que retorna advertencias (D4).
- [ ] **T916** Integrar en `cmd_save_plan`: emitir advertencias en stderr y en el JSON (`advertencias`).
- [ ] **T917** Implementar el umbral `PRA_PLAN_ESTRICTO=1` que eleva advertencias bloqueantes a error (aborta el guardado).

## Fase 3: Backend `opencode` robusto (`pra_orchestrator.py`)

- [ ] **T918** Implementar `_resolver_binario_opencode()` con PATH + rutas conocidas (D5).
- [ ] **T919** Usar la resolucion en `OpenCodeBackend`; si es `None`, no lanzar FileNotFoundError.
- [ ] **T920** Implementar el diagnostico `BACKEND_NO_DISPONIBLE` con rutas intentadas y PATH relevante (D8).

## Fase 4: Seleccion explicita de proyecto activo (`pra_helper.py`)

- [ ] **T921** Filtrar directorios no-proyecto al enumerar candidatos (`backup`, `themes`, etc.).
- [ ] **T922** Detectar ambiguedad (varios candidatos sin `PRA_ACTIVE_PROJECT`) y emitir advertencia listando candidatos (D6).

## Fase 5: Pruebas (verde y refactor)

- [ ] **T923** Ejecutar las pruebas de la Fase 0 y confirmar que pasan tras la implementacion (verde).
- [ ] **T924** Revisar/ajustar fixtures de `conftest.py` para que plan y laminas sean coherentes por defecto.
- [ ] **T925** Agregar pruebas de integracion CLI: `consolidate` con lamina huerfana; `save-plan` con registros vacios.
- [ ] **T926** Agregar pruebas constitucionales: nunca un manifest incompleto ante incoherencia.
- [ ] **T927** Refactorizar y eliminar deuda sin romper la suite.

## Fase 6: Documentacion y validacion final

- [ ] **T928** Actualizar `README.md`, `AGENTS.md` y `SESION_PRA_RESUMEN.md`.
- [ ] **T929** Actualizar contratos CLI de las especificaciones 001 y 003 (bloque `coherencia`, `advertencias`, diagnostico backend, ambiguedad).
- [ ] **T930** Ejecutar `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
- [ ] **T931** Ejecutar una corrida mock E2E y validar que consolida sin incoherencias y que `--backend opencode` resuelve o diagnostica.
- [ ] **T932** Confirmar cobertura minima de 85% en ambos modulos y cero regresiones.
