# Lista de Tareas: Orquestador Automatico de Flujo PRA (003-orquestador-automatizado-pra)

## Fase 1: Contrato y Esqueleto del Orquestador
- [x] T301 Implementar esqueleto `pra_orchestrator.py` con `argparse` (`run`, `resume`, `status`) y codigos de salida estandar (0/1/2/3/4).
- [x] T302 Implementar persistencia atomica de `orchestration_state.json` y transiciones de estado validas (`pendiente/en_curso/completada/fallida`).
- [x] T303 Implementar log de auditoria `orchestration_log.txt` (timestamp, fase, intento, resultado, duracion).

## Fase 2: Backends LLM
- [x] T304 Implementar abstraccion `LLMBackend` con metodo comun `generar(prompt) -> str`.
- [x] T305 Implementar `MockBackend`: fixtures desde `mocks_llm/` + modo secuencia programada para pruebas del retry loop.
- [x] T306 Implementar `OpenCodeBackend`: subprocess a CLI no interactiva con timeout y captura STDOUT/STDERR.
- [x] T307 [P] Crear directorio `mocks_llm/` con respuestas deterministas (plan + sesiones del ejemplo Docker).

## Fase 3: Motor del Bucle de Fases
- [x] T308 Implementar fases `init` y `save_plan` delegando en subprocess a `pra_helper.py`.
- [x] T309 Implementar `fase_session(N)`: `prompt-session N` -> backend -> `process-session N '<respuesta>'`.
- [x] T310 Implementar `validar_post_sesion(N)`: exit code, regex anti CSS inline, laminas completas vs plan (`ValidationReport`).
- [x] T311 Implementar bucle de reintentos con `--max-retries` y constructor de prompt de reflexion de error.
- [x] T312 Implementar fase `pytest` (parse de resumen passed/cobertura, umbrales >= 85%) y fase `zip`.

## Fase 4: Estado y Reanudacion
- [x] T313 Implementar `cmd_status` (tabla legible) y `cmd_resume` (retoma primera fase no completada; codigo 2 sin estado previo).

## Fase 5: Pruebas Automatizadas
- [x] T314 [P] `tests/unit/test_orchestrator_state.py`: atomicidad, transiciones, estado corrupto -> codigo 2.
- [x] T315 [P] `tests/unit/test_orchestrator_validations.py`: puertas post-sesion sobre arboles tmp_path.
- [x] T316 `tests/integration/test_cli_orchestrator_run_mock.py`: E2E mock completo en tmp_path; verificacion de artefactos y exclusion del zip.
- [x] T317 `tests/integration/test_cli_orchestrator_retry.py`: secuencia contaminada->valida completa en intento 2; agotamiento -> aborta codigo 1 con sesion fallida.
- [x] T318 `tests/integration/test_cli_orchestrator_resume.py`: interrupcion simulada tras sesion K y continuacion por K+1.
- [x] T319 [P] `tests/constitutional/test_orchestrator_rules.py`: el orquestador no escribe artefactos directamente; backends invalidos -> 4; plan 0 sesiones -> 2.

## Fase 6: Verificacion Final y Documentacion
- [x] T320 Ejecutar suite completa `pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`; verificar 0 fallos y coberturas >= 85%.
- [x] T321 Actualizar `AGENTS.md` (nuevo comando de automatizacion y flujo desatendido) y `README.md` (seccion orquestador).
- [x] T322 Validar E2E real con documento Docker segun `quickstart.md` (Escenarios 1-5).