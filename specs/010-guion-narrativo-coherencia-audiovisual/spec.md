# Especificación funcional: guion narrativo y coherencia audiovisual PRA

**Rama funcional**: `010-guion-narrativo-coherencia-audiovisual`  
**Estado**: especificación previa a implementación  
**Fecha**: 2026-09-01

## 1. Resumen

El flujo PRA debe generar presentaciones cuyas láminas funcionen como apoyo visual de un guion de narración. Cada sesión tendrá un archivo de texto en `assets/audio/guion_sesionN.txt`, con fragmentos asociados explícitamente a láminas mediante marcas `[slide: N]`.

La narración se generará a partir de los objetivos e insumos del plan maestro. Las láminas no deben repetir de forma literal todo el audio ni introducir conceptos que la narración no desarrolla. Deben reforzar visualmente la idea narrada mediante ejemplos, código, esquemas, listas o datos definidos en el plan.

La iteración mantiene las reglas existentes: `pra_helper.py` es el único punto de escritura de artefactos del proyecto y `pra_orchestrator.py` coordina el flujo sin escribir directamente en él.

## 2. Objetivos

1. Generar un guion narrativo por sesión alineado con los objetivos pedagógicos.
2. Asociar cada fragmento narrativo con una lámina concreta.
3. Crear los guiones en `assets/audio/` y conservarlos en `backup/fuente/`.
4. Validar que no existan láminas sin narración ni narración sin lámina.
5. Verificar que las láminas sean apoyo visual y no contenido contradictorio o desconectado.
6. Mantener compatibilidad con el flujo manual y el orquestado.

## 3. Alcance

### Incluido

- Nuevo contrato de salida para sesiones con guion narrativo.
- Parseo de marcas `[slide: N]`.
- Escritura de `assets/audio/guion_sesionN.txt`.
- Validación estructural y semántica básica entre plan, guion y láminas.
- Modo estricto mediante `PRA_AUDIO_ESTRICTO=1`.
- Inclusión del audio en consolidación, limpieza y respaldo de fuente.
- Pruebas TDD unitarias, de integración y constitucionales.

### Fuera de alcance

- Síntesis de voz o generación de archivos MP3/WAV.
- Reproducción automática de audio desde Reveal.js.
- Edición de audio, medición acústica o sincronización temporal real.
- Evaluación pedagógica completamente autónoma por un modelo externo.
- Modificación del contrato de estilos, scripts o registros CSS/JS existente.

## 4. Convenciones de numeración

El ejemplo de referencia utiliza índices basados en cero:

```text
[slide: 0] -> primera lámina
[slide: 1] -> segunda lámina
```

El plan maestro conserva `orden` basado en uno. La relación normativa será:

```text
indice_narrativo = orden - 1
```

La conversión debe ser interna y explícita. No se modificará el campo `orden` del plan.

## 5. Historias de usuario

### HU-001: guion basado en objetivos

Como creador de una presentación, quiero que cada sesión tenga una narración derivada de sus objetivos e insumos para que el discurso tenga intención pedagógica.

**Aceptación**:
- El guion contiene una o más entradas por sesión.
- Cada entrada referencia una lámina válida.
- El contenido puede rastrearse al objetivo o a los insumos del plan.

### HU-002: lámina como apoyo visual

Como estudiante, quiero que la lámina complemente lo que se narra para que pueda seguir el discurso sin leer un párrafo duplicado.

**Aceptación**:
- Cada lámina tiene un bloque narrativo asociado.
- La lámina incluye al menos un elemento visual relacionado con sus insumos.
- La validación informa ausencia de apoyo o contenido no declarado.

### HU-003: archivo de audio textual localizable

Como operador, quiero encontrar un archivo de guion por sesión en `assets/audio/` para poder revisarlo, editarlo o utilizarlo posteriormente en una herramienta de voz.

**Aceptación**:
- Se crea `assets/audio/guion_sesionN.txt` con UTF-8.
- El formato conserva las marcas `[slide: N]`.
- El archivo se respalda en `backup/fuente/`.

### HU-004: control de calidad configurable

Como operador, quiero que las incoherencias sean advertencias en modo normal y errores en modo estricto para controlar el nivel de defensa del flujo.

**Aceptación**:
- El modo normal informa advertencias estructuradas.
- `PRA_AUDIO_ESTRICTO=1` bloquea la sesión o consolidación cuando hay errores.
- El diagnóstico identifica sesión, slide y causa.

## 6. Requisitos funcionales

- **RF-001**: `process-session` debe aceptar el bloque narrativo de la respuesta LLM.
- **RF-002**: El parser debe reconocer una marca con el formato exacto `[slide: N]` permitiendo espacios laterales.
- **RF-003**: Una entrada narrativa debe conservar todo el texto hasta la siguiente marca o el final del archivo.
- **RF-004**: No se permitirán marcas duplicadas para el mismo índice salvo que el contrato defina explícitamente concatenación.
- **RF-005**: Todo índice debe corresponder a una lámina declarada en la sesión.
- **RF-006**: Toda lámina declarada debe tener al menos una entrada narrativa no vacía.
- **RF-007**: Se debe crear `assets/audio/` de forma idempotente.
- **RF-008**: El archivo debe escribirse en UTF-8 y terminar con salto de línea estable.
- **RF-009**: `consolidate` debe comprobar la coherencia audiovisual antes de crear el manifest final.
- **RF-010**: El reporte debe incluir `audio`, con `faltantes`, `huerfanas`, `duplicadas`, `vacias` y `advertencias`.
- **RF-011**: El modo estricto `PRA_AUDIO_ESTRICTO=1` debe convertir errores bloqueantes en código no exitoso.
- **RF-012**: `cleanup` debe preservar el guion dentro del lote protegido y su fuente interna.
- **RF-013**: Dos ejecuciones con las mismas entradas deben producir guiones deterministas cuando se utilice el backend mock.
- **RF-014**: Las respuestas antiguas sin bloque narrativo podrán aceptarse solo en modo compatibilidad; los proyectos nuevos deben exigirlo.

## 7. Contrato del bloque narrativo

La respuesta de una sesión mantendrá los cinco bloques existentes y añadirá:

```text
**BLOQUE 6 — Guion de narración**
```text
[slide: 0] Texto de apertura de la sesión.
[slide: 1] Explicación del primer concepto.
[slide: 2] Cierre y transición.
```
```

El bloque debe contener únicamente texto de narración y sus marcas. No debe contener HTML, CSS, JavaScript ni instrucciones para el LLM.

## 8. Modelo de diagnóstico

```json
{
  "audio": {
    "archivo": "assets/audio/guion_sesion1.txt",
    "faltantes": [{"slide": 2, "id": "cierre"}],
    "huerfanas": [{"slide": 4, "detalle": "No existe en el plan"}],
    "duplicadas": [{"slide": 1}],
    "vacias": [],
    "advertencias": []
  }
}
```

## 9. Criterios de éxito

- **CSE-001**: Cada sesión válida genera su guion en `assets/audio/`.
- **CSE-002**: Cada marca del guion se puede resolver contra una lámina.
- **CSE-003**: Ninguna lámina válida queda sin narración.
- **CSE-004**: El sistema detecta marcas inválidas, duplicadas y vacías.
- **CSE-005**: El plan, los objetivos y los insumos se incluyen en el prompt narrativo.
- **CSE-006**: Las incoherencias aparecen en JSON y en los diagnósticos del flujo.
- **CSE-007**: El modo estricto bloquea entregables incoherentes.
- **CSE-008**: `cleanup` conserva los guiones y no deja artefactos duplicados.
- **CSE-009**: El flujo mock mantiene determinismo y la suite conserva cobertura mínima del 85%.

## 10. Reglas constitucionales

- El orquestador no escribirá guiones ni láminas directamente.
- No se generarán archivos de audio binarios en esta iteración.
- La validación no modificará el contenido para ocultar incoherencias.
- El guion será una fuente revisable, no un texto embebido únicamente en el manifest.
- La narración no sustituye los objetivos del plan ni autoriza a inventar insumos.
