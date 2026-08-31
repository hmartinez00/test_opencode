# Modelo de Datos: Calidad de Salida de Presentaciones PRA

## Interpolacion de ruta del proyecto (P1)

Los entry points finales y el manifest usan interpolacion Blade valida con llave unica:

| Archivo | Antes (incorrecto) | Despues (correcto) |
|---|---|---|
| `manifest.blade.php` (push styles) | `@include("presentation.slides.{{$presentation->folder_name}}.assets.styles")` | `@include("presentation.slides.{$presentation->folder_name}.assets.styles")` |
| `manifest.blade.php` (push scripts) | `@include("presentation.slides.{{$presentation->folder_name}}.assets.scripts")` | `@include("presentation.slides.{$presentation->folder_name}.assets.scripts")` |
| `assets/styles.blade.php` | `@include("presentation.slides.{{$presentation->folder_name}}.styles_blade.css.sesionN_styles")` | `@include("presentation.slides.{$presentation->folder_name}.styles_blade.css.sesionN_styles")` |
| `assets/scripts.blade.php` | `@include("presentation.slides.{{$presentation->folder_name}}.styles_blade.js.sesionN_scripts")` | `@include("presentation.slides.{$presentation->folder_name}.styles_blade.js.sesionN_scripts")` |

## Envoltura de fragmentos de assets (P2, P3)

`consolidate` produce los fragmentos finales envueltos:

**Fragmento CSS** (`assets/styles_blade/css/sesionN_styles.blade.php`):

```text
<style>
/* ... CSS ... */
</style>
```

**Fragmento JS** (`assets/styles_blade/js/sesionN_scripts.blade.php`):

```text
<script>
// ... JS ...
</script>
```

**Reglas de identidad de la envoltura**:
- Una envoltura se identifica por el prefijo `<style>`/`<script>`.
- Nunca debe haber mas de una envoltura por fragmento.
- La fuente de verdad es `styles_additions/*.css` y `scripts_additions/*.js` (sin envoltura).

## Respuesta LLM por archivo (P4)

Nuevo parametro para `process-session`:

| Parametro | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `n` | `int` | Si | Numero de sesion |
| `respuesta_llm` | `str` | No (si se usa `--respuesta-file`) | Respuesta LLM inline |
| `--respuesta-file` | `str` | No | Ruta a archivo con la respuesta LLM |

**Precedencia**: si `--respuesta-file` esta presente, gana sobre `respuesta_llm`.

**Umbral del orquestador**: `run_helper` de `pra_orchestrator.py` usa archivo temporal cuando un argumento supera el umbral (default 30000 chars). El archivo temporal se limpia en `finally`.

## Seleccion de proyecto activo (P5)

Nueva variable de entorno:

```text
PRA_ACTIVE_PROJECT=<carpeta_snake_case>
```

**Regla**: si `<base>/<PRA_ACTIVE_PROJECT>/presentation_plan.json` existe, es el proyecto activo. Si no, se usa el comportamiento actual (primer proyecto / cwd).

## Titulo de lamina legible (P6)

La funcion `titulo_legible(id_kebab_case)` transforma:

| id_kebab_case | titulo_legible |
|---|---|
| `s1-portada` | `S1 Portada` |
| `s1-listas-teoria` | `S1 Listas Teoria` |
| `s1-retofinal-contactos` | `S1 Retofinal Contactos` |

**Regla de prioridad** en `_consolidate_project()`:

```text
data_title = lamina.data_title | lamina.titulo | titulo_legible(lamina.id_kebab_case)
```

## Registros y estado

- `class_registry.json` y `js_registry.json` no cambian su esquema en esta iteracion; solo los registries ya existentes se siguen actualizando via `pra_helper.py` (no se tocan manualmente).
- El estado de orquestacion (`orchestration_state.json`) no cambia su forma; la fase `consolidate` ya existe y solo ve modificada la salida que genera el motor.

## Contenido del ZIP

El `outputs.zip` debe incluir el producto final corregido. Continua excluyendo:
- El propio `outputs.zip`.
- `orchestration_state.json`.
- `orchestration_log.txt`.
