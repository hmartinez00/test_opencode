# Research: Orquestador Automatico de Flujo PRA (003-orquestador-automatizado-pra)

**Fecha**: 2026-08-22 | **Especificacion**: [spec.md](./spec.md)

Este documento registra las decisiones tecnicas (D) y sus alternativas evaluadas para la iteracion del orquestador automatico.

---

## D1. Integracion con el LLM: CLI headless vs API REST directa

| Alternativa | Pros | Contras |
|---|---|---|
| **(A) OpenCode CLI no interactivo** (`opencode run "<prompt>"` via subprocess) | Reutiliza sesion/credenciales ya configuradas; sin nuevas dependencias HTTP; consistente con como trabaja hoy el agente | Depende de que la CLI este en PATH; parsing de salida por STDOUT |
| (B) API REST directa del proveedor LLM | Control fino (temperatura, tokens) | Requiere claves API, SDK/httpx, gestion de secretos y costos; acopla PRA a un proveedor |

**Decision**: Alternativa **A**, detras de la abstraccion `OpenCodeBackend`. Invocacion por subprocess con timeout configurable y captura de STDOUT/STDERR. Si la CLI no existe o expira -> codigo de salida `3`.

---

## D2. Comunicacion con pra_helper.py: subprocess vs import in-process

| Alternativa | Pros | Contras |
|---|---|---|
| **(A) Subprocess al CLI existente** | Respeta el contrato CLI de la spec 001 como frontera; captura exit codes/STDERR reales; aisla fallos; cero cambios en `pra_helper.py` | Overhead de proceso (~ms) |
| (B) Importar funciones internas de `pra_helper` | Rapido, tipado directo | Acopla internals; habria que simular exit codes/stderr; rompe la frontera contractual |

**Decision**: Alternativa **A**. El orquestador consume `init|save-plan|prompt-session|process-session|zip` exactamente como un agente humano, segun `specs/001.../contracts/cli-contract.md`.

---

## D3. Validacion post-sesion: confiar solo en pra_helper vs defensa en profundidad

**Decision**: Defensa en profundidad. `pra_helper.py` ya valida estructura de 5 bloques, CSS inline y secuencialidad; sin embargo, el orquestador repite checks economicos e independientes:

1. Exit code `0` del subprocess.
2. Regex anti CSS inline (`style="..."`) sobre los `.blade.php` de `sesion[N]/`.
3. Presencia de un archivo por cada lamina declarada en `presentation_plan.json` para esa sesion.

Justificacion: costo < 50 ms, independencia del motor (detectaria bugs futuros del propio helper) y conversion de la Constitucion en checks ejecutables.

---

## D4. Bucle de autocorreccion: prompt original + anexo de diagnostico

**Decision**: En reintento se reenvia el prompt compilado original mas un **anexo de reflexion** estructurado:

```text
## REINTENTO {k}/{max} - DIAGNOSTICO DEL FALLO ANTERIOR
- Fase: process-session N
- Codigo de retorno: 2
- Validacion incumplida: Cero CSS Inline
- Detalle STDERR: "Violacion detectada: style= en lamina X"
INSTRUCCION: Corrige UNICAMENTE el problema descrito y regenera la respuesta completa.
```

Alternativas descartadas:
- Regenerar desde cero sin contexto del error: alta probabilidad de repetir el fallo.
- Parchear la respuesta defectuosa con regex desde el orquestador: violaria Constitucion III (el orquestador no muta artefactos).

---

## D5. Backends intercambiables y determinismo del mock

**Decision**: Interfaz comun `LLMBackend.generar(prompt: str) -> str` con dos implementaciones:

- `MockBackend`: sirve respuestas estaticas desde `mocks_llm/` mapeadas por fase/sesion (`plan.txt`, `sesion1.txt`, ...). Admite ademas una "secuencia programada" (lista de respuestas por intento) para probar el retry loop de forma determinista en pruebas.
- `OpenCodeBackend`: subprocess headless a la CLI.

El mock garantiza SC-202 (corridas byte a byte identicas) porque las respuestas son estaticas y `pra_helper.py` es determinista.

*(continua: D6, D7)*

---

## D6. Persistencia del estado: JSON plano con escritura atomica

**Decision**: `orchestration_state.json` en la raiz del workspace de corrida, escrito atomicamente (archivo temporal + `os.replace`) tras cada transicion de estado. Esquema versionado (`"version": "1.0"`), detallado en [data-model.md](./data-model.md).

Alternativas descartadas:
- SQLite: innecesario para un archivo unico por corrida.
- Derivar el estado inspeccionando carpetas: fragil ante corridas parciales (no distingue `completada` de `en_curso`).

---

## D7. Verificacion de calidad pre-zip: parsing del resumen pytest-cov

**Decision**: Ejecutar `pytest --cov=pra_helper --cov-report=term-missing` via subprocess y parsear:
- Contadores `passed / failed / errors` de la linea resumen final.
- Porcentaje de cobertura de la fila `pra_helper.py` en la tabla `--cov-report=term-missing`.

Umbrales exigidos: `failed == 0 and errors == 0` y `cobertura >= 85%`. Cualquier desvio aborta sin generar `outputs.zip`.

Nota: en pruebas automatizadas del orquestador, este subprocess se simula con mocks para no acoplar los tests a la duracion real de la suite.

---

## Referencias

- Contrato CLI vigente del motor: `specs/001-sistema-automatizacion-presentaciones-pra/contracts/cli-contract.md`.
- Constitucion: `.specify/memory/constitution.md`.
- Fixtures LLM existentes reutilizables como base de los mocks: `tests/conftest.py` (`sample_llm_response_s1`, `sample_invalid_llm_response_inline_css`).
