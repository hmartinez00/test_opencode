# Investigacion y Decisiones de Diseno: Sistema PRA

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [Plan de Implementacion](./plan.md)

## Decisiones Arquitectonicas

### D1. Motor de Fusion Determinista en Python

**Decision**: El motor de creacion, mutacion y fusion de archivos sera un script Python (`pra_helper.py`) que opera exclusivamente mediante argumentos CLI.

**Justificacion**: La Constitucion del proyecto (Principio III) exige que los agentes de IA no modifiquen manualmente archivos ni registries. Un script Python con logica determinista de regex y manejo de JSON garantiza precision y previene corrupcion de datos acumulativos.

**Alternativas Consideradas**:
- Shell scripts (Bash): Descartada por la falta de un manejo robusto de JSON en Windows sin dependencias adicionales.
- Node.js: Descartada por introducir un ecosistema adicional innecesario.
- Permitir escritura directa del LLM: Violacion directa del Principio III.

---

### D2. Aislamiento de JavaScript por Lamina

**Decision**: Cada script interactivo se encapsula en un bloque `document.addEventListener('DOMContentLoaded', ...)` con un comentario explicito que identifica la lamina propietaria.

**Justificacion**: Reveal.js carga todas las diapositivas en el DOM simultaneamente. Sin aislamiento, las funciones y variables globales colisionan durante las transiciones entre laminas.

**Alternativas Consideradas**:
- Modulos ES6 con import/export: Descartada porque los scripts Blade en Laravel no soportan nativamente modulos ES sin configuracion adicional de bundler.
- Web Components / Shadow DOM: Solucion sobredimensionada para el alcance del proyecto.

---

### D3. Empaquetado ZIP Estructurado

**Decision**: El comando `pra_helper.py --zip` genera un archivo `.zip` que preserva la estructura de directorios completa del proyecto generado.

**Justificacion**: El usuario final necesita un entregable portable que incluya tanto las laminas Blade como los registros, estilos y scripts acumulados. El formato ZIP es universalmente compatible.

**Alternativas Consideradas**:
- Tar.gz: Menor compatibilidad nativa en Windows.
- Carpeta de salida directa sin comprimir: Menos portable para transferencia entre entornos de desarrollo.

---

### D4. Prompt Adaptado por Sesion

**Decision**: Antes de generar laminas para la Sesion N, `pra_helper.py --prompt-session N` compila un prompt que inyecta:
1. El contenido del `presentation_plan.json` (solo la sesion N y sus laminas)
2. El estado actual de `class_registry.json` (clases ya implementadas)
3. El estado actual de `js_registry.json` (comportamientos ya implementados)
4. Las plantillas maestras de prompts (slide meta prompt)

**Justificacion**: Proporciona al LLM todo el contexto necesario para generar contenido coherente sin duplicar clases o comportamientos existentes.

**Alternativas Consideradas**:
- Inyectar el plan completo siempre: Sobredimensiona el contexto con informacion irrelevante.
- Sin contexto de registros: Genera duplicacion de clases CSS y comportamientos JS.
- Inyectar toda la historia de sesiones previas: Escalabilidad limitada.

---

### D5. Separacion de Estilos y Scripts por Sesion

**Decision**: Los estilos y scripts generados en cada sesion se almacenan tanto en los archivos acumuladores (`styles.blade.php`, `scripts.blade.php`) como en archivos de respaldo aislados (`styles_additions/sesion[N]_styles.css`, `scripts_additions/sesion[N]_scripts.js`).

**Justificacion**: Los archivos acumuladores son los que se integran en la presentacion final. Los archivos de respaldo permiten auditar, editar o revertir cambios de una sesion especifica sin afectar a las demas.

**Alternativas Consideradas**:
- Solo archivos acumuladores: Imposible revertir o auditar cambios por sesion.
- Solo archivos aislados: Requiere un proceso adicional de fusion para integrar en la presentacion final.
