# Lista de tareas: guion narrativo y coherencia audiovisual

**Fecha**: 2026-09-01  
**Especificación**: [spec.md](./spec.md)  
**Plan**: [plan.md](./plan.md)  
**Estado**: implementación completada; lista conservada como trazabilidad de ejecución

## Fase 0: definición y pruebas rojas

- [ ] **T001** Confirmar la convención `[slide: N]` basada en cero y su mapeo con `orden`.
- [ ] **T002** Crear fixture de respuesta de sesión con BLOQUE 6 válido.
- [ ] **T003** Crear fixture con marca duplicada.
- [ ] **T004** Crear fixture con índice fuera de rango.
- [ ] **T005** Crear fixture con entrada narrativa vacía.
- [ ] **T006** Crear fixture con lámina sin entrada narrativa.
- [ ] **T007** Crear fixture con narración sin lámina.
- [ ] **T008** Redactar todas las pruebas rojas del [test_plan.md](./test_plan.md).
- [ ] **T009** Ejecutar solo las pruebas nuevas y registrar el fallo esperado.

## Fase 1: contrato y parser

- [ ] **T011** Definir la expresión de parseo de marcas `[slide: N]`.
- [ ] **T012** Implementar el parser del BLOQUE 6 sin mezclarlo con el parser Blade.
- [ ] **T013** Implementar normalización de índices narrativos a láminas del plan.
- [ ] **T014** Implementar diagnóstico estructurado de faltantes, huérfanas, duplicadas y vacías.
- [ ] **T015** Definir el comportamiento para texto antes de la primera marca.
- [ ] **T016** Definir y probar la política de compatibilidad sin BLOQUE 6.

## Fase 2: generación y persistencia

- [ ] **T021** Ampliar `presentation_slide_meta_prompt.md` con los objetivos e insumos narrativos.
- [ ] **T022** Añadir el contrato del BLOQUE 6 al prompt.
- [ ] **T023** Integrar el resultado narrativo en `process-session`.
- [ ] **T024** Crear `assets/audio/` de forma idempotente.
- [ ] **T025** Escribir `guion_sesionN.txt` en UTF-8 con formato estable.
- [ ] **T026** Evitar escritura parcial si el guion falla la validación estructural.
- [ ] **T027** Añadir el guion al respaldo `backup/fuente/`.
- [ ] **T028** Actualizar las respuestas mock de las sesiones.

## Fase 3: validación audiovisual

- [ ] **T031** Implementar la validación de cobertura uno-a-uno entre láminas y narración.
- [ ] **T032** Implementar advertencias de entradas vacías.
- [ ] **T033** Implementar comprobaciones básicas contra objetivos e insumos del plan.
- [ ] **T034** Integrar la puerta audiovisual en `consolidate`.
- [ ] **T035** Incluir el bloque `audio` en los reportes JSON.
- [ ] **T036** Implementar `PRA_AUDIO_ESTRICTO=1`.
- [ ] **T037** Verificar que no se cree manifest final ante error bloqueante.

## Fase 4: orquestador y reintentos

- [ ] **T041** Propagar diagnósticos audiovisuales al orquestador.
- [ ] **T042** Añadir errores audiovisuales al prompt de reflexión.
- [ ] **T043** Mantener códigos de salida y estados existentes.
- [ ] **T044** Verificar que el orquestador no escriba archivos de audio directamente.
- [ ] **T045** Verificar reanudación de una sesión con guion fallido.

## Fase 5: consolidación y limpieza

- [ ] **T051** Incluir `assets/audio/` en el lote protegido.
- [ ] **T052** Copiar o preservar guiones durante la consolidación sin regenerarlos.
- [ ] **T053** Respaldar guiones en `backup/fuente/` de forma determinista.
- [ ] **T054** Eliminar solo residuales permitidos y no el directorio `assets/audio/`.
- [ ] **T055** Verificar idempotencia de consolidación y limpieza.

## Fase 6: validación TDD y documentación

- [ ] **T061** Ejecutar pruebas unitarias nuevas.
- [ ] **T062** Ejecutar pruebas de integración nuevas.
- [ ] **T063** Ejecutar pruebas constitucionales nuevas.
- [ ] **T064** Ejecutar la suite completa con cobertura de `pra_helper.py` y `pra_orchestrator.py`.
- [ ] **T065** Confirmar cobertura mínima del 85% en ambos módulos.
- [ ] **T066** Actualizar README, AGENTS y resumen de sesión.
- [ ] **T067** Revisar que no se hayan creado archivos de implementación fuera del alcance.

## Dependencias

- T001 debe completarse antes de T011 y T013.
- T002-T009 deben completarse antes de T023.
- T011-T016 deben completarse antes de T031.
- T023-T028 deben completarse antes de T034.
- T034-T037 deben completarse antes de T041.
- T051-T055 dependen de la definición del lote protegido existente.
- T061-T065 son puertas de salida y deben ejecutarse antes de cerrar la iteración.

## Criterio de aceptación de la planificación

La fase previa queda completa cuando el contrato narrativo, la numeración, las rutas, las puertas de calidad, las dependencias y las pruebas TDD están definidos sin cambios en producción.
