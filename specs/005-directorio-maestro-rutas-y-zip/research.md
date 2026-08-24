# Decisiones Tecnicas: Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento registra las decisiones tecnicas clave tomadas durante la fase de investigacion para la implementacion de la Iteracion 005, que modifica la gestion del directorio maestro de salida, la interaccion con el usuario y la ubicacion del entregable `outputs.zip`.

---

## D-501: Ruta Base por Defecto y Resolucion de `OUTPUT_BASE_DIR`

**Problema**: La ruta base por defecto de los proyectos generados debe cambiar a `C:\laragon\www\product_samples\slides`, manteniendo la sobreescritura via `PRA_OUTPUT_DIR`.

**Opciones Evaluadas**:
1. Hardcodear la nueva ruta como un literal de string en cada punto del codigo donde se usa `OUTPUT_BASE_DIR`.
2. Definir una constante `DEFAULT_OUTPUT_BASE_DIR` y una funcion `resolve_output_base_dir()` que la utilice, priorizando `PRA_OUTPUT_DIR`.

**Decision**: Opcion 2.
- **Justificacion**: La centralizacion en una constante (`DEFAULT_OUTPUT_BASE_DIR = Path(r"C:\laragon\www\product_samples\slides")`) y una funcion de resolucion (`resolve_output_base_dir()`) asegura un unico punto de verdad para la logica de la ruta base. Esto mejora la mantenibilidad, facilita las pruebas (mocking de la variable de entorno o de la funcion de resolucion) y permite una logica mas compleja (como la validacion de existencia e interaccion con el usuario) sin duplicacion. El uso de `Path` garantiza la compatibilidad multiplataforma al manejar correctamente los separadores de ruta.
- **Impacto**: `pra_helper.py` y `pra_orchestrator.py` deben importar y utilizar esta funcion de resolucion.

---

## D-502: Logica de Interaccion para Directorio Maestro Inexistente

**Problema**: Si el directorio maestro (`OUTPUT_BASE_DIR` resuelta) no existe, el sistema debe reaccionar de forma diferente segun si la ejecucion es interactiva o no.

**Opciones Evaluadas**:
1. Siempre abortar con error si el directorio no existe.
2. Siempre crear el directorio maestro con `mkdir(parents=True, exist_ok=True)`.
3. Implementar un comportamiento condicional: prompt interactivo en TTY, aborto en no-TTY.

**Decision**: Opcion 3.
- **Justificacion**: La opcion 1 no cumple con el requisito de ofrecer una alternativa al usuario. La opcion 2 entra en conflicto con la solicitud de interaccion del usuario. La opcion 3 (`sys.stdin.isatty()` para detectar TTY) satisface ambos requisitos (HU-2 y HU-3). Permite a los usuarios interactivos corregir la ruta sobre la marcha y evita cuelgues en entornos automatizados. El limite de 3 reintentos en modo interactivo evita bucles infinitos.
- **Impacto**: Se requiere logica que detecte `isatty()` y gestione `input()` en `resolve_output_base_dir()`. En entornos no TTY, un `sys.exit(1)` con mensaje JSON descriptivo es necesario.

---

## D-503: Ubicacion del Entregable `outputs.zip`

**Problema**: El `outputs.zip` debe moverse desde la raiz del directorio maestro (`output_projects/outputs.zip` o `slides/outputs.zip`) a dentro del subdirectorio de cada proyecto generado (`slides/<proyecto>/outputs.zip`).

**Opciones Evaluadas**:
1. Mantener la ubicacion actual (`<OUTPUT_BASE_DIR>/outputs.zip`).
2. Moverlo a `<project_dir>/outputs.zip` y excluirlo de la compresion.

**Decision**: Opcion 2.
- **Justificacion**: Mover el `zip` a la carpeta del proyecto resuelve HU-4, garantizando que cada presentacion tenga su propio entregable autocontenido y evitando conflictos de nombres o sobreescritura entre proyectos. La exclusion del propio `outputs.zip` de la lista de archivos a comprimir es crucial para evitar bucles infinitos y aumentar el tamano del archivo innecesariamente.
- **Impacto**: Modificacion de `cmd_zip` en `pra_helper.py` para construir la ruta del zip y para filtrar archivos durante el proceso de compresion.

---

## D-504: Persistencia de la Ruta Ingresada Interactivamente

**Problema**: Si un usuario ingresa una ruta interactiva, ¿debe esta persistir para futuras ejecuciones?

**Opciones Evaluadas**:
1. Persistencia solo por la duracion de la sesion actual del CLI.
2. Persistencia en un archivo de configuracion (ej. `.pra_config.json`).
3. Preguntar al usuario si desea guardar la ruta en `PRA_OUTPUT_DIR` (ej. `set PRA_OUTPUT_DIR=...`).

**Decision**: Opcion 1 (con una posible sugerencia de Opcion 3).
- **Justificacion**: La opcion 1 es la mas simple de implementar y la menos intrusiva. Evita la complejidad de gestionar archivos de configuracion adicionales, que podrian ser versionados por error o causar conflictos. La sugerencia de usar `PRA_OUTPUT_DIR` al finalizar (o al abortar por no-TTY) es un buen balance entre flexibilidad y simplicidad, educando al usuario sobre la opcion persistente sin forzarla.
- **Impacto**: La funcion `resolve_output_base_dir()` devolvera la ruta validada, pero no habra logica para guardarla mas alla de la memoria del proceso actual.

---

## D-505: Testabilidad de Interacciones CLI

**Problema**: Como probar de forma automatica la logica de `input()` y `isatty()`.

**Opciones Evaluadas**:
1. Pruebas manuales.
2. Monkeypatching de `sys.stdin`, `sys.stdout` y `os.isatty`.

**Decision**: Opcion 2.
- **Justificacion**: Las pruebas manuales no son escalables ni parte de la suite automatizada. El monkeypatching de estas funciones del modulo `sys` permite simular entradas de usuario, salidas y el estado TTY, garantizando la cobertura de los escenarios interactivos y no interactivos sin depender de una interaccion real.
- **Impacto**: Se requiere un fixture de `pytest` o funciones auxiliares para configurar entornos de prueba con `stdin` y `isatty` mockeados.
