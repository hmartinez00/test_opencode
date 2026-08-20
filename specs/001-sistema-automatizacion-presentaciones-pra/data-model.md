# Modelo de Datos: Sistema PRA

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [Plan de Implementacion](./plan.md)

## Entidades del Sistema

### 1. PresentationPlan (`presentation_plan.json`)

Representa el plan maestro completo de una presentacion. Se genera durante la fase de inicializacion (`--init`) y se actualiza durante `--save-plan`.

**Campos**:
- `titulo` (string, requerido): Titulo de la presentacion. Ejemplo: "Automatizacion de Presentaciones Reveal.js"
- `carpeta_snake_case` (string, requerido): Nombre de carpeta del proyecto en formato snake_case. Ejemplo: "automatizacion_presentaciones_pra"
- `idioma` (string, requerido): Codigo de idioma ISO 639-1. Ejemplo: "es"
- `resumen_general` (string, requerido): Descripcion breve del objetivo de la presentacion.
- `sesiones` (array de Sesion, requerido): Lista ordenada de sesiones del plan.

**Reglas de Validacion**:
- `titulo` no puede estar vacio.
- `carpeta_snake_case` debe coincidir con el patron `^[a-z][a-z0-9_]*$`.
- `sesiones` debe contener al menos una entrada.
- Las sesiones deben estar ordenadas secuencialmente por su campo `numero`.

---

### 2. Sesion (objeto dentro de `presentation_plan.json.sesiones`)

Representa una sesion logica dentro de la presentacion. Cada sesion agrupa laminas que comparten un objetivo pedagogico comun.

**Campos**:
- `numero` (entero, requerido): Numero secuencial de la sesion. Inicia en 1.
- `titulo` (string, requerido): Titulo descriptivo de la sesion.
- `objetivo_pedagogico` (string, requerido): Objetivo de aprendizaje que persigue la sesion.
- `laminas` (array de Lamina, requerido): Lista ordenada de laminas de la sesion.

**Reglas de Validacion**:
- `numero` debe ser un entero positivo sin repetir entre sesiones.
- `laminas` debe contener al menos una entrada.
- Las laminas deben estar ordenadas secuencialmente por su campo `orden`.

---

### 3. Lamina (objeto dentro de `presentation_plan.json.sesiones[n].laminas`)

Representa una lamina individual (diapositiva) dentro de una sesion. Se traduce directamente a un archivo Blade `.blade.php`.

**Campos**:
- `orden` (entero, requerido): Posicion de la lamina dentro de la sesion. Inicia en 1.
- `id_kebab_case` (string, requerido): Identificador unico en formato kebab-case. Ejemplo: "intro-que-es-pra"
- `tipo` (string, requerido): Tipo de lamina. Valores permitidos: `portada`, `contenido`, `interactiva`, `cierre`.
- `objetivo` (string, requerido): Breve descripcion del proposito de la lamina.
- `insumos` (array de strings, opcional): Elementos de contenido que debe incluir la lamina (textos, listas, codigo, imagenes, etc.).

**Reglas de Validacion**:
- `id_kebab_case` debe ser unico en toda la presentacion (no solo dentro de la sesion).
- `id_kebab_case` debe coincidir con el patron `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.
- `tipo` debe pertenecer al conjunto de valores permitidos.
- `orden` debe ser un entero positivo sin repetir entre laminas de la misma sesion.

---

### 4. ClassRegistry (`class_registry.json`)

Registro vivo de todas las clases CSS implementadas en la presentacion. Se inicializa durante `--save-plan` y se actualiza durante `--process-session`.

**Campos**:
- `clases` (array de EntradaClase): Lista de todas las clases CSS registradas.

**EntradaClase**:
- `nombre` (string, requerido): Nombre de la clase CSS. Ejemplo: `pra-slide-title`
- `descripcion` (string, requerido): Breve descripcion del proposito visual de la clase.
- `implementada` (booleano, requerido): `false` si esta definida en el plan pero aun no implementada; `true` si ya fue integrada en `styles.blade.php`.
- `sesion_creacion` (entero, requerido): Numero de la sesion en la que fue creada. 0 si es una clase predefinida del plan inicial.

**Reglas de Validacion**:
- `nombre` debe ser unico en todo el registro.
- `nombre` debe coincidir con el patron de clases CSS valido (letras, numeros, guiones, guion bajo).
- No se permiten duplicados por nombre.

---

### 5. JSRegistry (`js_registry.json`)

Registro vivo de todos los comportamientos JavaScript implementados en la presentacion. Se inicializa durante `--save-plan` y se actualiza durante `--process-session`.

**Campos**:
- `comportamientos` (array de EntradaJS): Lista de todos los comportamientos JS registrados.

**EntradaJS**:
- `nombre` (string, requerido): Nombre descriptivo del comportamiento. Ejemplo: `animacion_titulo_entrada`
- `descripcion` (string, requerido): Breve descripcion de que hace el comportamiento.
- `implementada` (booleano, requerido): `false` si esta definida en el plan pero aun no implementada; `true` si ya fue integrada en `scripts.blade.php`.
- `sesion_creacion` (entero, requerido): Numero de la sesion en la que fue creado. 0 si es un comportamiento predefinido del plan inicial.

**Reglas de Validacion**:
- `nombre` debe ser unico en todo el registro.
- No se permiten duplicados por nombre.

---

### 6. SlideBlade (`sesion[N]/[slide-id-kebab-case].blade.php`)

Archivo Blade que representa una lamina individual renderizable en Reveal.js. No es una entidad JSON, sino un archivo de plantilla Blade.

**Estructura interna esperada**:
- Etiqueta `<x-slide>` con atributos `view` y `data-title`.
- Contenido HTML con clases CSS registradas (sin `style="..."`).
- Bloques `@push('styles')` y `@push('scripts')` para estilos y scripts de la lamina.

**Reglas de Validacion**:
- No debe contener atributos `style="..."` en ninguna etiqueta HTML (validacion regex).
- Las clases CSS utilizadas deben existir en `class_registry.json` con `implementada: true`.
- Los scripts JavaScript deben estar encapsulados en `DOMContentLoaded` con comentario de lamina.

---

## Relaciones entre Entidades

```text
PresentationPlan (1) ----< (N) Sesion
Sesion (1) ----< (N) Lamina
Lamina (1) ----> (1) SlideBlade [generado como archivo]
PresentationPlan (1) ----< (N) ClassRegistry.entrada
PresentationPlan (1) ----< (N) JSRegistry.entrada
```

## Transiciones de Estado

### Estado de una Sesion
```
PENDIENTE -> EN_PROCESO -> COMPLETADA
```
- `PENDIENTE`: La sesion esta definida en el plan pero no ha sido procesada.
- `EN_PROCESO`: El prompt de la sesion ha sido enviado al LLM y se esta esperando/procesando la respuesta.
- `COMPLETADA`: Todos los archivos Blade, estilos, scripts y registros de la sesion han sido escritos y validados.

### Estado de una Entrada de Registro (Clase o Comportamiento)
```
PENDIENTE -> IMPLEMENTADA
```
- `PENDIENTE` (`implementada: false`): La entrada fue definida en el plan pero aun no integrada en el acumulador correspondiente.
- `IMPLEMENTADA` (`implementada: true`): La entrada fue integrada exitosamente en `styles.blade.php` o `scripts.blade.php`.
