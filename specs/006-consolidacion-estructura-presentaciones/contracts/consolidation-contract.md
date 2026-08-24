# Contrato CLI: Consolidacion de Presentaciones PRA

## Comando

```text
python pra_helper.py consolidate
```

El comando opera sobre el proyecto activo localizado mediante `PRA_OUTPUT_DIR` y sus fallbacks vigentes.

## Salida exitosa

- Codigo de salida `0`.
- Se genera `manifest.blade.php`.
- Se generan los directorios finales `global/`, `sessionN/` y `assets/` segun corresponda.
- Se imprime un reporte JSON con `ok: true` y los conteos de materializacion.

Ejemplo:

```json
{
  "ok": true,
  "manifest": "C:\\laragon\\www\\product_samples\\slides\\intro_docker\\manifest.blade.php",
  "laminas_materializadas": 3,
  "errores": []
}
```

## Salida rechazada

El comando debe devolver codigo no cero y un reporte descriptivo cuando ocurra cualquiera de estas condiciones:

- No existe un proyecto activo o `presentation_plan.json` es ilegible.
- Falta una lamina declarada en el plan.
- Hay referencias de vista inexistentes.
- Se detecta CSS inline.
- Existen duplicados no resolubles.
- Un include de estilos o scripts apunta a un archivo inexistente.

## Contrato del manifest final

El archivo debe:

- Extender el layout Reveal requerido por la aplicacion.
- Definir una seccion de laminas.
- Contener una seccion por sesion en orden numerico.
- Referenciar cada lamina una sola vez.
- Usar `global.nombre` y `sessionN.nombre`.
- Incluir assets mediante entrypoints bajo `assets/`.
- No contener comentarios con la forma invalida `{-- ... --}`.

## Contrato de assets

Los entrypoints obligatorios son:

```text
assets/styles.blade.php
assets/scripts.blade.php
```

Todos los includes deben resolverse dentro de:

```text
assets/styles_blade/css/
assets/styles_blade/js/
```

## Contrato del orquestador

La fase `consolidate` debe:

1. Ejecutarse una vez completadas todas las sesiones del plan.
2. Registrar estado e intentos en `orchestration_state.json`.
3. Registrar auditoria en `orchestration_log.txt`.
4. Impedir `pytest` y `zip` ante un resultado invalido.
5. Ser reanudable mediante `python pra_orchestrator.py resume`.

## Contrato del ZIP

`outputs.zip` debe ubicarse en `<project_dir>/outputs.zip` y excluir:

- Su propia entrada.
- `orchestration_state.json`.
- `orchestration_log.txt`.

Debe contener la estructura consolidada y no depender de `manifest_draft.blade.php` como punto de entrada.
