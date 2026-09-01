# -*- coding: utf-8 -*-
import pytest

import pra_helper


@pytest.fixture
def plan_sesion():
    return {
        "numero": 1,
        "laminas": [
            {"orden": 1, "id_kebab_case": "apertura", "objetivo": "Presentar el contexto", "insumos": ["contexto"]},
            {"orden": 2, "id_kebab_case": "concepto", "objetivo": "Explicar el concepto central", "insumos": ["ejemplo"]},
        ],
    }


def test_parse_guion_asocia_texto_y_conserva_indice():
    resultado = pra_helper.parse_guion_narrativo(
        "[slide: 0] Apertura de la sesión.\n[slide: 1] Explicación central."
    )

    assert resultado == [
        {"slide": 0, "texto": "Apertura de la sesión."},
        {"slide": 1, "texto": "Explicación central."},
    ]


def test_validar_guion_detecta_slide_duplicada(plan_sesion):
    reporte = pra_helper.validar_guion_narrativo(
        "[slide: 0] Uno.\n[slide: 0] Dos.\n[slide: 1] Tres.", plan_sesion
    )

    assert reporte["duplicadas"] == [0]


def test_validar_guion_detecta_indice_fuera_de_rango(plan_sesion):
    reporte = pra_helper.validar_guion_narrativo(
        "[slide: 4] Texto sin destino.", plan_sesion
    )

    assert reporte["huerfanas"][0]["slide"] == 4


def test_validar_guion_detecta_entrada_vacia(plan_sesion):
    reporte = pra_helper.validar_guion_narrativo(
        "[slide: 0]   \n[slide: 1] Texto válido.", plan_sesion
    )

    assert reporte["vacias"] == [0]


def test_validar_guion_detecta_lamina_sin_narracion(plan_sesion):
    reporte = pra_helper.validar_guion_narrativo(
        "[slide: 0] Solo la primera.", plan_sesion
    )

    assert reporte["faltantes"][0]["slide"] == 1


def test_parse_guion_rechaza_texto_sin_marca():
    with pytest.raises(pra_helper.AudioNarrationError):
        pra_helper.parse_guion_narrativo("Texto sin slide asociada")


def test_validar_guion_reporta_advertencia_semantica(plan_sesion):
    reporte = pra_helper.validar_guion_narrativo(
        "[slide: 0] Texto ajeno.\n[slide: 1] También ajeno.", plan_sesion
    )

    assert reporte["advertencias"]
