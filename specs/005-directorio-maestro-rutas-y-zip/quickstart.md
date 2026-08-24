# Guia de Validacion Rapida (Quickstart): Directorio Maestro por Defecto, Prompt Interactivo y Entregable Autocontenido (005-directorio-maestro-rutas-y-zip)

**Fecha**: 2026-08-24

Este documento proporciona una guia rapida para validar el correcto funcionamiento de las nuevas caracteristicas introducidas en la Iteracion 005. Se recomienda ejecutar estas pruebas despues de implementar los cambios.

---

## 1. Pre-requisitos

- Acceso a una terminal con Python 3.8+.
- El repositorio del proyecto `test_opencode` clonado y dependencias instaladas.
- Se asume el `documento_fuente.md` de ejemplo en `ejemplos/introduccion_docker/documento_fuente.md`.

---

## 2. Escenarios de Prueba Manual

### Escenario 1: Creacion de Proyecto con Directorio Maestro por Defecto Existente (HU-1, SC-501)

**Objetivo**: Verificar que el proyecto se crea en `C:\laragon\www\product_samples\slides\<carpeta_proyecto>/` cuando el directorio maestro existe.

**Pasos**:
1. Asegurarse de que el directorio `C:\laragon\www\product_samples\slides` existe en su sistema.
   ```bash
   mkdir -p C:\laragon\www\product_samples\slides  # Crear si no existe
   ```
2. Ejecutar el comando `save-plan`:
   ```bash
   python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md
   ```
3. **Verificacion**:
   - Comprobar que existe la carpeta `C:\laragon\www\product_samples\slides\intro_docker/`.
   - Dentro, verificar la presencia de `presentation_plan.json` y otros archivos del proyecto.
   - La salida JSON de `save-plan` debe reportar `"proyecto": "C:\\laragon\\www\\product_samples\\slides\\intro_docker"`.

### Escenario 2: Creacion de Proyecto con Directorio Maestro Inexistente (Interactiva) (HU-2, SC-502)

**Objetivo**: Validar el prompt interactivo cuando el directorio maestro no existe y se ejecuta en un TTY.

**Pasos**:
1. Asegurarse de que el directorio `C:\laragon\www\product_samples\slides` NO existe. Si existe, eliminarlo temporalmente:
   ```bash
   rmdir /s /q C:\laragon\www\product_samples\slides  # O eliminarlo manualmente
   ```
2. Ejecutar el comando `save-plan`:
   ```bash
   python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md
   ```
3. **Interaccion**:
   - El sistema debe mostrar un mensaje de advertencia y solicitar una ruta.
   - Introducir una ruta de directorio **existente** (ej. `C:\Users\<tu_usuario>\Desktop\mis_presentaciones`).
   - **Prueba de Reintento**: Si en el primer intento ingresa una ruta invalida (`C:\ruta\inexistente`), el sistema debe pedir un reintento (hasta 3).
4. **Verificacion**:
   - El proyecto `intro_docker` debe crearse bajo la ruta que usted ingreso interactivamente.

### Escenario 3: Creacion de Proyecto con Directorio Maestro Inexistente (No-Interactiva) (HU-3, SC-503)

**Objetivo**: Verificar que el sistema aborta limpiamente en entornos no TTY cuando el directorio maestro no existe.

**Pasos**:
1. Asegurarse de que `C:\laragon\www\product_samples\slides` NO existe (eliminar si es necesario).
2. Ejecutar el comando `save-plan` redirigiendo `stdin` desde `/dev/null` (simulando no-TTY):
   ```bash
   python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md < NUL  # Windows
   # O en Linux/Git Bash: python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md < /dev/null
   ```
3. **Verificacion**:
   - El comando debe fallar inmediatamente con un `exit code 1`.
   - La salida STDERR (o STDOUT si es JSON) debe contener un mensaje de error claro (ej. `{"error": "PRA_OUTPUT_DIR_INVALID", ...}`).
   - NO se debe crear ningun directorio de proyecto.

### Escenario 4: Empaquetado `outputs.zip` Autocontenido (HU-4, SC-504)

**Objetivo**: Verificar que `outputs.zip` se crea dentro del directorio del proyecto y se excluye de su propio contenido.

**Pasos**:
1. Completar el Escenario 1 o 2 para tener un proyecto `intro_docker` creado y con al menos una sesion generada (ej. `python pra_helper.py prompt-session 1 && python pra_helper.py process-session 1 "{...mock_response...}"`).
2. Ejecutar el comando `zip`:
   ```bash
   python pra_helper.py zip
   ```
3. **Verificacion**:
   - Comprobar que existe el archivo `C:\laragon\www\product_samples\slides\intro_docker\outputs.zip`.
   - Descomprimir `outputs.zip` e inspeccionar su contenido: debe contener todos los archivos del proyecto, pero NO debe haber un archivo `outputs.zip` anidado dentro de si mismo.
   - Verificar que NO existe ningun `outputs.zip` en la raiz de `C:\laragon\www\product_samples\slides`.

### Escenario 5: Override con `PRA_OUTPUT_DIR` (HU-1, SC-501)

**Objetivo**: Verificar que la variable de entorno `PRA_OUTPUT_DIR` sobreescribe el directorio maestro por defecto.

**Pasos**:
1. Crear un directorio temporal (ej. `C:\temp\custom_pra_output`).
2. Ejecutar `save-plan` configurando `PRA_OUTPUT_DIR`:
   ```bash
   set PRA_OUTPUT_DIR=C:\temp\custom_pra_output && python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md  # Windows
   # O en Linux/Git Bash: PRA_OUTPUT_DIR=/tmp/custom_pra_output python pra_helper.py save-plan ejemplos/introduccion_docker/documento_fuente.md
   ```
3. **Verificacion**:
   - El proyecto `intro_docker` debe crearse bajo `C:\temp\custom_pra_output\intro_docker/`.
   - Luego, ejecutar `zip` con la misma variable de entorno y verificar que `C:\temp\custom_pra_output\intro_docker\outputs.zip` se crea correctamente.

---

## 3. Ejecucion de la Suite de Pruebas Automatizadas (SC-505)

**Objetivo**: Asegurar que todos los tests unitarios, de integracion y constitucionales pasan, y que la cobertura de codigo se mantiene.

**Pasos**:
1. Ejecutar la suite completa de pruebas:
   ```bash
   python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
   ```
2. **Verificacion**:
   - Todas las pruebas deben pasar (100% aprobado).
   - La cobertura de codigo para `pra_helper.py` y `pra_orchestrator.py` debe ser igual o superior al 85%.
