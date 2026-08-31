# Research y Decisiones Tecnicas: Calidad de Salida de Presentaciones PRA

**Fecha**: 2026-08-31

## Antecedentes

Durante la corrida de validacion del Modulo 3 (Estructuras de Datos) se observaron seis desviaciones entre los artefactos generados por el flujo PRA y lo que la aplicacion Laravel/Reveal.js necesita para renderizar correctamente. Este documento registra las decisiones tecnicas (D1-D7) que fundamentan la implementacion.

## Decisiones

### D1 - Interpolacion de ruta del proyecto (P1)

**Contexto**: Blade usa `{{ $var }}` para escapar salida y `{!! $var !!}` para salida sin escapar, pero dentro de una cadena (como dentro de `@include("...")`) la interpolacion de la variable se expresa con **una unica llave** `{$presentation->folder_name}`, no con doble. El codigo actual genera literalmente la secuencia `{{$presentation->folder_name}}`, que Blade interpreta como texto literal de un solo bloque o falla segun el contexto.

**Opciones**:
- **A (elegida)**: Escribir la cadena con `{$presentation->folder_name}` en los entry points.
- B: Usar `{{ $presentation->folder_name }}` concatenada — inviable dentro de una cadena de include.

**Decision**: En `_consolidate_project()`:
- Lienas de `assets/styles.blade.php` y `assets/scripts.blade.php`: cambiar `{{{{$presentation->folder_name}}}}` (JS-f-string produce `{{$presentation->folder_name}}`) por `{$presentation->folder_name}`.
- Lienas del `manifest.blade.php` (`@include("presentation.slides.{{$presentation->folder_name}}.assets.styles")`): cambiar por `@include("presentation.slides.{$presentation->folder_name}.assets.styles")`.

**Consecuencia**: El archivo generado contiene exactamente `{$presentation->folder_name}`. Ningun test debe buscar la variante con doble llave.

### D2 - Envoltura de fragmentos CSS (P2)

**Contexto**: `consolidate` copia el contenido de `styles_additions/*.css` (CSS puro) directamente a `assets/styles_blade/css/*.blade.php`. Al incluirse via `@include`, el contenido no queda dentro de una etiqueta `<style>`, por lo que Laravel no lo emite como CSS.

**Opciones**:
- **A (elegida)**: Envolver el contenido con `<style>` al escribir el fragmento final.
- B: Dejar el envoltorio en la vista padre — fragmenta el responsable y rompe la modularidad.

**Decision**: Al escribir cada fragmento final en `_consolidate_project()`, generar:
`"<style>\n" + contenido + "\n</style>"`.

**Idempotencia**: Siempre se regenera desde la fuente limpia (`styles_additions/*.css`), que nunca lleva envoltura, por lo que un segundo `consolidate` no duplica la etiqueta. Si alguna vez la fuente estuviera ya envuelta, se detecta con un pre-chequeo `startswith("<style>")` y se evita doble envoltura (defensivo).

### D3 - Envoltura de fragmentos JS (P3)

**Contexto**: Igual que D2 pero para `scripts_additions/*.js` hacia `assets/styles_blade/js/*.blade.php`.

**Decision**: Envolver con `"<script>\n" + contenido + "\n</script>"`. Mismas reglas de idempotencia que D2 (`startswith("<script>")` como guarda defensiva).

### D4 - Respuesta LLM por archivo (P4)

**Contexto**: `process-session` exige la respuesta como argumento posicional. En Windows, `CreateProcess` tiene un limite de 32767 caracteres para la linea completa, por lo que respuestas LLM reales (con 18+ laminas, CSS y JS) lanzan `WinError 206`.

**Opciones**:
- **A (elegida)**: Nuevo flag opcional `--respuesta-file <ruta>` en `process-session`. `cmd_process_session` lee la respuesta desde el archivo cuando el flag esta presente.
- B: Leer desde stdin — cambia el contrato CLI y complica la prueba/uso manual.
- C: Solo documentar — no resuelve el problema real.

**Decision**:
- `main()`: `process_parser.add_argument("--respuesta-file", help="Ruta a archivo con la respuesta LLM")`.
- `cmd_process_session()`: si `--respuesta-file` presente, `response_text = Path(flag).read_text(...)`; si no, `response_text = args.respuesta_llm`. Precedencia: archivo gana si ambos se proveen (documentado).
- `pra_orchestrator.run_helper()`: si un argumento supera un umbral configurable (p. ej. 30000 chars), escribe esa respuesta a un archivo temporal y lo reemplaza por `--respuesta-file <ruta>`. Limpieza del temporal en `finally`.

**Consecuencia**: Responde respuestas grandes en Windows y mantiene retrocompatibilidad (el posicional sigue funcionando para respuestas cortas y para la mayoria de tests existentes).

### D5 - Seleccion de proyecto activo por entorno (P5)

**Contexto**: `find_project_dir()` (`pra_helper.py`) y `buscar_proyecto()` (`pra_orchestrator.py`) recorren el directorio base y eligen el primer proyecto (orden alfabetico), lo que falla con 2+ proyectos.

**Opciones**:
- **A (elegida)**: Nueva variable `PRA_ACTIVE_PROJECT=<carpeta>`; si existe `<base>/<carpeta>/presentation_plan.json`, priorizarla.
- B: Solo workdir — no resuelve el caso de automation/orquestador.
- C: No hacer nada — deja el bug latente.

**Decision**: En ambos metodos, leer `os.environ.get("PRA_ACTIVE_PROJECT")`. Si esta definido y el proyecto existe, devolverlo **antes** del recorrido por defecto. Si la carpeta indicada no existe, caer al comportamiento actual (sin error silencioso y, opcionalmente, con una advertencia en stderr).

### D6 - Titulo de lamina legible (P6)

**Contexto**: `_consolidate_project()` calcula `data_title = lamina.get("data_title") or lamina.get("titulo") or slide_id`. Cuando el plan no define `data_title` por lamina (caso comun en planes auto-generados), el manifest muestra el id crudo `s1-portada`.

**Opciones**:
- **A (elegida)**: Derivar un titulo legible del `id_kebab_case` cuando no hay `data_title` ni `titulo`: reemplazar `-` por espacios y capitalizar cada palabra.
- B: Dejar el id — no cumple el objetivo de legibilidad.

**Decision**: Nueva funcion helper `titulo_legible(id_kebab_case: str) -> str`. En `_consolidate_project()`: `data_title = lamina.get("data_title") or lamina.get("titulo") or titulo_legible(slide_id)`.

**Ejemplo**: `s1-listas-teoria` -> `S1 Listas Teoria`.

### D7 - Estrategia de pruebas TDD

**Contexto**: La iteracion toca serializacion de texto (interpolacion), envoltura de contenido y un cambio de contrato CLI. Requiere red (red-green-refactor) con pruebas que capturen el comportamiento antes de la correccion.

**Decision**:
- Escribir primero las pruebas que reproducen los problemas (rojo), luego implementar (verde), luego refactorizar sin romper.
- Usar `tmp_path` y el aislamiento de `PRA_OUTPUT_DIR` ya provistos por `conftest.py` (fixtures `run_cli`, `initialized_project`, `sample_llm_response_s1`, `sample_plan_json_str`, `isolated_dir`).
- Las pruebas vivas del TDD se documentan en `test_plan.md` de esta carpeta y se materializan en `tests/{unit,integration,constitutional}/`.
- Garantizar idempotencia de `consolidate` en el mismo proyecto.
- No descender cobertura por debajo de 85% en `pra_helper.py` y `pra_orchestrator.py`; mantener la suite verde completa.
