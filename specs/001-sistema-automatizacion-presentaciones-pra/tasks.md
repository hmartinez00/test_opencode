# Lista de Tareas: Sistema de Automatizacion Progresiva de Presentaciones Reveal.js (PRA)

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [Plan de Implementacion](./plan.md)

## Resumen de Ejecucion

- **Total de Tareas**: 19
- **MVP Sugerido**: Fases 1 a 3 (T001 a T008) - Generacion e inicializacion del Plan Maestro
- **Historias de Usuario cubiertas**: US1 (P1), US2 (P1), US3 (P2), US4 (P3)

---

## Fase 1: Configuracion Inicial (Setup)

- [ ] T001 Verificar entorno Python 3.11+ y estructura base del proyecto en `C:\laragon\www\test_opencode\`
- [ ] T002 [P] Verificar que el enlace de union `research_prompts_templates/` sea funcional y accesible
- [ ] T003 [P] Verificar que `.specify/memory/constitution.md` exista y contenga los 5 principios fundamentales

---

## Fase 2: Componentes Fundamentales (Foundational - Motor `pra_helper.py`)

- [ ] T004 [P] Crear esqueleto de `pra_helper.py` con manejo de argumentos CLI via `argparse` en `C:\laragon\www\test_opencode\pra_helper.py`
- [ ] T005 [P] Implementar utilidades de lectura/escritura UTF-8 y manejo determinista de JSON (carga, fusion sin duplicados, guardado con indentacion de 2 espacios) en `pra_helper.py`
- [ ] T006 [P] Implementar validador regex de Cero CSS Inline (deteccion y rechazo de `style="..."` en archivos Blade) en `pra_helper.py`

---

## Fase 3: Historia de Usuario 1 - Generacion e Inicializacion del Plan Maestro (Prioridad: P1)

> **Objetivo**: Permitir la lectura de un documento fuente y la inicializacion del plan maestro y registros vacios.
> **Prueba Independiente**: Ejecutar `--init` y `--save-plan` para verificar la creacion de `presentation_plan.json`, `class_registry.json`, `js_registry.json`, `manifest_draft.blade.php` y las subcarpetas por sesion.

- [ ] T007 [US1] Implementar comando `pra_helper.py --init <documento_fuente>` para extraer texto del documento fuente y compilar el prompt de generacion del Plan Maestro combinando el contenido con la plantilla `presentation_plan_meta_prompt.md`
- [ ] T008 [US1] Implementar comando `pra_helper.py --save-plan <json_plan>` para validar el JSON contra el esquema `PresentationPlan`, guardar `presentation_plan.json`, inicializar `class_registry.json` y `js_registry.json` con entradas iniciales, crear subcarpetas `sesion[N]/`, carpetas `styles_additions/`, `scripts_additions/`, `manifest_additions/`, y generar `manifest_draft.blade.php`
- [ ] T009 [US1] Validar ejecucion independiente de la Historia de Usuario 1 con un documento fuente de ejemplo (verificar estructura de archivos creados y registros inicializados)

---

## Fase 4: Historia de Usuario 2 - Construccion Progresiva por Sesiones (Prioridad: P1)

> **Objetivo**: Generar las laminas Blade, acumular estilos/scripts y fusionar registros de forma incremental por sesion.
> **Prueba Independiente**: Ejecutar `--prompt-session 1` y `--process-session 1` para verificar la creacion de laminas `.blade.php`, estilos en `styles.blade.php`, scripts en `scripts.blade.php` y actualizacion de registros sin duplicados.

- [ ] T010 [US2] Implementar comando `pra_helper.py --prompt-session <N>` para compilar el prompt adaptado inyectando: contexto de la sesion N del plan, laminas a generar, clases CSS y comportamientos JS ya implementados en los registros, y la plantilla maestra `presentation_slide_meta_prompt.md`
- [ ] T011 [US2] Implementar comando `pra_helper.py --process-session <N> <respuesta_llm>` para parsear la respuesta del LLM, crear archivos `sesion[N]/[slide-id-kebab-case].blade.php`, acumular estilos CSS en `styles.blade.php`, acumular scripts JS en `scripts.blade.php`, escribir respaldos en `styles_additions/` y `scripts_additions/`, fusionar registros JSON sin duplicados, generar `manifest_additions/sesion[N].blade.php` y actualizar `manifest_draft.blade.php`
- [ ] T012 [US2] Validar que `--process-session` ejecute la validacion regex de Cero CSS inline sobre cada lamina generada y reporte error si detecta violaciones
- [ ] T013 [US2] Validar ejecucion independiente de la Sesion 1: verificar creacion de laminas Blade, acumulacion correcta de estilos/scripts y actualizacion de registros con `implementada: true`

---

## Fase 5: Historia de Usuario 3 - Garantia de Cumplimiento Constitucional (Prioridad: P2)

> **Objetivo**: Asegurar el cumplimiento estricto de las reglas no negociables de la Constitucion.
> **Prueba Independiente**: Verificar que el sistema bloquea cualquier intento de introduccion de estilos inline o construccion fuera de orden secuencial.

- [ ] T014 [US3] Implementar bloqueo de ejecucion en `--prompt-session <N>` si la sesion N-1 no esta en estado COMPLETADA (o si N>1 y no existe `sesion[N-1]` con archivos generados)
- [ ] T015 [US3] Implementar validacion de encapsulamiento JS: verificar que los scripts generados esten dentro de `DOMContentLoaded` con comentario de trazabilidad de lamina
- [ ] T016 [US3] Validar que el sistema rechace y reporte cualquier lamina Blade que contenga atributos `style="..."` durante `--process-session`

---

## Fase 6: Historia de Usuario 4 - Empaquetado y Exportacion Final (Prioridad: P3)

> **Objetivo**: Permitir la compresion y entrega del resultado final para su integracion en Laravel.
> **Prueba Independiente**: Ejecutar `pra_helper.py --zip` y comprobar la validez de la estructura interna del archivo `.zip` generado.

- [ ] T017 [US4] Implementar comando `pra_helper.py --zip` para comprimir recursivamente el proyecto activo (laminas Blade, registros JSON, estilos/scripts acumuladores, manifest, estilos/scripts de respaldo, plan maestro) en `outputs.zip`
- [ ] T018 [US4] Validar que el archivo `.zip` generado contenga la estructura completa y que pueda descomprimirse sin errores

---

## Fase 7: Pulido y Verificacion End-to-End

- [ ] T019 Ejecutar los escenarios de prueba completos definidos en `quickstart.md` (flujo completo Sesion 1, validacion constitucional, verificacion de registros)

---

## Grafo de Dependencias

```text
T001, T002, T003 (Setup) --> T004, T005, T006 (Foundational)
T004, T005, T006 --> T007, T008, T009 (US1)
T007, T008, T009 --> T010, T011, T012, T013 (US2)
T010, T011, T012, T013 --> T014, T015, T016 (US3)
T014, T015, T016 --> T017, T018 (US4)
T017, T018 --> T019 (Polish)
```

## Ejemplos de Ejecucion Paralela

| Fase | Tareas Paralelas | Justificacion |
|------|------------------|---------------|
| Setup | T001 + T002 + T003 | Verificaciones independientes del entorno |
| Foundational | T004 + T005 + T006 | Componentes de `pra_helper.py` sin dependencias cruzadas |
| US1 | T007 + T008 | Comandos CLI independientes (se ejecutan en secuencia de uso, pero se pueden desarrollar en paralelo) |
| US2 | T010 + T011 | Comandos CLI independientes (se desarrollan en paralelo, se validan en secuencia) |

## Estrategia de Implementacion

1. **MVP Primero**: Completar Fases 1-3 (T001 a T009) para tener un sistema funcional de inicializacion de plan maestro.
2. **Incremento 1**: Fase 4 (T010 a T013) para habilitar la construccion de laminas.
3. **Incremento 2**: Fases 5-6 (T014 a T018) para completar el cumplimiento constitucional y empaquetado.
4. **Verificacion Final**: Fase 7 (T019) para validacion end-to-end.
