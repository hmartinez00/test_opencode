# Especificacion de Funcionalidad: Robustez y Coherencia del Flujo PRA (009-robustez-coherencia-pra)

**Rama de Funcionalidad**: `009-robustez-coherencia-pra`

**Fecha de Creacion**: 2026-08-31

**Estado**: Borrador

**Entrada**: Al levantar una presentacion real (modulo1_fundamentos_python) mediante el flujo manual de PRA se detectaron varios inconvenientes que debilitan la robustez del flujo y la confiabilidad del entregable:

1. **Lamina fuera del plan ignorada silenciosamente**: el consolidador (`_consolidate_project`) itera exclusivamente sobre las laminas declaradas en `presentation_plan.json`, de modo que una lamina escrita en `sesion[N]/` que NO este declarada en el plan se omite del `manifest.blade.php` sin advertencia. En la corrida real, `conversion-tipos`, `entorno-colab` y `manipulacion-strings` no aparecieron en el manifest (solo se resolvio tras editar manualmente el plan).
2. **Plan guardado sin registros ni insumos**: un `save-plan` que solo envie la Parte 1 (JSON de sesiones) deja `class_registry.json` y `js_registry.json` vacios y todos los `insumos` de las laminas como lista vacia. El constructor de sesiones carece de vocabulario visual planificado y de insumos a materializar, debilitando la fidelidad al documento fuente.
3. **Backend `opencode` del orquestador no resuelve el binario**: `pra_orchestrator.py run ... --backend opencode` reporto `CLI 'opencode' no encontrada en PATH`, a pesar de que el binario esta en `C:\Users\HP\.opencode\bin\opencode.exe` y se resuelve desde Python en pruebas aisladas. La causa es una discrepancia del PATH heredado por el subprocess del orquestador.
4. **Seleccion de proyecto activo ambigua**: con varios proyectos bajo la ruta base y sin `PRA_ACTIVE_PROJECT`, la busqueda automatica selecciono `intro_docker` en lugar del proyecto recien creado (`modulo1_fundamentos_python`), provocando que `prompt-session` leyera el plan equivocado.

Esta iteracion introduce las salvaguardas y validaciones necesarias para que estos fallos sean detectados, reportados de forma estructurada y, cuando corresponda, abortados con un mensaje claro en lugar de fallar en silencio.

---

## Objetivo

Endurecer el flujo PRA frente a los cuatro inconvenientes detectados:

1. **Coherencia plan vs. laminas en consolidacion**: el consolidador debe detectar y reportar laminas huerfanas (escritas en `sesion[N]/` pero no declaradas en el plan), laminas faltantes (declaradas en el plan pero no escritas) y laminas duplicadas, devolviendo un reporte estructurado. Ante una incoherencia bloqueante, la consolidacion aborta sin generar un manifest incompleto.
2. **Calidad minima del plan al guardar**: `save-plan` debe validar que el plan incluya registros CSS/JS no vacios y que cada lamina tenga `insumos` materizables, emitiendo advertencias (o errores configurable) cuando no sea asi.
3. **Backend `opencode` robusto en el orquestador**: el orquestador debe resolver el binario `opencode` de forma fiable, contemplando rutas conocidas y el PATH, con un mensaje de error diagnostico cuando no lo encuentre.
4. **Seleccion explicita de proyecto activo**: la busqueda automatica debe detectar ambiguedad (mas de un proyecto candidato) y exigir `PRA_ACTIVE_PROJECT` o advertir claramente, evitando operar sobre el proyecto equivocado.

## Contexto de los 4 inconvenientes (problema -> solucion propuesta)

| # | Inconveniente | Problema raiz | Solucion propuesta |
|---|---|---|---|
| 1 | Lamina fuera del plan ignorada | `_consolidate_project` itera por `plan.sesiones[].laminas`, descartando archivos de `sesion[N]/` no declarados | Oracle de coherencia en consolidacion: detecta huerfanas/faltantes/duplicadas y reporta o aborta |
| 2 | Plan sin registros/insumos | `save-plan` no valida que se entreguen Partes 2/3 (registros) ni insumos | Validacion de calidad minima del plan al guardar |
| 3 | Backend opencode no resuelto | El subprocess no hereda el PATH de Git Bash con `C:\Users\HP\.opencode\bin` | Resolucion robusta del binario con rutas conocidas + diagnostico |
| 4 | Proyecto activo ambiguo | Busqueda automatica toma el primero alfabetico sin verificar ambiguedad | Deteccion de ambiguedad y exigencia de `PRA_ACTIVE_PROJECT` |

---

## Historias de Usuario y Pruebas

### Historia de Usuario 1 - Coherencia plan vs. laminas (Prioridad: P1)

Como desarrollador PRA, necesito que la consolidacion detecte y reporte cualquier lamina que no tenga correspondencia exacta entre el plan y los archivos escritos, para no entregar un manifest incompleto silenciosamente.

**Prueba Independiente**: Escribir en `sesion[N]/` una lamina que no esta declarada en el plan y ejecutar `consolidate`. Verificar que el consolidador reporta la lamina huerfana y (segun la puerta configurada) aborta sin generar un manifest incompleto.

**Escenarios de Aceptacion**:

1. Una lamina en `sesion[N]/` no declarada en el plan se reporta como "huerfana" en el reporte estructurado.
2. Una lamina declarada en el plan pero no escrita en `sesion[N]/` se reporta como "faltante".
3. Una lamina declarada dos veces con el mismo `id_kebab_case` en el plan se reporta como "duplicada".
4. Si existen incoherencias bloqueantes, el manifest NO se genera incompleto y `ok` es `false`.
5. Si no hay incoherencias, el manifest se genera completo y `ok` es `true`.

### Historia de Usuario 2 - Validacion de calidad del plan (Prioridad: P1)

Como creador de presentaciones, necesito que `save-plan` me advierta si el plan no incluye los registros CSS/JS iniciales o si alguna lamina carece de insumos, para corregirlo antes de construir las sesiones.

**Prueba Independiente**: Guardar un plan que solo contiene la Parte 1 (sin partes 2/3, sin insumos) y verificar que `save-plan` emite advertencias estructuradas de calidad.

**Escenarios de Aceptacion**:

1. Si `class_registry.json` y `js_registry.json` quedarian vacios, se emite una advertencia visible.
2. Si alguna lamina tiene `insumos` vacio, se emite una advertencia por cada lamina afectada.
3. Por defecto la validacion es de advertencia (no bloquea); el plan se guarda igualmente.
4. Un criterio de bloqueo configurable permite convertir estas advertencias en errores cuando se requiera.

### Historia de Usuario 3 - Backend opencode robusto (Prioridad: P1)

Como usuario del flujo desatendido, necesito que el backend `opencode` se resuelva de forma confiable, para poder ejecutar `pra_orchestrator.py run ... --backend opencode` sin que falle por no encontrar el binario.

**Prueba Independiente**: Ejecutar el orquestador con `--backend opencode` y verificar que (a) resuelve el binario y procede, o (b) si no lo encuentra, emite un mensaje de diagnostico claro con las rutas intentadas.

**Escenarios de Aceptacion**:

1. El binario `opencode` se resuelve via PATH o via rutas conocidas (`~/.opencode/bin/opencode`, etc.).
2. Si no se encuentra, el orquestador reporta `BACKEND_NO_DISPONIBLE` con las rutas intentadas y el PATH relevante.
3. La resolucion no depende del shell desde el que se lanza el orquestador (Git Bash vs cmd).

### Historia de Usuario 4 - Seleccion explicita de proyecto activo (Prioridad: P2)

Como usuario con varios proyectos bajo la ruta base, necesito que el sistema detecte la ambiguedad y no opere sobre un proyecto incorrecto por defecto.

**Prueba Independiente**: Tener al menos dos proyectos bajo la ruta base sin `PRA_ACTIVE_PROJECT` y ejecutar un comando que depende del proyecto activo. Verificar que el sistema advierte de la ambiguedad (o exige la variable) en lugar de elegir silenciosamente el primero alfabetico.

**Escenarios de Aceptacion**:

1. Con `PRA_ACTIVE_PROJECT` valido, se usa ese proyecto de forma determinista.
2. Sin `PRA_ACTIVE_PROJECT` y con ambiguedad (varios proyectos), se emite una advertencia clara listando los candidatos.
3. El comportamiento de "un solo proyecto" (sin ambiguedad) se mantiene sin cambios.

---

## Requisitos Funcionales

### Coherencia en consolidacion
- **FR-901**: El consolidador calcula el conjunto de laminas declaradas en el plan por sesion.
- **FR-902**: El consolidador detecta laminas **huerfanas**: archivos `.blade.php` en `sesion[N]/` cuyo nombre no esta declarado en el plan de esa sesion.
- **FR-903**: El consolidador detecta laminas **faltantes**: `id_kebab_case` declarado en el plan cuyo archivo `sesion[N]/<id>.blade.php` no existe.
- **FR-904**: El consolidador detecta laminas **duplicadas**: el mismo `id_kebab_case` declarado mas de una vez en el plan (misma o distinta sesion).
- **FR-905**: El consolidador agrega al reporte del JSON un bloque `coherencia` con listas `huerfanas`, `faltantes` y `duplicadas`, cada una con informacion diagnostica (sesion, id, sugerencia).
- **FR-906**: Ante incoherencias bloqueantes (huerfanas/faltantes/duplicadas), el consolidador NO genera un manifest incompleto y devuelve `ok: false` con los errores de coherencia.
- **FR-907**: Si no hay incoherencias, el consolidador genera el manifest completo y devuelve `ok: true`.
- **FR-908**: El consolidador mantiene la validacion existente de CSS inline sobre las laminas que SÍ se consolidan.

### Calidad del plan
- **FR-909**: `save-plan` valida que `class_registry.json` y `js_registry.json` resultantes no esten vacios, y emite advertencia si lo estan.
- **FR-910**: `save-plan` valida que cada lamina tenga `insumos` no vacios, y emite una advertencia por lamina afectada.
- **FR-911**: La validacion de calidad es de advertencia por defecto (no bloquea el guardado); un criterio configurable permite elevarla a error.

### Backend opencode
- **FR-912**: El backend `opencode` del orquestador resuelve el binario via PATH y via rutas conocidas (`~/.opencode/bin/opencode[.exe]`, etc.).
- **FR-913**: Si el binario no se encuentra, el orquestador reporta `BACKEND_NO_DISPONIBLE` con las rutas intentadas y el PATH relevante, sin traceback crudo.

### Proyecto activo
- **FR-914**: La seleccion del proyecto activo detecta ambiguedad (varios proyectos bajo la ruta base) cuando no hay `PRA_ACTIVE_PROJECT`.
- **FR-915**: Con ambiguedad y sin `PRA_ACTIVE_PROJECT`, se emite una advertencia clara listando los candidatos validos.

## Criterios de Exito

- **SC-901**: Una lamina fuera del plan ya no se omite silenciosamente; se reporta como huerfana.
- **SC-902**: La consolidacion con incoherencias devuelve `ok: false` y no entrega un manifest incompleto.
- **SC-903**: `save-plan` advierte de planes sin registros CSS/JS o con laminas sin insumos.
- **SC-904**: `pra_orchestrator.py run ... --backend opencode` resuelve el binario o reporta un diagnostico claro.
- **SC-905**: Con proyectos ambiguos y sin `PRA_ACTIVE_PROJECT`, se advierte en lugar de elegir silenciosamente.
- **SC-906**: La suite completa permanece en verde y la cobertura de `pra_helper.py` y `pra_orchestrator.py` es >= 85%.

## Casos Extremos

- Lamina huerfana que comparte nombre con una declarada en otra sesion: se reporta segun su sesion concreta.
- `insumos` nulo (no solo `[]`) en una lamina: se trata como vacio y se advierte.
- Backend `opencode` presente en PATH pero no ejecutable: se captura el error de ejecucion y se reporta.
- Ambiguedad con proyectos temporales (`backup/`, `themes/`) que no son proyectos reales: se filtran antes de contar.
- Plan que declara una lamina pero ninguna sesion tiene archivos escritos: se reportan todas como faltantes.
- Re-consolidacion idempotente: una segunda consolidacion sin cambios no debe reportar incoherencias nuevas.

## Fuera de Alcance

- Rediseñar laminas o estilos visuales.
- Migrar retroactivamente proyectos ya consolidados.
- Cambiar el algoritmo de generacion de contenido de las laminas.
- Modificar la constitucion del proyecto.
- Reescribir el backend `opencode` mas alla de la resolucion robusta del binario y el diagnostico.
- Cambiar el contrato de `save-plan` como comando (el JSON sigue aceptando cualquiera de los dos juegos de nombres de campo normalizados).
