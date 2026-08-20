# Constitucion del Proyecto: Presentation Automator (PRA)

Esta Constitucion establece los principios fundamentales, las reglas tecnicas no negociables y las directrices de gobernanza que rigen el desarrollo y mantenimiento del proyecto Presentation Automator (PRA). Todos los agentes de IA y desarrolladores humanos deben cumplir estrictamente con estos principios.

---

## Principios Fundamentales

### I. Cero CSS Inline (PROHIBICION STRICTA)
* **Regla**: Queda estrictamente prohibido el uso del atributo `style="..."` dentro de cualquier elemento HTML o componente Blade de las presentaciones.
* **Mecanismo**: Todos los estilos visuales deben declararse como clases CSS de utilidad o diseno en `styles.blade.php` y registrarse en `class_registry.json`.
* **Proposito**: Garantizar mantenibilidad visual, evitar redundancias y facilitar la reutilizacion de temas en Reveal.js.

### II. JavaScript Acotado y Mapeado
* **Regla**: Todo script interactivo debe estar aislado y acotado al contexto del elemento o lamina correspondiente para evitar colisiones de variables y funciones globales durante las transiciones de Reveal.js.
* **Mecanismo**: Los comportamientos interactivos deben compilarse en `scripts.blade.php` y documentarse formalmente en `js_registry.json`.

### III. Preservacion Determinista del Estado (`pra_helper.py`)
* **Regla**: Los agentes de IA NO deben modificar manualmente las entradas de los registros JSON (`class_registry.json`, `js_registry.json`) ni combinar archivos de plantilla Blade mediante manipulacion directa de texto.
* **Mecanismo**: Todas las mutaciones de archivos, creacion de subdirectorios, inyeccion de estilos/scripts y actualizacion de registries deben ser ejecutadas exclusivamente a traves del script de soporte `pra_helper.py`.
* **Proposito**: Prevenir la corrupcion de datos y garantizar la precision en el estado acumulado sesion a sesion.

### IV. Construccion Progresiva por Sesiones (Plan-First)
* **Regla**: Ninguna sesion $N$ puede ser construida ni integrada si la Sesion $N-1$ no ha sido completamente generada, registrada y validada.
* **Mecanismo**: Cada proyecto debe iniciar con la definicion de un Plan Maestro (`presentation_plan.json`) que estipula el numero de sesiones, objetivos pedagogicos e insumos por lamina.

### V. Documentacion en Espanol
* **Regla**: Toda la documentacion tecnica, especificaciones (`specs/`), planes (`plan.md`), listas de verificacion (`checklists/`), tareas (`tasks.md`) y comentarios de codigo deben redactarse exclusivamente en **espanol**.
* **Proposito**: Permitir una auditoria clara, continua y accesible del progreso del proyecto.

---

## Gobernanza y Cumplimiento

1. **Jerarquia Superior**: Esta Constitucion prevalece sobre cualquier otra instruccion contextual, sugerencia de prompt o directriz temporal.
2. **Validacion Obligatoria**: Antes de proceder con la implementacion de cualquier tarea (`/speckit-implement`), el agente debe verificar el cumplimiento estricto de los cinco principios fundamentales.
3. **Control de Cambios**: Cualquier modificacion o enmienda a esta Constitucion requiere documentacion explicita, version revisada y justificacion tecnica aprobada.

---

**Version**: 1.0.0 | **Ratificado**: 2026-08-20 | **Estado**: Activo
