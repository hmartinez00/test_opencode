# -*- coding: utf-8 -*-
"""Pruebas constitucionales del orquestador (T319).

Verifican que el orquestador respeta la Constitucion del proyecto:
no escribe artefactos de presentacion por si mismo, excluye sus artefactos
de control del entregable y aplica los codigos de salida pactados.
"""
import json
from pathlib import Path

import pytest

import pra_orchestrator as po


COBERTURA_OK = "pra_helper.py  320  38  91%\n30 passed in 0.42s\n"
COBERTURA_FALSA = "pra_helper.py  320  38  90%\n1 failed, 29 passed in 0.5s\n"

ARCHIVOS_RAIZ_PERMITIDOS = {
    "documento_fuente.md",
    # Iteracion 005: el subdirectorio maestro por defecto es 'product_samples'
    "product_samples",
    po.STATE_FILE,
    po.LOG_FILE,
}

ARTEFACTOS_DEL_MOTOR = [
    "presentation_plan.json",
    "class_registry.json",
    "js_registry.json",
    "manifest.blade.php",
    "session1",
    "assets",
]


@pytest.fixture
def entorno(isolated_dir, monkeypatch):
    doc = isolated_dir / "documento_fuente.md"
    doc.write_text("# Introducción a Docker\nContenido.", encoding="utf-8")
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (0, COBERTURA_OK))
    return doc


def test_orquestador_no_escribe_nada_fuera_de_su_whitelist(run_orchestrator, entorno, isolated_dir):
    """Constitucion III: toda mutacion de artefactos la ejecuta pra_helper.py.
    Iteracion 004/005: la corrida deja en raiz solo el maestro product_samples/."""
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")
    assert codigo == 0

    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    presentes = {p.name for p in isolated_dir.iterdir()}
    assert presentes == ARCHIVOS_RAIZ_PERMITIDOS
    assert not (isolated_dir / "outputs.zip").exists()
    # Iteracion 008: sin outputs.zip; el lote protegido + backup/fuente se conservan
    assert not (proyecto / "outputs.zip").exists()

    for artefacto in ARTEFACTOS_DEL_MOTOR:
        assert (proyecto / artefacto).exists(), (
            f"Falta el artefacto generado por pra_helper: {artefacto}"
        )
    # Respaldo de la fuente re-consolidable
    assert (proyecto / "backup/fuente/sesion1").is_dir()
    # Residuales de construccion ya eliminados
    assert not (proyecto / "sesion1").exists()
    assert not (proyecto / "manifest_draft.blade.php").exists()


def test_plan_sin_sesiones_aborta_con_codigo_2(run_orchestrator, entorno, isolated_dir, monkeypatch):
    """Un plan esquematicamente invalido es determinista: aborta sin reintentar."""
    plan_invalido = (
        'Aqui va el plan:\n```json\n{"titulo": "X", "carpeta_snake_case": "x_proyecto",'
        ' "idioma": "es", "resumen_general": "r"}\n```\n'
    )
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(secuencia=[plan_invalido]),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md")

    assert codigo == 2
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert estado["fases"]["save_plan"]["estado"] == "fallida"
    assert estado["fases"]["save_plan"]["intentos"] == 1


def test_pytest_fallido_impide_la_limpieza(run_orchestrator, entorno, isolated_dir, monkeypatch):
    """Constitucion de calidad: sin suite verde no se llega a la fase cleanup."""
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (1, COBERTURA_FALSA))
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")

    assert codigo == 1
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert estado["fases"]["pytest"]["estado"] == "fallida"
    assert estado["fases"]["cleanup"]["estado"] == "pendiente"
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    assert not (proyecto / "outputs.zip").exists()
    assert not (isolated_dir / "outputs.zip").exists()


def test_limpieza_fallida_reporta_codigo_1(run_orchestrator, entorno, isolated_dir, monkeypatch):
    real_run_helper = po.run_helper

    def run_helper_falso(*args):
        if args and args[0] == "limpiar":
            return 2, '{"ok": false}', "lote incompleto simulado"
        return real_run_helper(*args)

    monkeypatch.setattr(po, "run_helper", run_helper_falso)
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")

    assert codigo == 1
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert estado["fases"]["cleanup"]["estado"] == "fallida"


def test_init_fallido_por_motor_retorna_codigo_2(run_orchestrator, entorno, isolated_dir, monkeypatch):
    real_run_helper = po.run_helper

    def run_helper_falso(*args):
        if args and args[0] == "init":
            return 9, "", "fallo simulado del motor en init"
        return real_run_helper(*args)

    monkeypatch.setattr(po, "run_helper", run_helper_falso)
    codigo, _ = run_orchestrator("run", "documento_fuente.md")

    assert codigo == 2
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert estado["fases"]["init"]["estado"] == "fallida"
