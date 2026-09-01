# Especificación funcional: Robustez y coherencia del flujo PRA

**Rama funcional**: `009-robustez-coherencia-pra`
**Estado**: Implementada parcialmente; núcleo validado en la suite actual
**Fecha**: 2026-09-01

## 1. Resumen ejecutivo

Esta especificación define la segunda capa de robustez del flujo PRA, tras la consolidación inicial y la validación básica de calidad de salida. El objetivo no es introducir nuevas capacidades de presentación, sino asegurar que el sistema detecte, informe y bloquee errores de coherencia ocultos antes de entregar un proyecto final.

Los problemas detectados y documentados en la fase previa no son fallos de redacción sino errores de flujo real:

- laminas generadas fuera del plan se omitían silenciosamente,
- el plan podía guardarse sin registros y sin insumos mínimamente definidos,
- el backend `opencode` podía fallar por resolución de ruta y PATH,
- la selección de proyecto activo podía operar sobre un proyecto incorrecto cuando había ambigüedad.

La solución propuesta a nivel de especificación es defensiva, con validaciones tempranas y diagnósticos estructurados, sin alterar la intención del sistema ni la forma en que el orquestador delega la creación de artefactos en `pra_helper.py`.

---

## 2. Objetivo del cambio

El proyecto debe pasar de un flujo “funcional pero frágil” a un flujo “coherente y defendido”, en el que el sistema:

1. detecta incoherencias entre el plan y las laminas escritas,
2. revisa la calidad mínima del plan antes de aceptar la generación de sesiones,
3. resuelve el backend `opencode` de manera determinista,
4. exige explicitud cuando el proyecto activo es ambiguo.

El cambio se limita a captura de errores, validación y diagnósticos. No incluye rediseñar la lógica de generación ni cambiar el modelo de presentación.

---

## 3. Problemas y contexto del negocio

### 3.1 Incoherencia plan vs. laminas

Cuando el consolidador se basaba únicamente en el plan maestro para construir el manifest, cualquier archivo blade generado físicamente en `sesion[N]/` pero no declarado en `presentation_plan.json` quedaba invisibilizado para el producto final. Esto provocaba entregables incompletos sin una advertencia clara.

El sistema debe detectar tres tipos de incoherencias:

- laminas huérfanas: existían en el filesystem pero no estaban declaradas,
- laminas faltantes: estaban declaradas en el plan pero no materializadas,
- laminas duplicadas: el mismo `id_kebab_case` aparecía más de una vez.

### 3.2 Calidad mínima del plan

Un plan incompleto puede llevar a una presentación inválida aunque la sesión se construya sin error. Para evitarlo, el sistema debe exigir que el plan contenga al menos un mínimo de información operativa: registros CSS/JS y `insumos` definidos para cada lamina.

La validación debe ser de advertencia por defecto y configurable como error estrictamente en entornos controlados.

### 3.3 Dependencia externa del backend `opencode`

El backend de orquestación no debe depender del shell que ejecutó el proceso. Debe resolver la ruta del binario con prioridad determinista y generar un diagnóstico útil cuando no exista.

### 3.4 Ambigüedad del proyecto activo

Cuando hay varios proyectos bajo la base de salida, el sistema debe evitar elegir uno al azar o por orden alfabético sin advertir. Debe exigir `PRA_ACTIVE_PROJECT` o mostrar una lista explícita de candidatos.

---

## 4. Historias de usuario

### HU-001: coherencia entre plan y material real
Como desarrollador PRA, quiero que el consolidador detecte laminas faltantes, huérfanas y duplicadas, para evitar entregar manifestos incompletos sin saberlo.

Criterio de aceptación:
- El sistema devuelve un bloque `coherencia` con los diagnósticos.
- Si hay incoherencia bloqueante, la consolidación devuelve `ok: false`.
- El manifest no se produce en un estado parcialmente válido.

### HU-002: validación temprana del plan
Como creador de presentaciones, quiero que `save-plan` advierta si faltan registros CSS/JS o si hay laminas sin `insumos`, para corregir el plan antes de continuar.

Criterio de aceptación:
- Las advertencias se exponen en el JSON de salida y en la salida estándar.
- La operación continúa por defecto.
- La variable de entorno `PRA_PLAN_ESTRICTO=1` convierte esas advertencias en error.

### HU-003: backend `opencode` resuelto con diagnóstico
Como operador del orquestador, quiero que `opencode` se resuelva de forma fiable o muestre un diagnóstico claro, para no depender del entorno del shell que lanzó la aplicación.

Criterio de aceptación:
- La resolución intenta PATH y rutas conocidas.
- Si no existe, el error se reporta bajo el código `BACKEND_NO_DISPONIBLE` con rutas intentadas y PATH visible.

### HU-004: proyecto activo explícito y seguro
Como usuario con varios proyectos, quiero tener una regla explícita para elegir el proyecto activo, para evitar operar sobre el proyecto equivocado.

Criterio de aceptación:
- Si `PRA_ACTIVE_PROJECT` es válido, se usa siempre.
- Si no está definido y hay más de un proyecto candidato, se emite una advertencia de ambigüedad.

---

## 5. Requisitos funcionales

### RF-001: diagnóstico de incoherencia
El sistema debe calcular, por cada sesión, la diferencia entre:
- las laminas declaradas en `presentation_plan.json`, y
- las laminas generadas físicamente en `sesion[N]/`.

### RF-002: huérfanas
El sistema debe identificar archivos `.blade.php` en `sesion[N]/` cuyo identificador no aparece en el plan de esa sesión.

### RF-003: faltantes
El sistema debe identificar identificadores declarados en el plan que no tienen archivo equivalente en `sesion[N]/`.

### RF-004: duplicadas
El sistema debe detectar duplicados de `id_kebab_case` dentro del mismo plan, incluso si están en distintas sesiones.

### RF-005: JSON de coherencia
El reporte JSON de consolidación debe incluir un bloque `coherencia` con listas `huerfanas`, `faltantes` y `duplicadas`.

### RF-006: bloqueo por incoherencia
Si existe cualquiera de las incoherencias bloqueantes, `consolidate` debe devolver `ok: false` y no entregar un manifest parcialmente válido.

### RF-007: plan mínimo viable
`save-plan` debe comprobar si el registro CSS/JS queda vacío o si alguna lamina carece de `insumos`.

### RF-008: advertencia por defecto
La validación del plan debe ser no bloqueante por defecto; solo se convierte en bloqueo cuando se activa `PRA_PLAN_ESTRICTO`.

### RF-009: resolución del backend `opencode`
El backend `opencode` debe intentar resolver el binario a través de PATH y rutas conocidas del sistema operativo.

### RF-010: diagnóstico estructurado
Cuando el binario no exista o no sea ejecutable, el orquestador debe informar `BACKEND_NO_DISPONIBLE` con rutas intentadas y el PATH relevante.

### RF-011: proyecto activo con ambigüedad
El resolver de proyecto debe detectar más de un candidato y avisar explícitamente antes de elegir un proyecto por defecto.

### RF-012: no regresión del flujo normal
El flujo sin anomalías debe continuar siendo el mismo en términos de operación, determinismo y salida esperada.

---

## 6. Reglas de calidad y seguridad del flujo

- Todo diagnóstico debe emitirse en formato estructurado, no como excepción cruda.
- La validación del plan debe ser positiva por defecto para no romper flujos ya existentes.
- La consolidación debe ser una etapa de guardado final, no un paso que “adivina” lo que el sistema quiere.
- El backend externo y la resolución del proyecto activo deben ser deterministas y reproducibles.

---

## 7. Criterios de éxito

- CSE-001: una lamina fuera del plan ya no se omite silenciosamente.
- CSE-002: el reporte de consolidación incluye el bloque `coherencia` con detalles accionables.
- CSE-003: `consolidate` retorna `ok: false` y evita manifest incompleto al detectar incoherencias.
- CSE-004: `save-plan` provoca advertencias visibles por registros vacíos o insumos vacíos.
- CSE-005: `PRA_PLAN_ESTRICTO=1` convierte esas advertencias en error de ejecución.
- CSE-006: el backend `opencode` resuelve o diagnostica sin depender del shell.
- CSE-007: la selección del proyecto activo no toma decisiones silenciosas cuando hay ambigüedad.
- CSE-008: la suite de pruebas permanece en verde y la cobertura de los módulos modificados no cae por debajo del mínimo requerido.

---

## 8. Fuera de alcance

- No se modifica el contenido pedagógico de las presentaciones.
- No se reescribe la lógica de generación de sesiones ni de prompts.
- No se cambia el objetivo del directorio maestro ni el patrón de archivos de salida.
- No se reemplaza el contrato de `save-plan`, solo se hace más robusto.
- No se introduce nueva infraestructura de persistencia para orquestación.

---

## 9. Consideraciones de TDD

El cumplimiento de esta especificación exige desarrollo guiado por pruebas:

1. escribir pruebas que reproduzcan cada anomalía,
2. confirmar el fallo en rojo,
3. implementar la corrección mínima,
4. ejecutar la suite completa de validación.

La prueba es la fuerza de validación del comportamiento esperado y no puede sustituirse por inspección visual del código.
