# Plan de Implementacion: Calidad de Salida de Presentaciones PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Decisiones**: [research.md](./research.md) | **Contrato**: [contracts/cli-contract.md](./contracts/cli-contract.md)

## 1. Enfoque TDD (red-green-refactor)

Esta iteracion se implementa con desarrollo guiado por pruebas:

1. **Rojo**: Se escriben primero las pruebas que reproducen los problemas P1-P6 (deben fallar con el codigo actual).
2. **Verde**: Se implementan las correcciones en `pra_helper.py` y `pra_orchestrator.py` hasta que pasen.
3. **Refactor**: Se limpia el codigo sin cambiar comportamiento; la suite completa debe seguir en verde.

El detalle de cada prueba se documenta en [test_plan.md](./test_plan.md).

## 2. Arquitectura propuesta

Los cambios son puntuales sobre el motor y el orquestador; no se modifica la estructura general del flujo.

```text
pra_helper.py
  ├── cmd_process_session: + lectura por --respuesta-file (D4)
  ├── find_project_dir:    + respeto de PRA_ACTIVE_PROJECT (D5)
  ├── _consolidate_project:
  │     ├── interpolacion {$presentation->folder_name} (D1)
  │     ├── envoltura <style> en fragmentos CSS (D2)
  │     ├── envoltura <script> en fragmentos JS (D3)
  │     └── data-title legible (D6)
  └── main: + flag --respuesta-file

pra_orchestrator.py
  ├── run_helper: + archivo temporal para respuestas largas (D4)
  └── buscar_proyecto: + respeto de PRA_ACTIVE_PROJECT (D5)
```

## 3. Cambios en `pra_helper.py`

### 3.1 Interpolacion de ruta (P1)
- En `_consolidate_project()`, lineas de `assets/styles.blade.php` y `assets/scripts.blade.php`: reemplazar `{{{{$presentation->folder_name}}}}` por `{$presentation->folder_name}`.
- En las lineas `@include("presentation.slides.{{$presentation->folder_name}}.assets.styles")` y `...assets.scripts")` del manifest: reemplazar `{{$presentation->folder_name}}` por `{$presentation->folder_name}`.

### 3.2 Envoltura de fragmentos (P2 y P3)
- Al escribir cada `assets/styles_blade/css/*.blade.php`: envolver con `<style>`/`</style>`.
- Al escribir cada `assets/styles_blade/js/*.blade.php`: envolver con `<script>`/`</script>`.
- Guarda defensiva `startswith("<style>")`/`startswith("<script>")` para no duplicar la envoltura.

### 3.3 Respuesta LLM por archivo (P4)
- `cmd_process_session()`: aceptar `args.respuesta_file` y leer la respuesta desde el archivo si esta presente. Precedencia: archivo sobre posicional.
- `main()`: registrar `--respuesta-file` en el parser de `process-session`.

### 3.4 Seleccion de proyecto activo (P5)
- `find_project_dir()`: leer `PRA_ACTIVE_PROJECT`; si la carpeta indicada existe bajo el base, priorizarla; si no, fallback al comportamiento actual.

### 3.5 Titulo legible (P6)
- Nueva funcion `titulo_legible(id_kebab_case) -> str`.
- `_consolidate_project()`: `data_title = lamina.get("data_title") or lamina.get("titulo") or titulo_legible(slide_id)`.

## 4. Cambios en `pra_orchestrator.py`

- `run_helper()`: detectar argumentos largos (> umbral) y, para el comando `process-session`, escribir la respuesta a un archivo temporal y pasar `--respuesta-file <ruta>`; limpiar el temporal en `finally`.
- `buscar_proyecto()`: replicar la logica de `PRA_ACTIVE_PROJECT`.

## 5. Validacion estructural

Se actualizara la validacion post-consolidacion para verificar:

- Interpolacion valida (`{$presentation->folder_name}`) en manifest y assets.
- Fragmentos CSS/JS envueltos.
- Idempotencia del `consolidate`.
- `data-title` legible en el manifest.

## 6. Pruebas TDD

Ver [test_plan.md](./test_plan.md) para la lista completa. Resumen por ubicacion:

- `tests/unit/`: `titulo_legible`, envoltura, interpolacion, seleccion por env.
- `tests/integration/`: `process-session --respuesta-file` (corto y largo), `consolidate` idempotente, `PRA_ACTIVE_PROJECT` con 2 proyectos.
- `tests/constitutional/`: estructura de salida, escritura exclusiva via `pra_helper.py`, ZIP autocontenido.

## 7. Documentacion a actualizar despues de la implementacion

- `README.md`: documentar `--respuesta-file` y `PRA_ACTIVE_PROJECT`.
- `AGENTS.md`: actualizar el contrato CLI y las rutas/entorno.
- `specs/001.../contracts/cli-contract.md` y `specs/003.../contracts/orchestrator-contract.md`: reflejar los nuevos parametros.
- `SESION_PRA_RESUMEN.md`: registrar la iteracion 007.

## 8. Secuencia de implementacion

1. Escribir pruebas rojas (test_plan.md -> archivos en `tests/`).
2. Corregir interpolacion (P1).
3. Envolver fragmentos CSS/JS (P2, P3).
4. Implementar `--respuesta-file` (P4) en `pra_helper.py`.
5. Adaptar `run_helper` del orquestador (P4).
6. Implementar `PRA_ACTIVE_PROJECT` (P5) en ambos.
7. Implementar `titulo_legible` (P6).
8. Refactorizar y ejecutar la suite + cobertura.

## 9. Criterios de finalizacion

- Suite completa en verde.
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
- `outputs.zip` renderiza en Laravel sin retoques manuales.
