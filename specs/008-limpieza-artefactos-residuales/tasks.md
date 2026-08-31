# Lista de Tareas: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

## Fase 0: Preparacion TDD (red)

- [ ] **T801** Escribir pruebas rojas de `_limpiar_proyecto` que preservan el lote protegido (FR-801/803).
- [ ] **T802** Escribir pruebas rojas de respaldo de la fuente en `backup/fuente/` (FR-802).
- [ ] **T803** Escribir pruebas rojas de eliminacion de artefactos residuales (FR-804).
- [ ] **T804** Escribir prueba roja de puerta protectora que aborta sin borrar cuando falta el lote (FR-805).
- [ ] **T805** Escribir prueba roja de idempotencia y determinismo del respaldo (FR-810).
- [ ] **T806** Escribir prueba roja de omision de la fase `zip` en el orquestador (FR-806/807).
- [ ] **T807** Escribir prueba roja de retrocompatibilidad de `resume` con estados que contienen `zip` (FR-808).

## Fase 1: Comando `limpiar` en `pra_helper.py`

- [ ] **T808** Implementar `_limpiar_proyecto(project_dir)` fase de respaldo.
- [ ] **T809** Implementar puerta protectora del lote (aborta sin borrar si falta el lote).
- [ ] **T810** Implementar fase de eliminacion de artefactos residuales.
- [ ] **T811** Implementar retorno de reporte JSON (`ok`, `backup`, `eliminados`, `protegidos`).
- [ ] **T812** Implementar `cmd_limpiar` y registrar el subparser `limpiar` en `main()`.

## Fase 2: Orquestador - fase `cleanup` y omision de `zip`

- [ ] **T813** Reemplazar `"zip"` por `"cleanup"` en `nuevo_estado()`.
- [ ] **T814** Implementar `fase_cleanup(estado)` invocando `run_helper("limpiar")` y validando el reporte.
- [ ] **T815** Actualizar `ejecutar_desde_estado` para llamar `fase_cleanup` en lugar de `fase_zip`.
- [ ] **T816** Ajustar el mensaje `[FIN]` y la tabla de fases de `status`.
- [ ] **T817** Ajustar `TRANSICIONES_VALIDAS` para la fase `cleanup`.

## Fase 3: Retrocompatibilidad de `resume`

- [ ] **T818** Normalizar fases al cargar estado: mapear `zip` -> `cleanup`.
- [ ] **T819** Manejar `zip@completada` como `cleanup@completada` (no re-ejecutar).
- [ ] **T820** Manejar `zip@pendiente/en_curso/fallida` sin corromper la corrida.

## Fase 4: Pruebas (verde y refactor)

- [ ] **T821** Ejecutar las pruebas de la Fase 0 y confirmar que pasan tras la implementacion (verde).
- [ ] **T822** Actualizar `tests/integration/test_cli_orchestrator_run_mock.py` al nuevo estado final (sin `outputs.zip`, con `cleanup`, `backup/`).
- [ ] **T823** Actualizar `tests/integration/test_cli_orchestrator_resume.py` para verificar la fase `cleanup` y la retrocompatibilidad.
- [ ] **T824** Agregar prueba de integracion CLI del comando `limpiar`.
- [ ] **T825** Refactorizar y eliminar deuda sin romper la suite.

## Fase 5: Documentacion y validacion final

- [ ] **T826** Actualizar `README.md`, `AGENTS.md` y `SESION_PRA_RESUMEN.md`.
- [ ] **T827** Actualizar contratos CLI de las especificaciones 001 y 003 (fase `cleanup`, comando `limpiar`).
- [ ] **T828** Ejecutar `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
- [ ] **T829** Ejecutar una corrida mock E2E y validar el estado final (solo lote + `backup/fuente/`, sin `outputs.zip`).
- [ ] **T830** Confirmar cobertura minima de 85% en ambos modulos y cero regresiones.
