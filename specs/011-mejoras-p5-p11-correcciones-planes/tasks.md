# Lista de tareas: correcciones al motor PRA (iteracion 011)

**Fecha**: 2026-09-02
**Especificacion**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Estado**: En planificacion (pre-implementacion)

## Fase 0: baseline y fixtures

- [ ] **T001** Ejecutar suite existente y confirmar baseline verde con cobertura actual.
- [ ] **T002** Crear fixture de plan sin campo `orden` en ninguna lamina.
- [ ] **T003** Crear fixture de plan con `orden` parcialmente presente.
- [ ] **T004** Crear fixture de plan con todas las laminas con `orden` explicito.
- [ ] **T005** Crear fixture de plan con `data_title` definido en algumas laminas.
- [ ] **T006** Crear fixture de plan con la misma clase CSS declarada en dos laminas.
- [ ] **T007** Crear fixture de respuesta LLM con BLOQUE 6 y linea en blanco antes del fence.
- [ ] **T008** Crear fixture de respuesta LLM con BLOQUE 6 sin linea en blanco (actual).
- [ ] **T009** Crear fixture de respuesta LLM sin BLOQUE 6.
- [ ] **T010** Crear archivo JSON temporal con acentos para prueba de `--plan-file`.

## Fase 1: A1 — Regex BLOQUE 6 tolerante

- [ ] **T101** Escribir prueba: BLOQUE 6 con linea en blanco antes del fence -> parsea correctamente.
- [ ] **T102** Escribir prueba: BLOQUE 6 sin linea en blanco -> parsea correctamente (regression).
- [ ] **T103** Escribir prueba: respuesta sin BLOQUE 6 -> devuelve cadena vacia.
- [ ] **T104** Ejecutar pruebas T101-T103 y confirmar fallo (estado rojo).
- [ ] **T105** Modificar regex en `parse_llm_response` (linea ~691).
- [ ] **T106** Ejecutar pruebas T101-T103 y confirmar pase (estado verde).
- [ ] **T107** Ejecutar suite completa y verificar sin regresiones.

## Fase 2: A2 — Deduplicacion de registros

- [ ] **T201** Escribir prueba: plan con clase duplicada en 2 laminas -> registry con 1 entrada.
- [ ] **T202** Escribir prueba: plan con comportamiento duplicado en 2 laminas -> registry con 1 entrada.
- [ ] **T203** Escribir prueba: orden de primera aparicion se mantiene.
- [ ] **T204** Ejecutar pruebas T201-T203 y confirmar fallo (estado rojo).
- [ ] **T205** Crear funcion `_deduplicar_por_nombre` en `pra_helper.py`.
- [ ] **T206** Integrar deduplicacion en `cmd_save_plan` antes de sembrar registros.
- [ ] **T207** Ejecutar pruebas T201-T203 y confirmar pase (estado verde).
- [ ] **T208** Ejecutar suite completa y verificar sin regresiones.

## Fase 3: A3 — Auto-numerado de `orden`

- [ ] **T301** Escribir prueba: plan sin `orden` -> laminas numeradas 1..N.
- [ ] **T302** Escribir prueba: plan con `orden` parcial -> faltantes completan secuencia sin colisionar.
- [ ] **T303** Escribir prueba: plan con `orden` explicito en todas -> se respeta.
- [ ] **T304** Escribir prueba: `PRA_PLAN_ESTRICTO=1` con plan sin orden -> error.
- [ ] **T305** Ejecutar pruebas T301-T304 y confirmar fallo (estado rojo).
- [ ] **T306** Modificar `normalize_plan` para auto-numerar.
- [ ] **T307** Modificar `_validar_calidad_plan` para advertencia/error de orden.
- [ ] **T308** Ejecutar pruebas T301-T304 y confirmar pase (estado verde).
- [ ] **T309** Ejecutar suite completa y verificar sin regresiones.

## Fase 4: A4 — Preservar `data_title`

- [ ] **T401** Escribir prueba: plan con `data_title` -> normalizado conserva el campo.
- [ ] **T402** Escribir prueba: plan sin `data_title` -> fallback a `titulo`.
- [ ] **T403** Escribir prueba: `manifest_draft` usa `data_title` del plan.
- [ ] **T404** Escribir prueba: `manifest.blade.php` final usa `data_title` del plan.
- [ ] **T405** Ejecutar pruebas T401-T404 y confirmar fallo (estado rojo).
- [ ] **T406** Modificar `normalize_plan` para conservar `data_title`.
- [ ] **T407** Verificar que `cmd_save_plan` y `_consolidate_project` ya usan el fallback correcto.
- [ ] **T408** Ejecutar pruebas T401-T404 y confirmar pase (estado verde).
- [ ] **T409** Ejecutar suite completa y verificar sin regresiones.

## Fase 5: A5 — Unificacion de prefijo

- [ ] **T501** Escribir prueba: consolidar proyecto -> `session{N}/` existe en lote final.
- [ ] **T502** Escribir prueba: consolidar proyecto -> vistas del manifest usan `session{N}.*`.
- [ ] **T503** Escribir prueba: `limpiar` elimina `sesion*/` internas y preserva `session*/`.
- [ ] **T504** Escribir prueba: `backup/fuente/` conserva `sesion*/` (compatibilidad).
- [ ] **T505** Ejecutar pruebas T501-T504 y confirmar que pasan (ya implementado, solo regresion).
- [ ] **T506** Actualizar `AGENTS.md` con convencion explicita session/sesion.
- [ ] **T507** Ejecutar suite completa y verificar sin regresiones.

## Fase 6: A6 — `save-plan --plan-file`

- [ ] **T601** Escribir prueba: `--plan-file` con JSON valido -> plan guardado correctamente.
- [ ] **T602** Escribir prueba: `--plan-file` con archivo inexistente -> error PLAN_FILE_NOT_FOUND.
- [ ] **T603** Escribir prueba: `--plan-file` produce resultado identico a argv para el mismo JSON.
- [ ] **T604** Escribir prueba: JSON con acentos via `--plan-file` -> campos normalizados correctamente.
- [ ] **T605** Ejecutar pruebas T601-T604 y confirmar fallo (estado rojo).
- [ ] **T606** Modificar parser CLI para aceptar `--plan-file`.
- [ ] **T607** Modificar `cmd_save_plan` para leer desde archivo cuando se provee `--plan-file`.
- [ ] **T608** Hacer `json_plan` opcional con `nargs="?"` y validar al menos una via.
- [ ] **T609** Ejecutar pruebas T601-T604 y confirmar pase (estado verde).
- [ ] **T610** Ejecutar suite completa y verificar sin regresiones.

## Fase 7: verificacion final y documentacion

- [ ] **T701** Ejecutar suite completa: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing -q`.
- [ ] **T702** Verificar cobertura `pra_helper.py` >= 85%.
- [ ] **T703** Verificar cobertura `pra_orchestrator.py` >= 85%.
- [ ] **T704** Verificar que no se rompio interfaz CLI existente (pruebas de regresion).
- [ ] **T705** Actualizar `SESION_PRA_RESUMEN.md` con resumen de iteracion.
- [ ] **T706** Verificar que `AGENTS.md` refleja la convencion session/sesion.
- [ ] **T707** Revisar que no se crearon archivos de implementacion fuera del alcance.

## Dependencias

- T001-T010 deben completarse antes de cualquier fase de implementacion.
- Fase 1 (A1) no tiene dependencias de otras fases.
- Fase 2 (A2) no tiene dependencias de otras fases.
- Fase 3 (A3) no tiene dependencias de otras fases.
- Fase 4 (A4) no tiene dependencias de otras fases.
- Fase 5 (A5) depende de A4 (consolidate ya usa data_title).
- Fase 6 (A6) no tiene dependencias de otras fases.
- Fase 7 (verificacion) depende de todas las fases 1-6.
- Las fases 1-6 son independientes entre si y pueden ejecutarse en paralelo, pero el orden secuencial facilita el aislamiento de regresiones.

## Criterio de aceptacion de la planificacion

La fase previa queda completa cuando:
- La especificacion, el plan, esta lista de tareas y el test_plan estan definidos.
- Ningun archivo de produccion ha sido modificado.
- Los fixtures estan identificados y las pruebas rojas estan disenadas.
- La suite actual pasa sin fallos (baseline verde confirmada).
