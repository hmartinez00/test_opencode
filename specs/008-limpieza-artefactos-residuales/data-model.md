# Modelo de Datos: Limpieza de Artefactos Residuales con Proteccion del Lote

## Estado final del proyecto tras la limpieza

```text
<base>/<carpeta_snake_case>/
├── manifest.blade.php          # Lote protegido
├── presentation_plan.json      # Lote protegido
├── class_registry.json         # Lote protegido
├── js_registry.json            # Lote protegido
├── session[N]/                 # Lote protegido (vistas finales referenciadas por el manifest)
├── assets/                     # Lote protegido (entry points + fragmentos CSS/JS finales)
└── backup/
    └── fuente/                 # Respaldo de la fuente interna (re-consolidable)
        ├── sesion[N]/          # Laminas fuente originales
        ├── styles_additions/   # CSS aislado por sesion
        ├── scripts_additions/  # JS aislado por sesion
        ├── manifest_additions/ # Fragmentos <x-slide> por sesion
        ├── manifest_draft.blade.php
        └── presentation_plan.json
```

## Lote protegido (whitelist de conservacion)

| Ruta | Tipo | Regla |
|---|---|---|
| `manifest.blade.php` | archivo | Obligatorio |
| `presentation_plan.json` | archivo | Obligatorio |
| `class_registry.json` | archivo | Obligatorio |
| `js_registry.json` | archivo | Obligatorio |
| `session[N]/` | directorio | Obligatorio (al menos una con laminas) |
| `assets/` | directorio | Obligatorio |

## Artefactos residuales (a respaldar y/o eliminar)

| Ruta | Accion |
|---|---|
| `sesion[N]/` | Respaldar en `backup/fuente/sesion[N]/` y eliminar del dir |
| `manifest_draft.blade.php` | Respaldar en `backup/fuente/` y eliminar del dir |
| `manifest_additions/` | Respaldar en `backup/fuente/` y eliminar del dir |
| `styles.blade.php` | Eliminar del dir |
| `scripts.blade.php` | Eliminar del dir |
| `styles_additions/` | Respaldar en `backup/fuente/` y eliminar del dir |
| `scripts_additions/` | Respaldar en `backup/fuente/` y eliminar del dir |
| `outputs.zip` | Eliminar del dir (no se respalda) |

## Reporte JSON de `limpiar`

```json
{
  "ok": true,
  "backup": [
    "backup/fuente/sesion1/que-es-docker.blade.php",
    "backup/fuente/styles_additions/sesion1_styles.css",
    "..."
  ],
  "eliminados": [
    "sesion1",
    "manifest_draft.blade.php",
    "styles.blade.php",
    "scripts.blade.php",
    "styles_additions",
    "scripts_additions",
    "manifest_additions",
    "outputs.zip"
  ],
  "protegidos": [
    "manifest.blade.php",
    "presentation_plan.json",
    "class_registry.json",
    "js_registry.json",
    "session1",
    "assets"
  ]
}
```

## Codigos de salida del comando `limpiar`

| Codigo | Significado |
|---|---|
| `0` | Limpieza exitosa |
| `1` | Proyecto no encontrado |
| `2` | Lote protegido incompleto (puerta abortada, no se borro nada) |
| `3` | Error de lectura/escritura de archivos |

## Estado de orquestacion (fases)

El hash de fases en `nuevo_estado()` pasa de:

```json
{ "init", "save_plan", "sesiones", "consolidate", "pytest", "zip" }
```

a:

```json
{ "init", "save_plan", "sesiones", "consolidate", "pytest", "cleanup" }
```

## Normalizacion retrocompatible de `resume`

Al cargar un estado previo con la clave `"zip"`:

| Estado de `zip` | Mapeo a `cleanup` |
|---|---|
| `completada` | `completada` (no se re-ejecuta) |
| `pendiente` | `pendiente` (se limpia al reanudar) |
| `en_curso` | `pendiente` (se limpia al reanudar) |
| `fallida` | `fallida` (se registra pero no bloquea) |

La clave `"zip"` se elimina del diccionario de fases tras normalizar.
