# -*- coding: utf-8 -*-
"""Pruebas unitarias del subdirectorio maestro de salida (iteracion 005)."""
from pathlib import Path
import os
import sys
import pytest
import pra_helper as ph
import pra_orchestrator as po

def _sembrar_proyecto(raiz, nombre="intro_docker"):
    d = raiz / nombre
    d.mkdir(parents=True, exist_ok=True)
    (d / "presentation_plan.json").write_text("{}", encoding=ph.ENCODING)
    return d

def test_output_base_dir_valor_constante():
    """FR-501: la constante default es la especificada."""
    assert ph.DEFAULT_OUTPUT_BASE_DIR == Path(r"C:\laragon\www\product_samples\slides")

def test_motor_y_orquestador_comparten_la_misma_base():
    """D-501: motor y orquestador resuelven la base identica."""
    assert ph.OUTPUT_BASE_DIR == po.OUTPUT_BASE_DIR

def test_get_project_dir_retorna_base_correcta(isolated_dir):
    """T503: get_project_dir usa la base resuelta."""
    plan = {"carpeta_snake_case": "demo_curso"}
    # ph.OUTPUT_BASE_DIR es el tmp asignado en conftest
    ruta = ph.get_project_dir(plan, interactive=False)
    assert ruta == ph.OUTPUT_BASE_DIR / "demo_curso"

def test_find_project_dir_prioriza_subdirectorio_maestro(isolated_dir):
    en_maestro = _sembrar_proyecto(ph.OUTPUT_BASE_DIR)
    _sembrar_proyecto(isolated_dir, "legacy_proyecto")
    assert ph.find_project_dir() == en_maestro


def test_find_project_dir_prioriza_cwd_si_ya_es_un_proyecto(monkeypatch, tmp_path):
    base = tmp_path / "slides"
    base.mkdir()
    intro = base / "intro_docker"
    target = base / "modulo2_control_flujo"
    intro.mkdir()
    target.mkdir()
    (intro / "presentation_plan.json").write_text("{}", encoding=ph.ENCODING)
    (target / "presentation_plan.json").write_text("{}", encoding=ph.ENCODING)

    monkeypatch.chdir(target)
    monkeypatch.setattr(ph, "_base_salida_candidata", lambda: base)

    assert ph.find_project_dir() == target


def test_resolve_base_dir_interactivo_exito(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    ruta_input = tmp_path / "custom_base"
    ruta_input.mkdir()
    monkeypatch.setattr("builtins.input", lambda prompt: str(ruta_input))
    monkeypatch.delenv("PRA_OUTPUT_DIR")
    monkeypatch.setattr(ph, "DEFAULT_OUTPUT_BASE_DIR", Path("no_existe"))
    base_resolvida = ph.resolve_output_base_dir(interactive=True)
    assert base_resolvida == ruta_input

def test_resolve_base_dir_no_interactivo_falla(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.delenv("PRA_OUTPUT_DIR")
    monkeypatch.setattr(ph, "DEFAULT_OUTPUT_BASE_DIR", Path("no_existe"))
    with pytest.raises(SystemExit) as e:
        ph.resolve_output_base_dir(interactive=True)
    assert e.value.code == 1
