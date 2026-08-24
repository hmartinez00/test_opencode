# Lista de Tareas: 004-subdirectorio-maestro-proyectos-pra

**Fecha**: 2026-08-24 | **Especificacion**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Fase 1: Motor `pra_helper.py` (T401-T404)

- [ ] **T401** Agregar constante de modulo `OUTPUT_BASE_DIR` resuelta desde `PRA_OUTPUT_DIR` (default `output_projects`) junto a las constantes existentes.
- [ ] **T402** Modificar `get_project_dir()` para retornar `Path.cwd() / OUTPUT_BASE_DIR / <carpeta_snake_case>`.
- [ ] **T403** Modificar `find_project_dir()`: busqueda primero en `cwd/OUTPUT_BASE_DIR`, fallback al escaneo actual sobre la raiz (proyectos legacy).
- [ ] **T404** Modificar `cmd_zip`: crear el subdirectorio maestro si falta y escribir `outputs.zip` dentro de el, conservando exclusiones y `arcname`.

## Fase 2: Orquestador `pra_orchestrator.py` (T405-T406)

- [ ] **T405** Replicar estrategia dual en `buscar_proyecto()` (maestro primero, fallback raiz), derivando la base de `PRA_OUTPUT_DIR` con idéntico default.
- [ ] **T406** Verificar/ajustar que las puertas post-sesion (`validar_post_sesion`) y la fase `zip` del orquestador operen sobre rutas bajo el maestro; sin cambios de esquema de estado ni codigos de salida.

## Fase 3: Suite de Pruebas (T407-T410)

- [ ] **T407** Unitarias nuevas: default de `OUTPUT_BASE_DIR`, override por env var, `get_project_dir`, precedencia de `find_project_dir` (maestro > raiz) y caso legacy-only.
- [ ] **T408** Actualizar aserciones de ruta en `tests/integration/test_cli_save_plan.py`, `tests/integration/test_cli_session.py` y demas tests que referencian `isolated_dir / "intro_docker"`.
- [ ] **T409** Integracion nueva: E2E mock completo verificando arbol bajo `output_projects/intro_docker/`, raiz limpia y `output_projects/outputs.zip` presente.
- [ ] **T410** Constitucional nueva: tras una corrida completa no existen carpetas de proyecto ni `outputs.zip` en la raiz; validaciones anti CSS inline siguen aplicando sobre laminas bajo el maestro.

## Fase 4: Documentacion y Cierre (T411-T413)

- [ ] **T411** Actualizar arbol de directorios y reglas en `AGENTS.md`; documentar variable `PRA_OUTPUT_DIR`.
- [ ] **T412** Actualizar `README.md` (estructura generada, comandos y ejemplos) y anotar el cambio en `SESION_PRA_RESUMEN.md`.
- [ ] **T413** Ejecutar suite completa con cobertura; verificar >= 95 pruebas verdes y cobertura >= 85% en ambos modulos; corrida E2E mock final de validacion.

---

## Dependencias

- T402/T403/T404 dependen de T401.
- T405 depende conceptualmente de D-405 pero es implementable en paralelo a Fase 1.
- Fases 3 y 4 dependen de Fases 1 y 2 completadas.
