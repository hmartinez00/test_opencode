# Contrato CLI del Orquestador (orchestrator-contract.md)

**Especificacion de Interfaz para `pra_orchestrator.py`**

**Fecha**: 2026-08-22 | **Spec**: [../spec.md](../spec.md) | **Modelo de datos**: [../data-model.md](../data-model.md)

---

## Comandos

### 1. `run` - Ejecucion desatendida completa

```bash
python pra_orchestrator.py run <documento_fuente> [--backend mock|opencode] [--max-retries N] [--timeout-s S]
```

| Argumento | Requerido | Defecto | Descripcion |
|---|---|---|---|
| `documento_fuente` | Si | - | Ruta al documento fuente (.md, .txt, ...) |
| `--backend` | No | `mock` | Backend LLM: `mock` (fixtures deterministas) o `opencode` (CLI real) |
| `--max-retries` | No | `3` | Maximo de intentos por fase/sesion |
| `--timeout-s` | No | `300` | Timeout del subprocess del backend real |

**Comportamiento**:
1. Crea/reescribe `orchestration_state.json` en el CWD.
2. Ejecuta fases en orden: `init` -> `save_plan` -> `sesion[1..S]` -> `pytest` -> `cleanup`.
3. Imprime progreso por fase en STDOUT y auditoria detallada en `orchestration_log.txt`.

**Salidas**: codigo `0` con resumen final del directorio limpio (lote protegido + `backup/fuente/`); codigos de error segun tabla inferior.

**Nota (iteracion 008)**: la fase `zip` fue omitida del flujo automatico y reemplazada por `cleanup`, que invoca `pra_helper.py limpiar`. Estados guardados previos que contengan la fase `zip` se normalizan (via `normalizar_fases`) a `cleanup` al reanudar; `zip@completada` se mapea a `cleanup@completada` sin re-ejecutar.

---

### 2. `resume` - Reanudar corrida interrumpida

```bash
python pra_orchestrator.py resume
```

- **Precondicion**: existe `orchestration_state.json` valido.
- Retoma la primera fase/sesion cuyo estado sea `pendiente`, `en_curso` o `fallida`.
- Sin estado previo: mensaje "No hay corrida activa" y codigo `2`.

---

### 3. `status` - Estado actual

```bash
python pra_orchestrator.py status
```

Imprime tabla legible:

```text
Fixture       Estado       Intentos
init          completada   1
save_plan     completada   1
sesion 1      completada   2
sesion 2      pendiente    0
pytest        pendiente    0
cleanup       pendiente    0
```

Sin estado previo: codigo `2`.

---

## Codigos de Salida Estandar

| Codigo | Significado | Ejemplos |
|--------|-------------|----------|
| `0` | Exito | Corrida/resume completo; status impreso |
| `1` | Validacion incumplida tras agotar reintentos | CSS inline persistente; suite pytest fallida; JSON de plan malformado persistente |
| `2` | Error de estado/secuencialidad | `resume` sin corrida activa; estado corrupto; plan con 0 sesiones |
| `3` | Backend LLM no disponible | `opencode` no encontrado; timeout del backend real |
| `4` | Uso incorrecto de la CLI | Backend desconocido; documento fuente inexistente; argumentos invalidos |

---

## Garantias del Contrato

1. **Delegacion exclusiva**: toda mutacion de artefactos del proyecto se ejecuta via subprocess a `pra_helper.py`. El orquestador jamas escribe laminas, estilos, scripts, manifest ni registros.
2. **Estado atomico**: cada transicion persiste `orchestration_state.json` de forma atomica; una caida nunca deja un estado a medio escribir.
3. **No contaminacion del proyecto**: `orchestration_state.json` y `orchestration_log.txt` quedan fuera del directorio del proyecto.
4. **Secuencialidad estricta**: no se invoca `prompt-session N+1` sin sesion N `completada`.
5. **Determinismo mock**: con `--backend mock`, las respuestas provienen integramente de `mocks_llm/` y dos corridas producen arboles identicos.
6. **Auditoria**: todo intento (OK/FALLO) queda registrado con timestamp, diagnostico y duracion.

---

## Interaccion con el contrato existente de pra_helper.py

Este contrato es un **superset orquestador** del definido en `specs/001.../contracts/cli-contract.md`: lo consume sin modificarlo. Si el motor devuelve un codigo de salida distinto de 0, el orquestador clasifica:
- Exit code del motor + STDERR -> alimenta la puerta de validacion y el prompt de reflexion.
- Tras agotar `--max-retries` -> aborta con codigo `1` dejando la fase/sesion como `fallida` (reanudable).

### Respuestas largas (iteracion 007/P4)

Al delegar `process-session N '<respuesta>'`, si la respuesta supera el umbral `RESPUESTA_UMBRAL_CHARS` (default 30000 caracteres, por el limite de argv en Windows), `run_helper` la escribe a un archivo temporal y ejecuta `process-session N --respuesta-file <ruta>`. El archivo temporal se elimina en `finally`, incluso ante fallos del subproceso.

### Seleccion de proyecto activo (iteracion 007/P5)

`buscar_proyecto()` prioriza la variable de entorno `PRA_ACTIVE_PROJECT` dentro del directorio maestro; si la carpeta indicada no existe o no contiene `presentation_plan.json`, cae a la busqueda automatica (primer proyecto alfabetico).