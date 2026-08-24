# Research Tecnico: Consolidacion de Presentaciones PRA

**Iteracion**: 006-consolidacion-estructura-presentaciones

## D-601: Separar construccion interna y producto final

**Decision**: Mantener los artefactos `presentation_plan.json`, registries y `*_additions` como estado de construccion, y generar una salida consolidada independiente dentro del mismo proyecto.

**Razon**: Los artefactos internos son necesarios para sesiones progresivas y reanudacion, pero no constituyen por si mismos una presentacion Laravel lista para integrar.

## D-602: Manifest unico como punto de entrada

**Decision**: El producto final debe tener exactamente un `manifest.blade.php` como punto de entrada de laminas.

**Razon**: El ejemplo consolidado integra layout, secciones, vistas globales y assets desde un solo manifest. Los archivos `manifest_draft.blade.php` y `manifest_additions/` son fuentes intermedias, no sustitutos del manifest final.

## D-603: Convencion `sessionN` y `global`

**Decision**: La salida consolidada usara nombres de directorio en ingles: `session1/`, `session2/` y `global/`.

**Razon**: Coincide con la estructura de referencia y con la convencion de namespaces Blade esperada por la aplicacion Laravel. La entrada `sesionN` se tratara como nombre interno y se normalizara al exportar.

## D-604: Assets modulares con entrypoints

**Decision**: Los entrypoints seran `assets/styles.blade.php` y `assets/scripts.blade.php`, con fragmentos separados en `assets/styles_blade/css/` y `assets/styles_blade/js/`.

**Razon**: Permite que el manifest use `@include` estables, reduce conflictos entre sesiones y mantiene los bloques de estilos y scripts auditables.

## D-605: Validacion antes del empaquetado

**Decision**: La fase de consolidacion tendra una puerta estructural propia y `zip` no podra ejecutarse si falla.

**Razon**: Un ZIP exitoso que contiene una estructura incorrecta es un falso positivo del flujo.

## D-606: CSS inline

**Decision**: El exportador rechazara CSS inline en las vistas finales. No se copiara esta practica del proyecto de referencia.

**Razon**: La referencia `filtros_multidimensionales` es valida como modelo estructural, pero sus atributos `style` contradicen el principio constitucional I.

## D-607: Idempotencia

**Decision**: Ejecutar la consolidacion varias veces debe producir el mismo conjunto de archivos y referencias.

**Razon**: `resume`, reintentos y ejecuciones de validacion pueden invocar la fase mas de una vez.

## D-608: Responsabilidad de escritura

**Decision**: Toda escritura de artefactos de consolidacion sera delegada a `pra_helper.py`; el orquestador solo coordinara comandos y validaciones.

**Razon**: Preserva el principio constitucional III y evita que existan dos escritores con reglas distintas.
