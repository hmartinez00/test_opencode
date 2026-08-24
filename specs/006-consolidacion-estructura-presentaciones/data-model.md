# Modelo de Datos: Consolidacion de Presentaciones PRA

## Estructura final del proyecto

```text
<proyecto>/
├── manifest.blade.php
├── global/
│   └── <vista-global>.blade.php
├── session1/
│   └── <lamina>.blade.php
├── session2/
│   └── <lamina>.blade.php
├── assets/
│   ├── styles.blade.php
│   ├── scripts.blade.php
│   ├── styles_blade/
│   │   ├── styles_0.blade.php
│   │   ├── css/
│   │   └── js/
│   └── audio/
├── presentation_plan.json
├── class_registry.json
├── js_registry.json
└── outputs.zip
```

Los artefactos internos `manifest_additions/`, `styles_additions/` y `scripts_additions/` pueden permanecer fuera del entregable final o en una zona de construccion definida por el contrato de implementacion.

## Entidad `ConsolidationReport`

```json
{
  "ok": true,
  "manifest": "manifest.blade.php",
  "sesiones": [1, 2],
  "laminas_materializadas": 3,
  "vistas_globales": 0,
  "includes_css": 2,
  "includes_js": 1,
  "duplicados": [],
  "referencias_inexistentes": [],
  "css_inline": [],
  "errores": []
}
```

## Reglas de normalizacion

| Entrada | Salida |
|---|---|
| `sesion1/` | `session1/` |
| `sesion2.nombre` | `session2.nombre` |
| `manifest_draft.blade.php` | `manifest.blade.php` |
| `styles.blade.php` | `assets/styles.blade.php` |
| `scripts.blade.php` | `assets/scripts.blade.php` |
| `styles_additions/sesion1_styles.css` | fragmento bajo `assets/styles_blade/css/` |
| `scripts_additions/sesion1_scripts.js` | fragmento bajo `assets/styles_blade/js/` |
| `{-- comentario --}` | `{{-- comentario --}}` |

## Reglas de identidad

- La identidad de una lamina es `(numero_sesion, id_kebab_case)`.
- El orden de salida se determina por `numero` y `orden` en `presentation_plan.json`.
- Una identidad solo puede aparecer una vez en el manifest final.
- Un include de asset se identifica por su ruta Blade normalizada.
- Una referencia de vista es valida solo si existe el archivo Blade correspondiente.

## Estado de la fase

La fase `consolidate` usa la misma forma de estado que las demas fases:

```json
{
  "estado": "pendiente|en_curso|completada|fallida",
  "intentos": 0,
  "ultimo_error": null,
  "validaciones": {
    "manifest_ok": false,
    "estructura_ok": false,
    "sin_css_inline": false,
    "referencias_ok": false,
    "assets_ok": false
  }
}
```

## Contenido del ZIP

El ZIP debe incluir el producto consolidado y los archivos de proyecto definidos por el contrato. Nunca debe incluir:

- El propio `outputs.zip`.
- `orchestration_state.json`.
- `orchestration_log.txt`.
