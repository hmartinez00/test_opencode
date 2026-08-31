# -*- coding: utf-8 -*-
"""Pruebas unitarias del estado de orquestacion y utilidades puras del orquestador."""
import json
from pathlib import Path

import pytest

import pra_orchestrator as po


# ============================================================
# Estado: creacion, persistencia atomica y carga - T302/T314
# ============================================================

def test_nuevo_estado_estructura_completa():
    estado = po.nuevo_estado("doc.md", "mock", 3)
    assert estado["version"] == "1.0"
    assert estado["backend"] == "mock"
    assert estado["max_reintentos"] == 3
    for fase in ("init", "save_plan", "pytest", "cleanup"):
        assert estado["fases"][fase]["estado"] == "pendiente"
    assert "cleanup" in estado["fases"]
    assert "zip" not in estado["fases"]
    assert estado["fases"]["sesiones"] == []


def test_normalizar_fases_zip_a_cleanup_completada():
    estado = po.nuevo_estado("doc.md", "mock", 3)
    estado["fases"].pop("cleanup")
    estado["fases"]["zip"] = {"estado": "completada", "intentos": 1, "ultimo_error": None}
    po.normalizar_fases(estado)
    assert "zip" not in estado["fases"]
    assert estado["fases"]["cleanup"]["estado"] == "completada"


def test_normalizar_fases_zip_pendiente_a_cleanup_pendiente():
    estado = po.nuevo_estado("doc.md", "mock", 3)
    estado["fases"].pop("cleanup")
    estado["fases"]["zip"] = {"estado": "en_curso", "intentos": 1, "ultimo_error": None}
    po.normalizar_fases(estado)
    assert "zip" not in estado["fases"]
    assert estado["fases"]["cleanup"]["estado"] == "pendiente"


def test_guardar_y_cargar_roundtrip(isolated_dir):
    estado = po.nuevo_estado("doc.md", "opencode", 5)
    po.guardar_estado(estado)
    cargado = po.cargar_estado()
    assert cargado is not None
    assert cargado["max_reintentos"] == 5
    assert cargado["backend"] == "opencode"


def test_guardado_atomico_no_deja_temporales(isolated_dir):
    estado = po.nuevo_estado("doc.md", "mock", 3)
    po.guardar_estado(estado)
    po.guardar_estado(estado)
    residuos = list(Path(".").glob(".state_*.tmp"))
    assert residuos == []
    assert Path(po.STATE_FILE).exists()


def test_cargar_estado_inexistente_retorna_none(isolated_dir):
    assert po.cargar_estado() is None


def test_cargar_estado_corrupto_retorna_none(isolated_dir):
    Path(po.STATE_FILE).write_text("{json roto", encoding="utf-8")
    assert po.cargar_estado() is None


def test_cargar_estado_sin_fases_retorna_none(isolated_dir):
    Path(po.STATE_FILE).write_text('{"version": "1.0"}', encoding="utf-8")
    assert po.cargar_estado() is None


# ============================================================
# Transiciones de estados - T302/T314
# ============================================================

def test_transiciones_validas_del_automata():
    fase = po._fase_nueva()
    po.iniciar_fase(fase)
    assert fase["estado"] == "en_curso"
    po.completar_fase(fase)
    assert fase["estado"] == "completada"
    fase2 = po._fase_nueva()
    po.iniciar_fase(fase2)
    po.fallar_fase(fase2, "motivo x")
    assert fase2["ultimo_error"] == "motivo x"
    po.iniciar_fase(fase2)
    assert fase2["estado"] == "en_curso"


@pytest.mark.parametrize(
    "desde,hacia",
    [
        ("pendiente", "completada"),
        ("pendiente", "fallida"),
        ("completada", "en_curso"),
        ("completada", "fallida"),
        ("fallida", "completada"),
        ("en_curso", "pendiente"),
    ],
)
def test_transiciones_invalidas_lanzan_error(desde, hacia):
    fase = {"estado": desde, "intentos": 0, "ultimo_error": None}
    with pytest.raises(ValueError, match="Transicion invalida"):
        po.aplicar_transicion(fase, hacia)


def test_resetear_fase_normaliza_a_pendiente():
    fase = {"estado": "fallida", "intentos": 3, "ultimo_error": "boom"}
    po.resetear_fase(fase)
    assert fase == {"estado": "pendiente", "intentos": 0, "ultimo_error": None}


def test_sesion_en_estado_crea_y_mantiene_orden():
    estado = po.nuevo_estado("doc.md", "mock", 3)
    po.sesion_en_estado(estado, 2)
    s1 = po.sesion_en_estado(estado, 1)
    numeros = [s["numero"] for s in estado["fases"]["sesiones"]]
    assert numeros == [1, 2]
    assert po.sesion_en_estado(estado, 2) is estado["fases"]["sesiones"][1]
    assert s1["estado"] == "pendiente"


# ============================================================
# Log de auditoria - T303/T314
# ============================================================

def test_registrar_log_formato_de_linea(isolated_dir):
    po.registrar_log("sesion1", 2, "OK", "", 1.25)
    po.registrar_log("save-plan", 1, "FALLO", "JSON malformado", 0.5)
    lineas = Path(po.LOG_FILE).read_text(encoding="utf-8").strip().splitlines()
    assert len(lineas) == 2
    assert "sesion1" in lineas[0]
    assert "intento=2" in lineas[0]
    assert "resultado=OK" in lineas[0]
    assert "duracion_s=1.25" in lineas[0]
    assert 'motivo="JSON malformado"' in lineas[1]


# ============================================================
# Utilidades puras: extraer_json y resumen pytest
# ============================================================

PLAN_MINIMO = '{"titulo": "T", "carpeta_snake_case": "t", "idioma": "es", "resumen_general": "r", "sesiones": []}'


def test_extraer_json_directo():
    assert po.extraer_json(PLAN_MINIMO)["titulo"] == "T"


def test_extraer_json_en_cerca_markdown():
    respuesta = f"Aqui tienes:\n```json\n{PLAN_MINIMO}\n```\nSaludos."
    assert po.extraer_json(respuesta)["carpeta_snake_case"] == "t"


def test_extraer_json_embebido_en_prosa():
    respuesta = f"Plan generado:\nPrefacio... {PLAN_MINIMO} ...fin."
    assert po.extraer_json(respuesta)["idioma"] == "es"


def test_extraer_json_basura_retorna_none():
    assert po.extraer_json("No hay nada por aqui") is None


RESUMEN_OK = (
    "----------- coverage -----------\n"
    "Name            Stmts Miss Cover\n"
    "pra_helper.py     320   38   88%\n"
    "TOTAL             320   38   88%\n"
    "30 passed, 1 warning in 0.65s\n"
)


def test_parsear_resumen_pytest_exito():
    passed, failed, errores, cobertura = po.parsear_resumen_pytest(RESUMEN_OK)
    assert (passed, failed, errores, cobertura) == (30, 0, 0, 88.0)


def test_parsear_resumen_pytest_con_fallos():
    salida = RESUMEN_OK.replace("30 passed", "1 failed, 29 passed")
    passed, failed, errores, cobertura = po.parsear_resumen_pytest(salida)
    assert (passed, failed, errores) == (29, 1, 0)
    assert cobertura == 88.0


def test_parsear_resumen_pytest_sin_cobertura_detectable():
    passed, failed, errores, cobertura = po.parsear_resumen_pytest("12 passed in 0.1s")
    assert (passed, failed, errores, cobertura) == (12, 0, 0, None)


def test_parsear_resumen_pytest_vacio():
    assert po.parsear_resumen_pytest("") == (0, 0, 0, None)


# ============================================================
# Prompt de reflexion - T311
# ============================================================

def test_prompt_reflexion_contiene_diagnostico():
    prompt = po.construir_prompt_reflexion(
        "PROMPT BASE", "process-session 1", 2,
        ["Cero CSS Inline"], 'violacion en lamina', 2, 3,
    )
    assert prompt.startswith("PROMPT BASE")
    assert "REINTENTO 2/3" in prompt
    assert "- Fase: process-session 1" in prompt
    assert "Codigo de retorno: 2" in prompt
    assert "Cero CSS Inline" in prompt
    assert "regenera la respuesta COMPLETA" in prompt


def test_prompt_reflexion_recorta_detalle_stderr():
    detalle = "x" * 2000
    prompt = po.construir_prompt_reflexion("P", "fase", 1, [], detalle, 1, 3)
    cuerpo = prompt.split("STDERR")[1]
    assert detalle not in prompt
    assert len(cuerpo) < len(detalle)
