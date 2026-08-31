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


def test_cli_consolidate_interpolacion_valida(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    """consolidate debe generar interpolacion Blade valida {$presentation->folder_name} (P1)."""
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    for rel in ["manifest.blade.php", "assets/styles.blade.php", "assets/scripts.blade.php"]:
        content = (project_dir / rel).read_text(encoding="utf-8")
        assert "{$presentation->folder_name}" in content, rel
        assert "{{$presentation->folder_name}}" not in content, rel
        assert "{{{$presentation->folder_name}}}" not in content, rel


def test_cli_consolidate_envuelve_assets_y_es_idempotente(run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir):
    """consolidate debe envolver CSS/JS en <style>/<script> y ser idempotente (P2, P3)."""
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", sample_llm_response_s1)[0] == 0
    assert run_cli("consolidate")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    css_file = project_dir / "assets/styles_blade/css/sesion1_styles.blade.php"
    js_file = project_dir / "assets/styles_blade/js/sesion1_scripts.blade.php"
    assert css_file.exists()
    assert js_file.exists()

    css = css_file.read_text(encoding="utf-8")
    js = js_file.read_text(encoding="utf-8")
    assert css.startswith("<style>") and css.endswith("</style>")
    assert js.startswith("<script>") and js.endswith("</script>")

    # idempotencia
    assert run_cli("consolidate")[0] == 0
    css2 = css_file.read_text(encoding="utf-8")
    js2 = js_file.read_text(encoding="utf-8")
    assert css2.count("<style>") == 1 and css2.count("</style>") == 1
    assert js2.count("<script>") == 1 and js2.count("</script>") == 1


def test_cli_process_session_respuesta_file(run_cli, initialized_project, sample_llm_response_s1, isolated_dir):
    """process-session debe leer la respuesta desde --respuesta-file (P4)."""
    resp_file = isolated_dir / "respuesta.txt"
    resp_file.write_text(sample_llm_response_s1, encoding="utf-8")
    code, out = run_cli("process-session", "1", "--respuesta-file", str(resp_file))
    assert code == 0
    assert json.loads(out)["laminas_escritas"] == 2

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    assert (project_dir / "sesion1/que-es-docker.blade.php").exists()


def test_cli_process_session_respuesta_file_inexistente(run_cli, initialized_project, isolated_dir):
    """process-session con --respuesta-file inexistente debe fallar con codigo 1."""
    code, out = run_cli("process-session", "1", "--respuesta-file", "no_existe.txt")
    assert code == 1
    payload = json.loads(out)
    assert "RESPUESTA_FILE_NOT_FOUND" in payload.get("codigo", "")


def test_cli_process_session_respuesta_ausente(run_cli, initialized_project):
    """process-session sin respuesta ni --respuesta-file debe fallar con codigo 1."""
    code, out = run_cli("process-session", "1")
    assert code == 1
    payload = json.loads(out)
    assert "vacia" in payload["error"]


def test_cli_process_session_respuesta_larga_por_archivo(run_cli, initialized_project, isolated_dir):
    """process-session con respuesta > 33000 chars via archivo debe procesarse (P4 / WinError 206)."""
    lamina = "{{- sesion1/que-es-docker.blade.php -}}\n<div class='x'>todos</div>\n"
    # ~ 800 laminas * ~44 chars = > 33000
    grande = "**BLOQUE 1**\n" + (lamina * 800)
    grande += (
        "\n**BLOQUE 5**\n```json\n"
        '{"nuevas_clases": [], "clases_materializadas": [], '
        '"nuevos_comportamientos": [], "comportamientos_materializados": []}\n```\n'
    )
    assert len(grande) > 33000, len(grande)

    resp_file = isolated_dir / "respuesta_larga.txt"
    resp_file.write_text(grande, encoding="utf-8")
    code, out = run_cli("process-session", "1", "--respuesta-file", str(resp_file))
    assert code == 0
    assert json.loads(out)["laminas_escritas"] >= 1


def test_cli_activo_por_pra_active_project(run_cli, sample_plan_json_str, isolated_dir, monkeypatch):
    """PRA_ACTIVE_PROJECT debe priorizar el proyecto indicado sobre el primero alfabetico (P5)."""
    # Crea dos proyectos via save-plan (cada uno genera sus registros)
    for proy, titulo in [("proyecto_a", "Proyecto AAAA"), ("proyecto_b", "Proyecto BBBB")]:
        plan = json.loads(sample_plan_json_str)
        plan["carpeta_snake_case"] = proy
        plan["sesiones"][0]["titulo"] = titulo
        code, _ = run_cli("save-plan", json.dumps(plan, ensure_ascii=False))
        assert code == 0

    # Sin la variable elegiria proyecto_a (primero alfabetico); con la variable elige proyecto_b
    monkeypatch.delenv("PRA_ACTIVE_PROJECT", raising=False)
    monkeypatch.setenv("PRA_ACTIVE_PROJECT", "proyecto_b")
    code, out = run_cli("prompt-session", "1")
    assert code == 0
    assert "Proyecto BBBB" in out
