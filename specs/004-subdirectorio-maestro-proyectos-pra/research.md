# Decisiones Tecnicas: 004-subdirectorio-maestro-proyectos-pra

**Fecha**: 2026-08-24

---

## D-401: Nombre del subdirectorio maestro

**Decision**: `output_projects/`.

**Alternativas evaluadas**:
- `presentations/`: corto pero ambiguo (podria confundirse con assets de presentacion).
- `generated_projects/`: explicito pero verboso.

**Justificacion**: Eleccion directa del usuario. Explicito, estandarizado y deja claro que contiene los proyectos generados por PRA.

## D-402: Resolucion centralizada de la ruta base en pra_helper.py

**Decision**: Constante de modulo `OUTPUT_BASE_DIR` resuelta al importar:

```python
OUTPUT_BASE_DIR = Path(os.environ.get("PRA_OUTPUT_DIR", "output_projects"))
```

**Alternativas evaluadas**:
- Argumento CLI `--output-dir` en cada comando: rechazado; obligaria a propagar la bandera por todos los comandos y por el orquestador, duplicando superficie de API sin necesidad real.
- Hardcodear el literal `"output_projects"` en cada funcion: rechazado; viola el principio de punto unico y multiplica riesgos de desincronizacion.

**Justificacion**: Un solo punto de verdad + configurabilidad por entorno (CI) sin tocar contratos CLI existentes.

## D-403: get_project_dir() antepone la base

**Decision**: `get_project_dir(plan)` retorna `Path.cwd() / OUTPUT_BASE_DIR / carpeta_snake_case`. Es el unico punto donde se calcula la carpeta de un proyecto nuevo (`save-plan`).

**Justificacion**: Cambio minimo y determinista; toda la creacion de estructura fluye desde ahi.

## D-404: Busqueda dual del proyecto activo (nuevo primero, legacy como fallback)

**Decision**: `find_project_dir()` busca primero `<cwd>/OUTPUT_BASE_DIR/*/presentation_plan.json` (ordenado) y, si no hay resultados, repite el escaneo actual sobre `<cwd>`.

**Alternativas evaluadas**:
- Busqueda exclusiva en el nuevo directorio: romperia proyectos legacy existentes (p. ej. `intro_docker/` ya generado en la raiz).
- Migracion automatica de proyectos legacy: rechazada; mutaciones implicitas de archivos fuera del alcance del comando violarian el principio de menor sorpresa.

**Justificacion**: Compatibilidad sin migracion forzada; precedencia clara ante colisiones.

## D-405: buscar_proyecto() del orquestador replica la estrategia dual

**Decision**: Misma logica D-404 implementada en `pra_orchestrator.py`. Se evaluo importar la funcion del motor, pero el orquestador se mantiene deliberadamente desacoplado (solo subprocess hacia `pra_helper.py`), por lo que se replica la logica con su propia constante derivada de la misma variable de entorno `PRA_OUTPUT_DIR`.

**Justificacion**: Consistencia de comportamiento sin acoplar modulos ni romper el contrato "el orquestador no importa al motor".

## D-406: outputs.zip dentro del subdirectorio maestro

**Decision**: `cmd_zip` escribe `<OUTPUT_BASE_DIR>/outputs.zip` (en lugar de `<cwd>/outputs.zip`), conservando `arcname` relativo al proyecto y las exclusiones de artefactos de orquestacion.

**Alternativas evaluadas**:
- Mantener el zip en la raiz: contradice el objetivo de raiz limpia.
- Zip dentro de la carpeta del propio proyecto: riesgo de auto-inclusion recursiva en corridas posteriores y ensucia el arbol entregable.

**Justificacion**: El zip es artefacto de salida colectivo; pertenece junto a los proyectos que empaqueta.

## D-407: Estrategia de pruebas

**Decision**: Tres niveles:
1. **Unitarias nuevas**: resolucion de `OUTPUT_BASE_DIR` (default y via env var), `get_project_dir`, precedencia de busqueda dual.
2. **Integracion**: actualizar aserciones de ruta en `tests/integration/` (`isolated_dir / "output_projects" / "intro_docker"`) y verificar ausencia de carpetas de proyecto en raiz.
3. **Constitucionales**: actualizar `tests/constitutional/` para escanear laminas bajo la nueva ubicacion; nueva regla: ninguna corrida deja artefactos de proyecto en la raiz.

**Justificacion**: La Constitucion exige suite verde >= 95 pruebas y cobertura >= 85%; el cambio toca rutas usadas transversalmente por todos los fixtures existentes.

## D-408: Sin cambios de esquema en orchestration_state.json ni codigos de salida

**Decision**: Los campos de estado que guardan rutas pasan a apuntar bajo el subdirectorio maestro, pero el esquema (fases, sesiones, intentos, reportes) y los codigos 0/1/2/3/4 permanecen intactos.

**Justificacion**: El contrato del orquestador (`specs/003-*/contracts/orchestrator-contract.md`) debe seguir vigente salvo el detalle de rutas; minimiza impacto en consumidores.
