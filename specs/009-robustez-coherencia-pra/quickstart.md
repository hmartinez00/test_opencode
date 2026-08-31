# Guia de Validacion: Robustez y Coherencia del Flujo PRA

**Fecha**: 2026-08-31

**Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Esta guia describe como validar end-to-end los cuatro inconvenientes resueltos en la iteracion 009. Requiere implementar las fases de [tasks.md](./tasks.md) antes de poder ejecutar estas validaciones en modo "verde".

## 0. Entorno

- Todos los comandos se ejecutan desde `C:\laragon\www\test_opencode`.
- Ruta base de salida: `C:\laragon\www\product_samples\slides` (o `PRA_OUTPUT_DIR`).
- Suite: `python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing`.

## Escenario E1 - Coherencia plan vs. laminas (issue #4)

Objetivo: verificar que una lamina fuera del plan ya NO se omite silenciosamente.

```powershell
# 1. Levantar un proyecto de prueba (flujo manual)
$env:PRA_OUTPUT_DIR = "C:\laragon\www\product_samples\slides"
$env:PRA_ACTIVE_PROJECT = "modulo1_fundamentos_python"
python pra_helper.py init "C:\laragon\www\product_samples\slides\backup\Python de Cero a Pro\Lessons\modulo1_fundamentos.ipynb"
# 2. (generar plan + procesar sesion como en el flujo)

# 3. Introducir una lamina fuera del plan en la fuente interna
#    (p.ej. copiar un blade extra a sesion1/)

# 4. Consolidar: debe reportar incoherencia y NO emitir manifest incompleto
python pra_helper.py consolidate
```

Resultado esperado: el JSON de salida contiene `"coherencia": {"huerfanas": [...], "faltantes": [], "duplicadas": []}` y `"ok": false`.

## Escenario E2 - Validacion de calidad del plan (issues #2)

```powershell
# Guardar un plan solo con la Parte 1 (sin registros ni insumos)
python pra_helper.py save-plan '{ "titulo": "X", "carpeta_snake_case": "x", "sesiones": [ { "numero": 1, "laminas": [ {"id_kebab_case": "a", "insumos": []} ] } ] }'
```

Resultado esperado: el JSON de salida incluye `"advertencias": [...]` (registros vacios + lamina sin insumos) aunque el estado sea `exito`.

Repetir con `$env:PRA_PLAN_ESTRICTO = "1"`: el guardado debe abortar (estado `error`, `PLAN_INCOMPLETO_ESTRICTO`).

## Escenario E3 - Backend `opencode` robusto (issue #1)

```powershell
# Con opencode instalado en ~/.opencode/bin
python pra_orchestrator.py run "<documento>" --backend opencode --max-retries 1
```

Resultado esperado:
- Si el binario se resuelve -> la corrida procede (init/save-plan).
- Si no -> el estado/log registran `BACKEND_NO_DISPONIBLE` con las rutas intentadas y el PATH, sin traceback crudo.

Para verificar el diagnostico controladamente (sin depender de la instalacion):
```powershell
python pra_orchestrator.py run "<documento>" --backend opencode  # tras forzar resolucion None en pruebas
```

## Escenario E4 - Ambiguedad del proyecto activo (issue #3)

```powershell
# Tener al menos dos proyectos bajo la ruta base y NO definir PRA_ACTIVE_PROJECT
Remove-Item Env:PRA_ACTIVE_PROJECT    # si estaba definida
python pra_helper.py prompt-session 1
```

Resultado esperado: se emite una advertencia (stderr) listando los candidatos (p.ej. `filtros_multidimensionales`, `intro_docker`, `modulo1_fundamentos_python`), en lugar de elegir silenciosamente el primero alfabetico.

Con `$env:PRA_ACTIVE_PROJECT = "modulo1_fundamentos_python"`: sin advertencia y opcion determinista.

## Escenario E5 - No-regresion del flujo desatendido

```powershell
python pra_orchestrator.py run "C:\laragon\www\test_opencode\ejemplos\introduccion_docker\documento_fuente.md" --backend mock
```

Resultado esperado: la corrida completa sin incoherencias, con el lote protegido + `backup/fuente/` (fases de la iteracion 008). El oracle de coherencia no rompe flujos coherentes.

## Verificacion final

```powershell
python -m pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

Criterios:
- Suite completa en verde.
- Cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.
- Confirmar que los cuatro escenarios E1-E4 se comportan como se describe.
