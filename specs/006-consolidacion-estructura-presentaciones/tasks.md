# Lista de Tareas: Consolidacion de Presentaciones PRA

**Fecha**: 2026-08-24

## Fase 1: Modelo y normalizacion

- [ ] **T601** Definir el contrato interno de `ConsolidationReport` y las reglas de identidad de laminas.
- [ ] **T602** Implementar helpers para normalizar `sesionN` a `sessionN` y referencias Blade.
- [ ] **T603** Implementar deteccion de duplicados y ordenamiento segun `presentation_plan.json`.
- [ ] **T604** Implementar validacion de referencias de vistas y archivos existentes.

## Fase 2: Consolidacion en `pra_helper.py`

- [ ] **T605** Implementar la operacion CLI `consolidate`.
- [ ] **T606** Generar `manifest.blade.php` con `@extends`, `@section('title')`, `@section('slides')` y cierre correcto.
- [ ] **T607** Fusionar `manifest_additions/` sin duplicar laminas y corregir comentarios Blade invalidos.
- [ ] **T608** Materializar vistas en `sessionN/` y `global/`.
- [ ] **T609** Generar `assets/styles.blade.php` y fragmentos CSS bajo `assets/styles_blade/css/`.
- [ ] **T610** Generar `assets/scripts.blade.php` y fragmentos JS bajo `assets/styles_blade/js/`.
- [ ] **T611** Validar CSS inline, includes rotos y referencias `sesionN` antes de reportar exito.
- [ ] **T612** Garantizar idempotencia al ejecutar `consolidate` repetidamente.

## Fase 3: Integracion del orquestador

- [ ] **T613** Agregar la fase `consolidate` al estado de orquestacion.
- [ ] **T614** Ejecutar `consolidate` despues de la ultima sesion y antes de `pytest`.
- [ ] **T615** Integrar reporte, errores, reintentos y transiciones de estado.
- [ ] **T616** Permitir reanudar una consolidacion fallida sin repetir sesiones completadas.
- [ ] **T617** Bloquear `pytest` y `zip` cuando la consolidacion no sea valida.

## Fase 4: Pruebas

- [ ] **T618** Crear pruebas unitarias para normalizacion de nombres y referencias.
- [ ] **T619** Crear pruebas unitarias para fusion de manifest y eliminacion de duplicados.
- [ ] **T620** Crear pruebas unitarias para consolidacion de estilos y scripts.
- [ ] **T621** Crear pruebas unitarias para deteccion de CSS inline y referencias inexistentes.
- [ ] **T622** Crear pruebas de integracion para `pra_helper.py consolidate`.
- [ ] **T623** Crear pruebas de integracion para `run` y `resume` con la nueva fase.
- [ ] **T624** Actualizar pruebas constitucionales de estructura, escritura exclusiva y ZIP.

## Fase 5: Documentacion y validacion final

- [ ] **T625** Actualizar `README.md`, `AGENTS.md` y `SESION_PRA_RESUMEN.md`.
- [ ] **T626** Validar manualmente los escenarios del Quickstart.
- [ ] **T627** Ejecutar `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.
- [ ] **T628** Ejecutar una corrida mock completa y verificar la estructura consolidada y `outputs.zip`.
- [ ] **T629** Confirmar cobertura minima de 85% en ambos modulos y cero regresiones.
