# Plan de pruebas TDD: guion narrativo y coherencia audiovisual

**Fecha**: 2026-09-01  
**Especificación**: [spec.md](./spec.md)  
**Estado**: pruebas previstas, aún no implementadas

Este documento define las pruebas que deberán escribirse primero. En esta etapa no se crean archivos bajo `tests/` ni se modifica código de producción.

## Convenciones

- Usar `python -m pytest`, nunca el ejecutable `pytest.exe`.
- Reutilizar `isolated_dir`, `run_cli`, `run_orchestrator`, `sample_plan_json_str` y los fixtures de `tests/conftest.py`.
- Mantener `PRA_OUTPUT_DIR` aislado por prueba.
- Usar respuestas mock deterministas.
- Cada prueba nueva debe indicar el requisito funcional y el criterio de éxito que cubre.
- La primera ejecución de cada grupo debe demostrar el estado rojo.

## Grupo A: pruebas unitarias del parser

### A1. Parseo válido y conversión de índices

Archivo previsto: `tests/unit/test_audio_narration.py`

```python
def test_parse_guion_asocia_texto_y_convierte_indice():
    respuesta = "[slide: 0] Apertura.\n[slide: 1] Primer concepto."
    resultado = pra_helper.parse_guion_narrativo(respuesta)
    assert resultado[0]["slide"] == 0
    assert resultado[0]["texto"] == "Apertura."
```

Cubre RF-002, RF-003 y CSE-002.

**Rojo esperado**: la función aún no existe.

### A2. Marca duplicada

```python
def test_parse_guion_detecta_slide_duplicada():
    guion = "[slide: 0] Uno.\n[slide: 0] Dos."
    reporte = pra_helper.validar_guion_narrativo(guion, plan_sesion)
    assert reporte["duplicadas"] == [0]
```

Cubre RF-004 y CSE-004.

### A3. Índice fuera de rango

```python
def test_validar_guion_detecta_indice_fuera_de_rango():
    guion = "[slide: 4] Texto sin destino."
    reporte = pra_helper.validar_guion_narrativo(guion, plan_sesion_con_dos_laminas)
    assert reporte["huerfanas"][0]["slide"] == 4
```

Cubre RF-005.

### A4. Texto vacío

```python
def test_validar_guion_detecta_entrada_vacia():
    guion = "[slide: 0]   \n[slide: 1] Texto válido."
    reporte = pra_helper.validar_guion_narrativo(guion, plan_sesion)
    assert reporte["vacias"] == [0]
```

Cubre RF-003 y CSE-004.

### A5. Lámina sin narración

```python
def test_validar_guion_detecta_lamina_sin_narracion():
    guion = "[slide: 0] Solo la primera."
    reporte = pra_helper.validar_guion_narrativo(guion, plan_sesion_con_dos_laminas)
    assert reporte["faltantes"][0]["slide"] == 1
```

Cubre RF-006 y CSE-003.

### A6. Texto sin marca

```python
def test_parse_guion_rechaza_texto_sin_marca():
    with pytest.raises(pra_helper.AudioNarrationError):
        pra_helper.parse_guion_narrativo("Texto sin slide asociada")
```

Cubre RF-002 y RF-003.

## Grupo B: pruebas unitarias de calidad

### B1. Índice narrativo frente a `orden`

Verificar que la primera lámina del plan (`orden: 1`) corresponde a `[slide: 0]` y la última no queda desplazada.

Cubre RF-005 y CSE-002.

### B2. Advertencia semántica

Crear una lámina cuyo objetivo e insumos sean conocidos y un texto narrativo que no mencione ninguna señal esperada. La validación debe devolver una advertencia, no lanzar error en modo normal.

Cubre D5 y RF-011.

### B3. Modo estricto

```python
def test_audio_estricto_convierte_advertencias_en_error(monkeypatch):
    monkeypatch.setenv("PRA_AUDIO_ESTRICTO", "1")
    assert pra_helper.audio_es_bloqueante(reporte_con_advertencias)
```

Cubre RF-011 y CSE-007.

## Grupo C: pruebas de integración CLI

### C1. `process-session` crea el guion

Preparar un proyecto, procesar una respuesta válida con BLOQUE 6 y comprobar:

```text
assets/audio/guion_sesion1.txt
```

El contenido debe conservar las marcas `[slide: 0]`, `[slide: 1]` y terminar con salto de línea.

Cubre RF-001, RF-007, RF-008 y CSE-001.

### C2. Respuesta sin BLOQUE 6

En modo compatibilidad, verificar el diagnóstico previsto. En modo estricto o proyecto nuevo, comprobar que `process-session` retorna código no exitoso y no crea un archivo de audio vacío.

Cubre RF-014.

### C3. Consolidación bloqueada

Crear un proyecto con una lámina sin entrada narrativa y ejecutar `consolidate`. Verificar:

- código de salida no exitoso;
- `ok: false`;
- bloque `audio` en el JSON;
- ausencia de manifest final parcialmente válido.

Cubre RF-009, RF-010 y CSE-006.

### C4. Consolidación coherente

Procesar una sesión válida, consolidar y comprobar que `assets/audio/guion_sesion1.txt` sigue presente y que la segunda consolidación no duplica ni altera el contenido.

Cubre RF-007, RF-008 y CSE-008.

### C5. `cleanup` preserva audio

Después de una corrida completa, ejecutar limpieza y verificar que el audio permanece en el lote protegido y en `backup/fuente/`, mientras los residuales permitidos desaparecen.

Cubre RF-012 y CSE-008.

### C6. Determinismo mock

Ejecutar dos corridas mock equivalentes y comparar el contenido y la ruta relativa de cada `guion_sesionN.txt`.

Cubre RF-013 y CSE-009.

## Grupo D: pruebas de integración del orquestador

### D1. Retry por incoherencia narrativa

Usar una primera respuesta con guion inválido y una segunda válida. Verificar que:

- la primera tentativa queda registrada como fallo;
- el prompt de reintento incluye el diagnóstico audiovisual;
- la sesión termina completada en el segundo intento.

Cubre RF-011 y CSE-006.

### D2. No escritura directa del orquestador

Interceptar o inspeccionar las operaciones permitidas y verificar que el orquestador solo delega en `pra_helper.py`; el archivo de audio debe ser creado por el helper.

Cubre las reglas constitucionales.

### D3. Timeout de pruebas internas

Verificar que un fallo o bloqueo de la suite de calidad no deja al orquestador esperando indefinidamente y que retorna el código de timeout controlado existente.

Cubre la garantía de no bloqueo del flujo.

## Grupo E: pruebas constitucionales

### E1. Audio textual, no binario

Una corrida válida debe contener archivos `.txt` bajo `assets/audio/` y no crear MP3, WAV u otros binarios de audio.

### E2. Protección del lote

La limpieza debe conservar:

```text
assets/audio/guion_sesionN.txt
backup/fuente/assets/audio/guion_sesionN.txt
```

### E3. Sin CSS inline ni cambios de responsabilidad

La incorporación del BLOQUE 6 no debe permitir CSS inline, escritura directa del orquestador ni archivos Blade dentro de `assets/audio/`.

## Matriz de trazabilidad

| Requisito | Pruebas |
|---|---|
| RF-001 a RF-003 | A1, A6, C1 |
| RF-004 a RF-006 | A2, A3, A5 |
| RF-007 y RF-008 | C1, C4, C5 |
| RF-009 y RF-010 | C3, D1 |
| RF-011 | B2, B3, C2, D1 |
| RF-012 | C5, E2 |
| RF-013 | C6 |
| RF-014 | C2 |
| Reglas constitucionales | D2, E1, E3 |

## Secuencia de ejecución TDD

1. Escribir Grupo A y confirmar fallos por funciones inexistentes.
2. Escribir Grupo B y confirmar que las puertas de calidad aún no existen.
3. Escribir Grupo C y D con fixtures aisladas.
4. Escribir Grupo E para proteger las reglas constitucionales.
5. Implementar por fases del `plan.md` y ejecutar el grupo afectado después de cada cambio.
6. Ejecutar la suite completa con cobertura antes de declarar la iteración terminada.

## Criterio de aceptación del plan de pruebas

El plan queda listo para implementación cuando cada requisito tiene al menos una prueba prevista, los casos rojos están definidos, los fixtures necesarios están identificados y ninguna prueba requiere generar audio binario o depender de servicios externos.
