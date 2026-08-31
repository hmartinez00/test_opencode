# -*- coding: utf-8 -*-
"""Pruebas de integracion del comando limpiar de pra_helper.py (T824/B1-B2)."""
import json

import pra_helper


def _proyecto(isolated_dir):
    return isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"


def test_cli_limpiar_sin_proyecto(run_cli, isolated_dir):
    code, out = run_cli("limpiar")
    assert code == 1
    assert json.loads(out)["ok"] is False


def test_cli_limpiar_deja_solo_lote_y_backup(
        run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0

    code, out = run_cli("limpiar")

    assert code == 0
    payload = json.loads(out)
    assert payload["ok"] is True
    proyecto = _proyecto(isolated_dir)
    # Lote protegido presente
    assert (proyecto / "manifest.blade.php").exists()
    assert (proyecto / "session1").is_dir()
    assert (proyecto / "session1" / "que-es-docker.blade.php").exists()
    assert (proyecto / "assets").is_dir()
    # Residuo eliminado
    assert not (proyecto / "outputs.zip").exists()
    assert not (proyecto / "sesion1").exists()
    assert not (proyecto / "manifest_draft.blade.php").exists()
    # Respaldo presente
    assert (proyecto / "backup/fuente/sesion1").is_dir()


def test_cli_limpiar_lote_incompleto_exit_code_2(
        run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0
    (isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker" / "manifest.blade.php").unlink()

    code, out = run_cli("limpiar")

    assert code == 2
    assert json.loads(out)["ok"] is False
