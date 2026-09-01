# Plan de implementación: robustez y coherencia del flujo PRA

**Fecha**: 2026-09-01
**Especificación**: [spec.md](./spec.md)
**Estado**: Implementación del núcleo completada; detección de ambigüedad del proyecto queda pendiente

## 1. Método de trabajo

Este cambio se guiará por TDD estricto:

1. escribir primero pruebas que reproduzcan cada problema observado,
2. confirmar el fallo en rojo,
3. implementar la corrección mínima,
4. ejecutar la suite relevante,
5. refactorizar solo si la validación sigue en verde.

La regla es que ninguna corrección entra a producción sin evidencia de prueba que falle antes y pase después.

---

## 2. Objetivo arquitectónico

La implementación debe reforzar dos responsabilidades del sistema:

- control de coherencia del proyecto generado,
- validación de dependencias del entorno y del proyecto activo.

Se debe preservar la separación actual:
- `pra_helper.py` sigue siendo el único punto de escritura del proyecto,
- `pra_orchestrator.py` sigue siendo la capa de coordinación y control de calidad,
- la lógica de negocio y la lógica de ejecución no se mezclan.

---

## 3. Cambios previstos por módulo

### 3.1 `pra_helper.py`

#### A. Oracle de coherencia en consolidación
Se añadirá una función de análisis que compare:
- ids declarados en `presentation_plan.json`,
- ids realmente presentes en `sesion[N]/`,
- ids duplicados a nivel global.

Se espera evaluar estos resultados en un estructura de retorno como:

```python
{
  "huerfanas": [{"sesion": 2, "id": "x", "sugerencia": "..."}],
  "faltantes": [{"sesion": 1, "id": "y", "sugerencia": "..."}],
  "duplicadas": [{"sesion": 1, "id": "z", "detalle": "..."}],
}
```

La consolidación debe abortar cuando exista al menos una incoherencia bloqueante.

#### B. Validación mínima del plan
Se añadirá una comprobación previa a la persistencia del plan que revise:
- registros CSS/JS vacíos,
- laminas con `insumos` vacíos o nulos,
- condiciones opcionales de error cuando `PRA_PLAN_ESTRICTO=1`.

La validación será no bloqueante por defecto y debe exponer advertencias accionables.

#### C. Resolución del proyecto activo
Se añadirá una comprobación en la resolución del proyecto activo que:
- filtre carpetas no proyectables,
- detecte ambigüedad cuando haya varios candidatos,
- informe de forma explícita la lista de proyectos que podrían corresponder.

### 3.2 `pra_orchestrator.py`

#### D. Resolución robusta del backend `opencode`
Se encapsulará la resolución del binario `opencode` para:
- intentar PATH,
- intentar rutas conocidas del sistema,
- devolver un estado de error estructurado si no existe.

Se debe evitar que el backend falle con `FileNotFoundError` sin contexto útil.

#### E. Diagnóstico estructurado
Cuando el backend no este disponible, el orquestador debe generar un error con un formato estable y legible, no un traceback crudo.

---

## 4. Diseño de flujo propuesto

El flujo deseado es el siguiente:

1. `init` genera el prompt del plan maestro.
2. `save-plan` valida calidad mínima del plan.
3. `prompt-session` y `process-session` generan las laminas por sesión.
4. `consolidate` valida coherencia plan-vs-laminas antes de materializar el manifest final.
5. `pytest` ejecuta la validación de calidad del repositorio.
6. `cleanup` solo elimina artefactos residuales si el lote protegido existe y es correcto.

La clave es que la coherencia no debe ser una comprobación tardía que se “adivina” en el manifest final. Debe ser un guardrail explícito antes de la materialización final.

---

## 5. Decisiones de diseño

### D1. Centralización de validación
La validación de coherencia será una función única reutilizable para la consolidación y para diagnósticos en el futuro.

### D2. No se mezcla validación con escritura
La validación no debe escribir ni materializar archivos por sí misma; solo debe devolver metadatos estructurados para que el flujo los use.

### D3. Diagnóstico antes que silenciamiento
Si el sistema detecta anomalía, debe informar el problema con contexto, no ocultarlo.

### D4. Por defecto conservador
La validación de calidad mínima del plan será defensiva y no bloqueante a menos que se active el modo estricto.

### D5. Resolución cerrada del backend externo
Se evitará depender de variables de entorno del shell que no estén explícitas en la app.

---

## 6. Plan de implementación por fases

### Fase 0: pruebas rojas
Se escriben pruebas unitarias, de integración y constitucionales para cada anomalía detectada.

### Fase 1: coherencia de consolidación
Se implementa el analizador de redundancias y se integra en `_consolidate_project()`.

### Fase 2: validación del plan
Se añade la validación de registros vacíos e `insumos` vacíos.

### Fase 3: backend `opencode`
Se implementa la resolución del binario con diagnóstico estructurado.

### Fase 4: proyecto activo
Se añade detección de ambigüedad y advertencia de candidatos.

### Fase 5: refactor final
Se limpia la implementación eliminando duplicados de lógica y se confirma la suite en verde.

---

## 7. Criterios de salida

La implementación se considera lista cuando:

- todas las pruebas TDD rojas pasan,
- las pruebas de integración del flujo permanecen estables,
- la consolidación reporta incoherencias de forma explícita,
- `save-plan` reporta advertencias de calidad mínima,
- el orquestador no depende del shell para resolver `opencode`,
- la detección de proyecto activo no opera en silencio cuando hay ambigüedad,
- la cobertura mínima para módulos modificados sigue en rango aceptado.

---

## 8. Documentación a actualizar tras la implementación

- [README.md](../../README.md)
- [AGENTS.md](../../AGENTS.md)
- [SESION_PRA_RESUMEN.md](../../SESION_PRA_RESUMEN.md)
- contratos relevantes bajo [specs](../)

No se toca la lógica de negocio ni el diseño del producto en esta fase; solo la robustez del flujo y las validaciones defensivas.
