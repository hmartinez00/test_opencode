# Guia de Validacion: 004-subdirectorio-maestro-proyectos-pra

**Fecha**: 2026-08-24

---

## Escenario 1: Suite de calidad (obligatorio)

```bash
pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```

Esperado: todas las pruebas en verde (95 previas + nuevas), cobertura >= 85% en `pra_helper.py` y `pra_orchestrator.py`.

## Escenario 2: Corrida E2E desatendida con backend mock

En un workspace limpio o tras eliminar artefactos previos:

```bash
python pra_orchestrator.py run ejemplos/introduccion_docker/documento_fuente.md --backend mock
```

Verificaciones:

1. Exit code `0`.
2. El arbol completo existe SOLO bajo el subdirectorio maestro:

```text
output_projects/
└── intro_docker/
    ├── presentation_plan.json
    ├── class_registry.json
    ├── js_registry.json
    ├── manifest_draft.blade.php
    ├── styles.blade.php / scripts.blade.php
    ├── sesion1/ sesion2/
    └── *_additions/
```

3. La raiz NO contiene `intro_docker/` ni `outputs.zip`.
4. Existe `output_projects/outputs.zip` y su contenido excluye artefactos de orquestacion.

## Escenario 3: Flujo manual respeta la ubicacion

```bash
python pra_helper.py init ejemplos/introduccion_docker/documento_fuente.md > prompt.txt
# ... generar plan LLM ...
python pra_helper.py save-plan '<json_del_plan>'
python pra_helper.py prompt-session 1 > prompt_s1.txt
# ... generar respuesta LLM ...
python pra_helper.py process-session 1 '<respuesta_llm>'
python pra_helper.py zip
```

Verificaciones:

- Tras `save-plan`, la salida JSON reporta `"proyecto": "output_projects\\intro_docker"` (o equivalente con separador de plataforma) y ninguna carpeta aparece en la raiz.
- `prompt-session`/`process-session` localizan el proyecto sin configuracion extra.
- `zip` deja el entregable en `output_projects/outputs.zip`.

## Escenario 4: Override por variable de entorno

```bash
PRA_OUTPUT_DIR=custom_out python pra_helper.py save-plan '<json>'
PRA_OUTPUT_DIR=custom_out python pra_helper.py zip
```

Esperado: arbol y zip bajo `custom_out/`.

## Escenario 5: Compatibilidad legacy (fallback)

1. Crear manualmente `<raiz>/proyecto_legacy/presentation_plan.json` (minimo valido).
2. Ejecutar `python pra_helper.py prompt-session 1`.
3. Esperado: el comando resuelve el proyecto legacy desde la raiz cuando no hay proyecto en el maestro; si hay proyectos en ambos lugares, precede el del maestro.

## Escenario 6: Determinismo

Dos corridas mock consecutivas en workspaces temporales distintos producen arboles identicos byte a byte (excluyendo logs con timestamps).
