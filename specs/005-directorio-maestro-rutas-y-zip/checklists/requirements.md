# Lista de Requisitos (Checklist): Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento proporciona un checklist de todos los requisitos funcionales y no funcionales para la Iteracion 005. Se utilizara para verificar la implementacion completa de la funcionalidad.

---

## Requisitos Funcionales (FR)

- [ ] **FR-501**: La constante de ruta base por defecto pasa a ser `C:\laragon\www\product_samples\slides` (manejada via `Path` para soporte multiplataforma), manteniendo la variable de entorno `PRA_OUTPUT_DIR` como mecanismo de sobreescritura de maxima precedencia.
- [ ] **FR-502**: Se implementa una funcion centralizada de resolucion de directorio base (`resolve_output_base_dir()`) en `pra_helper.py` que verifica si la ruta configurada existe.
- [ ] **FR-503**: Si la ruta base no existe y `sys.stdin.isatty()` es `True`, `resolve_output_base_dir()` solicita interactivamente una ruta de directorio existente al usuario, validando la entrada via `os.path.isdir()`. Permite un maximo de 3 reintentos.
- [ ] **FR-504**: Si la ruta base no existe y `sys.stdin.isatty()` es `False`, el proceso aborta con exit code 1 y emite un mensaje formateado JSON con la clave `error` que indica la ausencia del directorio y las alternativas de remediacion.
- [ ] **FR-505**: El comando `zip` (`cmd_zip`) debe guardar `outputs.zip` en `<project_dir>/outputs.zip` en lugar de `<OUTPUT_BASE_DIR>/outputs.zip`.
- [ ] **FR-506**: El comando `zip` debe excluir explicitamente la lectura/inclusion de `outputs.zip` al recorrer los archivos del proyecto.
- [ ] **FR-507**: `pra_orchestrator.py` utiliza la misma logica de resolucion de directorio base y valida la existencia de `<project_dir>/outputs.zip` al finalizar la fase `zip`.
- [ ] **FR-508**: Las funciones de localizacion del proyecto activo (`find_project_dir()` y `buscar_proyecto()`) deben buscar primero en la ruta resuelta por `resolve_output_base_dir()`, manteniendo los fallbacks legados vigentes.
- [ ] **FR-509**: Toda la suite de pruebas automatizadas debe actualizarse para aislar la nueva ruta por defecto (usando fixtures de `tmp_path` y monkeypatching de `PRA_OUTPUT_DIR`) y agregar pruebas unitarias e integracion para el prompt interactivo y la nueva ubicacion del zip.
- [ ] **FR-510**: Se garantiza el cumplimiento de las 5 reglas constitucionales (Cero CSS inline, JS acotado, preservacion determinista via pra_helper, construccion progresiva plan-first, documentacion en espanol).

---

## Requisitos No Funcionales (NFR)

- [ ] **NFR-501 (Usabilidad)**: La interaccion para solicitar una ruta de directorio debe ser clara y guiar al usuario a traves de los reintentos.
- [ ] **NFR-502 (Robustez)**: El sistema debe manejar entradas invalidas del usuario en el prompt interactivo (ej. espacios extra, comillas) sin fallar.
- [ ] **NFR-503 (Rendimiento)**: La verificacion de la existencia del directorio y la logica de resolucion no deben introducir latencia perceptible en el flujo de trabajo normal.
- [ ] **NFR-504 (Seguridad)**: El sistema no debe permitir que se ingresen rutas que puedan comprometer la seguridad del sistema (ej. inyeccion de comandos), aunque `os.path.isdir()` ya mitiga esto parcialmente.
- [ ] **NFR-505 (Mantenibilidad)**: La logica de resolucion de ruta base debe estar centralizada y ser facilmente testeable y modificable.
- [ ] **NFR-506 (Observabilidad)**: Los mensajes de error para entornos no-TTY deben ser lo suficientemente descriptivos para diagnosticar el problema de forma remota.

---

## Criterios de Exito (SC)

- [ ] **SC-501**: Una ejecucion de `save-plan` en un entorno donde `C:\laragon\www\product_samples\slides` existe ubica el proyecto en `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/`.
- [ ] **SC-502**: Ejecutar `save-plan` sin que exista el directorio maestro predeterminado en un entorno interactivo solicita la ruta, acepta una existente y crea el proyecto en ella.
- [ ] **SC-503**: Ejecutar `save-plan` en entorno no TTY sin el directorio maestro falla inmediatamente con exit code 1.
- [ ] **SC-504**: La ejecucion de `zip` crea `<project_dir>/outputs.zip` conteniendo la estructura del proyecto y excluyendo el propio `.zip`.
- [ ] **SC-505**: Toda la suite de pruebas `pytest` se mantiene en verde (100% de tests aprobados) con una cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
