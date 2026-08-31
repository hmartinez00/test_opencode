# Contrato CLI: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

## `pra_helper.py limpiar`

Elimina los artefactos residuales del proyecto activo preservando el lote protegido y respaldando la fuente en `backup/fuente/`.

```text
python pra_helper.py limpiar
```

### Semantica

1. Localiza el proyecto activo (`find_project_dir`, respeta `PRA_ACTIVE_PROJECT` y `PRA_OUTPUT_DIR`).
2. Verifica la integridad del lote protegido (puerta protectora).
3. Si el lote esta incompleto: aborta SIN borrar nada, imprime reporte con `ok: false` y sale con codigo 2.
4. Si el lote esta completo: respalda la fuente en `backup/fuente/`, elimina los residuos e imprime el reporte.

### Codigos de salida

| Codigo | Significado |
|---|---|
| `0` | Limpieza exitosa |
| `1` | Proyecto no encontrado |
| `2` | Lote protegido incompleto (puerta abortada, no se borro nada) |
| `3` | Error de lectura/escritura de archivos |

### Salida (stdout, JSON)

```json
{
  "ok": true,
  "backup": ["backup/fuente/sesion1/que-es-docker.blade.php", "..."],
  "eliminados": ["sesion1", "manifest_draft.blade.php", "outputs.zip", "..."],
  "protegidos": ["manifest.blade.php", "session1", "assets", "..."]
}
```

### Ejemplos

```powershell
python pra_helper.py limpiar
# OK: limpieza exitosa, proyecto con solo lote + backup/fuente/
```

---

## Fase `cleanup` en `pra_orchestrator.py`

### `run <documento>`

```text
python pra_orchestrator.py run <documento> [--backend mock|opencode] [--max-retries N]
```

Nueva secuencia de fases:

```text
init -> save-plan -> sesiones -> consolidate -> pytest -> cleanup -> [FIN]
```

La fase `cleanup` invoca `run_helper("limpiar")`, valida el reporte `ok: true` y, si falla, marca la fase `fallida` y devuelve `EXIT_VALIDACION`. La fase `zip` ya NO forma parte del pipeline.

### `resume`

```text
python pra_orchestrator.py resume
```

Al cargar un estado que aun contiene la fase `zip`:
- `zip@completada` -> se mapea a `cleanup@completada` (no se re-ejecuta).
- `zip@pendiente/en_curso` -> se mapea a `cleanup@pendiente` (se limpia al reanudar).
- `zip@fallida` -> se registra como `cleanup@fallida` sin corromper la corrida.

La clave `"zip"` se elimina del diccionario de fases tras normalizar.

### `status`

```text
python pra_orchestrator.py status
```

La tabla de fases muestra `cleanup` como fase final (ya no `zip`). Los estados previos con `zip` se muestran normalizados como `cleanup`.

### Codigos de salida de `run`/`resume`

| Codigo | Significado |
|---|---|
| `0` | Flujo completo exitoso (incluye `cleanup`) |
| `2` | Error de orquestacion / validacion (incluye `cleanup` fallida) |
| Otros | Se conservan los codigos documentados en `specs/003...` para el resto de fases |
