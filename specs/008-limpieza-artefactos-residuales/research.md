# Investigacion y Decisiones Tecnicas: Limpieza de Artefactos Residuales con Proteccion del Lote

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Este documento registra las decisiones tecnicas (D1-D7) para la iteracion 008.

## Contexto

Una corrida PRA deja en el directorio del proyecto artefactos internos de construccion ademas del lote protegido que el usuario integra en Laravel. Esto produce duplicacion (p.ej. `sesion1/` y `session1/` con las mismas laminas) y contamina el directorio. Ademas, en esa misma fase se confirmo que el flujo automatico ya no toma `outputs.zip` como entregable (integra desde el directorio), por lo que la fase `zip` se vuelve residual.

---

## D1 - Mecanismo de limpieza: comando CLI en el motor (elegida)

**Alternativas**:
- **A (elegida)**: Nuevo comando `pra_helper.py limpiar` que implementa la logica de limpieza. El motor es el unico punto de escritura de archivos del proyecto (regla PRA), por lo que la mutacion debe residir en `pra_helper.py`.
- B: Funcion en `pra_orchestrator.py` que manipula el FS directamente. Violaria la regla de que el orquestador delega TODA mutacion al motor.

**Justificacion**: Mantiene la separacion de responsabilidades: el motor muta el proyecto; el orquestador solo orquesta. Permite invocar la limpieza tambien en flujos manuales.

## D2 - Ubicacion del respaldo: `backup/fuente/` dentro del proyecto (elegida)

**Alternativas**:
- **A (elegida)**: `backup/fuente/` dentro del directorio del proyecto generado.
- B: Carpeta `backup/` fuera del proyecto en la ruta base.

**Justificacion**: El usuario eligio "dentro del proyecto". Mantiene el respaldo autocontenido junto al lote, lo que facilita re-consolidar y no contamina la ruta base.

## D3 - Tratamiento de `outputs.zip`: residual y se elimina (elegida)

**Alternativas**:
- **A (elegida)**: `outputs.zip` se considera residual; se elimina en la limpieza y no se genera en el flujo automatico.
- B: Se conserva como entregable de empaquetado.

**Justificacion**: El usuario integra la presentacion desde el directorio del proyecto, no desde un zip. La fase `zip` se omite del pipeline (D4).

## D4 - Fase `zip` omitida en el flujo automatico (elegida)

**Alternativas**:
- **A (elegida)**: Se elimina la fase `zip` del estado y del pipeline; la fase final es `cleanup`.
- B: Se conserva `zip` y la limpieza ocurre despues (generar y luego borrar).

**Justificacion**: El usuario eligio "omitir fase zip por completo". Evita generar un artefacto que luego se descarta. Requiere retrocompatibilidad de `resume` (D5).

## D5 - Retrocompatibilidad de `resume` con estados que contienen `zip` (elegida)

**Alternativas**:
- **A (elegida)**: Al cargar estado, normalizar `fases["zip"]` -> `fases["cleanup"]`; `zip@completada` se mapea a `cleanup@completada` (no re-ejecutar); otros estados se pasan de largo o se marcan pendientes.
- B: Rechazar estados viejos (romper `resume`).

**Justificacion**: Un usuario con una corrida interrumpida previa a la iteracion 008 debe poder reanudar sin corromper el estado ni re-generar `outputs.zip`.

## D6 - Puerta protectora: abortar sin borrar si falta el lote (elegida)

**Alternativas**:
- **A (elegida)**: Verificar la existencia integra del lote (`manifest.blade.php`, planes JSON, `session[N]/` con `.blade.php`, `assets/`) ANTES de eliminar; si falta alguno, abortar con exit code distinto de 0 y no borrar nada.
- B: Eliminar incondicionalmente.

**Justificacion**: Garantiza que nunca se borre un proyecto cuya fuente de verdad (lote) este incompleta, protegiendo la integridad del "source de verdad".

## D7 - Determinismo del respaldo

**Alternativas**:
- **A (elegida)**: El respaldo sobrescribe `backup/fuente/` de forma determinista (se elimina el contenido previo y se re-copia desde la fuente original antes de borrarla). No se introducen marcas de tiempo en los archivos copiados (se copian byte a byte).
- B: Copia incremental con timestamps.

**Justificacion**: La prueba `test_run_mock_determinismo_entre_corridas` compara arboles byte a byte entre corridas; el respaldo debe ser reproducible de forma identica.

---

## Sintesis

| Problema | Decision |
|---|---|
| Donde mutar | Comando `limpiar` en `pra_helper.py` (D1) |
| Donde respaldar | `backup/fuente/` dentro del proyecto (D2) |
| Que hacer con el zip | Residual; se elimina (D3) |
| Fase zip en pipeline | Se omite; fase final `cleanup` (D4) |
| Resume con estados viejos | Normalizar `zip` -> `cleanup` (D5) |
| Seguridad | Puerta protectora del lote (D6) |
| Reproducible | Respaldo determinista (D7) |
