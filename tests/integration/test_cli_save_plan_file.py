# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pra_helper
from pra_helper import load_json


def test_save_plan_file_json_valido(run_cli, isolated_dir, tmp_path):
    """A6: --plan-file con JSON valido debe guardar el plan correctamente."""
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps({
        "titulo": "Test File Plan",
        "carpeta_snake_case": "test_file_plan",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": []}
            ]
        }]
    }), encoding="utf-8")
    code, out = run_cli("save-plan", "--plan-file", str(plan_file))
    assert code == 0

    project_dir = Path(isolated_dir) / "product_samples" / "slides" / "test_file_plan"
    assert (project_dir / "presentation_plan.json").exists()


def test_save_plan_file_inexistente(run_cli, isolated_dir):
    """A6: --plan-file con archivo inexistente debe retornar error."""
    code, out = run_cli("save-plan", "--plan-file", "/no/existe/plan.json")
    assert code == 1
    assert "PLAN_FILE_NOT_FOUND" in out


def test_save_plan_file_vs_argv_identico(run_cli, isolated_dir, tmp_path):
    """A6: El resultado debe ser identico via --plan-file o argv."""
    plan_dict = {
        "titulo": "Test Equiv",
        "carpeta_snake_case": "test_equiv_plan",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {"orden": 1, "id_kebab_case": "lamina-1", "tipo": "contenido", "objetivo": "o", "insumos": []}
            ]
        }]
    }

    # Via argv
    code1, _ = run_cli("save-plan", json.dumps(plan_dict))
    assert code1 == 0
    plan_argv = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_equiv_plan" / "presentation_plan.json")

    # Limpiar y via archivo
    import shutil
    shutil.rmtree(Path(isolated_dir) / "product_samples" / "slides" / "test_equiv_plan")

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan_dict), encoding="utf-8")
    code2, _ = run_cli("save-plan", "--plan-file", str(plan_file))
    assert code2 == 0
    plan_file_result = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_equiv_plan" / "presentation_plan.json")

    assert plan_argv == plan_file_result


def test_save_plan_file_con_acentos(run_cli, isolated_dir, tmp_path):
    """A6: JSON con acentos via --plan-file debe preservar contenido."""
    plan_file = tmp_path / "plan_acentos.json"
    plan_file.write_text(json.dumps({
        "titulo": "Presentacion con acentos: informacion y comunicacion",
        "carpeta_snake_case": "test_acentos_plan",
        "idioma": "es",
        "resumen_general": "Contenido con acentos: aeiou",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion de introduccion",
            "objetivo_pedagogico": "Comprender la importancia de la informacion",
            "laminas": [
                {"orden": 1, "id_kebab_case": "intro", "tipo": "portada", "objetivo": "Presentar", "insumos": []}
            ]
        }]
    }, ensure_ascii=False), encoding="utf-8")
    code, out = run_cli("save-plan", "--plan-file", str(plan_file))
    assert code == 0

    plan = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_acentos_plan" / "presentation_plan.json")
    assert "acentos" in plan["titulo"]


def test_save_plan_sin_argumentos_falla(run_cli):
    """A6: save-plan sin argumentos no debe funcionar."""
    code, out = run_cli("save-plan")
    assert code != 0
