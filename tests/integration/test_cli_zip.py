# -*- coding: utf-8 -*-
import json
import zipfile


def test_cli_zip_without_project(run_cli):
    """zip sin proyecto activo debe fallar con codigo 1."""
    code, out = run_cli("zip")

    assert code == 1
    payload = json.loads(out)
    assert "error" in payload


def test_cli_zip_without_completed_sessions(run_cli, sample_plan_json_str, isolated_dir):
    """zip con plan guardado pero sin sesiones construidas debe fallar con codigo 1."""
    assert run_cli("save-plan", sample_plan_json_str)[0] == 0

    code, out = run_cli("zip")

    assert code == 1
    payload = json.loads(out)
    assert "No hay sesiones completadas" in payload["error"]


def test_cli_zip_success(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    """zip tras completar la sesion 1 debe generar outputs.zip con toda la estructura."""
    assert run_cli("save-plan", sample_plan_json_str)[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0

    code, out = run_cli("zip")

    assert code == 0
    payload = json.loads(out)
    assert payload["status"] == "exito"

    zip_path = isolated_dir / "outputs.zip"
    assert zip_path.exists()
    assert payload["tamano_bytes"] > 0

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "intro_docker/presentation_plan.json" in names
    assert "intro_docker/class_registry.json" in names
    assert "intro_docker/js_registry.json" in names
    assert "intro_docker/manifest_draft.blade.php" in names
    assert "intro_docker/styles.blade.php" in names
    assert "intro_docker/scripts.blade.php" in names
    assert "intro_docker/sesion1/que-es-docker.blade.php" in names
