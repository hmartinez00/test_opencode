# -*- coding: utf-8 -*-
"""Pruebas de integracion de resume y status del orquestador (T313/T318)."""
import json
from pathlib import Path

import pytest

import pra_orchestrator as po
from pra_helper import load_json


COBERTURA_OK = "pra_helper.py  320  38  91%\n30 passed in 0.42s\n"


@pytest.fixture
def entorno(isolated_dir, monkeypatch):
    doc = isolated_dir / "documento_fuente.md"
    doc.write_text("# Introducción a Docker\nContenido.", encoding="utf-8")
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (0, COBERTURA_OK))
    return doc


def construir_proyecto_hasta_sesion1(entorno, isolated_dir):
    """Construye el proyecto real hasta sesion 1 completada usando el motor directo."""
    plan = (po.MOCKS_DIR / "plan.txt").read_text(encoding="utf-8")
    s1 = (po.MOCKS_DIR / "sesion1.txt").read_text(encoding="utf-8")
    codigo, _, _ = po.run_helper("init", str(entorno))
    assert codigo == 0
    plan_json = po.extraer_json(plan)
    codigo, _, _ = po.run_helper("save-plan", json.dumps(plan_json, ensure_ascii=False))
    assert codigo == 0
    codigo, _, _ = po.run_helper("process-session", "1", s1)
    assert codigo == 0


def sembrar_estado_con_sesion1_completada(isolated_dir):
    """Escribe un estado consistente con init/save_plan/sesion1 completadas."""
    estado = po.nuevo_estado("documento_fuente.md", "mock", 3)
    estado["fases"]["init"]["estado"] = "completada"
    estado["fases"]["save_plan"]["estado"] = "completada"
    s1 = {"numero": 1, "estado": "completada", "intentos": 1,
          "validaciones": {"exit_code_ok": True, "sin_css_inline": True,
                           "laminas_faltantes": [], "detalle": ""}}
    s2 = {"numero": 2, "estado": "pendiente", "intentos": 0, "validaciones": None}
    estado["fases"]["sesiones"] = [s1, s2]
    po.guardar_estado(estado)
    return estado


def test_resume_continua_desde_sesion2_sin_reprocesar_la_1(run_orchestrator, entorno, isolated_dir):
    construir_proyecto_hasta_sesion1(entorno, isolated_dir)
    sembrar_estado_con_sesion1_completada(isolated_dir)
    styles_antes = (isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker" / "styles.blade.php").read_text(encoding="utf-8")

    codigo, salida = run_orchestrator("resume")

    assert codigo == 0
    proyecto = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker"
    # Sesion 2 generada; sesion 1 intacta (CSS no duplicado)
    assert (proyecto / "sesion2" / "comandos-basicos.blade.php").exists()
    styles_despues = (proyecto / "styles.blade.php").read_text(encoding="utf-8")
    assert styles_despues.count(".docker-blue") == styles_antes.count(".docker-blue") == 1
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    assert all(f["estado"] == "completada" for f in (
        estado["fases"]["pytest"], estado["fases"]["zip"]))


def test_resume_sin_corrida_activa_retorna_2(run_orchestrator, entorno):
    codigo, _ = run_orchestrator("resume")
    assert codigo == 2


def test_resume_con_estado_corrupto_retorna_2(run_orchestrator, entorno):
    Path(po.STATE_FILE).write_text("{{no-json", encoding="utf-8")
    codigo, _ = run_orchestrator("resume")
    assert codigo == 2


def test_status_sin_corrida_activa_retorna_2(run_orchestrator, entorno):
    codigo, _ = run_orchestrator("status")
    assert codigo == 2


def test_status_muestra_tabla_de_fases(run_orchestrator, entorno, isolated_dir):
    estado = po.nuevo_estado("documento_fuente.md", "opencode", 4)
    estado["fases"]["init"]["estado"] = "completada"
    estado["fases"]["init"]["intentos"] = 1
    estado["fases"]["sesiones"] = [
        {"numero": 1, "estado": "fallida", "intentos": 3, "validaciones": None}
    ]
    po.guardar_estado(estado)

    codigo, salida = run_orchestrator("status")

    assert codigo == 0
    assert "backend=opencode" in salida
    assert "init" in salida and "completada" in salida
    assert "sesion 1" in salida and "fallida" in salida
