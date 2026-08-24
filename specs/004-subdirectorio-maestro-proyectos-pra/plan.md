# Plan de Implementacion: Subdirectorio Maestro para Proyectos Generados (004-subdirectorio-maestro-proyectos-pra)

**Rama**: `004-subdirectorio-maestro-proyectos-pra` | **Fecha**: 2026-08-24 | **Especificacion**: [spec.md](./spec.md) | **Decisiones**: [research.md](./research.md)

---

## Resumen

Este plan aísla todos los proyectos de presentacion generados en un subdirectorio maestro (`output_projects/`, configurable via `PRA_OUTPUT_DIR`), eliminando la contaminacion de la raiz del repositorio. El cambio se materializa en tres frentes: (1) `pra_helper.py` centraliza la ruta base en una constante y antepone el subdirectorio en creacion (`get_project_dir`) y busqueda (`find_project_dir`, con fallback legacy); (2) `pra_orchestrator.py` replica la busqueda dual en `buscar_proyecto()` y persiste rutas coherentes en su estado; (3) la suite de pruebas actualiza sus aserciones de ruta y agrega pruebas unitarias, de integracion y constitucionales para la nueva ubicacion.

---

## Contexto Tecnico

**Lenguaje/Version**: Python 3.11+ (stdlib unicamente; sin dependencias nuevas)

**Puntos exactos de cambio en el codigo**:

| Archivo | Simbolo / Linea aprox. | Cambio |
|---|---|---|
| `pra_helper.py` | constante nueva junto a las existentes (~L26-32) | `OUTPUT_BASE_DIR = Path(os.environ.get("PRA_OUTPUT_DIR", "output_projects"))` |
| `pra_helper.py` | `get_project_dir()` (~L162) | retornar `Path.cwd() / OUTPUT_BASE_DIR / folder` |
| `pra_helper.py` | `find_project_dir()` (~L307) | escanear primero `cwd/OUTPUT_BASE_DIR`; fallback al escaneo actual sobre `cwd` |
| `pra_helper.py` | `cmd_zip` ruta del zip (~L657) | escribir `Path.cwd() / OUTPUT_BASE_DIR / "outputs.zip"`; asegurar mkdir del maestro |
| `pra_orchestrator.py` | `buscar_proyecto()` (~L344) | misma estrategia dual (maestro primero, fallback raiz); base derivada de `PRA_OUTPUT_DIR` con mismo default |
| `tests/conftest.py` | fixtures | sin cambios de logica; las aserciones de consumidores cambian |
| `tests/integration/*`, `tests/unit/*`, `tests/constitutional/*` | aserciones `isolated_dir / "intro_docker"` | pasar a `isolated_dir / "output_projects" / "intro_docker"` + nuevas pruebas de ubicacion |

**Nota**: `orchestration_state.json` y `outputs.zip` permanecen EXCLUIDOS del zip y del versionado (`.gitignore` vigente), sin cambios de esquema ni codigos de salida del orquestador.

---

## Estrategia por Fases

1. **Fase 1 - Motor (`pra_helper.py`)**: constante + `get_project_dir` + `find_project_dir` dual + zip en maestro.
2. **Fase 2 - Orquestador (`pra_orchestrator.py`)**: `buscar_proyecto` dual; verificar que puertas post-sesion y `resume` operen sobre las rutas nuevas (sin tocar contratos).
3. **Fase 3 - Pruebas**: actualizar aserciones existentes; agregar unitarias (constante/env var/precedencia), integracion (E2E mock con arbol bajo maestro y raiz limpia) y constitucional (cero artefactos de proyecto en raiz tras corrida completa).
4. **Fase 4 - Documentacion**: actualizar arbol de directorios en `AGENTS.md`, `README.md`, `SESION_PRA_RESUMEN.md`; registrar la variable `PRA_OUTPUT_DIR`.

---

## Verificacion Constitucional

| Principio | Estado | Mecanismo |
|-----------|--------|-----------|
| I. Cero CSS Inline | CUMPLE (sin regresion) | Validaciones y puertas intactas; solo cambia la ruta escaneada |
| II. JavaScript Acotado | CUMPLE (sin regresion) | Sin cambios en scripts ni registries |
| III. Preservacion Determinista | CUMPLE | Punto unico de escritura se mantiene: `pra_helper.py` sigue siendo el unico escritor de artefactos; la ruta base es determinista |
| IV. Construccion Progresiva | CUMPLE (sin regresion) | Secuencialidad de sesiones intacta; `find_project_dir` garantiza localizar el proyecto activo |
| V. Documentacion en Espanol | CUMPLE | Specs, mensajes y docs actualizados en espanol |

---

## Metricas de Calidad y Criterios de Parada

- Suite completa verde: 95 pruebas previas + nuevas, `0 failures`.
- Cobertura: `pra_helper.py` >= 85% y `pra_orchestrator.py` >= 85% (sin regresion).
- Comando de verificacion:
```bash
pytest --cov=pra_helper --cov=pra_orchestrator --cov-report=term-missing
```
- E2E mock: corrida completa deja el arbol SOLO bajo `output_projects/` y la raiz sin carpetas de proyecto ni `outputs.zip`.

## Riesgos y Mitigaciones

| Riesgo | Mitigacion |
|---|---|
| Tests existentes rompen por cambio de ruta | Actualizacion sistematica de aserciones en Fase 3 antes de cerrar |
| Proyectos legacy inaccesibles | Busqueda dual con fallback (D-404/D-405); sin migracion implicita |
| Divergencia de default entre motor y orquestador | Ambos leen `PRA_OUTPUT_DIR` con idéntico default literal documentado |
