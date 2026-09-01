# Plan de implementación: guion narrativo y coherencia audiovisual

**Fecha**: 2026-09-01  
**Especificación**: [spec.md](./spec.md)  
**Estado**: previo a implementación

## 1. Estrategia

La iteración se ejecutará con TDD:

1. ampliar fixtures y escribir pruebas rojas;
2. ejecutar únicamente esas pruebas y confirmar el fallo;
3. implementar el parser y el contrato mínimo;
4. integrar la escritura del guion en `pra_helper.py`;
5. añadir las puertas de coherencia en consolidación y orquestación;
6. ejecutar pruebas enfocadas y luego la suite completa;
7. actualizar documentación solo después del estado verde.

No se implementará ningún cambio de producción antes de completar la fase de pruebas rojas.

## 2. Diseño arquitectónico

### 2.1 `pra_helper.py`

Será responsable de:

- parsear el bloque narrativo;
- normalizar sus índices frente a `orden` del plan;
- validar marcas, duplicados, vacíos y referencias;
- crear `assets/audio/`;
- escribir `guion_sesionN.txt`;
- incluir el archivo en el respaldo de fuente;
- exponer el reporte estructurado a `process-session` y `consolidate`.

La validación debe ser pura siempre que sea posible. La escritura ocurrirá después de que el contenido haya sido parseado y validado.

### 2.2 `pra_orchestrator.py`

Será responsable de:

- incluir en el prompt de reflexión los errores audiovisuales;
- tratar la incoherencia narrativa como fallo de sesión cuando sea bloqueante;
- preservar el comportamiento de reintentos;
- no escribir el archivo de audio directamente.

### 2.3 Prompt de sesión

La plantilla de sesión se ampliará para que el modelo reciba:

- objetivo de la sesión;
- objetivo e insumos de cada lámina;
- rol visual de cada lámina;
- reglas de narración;
- convención de índices basada en cero;
- formato obligatorio del BLOQUE 6.

La instrucción pedagógica será: la narración expresa la idea y la lámina la hace visible; no se debe duplicar literalmente el audio en HTML.

## 3. Decisiones de diseño

### D1. Un archivo por sesión

Se usará `assets/audio/guion_sesionN.txt`, no un único archivo global. Esto permite construir y reanudar sesiones de forma independiente.

### D2. Guion como artefacto fuente

El archivo bajo `assets/audio/` será el artefacto final textual. Su copia en `backup/fuente/` será la fuente reconsolidable. `consolidate` no regenerará ni reescribirá el guion.

### D3. Índices separados

El plan seguirá usando `orden` desde uno y el guion usará `[slide: N]` desde cero. El sistema hará la conversión internamente y la mostrará en diagnósticos con ambos valores cuando sea útil.

### D4. Diagnóstico en lugar de reparación silenciosa

El sistema no agregará marcas, moverá texto ni inventará narración para hacer pasar la validación. Reportará la anomalía y dejará que el reintento del LLM la corrija.

### D5. Dos niveles de validación

- Estructural: siempre determinista y bloqueante en consolidación cuando falta una referencia.
- Semántica básica: comparación de objetivos e insumos con el texto disponible; advertencia por defecto y bloqueante en modo estricto si el contrato lo permite.

### D6. Compatibilidad gradual

Se conservará un modo de lectura de respuestas antiguas sin BLOQUE 6 para no romper reanudaciones existentes. `PRA_AUDIO_ESTRICTO=1` y los proyectos nuevos exigirán el bloque.

## 4. Cambios previstos por archivo

- `research_prompts_templates/presentation_slide_meta_prompt.md`: añadir contrato y reglas del BLOQUE 6.
- `pra_helper.py`: parser, validador, escritura, respaldo y reporte de audio.
- `pra_orchestrator.py`: propagación de diagnósticos y retry específico.
- `mocks_llm/sesion1.txt`, `mocks_llm/sesion2.txt`: añadir respuestas narrativas deterministas.
- `tests/conftest.py`: fixture de respuesta con guion y casos inválidos.
- `tests/unit/`: parser, normalización y validadores.
- `tests/integration/`: CLI, consolidación, cleanup y determinismo.
- `tests/constitutional/`: delegación exclusiva, ausencia de audio binario y preservación.
- `README.md`, `AGENTS.md`, `SESION_PRA_RESUMEN.md`: documentación posterior al estado verde.

Estos cambios son planificación; no se aplican en esta etapa documental.

## 5. Flujo objetivo

```text
init
  -> save-plan
  -> prompt-session N con objetivos e insumos
  -> LLM: BLOQUES 1-5 + BLOQUE 6 narrativo
  -> process-session N
  -> validar plan, guion y láminas
  -> escribir assets/audio/guion_sesionN.txt
  -> siguiente sesión
  -> consolidate con puerta audiovisual
  -> pytest
  -> cleanup preservando audio y backup/fuente
```

## 6. Puertas de calidad

### Puerta P1: contrato

El bloque narrativo existe, tiene formato reconocido y usa índices válidos.

### Puerta P2: cobertura

Todas las láminas del plan tienen narración y no hay entradas narrativas sin lámina.

### Puerta P3: contenido

Las entradas no están vacías y no introducen referencias estructurales desconocidas.

### Puerta P4: materialización

El archivo final existe en la ruta esperada, es UTF-8, es idempotente y está respaldado.

### Puerta P5: consolidación

No se produce el manifest final si la coherencia audiovisual bloqueante falla.

### Puerta P6: limpieza

El lote protegido conserva audio y la fuente interna; no se crean copias residuales fuera del contrato.

## 7. Riesgos y mitigaciones

- **Numeración ambigua**: fijar `[slide: N]` en cero y probar la conversión con primera y última lámina.
- **Texto narrativo excesivamente largo**: validar contenido, no imponer longitud rígida en la primera versión; añadir límites solo si el producto los necesita.
- **Duplicación entre audio y HTML**: instrucción explícita en el prompt y advertencia semántica, sin exigir igualdad textual.
- **Reanudación parcial**: escribir el guion junto con el resultado validado de la sesión y usar escritura atómica si el patrón local lo permite.
- **Respuestas antiguas**: compatibilidad fuera del modo estricto y rechazo explícito en proyectos nuevos.
- **Falsos positivos semánticos**: no convertir heurísticas en bloqueo por defecto.

## 8. Criterio de salida de la implementación

La implementación podrá comenzar después de que:

- la especificación y este plan sean aprobados;
- las pruebas rojas estén definidas en `test_plan.md`;
- los contratos de CLI y datos estén claros;
- se confirme que no se modifica aún código de producción;
- las fixtures necesarias estén identificadas.
