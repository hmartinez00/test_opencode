# -*- coding: utf-8 -*-
"""Pruebas unitarias del subdirectorio maestro de salida (iteracion 004 - T407)."""
from pathlib import Path

import pra_helper as ph
import pra_orchestrator as po


def _sembrar_proyecto(raiz, nombre="intro_docker"):
    """Crea un directorio con presentation_plan.json y retorna su Path."""
    d = raiz / nombre
    d.mkdir(parents=True)
    (d / "presentation_plan.json").write_text("{}", encoding=ph.ENCODING)
    return d


def test_output_base_dir_por_defecto_es_output_projects():
    """FR-402: el subdirectorio maestro por defecto es output_projects."""
    assert ph.OUTPUT_BASE_DIR == Path("output_projects")


def test_motor_y_orquestador_comparten_la_misma_base():
    """D-405: motor y orquestador resuelven la base identica."""
    assert ph.OUTPUT_BASE_DIR == po.OUTPUT_BASE_DIR


def test_get_project_dir_antepon_el_subdirectorio_maestro(isolated_dir):
    """T402: get_project_dir retorna <cwd>/output_projects/<carpeta>."""
    plan = {"carpeta_snake_case": "demo_curso"}
    ruta = ph.get_project_dir(plan)
    assert ruta == isolated_dir / ph.OUTPUT_BASE_DIR / "demo_curso"


def test_get_project_dir_acepta_campo_normalizado_folder_name(isolated_dir):
    plan = {"folder_name": "otro_curso"}
    ruta = ph.get_project_dir(plan)
    assert ruta == isolated_dir / ph.OUTPUT_BASE_DIR / "otro_curso"


def test_find_project_dir_prioriza_subdirectorio_maestro(isolated_dir):
    """US2 esc.3: ante proyectos en ambos lugares precede el del maestro."""
    en_maestro = _sembrar_proyecto(isolated_dir / ph.OUTPUT_BASE_DIR)
    _sembrar_proyecto(isolated_dir, "legacy_proyecto")
    encontrado = ph.find_project_dir()
    assert encontrado == en_maestro


def test_find_project_dir_fallback_a_proyecto_legacy_en_raiz(isolated_dir):
    """US2 esc.2: sin proyectos en el maestro se localiza el legacy de la raiz."""
    legacy = _sembrar_proyecto(isolated_dir, "legacy_proyecto")
    encontrado = ph.find_project_dir()
    assert encontrado == legacy


def test_find_project_dir_sin_proyectos_retorna_none(isolated_dir):
    assert ph.find_project_dir() is None


def test_buscar_proyecto_del_orquestador_prioriza_maestro(isolated_dir):
    """US5 esc.1: el orquestador resuelve el proyecto dentro del maestro."""
    en_maestro = _sembrar_proyecto(isolated_dir / po.OUTPUT_BASE_DIR)
    _sembrar_proyecto(isolated_dir, "legacy_proyecto")
    assert po.buscar_proyecto() == en_maestro


def test_buscar_proyecto_del_orquestador_fallback_a_raiz(isolated_dir):
    legacy = _sembrar_proyecto(isolated_dir, "legacy_proyecto")
    assert po.buscar_proyecto() == legacy
