# -*- coding: utf-8 -*-
import json
import pytest
import pra_helper
from pra_helper import load_json


@pytest.fixture
def initialized_project(run_cli, sample_plan_json_str):
    """Fixture que inicializa un proyecto valido ejecutando save-plan."""
    code, _ = run_cli("save-plan", sample_plan_json_str)
    assert code == 0, out


def test_cli_prompt_session_success(run_cli, initialized_project):
    """prompt-session 1 debe imprimir el prompt compilado con contexto de la sesion."""
    code, out = run_cli("prompt-session", "1")

    assert code == 0
    assert "Conceptos Básicos" in out
    assert "que-es-docker" in out


def test_cli_prompt_session_sequentiality_blocked(run_cli, initialized_project):
    """prompt-session 2 sin completar la sesion 1 debe abortar con codigo 2."""
    code, out = run_cli("prompt-session", "2")

    assert code == 2
    payload = json.loads(out)
    assert "no completada" in payload["error"]


def test_cli_prompt_session_not_found(run_cli, initialized_project):
    """prompt-session con numero inexistente en el plan debe fallar con codigo 1."""
    code, out = run_cli("prompt-session", "99")

    assert code == 1
    payload = json.loads(out)
    assert "no encontrada" in payload["error"]


def test_cli_process_session_success(run_cli, initialized_project, sample_llm_response_s1, isolated_dir):
    """process-session 1 debe escribir laminas, acumular CSS/JS y actualizar registros."""
    code, out = run_cli("process-session", "1", sample_llm_response_s1)

    assert code == 0
    payload = json.loads(out)
    assert payload["status"] == "exito"
    assert payload["laminas_escritas"] == 2
    assert payload["violaciones_css_inline"] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"

    # Laminas Blade escritas
    lamina_1 = project_dir / "sesion1" / "que-es-docker.blade.php"
    lamina_2 = project_dir / "sesion1" / "arquitectura.blade.php"
    assert lamina_1.exists()
    assert "<h1>¿Qué es Docker?</h1>" in lamina_1.read_text(encoding="utf-8")
    assert lamina_2.exists()

    # Estilos y scripts acumulados
    styles = (project_dir / "styles.blade.php").read_text(encoding="utf-8")
    scripts = (project_dir / "scripts.blade.php").read_text(encoding="utf-8")
    assert ".docker-blue" in styles
    assert "Docker slide loaded" in scripts

    # Respaldos aislados por sesion
    assert (project_dir / "styles_additions" / "sesion1_styles.css").exists()
    assert (project_dir / "scripts_additions" / "sesion1_scripts.js").exists()

    # Registros actualizados sin duplicados
    class_registry = load_json(project_dir / "class_registry.json")
    js_registry = load_json(project_dir / "js_registry.json")
    nombres_clases = [c["nombre"] for c in class_registry["clases"]]
    assert len(nombres_clases) == len(set(nombres_clases))
    docker_blue = next(c for c in class_registry["clases"] if c["nombre"] == "docker-blue")
    assert docker_blue["implementada"] is True
    ripple = next(j for j in js_registry["comportamientos"] if j["nombre"] == "ripple-effect")
    assert ripple["implementada"] is True

    # Manifest de adiciones y borrador actualizado
    manifest_addition = (project_dir / "manifest_additions" / "sesion1.blade.php").read_text(encoding="utf-8")
    assert '<x-slide view="sesion1.que-es-docker"' in manifest_addition
    manifest_draft = (project_dir / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert "Sesion 1 completada" in manifest_draft


def test_cli_process_session_sequentiality_blocked(run_cli, initialized_project, sample_llm_response_s1):
    """process-session 2 sin completar la sesion 1 debe abortar con codigo 2."""
    code, out = run_cli("process-session", "2", sample_llm_response_s1)

    assert code == 2
    payload = json.loads(out)
    assert "no completada" in payload["error"]


def test_cli_consolidate_creates_final_structure(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    """consolidate debe materializar la estructura final Laravel sin duplicados."""
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0

    code, out = run_cli("consolidate")

    assert code == 0
    payload = json.loads(out)
    assert payload["ok"] is True
    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    manifest = project_dir / "manifest.blade.php"
    styles = project_dir / "assets" / "styles.blade.php"
    scripts = project_dir / "assets" / "scripts.blade.php"
    assert manifest.exists()
    assert styles.exists()
    assert scripts.exists()
    manifest_content = manifest.read_text(encoding="utf-8")
    assert "@extends('layouts.reveal')" in manifest_content
    assert "session1.que-es-docker" in manifest_content
    assert "sesion1." not in manifest_content
    assert (project_dir / "session1" / "que-es-docker.blade.php").exists()
    assert (project_dir / "assets" / "styles_blade" / "css" / "sesion1_styles.blade.php").exists()
    assert (project_dir / "assets" / "styles_blade" / "js" / "sesion1_scripts.blade.php").exists()

    code, second_out = run_cli("consolidate")
    assert code == 0
    assert json.loads(second_out)["laminas_materializadas"] == 2
