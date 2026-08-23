# Plan de Implementacion: Orquestador Automatico de Flujo PRA (003-orquestador-automatizado-pra)

**Rama**: `003-orquestador-automatizado-pra` | **Fecha**: 2026-08-22 | **Especificacion**: [spec.md](./spec.md) | **Decisiones**: [research.md](./research.md)

---

## Resumen

Este plan define la capa de orquestacion que automatiza el flujo completo PRA de punta a punta: un nuevo script CLI (`pra_orchestrator.py`) coordina los comandos existentes de `pra_helper.py` (caja negra, via subprocess), invoca al LLM mediante backends intercambiables (`mock` determinista / `opencode` real), aplica puertas de validacion constitucional por sesion, ejecuta un bucle de autocorreccion con reintentos y finaliza con verificacion de calidad (`pytest`) y empaquetado (`zip`). El orquestador no escribe nunca artefactos del proyecto de presentacion: solo su estado y logs propios.

---

## Contexto Tecnico

**Lenguaje/Version**: Python 3.11+ (stdlib unicamente; sin dependencias nuevas)
**Componentes clave**:
- `subprocess`: invocacion a `pra_helper.py`, `opencode run`, `pytest`.
- `argparse`: interfaz CLI (`run`, `resume`, `status`).
- `json` + escritura atomica (`tempfile` + `os.replace`): persistencia del estado.
- ABC (`abc.LLMBackend`): contrato comun de backends.
- Fixtures pytest existentes (`tmp_path`, `capsys`, mocks de subprocess): base de las pruebas.

**Estructura de archivos nueva**:
```text
├── pra_orchestrator.py            # Motor de orquestacion (nuevo)
├── mocks_llm/                     # Respuestas LLM deterministas para --backend mock
│   ├── plan.txt
│   └── sesion{N}.txt
├── orchestration_state.json       # Estado por corrida (generado en runtime)
└── tests/
    ├── unit/
    │   ├── test_orchestrator_state.py     # Persistencia atomica + transiciones
    │   └── test_orchestrator_validations.py # Puertas post-sesion
    ├── integration/
    │   ├── test_cli_orchestrator_run_mock.py  # E2E mock en tmp_path
    │   └── test_cli_orchestrator_retry.py     # Secuencia contaminada->valida
    └── constitutional/
        └── test_orchestrator_rules.py     # No-escritura directa, abortos y codigos
```

---

## Arquitectura Interna de `pra_orchestrator.py`

```text
main(argv)
├── cmd_run(doc, backend, max_retries)    # Flujo end-to-end
├── cmd_resume()                          # Retoma desde ultima fase valida
├── cmd_status()                          # Resumen legible del estado
│
├── class LLMBackend(ABC)                 # generar(prompt:str) -> str
│   ├── MockBackend(fixtures_dir, secuencia=None)
│   └── OpenCodeBackend(timeout_s)
│
├── run_helper(*args) -> (code, out, err) # Subprocess a pra_helper.py
├── fase_init(doc)                        # init -> prompt plan maestro
├── fase_save_plan(prompt)                # LLM -> save-plan '<json>'
├── fase_session(n, backend)              # prompt-session N -> LLM -> process-session N
│   └── validar_post_sesion(n) -> ValidationReport
│   └── construir_prompt_reflexion(...)   # anexo diagnostico para reintento
├── fase_pytest()                         # suite verde + cobertura >= 85%
└── fase_zip()                            # pra_helper zip
```

### Mapeo fases -> comandos del motor (contrato 001)

| Fase del orquestador | Comando delegado | Criterio de exito |
|---|---|---|
| `init` | `python pra_helper.py init <doc>` | exit code 0 + STDOUT con prompt |
| `save_plan` | `save-plan '<json>'` tras extraer JSON del LLM | exit code 0 |
| `sesion[N]` | `prompt-session N` -> LLM -> `process-session N '<resp>'` | exit 0 + ValidationReport OK |
| `pytest` | `pytest --cov=pra_helper --cov-report=term-missing` | passed==total, cobertura >= 85 |
| `zip` | `python pra_helper.py zip` | existe `outputs.zip` |

---

## Verificacion Constitucional

| Principio | Estado | Mecanismo en el orquestador |
|-----------|--------|------------------------------|
| I. Cero CSS Inline | CUMPLE | Puerta regex post-sesion (defensa en profundidad) + reintento con reflexion |
| II. JavaScript Acotado | CUMPLE | Delegacion total en `pra_helper.py` (validaciones existentes intactas) |
| III. Preservacion Determinista | CUMPLE | El orquestador solo escribe `orchestration_state.json` y log; artefactos exclusivamente via pra_helper (verificado por prueba constitucional) |
| IV. Construccion Progresiva | CUMPLE | Iteracion estricta 1..S; puerta impide avanzar con sesion previa incompleta |
| V. Documentacion en Espanol | CUMPLE | Specs, mensajes CLI y docstrings en espanol |

---

## Estrategia de Pruebas

1. **Unitarias**: persistencia atomica y transiciones del estado; parser de resumen pytest-cov; constructor de prompt de reflexion; puertas de validacion sobre arboles tmp.
2. **Integracion**: E2E `run --backend mock` en `tmp_path` (con documento fixture); `resume` tras interrupcion simulada; retry loop con `MockBackend(secuencia=[contaminada, valida])`; codigos de salida 1/2/3/4.
3. **Constitucionales**: auditoria de que el orquestador no crea/edita laminas ni registros; aborto limpio al agotar reintentos; rechazo de backends invalidos.
4. **Mocks de subprocess**: `run_helper` y `fase_pytest` se simulan en pruebas unitarias/integracion cuando corresponda para mantener la suite rapida (< 60 s).

---

## Metricas de Calidad y Criterios de Parada

- Suite completa en verde: 30 pruebas previas + nuevas, `0 failures`.
- Cobertura: `pra_helper.py` >= 85% (sin regresion) y `pra_orchestrator.py` >= 85%.
- Comando de verificacion:
```bash
pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```
- SC-202 (determinismo mock): dos corridas E2E consecutivas comparadas por hash de arbol (excluyendo `orchestration_log.txt`).