# Plan de Implementacion: Consolidacion de Presentaciones PRA

**Fecha**: 2026-08-24

## 1. Arquitectura propuesta

La consolidacion se implementara como una operacion de `pra_helper.py`, invocada por una fase `consolidate` de `pra_orchestrator.py`.

```text
presentation_plan.json
manifest_additions/
styles_additions/
scripts_additions/
sesionN/
        |
        v
pra_helper.py consolidate
        |
        v
manifest.blade.php + global/ + sessionN/ + assets/
```

## 2. Cambios en `pra_helper.py`

- Definir la funcion de consolidacion y sus helpers de normalizacion.
- Leer el plan y determinar sesiones y laminas en orden estable.
- Crear `manifest.blade.php` con layout, secciones y referencias unicas.
- Materializar vistas bajo `sessionN/` y `global/`.
- Crear `assets/styles.blade.php` y `assets/scripts.blade.php`.
- Convertir adiciones de estilos y scripts en fragmentos Blade modulares.
- Validar sintaxis de comentarios, referencias de vistas y CSS inline.
- Hacer la operacion idempotente.
- Exponer el comando CLI `consolidate` con salida JSON de reporte.

## 3. Cambios en `pra_orchestrator.py`

- Agregar la fase `consolidate` al estado inicial.
- Ejecutarla despues de completar todas las sesiones.
- Invocar `pra_helper.py consolidate` mediante `run_helper`.
- Interpretar el reporte y detener la corrida ante errores estructurales.
- Permitir que `resume` reintente solo la consolidacion fallida.
- Ejecutar `pytest` y `zip` unicamente despues de consolidar correctamente.
- Registrar intentos, duracion, diagnostico y resultado en el log existente.

## 4. Validacion estructural

Crear validadores para:

- Manifest unico y no vacio.
- Secciones y orden de sesiones.
- Referencias de vistas existentes.
- Convencion `sessionN` y `global`.
- Entry points de assets.
- Includes existentes.
- Ausencia de CSS inline.
- Ausencia de duplicados.
- ZIP autocontenido sin archivos de control.

## 5. Pruebas

Actualizar o agregar pruebas unitarias, de integracion y constitucionales para todos los requisitos FR-601 a FR-612. Las pruebas deben usar `tmp_path` y aislar `PRA_OUTPUT_DIR` cuando invoquen el CLI.

## 6. Documentacion

Actualizar despues de la implementacion:

- `README.md` con el nuevo paso de consolidacion.
- `AGENTS.md` con la distincion entre artefactos internos y salida final.
- `SESION_PRA_RESUMEN.md` con la iteracion 006.
- Quickstart y contrato de consolidacion.

## 7. Secuencia de implementacion

1. Implementar modelo y helpers de normalizacion.
2. Implementar consolidacion del manifest.
3. Implementar consolidacion de assets.
4. Implementar materializacion de directorios finales.
5. Integrar la fase en el orquestador.
6. Agregar validadores y pruebas.
7. Actualizar documentacion.
8. Ejecutar suite completa y corrida mock E2E.
