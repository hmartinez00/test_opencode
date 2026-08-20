# Especificacion de Funcionalidad: Sistema de Automatizacion Progresiva de Presentaciones Reveal.js (PRA)

**Rama de Funcionalidad**: `001-sistema-automatizacion-presentaciones-pra`

**Fecha de Creacion**: 2026-08-20

**Estado**: Borrador

**Entrada**: Descripcion del usuario: "Sistema automatizado para la construccion modular y progresiva de presentaciones interactivas basadas en Reveal.js, integradas en un modulo Laravel/Blade, utilizando un enfoque de Plan Maestro y construccion por sesiones."

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Generacion e Inicializacion del Plan Maestro de Presentacion (Prioridad: P1)

El usuario proporciona un documento fuente (PDF, Jupyter Notebook, paper, documentacion tecnica o codigo) al sistema. El sistema procesa el contenido, genera un borrador del plan de presentacion completo en formato JSON (`presentation_plan.json`) que define la estructura de sesiones, objetivos pedagogicos y laminas, e inicializa los registros vacios de clases CSS (`class_registry.json`) y comportamientos JavaScript (`js_registry.json`). Ademas, crea la estructura de directorios por sesion y un borrador del manifest Blade (`manifest_draft.blade.php`).

**Por que esta prioridad**: Esta funcionalidad es la base de todo el sistema. Sin un plan maestro estructurado y registros inicializados, es imposible construir laminas de manera coherente. Es el MVP que permite pasar de un documento fuente a un esqueleto funcional.

**Prueba Independiente**: Se puede probar completamente proporcionando un documento fuente de ejemplo y verificando que se generan los archivos `presentation_plan.json`, `class_registry.json`, `js_registry.json`, `manifest_draft.blade.php` y las subcarpetas `sesion[N]/` en el directorio de salida.

**Escenarios de Aceptacion**:

1. **Dado** que el usuario proporciona un documento fuente valido, **Cuando** ejecuta el comando de generacion de plan, **Entonces** el sistema produce un archivo `presentation_plan.json` con al menos una sesion, sus objetivos y laminas definidas.
2. **Dado** que el plan maestro ha sido generado, **Cuando** se inspecciona el directorio de salida, **Entonces** existen subcarpetas `sesion1/`, `sesion2/`, etc., una por cada sesion definida en el plan.
3. **Dado** que el plan maestro ha sido generado, **Cuando** se leen los registros `class_registry.json` y `js_registry.json`, **Entonces** ambos archivos estan inicializados con las entradas iniciales del plan, cada una con el campo `implementada` en `false`.
4. **Dado** que el plan maestro ha sido generado, **Cuando** se lee `manifest_draft.blade.php`, **Entonces** contiene las secciones Blade con las entradas `<x-slide>` pendientes para cada lamina.

---

### Historia de Usuario 2 - Construccion Progresiva e Incremental por Sesiones (Prioridad: P1)

El usuario solicita construir la sesion N del plan. El sistema genera el prompt adaptado consultando el plan actual y el estado de los registros, lo envia al LLM, y al recibir la respuesta, escribe los archivos `.blade.php` de cada lamina, anexa los estilos CSS nuevos al acumulado `styles.blade.php`, anexa los scripts JS al acumulado `scripts.blade.php`, guarda las adiciones del manifest, y fusiona los nuevos registros sin duplicar clases o comportamientos ya existentes.

**Por que esta prioridad**: Esta es la funcionalidad central del sistema. Sin ella, no hay forma de convertir el plan en laminas Blade reales. Es el motor de construccion que permite crecer la presentacion sesion a sesion.

**Prueba Independiente**: Se puede probar ejecutando la construccion de la sesion 1 sobre un plan maestro inicializado y verificando que se generan los archivos Blade de laminas, que los estilos y scripts se acumulan correctamente, y que los registros se actualizan sin duplicados.

**Escenarios de Aceptacion**:

1. **Dado** que existe un plan maestro con la sesion 1 definida, **Cuando** el usuario ejecuta el comando de construccion de sesion 1, **Entonces** se generan los archivos `.blade.php` correspondientes a cada lamina de la sesion.
2. **Dado** que la sesion 1 ha sido construida, **Cuando** se inspecciona `styles.blade.php`, **Entonces** contiene los bloques CSS acumulados de la sesion 1.
3. **Dado** que la sesion 1 ha sido construida, **Cuando** se inspecciona `scripts.blade.php`, **Entonces** contiene los bloques JS acumulados de la sesion 1.
4. **Dado** que la sesion 1 ha sido construida, **Cuando** se lee `class_registry.json`, **Entonces** las clases CSS nuevas de la sesion 1 estan registradas con `implementada: true`, sin duplicar ninguna clase preexistente.
5. **Dado** que la sesion 1 ha sido construida, **Cuando** se inspecciona `manifest_additions/sesion1.blade.php`, **Entonces** contiene las entradas `<x-slide>` de la sesion 1.

---

### Historia de Usuario 3 - Garantia de Cumplimiento Constitucional (Prioridad: P2)

El sistema debe garantizar que todas las laminas generadas cumplan con las reglas no negociables establecidas en la Constitucion del proyecto: cero estilos inline, JavaScript acotado y mapeado, y preservacion determinista del estado a traves de `pra_helper.py`.

**Por que esta prioridad**: Es esencial para mantener la integridad del proyecto a largo plazo. Sin verificacion de cumplimiento, los agentes de IA podrian introducir practicas destructivas como CSS inline o JavaScript global que rompan la coherencia visual y funcional de la presentacion.

**Prueba Independiente**: Se puede probar ejecutando la construccion de una sesion y verificando que ningun archivo Blade generado contiene atributos `style="..."` y que los archivos de registros se actualizaron correctamente via `pra_helper.py` y no por edicion manual.

**Escenarios de Aceptacion**:

1. **Dado** que una sesion ha sido construida, **Cuando** se buscan atributos `style="..."` en todos los archivos `.blade.php` de laminas, **Entonces** no se encuentra ninguno.
2. **Dado** que una sesion ha sido construida, **Cuando** se inspeccionan los archivos JavaScript en `scripts_additions/`, **Entonces** cada script esta acotado y comentado indicando la lamina a la que pertenece.
3. **Dado** que una sesion ha sido procesada, **Cuando** se verifica el historial de archivos, **Entonces** todas las mutaciones de archivos fueron ejecutadas por `pra_helper.py` y no por escritura directa del agente.

---

### Historia de Usuario 4 - Empaquetado y Exportacion Final (Prioridad: P3)

El usuario solicita el cierre y empaquetado del proyecto. El sistema comprime toda la carpeta de resultados del proyecto (incluyendo las laminas Blade, estilos acumulados, scripts acumulados, manifest, registros y el plan maestro) en un archivo `.zip` listo para ser descargado e integrado en el modulo Laravel de presentaciones.

**Por que esta prioridad**: Es la etapa final del ciclo de vida del proyecto. Aunque no es critica para la construccion, es indispensable para entregar el resultado al usuario.

**Prueba Independiente**: Se puede probar ejecutando el empaquetado sobre un proyecto con al menos una sesion construida y verificando que el archivo `.zip` contiene todos los archivos esperados en la estructura correcta.

**Escenarios de Aceptacion**:

1. **Dado** que el proyecto tiene al menos una sesion construida, **Cuando** el usuario ejecuta el comando de empaquetado, **Entonces** se genera un archivo `outputs.zip` en el directorio de salida.
2. **Dado** que el archivo `.zip` ha sido generado, **Cuando** se descomprime, **Entonces** contiene todas las laminas Blade, los archivos `styles.blade.php`, `scripts.blade.php`, `manifest_draft.blade.php`, los registros `class_registry.json` y `js_registry.json`, y una copia de `presentation_plan.md`.

---

### Casos Extremos

- Que pasa cuando el usuario proporciona un documento fuente vacio o ilegible?
- Que pasa cuando el plan maestro define una sesion sin laminas?
- Que pasa cuando el LLM devuelve una respuesta con bloques CSS o JS vacios?
- Que pasa cuando el usuario intenta construir una sesion cuyo numero no existe en el plan?
- Que pasa cuando el usuario intenta construir la sesion 3 sin haber completado la sesion 2?

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-001**: El sistema DEBE procesar documentos fuente (PDF, Jupyter Notebook, Markdown, articulos tecnicos, documentacion de codigo) como insumo para el plan maestro.
- **FR-002**: El sistema DEBE generar un archivo `presentation_plan.json` que contenga el titulo, el nombre de carpeta en snake_case, el idioma, el resumen general y la lista de sesiones con sus laminas.
- **FR-003**: El sistema DEBE crear subcarpetas `sesion[N]/` en el directorio de salida por cada sesion definida en el plan.
- **FR-004**: El sistema DEBE mantener un registro vivo de clases CSS (`class_registry.json`) para evitar redefinir estilos visuales entre sesiones.
- **FR-005**: El sistema DEBE mantener un registro vivo de comportamientos JS (`js_registry.json`) para evitar colisiones de scripts entre laminas.
- **FR-006**: El sistema DEBE prohibir el uso de estilos inline (`style="..."`) en los archivos de laminas Blade.
- **FR-007**: El sistema DEBE delegar la creacion, mutacion y fusion de archivos al script ejecutor de soporte `pra_helper.py`.
- **FR-008**: El sistema DEBE generar entradas `<x-slide>` acumulativas en `manifest_additions/` para facilitar la integracion en el layout principal de Laravel.
- **FR-009**: El sistema DEBE operar de manera incremental y secuencial por numero de sesion.
- **FR-010**: El sistema DEBE empaquetar los resultados finales en un archivo `.zip` comprimido.

### Entidades Clave

- **Sesion**: Un grupo logico de laminas que comparten un objetivo pedagogico comun dentro del plan maestro. Cada sesion tiene un numero secuencial, un titulo y una lista de laminas.
- **Lamina**: Un componente Blade individual (`[slide-id-kebab-case].blade.php`) que representa una diapositiva dentro de una sesion. Tiene un identificador unico, un tipo (portada, contenido, interactiva, cierre), un objetivo pedagogico y una lista de insumos.
- **Registro de Clases (class_registry.json)**: Un archivo JSON que almacena todas las clases CSS implementadas hasta el momento. Cada entrada contiene el nombre de la clase, su descripcion, su estado de implementacion y la sesion en la que fue creada.
- **Registro de Comportamientos (js_registry.json)**: Un archivo JSON que almacena todos los comportamientos JavaScript implementados hasta el momento. Cada entrada contiene el nombre del comportamiento, su descripcion, su estado de implementacion y la sesion en la que fue creado.
- **Plan Maestro (presentation_plan.json)**: El documento JSON que define la estructura completa de la presentacion, incluyendo todas las sesiones, sus laminas y metadatos generales.

---

## Criterios de Exito *(obligatorio)*

### Resultados Medibles

- **SC-001**: El 100% de las laminas generadas cumplen con la norma de Cero CSS Inline.
- **SC-002**: Cero colisiones de nombres en clases CSS o comportamientos JavaScript entre sesiones diferentes.
- **SC-003**: El tiempo de procesamiento por sesion no supera los 2 minutos de ejecucion interactiva en la CLI.
- **SC-004**: Los archivos generados son 100% compatibles con la estructura Blade de Laravel sin requerir ajustes manuales.
- **SC-005**: Al menos el 90% de las laminas generadas son validas y renderizables en Reveal.js en el primer intento.

---

## Suposiciones

- El usuario tiene acceso a un modelo de LLM operativo desde OpenCode para la generacion de planes y laminas.
- El framework Laravel esta configurado para aceptar componentes Blade (`<x-slide>`) con atributos `view` y `data-title`.
- Reveal.js esta configurado para renderizar las diapositivas a partir de los archivos Blade generados.
- El script `pra_helper.py` sera el unico punto de escritura de archivos del proyecto generado.
- Los documentos fuente proporcionados por el usuario contienen informacion suficiente para generar un plan de presentacion coherente.
- El numero maximo de sesiones por presentacion no supera las 10.
- El numero maximo de laminas por sesion no supera las 15.
