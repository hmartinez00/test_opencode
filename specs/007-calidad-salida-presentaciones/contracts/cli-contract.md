# Contrato CLI: Calidad de Salida de Presentaciones PRA

**Especificacion**: [../spec.md](../spec.md) | **Plan**: [../plan.md](../plan.md)

Este contrato detalla los cambios en la interfaz de comandos y la interaccion con el entorno para la iteracion 007.

## 1. Comando `process-session`

### Sintaxis

```bash
python pra_helper.py process-session <N> [<respuesta_llm>] [--respuesta-file <ruta>]
```

### Parametros

| Parametro | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `N` | `int` | Si | Numero de sesion a procesar |
| `respuesta_llm` | `str` | No* | Respuesta LLM inline (5 bloques) |
| `--respuesta-file` | `str` | No* | Ruta al archivo con la respuesta LLM |

*Al menos uno de `respuesta_llm` o `--respuesta-file` es requerido.

### Reglas

1. **Precedencia**: si `--respuesta-file` esta presente, prevalece sobre el posicional.
2. Si se usa `--respuesta-file` y el archivo no existe, se imprime error JSON y se sale con codigo `1`.
3. Si se usa `--respuesta-file` y el archivo esta vacio o no contiene laminas parseables, se sale con codigo `1` (equivalente al caso posicional sin laminas).
4. La salida de exito es JSON con `status`, `archivos_creados`, `laminas_escritas`, etc. (inalterada).

### Codigos de salida

| Codigo | Significado |
|---|---|
| `0` | Exito |
| `1` | Respuesta invalida, archivo inexistente o sin laminas |
| `2` | Violacion de Cero CSS Inline, o secuencialidad bloqueada |
| `3` | Error leyendo registros |
| `4` | Proyecto no encontrado o plan ilegible |

## 2. Variable de entorno `PRA_ACTIVE_PROJECT`

```text
PRA_ACTIVE_PROJECT=<carpeta_snake_case>
```

### Reglas

1. Si `<base>/<PRA_ACTIVE_PROJECT>/presentation_plan.json` existe, todos los comandos que resuelven proyecto (`init` no aplica, `save-plan`, `prompt-session`, `process-session`, `consolidate`, `zip`, `resume`, `status`) operan sobre ese proyecto.
2. Si la variable no esta definida, se usa el comportamiento actual (cwd si es proyecto / primer proyecto alfabetico del base).
3. Si la variable apunta a una carpeta inexistente o sin `presentation_plan.json`, se cae al comportamiento actual sin error bloqueante.

## 3. Comportamiento del orquestador en `run_helper`

### Umbral de archivo temporal

- Por defecto, si una respuesta LLM supera los `30000` caracteres, `run_helper` la escribe a un archivo temporal y ejecuta `process-session N --respuesta-file <ruta>`.
- El archivo temporal se limpia en un bloque `finally`, incluso si el subproceso falla.
- El umbral es configurable via constante de modulo.

### Invariantes

- El subproceso nunca recibe una cadena de respuesta que supere el limite de argv de Windows.
- La salida/errores del subproceso se siguen devolviendo como `(codigo, stdout, stderr)`.

## 4. Contrato de salida de `consolidate` (cambios)

El reporte JSON de `consolidate` no cambia de forma, pero su salida escrita cambia:

- `assets/styles_blade/css/*.blade.php` sale envuelto en `<style>`.
- `assets/styles_blade/js/*.blade.php` sale envuelto en `<script>`.
- `manifest.blade.php` y `assets/*.blade.php` usan interpolacion `{$presentation->folder_name}`.
- El `data-title` de cada lamina usa titulo legible.
