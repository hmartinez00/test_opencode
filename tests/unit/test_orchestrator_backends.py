# -*- coding: utf-8 -*-
"""Pruebas unitarias de los backends LLM intercambiables (T304-T306)."""
import subprocess
from unittest import mock

import pytest

import pra_orchestrator as po


# ============================================================
# MockBackend - T305
# ============================================================

def test_mock_backend_sirve_fixture_por_clave(isolated_dir):
    fixtures = isolated_dir / "fixtures"
    fixtures.mkdir()
    (fixtures / "plan.txt").write_text("RESPUESTA PLAN", encoding="utf-8")
    backend = po.MockBackend(fixtures_dir=fixtures)
    assert backend.generar("cualquier prompt", clave="plan") == "RESPUESTA PLAN"


def test_mock_backend_fixture_inexistente_lanza_backenderror():
    backend = po.MockBackend(fixtures_dir="/ruta/inexistente")
    with pytest.raises(po.BackendError, match="Fixture mock no encontrada"):
        backend.generar("prompt", clave="sesion99")


def test_mock_backend_secuencia_respeta_orden():
    backend = po.MockBackend(secuencia=["primera", "segunda"])
    assert backend.generar("p1", clave="x") == "primera"
    assert backend.generar("p2", clave="y") == "segunda"


def test_mock_backend_secuencia_agotada_lanza_backenderror():
    backend = po.MockBackend(secuencia=["unica"])
    backend.generar("p", clave="x")
    with pytest.raises(po.BackendError, match="agotada"):
        backend.generar("p", clave="y")


# ============================================================
# OpenCodeBackend - T306
# ============================================================

class _ProcesoFalso:
    def __init__(self, returncode=0, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_opencode_backend_exitoso(monkeypatch):
    llamado = {}

    def fake_run(cmd, **kwargs):
        llamado["cmd"] = cmd
        return _ProcesoFalso(returncode=0, stdout="respuesta real".encode("utf-8"))

    monkeypatch.setattr(po.subprocess, "run", fake_run)
    backend = po.OpenCodeBackend(timeout_s=10)
    assert backend.generar("hola", clave="x") == "respuesta real"
    assert llamado["cmd"] == ["opencode", "run", "hola"]


def test_opencode_backend_codigo_no_cero(monkeypatch):
    def fake_run(cmd, **kwargs):
        return _ProcesoFalso(returncode=2, stderr="fallo interno".encode("utf-8"))

    monkeypatch.setattr(po.subprocess, "run", fake_run)
    backend = po.OpenCodeBackend()
    with pytest.raises(po.BackendError, match="retorno codigo 2"):
        backend.generar("hola")


def test_opencode_backend_cli_no_encontrada(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise FileNotFoundError("no esta en PATH")

    monkeypatch.setattr(po.subprocess, "run", fake_run)
    with pytest.raises(po.BackendError, match="no encontrada en PATH"):
        po.OpenCodeBackend().generar("hola")


def test_opencode_backend_timeout(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 5)

    monkeypatch.setattr(po.subprocess, "run", fake_run)
    with pytest.raises(po.BackendError, match="Timeout"):
        po.OpenCodeBackend(timeout_s=5).generar("hola")


def test_llmbackend_es_abstracta():
    with pytest.raises(TypeError):
        po.LLMBackend()


def test_crear_backend_fabrica_y_validacion():
    assert isinstance(po.crear_backend("mock"), po.MockBackend)
    assert isinstance(po.crear_backend("opencode"), po.OpenCodeBackend)
    with pytest.raises(po.BackendError, match="desconocido"):
        po.crear_backend("chatgpt")
