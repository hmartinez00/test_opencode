# -*- coding: utf-8 -*-
"""Pruebas constitucionales: violaciones intencionales de las reglas no negociables del PRA."""
import json
import pytest

import pra_helper


@pytest.fixture
def initialized_project(run_cli, sample_plan_json_str):
    """Fixture que inicializa un proyecto valido ejecutando save-plan."""
    code, _ = run_cli("save-plan", sample_plan_json_str)
    assert code == 0


def test_constitucion_I_cero_css_inline_rechazado(run_cli, initialized_project, sample_invalid_llm_response_inline_css, isolated_dir):
    """Regla I: una respuesta LLM con style=\"...\" debe abortar con codigo 2 y no escribir la lamina contaminada."""
    code, out = run_cli("process-session", "1", sample_invalid_llm_response_inline_css)

    assert code == 2
    payload = json.loads(out)
    assert "Cero CSS Inline" in payload["error"]
    assert len(payload["violaciones"]) >= 1

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    laminas = list((project_dir / "sesion1").glob("*.blade.php"))
    assert laminas == []

    # Los registros no deben marcarse como materializados tras el aborto
    class_registry = json.loads((project_dir / "class_registry.json").read_text(encoding="utf-8"))
    assert all(c["implementada"] is False for c in class_registry["clases"])


def test_constitucion_IV_secuencialidad_sesiones(run_cli, initialized_project, sample_llm_response_s1):
    """Regla IV: no se puede construir la Sesion 2 sin haber completado la Sesion 1."""
    code_prompt, out_prompt = run_cli("prompt-session", "2")
    assert code_prompt == 2
    assert "no completada" in json.loads(out_prompt)["error"]

    code_process, out_process = run_cli("process-session", "2", sample_llm_response_s1)
    assert code_process == 2
    assert "no completada" in json.loads(out_process)["error"]


def test_constitucion_III_estado_determinista_json_malformado(run_cli, isolated_dir):
    """Regla III: JSON malformado en save-plan no debe dejar estructura corrupta ni parcial."""
    code, out = run_cli("save-plan", "{plan_roto")

    assert code == 1
    assert "Error de parseo JSON" in json.loads(out)["error"]
    assert list(isolated_dir.iterdir()) == []


def test_respuesta_llm_sin_laminas_aborta(run_cli, initialized_project):
    """Caso extremo: respuesta LLM sin bloques de laminas debe abortar sin escribir archivos."""
    code, out = run_cli("process-session", "1", "Respuesta sin delimitadores validos")

    assert code == 1
    assert "No se pudieron parsear laminas" in json.loads(out)["error"]


def test_laminas_validas_no_contienen_css_inline(run_cli, initialized_project, sample_llm_response_s1, isolated_dir):
    """Regla I (positiva): las laminas generadas por el flujo normal no contienen style=."""
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    for blade in (project_dir / "sesion1").glob("*.blade.php"):
        assert 'style="' not in blade.read_text(encoding="utf-8")
