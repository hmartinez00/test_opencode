# Especificacion de Funcionalidad: Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Rama de Funcionalidad**: `005-directorio-maestro-rutas-y-zip`

**Fecha de Creacion**: 2026-08-24

**Estado**: Borrador

**Entrada**: Requerimiento del usuario:
1. Cambiar el directorio maestro por defecto donde se alojan las presentaciones generadas de `C:\laragon\www\test_opencode\output_projects` a `C:\laragon\www\product_samples\slides`.
2. Si `C:\laragon\www\product_samples\slides` no existe al momento de generar, el sistema debe solicitar interactivamente al usuario una ruta de directorio existente.
3. El entregable `outputs.zip` debe alojarse dentro del subdirectorio del proyecto generado (ej. `C:\laragon\www\product_samples\slides\<carpeta_proyecto>\outputs.zip`).

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Nueva Ruta Maestra por Defecto (Prioridad: P1)

Cuando el usuario ejecuta la creacion de un proyecto (ej. `pra_helper.py save-plan` o `pra_orchestrator.py run`), el sistema busca alojar el proyecto generado dentro de `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/` por defecto, a menos que la variable de entorno `PRA_OUTPUT_DIR` este definida para sobreescribir dicha ubicacion.

**Por que esta prioridad**: Establece la nueva convencion de salida del negocio para consolidar las presentaciones generadas directamente en la carpeta de muestras de producto.

**Prueba Independiente**: Con el directorio por defecto presente en el sistema, ejecutar `save-plan` en entorno de prueba y verificar que la carpeta del proyecto se crea bajo `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/`.

**Escenarios de Aceptacion**:
1. **Dado** que la ruta por defecto existe, **Cuando** se ejecuta `save-plan`, **Entonces** el proyecto se crea bajo `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/`.
2. **Dado** la variable `PRA_OUTPUT_DIR` configurada con otra ruta valida (ej. `C:\custom_path`), **Cuando** se crea un proyecto, **Entonces** la variable tiene precedencia y se utiliza `C:\custom_path\<carpeta_proyecto>/`.

---

### Historia de Usuario 2 - Prompt Interactivo por Ausencia del Directorio Maestro (Prioridad: P1)

Si la ruta del directorio maestro por defecto (o la configurada por env var) NO existe en el disco al momento de iniciar la generacion, el sistema detecta la ausencia e interrumpe el flujo solicitando al usuario por consola (`stdin`) que proporcione una ruta de directorio existente valida.

**Por que esta prioridad**: Evita fallos silenciosos y permite al usuario definir dinamicamente una ubicacion valida en disco sin necesidad de reiniciar la configuracion.

**Prueba Independiente**: Simular la inexistencia del directorio maestro por defecto en una sesion interactiva (TTY activa), ejecutar `save-plan` e ingresar una ruta valida existente a la pregunta de consola; verificar que el proyecto se aloja en la ruta ingresada.

**Escenarios de Aceptacion**:
1. **Dado** que la ruta por defecto no existe y el entorno es interactivo (TTY activo), **Cuando** se ejecuta la creacion de un proyecto, **Entonces** la CLI muestra un mensaje de advertencia e ingresa a un prompt interactivo solicitando una ruta existente.
2. **Dado** que el usuario ingresa una ruta existente valida, **Cuando** la CLI valida `os.path.isdir()`, **Entonces** se acepta la ruta y continua la creacion del proyecto dentro de ella.
3. **Dado** que el usuario ingresa una ruta inexistente o invalida, **Cuando** se valida la entrada, **Entonces** el sistema muestra un mensaje de error y permite hasta 3 reintentos antes de abortar.

---

### Historia de Usuario 3 - Manejo de Ausencia de Directorio en Entornos No Interactivos (CI/CD / Automation) (Prioridad: P1)

Si la ruta del directorio maestro NO existe y la ejecucion ocurre en un entorno no interactivo (sin TTY o subproceso automatizado sin entrada de consola), el sistema aborta de inmediato con una salida descriptiva de error y codigo de salida no cero.

**Por que esta prioridad**: Previene cuelgues indefinidos (hangs) en subprocesos, scripts de CI/CD u orquestaciones desatendidas que intenten leer `stdin` en segundo plano.

**Prueba Independiente**: Ejecutar `save-plan` o `pra_orchestrator run` apuntando a un directorio inexistente en entorno no TTY (ej. redirigiendo stdin desde nulo) y comprobar que el proceso finaliza de inmediato con exit code 1.

**Escenarios de Aceptacion**:
1. **Dado** un entorno no TTY y una ruta maestra inexistente, **Cuando** el sistema evalua la ruta base, **Entonces** aborta inmediatamente reportando el error en JSON/STDERR sin intentar leer consola.
2. **Dado** la cancelacion o aborto por no-TTY, **Cuando** se lee el mensaje de error, **Entonces** sugiere explícitamente definir `PRA_OUTPUT_DIR` o crear el directorio maestro antes de ejecutar.

---

### Historia de Usuario 4 - Entregable `outputs.zip` Autocontenido en el Proyecto (Prioridad: P1)

El comando `zip` (`pra_helper.py zip` o fase final del orquestador) genera el entregable comprimido `outputs.zip` **dentro del propio subdirectorio del proyecto** (ej. `<directorio_maestro>/<carpeta_proyecto>/outputs.zip`).

**Por que esta prioridad**: Mantiene cada proyecto autocontenido con su propio entregable `.zip`, eliminando sobreescrituras entre diferentes presentaciones en el directorio maestro.

**Prueba Independiente**: Ejecutar `zip` sobre un proyecto completado y comprobar que existe `<directorio_maestro>/<carpeta_proyecto>/outputs.zip`, y que al inspeccionar el comprimido no se incluye recursivamente el propio `outputs.zip`.

**Escenarios de Aceptacion**:
1. **Dado** un proyecto completado en `<directorio_base>/<carpeta_proyecto>`, **Cuando** se ejecuta `zip`, **Entonces** se crea `<directorio_base>/<carpeta_proyecto>/outputs.zip`.
2. **Dado** el proceso de zipeado, **Cuando** se empaquetan los archivos del proyecto, **Entonces** se excluye de forma explicita la entrada `outputs.zip` para prevenir bucles de recursividad.
3. **Dado** el directorio maestro, **Cuando** finaliza la ejecucion de `zip`, **Entonces** NO existe ningun archivo `outputs.zip` suelto directamente en la raiz del directorio maestro.

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-501**: La constante de ruta base por defecto pasa a ser `C:\laragon\www\product_samples\slides` (manejada via `Path` para soporte multiplataforma), manteniendo la variable de entorno `PRA_OUTPUT_DIR` como mecanismo de sobreescritura de maxima precedencia.
- **FR-502**: Se implementa una funcion centralizada de resolucion de directorio base (`resolve_output_base_dir()`) en `pra_helper.py` que verifica si la ruta configurada existe.
- **FR-503**: Si la ruta base no existe y `sys.stdin.isatty()` es `True`, `resolve_output_base_dir()` solicita interactivamente una ruta de directorio existente al usuario, validando la entrada via `os.path.isdir()`. Permite un maximo de 3 reintentos.
- **FR-504**: Si la ruta base no existe y `sys.stdin.isatty()` es `False`, el proceso aborta con exit code 1 y emite un mensaje formateado JSON con la clave `error` que indica la ausencia del directorio y las alternativas de remediacion.
- **FR-505**: El comando `zip` (`cmd_zip`) debe guardar `outputs.zip` en `<project_dir>/outputs.zip` en lugar de `<OUTPUT_BASE_DIR>/outputs.zip`.
- **FR-506**: El comando `zip` debe excluir explicitamente la lectura/inclusión de `outputs.zip` al recorrer los archivos del proyecto.
- **FR-507**: `pra_orchestrator.py` utiliza la misma logica de resolucion de directorio base y valida la existencia de `<project_dir>/outputs.zip` al finalizar la fase `zip`.
- **FR-508**: Las funciones de localizacion del proyecto activo (`find_project_dir()` y `buscar_proyecto()`) deben buscar primero en la ruta resuelta por `resolve_output_base_dir()`, manteniendo los fallbacks legados vigentes.
- **FR-509**: Toda la suite de pruebas automatizadas debe actualizarse para aislar la nueva ruta por defecto (usando fixtures de `tmp_path` y monkeypatching de `PRA_OUTPUT_DIR`) y agregar pruebas unitarias e integracion para el prompt interactivo y la nueva ubicacion del zip.
- **FR-510**: Se garantiza el cumplimiento de las 5 reglas constitucionales (Cero CSS inline, JS acotado, preservacion determinista via pra_helper, construccion progresiva plan-first, documentacion en espanol).

---

## Criterios de Exito *(obligatorio)*

### Resultados Medibles

- **SC-501**: Una ejecucion de `save-plan` en un entorno donde `C:\laragon\www\product_samples\slides` existe ubica el proyecto en `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/`.
- **SC-502**: Ejecutar `save-plan` sin que exista el directorio maestro predeterminado en un entorno interactivo solicita la ruta, acepta una existente y crea el proyecto en ella.
- **SC-503**: Ejecutar `save-plan` en entorno no TTY sin el directorio maestro falla inmediatamente con exit code 1.
- **SC-504**: La ejecucion de `zip` crea `<project_dir>/outputs.zip` conteniendo la estructura del proyecto y excluyendo el propio `.zip`.
- **SC-505**: Toda la suite de pruebas `pytest` se mantiene en verde (100% de tests aprobados) con una cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.

---

## Casos Extremos

- El usuario ingresa espacios en blanco o comillas alrededor de la ruta en el prompt interactivo: el sistema debe aplicar `.strip('"\' ')` antes de validar la ruta.
- El usuario cancela el prompt interactivo con `Ctrl+C` (`KeyboardInterrupt`): el sistema atrapa la excepcion y aborta limpiamente con exit code 1.
- La carpeta del proyecto ya contiene un `outputs.zip` previo: el comando `zip` lo sobreescribe limpiamente sin incluirlo en el arbol comprimido.
- Se ejecuta `resume` u operacion de lectura de sesion cuando el directorio maestro ha sido cambiado mediante variable de entorno entre ejecuciones: la busqueda debe resolver a traves de los fallbacks de ruta.

---

## Suposiciones

- El sistema operativo en entornos de produccion locales tendra Laragon instalado en `C:\laragon\www\`.
- Para ejecuciones en plataformas no Windows (Linux/Mac) o entornos CI, la ruta por defecto `C:\laragon\www\product_samples\slides` no existira por defecto, lo que disparara la solicitud interactiva o requerira definir `PRA_OUTPUT_DIR` en los scripts de CI.
