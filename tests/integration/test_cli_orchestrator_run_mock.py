# -*- coding: utf-8 -*-
"""Pruebas de integracion del comando run del orquestador con backend mock (T316)."""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

import pra_orchestrator as po


COBERTURA_OK = (
    "----------- coverage -----------\n"
    "Name            Stmts Miss Cover\n"
    "pra_helper.py     320   38   91%\n"
    "TOTAL             320   38   91%\n"
    "30 passed in 0.42s\n"
)


@pytest.fixture
def entorno_e2e(isolated_dir, monkeypatch):
    """Documento fuente + fase pytest simulada para corridas E2E rapidas."""
    doc = isolated_dir / "documento_fuente.md"
    doc.write_text("# Introducción a Docker\nContenido de Docker aquí.", encoding="utf-8")
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (0, COBERTURA_OK))
    return doc


def arbol_hashes(raiz):
    """Hash SHA-256 de cada archivo del arbol, indexado por ruta relativa."""
    resultado = {}
    for p in sorted(Path(raiz).rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(raiz)).replace("\\", "/")
            resultado[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return resultado


def test_run_mock_flujo_completo_exitoso(run_orchestrator, entorno_e2e, isolated_dir):
    codigo, salida = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")

    assert codigo == 0
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    # Lote protegido generado y conservado por pra_helper.py
    assert (proyecto / "presentation_plan.json").exists()
    assert (proyecto / "class_registry.json").exists()
    assert (proyecto / "js_registry.json").exists()
    assert (proyecto / "manifest.blade.php").exists()
    for lamina in (
        proyecto / "session1" / "que-es-docker.blade.php",
        proyecto / "session1" / "arquitectura.blade.php",
        proyecto / "session2" / "comandos-basicos.blade.php",
    ):
        assert lamina.exists(), f"Falta {lamina}"
    assert (proyecto / "assets").is_dir()
    # Iteracion 008: sin outputs.zip (fase zip omitida) ni artefactos residuales
    assert not (proyecto / "outputs.zip").exists()
    assert not (proyecto / "sesion1").exists()
    assert not (proyecto / "sesion2").exists()
    assert not (proyecto / "manifest_draft.blade.php").exists()
    assert not (proyecto / "styles.blade.php").exists()
    assert not (proyecto / "scripts.blade.php").exists()
    # Respaldo de la fuente re-consolidable
    assert (proyecto / "backup/fuente/sesion1").is_dir()
    assert (proyecto / "backup/fuente/sesion2").is_dir()
    assert (proyecto / "backup/fuente/manifest_draft.blade.php").exists()
    # Estado final completamente completado, con cleanup y sin zip
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    for fase in ("init", "save_plan", "pytest", "cleanup"):
        assert estado["fases"][fase]["estado"] == "completada", f"Fase {fase} no completada"
    assert "zip" not in estado["fases"]
    assert all(s["estado"] == "completada" for s in estado["fases"]["sesiones"])
    assert (isolated_dir / po.LOG_FILE).exists()


def test_run_mock_determinismo_entre_corridas(run_orchestrator, entorno_e2e, isolated_dir):
    dir_a = isolated_dir / "corrida_a"
    dir_b = isolated_dir / "corrida_b"
    hashes = []
    for destino in (dir_a, dir_b):
        destino.mkdir()
        (destino / "documento_fuente.md").write_text(
            "# Introducción a Docker\nContenido.", encoding="utf-8"
        )
        import os
        cwd_previo = os.getcwd()
        os.chdir(destino)
        try:
            codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")
            assert codigo == 0
            hashes.append(arbol_hashes(destino / po.OUTPUT_BASE_DIR / "intro_docker"))
            # Iteracion 008: el respaldo y el lote deben ser identicos entre corridas
            assert (destino / po.OUTPUT_BASE_DIR / "intro_docker" / "manifest.blade.php").exists()
            assert not (destino / po.OUTPUT_BASE_DIR / "intro_docker" / "outputs.zip").exists()
        finally:
            os.chdir(cwd_previo)

    assert hashes[0] == hashes[1], "Las corridas mock deben ser byte a byte identicas"


def test_run_backend_invalido_es_error_de_uso(run_orchestrator, entorno_e2e):
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "chatgpt")
    assert codigo == 4


def test_run_documento_inexistente_es_error_de_uso(run_orchestrator, entorno_e2e):
    codigo, _ = run_orchestrator("run", "no_existe.md")
    assert codigo == 4


def test_run_max_retries_cero_es_error_de_uso(run_orchestrator, entorno_e2e):
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--max-retries", "0")
    assert codigo == 4
