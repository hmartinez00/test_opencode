# Especificacion de Funcionalidad: Subdirectorio Maestro para Proyectos Generados (004-subdirectorio-maestro-proyectos-pra)

**Rama de Funcionalidad**: `004-subdirectorio-maestro-proyectos-pra`

**Fecha de Creacion**: 2026-08-24

**Estado**: Borrador

**Entrada**: Requerimiento del usuario: "Los directorios creados para cada presentacion deben alojarse en un subdirectorio maestro en lugar de la raiz del repositorio" (nombre elegido: `output_projects/`).

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Creacion de Proyectos Bajo el Subdirectorio Maestro (Prioridad: P1)

Cuando el usuario ejecuta `pra_helper.py save-plan` con un plan valido, el sistema crea la carpeta del proyecto (`carpeta_snake_case`) dentro del subdirectorio maestro `output_projects/` de la raiz del workspace, en lugar de crearla directamente en la raiz. La raiz del repositorio permanece limpia, conteniendo solo codigo fuente, especificaciones y documentacion.

**Por que esta prioridad**: Es el cambio central de la iteracion. Sin el aislamiento, cada presentacion generada contamina la raiz del repositorio con artefactos que no deben versionarse.

**Prueba Independiente**: Ejecutar `save-plan` en un directorio temporal aislado y verificar que existe `<tmp>/output_projects/intro_docker/presentation_plan.json` y que NO existe `<tmp>/intro_docker/`.

**Escenarios de Aceptacion**:

1. **Dado** un plan maestro valido, **Cuando** se ejecuta `save-plan`, **Entonces** la estructura completa del proyecto se crea bajo `output_projects/<carpeta_snake_case>/`.
2. **Dado** cualquier corrida exitosa, **Cuando** se inspecciona la raiz del workspace, **Entonces** ninguna carpeta de proyecto de presentacion aparece directamente en ella.
3. **Dado** un proyecto recien creado, **Cuando** se lee la salida JSON de `save-plan`, **Entonces** el campo `proyecto` y todas las rutas de `archivos_creados` son relativas y apuntan bajo `output_projects/`.

---

### Historia de Usuario 2 - Localizacion Confiable del Proyecto Activo (Prioridad: P1)

Los comandos posteriores a la creacion (`prompt-session`, `process-session`, `zip`) localizan el proyecto activo buscando primero en `output_projects/`; si no encuentran ningun proyecto alli, aplican un fallback de compatibilidad escaneando la raiz (proyectos legacy creados antes de esta iteracion).

**Por que esta prioridad**: Si los comandos de sesion no encontraran el proyecto tras el cambio de ubicacion, el flujo completo quedaria roto. El fallback evita romper proyectos existentes sin exigir migracion manual.

**Prueba Independiente**: Con un proyecto creado via `save-plan`, ejecutar secuencialmente `prompt-session 1`, `process-session 1 <respuesta>` y `zip`: todos deben operar sobre `output_projects/intro_docker/` sin configuracion adicional.

**Escenarios de Aceptacion**:

1. **Dado** un proyecto vigente bajo `output_projects/`, **Cuando** se ejecuta cualquier comando de lectura/escritura de sesion, **Entonces** lo resuelve automaticamente dentro del subdirectorio maestro.
2. **Dado** un proyecto legacy ubicado en la raiz (sin subdirectorio maestro), **Cuando** se ejecuta `prompt-session` o `process-session`, **Entonces** el fallback lo encuentra y el flujo continua funcionando.
3. **Dado** proyectos en ambas ubicaciones simultaneamente, **Cuando** se busca el proyecto activo, **Entonces** tiene precedencia el ubicado en `output_projects/`.

---

### Historia de Usuario 3 - Empaquetado Limpio (Prioridad: P2)

El comando `zip` genera el entregable `outputs.zip` dentro del subdirectorio maestro (`output_projects/outputs.zip`), manteniendo las exclusiones vigentes (artefactos de orquestacion excluidos) y preservando la integridad de laminas Blade, estilos, scripts, manifest y registros.

**Por que esta prioridad**: El zip es el entregable final; ubicarlo fuera de la raiz completa el objetivo de raiz limpia de punta a punta.

**Prueba Independiente**: Completar un proyecto y ejecutar `zip`; verificar que `output_projects/outputs.zip` existe, contiene el arbol completo del proyecto y que la raiz no contiene ningun `outputs.zip`.

**Escenarios de Aceptacion**:

1. **Dado** un proyecto completado, **Cuando** se ejecuta `zip`, **Entonces** el paquete se genera en `output_projects/outputs.zip`.
2. **Dado** el contenido del zip, **Cuando** se inspeccionan sus entradas, **Entonces** incluye todas las carpetas/laminas del proyecto y excluye `orchestration_state.json` y logs de auditoria.
3. **Dado** una invocacion de `zip` sin proyecto existente, **Cuando** se evalua el comando, **Entonces** aborta con codigo distinto de 0 igual que en la iteracion anterior.

---

### Historia de Usuario 4 - Configurabilidad del Directorio de Salida (Prioridad: P3)

El subdirectorio maestro por defecto es `output_projects/`, pero puede personalizarse mediante la variable de entorno `PRA_OUTPUT_DIR`, tanto en el motor como en el orquestador. Esto permite entornos donde la convencion de nombres difiere (CI, montajes alternativos).

**Por que esta prioridad**: Da flexibilidad operativa sin introducir banderas CLI nuevas en cada comando; el default cubre el 100% de los casos normales.

**Prueba Independiente**: Definir `PRA_OUTPUT_DIR=custom_out` en un entorno aislado, correr `save-plan` + `zip`, y verificar que todo el arbol (incluido el zip) queda bajo `custom_out/`.

**Escenarios de Aceptacion**:

1. **Dado** `PRA_OUTPUT_DIR` definido, **Cuando** se crea un proyecto, **Entonces** se aloja bajo esa ruta en lugar de `output_projects/`.
2. **Dado** `PRA_OUTPUT_DIR` ausente, **Cuando** se crea un proyecto, **Entonces** se usa el default `output_projects/`.

---

### Historia de Usuario 5 - Orquestador Desatendido Respeta la Nueva Ubicacion (Prioridad: P2)

La corrida desatendida `pra_orchestrator.py run` produce todo su resultado dentro del subdirectorio maestro: proyecto, laminas, registros y `outputs.zip`. Las puertas de validacion post-sesion (anti CSS inline, laminas completas) escanean las rutas nuevas, y `orchestration_state.json` registra las rutas correctas del proyecto.

**Por que esta prioridad**: El orquestador es hoy la via principal de uso; si sus puertas validan rutas viejas, la automatizacion reportaria falsos fallos.

**Prueba Independiente**: Ejecutar `python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend mock` en workspace aislado: exit 0, arbol completo bajo `output_projects/intro_docker/` y cero carpetas de proyecto en la raiz.

**Escenarios de Aceptacion**:

1. **Dado** una corrida mock completa, **Cuando** termina con exit 0, **Entonces** `buscar_proyecto()` del orquestador resolvio el proyecto dentro del subdirectorio maestro.
2. **Dado** las puertas post-sesion, **Cuando** se validan las laminas, **Entonces** el regex anti CSS inline y el chequeo de laminas faltantes operan sobre `output_projects/sesion[N]/`.
3. **Dado** el estado persistido, **Cuando** se consulta `status` o se reanuda con `resume`, **Entonces** las rutas registradas apuntan al subdirectorio maestro y la reanudacion funciona sin reprocesar sesiones completadas.

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-401**: TODO proyecto nuevo DEBE crearse dentro del subdirectorio maestro (default `output_projects/`), nunca directamente en la raiz del workspace.
- **FR-402**: La ruta base DEBE centralizarse en una constante unica de `pra_helper.py`, overridable por la variable de entorno `PRA_OUTPUT_DIR`; prohibido duplicar literales de ruta en multiples puntos del motor.
- **FR-403**: La localizacion del proyecto activo (`find_project_dir()` en el motor, `buscar_proyecto()` en el orquestador) DEBE buscar primero en el subdirectorio maestro y aplicar fallback de lectura sobre la raiz solo para proyectos legacy.
- **FR-404**: El comando `zip` DEBE generar el entregable dentro del subdirectorio maestro y mantener las exclusiones de artefactos de orquestacion.
- **FR-405**: Toda salida JSON de los comandos CLI DEBE reportar rutas coherentes con la nueva ubicacion (campos `proyecto`, `archivos_creados`).
- **FR-406**: El orquestador DEBE persistir en `orchestration_state.json` las rutas del proyecto conforme a la nueva ubicacion, sin cambiar su esquema de fases ni codigos de salida (0/1/2/3/4).
- **FR-407**: NO se requiere migracion automatica de proyectos preexistentes en la raiz; estos permanecen legibles via fallback.
- **FR-408**: La suite de pruebas DEBE actualizarse y ampliarse para cubrir la nueva ubicacion (unitarias, integracion y constitucionales), manteniendose verde con cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
- **FR-409**: La documentacion (`AGENTS.md`, `README.md`, `SESION_PRA_RESUMEN.md`) DEBE reflejar el nuevo arbol de directorios.
- **FR-410**: Ninguna regla constitucional previa (cero CSS inline, secuencialidad de sesiones, punto unico de escritura) puede verse afectada por este cambio.

### Entidades Clave

- **Subdirectorio Maestro (`OUTPUT_BASE_DIR`)**: Carpeta contenedora de todos los proyectos generados. Default `output_projects/`, configurable via `PRA_OUTPUT_DIR`.
- **Proyecto de Presentacion**: Arbol autocontenido de plan, registros, laminas, estilos/scripts acumulados y adiciones por sesion. Su ubicacion pasa de `<raiz>/<carpeta>` a `<raiz>/output_projects/<carpeta>`.
- **Fallback Legacy**: Estrategia de busqueda secundaria sobre la raiz que mantiene legibles los proyectos anteriores a esta iteracion.

---

## Criterios de Exito *(obligatorio)*

### Resultados Medibles

- **SC-401**: Corrida E2E mock sobre `ejemplos/introduccion_docker/documento_fuente.md` termina con exit 0 y genera el arbol completo exclusivamente bajo `output_projects/intro_docker/`.
- **SC-402**: Tras la corrida E2E, la raiz del workspace NO contiene ninguna carpeta de proyecto ni `outputs.zip` nuevos.
- **SC-403**: La suite completa permanece verde (95+ pruebas) con cobertura >= 85% en ambos modulos del motor/orquestador.
- **SC-404**: Se mantiene el determinismo byte-a-byte de dos corridas mock consecutivas (excluyendo timestamps).
- **SC-405**: Un proyecto legacy simulado en la raiz sigue siendo procesable por `prompt-session`/`process-session` gracias al fallback.

---

## Casos Extremos

- `PRA_OUTPUT_DIR` apunta a ruta inexistente: debe crearse automaticamente en `save-plan` (mkdir parents).
- `PRA_OUTPUT_DIR` apunta a un archivo (no directorio): abortar con error claro en `save-plan`.
- Colision de nombres: proyecto con mismo `carpeta_snake_case` en raiz (legacy) y en `output_projects/`: precede el del subdirectorio maestro.
- `zip` sin proyecto en ninguna ubicacion: comportamiento previo intacto (error, exit distinto de 0).
- Corrida de orquestador interrumpida antes del cambio de ubicacion: `resume` sobre estado viejo debe seguir resolviendo el proyecto via fallback o reiniciar limpio, nunca corromper artefactos.

---

## Suposiciones

- No hay despliegues externos dependientes de la ubicacion raiz de los proyectos (el zip es el unico entregable consumido).
- Los proyectos ya generados en la raiz (p. ej. `intro_docker/` actual) pueden eliminarse o migrarse manualmente por el usuario; el sistema no los migra.
- Los limites de sesiones (10) y laminas por sesion (15) heredados de la especificacion 001 no cambian.
