# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path

import pra_helper
import pra_orchestrator as po


def test_analizar_coherencia_detecta_huerfanas(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "sesion1").mkdir()
    (project_dir / "sesion1" / "intro.blade.php").write_text("<section></section>", encoding="utf-8")
    (project_dir / "sesion1" / "extra.blade.php").write_text("<section></section>", encoding="utf-8")

    plan = {
        "sesiones": [
            {"numero": 1, "laminas": [{"id_kebab_case": "intro"}]}
        ]
    }

    report = pra_helper._analizar_coherencia(plan, project_dir)

    assert any(item["id"] == "extra" for item in report["huerfanas"])


def test_validar_calidad_plan_advierte_registros_vacios():
    plan = {
        "sesiones": [
            {
                "numero": 1,
                "laminas": [{"id_kebab_case": "intro", "insumos": []}],
            }
        ]
    }

    warnings = pra_helper._validar_calidad_plan(plan, {"clases": [], "comportamientos": []})

    assert warnings


def test_resolver_binario_opencode_usa_rutas_conocidas(monkeypatch, tmp_path):
    fake_home = tmp_path / "fake_home"
    fake_bin = fake_home / ".opencode" / "bin"
    fake_bin.mkdir(parents=True)
    target = fake_bin / ("opencode.exe" if os.name == "nt" else "opencode")
    target.write_text("stub", encoding="utf-8")

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.setattr(po.shutil, "which", lambda name: None)
    monkeypatch.setenv("PATH", "")

    resolved = po._resolver_binario_opencode()

    assert resolved is not None
    assert target.name in resolved
