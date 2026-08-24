# Modelo de Datos: 004-subdirectorio-maestro-proyectos-pra

**Fecha**: 2026-08-24

---

## Cambio de Ubicacion (sin cambios de esquema)

Esta iteracion NO agrega ni modifica entidades de datos. Solo cambia la **ubicacion fisica** de los artefactos existentes:

### Antes (iteraciones 001-003)

```text
<workspace_root>/
├── <carpeta_snake_case>/          <-- proyecto en la raiz
│   ├── presentation_plan.json
│   ├── class_registry.json
│   ├── js_registry.json
│   ├── manifest_draft.blade.php
│   ├── styles.blade.php
│   ├── scripts.blade.php
│   ├── *_additions/
│   └── sesion[N]/*.blade.php
└── outputs.zip                    <- generado por zip en la raiz
```

### Despues (iteracion 004)

```text
<workspace_root>/
├── output_projects/               <-- subdirectorio maestro (default; PRA_OUTPUT_DIR lo reemplaza)
│   ├── <carpeta_snake_case>/      <-- mismo arbol interno, intacto
│   │   ├── presentation_plan.json
│   │   ├── class_registry.json
│   │   ├── js_registry.json
│   │   ├── manifest_draft.blade.php
│   │   ├── styles.blade.php
│   │   ├── scripts.blade.php
│   │   ├── styles_additions/
│   │   ├── scripts_additions/
│   │   ├── manifest_additions/
│   │   └── sesion[N]/ *.blade.php
│   └── outputs.zip                <- entregable, dentro del maestro
├── orchestration_state.json       <- sin cambios de esquema; rutas relativas nuevas
└── orchestration_log.txt          <- sin cambios
```

## Campos Afectados por el Cambio de Ruta

| Artefacto | Campo / Detalle | Antes | Despues |
|---|---|---|---|
| Salida JSON `save-plan` | `proyecto` | `<cwd>/<carpeta>` | `<cwd>/output_projects/<carpeta>` |
| Salida JSON `save-plan` | `archivos_creados[]` | rutas bajo `<cwd>/<carpeta>` | rutas bajo `<cwd>/output_projects/<carpeta>` |
| `orchestration_state.json` | referencias al directorio de proyecto | `<carpeta>` en raiz | `output_projects/<carpeta>` |

## Invariantes que NO Cambian

- Esquema de `presentation_plan.json`, `class_registry.json`, `js_registry.json` (ver data-model 001).
- Estructura interna completa del proyecto (sesiones, adiciones, manifest).
- Esquema de `orchestration_state.json` y codigos de salida del orquestador.
- Exclusiones del zip (artefactos de orquestacion fuera del entregable).

## Variable de Entorno Nueva

| Variable | Default | Efecto |
|---|---|---|
| `PRA_OUTPUT_DIR` | `output_projects` | Reemplaza el nombre del subdirectorio maestro para motor y orquestador en esa ejecucion. Debe ser una ruta relativa o absoluta valida; si es un archivo existente, `save-plan` aborta con error claro. |
