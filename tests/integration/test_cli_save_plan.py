# -*- coding: utf-8 -*-
import json
from pra_helper import load_json


def test_cli_save_plan_success(run_cli, sample_plan_json_str, isolated_dir):
    """save-plan debe crear plan, registros, manifest, carpetas de sesion y acumuladores."""
    code, out = run_cli("save-plan", sample_plan_json_str)

    assert code == 0
    payload = json.loads(out)
    assert payload["status"] == "exito"
    assert payload["sesiones_inicializadas"] == 2

    project_dir = isolated_dir / "intro_docker"

    # Plan maestro normalizado
    plan = load_json(project_dir / "presentation_plan.json")
    assert plan["titulo"] == "Introducción a Docker"
    assert plan["carpeta_snake_case"] == "intro_docker"
    assert len(plan["sesiones"]) == 2

    # Registros inicializados con entradas del plan en False
    class_registry = load_json(project_dir / "class_registry.json")
    js_registry = load_json(project_dir / "js_registry.json")
    assert {c["nombre"] for c in class_registry["clases"]} == {"text-center", "docker-blue"}
    assert all(c["implementada"] is False for c in class_registry["clases"])
    assert {j["nombre"] for j in js_registry["comportamientos"]} == {"ripple-effect"}
    assert all(j["implementada"] is False for j in js_registry["comportamientos"])

    # Manifest borrador con entradas <x-slide> pendientes
    manifest = (project_dir / "manifest_draft.blade.php").read_text(encoding="utf-8")
    assert '<x-slide view="sesion1.que-es-docker"' in manifest
    assert '<x-slide view="sesion2.comandos-basicos"' in manifest

    # Carpetas por sesion y carpetas de adiciones
    for folder in ["sesion1", "sesion2", "styles_additions", "scripts_additions", "manifest_additions"]:
        assert (project_dir / folder).is_dir()

    # Acumuladores inicializados
    assert (project_dir / "styles.blade.php").exists()
    assert (project_dir / "scripts.blade.php").exists()


def test_cli_save_plan_malformed_json(run_cli, isolated_dir):
    """save-plan con JSON malformado debe salir con codigo 1 sin crear carpetas."""
    code, out = run_cli("save-plan", "{json_invalido::")

    assert code == 1
    payload = json.loads(out)
    assert "Error de parseo JSON" in payload["error"]
    assert list(isolated_dir.iterdir()) == []


def test_cli_save_plan_schema_errors(run_cli, isolated_dir):
    """save-plan con esquema invalido debe salir con codigo 2 y listar errores."""
    bad_plan = json.dumps({"titulo": "", "idioma": "es"})
    code, out = run_cli("save-plan", bad_plan)

    assert code == 2
    payload = json.loads(out)
    assert payload["error"] == "Errores de validacion"
    assert any("carpeta_snake_case" in d for d in payload["detalles"])
    assert list(isolated_dir.iterdir()) == []
