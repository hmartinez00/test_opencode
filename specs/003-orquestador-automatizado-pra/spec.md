# Especificacion de Funcionalidad: Orquestador Automatico de Flujo PRA (003-orquestador-automatizado-pra)

**Rama de Funcionalidad**: `003-orquestador-automatizado-pra`

**Fecha de Creacion**: 2026-08-22

**Estado**: Borrador

**Entrada**: Requerimiento del usuario: "Automatizar de manera determinista el flujo completo PRA (`init` -> `save-plan` -> [`prompt-session N` -> LLM -> `process-session N`]* -> `zip`) en un solo comando, incluyendo las pruebas de validacion y un bucle de autocorreccion ante respuestas defectuosas del LLM."

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Ejecucion Desatendida End-to-End (Prioridad: P1)

El usuario proporciona un documento fuente y ejecuta un unico comando del orquestador (`pra_orchestrator.py`). El sistema, sin intervencion manual, ejecuta la secuencia completa: compila el prompt del Plan Maestro via `pra_helper.py init`, lo envia al backend LLM seleccionado, guarda el plan con `save-plan`, itera secuencialmente por cada sesion del plan (`prompt-session N` -> LLM -> `process-session N`) y finaliza empaquetando con `zip`, dejando el proyecto listo para integrarse en Laravel.

**Por que esta prioridad**: Elimina el cuello de botella manual actual (copiar prompts entre comandos). Es el valor central de la iteracion: convertir el flujo interactivo en un pipeline determinista.

**Prueba Independiente**: Ejecutar `python pra_orchestrator.py run <documento> --backend mock` en un directorio aislado y verificar que se genera la estructura completa del proyecto (plan, laminas Blade, estilos/scripts acumulados, registros actualizados y `outputs.zip`) sin entrada humana intermedia.

**Escenarios de Aceptacion**:

1. **Dado** un documento fuente valido, **Cuando** se ejecuta `run --backend mock`, **Entonces** el proceso termina con codigo de salida `0` y existen `presentation_plan.json`, las carpetas `sesion[N]/` con sus laminas, `styles.blade.php`, `scripts.blade.php`, los registros actualizados y `outputs.zip`.
2. **Dado** un plan maestro con S sesiones, **Cuando** el orquestador avanza, **Entonces** procesa las sesiones estrictamente en orden ascendente (1..S) delegando cada mutacion en los comandos CLI de `pra_helper.py`.
3. **Dado** que una fase intermedia falla de forma irrecuperable, **Cuando** el proceso aborta, **Entonces** lo hace con codigo distinto de `0` y el estado persistido permite reanudar desde la fase fallida.

---

### Historia de Usuario 2 - Bucle de Autocorreccion ante Respuestas Defectuosas del LLM (Prioridad: P1)

Ante una respuesta del LLM rechazada por `process-session` o por las validaciones posteriores (estructura de 5 bloques incompleta, CSS inline, JSON de registros malformado), el orquestador construye automaticamente un prompt de reflexion de error con el motivo exacto del rechazo y reinvoca al backend, hasta un maximo configurable de reintentos.

**Por que esta prioridad**: El LLM es la unica fuente de no-determinismo del sistema. Sin correccion autonoma, cada respuesta defectuosa requeriria intervencion humana, anulando el objetivo de automatizacion total.

**Prueba Independiente**: Con un mock programado para devolver primero una respuesta contaminada con `style="color:red;"` y luego una valida, la corrida debe completar la sesion en el segundo intento, registrando ambos intentos en el log de auditoria.

**Escenarios de Aceptacion**:

1. **Dado** una respuesta que viola Cero CSS Inline, **Cuando** `process-session` rechaza la escritura, **Entonces** el orquetador genera un prompt de reintento citando la violacion detectada y reinvoca al backend sin tocar archivos del proyecto.
2. **Dado** que los intentos fallidos alcanzan `--max-retries` (por defecto 3), **Cuando** la sesion sigue sin validar, **Entonces** aborta con codigo `1`, marca la sesion como `fallida` en el estado y no deja artefactos parcialmente integrados.
3. **Dado** un reintento exitoso, **Cuando** se consulta el estado, **Entonces** la sesion figura como `completada` con su contador de intentos.

---

### Historia de Usuario 3 - Puertas de Validacion Constitucional por Sesion (Prioridad: P2)

Tras cada `process-session N`, el orquestador ejecuta verificaciones independientes (defensa en profundidad): codigo de retorno `0` de pra_helper, ausencia de `style="..."` en laminas generadas, y presencia de todos los archivos `.blade.php` definidos en el plan para esa sesion. Solo si todas pasan, marca la sesion como completada y avanza.

**Por que esta prioridad**: La Constitucion (III y IV) exige integridad y secuencialidad. Las puertas convierten esas reglas en checks automaticos que impiden propagar errores a sesiones posteriores.

**Prueba Independiente**: Procesar una sesion cuyo plan declara 3 laminas pero cuya respuesta LLM solo materializa 2 archivos; la puerta debe detectar el faltante, activar el reintento y, agotados los intentos, abortar.

**Escenarios de Aceptacion**:

1. **Dado** una sesion procesada con exit code `0`, **Cuando** se escanean las laminas de `sesion[N]/`, **Entonces** ningun archivo contiene `style="..."`.
2. **Dado** el plan maestro vigente, **Cuando** se valida la sesion N, **Entonces** existe un archivo `.blade.php` por cada lamina declarada, nombrado segun su `id_kebab_case`.
3. **Dado** cualquier validacion incumplida, **Cuando** se evalua la puerta, **Entonces** la sesion NO se marca como completada y no se permite avanzar a N+1.

---

### Historia de Usuario 4 - Estado Persistente y Reanudacion (Prioridad: P2)

El orquestador mantiene `orchestration_state.json` con el estado de cada fase/sesion (pendiente / en_curso / completada / fallida, contador de intentos y reporte de validaciones). El comando `resume` retoma desde la ultima fase valida sin repetir trabajo consolidado; `status` imprime un resumen legible del progreso.

**Por que esta prioridad**: Los flujos con LLM pueden interrumpirse (timeout, red, cierre de terminal). La reanudacion evita reconstruir sesiones ya validadas y preserva la coherencia acumulada.

**Prueba Independiente**: Iniciar una corrida mock, simular interrupcion tras completar la sesion 1 de un plan de 2, y ejecutar `resume`: debe continuar directamente por la sesion 2 sin regenerar la 1.

**Escenarios de Aceptacion**:

1. **Dado** una corrida interrumpida tras la sesion K, **Cuando** se ejecuta `resume`, **Entonces** la construccion continua desde la sesion K+1.
2. **Dado** cualquier punto del flujo, **Cuando** se ejecuta `status`, **Entonces** se imprime el estado por fase/sesion con contadores de intentos.
3. **Dado** que no existe estado previo, **Cuando** se ejecuta `resume`, **Entonces** informa codigo `2` indicando que no hay corrida activa.

---

### Historia de Usuario 5 - Backend Mock Determinista para CI (Prioridad: P2)

Dos backends intercambiables detras de una interfaz comun: `mock`, que sirve respuestas prediseñadas deterministas desde fixtures (`mocks_llm/`), apto para CI sin red ni credenciales; y `opencode`, que delega en la CLI de OpenCode en modo no interactivo.

**Por que esta prioridad**: Permite probar el pipeline completo de forma 100% reproducible y sirve de base para las pruebas automatizadas del propio orquestador.

**Prueba Independiente**: Dos corridas consecutivas con `--backend mock` sobre el mismo documento en directorios temporales distintos deben generar arboles de archivos identicos byte a byte.

**Escenarios de Aceptacion**:

1. **Dado** `--backend mock`, **Cuando** se solicita el plan o una sesion, **Entonces** la respuesta proviene del fixture correspondiente y es identica en cada corrida.
2. **Dado** `--backend opencode`, **Cuando** la CLI externa no esta disponible o excede el timeout, **Entonces** aborta con codigo `3` informando el error de subprocess.
3. **Dado** un backend no reconocido, **Cuando** se pasa por argumento, **Entonces** rechaza la ejecucion con codigo `4` y mensaje de uso.

---

### Historia de Usuario 6 - Cierre con Verificacion de Calidad y Empaquetado (Prioridad: P3)

Antes del empaquetado final, el orquestador ejecuta la suite de calidad (`pytest --cov=pra_helper`) y verifica el umbral constitucional (suite verde y cobertura >= 85%). Solo entonces invoca `pra_helper.py zip` y reporta la ruta del entregable.

**Por que esta prioridad**: Asegura que ninguna iteracion del motor quede rota antes de emitir el entregable, alineandose con el mandato de Garantia de Calidad de AGENTS.md.

**Prueba Independiente**: Completar todas las sesiones de un proyecto mock; la fase final debe ejecutar pytest, validar umbrales y generar `outputs.zip`. Forzar un fallo de suite debe abortar el empaquetado con codigo `1`.

**Escenarios de Aceptacion**:

1. **Dado** todas las sesiones completadas, **Cuando** corre la fase final, **Entonces** pytest reporta cobertura y, si cumple umbrales, se genera `outputs.zip`.
2. **Dado** suite fallida o cobertura < 85%, **Cuando** se evalua la fase final, **Entonces** no se genera `outputs.zip` y el proceso sale con codigo `1`.

---

### Casos Extremos

- Documento fuente inexistente o vacio: aborta en fase `init` con codigo distinto de 0 y estado limpio.
- JSON de plan malformado persistente: `save-plan` agota reintentos y aborta con codigo `1` sin estructura parcial.
- Plan con 0 sesiones: reportado como plan invalido (codigo `2`).
- Interrupcion abrupta (kill) durante `process-session`: al reanudar, la sesion queda `en_curso`/`fallida` y se reprocesa completa.
- `orchestration_state.json` corrupto: informa codigo `2`; exige reiniciar corrida (sin reparacion silenciosa).
- Timeout del backend real: intento registrado como fallido y entra al bucle de reintentos.

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-201**: El orquestador DEBE ejecutar la secuencia completa `init` -> `save-plan` -> [`prompt-session N` -> LLM -> `process-session N`]* -> verificacion de calidad -> `zip` mediante un unico comando `run`, sin intervencion manual.
- **FR-202**: Toda mutacion de archivos del proyecto de presentacion DEBE delegarse exclusivamente en los comandos CLI de `pra_helper.py` (via subprocess); el orquestador PROHIBE escribir laminas, estilos, scripts, manifest o registros por si mismo (Constitucion III).
- **FR-203**: El orquestador SOLO puede escribir sus artefactos de control propios: `orchestration_state.json` y logs de auditoria, excluidos del paquete entregable (`outputs.zip`).
- **FR-204**: DEBE implementar un bucle de reintentos por fase/sesion con maximo configurable `--max-retries` (por defecto 3).
- **FR-205**: En cada reintento DEBE construir un prompt de reflexion de error con: fase/sesion, codigo de retorno, STDERR relevante y descripcion de la validacion incumplida.
- **FR-206**: DEBE ejecutar puertas de validacion post-sesion: (a) exit code `0` de `process-session`; (b) regex anti CSS inline sobre las laminas generadas; (c) presencia de archivos `.blade.php` por cada lamina del plan.
- **FR-207**: DEBE persistir `orchestration_state.json` con escritura atomica (archivo temporal + rename) tras cada transicion de estado.
- **FR-208**: DEBE ofrecer backends intercambiables `mock` y `opencode` detras de una interfaz comun, seleccionables por argumento CLI.
- **FR-209**: Antes del empaquetado DEBE ejecutar `pytest --cov=pra_helper` y exigir suite verde + cobertura >= 85%; en caso contrario abortar sin generar `outputs.zip`.
- **FR-210**: DEBE soportar los comandos `run`, `resume` y `status` con codigos de salida estandarizados (0, 1, 2, 3, 4).
- **FR-211**: DEBE registrar un log de auditoria por corrida con timestamp, fase, intento, resultado y duracion.
- **FR-212**: Su documentacion y mensajes deben redactarse en espanol (Constitucion V).

### Entidades Clave

- **Orquestador (`pra_orchestrator.py`)**: Script CLI que coordina fases y backends; nunca escribe artefactos del proyecto de presentacion.
- **Backend LLM (`LLMBackend`)**: Interfaz comun `generar(prompt) -> respuesta` con implementaciones `MockBackend` (fixtures deterministas) y `OpenCodeBackend` (subprocess a OpenCode CLI headless).
- **Estado de Orquestacion (`orchestration_state.json`)**: Registro persistente de fases, sesiones, intentos y reportes de validacion para reanudacion.
- **Puerta de Validacion (`ValidationReport`)**: Resultado estructurado de cada bateria de checks post-sesion (ok/fallo por regla).
- **Prompt de Reflexion de Error**: Prompt derivado del prompt original mas un anexo con el diagnostico exacto del rechazo.

---

## Criterios de Exito *(obligatorio)*

### Resultados Medibles

- **SC-201**: Flujo completo con backend mock sobre `ejemplos/introduccion_docker/documento_fuente.md` termina con codigo `0`, genera `outputs.zip` valido y requiere cero intervencion humana.
- **SC-202**: Determinismo: dos corridas mock consecutivas producen arboles de proyecto identicos byte a byte (excluyendo logs con timestamps).
- **SC-203**: Con mock programado (respuesta contaminada -> respuesta valida), la sesion se completa en <= 2 intentos y el log registra ambos intentos con su diagnostico.
- **SC-204**: Cero archivos del proyecto de presentacion escritos fuera de `pra_helper.py` (verificable por auditoria de escrituras).
- **SC-205**: La suite completa del repositorio permanece verde (30 pruebas previas + nuevas del orquestador) con cobertura de `pra_helper.py` >= 85% y cobertura de `pra_orchestrator.py` >= 85%.

---

## Suposiciones

- La CLI de OpenCode esta disponible en modo no interactivo (ej. `opencode run "<prompt>"`) para el backend real; su ausencia no afecta al backend mock.
- Las respuestas mock cubren la estructura canonica de 5 bloques definida por `pra_helper.py`.
- El numero maximo de sesiones (10) y laminas por sesion (15) hereda los limites de la especificacion 001.
- `pra_helper.py` no requiere modificaciones para esta iteracion; el orquestador lo consume como caja negra via su contrato CLI existente.
