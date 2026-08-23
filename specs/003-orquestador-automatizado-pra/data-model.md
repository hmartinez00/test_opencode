# Modelo de Datos: Orquestador Automatico de Flujo PRA (003-orquestador-automatizado-pra)

**Fecha**: 2026-08-22 | **Especificacion**: [spec.md](./spec.md)

Este documento define las entidades nuevas introducidas por el orquestador. No modifica el modelo de datos del proyecto de presentacion (ver `specs/001.../data-model.md`).

---

## 1. Estado de Orquestacion (`orchestration_state.json`)

Archivo JSON unico por corrida, ubicado en la raiz del workspace de ejecucion. Escritura atomica tras cada transicion.

```json
{
  "version": "1.0",
  "proyecto": "introduccion_docker",
  "documento_fuente": "ejemplos/introduccion_docker/documento_fuente.md",
  "backend": "mock",
  "max_reintentos": 3,
  "iniciada_en": "2026-08-22T10:00:00",
  "actualizada_en": "2026-08-22T10:05:32",
  "fases": {
    "init": {
      "estado": "completada",
      "intentos": 1,
      "ultimo_error": null
    },
    "save_plan": {
      "estado": "completada",
      "intentos": 1,
      "ultimo_error": null
    },
    "sesiones": [
      {
        "numero": 1,
        "estado": "completada",
        "intentos": 2,
        "validaciones": {
          "exit_code_ok": true,
          "sin_css_inline": true,
          "laminas_completas": true
        }
      },
      {
        "numero": 2,
        "estado": "pendiente",
        "intentos": 0,
        "validaciones": null
      }
    ],
    "pytest": { "estado": "pendiente", "intentos": 0, "ultimo_error": null },
    "zip":    { "estado": "pendiente", "intentos": 0, "ultimo_error": null }
  }
}
```

### Reglas del esquema

| Campo | Tipo | Regla |
|---|---|---|
| `version` | string | Fijo `"1.0"`; permite migraciones futuras |
| `backend` | enum | `mock` \| `opencode` |
| `max_reintentos` | int | `>= 1`; defecto 3 |
| `fases.*.estado` | enum | `pendiente` \| `en_curso` \| `completada` \| `fallida` |
| `fases.sesiones[].numero` | int | Orden estricto ascendente (Constitucion IV) |
| `fases.sesiones[].validaciones` | objeto/null | Reporte de la puerta post-sesion; `null` si aun no se evaluo |
| `ultimo_error` | string/null | Diagnostico del ultimo intento fallido |

### Transiciones validas

```text
pendiente -> en_curso -> completada
pendiente -> en_curso -> fallida      (agotados reintentos; terminal hasta resume/reinicio)
fallida   -> en_curso                 (solo via comando resume)
```

---

## 2. Reporte de Validacion (`ValidationReport`)

Resultado estructurado de la puerta post-sesion. No se persiste como archivo separado: vive dentro del estado.

```json
{
  "exit_code_ok": true,
  "sin_css_inline": true,
  "laminas_faltantes": [],
  "detalle": ""
}
```

- `exit_code_ok`: subprocess `process-session N` retorno `0`.
- `sin_css_inline`: regex `style\s*=` sin coincidencias en `sesion[N]/*.blade.php`.
- `laminas_faltantes`: lista de `id_kebab_case` declarados en el plan sin archivo `.blade.php` correspondiente.
- La sesion pasa la puerta solo si `exit_code_ok && sin_css_inline && laminas_faltantes == []`.

---

## 3. Registro de Intento (`AttemptRecord`, log de auditoria)

Linea append-only en el log de corrida (`orchestration_log.txt`, excluido del zip):

```text
2026-08-22T10:04:11 | sesion=1 | intento=1 | resultado=FALLO | motivo="CSS inline detectado en que-es-docker.blade.php" | duracion_s=41.2
2026-08-22T10:05:02 | sesion=1 | intento=2 | resultado=OK | motivo="" | duracion_s=38.9
```

Campos: timestamp ISO-8601, fase/sesion, numero de intento, resultado (`OK`|`FALLO`), motivo/diagnostico, duracion en segundos.

---

## 4. Prompt de Reflexion de Error

No es un archivo persistente: es un payload derivado en memoria.

```text
<prompt_original_compilado>

## REINTENTO {k}/{max} - DIAGNOSTICO DEL FALLO ANTERIOR
- Fase: {fase}
- Codigo de retorno: {exit_code}
- Validaciones incumplidas: {lista}
- Detalle STDERR: {stderr_recortado_a_500_chars}
INSTRUCCION: Corrige UNICAMENTE el problema descrito y regenera la respuesta COMPLETA con los 5 bloques.
```

---

## 5. Fixtures del MockBackend (`mocks_llm/`)

```text
mocks_llm/
├── plan.txt       # Respuesta completa esperada para la fase save-plan
└── sesion{N}.txt  # Respuesta completa esperada para prompt-session N
```

Convencion:
- Contenido identico a una respuesta LLM valida de 5 bloques.
- Para pruebas del retry loop, `MockBackend(secuencia=[...])` acepta respuestas programadas por intento (ej. primera contaminada con CSS inline, segunda valida).
