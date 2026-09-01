# Lista de tareas: robustez y coherencia del flujo PRA

**Fecha**: 2026-09-01
**Especificación**: [spec.md](./spec.md)
**Estado**: preparada para red -> green -> refactor

## Fase 0: pruebas rojas (TDD)

- [ ] **T001** Redactar prueba unitaria para la detección de laminas huérfanas.
- [ ] **T002** Redactar prueba unitaria para la detección de laminas faltantes.
- [ ] **T003** Redactar prueba unitaria para la detección de laminas duplicadas.
- [ ] **T004** Redactar prueba de integración para `consolidate` con incoherencia y `ok: false`.
- [ ] **T005** Redactar prueba para advertencias por `class_registry` y `js_registry` vacíos.
- [ ] **T006** Redactar prueba para advertencias de laminas sin `insumos`.
- [ ] **T007** Redactar prueba para el modo estricto `PRA_PLAN_ESTRICTO=1`.
- [ ] **T008** Redactar prueba para la resolución del binario `opencode`.
- [ ] **T009** Redactar prueba para el diagnóstico `BACKEND_NO_DISPONIBLE`.
- [ ] **T010** Redactar prueba para la ambigüedad del proyecto activo.

## Fase 1: coherencia del proyecto generado

- [ ] **T011** Implementar la función de análisis de coherencia del proyecto.
- [ ] **T012** Incluir los resultados del análisis en el reporte JSON de consolidación.
- [ ] **T013** Integrar la validación de coherencia dentro de `_consolidate_project()`.
- [ ] **T014** Asegurar que una incoherencia bloquee la creación del manifest final incompleto.
- [ ] **T015** Añadir pruebas de regresión para flujos coherentes sin errores.

## Fase 2: validación de calidad mínima del plan

- [ ] **T021** Implementar la validación de `class_registry` y `js_registry` vacíos.
- [ ] **T022** Implementar la validación de laminas sin `insumos`.
- [ ] **T023** Exponer advertencias en salida estándar y en el JSON de respuesta.
- [ ] **T024** Implementar `PRA_PLAN_ESTRICTO=1` como activador de error.
- [ ] **T025** Verificar que la operación normal no se rompa sin el modo estricto.

## Fase 3: backend `opencode` robusto

- [ ] **T031** Implementar la resolución de binario con PATH + rutas conocidas.
- [ ] **T032** Añadir manejo de archivos ejecutables no válidos en la resolución.
- [ ] **T033** Integrar el diagnóstico estructurado en el orquestador.
- [ ] **T034** Asegurar que el backend no falle con un traceback sin contexto.

## Fase 4: proyecto activo y ambigüedad

- [ ] **T041** Filtrar directorios no proyectables al resolver el proyecto activo.
- [ ] **T042** Detectar más de un proyecto candidato y advertir explícitamente.
- [ ] **T043** Mantener determinismo cuando `PRA_ACTIVE_PROJECT` está definido.

## Fase 5: pruebas de calidad y refactor

- [ ] **T051** Ejecutar la suite TDD y confirmar el estado rojo antes de la corrección.
- [ ] **T052** Ejecutar la suite tras la implementación y confirmar el estado verde.
- [ ] **T053** Revisar consultas y fixtures para evitar pruebas frágiles o dependientes del orden.
- [ ] **T054** Refactorizar sin cambiar comportamiento validado.

## Fase 6: documentación y cierre

- [ ] **T061** Actualizar documentación pública y de agente.
- [ ] **T062** Registrar la decisión y el alcance en la sesión de trabajo.
- [ ] **T063** Confirmar cobertura mínima y ejecución completa de pruebas.

---

## Dependencias entre tareas

- T011 requiere la definición concreta del analizador de coherencia.
- T013 depende de T011.
- T021 y T022 dependen del contrato exacto de `save-plan`.
- T031 depende de la comprobación de rutas del sistema y la resolución del PATH.
- T042 depende del algoritmo de resolución del proyecto activo.
- T051 y T052 deben ejecutarse antes de cerrar la iteración.

## Criterio de aceptación final

Se considerará completada la etapa previa a implementación cuando:

- todas las pruebas rojas estén escritas y reproducen el problema,
- la estructura de la especificación esté consolidada,
- la implementación no haya empezado todavía,
- la siguiente fase de desarrollo pueda comenzar con un conjunto de pruebas verificables.
