# Modelo de Datos y Estructura de Rutas: Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento describe el impacto de la Iteracion 005 en el modelo de datos (principalmente rutas y configuracion) y la estructura de archivos del proyecto Presentation Automator (PRA).

---

## 1. Arbol de Directorios Modificado

La estructura del arbol de directorios de los proyectos generados cambia para reflejar la nueva ruta base por defecto y la ubicacion autocontenida de `outputs.zip`.

```text
C:\laragon\www\test_opencode\                  <-- Raiz del repositorio
├── ...
└── [directorio_maestro_resuelto]/             <-- C:\laragon\www\product_samples\slides por defecto (configurable via PRA_OUTPUT_DIR)
    └── [nombre_proyecto_snake_case]/          <-- Directorio generado del proyecto activo
        ├── presentation_plan.json
        ├── class_registry.json
        ├── js_registry.json
        ├── manifest_draft.blade.php
        ├── styles.blade.php
        ├── scripts.blade.php
        ├── styles_additions/
        ├── scripts_additions/
        ├── manifest_additions/
        ├── outputs.zip                      <-- NUEVA UBICACION del entregable
        └── sesion[N]/
            └── [slide-id-kebab-case].blade.php
```

**Cambios Clave**:
- El `[directorio_maestro_resuelto]` ahora apunta por defecto a `C:\laragon\www\product_samples\slides`.
- El archivo `outputs.zip` se mueve del directorio maestro a `[nombre_proyecto_snake_case]/outputs.zip`.

---

## 2. Constantes y Variables de Configuracion

### Nueva Constante `DEFAULT_OUTPUT_BASE_DIR`

- **Ubicacion**: `pra_helper.py` (y replicada en `pra_orchestrator.py` para desacoplamiento)
- **Tipo**: `pathlib.Path`
- **Valor por defecto**: `Path(r"C:\laragon\www\product_samples\slides")`
- **Proposito**: Define la ruta base predeterminada para todos los proyectos generados cuando `PRA_OUTPUT_DIR` no esta configurada.

### Variable de Entorno `PRA_OUTPUT_DIR` (Preexistente, con nuevo impacto)

- **Tipo**: `string` (ruta)
- **Valor**: Cualquier ruta de directorio valida (relativa o absoluta)
- **Proposito**: Sobreescribe `DEFAULT_OUTPUT_BASE_DIR`. Si esta definida, esta tiene maxima precedencia.

---

## 3. Cambios en la Representacion de Rutas (JSON Output)

Las rutas reportadas en las salidas JSON de `pra_helper.py` (ej. `save-plan`, `zip`) reflejaran la nueva estructura.

| Entidad JSON | Campo | Descripcion | Valor Anterior (Iteracion 004) | Nuevo Valor (Iteracion 005) |
| :--- | :--- | :--- | :--- | :--- |
| Salida JSON `save-plan` | `proyecto` | Ruta relativa al directorio del proyecto | `output_projects/<carpeta>` | `<directorio_maestro_resuelto>/<carpeta>` |
| Salida JSON `save-plan` | `archivos_creados[]` | Rutas relativas a los archivos creados | Rutas bajo `output_projects/<carpeta>` | Rutas bajo `<directorio_maestro_resuelto>/<carpeta>` |
| Salida JSON `zip` | `archivo` | Ruta absoluta al `outputs.zip` generado | `<cwd>/output_projects/outputs.zip` | `<cwd>/<directorio_maestro_resuelto>/<carpeta>/outputs.zip` |

---

## 4. Estado de Orquestacion (`orchestration_state.json`)

El esquema de `orchestration_state.json` no cambia, pero los valores de las rutas almacenadas para `proyecto_activo` y otras referencias de ruta internas se actualizaran para reflejar la ruta base resuelta (`[directorio_maestro_resuelto]`) y la ubicacion del `outputs.zip` dentro del proyecto.

```json
{
  "proyecto_activo": "C:\\laragon\\www\\product_samples\\slides\\intro_docker",
  "fases": [...],
  "ultimo_zip": "C:\\laragon\\www\\product_samples\\slides\\intro_docker\\outputs.zip"
}
```

---

## 5. Interaccion CLI

Se introduce un nuevo tipo de interaccion en el CLI para la resolucion del directorio base. Esto no modifica estructuras de datos JSON, pero afecta el flujo de entrada/salida.

**Mensaje de Prompt (TTY)**:
```text
Advertencia: El directorio maestro de proyectos 'C:\laragon\www\product_samples\slides' no existe.
Por favor, ingrese una ruta de directorio existente para alojar los proyectos: 
```

**Mensaje de Error (No-TTY)**:
```json
{
  "error": "PRA_OUTPUT_DIR_INVALID",
  "mensaje": "El directorio maestro de proyectos configurado 'C:\\laragon\\www\\product_samples\\slides' no existe o no es valido. Por favor, cree el directorio o defina una ruta existente con la variable de entorno PRA_OUTPUT_DIR."
}
```
