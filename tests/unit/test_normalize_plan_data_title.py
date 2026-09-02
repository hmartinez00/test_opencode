# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pra_helper
from pra_helper import load_json


def test_normalize_plan_conserva_data_title():
    """A4: normalize_plan debe conservar data_title si existe."""
    plan_raw = {
        "titulo": "Test DT",
        "carpeta_snake_case": "test_dt",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {
                    "id_kebab_case": "a",
                    "tipo": "contenido",
                    "objetivo": "o1",
                    "insumos": [],
                    "data_title": "Titulo Real"
                }
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    lamina = plan["sesiones"][0]["laminas"][0]
    assert lamina.get("data_title") == "Titulo Real"


def test_normalize_plan_sin_data_title_no_crea_campo():
    """A4: Si no hay data_title, no se crea un campo fantasma."""
    plan_raw = {
        "titulo": "Test DT2",
        "carpeta_snake_case": "test_dt2",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {
                    "id_kebab_case": "a",
                    "tipo": "contenido",
                    "objetivo": "o1",
                    "insumos": []
                }
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    lamina = plan["sesiones"][0]["laminas"][0]
    assert "data_title" not in lamina


def test_save_plan_manifest_draft_usa_data_title(run_cli, isolated_dir):
    """A4: manifest_draft debe usar data_title del plan cuando existe."""
    plan_raw = {
        "titulo": "Test DT Draft",
        "carpeta_snake_case": "test_dt_draft",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "o",
                    "insumos": [],
                    "data_title": "Mi Titulo Real"
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan_raw))
    assert code == 0

    project_dir = Path(isolated_dir) / "product_samples" / "slides" / "test_dt_draft"
    draft = (project_dir / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert 'data-title="Mi Titulo Real"' in draft


def test_save_plan_manifest_draft_fallback(run_cli, isolated_dir):
    """A4: Sin data_title, manifest_draft usa fallback titulo_legible."""
    plan_raw = {
        "titulo": "Test DT FB",
        "carpeta_snake_case": "test_dt_fb",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "o",
                    "insumos": []
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan_raw))
    assert code == 0

    project_dir = Path(isolated_dir) / "product_samples" / "slides" / "test_dt_fb"
    draft = (project_dir / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert 'data-title="Lamina 1"' in draft
