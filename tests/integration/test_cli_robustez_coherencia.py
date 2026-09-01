# -*- coding: utf-8 -*-
import json

import pra_helper


def test_cli_save_plan_advierta_plan_incompleto(run_cli):
    plan = {
        "titulo": "Demo",
        "carpeta_snake_case": "demo",
        "idioma": "es",
        "resumen_general": "demo",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "Sesion 1",
                "objetivo_pedagogico": "Objetivo",
                "laminas": [
                    {"orden": 1, "id_kebab_case": "intro", "insumos": []}
                ],
            }
        ],
    }

    code, out = run_cli("save-plan", json.dumps(plan, ensure_ascii=False))

    assert code == 0
    payload = json.loads(out)
    assert "advertencias" in payload
    assert payload["advertencias"]


def test_cli_consolidate_aborta_por_incoherencia(run_cli, isolated_dir):
    plan = {
        "titulo": "Demo",
        "carpeta_snake_case": "demo",
        "idioma": "es",
        "resumen_general": "demo",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "Sesion 1",
                "objetivo_pedagogico": "Objetivo",
                "laminas": [{"orden": 1, "id_kebab_case": "intro"}],
            }
        ],
    }

    project_dir = pra_helper.OUTPUT_BASE_DIR / "demo"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "presentation_plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    (project_dir / "sesion1").mkdir(exist_ok=True)
    (project_dir / "sesion1" / "intro.blade.php").write_text("<section></section>", encoding="utf-8")
    (project_dir / "sesion1" / "extra.blade.php").write_text("<section></section>", encoding="utf-8")

    code, out = run_cli("consolidate")

    assert code != 0
    payload = json.loads(out)
    assert payload["ok"] is False
    assert "coherencia" in payload
