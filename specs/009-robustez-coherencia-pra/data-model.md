# Modelo de Datos: Robustez y Coherencia del Flujo PRA

## Reporte de coherencia de consolidacion

El comando `consolidate` agrega un bloque `coherencia` a su JSON de salida. Cuando existen incoherencias bloqueantes, `ok` es `false` y el manifest NO se genera incompleto.

```json
{
  "ok": false,
  "manifest": "manifest.blade.php",
  "error": "Incoherencia plan-vs-laminas",
  "coherencia": {
    "huerfanas": [
      {"sesion": 1, "id": "conversion-tipos", "sugerencia": "Lamina escrita en sesion1/ pero no declarada en el plan. Declarala o eliminala."}
    ],
    "faltantes": [
      {"sesion": 1, "id": "portada", "sugerencia": "Lamina declarada en el plan pero no escrita en sesion1/. Genera sesion1/portada.blade.php."}
    ],
    "duplicadas": [
      {"sesion": 1, "id": "portada", "sugerencia": "id declarado mas de una vez en el plan. Usa ids unicos."}
    ]
  },
  "sesiones": [1],
  "laminas_materializadas": 0,
  "errores": []
}
```

Caso coherente (sin incoherencias):

```json
{
  "ok": true,
  "manifest": "manifest.blade.php",
  "coherencia": {"huerfanas": [], "faltantes": [], "duplicadas": []},
  "sesiones": [1],
  "laminas_materializadas": 12,
  "errores": []
}
```

### Reglas del reporte

- `huerfanas`: archivos `sesion[N]/*.blade.php` cuyo `stem` no esta en los `id_kebab_case` de esa sesion en el plan.
- `faltantes`: `id_kebab_case` del plan sin archivo `sesion[N]/<id>.blade.php`.
- `duplicadas`: ids repetidos en todo el plan (deduplicados en el reporte).
- El calificador "bloqueante" aplica cuando cualquiera de las tres listas no es vacia.

## Advertencias de `save-plan`

El JSON de salida de `save-plan` incorpora el campo `advertencias`:

```json
{
  "status": "exito",
  "proyecto": "...",
  "advertencias": [
    "class_registry.json y js_registry.json quedarian vacios: incluye las Partes 2 y 3 del plan (registros CSS/JS iniciales).",
    "La lamina 'variables-tipos-datos' (sesion 1) no declara insumos."
  ],
  "archivos_creados": ["..."]
}
```

### Umbral `PRA_PLAN_ESTRICTO`

- Sin la variable (default): las advertencias no bloquean; el plan se guarda.
- `PRA_PLAN_ESTRICTO=1`: las advertencias de "registros vacios" y "lamina sin insumos" se tratan como errores bloqueantes; `save-plan` aborta y no guarda.

```json
{
  "status": "error",
  "error": "Plan incompleto (PRA_PLAN_ESTRICTO=1)",
  "advertencias": ["..."],
  "codigo": "PLAN_INCOMPLETO_ESTRICTO"
}
```

## Estado de orquestacion - diagnostico del backend

Cuando el backend `opencode` no se resuelve, el estado de orquestacion registra un error estructurado en la fase correspondiente bajo `ultimo_error`:

```json
{
  "backend": "opencode",
  "error": "BACKEND_NO_DISPONIBLE",
  "detalle": {
    "banderas": [],
    "binarios_intentados": [
      "C:\\Users\\HP\\.opencode\\bin\\opencode.exe",
      "C:\\Users\\HP\\AppData\\Roaming\\npm\\opencode.cmd"
    ],
    "path_relevante": "C:\\Windows\\System32;...;"
  }
}
```

## Seleccion del proyecto activo

### Flujo de seleccion (con deteccion de ambiguedad)

```text
PRA_ACTIVE_PROJECT definida y valida?
  SI  -> usar ese proyecto (determinista). FIN
  NO  ->
    Enumerar candidatos validos en <base>/ (excluyendo backup/, themes/, etc.)
    count == 0 -> None (sin proyecto)
    count == 1 -> usar el unico (sin advertencia)
    count > 1  -> emitir ADVERTENCIA en stderr listando candidatos y aplicar el criterio por defecto
```

### Directorios excluidos de la enumeracion de candidatos

| Nombre | Motivo |
|---|---|
| `backup` | Respaldo, no es un proyecto |
| `themes` | Temas institucionales, no un proyecto PRA |
| `__pycache__`, `.git`, `node_modules` | No relevantes |
| cualquier directorio sin `presentation_plan.json` | No es un proyecto generado |

## Reporte del backend (orquestador)

El backend `OpenCodeBackend` usa `_resolver_binario_opencode()` que retorna la primera ruta existente/ejecutable o `None`:

```json
{
  "ok": false,
  "backend": "opencode",
  "codigo": "BACKEND_NO_DISPONIBLE",
  "rutas_intentadas": ["...", "..."],
  "mensaje": "No se encontro el binario 'opencode'. Verifica la instalacion o agrega C:\\Users\\HP\\.opencode\\bin al PATH."
}
```

## Compatibilidad de esquemas (no cambios destructivos)

- `presentation_plan.json`, `class_registry.json`, `js_registry.json` y `manifest.blade.php` mantienen su esquema actual.
- `save-plan` sigue aceptando planes con nombres de campo de plantilla (`nro`, `folder_name`, `titulo_sesion`, `objetivos`, `id`) o del data-model (`numero`, `carpeta_snake_case`, `titulo`, `objetivo_pedagogico`, `id_kebab_case`); la normalizacion es identica.
- Los reportes JSON nuevos (`coherencia`, `advertencias`, `BACKEND_NO_DISPONIBLE`) son aditivos; no rompen consumidores previos.
