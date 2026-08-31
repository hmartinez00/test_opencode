# Plan de Implementacion: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Decisiones**: [research.md](./research.md) | **Contrato**: [contracts/cli-contract.md](./contracts/cli-contract.md)

## 1. Enfoque TDD (red-green-refactor)

Esta iteracion se implementa con desarrollo guiado por pruebas:

1. **Rojo**: Se escriben primero las pruebas que reproducen la necesidad de limpieza y la omision de `zip` (deben fallar con el codigo actual, que deja residuos y genera `outputs.zip`).
2. **Verde**: Se implementan el comando `limpiar` en `pra_helper.py`, la fase `cleanup` y la omision de `zip` en `pra_orchestrator.py`, hasta que pasen.
3. **Refactor**: Se limpia el codigo sin cambiar comportamiento; la suite completa debe seguir en verde.

El detalle de cada prueba se documenta en [test_plan.md](./test_plan.md).

## 2. Arquitectura propuesta

```text
pra_helper.py
  ├── cmd_limpiar:            + nuevo comando (T812)
  ├── _limpiar_proyecto:      + respaldo fuente + whitelist + eliminacion de residuos (P-1)
  └── main:                   + subparser 'limpiar'

pra_orchestrator.py
  ├── nuevo_estado:           fases 'zip' -> 'cleanup'
  ├── fase_cleanup(estado):   + invoca run_helper('limpiar')
  ├── ejecutar_desde_estado:  reemplaza fase_zip por fase_cleanup
  └── transiciones/status:    reflejan la fase 'cleanup'
```

## 3. Cambios en `pra_helper.py`

### 3.1 Nuevo comando `limpiar`
- `cmd_limpiar(args)`: localiza el proyecto activo (`find_project_dir`), invoca `_limpiar_proyecto(project_dir)` y emite reporte JSON.
- `_limpiar_proyecto(project_dir) -> dict` con la logica central:

**Fase A - Respaldo de la fuente** (`backup/fuente/`):
1. Crear `backup/fuente/`.
2. Copiar (o mover) `sesion[N]/` -> `backup/fuente/sesion[N]/`.
3. Copiar `styles_additions/`, `scripts_additions/`, `manifest_additions/` y `manifest_draft.blade.php` a `backup/fuente/`.
4. Copiar `presentation_plan.json` (copia de seguridad del contexto).
5. Sobrescribir de forma idempotente (eliminar previo si existe para evitar acumulacion).

**Fase B - Puerta protectora del lote**:
1. Verificar que todos los entregables del lote existen: `manifest.blade.php`, `presentation_plan.json`, `class_registry.json`, `js_registry.json`, al menos un `session[N]/` con sus `.blade.php` y `assets/`.
2. Si falta alguno, retornar error (sin borrar nada).

**Fase C - Eliminacion de residuos**:
1. `shutil.rmtree` sobre: `sesion[N]/`, `styles_additions/`, `scripts_additions/`, `manifest_additions/`.
2. `unlink` (si existe) sobre: `manifest_draft.blade.php`, `styles.blade.php`, `scripts.blade.php`, `outputs.zip`.

**Fase D - Reporte**:
1. `{"ok": bool, "backup": [...], "eliminados": [...], "protegidos": [...]}`.

### 3.2 Parser y registro
- `main()`: registrar subparser `limpiar` (sin argumentos adicionales; usa `find_project_dir`).

## 4. Cambios en `pra_orchestrator.py`

### 4.1 Estado de fases
- En `nuevo_estado()`, reemplazar `"zip": _fase_nueva()` por `"cleanup": _fase_nueva()`.

### 4.2 Nueva fase `cleanup`
- Renombrar/adaptar `fase_zip` -> `fase_cleanup(estado)`:
  1. `iniciar_fase(fase)`.
  2. `codigo, out, err = run_helper("limpiar")`.
  3. Validar que el reporte `ok` sea verdadero; si no, `fallar_fase` y devolver `EXIT_VALIDACION`.
  4. `completar_fase(fase)` y devolver `EXIT_OK`.

### 4.3 Pipeline
- En `ejecutar_desde_estado`, reemplazar el bloque que invocaba `fase_zip` por `fase_cleanup`.
- Ajustar el mensaje final `[FIN]` (ya no referencia `outputs.zip`).

### 4.4 Retrocompatibilidad de `resume`
- Si un estado cargado aun contiene la clave `"zip"`:
  - Si `zip@completada` -> tratar como `cleanup@completada` (no re-ejecutar).
  - Si `zip@pendiente/en_curso/fallida` -> marcar `cleanup` pendiente y limpiar de nuevo o pasar de largo segun criterio.
- Normalizar el diccionario de fases al cargar (`cargar_estado`/inicio de `ejecutar_desde_estado`).

### 4.5 `status` y transiciones
- Asegurar que la tabla de fases y `TRANSICIONES_VALIDAS` contemplen `cleanup`.

## 5. `cmd_zip` (utilidad manual)

- `cmd_zip` se conserva como utilidad CLI manual, pero **no se invoca** en el flujo automatico.
- No se elimina el codigo (evita romper la suite y la documentacion existente), pero deja de ser parte del pipeline.

## 6. Validacion estructural post-cleanup

Se verificara despues de `limpiar` (y en el orquestador tras `cleanup`):

- Solo existe lote + `backup/fuente/` en el directorio del proyecto.
- Todos los `.blade.php` que el `manifest.blade.php` referencia via `view="sessionN...."` existen en `session[N]/`.
- No existen `sesion[N]/` ni `outputs.zip`.
- `backup/fuente/` contiene la fuente re-consolidable.

## 7. Pruebas TDD

Ver [test_plan.md](./test_plan.md) para la lista completa. Resumen por ubicacion:

- `tests/unit/`: `_limpiar_proyecto` (whitelist, respaldo, eliminacion, idempotencia, puerta de aborto).
- `tests/integration/`: comando `limpiar` CLI; actualizacion de `test_cli_orchestrator_run_mock.py` y `test_cli_orchestrator_resume.py` (sin `outputs.zip`, sin `zip`, con `cleanup` y `backup/`).
- `tests/constitutional/`: el lote protegido queda intacto tras la limpieza; el respaldo conserva la fuente.

## 8. Documentacion a actualizar despues de la implementacion

- `README.md`: documentar el comando `limpiar` y la salida final (sin `outputs.zip`).
- `AGENTS.md`: actualizar el flujo (fases) y el contrato CLI/entorno.
- `specs/001.../contracts/cli-contract.md` y `specs/003.../contracts/orchestrator-contract.md`: reflejar `limpiar` y la fase `cleanup`.
- `SESION_PRA_RESUMEN.md`: registrar la iteracion 008 (209+ -> conteo final).

## 9. Secuencia de implementacion

1. Escribir pruebas rojas (test_plan.md -> archivos en `tests/`).
2. Implementar `_limpiar_proyecto` + `cmd_limpiar` + subparser en `pra_helper.py`.
3. Cambiar estado de fases (`zip` -> `cleanup`), `fase_cleanup` y pipeline en `pra_orchestrator.py`.
4. Implementar retrocompatibilidad de `resume` para estados con `zip`.
5. Actualizar tests de integracion afectados (run_mock y resume).
6. Refactorizar y ejecutar la suite + cobertura.

## 10. Criterios de finalizacion

- Suite completa en verde.
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
- Una corrida mock termina dejando el directorio con solo el lote protegido + `backup/fuente/`.
- No se genera `outputs.zip` en el flujo automatico.
