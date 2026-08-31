# Checklist de Requerimientos - Iteracion 009 (Robustez y Coherencia del Flujo PRA)

**Especificacion**: [spec.md](../spec.md)

Marque cada item segun su estado: `[ ]` pendiente, `[x]` cumplido, `[~]` parcial.

## Coherencia plan vs. laminas en consolidacion

- [ ] FR-901: `_analizar_coherencia` calcula el conjunto de laminas declaradas por sesion.
- [ ] FR-902: Detecta laminas huerfanas (en FS, no en plan).
- [ ] FR-903: Detecta laminas faltantes (en plan, no en FS).
- [ ] FR-904: Detecta laminas duplicadas (id repetido en el plan).
- [ ] FR-905: El JSON de `consolidate` incluye el bloque `coherencia` con `huerfanas`/`faltantes`/`duplicadas`.
- [ ] FR-906: Ante incoherencia bloqueante, `ok:false` y NO se genera manifest incompleto.
- [ ] FR-907: Sin incoherencias, manifest completo y `ok:true`.
- [ ] FR-908: Se conserva la validacion de CSS inline sobre las laminas consolidadas.

## Calidad del plan

- [ ] FR-909: `save-plan` advierte si `class_registry.json` y `js_registry.json` quedarian vacios.
- [ ] FR-910: `save-plan` advierte por cada lamina con `insumos` vacios.
- [ ] FR-911: Umbral `PRA_PLAN_ESTRICTO=1` eleva advertencias bloqueantes a error.

## Backend `opencode`

- [ ] FR-912: `_resolver_binario_opencode` resuelve via PATH y rutas conocidas.
- [ ] FR-913: Si no se resuelve, reporta `BACKEND_NO_DISPONIBLE` con rutas intentadas y PATH, sin traceback crudo.

## Seleccion del proyecto activo

- [ ] FR-914: Se detecta ambiguedad (varios proyectos) sin `PRA_ACTIVE_PROJECT`.
- [ ] FR-915: Con ambiguedad, se emite advertencia listando candidatos.

## Criterios de exito

- [ ] SC-901: Una lamina fuera del plan se reporta como huerfana (no se omite en silencio).
- [ ] SC-902: Consolidacion con incoherencias -> `ok:false`, sin manifest incompleto.
- [ ] SC-903: `save-plan` advierte de planes sin registros/insumos y bloquea solo con `PRA_PLAN_ESTRICTO`.
- [ ] SC-904: `--backend opencode` resuelve el binario o reporta `BACKEND_NO_DISPONIBLE`.
- [ ] SC-905: Proyectos ambiguos sin `PRA_ACTIVE_PROJECT` -> advertencia.
- [ ] SC-906: Suite completa en verde y cobertura >= 85% en ambos modulos.

## No-regresion

- [ ] Los flujos coherentes existentes (mocks) consolidan igual.
- [ ] Los reportes JSON nuevos son aditivos (no rompen consumidores previos).
- [ ] `save-plan` conserva la normalizacion de ambos juegos de nombres de campo.
