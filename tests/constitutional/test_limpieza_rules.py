# -*- coding: utf-8 -*-
"""Pruebas constitucionales de la limpieza (SC-801/802, principio de escritura via motor)."""
import json

import pra_helper
import pra_orchestrator as po


COBERTURA_OK = "pra_helper.py  320  38  91%\n30 passed in 0.42s\n"


def test_cleanup_preserva_lote_y_fuente_por_sesion_corrida(
        run_orchestrator, isolated_dir, monkeypatch):
    """SC-801/802: tras una corrida completa, el lote queda intacto y la fuente respaldada."""
    doc = isolated_dir / "documento_fuente.md"
    doc.write_text("# Introducción a Docker\nContenido.", encoding="utf-8")
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (0, COBERTURA_OK))

    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")

    assert codigo == 0
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    for protegido in ("manifest.blade.php", "presentation_plan.json",
                      "class_registry.json", "js_registry.json"):
        assert (proyecto / protegido).exists()
    assert (proyecto / "session1").is_dir()
    assert (proyecto / "session2").is_dir()
    assert (proyecto / "assets").is_dir()
    # Fuente re-consolidable respaldada
    assert (proyecto / "backup/fuente/sesion1").is_dir()
    assert (proyecto / "backup/fuente/sesion2").is_dir()
    assert (proyecto / "backup/fuente/manifest_draft.blade.php").exists()
    # Residuales eliminados
    for residuo in ("sesion1", "sesion2", "manifest_draft.blade.php", "styles.blade.php",
                    "scripts.blade.php", "styles_additions", "scripts_additions",
                    "manifest_additions", "outputs.zip"):
        assert not (proyecto / residuo).exists(), f"Residuo presente: {residuo}"
