# Plan de implementacion: correcciones al motor PRA (iteracion 011)

**Fecha**: 2026-09-02
**Especificacion**: [spec.md](./spec.md)
**Estado**: En planificacion (pre-implementacion)

## 1. Estrategia TDD

Cada correccion sigue el ciclo TDD estricto:

1. Redactar pruebas rojas que fallen por la limitacion actual.
2. Ejecutar solo esas pruebas y confirmar el fallo.
3. Implementar la correccion minima necesaria.
4. Ejecutar las pruebas afectadas y confirmar pase.
5. Ejecutar la suite completa y verificar que no hay regresiones.
6. Avanzar a la siguiente correccion.

No se implementa codigo de produccion antes de completar la fase de pruebas rojas. Las correcciones se aplican en orden secuencial (A1 -> A2 -> ... -> A6) para aislar cada cambio.

## 2. Orden de implementacion

Se priorizan las correcciones por impacto y dependencia:

| Paso | Correccion | Dependencias | Riesgo |
|------|-----------|--------------|--------|
| 1 | A1 — Regex BLOQUE 6 | Ninguna | Bajo: cambio aislado en regex |
| 2 | A2 — Deduplicacion registros | Ninguna | Bajo: logica de filtrado |
| 3 | A3 — Auto-numerado orden | Ninguna | Medio: afecta normalizacion |
| 4 | A4 — Preservar data_title | Ninguna | Medio: toca normalize + consolidate |
| 5 | A5 — Unificar prefijo session | A4 (consolidate) | Alto: toca manifest + limpieza |
| 6 | A6 — save-plan --plan-file | Ninguna | Bajo: addition pura |

## 3. Diseno por correccion

### 3.1 A1 — Regex BLOQUE 6 tolerante a linea en blanco

**Archivo**: `pra_helper.py`, lineas 691-697 (dentro de `parse_llm_response`)

**Cambio actual**:
```python
audio_pattern = re.compile(
    r"\*\*BLOQUE\s+6[^\n]*\n```(?:text|txt)?\s*\n?(.*?)```",
    re.IGNORECASE | re.DOTALL,
)
```

**Problema**: `\n` exige salto inmediato despues del encabezado y antes del fence. Una linea en blanco (otro `\n`) rompe la coincidencia.

**Solucion**: Reemplazar `\n` por `\s*\n` (o `[ \t]*\n`) antes del fence para tolerar lineas en blanco:

```python
audio_pattern = re.compile(
    r"\*\*BLOQUE\s+6[^\n]*\n[ \t]*\n?```(?:text|txt)?\s*\n?(.*?)```",
    re.IGNORECASE | re.DOTALL,
)
```

O mas simplemente: `\*\*BLOQUE\s+6[^\n]*\n\s*```(?:text|txt)?\s*\n?(.*?)```

**Revision de bloques 1-5**: Verificar que los patrones de extraccion de los bloques 1-5 no tienen el mismo problema. Los bloques usan `{{- sesionN/slide_id.blade.php -}}` como delimitador, no fences, asi que no se afectan.

**Funciones a modificar**: `parse_llm_response` (linea ~691).

### 3.2 A2 — Deduplicacion de clases en `save-plan`

**Archivo**: `pra_helper.py`, lineas 450-476 (dentro de `cmd_save_plan`)

**Cambio actual**: El loop agrega entradas a `class_registry["clases"]` sin verificar si ya existe una con el mismo `nombre`.

**Solucion**: Antes del loop, deduplicar las listas `clases_css_requeridas` y `comportamientos_js_requeridos` de todas las laminas:

```python
def _deduplicar_por_nombre(lista_entradas, campo_nombre="nombre"):
    """Deduplica por nombre manteniendo la primera ocurrencia."""
    vistos = set()
    resultado = []
    for entrada in lista_entradas:
        nombre = entrada["nombre"] if isinstance(entrada, dict) else entrada
        if nombre not in vistos:
            vistos.add(nombre)
            resultado.append(entrada)
    return resultado
```

Aplicar antes de sembrar en `cmd_save_plan`. La funcion `merge_registry` (linea 146) ya existe pero opera sobre el registro existente; la deduplicacion aqui es sobre las entradas del plan antes de sembrar.

**Funciones a crear/modificar**: nueva funcion `_deduplicar_por_nombre`, modificacion en `cmd_save_plan`.

### 3.3 A3 — Auto-numerado de `orden`

**Archivo**: `pra_helper.py`, lineas 219-252 (`normalize_plan`)

**Cambio actual**: `orden` se normaliza a `int` con default `0`. No hay logica de auto-numerado.

**Solucion**: Despues de normalizar todas las laminas, verificar si alguna tiene `orden == 0`. Si es asi:

```python
# Auto-numerado si alguna lamina carece de orden
orden_presente = all(l.get("orden", 0) != 0 for l in laminas_normalizadas)
if not orden_presente:
    contador = 1
    for l in laminas_normalizadas:
        if l.get("orden", 0) == 0:
            l["orden"] = contador
        contador += 1
```

Para la deteccion de "todas traen orden" vs "parcial", se puede verificar si el 100% de las laminas tienen `orden != 0` antes de decidir.

**Integracion con calidad**: En `_validar_calidad_plan`, agregar advertencia si el plan original no traia `orden` en ninguna lamina. Con `PRA_PLAN_ESTRICTO=1`, elevar a error.

**Funciones a modificar**: `normalize_plan`, `_validar_calidad_plan`.

### 3.4 A4 — Preservar `data_title`

**Archivos**: `pra_helper.py`, lineas 219-252 (`normalize_plan`) y linea 1040 (`_consolidate_project`)

**Problema**: `normalize_plan` solo copia campos explicitos (lineas 236-250). `data_title` no esta en la lista y se descarta.

**Solucion**:

1. En `normalize_plan`, agregar `data_title` al mapeo de campos de lamina:
   ```python
   if "data_title" in lamina_original:
       lamina["data_title"] = lamina_original["data_title"]
   ```

2. En `_consolidate_project` (linea 1040), ya existe el fallback:
   ```python
   data_title = lamina.get("data_title") or lamina.get("titulo") or titulo_legible(slide_id)
   ```
   Este codigo es correcto; solo necesita que `data_title` este presente en la lamina normalizada.

3. En `cmd_save_plan` (linea 487), el fallback ya existe:
   ```python
   data_title=lamina.get("data_title", lamina.get("titulo", lid))
   ```

**Funciones a modificar**: `normalize_plan` (agregar mapeo de `data_title`).

### 3.5 A5 — Unificacion de prefijo `session[N]`

**Archivos**: `pra_helper.py`, multipuntos

**Estado actual**:
- `cmd_save_plan` crea `sesion{N}/` (espanol) como directorios internos.
- `_consolidate_project` copia de `sesion{N}/` a `session{N}/` (ingles) para el lote final.
- `_limpiar_proyecto` elimina `sesion*/` internas y preserva `session*/`.
- `_lote_protegido_completo` busca `session*`.

**Accion**: Documentar la convencion explicitamente. No renombrar los directorios internos en esta iteracion (riesgo alto). La convencion es:
- Internos/backup: `sesion[N]/` (espanol, compatibilidad con data-model).
- Lote protegido: `session[N]/` (ingles, contrato del manifest `view="session{N}.*"`).

**Cambios documentales**: Actualizar `AGENTS.md` seccion 2 (estructura) y seccion 4 (flujo) con la distincion explicita.

**Verificacion**: La prueba de integracion debe confirmar que `session{N}/` existe en el lote y `sesion{N}/` en backup.

### 3.6 A6 — `save-plan --plan-file`

**Archivo**: `pra_helper.py`, lineas 1318-1365 (parser CLI) y 422-530 (`cmd_save_plan`)

**Cambio**: Anadir argumento opcional `--plan-file` al subparser de `save-plan`:

```python
save_plan_parser.add_argument("--plan-file", help="Ruta a archivo JSON con el plan (UTF-8)")
```

En `cmd_save_plan`, resolver la fuente del JSON:

```python
if args.plan_file:
    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print(json.dumps({"error": "PLAN_FILE_NOT_FOUND", ...}))
        sys.exit(1)
    json_text = plan_path.read_text(encoding="utf-8")
else:
    json_text = args.json_plan
```

El argumento posicional `json_plan` debe hacerse opcional (`nargs="?"`) para permitir `--plan-file` como unica fuente.

**Funciones a modificar**: `cmd_save_plan`, parser CLI.

## 4. Cambios previstos por archivo

| Archivo | Cambios |
|---------|---------|
| `pra_helper.py` | A1: regex BLOQUE 6; A2: deduplicacion; A3: auto-numerado; A4: data_title; A6: --plan-file |
| `tests/unit/test_normalize_plan.py` (o equivalente) | A3, A4: pruebas de normalizacion |
| `tests/unit/test_audio_narration.py` (o equivalente) | A1: pruebas de regex BLOQUE 6 |
| `tests/integration/test_cli_consolidate.py` (o equivalente) | A4, A5: pruebas de manifest y carpetas |
| `tests/integration/test_cli_save_plan.py` (o equivalente) | A2, A6: pruebas de deduplicacion y --plan-file |
| `tests/conftest.py` | Fixtures nuevas para planes con/without orden, data_title, duplicados |
| `AGENTS.md` | A5: documentar convencion session/sesion |
| `SESION_PRA_RESUMEN.md` | Resumen de iteracion |

## 5. Puertas de calidad

### Puerta T1: pruebas rojas
Cada grupo de pruebas nuevas debe fallar antes de implementar la correccion.

### Puerta T2: correccion aislada
Solo se modifica lo necesario para pasar las pruebas de la correccion actual.

### Puerta T3: suite completa
Despues de cada correccion, la suite completa (151+ pruebas existentes + nuevas) debe pasar en verde.

### Puerta T4: cobertura
Cobertura de `pra_helper.py` >= 85% y `pra_orchestrator.py` >= 85%.

### Puenta T5: retrocompatibilidad
Los comandos existentes (`save-plan '<json>'`, `process-session N '<respuesta>'`) no deben cambiar de comportamiento.

## 6. Riesgos y mitigaciones

- **A1 — Regex demasiado permisiva**: Usar anclas de fence triple-backtick para no capturar contenido espurio. Probar con respuestas que tengan bloques 1-5 y BLOQUE 6 con/sin linea en blanco.
- **A3 — Colision de orden**: Verificar que el auto-numerado no sobreescriba valores existentes no-cero.
- **A4 — Regresiones en fallback**: Mantener el chain de fallback `data_title -> titulo -> titulo_legible(id)` intacto.
- **A5 — Confusion sesion/session**: Documentar claramente y agregar validacion en `_lote_protegido_completo` que use `session*`.
- **A6 — Breaking change en argv**: Hacer `json_plan` opcional con `nargs="?"` y validar que al menos una de las dos vias esta presente.

## 7. Criterio de salida

La implementacion podra comenzar cuando:

- La especificacion y este plan sean aprobados.
- Las pruebas rojas esten definidas en `test_plan.md`.
- Los fixtures necesarios esten identificados.
- Se confirme que no se modifica codigo de produccion en esta etapa.
- La suite actual pase sin fallos (baseline verde).
