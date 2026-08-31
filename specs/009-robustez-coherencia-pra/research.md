# Investigacion y Decisiones Tecnicas: Robustez y Coherencia del Flujo PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Este documento registra las decisiones tecnicas (D1-D8) para la iteracion 009. Cada decision responde a uno de los cuatro inconvenientes detectados al levantar la presentacion real `modulo1_fundamentos_python`.

---

## D1 - Oracle de coherencia en consolidacion: conjunto plan vs. conjunto FS (elegida)

**Problema**: `_consolidate_project` itera solo por `plan.sesiones[].laminas`, descartando silenciosamente las laminas escritas en `sesion[N]/` no declaradas.

**Alternativas**:
- **A (elegida)**: Calcular el conjunto de archivos reales de `sesion[N]/` (`.blade.php`) y contrastarlo contra el conjunto de `id_kebab_case` declarados para esa sesion. La diferencia produce tres listas: `huerfanas` (en FS, no en plan), `faltantes` (en plan, no en FS) y `duplicadas` (ids repetidos en el plan).
- B: Confiar en que el plan siempre es la unica fuente (comportamiento actual, defectuoso).
- C: Consolidar TODO lo que este en `sesion[N]/` ignorando el plan (perderia el orden, los `data_title` y la intencion del plan).

**Justificacion**: El plan es la "unica fuente de verdad" del orden y la intencion, pero el FS refleja lo que realmente se construyo. Contrastar ambos revela desalineaciones que hoy fallan en silencio. Mantiene el plan como fuente del orden, pero valida contra los artefactos reales.

## D2 - Semantica de la puerta de coherencia: aborto ante incoherencias bloqueantes (elegida)

**Alternativas**:
- **A (elegida)**: Si existen `huerfanas`, `faltantes` o `duplicadas`, la consolidacion devuelve `ok: false`, NO escribe un manifest incompleto, y reporta el bloque `coherencia`. El usuario corrige (edita el plan o las laminas) y re-consolida.
- B: Siempre consolidar lo que se pueda y solo advertir (comportamiento actual: escribe manifest parcial).
- C: Abortar con excepcion inmediata sin reporte estructurado.

**Justificacion**: Un manifest incompleto es un entregable invalido que el integrador Laravel copiaria sin saberlo. Abortar con reporte estructurado fuerza la correccion antes de integrar, alineandose con el espiritu de "no fallar en silencio".

## D3 - Estructura del reporte `coherencia` (elegida)

**Alternativas**:
- **A (elegida)**: Bloque `coherencia` en el JSON de salida de `consolidate` con listas `huerfanas`, `faltantes`, `duplicadas`; cada entrada con `sesion`, `id` y `sugerencia`.
- B: Solo un listado textual de errores en `errores`.

**Justificacion**: Un reporte estructurado es verificable por tests y accionable por el usuario/orquestador, en linea con los reportes JSON ya existentes (`limpiar`, `process-session`).

## D4 - Validacion de calidad del plan en `save-plan`: advertencias no bloqueantes + umbral configurable (elegida)

**Alternativas**:
- **A (elegida)**: `save-plan` emite advertencias cuando los registros CSS/JS quedan vacios o hay laminas sin `insumos`. Por defecto no bloquea; una variable de entorno (p.ej. `PRA_PLAN_ESTRICTO=1`) eleva las advertencias a errores (aborta el guardado).
- B: Bloquear siempre ante registros vacios o insumos faltantes (quebraria flujos legacy que generan plan solo con Parte 1).
- C: No validar (comportamiento actual).

**Justificacion**: Se preserva la compatibilidad con planes legacy de una sola parte, pero se alerta al autor. El umbral configurable permite exigir planes completos cuando la organizacion lo requiera.

## D5 - Resolucion robusta del binario `opencode` (elegida)

**Alternativas**:
- **A (elegida)**: Nueva funcion `_resolver_binario_opencode()` que busca via `shutil.which('opencode')` y, si falla, revisa rutas conocidas deterministas (`~/.opencode/bin/opencode`, `~/AppData/Roaming/npm/opencode.cmd`, etc.) para el SO actual. Devuelve la ruta o `None`. El backend usa el resultado; si es `None`, reporta `BACKEND_NO_DISPONIBLE` con las rutas intentadas y el PATH relevante.
- B: Confiar unicamente en el PATH (comportamiento actual, falla en subprocess heredado de Git Bash).

**Justificacion**: El binario esta en `C:\Users\HP\.opencode\bin\opencode.exe` y aunque esta en el PATH de Windows, el subprocess del orquestador lanzado desde Git Bash no lo resuelve de forma fiable. Revisar rutas conocidas elimina la dependencia del shell de lanzamiento.

## D6 - Deteccion de ambiguedad del proyecto activo (elegida)

**Alternativas**:
- **A (elegida)**: La funcion de seleccion de proyecto activo filtra los candidatos validos (excluyendo `backup/`, `themes/` y otros directorios no-proyecto) y, si hay mas de uno sin `PRA_ACTIVE_PROJECT`, emite una advertencia listando los candidatos antes de aplicar el criterio por defecto (o abortar segun config).
- B: Mantener siempre el criterio "primero alfabetico" sin aviso (comportamiento actual, causo el issue).

**Justificacion**: Advierte al usuario de que su corrida podria operar sobre el proyecto equivocado. Se preserva el determinismo (con `PRA_ACTIVE_PROJECT` o con proyecto unico) pero se hace visible la ambiguedad.

## D7 - Compatibilidad y no-regresion en consolidacion (elegida)

**Alternativas**:
- **A (elegida)**: El nuevo oracle se activa de forma que los flujos existentes con plan y laminas coherentes (los mocks de prueba) sigan consolidando igual; solo cambia el comportamiento cuando hay incoherencia. Se actualizan los fixtures de prueba para que el plan y las laminas sean coherentes por defecto.
- B: Introducir el oracle como una flag que el usuario debe activar (menos proteccion por defecto).

**Justificacion**: El objetivo es detectar el fallo por defecto, no requerir opt-in. Los fixtures existentes ya son coherentes (plan y `sesion1/` con las mismas laminas), por lo que no deberian verse afectados salvo ajustes menores.

## D8 - Diagnostico del backend no disponible (elegida)

**Alternativas**:
- **A (elegida)**: Cuando el binario no se resuelve, el orquestador registra en el estado y en el log un error `BACKEND_NO_DISPONIBLE` que incluye las rutas intentadas y un fragmento del PATH, devolviendo `EXIT_INTERNO` (o el codigo que corresponda) sin traceback crudo.
- B: Lanzar la excepcion original (traceback confuso para el usuario final).

**Justificacion**: Un lexico de error claro (como `PRA_OUTPUT_DIR_INVALID` de la iteracion 005) permite al usuario actuar sin depurar tracebacks.

---

## Sintesis

| Problema | Fallo detectado | Decision |
|---|---|---|
| Lamina fuera del plan | Omitida silenciosamente del manifest | Oracle de coherencia plan vs. FS (D1, D2, D3) |
| Plan sin registros/insumos | Registros vacios + insumos `[]` | Validacion de calidad no bloqueante + umbral (D4) |
| Backend opencode | Subprocess no resuelve el binario | Resolucion por PATH + rutas conocidas (D5, D8) |
| Proyecto activo ambiguo | Opera sobre el proyecto equivocado | Deteccion de ambiguedad con advertencia (D6) |
| Regresiones | Mocks coherentes podrian romperse | Oracle activo por defecto pero no-regresivo (D7) |
