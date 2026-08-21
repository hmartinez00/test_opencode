# Especificacion de Funcionalidad: Sistema de Testing y Calidad para PRA (002-sistema-testing-pra)

**Rama de Funcionalidad**: `002-sistema-testing-pra`

**Fecha de Creacion**: 2026-08-21

**Estado**: En Revision

**Entrada**: Requerimiento del usuario: "Implementar un sistema de testing robusto que garantice la calidad de la entrega de PRA sin ruptura de codigo, siguiendo el estandar Speckit."

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Cobertura de Pruebas Unitarias para Funciones del Motor (`pra_helper.py`) (Prioridad: P1)

Como desarrollador/mantenedor del sistema PRA, quiero ejecutar pruebas unitarias automatizadas sobre todas las funciones internas de `pra_helper.py` (normalización de JSONs, parsing de bloques LLM, validación regex de CSS inline, fusión de registros) para asegurar que la lógica determinista funcione correctamente en aislamiento.

**Por que esta prioridad**: `pra_helper.py` es el componente ejecutor y la única fuente de verdad para la mutación de archivos. Asegurar la corrección de sus funciones internas evita fallos silenciosos al procesar respuestas del LLM o guardar estados.

**Prueba Independiente**: Ejecutar `pytest tests/unit/` y verificar que todas las pruebas unitarias pasen sin requerir ejecución externa de LLM ni cambios en el workspace activo.

**Escenarios de Aceptacion**:
1. **Dado** un JSON de plan maestro generado por LLM con nombres de campos alternativos (`nro`, `folder_name`, `titulo_sesion`, `objetivos`), **Cuando** se ejecuta `normalize_plan()`, **Entonces** produce un JSON normalizado estandarizado con los nombres de campo esperados (`numero`, `carpeta_snake_case`, `titulo`, `objetivo_pedagogico`).
2. **Dado** una respuesta de LLM estructurada en 5 bloques, **Cuando** se ejecuta `parse_llm_response()`, **Entonces** extrae exactamente cada bloque (archivos Blade, bloque CSS, bloque JS, fragmentos manifest, JSON de actualización de registros).
3. **Dado** un contenido HTML/Blade que incluye un atributo `style="..."`, **Cuando** se invoca `validate_no_inline_css()`, **Entonces** se lanza una excepción de violación de regla constitucional y rechaza el archivo.
4. **Dado** dos colecciones de registros de clases CSS o comportamientos JS, **Cuando** se invoca `merge_registries()`, **Entonces** actualiza el estado de las clases/comportamientos existentes a `implementada: true` y añade las nuevas entradas sin duplicar.

---

### Historia de Usuario 2 - Pruebas de Integración para Comandos CLI (Prioridad: P1)

Como desarrollador del sistema, quiero probar de manera automatizada la interfaz de comandos CLI de `pra_helper.py` (`init`, `save-plan`, `prompt-session`, `process-session`, `zip`) en un entorno temporal aislado para verificar que cada comando cree y actualice la estructura de archivos esperada con los códigos de salida correctos.

**Por que esta prioridad**: Los agentes e usuarios interactúan con PRA exclusivamente a través del contrato CLI. Probar los subcomandos de extremo a extremo garantiza la integración completa del sistema.

**Prueba Independiente**: Ejecutar `pytest tests/integration/` usando accesorios temporales (`tmp_path`) y verificar que todos los subcomandos se ejecuten con éxito sin modificar archivos reales del workspace.

**Escenarios de Aceptacion**:
1. **Dado** un documento fuente en formato Markdown, **Cuando** se ejecuta `python pra_helper.py init <doc>`, **Entonces** la CLI responde con código de salida `0` e imprime en STDOUT el prompt del Plan Maestro compilado.
2. **Dado** un payload JSON válido de plan maestro, **Cuando** se ejecuta `python pra_helper.py save-plan '<json>'`, **Entonces** se crean `presentation_plan.json`, `class_registry.json`, `js_registry.json`, `manifest_draft.blade.php` y las carpetas de sesión correspondientes.
3. **Dado** un proyecto con plan maestro guardado, **Cuando** se ejecuta `python pra_helper.py prompt-session 1`, **Entonces** se genera en STDOUT el prompt adaptado para la Sesión 1 con el contexto del plan y los registros vivos.
4. **Dado** un proyecto listo para procesar la Sesión 1, **Cuando** se ejecuta `python pra_helper.py process-session 1 '<llm_response>'`, **Entonces** se crean las láminas Blade, se acumulan estilos/scripts, se actualizan los registros JSON y se modifica el borrador del manifest.
5. **Dado** un proyecto procesado, **Cuando** se ejecuta `python pra_helper.py zip`, **Entonces** se genera el archivo `outputs.zip` comprimido conteniendo toda la estructura requerida.

---

### Historia de Usuario 3 - Validaciones de Seguridad Constitucional y Casos Extremos (Prioridad: P2)

Como auditor de calidad del proyecto, quiero probar que el sistema detenga la ejecución y devuelva errores informativos (código de salida != 0) ante violaciones intencionales de las 5 reglas constitucionales (CSS inline, intento de procesar sesiones fuera de orden, JSONs malformados, o parámetros faltantes).

**Por que esta prioridad**: Previene regresiones críticas e impide que respuestas defectuosas o desordenadas del LLM corrompan el proyecto o violen los principios fundamentales.

**Prueba Independiente**: Ejecutar `pytest tests/constitutional/` y verificar que todas las violaciones de reglas sean detectadas y abortadas con el código de error correspondiente.

**Escenarios de Aceptacion**:
1. **Dado** una respuesta de LLM para una sesión que contiene estilos inline (`style="color:red;"`), **Cuando** se intenta procesar con `process-session`, **Entonces** el proceso aborta con código de error (por ejemplo, `2` o `1`) y no guarda los archivos Blade contaminados.
2. **Dado** un proyecto donde la Sesión 1 no se ha completado, **Cuando** se intenta ejecutar `prompt-session 2` o `process-session 2`, **Entonces** el sistema aborta informando que la sesión previa debe ser completada.
3. **Dado** un JSON malformado enviado a `save-plan`, **Cuando** se ejecuta la orden, **Entonces** el sistema captura el error de deserialización y muestra un mensaje explicativo sin crear carpetas corruptas.

---

### Casos Extremos

- ¿Qué pasa si el archivo fuente proporcionado en `init` no existe? El sistema debe notificar error de archivo no encontrado y salir con código != 0.
- ¿Qué pasa si la respuesta del LLM no tiene la estructura de 5 bloques delimitados? El sistema debe notificar fallo de estructura y no modificar parcialmente el proyecto.
- ¿Qué pasa si la carpeta del proyecto ya existe al ejecutar `save-plan`? El sistema debe manejar la reutilización o reescritura segura de los archivos de registro.

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-101**: El marco de pruebas DEBE estar basado en `pytest` y ser ejecutable mediante un solo comando (`pytest`).
- **FR-102**: Las pruebas DEBEN ejecutarse en directorios temporales aislados (`tmp_path`) sin dejar residuos ni alterar archivos del repositorio.
- **FR-103**: La suite DEBE incluir pruebas unitarias para cada función clave de `pra_helper.py` (`normalize_plan`, `parse_llm_response`, `validate_no_inline_css`, `merge_registries`, `save_plan_and_structure`).
- **FR-104**: La suite DEBE incluir pruebas de integración CLI para los 5 comandos de `pra_helper.py` (`init`, `save-plan`, `prompt-session`, `process-session`, `zip`).
- **FR-105**: La suite DEBE incluir pruebas constitucionales para verificar la aplicación de las reglas (Cero CSS inline, secuencialidad estricta, encapsulamiento JS).
- **FR-106**: Las pruebas DEBEN capturar STDOUT/STDERR (`capsys` de pytest) para validar las salidas del sistema CLI.
- **FR-107**: La suite DEBE incluir un archivo `conftest.py` centralizado con accesorios (fixtures) reutilizables para documentos de prueba, JSONs de plan y respuestas LLM simuladas.
- **FR-108**: La suite DEBE ofrecer medición de cobertura de código mediante `pytest-cov`.

---

## Criterios de Exito *(obligatorio)*

### Resultados Medibles

- **SC-101**: El 100% de las pruebas automatizadas pasan con éxito (`0 failures, 0 errors`).
- **SC-102**: Cobertura de código de `pra_helper.py` de al menos el **85%**.
- **SC-103**: Tiempo total de ejecución de toda la suite de pruebas inferior a **60 segundos** (línea base medida en entorno Windows/Laragon con escaneo antivirus en tiempo real: ~27 segundos; el objetivo de diseño es un ciclo de retroalimentación rápido para el desarrollador).
- **SC-104**: Cero modificaciones colaterales en la estructura del proyecto o workspace durante la corrida de pruebas.
- **SC-105**: Inclusión de al menos 15 casos de prueba que cubran pruebas unitarias, integradas y de casos límite/constitucionales.
