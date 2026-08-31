# -*- coding: utf-8 -*-
"""Pruebas unitarias de la limpieza de artefactos residuales (FR-801 a FR-810)."""
import json
from pathlib import Path

import pra_helper


def _build_minimal_project(root):
    """Construye un proyecto minimo con lote + residuos en `root` (raiz entregable)."""
    proyecto = root
    proyecto.mkdir(parents=True)
    (proyecto / "manifest.blade.php").write_text("{{-- manifest --}}", encoding="utf-8")
    (proyecto / "presentation_plan.json").write_text(
        json.dumps({"titulo": "T", "sesiones": [{"numero": 1, "titulo": "S1", "laminas": []}]}),
        encoding="utf-8",
    )
    (proyecto / "class_registry.json").write_text("{}", encoding="utf-8")
    (proyecto / "js_registry.json").write_text("{}", encoding="utf-8")
    (proyecto / "session1").mkdir(parents=True)
    (proyecto / "session1" / "que-es-docker.blade.php").write_text("<div>lote</div>", encoding="utf-8")
    (proyecto / "assets").mkdir(parents=True)
    (proyecto / "assets" / "styles.blade.php").write_text("", encoding="utf-8")
    (proyecto / "assets" / "scripts.blade.php").write_text("", encoding="utf-8")
    (proyecto / "sesion1").mkdir(parents=True)
    (proyecto / "sesion1" / "que-es-docker.blade.php").write_text("<div>fuente</div>", encoding="utf-8")
    (proyecto / "styles_additions").mkdir()
    (proyecto / "styles_additions" / "sesion1_styles.css").write_text(".x{}", encoding="utf-8")
    (proyecto / "scripts_additions").mkdir()
    (proyecto / "scripts_additions" / "sesion1_scripts.js").write_text("// js", encoding="utf-8")
    (proyecto / "manifest_additions").mkdir()
    (proyecto / "styles.blade.php").write_text("", encoding="utf-8")
    (proyecto / "scripts.blade.php").write_text("", encoding="utf-8")
    (proyecto / "manifest_draft.blade.php").write_text("", encoding="utf-8")
    (proyecto / "outputs.zip").write_bytes(b"PK")
    return proyecto


def construir_proyecto_con_residuos(isolated_dir):
    """Construye un proyecto con el lote protegido completo mas artefactos residuales."""
    proyecto = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    proyecto.mkdir(parents=True)
    # Lote protegido
    (proyecto / "manifest.blade.php").write_text("{{-- manifest --}}", encoding="utf-8")
    (proyecto / "presentation_plan.json").write_text(
        json.dumps({"titulo": "T", "sesiones": [{"numero": 1, "titulo": "S1", "laminas": []}]}),
        encoding="utf-8",
    )
    (proyecto / "class_registry.json").write_text("{}", encoding="utf-8")
    (proyecto / "js_registry.json").write_text("{}", encoding="utf-8")
    # session1 (destino final) con lamina
    (proyecto / "session1").mkdir(parents=True)
    (proyecto / "session1" / "que-es-docker.blade.php").write_text(
        "<div>lote</div>", encoding="utf-8"
    )
    # assets (entry point)
    (proyecto / "assets").mkdir(parents=True)
    (proyecto / "assets" / "styles.blade.php").write_text("", encoding="utf-8")
    (proyecto / "assets" / "scripts.blade.php").write_text("", encoding="utf-8")

    # Artefactos residuales
    (proyecto / "sesion1").mkdir(parents=True)
    (proyecto / "sesion1" / "que-es-docker.blade.php").write_text(
        "<div>fuente</div>", encoding="utf-8"
    )
    (proyecto / "styles_additions").mkdir()
    (proyecto / "styles_additions" / "sesion1_styles.css").write_text(".x{}", encoding="utf-8")
    (proyecto / "scripts_additions").mkdir()
    (proyecto / "scripts_additions" / "sesion1_scripts.js").write_text("// js", encoding="utf-8")
    (proyecto / "manifest_additions").mkdir()
    (proyecto / "styles.blade.php").write_text("", encoding="utf-8")
    (proyecto / "scripts.blade.php").write_text("", encoding="utf-8")
    (proyecto / "manifest_draft.blade.php").write_text("", encoding="utf-8")
    (proyecto / "outputs.zip").write_bytes(b"PK")
    return proyecto


def test_limpieza_preserva_lote_protegido(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    reporte = pra_helper._limpiar_proyecto(proyecto)
    assert reporte["ok"] is True
    for protegido in ("manifest.blade.php", "presentation_plan.json",
                      "class_registry.json", "js_registry.json"):
        assert (proyecto / protegido).exists(), f"Falta lote: {protegido}"
    assert (proyecto / "session1" / "que-es-docker.blade.php").exists()
    assert (proyecto / "assets" / "styles.blade.php").exists()


def test_limpieza_respalda_fuente(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    pra_helper._limpiar_proyecto(proyecto)
    assert (proyecto / "backup/fuente/sesion1/que-es-docker.blade.php").exists()
    assert (proyecto / "backup/fuente/styles_additions/sesion1_styles.css").exists()
    assert (proyecto / "backup/fuente/scripts_additions/sesion1_scripts.js").exists()
    assert (proyecto / "backup/fuente/manifest_draft.blade.php").exists()


def test_limpieza_elimina_residuos(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    pra_helper._limpiar_proyecto(proyecto)
    for residuo in ("sesion1", "manifest_draft.blade.php", "manifest_additions",
                    "styles.blade.php", "scripts.blade.php", "styles_additions",
                    "scripts_additions", "outputs.zip"):
        assert not (proyecto / residuo).exists(), f"Residuo no eliminado: {residuo}"


def test_limpieza_aborta_sin_borrar_si_falta_lote(isolated_dir):
    proyecto = construir_proyecto_con_residuos(isolated_dir)
    (proyecto / "manifest.blade.php").unlink()
    antes = {p.name: p.exists() for p in proyecto.iterdir()}
    reporte = pra_helper._limpiar_proyecto(proyecto)
    assert reporte["ok"] is False
    for nombre, existe in antes.items():
        assert (proyecto / nombre).exists() == existe, f"Se borro algo: {nombre}"


def test_limpieza_idempotente_y_determinista(isolated_dir):
    a = isolated_dir / "proyecto_a"
    b = isolated_dir / "proyecto_b"

    def backup_bytes(p):
        return {str(x.relative_to(p)): x.read_bytes()
                for x in (p / "backup").rglob("*") if x.is_file()}

    pa = _build_minimal_project(a)
    pb = _build_minimal_project(b)

    pra_helper._limpiar_proyecto(pa)
    pra_helper._limpiar_proyecto(pb)

    assert backup_bytes(pa) == backup_bytes(pb)
    assert (pa / "backup/fuente/sesion1/que-es-docker.blade.php").exists()


def test_limpieza_segunda_limpieza_es_noop(isolated_dir):
    proyecto = _build_minimal_project(isolated_dir / "proyecto_a")
    pra_helper._limpiar_proyecto(proyecto)

    def elim():
        return sorted(str(x.relative_to(proyecto)).replace("\\", "/")
                      for x in proyecto.rglob("*") if x.is_file())

    antes = elim()
    reporte = pra_helper._limpiar_proyecto(proyecto)
    assert reporte["ok"] is True
    assert elim() == antes
    assert (proyecto / "backup/fuente/sesion1/que-es-docker.blade.php").exists()
