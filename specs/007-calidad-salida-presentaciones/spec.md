# Especificacion de Funcionalidad: Calidad de Salida de Presentaciones PRA (007-calidad-salida-presentaciones)

**Rama de Funcionalidad**: `007-calidad-salida-presentaciones`

**Fecha de Creacion**: 2026-08-31

**Estado**: Borrador

**Entrada**: Una corrida completa de PRA (manual u orquestador) produce archivos finales que no renderizan correctamente en Laravel/Reveal.js sin retoques manuales. Esta iteracion define y automatiza las correcciones para que el resultado final sea directamente integrable, y endurece el flujo ante respuestas LLM grandes y multiples proyectos.

---

## Objetivo

Garantizar que el entregable final de PRA renderice en la aplicacion Laravel sin intervencion manual, y que el flujo manual/orquestador sea robusto ante respuestas LLM grandes y multiples proyectos en el directorio base.

Flujo objetivo:

```text
init -> save-plan -> sesiones -> consolidate -> pytest -> zip
```

## Problemas detectados en la corrida de validacion (Modulo 3 - Estructuras de Datos)

1. **P1 (Interpolacion invalida)**: `manifest.blade.php`, `assets/styles.blade.php` y `assets/scripts.blade.php` usan `{{$presentation->folder_name}}` en vez de `{$presentation->folder_name}`, rompiendo la resolucion de la ruta del proyecto.
2. **P2 (Sin envoltura CSS)**: `assets/styles_blade/css/sesionN_styles.blade.php` se genera como CSS crudo sin `<style>...</style>`.
3. **P3 (Sin envoltura JS)**: `assets/styles_blade/js/sesionN_scripts.blade.php` se genera como JS crudo sin `<script>...</script>`.
4. **P4 (Argumentos de linea de comandos)**: `process-session` recibe la respuesta LLM como argumento posicional y supera el limite de 32767 caracteres de Windows (`WinError 206`).
5. **P5 (Seleccion de proyecto)**: `find_project_dir`/`buscar_proyecto` eligen el primer proyecto del directorio base, no el proyecto activo.
6. **P6 (Titulos de lamina)**: el `data-title` del manifest final muestra el id crudo (`s1-portada`) en vez de un titulo legible.

## Historias de Usuario y Pruebas

### Historia de Usuario 1 - Interpolacion de ruta valida (P1) (Prioridad: P1)

Como integrador Laravel, necesito que todas las referencias al `folder_name` del proyecto usen interpolacion Blade valida.

**Prueba Independiente**: Consolidar un proyecto y verificar que `manifest.blade.php`, `assets/styles.blade.php` y `assets/scripts.blade.php` contienen `{$presentation->folder_name}` y no contienen `{{$presentation->folder_name}}` ni `{{{$presentation->folder_name}}}`.

**Escenarios de Aceptacion**:

1. Dado un proyecto consolidado, cuando se inspeccionan los entry points, entonces usan `{$presentation->folder_name}`.
2. Los tres archivos (manifest, assets/styles, assets/scripts) respetan la misma convencion.
3. La interpolacion no aparece duplicada ni con llaves anidadas.

### Historia de Usuario 2 - Assets envueltos (P2 y P3) (Prioridad: P1)

Como integrador Laravel, necesito que los fragmentos CSS y JS finales esten envueltos en sus etiquetas correspondientes.

**Prueba Independiente**: Consolidar y verificar que `assets/styles_blade/css/*.blade.php` comienza con `<style>` y `assets/styles_blade/js/*.blade.php` con `<script>`.

**Escenarios de Aceptacion**:

1. Cada fragmento CSS final inicia con `<style>` y termina con `</style>`.
2. Cada fragmento JS final inicia con `<script>` y termina con `</script>`.
3. Ejecutar `consolidate` dos veces no duplica la envoltura (idempotencia).

### Historia de Usuario 3 - Respuesta LLM por archivo (P4) (Prioridad: P1)

Como usuario del flujo, necesito que `process-session` procese respuestas LLM grandes en Windows sin exceder el limite de argumentos.

**Prueba Independiente**: Llamar a `process-session` con `--respuesta-file <ruta>` de una respuesta de mas de 33000 caracteres y verificar que se escriben las laminas.

**Escenarios de Aceptacion**:

1. `process-session N --respuesta-file <ruta>` procesa la respuesta contenida en el archivo.
2. El argumento posicional puede omitirse cuando se usa `--respuesta-file`.
3. Si se proveen ambos, prevalece `--respuesta-file` (documentado).
4. El orquestador usa el mecanismo de archivo para respuestas largas y limpia el archivo temporal.

### Historia de Usuario 4 - Seleccion de proyecto activo (P5) (Prioridad: P2)

Como usuario con multiples proyectos, necesito apuntar al proyecto activo de forma explicita.

**Prueba Independiente**: Fijar `PRA_ACTIVE_PROJECT=<carpeta>` con 2 proyectos bajo el directorio base y verificar que los comandos operan sobre el indicado.

**Escenarios de Aceptacion**:

1. `PRA_ACTIVE_PROJECT` prioriza el proyecto indicado cuando existe.
2. Sin la variable, se conserva el comportamiento actual (primer proyecto / cwd).
3. Si la carpeta indicada no existe, se cae al comportamiento actual sin error silencioso.

### Historia de Usuario 5 - Titulos de lamina legibles (P6) (Prioridad: P2)

Como usuario, necesito que el `data-title` del manifest final muestre titulos legibles, no ids crudos.

**Prueba Independiente**: Consolidar un plan sin `data_title` en las laminas y verificar que el manifest muestra titulos derivados legibles (ej. `Listas Teoria`), no `s1-listas-teoria`.

**Escenarios de Aceptacion**:

1. Se usa `data_title`/`titulo` del plan cuando existe.
2. Si no existe, se deriva un titulo legible de `id_kebab_case` (guiones a espacios, capitalizar).
3. El id crudo no se usa como titulo de lamina.

## Requisitos Funcionales

- **FR-701**: Los entry points finales usan `{$presentation->folder_name}` en vez de la doble llave.
- **FR-702**: Los fragmentos CSS finales se envuelven en `<style>...</style>`.
- **FR-703**: Los fragmentos JS finales se envuelven en `<script>...</script>`.
- **FR-704**: La envoltura es idempotente ante multiples `consolidate`.
- **FR-705**: `process-session` acepta `--respuesta-file <ruta>` para leer la respuesta LLM desde archivo.
- **FR-706**: El mecanismo de archivo resuelve respuestas mayores al limite de argumentos de Windows.
- **FR-707**: `pra_orchestrator.run_helper` usa archivo temporal para respuestas largas y lo limpia.
- **FR-708**: Se respeta `PRA_ACTIVE_PROJECT` para seleccionar el proyecto activo.
- **FR-709**: La seleccion explicita tiene fallback seguro al comportamiento actual.
- **FR-710**: El `data-title` del manifest usa titulo legible derivado del id cuando falta `data_title`.

## Criterios de Exito

- **SC-701**: `outputs.zip` final renderiza en Laravel sin retoques manuales.
- **SC-702**: Tres asserts de interpolacion valida pasan en manifest y assets.
- **SC-703**: Los fragmentos CSS/JS finales estan envueltos e idempotentes.
- **SC-704**: Una respuesta de 33k caracteres se procesa correctamente via archivo.
- **SC-705**: Dos proyectos coexisten y `PRA_ACTIVE_PROJECT` desambigua.
- **SC-706**: El manifest muestra titulos legibles.
- **SC-707**: La suite completa permanece en verde y la cobertura de `pra_helper.py` y `pra_orchestrator.py` es >= 85%.

## Casos Extremos

- Respuesta LLM vacia via archivo: se rechaza con diagnostico (sin laminas).
- `--respuesta-file` apuntando a archivo inexistente: error claro, exit code 1.
- Archivo temporal del orquestador no eliminado por fallo del subproceso: se limpia en bloque `finally`.
- `PRA_ACTIVE_PROJECT` con carpeta inexistente: fallback al comportamiento actual sin error silencioso.
- Fragmento CSS/JS vacio: se genera envuelto vacio o se omite, sin includes rotos.
- `consolidate` repetido sobre proyecto ya envuelto: sin doble envoltura.

## Fuera de Alcance

- Rediseñar laminas o estilos visuales.
- Migrar retroactivamente proyectos ya consolidados.
- Cambiar la arquitectura general de `pra_helper.py` u orquestador mas alla de los ajustes puntuales de esta iteracion.
- Modificar la constitucion del proyecto.
