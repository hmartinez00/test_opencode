# Especificacion de Funcionalidad: Consolidacion de Presentaciones PRA (006-consolidacion-estructura-presentaciones)

**Rama de Funcionalidad**: `006-consolidacion-estructura-presentaciones`

**Fecha de Creacion**: 2026-08-24

**Estado**: Borrador

**Entrada**: La corrida del orquestador produce artefactos internos (`manifest_draft.blade.php`, `*_additions`, `styles.blade.php`, `scripts.blade.php` y directorios `sesionN`) que aun no coinciden con la estructura final de una presentacion Laravel consolidada. Esta iteracion define y automatiza la transformacion de dichos artefactos a una estructura lista para integracion.

---

## Objetivo

Agregar una fase de consolidacion posterior a la construccion de sesiones y anterior a las validaciones finales. La fase debe producir una presentacion final con manifest unico, vistas organizadas, assets modulares y referencias Blade coherentes, preservando los artefactos internos necesarios para reanudar o auditar la construccion.

Flujo objetivo:

```text
init -> save-plan -> sesiones -> consolidate -> pytest -> zip
```

## Historias de Usuario y Pruebas

### Historia de Usuario 1 - Manifest Final Consolidado (Prioridad: P1)

Como integrador Laravel, necesito un unico `manifest.blade.php` que extienda el layout de Reveal, agrupe las laminas por sesion y las referencie sin duplicados.

**Prueba Independiente**: Ejecutar una corrida mock y verificar que existe `manifest.blade.php`, contiene una seccion por sesion y cada lamina aparece exactamente una vez.

**Escenarios de Aceptacion**:

1. Dado un plan con varias sesiones, cuando se consolida el proyecto, entonces se genera `manifest.blade.php`.
2. Dado un manifest con adiciones por sesion, cuando se consolida, entonces las adiciones se fusionan en el orden del plan.
3. Dado que una lamina aparece en una adicion y en un borrador, cuando se consolida, entonces solo queda una referencia.
4. El manifest final contiene `@extends`, `@section('title')`, `@section('slides')` y `@endsection`.

### Historia de Usuario 2 - Estructura Final de Vistas (Prioridad: P1)

Como integrador Laravel, necesito que las vistas se ubiquen en `global/` y `sessionN/`, usando la convencion de nombres esperada por las referencias Blade.

**Prueba Independiente**: Verificar que cada vista referenciada por el manifest existe en el directorio final y que no quedan referencias `sesionN`.

**Escenarios de Aceptacion**:

1. Las vistas de sesion se generan bajo `session1/`, `session2/`, etc.
2. Las vistas reutilizables se generan bajo `global/` cuando el plan o la plantilla las requiera.
3. Las referencias usan `sessionN.nombre` y `global.nombre`.
4. Los nombres de archivos de laminas conservan el formato kebab-case.

### Historia de Usuario 3 - Assets Modulares (Prioridad: P1)

Como integrador Laravel, necesito que los estilos y scripts se entreguen bajo `assets/` con includes modulares y rutas consistentes.

**Prueba Independiente**: Verificar la existencia de `assets/styles.blade.php` y `assets/scripts.blade.php`, y que todos sus includes apunten a archivos existentes.

**Escenarios de Aceptacion**:

1. Los estilos finales se ubican bajo `assets/styles.blade.php` y `assets/styles_blade/css/`.
2. Los scripts finales se ubican bajo `assets/scripts.blade.php` y `assets/styles_blade/js/`.
3. Los fragmentos de estilos y scripts se fusionan sin duplicados.
4. Los comportamientos JavaScript conservan su correspondencia con `js_registry.json`.

### Historia de Usuario 4 - Cumplimiento Constitucional (Prioridad: P1)

Como mantenedor del proyecto, necesito que la consolidacion preserve las reglas constitucionales de PRA.

**Escenarios de Aceptacion**:

1. Ninguna vista final contiene atributos `style="..."`.
2. Todo comportamiento interactivo esta acotado a su lamina.
3. Los registries se actualizan exclusivamente mediante `pra_helper.py`.
4. La consolidacion no altera el orden plan-first de las sesiones.
5. La documentacion y mensajes tecnicos nuevos estan en espanol.

### Historia de Usuario 5 - Entregable Final (Prioridad: P1)

Como usuario del orquestador, necesito que `outputs.zip` contenga la presentacion consolidada y no solo los artefactos internos de construccion.

**Escenarios de Aceptacion**:

1. `outputs.zip` se crea dentro del directorio del proyecto.
2. El ZIP contiene `manifest.blade.php`, `assets/` y las vistas finales.
3. El ZIP no contiene otro `outputs.zip`.
4. La fase `zip` solo se ejecuta despues de una consolidacion y validacion exitosas.

## Requisitos Funcionales

- **FR-601**: Se implementa una operacion de consolidacion en `pra_helper.py` y una fase equivalente en `pra_orchestrator.py`.
- **FR-602**: La consolidacion genera un unico `manifest.blade.php` a partir del plan y de las adiciones de manifest.
- **FR-603**: El manifest final agrupa las laminas por sesion, respeta el orden del plan y evita duplicados.
- **FR-604**: El manifest final utiliza sintaxis Blade valida y referencias `global.nombre` o `sessionN.nombre`.
- **FR-605**: Las vistas de sesiones se materializan bajo `sessionN/`; las vistas compartidas bajo `global/`.
- **FR-606**: Los estilos y scripts se materializan bajo `assets/` con entrypoints `assets/styles.blade.php` y `assets/scripts.blade.php`.
- **FR-607**: Los includes de assets solo pueden referenciar archivos existentes dentro del proyecto final.
- **FR-608**: La consolidacion detecta CSS inline y referencias de vistas inexistentes, y falla con diagnostico descriptivo.
- **FR-609**: Los artefactos internos pueden conservarse para auditoria, pero el entregable final debe estar organizado por la estructura consolidada.
- **FR-610**: La fase `consolidate` se ejecuta despues de la ultima sesion y antes de `pytest` y `zip`.
- **FR-611**: `resume` puede reanudar desde una consolidacion fallida sin repetir sesiones ya completadas.
- **FR-612**: El ZIP final excluye su propio archivo y cualquier artefacto de control del orquestador.

## Criterios de Exito

- **SC-601**: Una corrida mock completa genera `manifest.blade.php`, `global/` cuando corresponda, `session1/`, `session2/` y `assets/`.
- **SC-602**: El manifest final no contiene referencias duplicadas ni referencias `sesionN`.
- **SC-603**: Todos los includes de estilos y scripts apuntan a archivos existentes.
- **SC-604**: La validacion rechaza cualquier CSS inline o vista referenciada inexistente.
- **SC-605**: `outputs.zip` contiene la estructura consolidada y no se incluye recursivamente.
- **SC-606**: La suite completa permanece en verde y la cobertura de `pra_helper.py` y `pra_orchestrator.py` es igual o superior a 85%.

## Casos Extremos

- Una adicion de manifest contiene una lamina no presente en el plan: la consolidacion falla y reporta el identificador.
- Dos adiciones definen la misma lamina: se conserva una sola referencia y se registra el conflicto.
- Una sesion no tiene laminas: se genera una seccion vacia o se rechaza segun el contrato, pero nunca se generan referencias inexistentes.
- Un archivo de estilos o scripts esta vacio: el entrypoint puede incluirlo, pero no debe crear includes rotos.
- Una lamina contiene `style="..."`: la consolidacion falla sin empaquetar el proyecto.
- Se ejecuta `consolidate` dos veces: el resultado debe ser idempotente y no duplicar contenido.

## Fuera de Alcance

- Rediseñar visualmente las laminas.
- Copiar automaticamente dependencias globales de la aplicacion Laravel que no pertenezcan al proyecto.
- Corregir retrospectivamente todas las presentaciones ya consolidadas.
- Modificar la constitucion del proyecto.
