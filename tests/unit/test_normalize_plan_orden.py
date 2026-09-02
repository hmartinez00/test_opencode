# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pra_helper
from pra_helper import load_json


def test_normalize_plan_asigna_orden_auto():
    """A3: Un plan sin campo orden debe numerar laminas 1..N."""
    plan_raw = {
        "titulo": "Test Orden Auto",
        "carpeta_snake_case": "test_orden_auto",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": []},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": []},
                {"id_kebab_case": "c", "tipo": "contenido", "objetivo": "o3", "insumos": []}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert [l["orden"] for l in laminas] == [1, 2, 3]


def test_normalize_plan_orden_parcial_completa_secuencia():
    """A3: Si solo algunas laminas traen orden, las faltantes completan sin colisionar."""
    plan_raw = {
        "titulo": "Test Parcial",
        "carpeta_snake_case": "test_orden_parcial",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": [], "orden": 1},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": []},
                {"id_kebab_case": "c", "tipo": "contenido", "objetivo": "o3", "insumos": [], "orden": 3}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert laminas[0]["orden"] == 1
    assert laminas[1]["orden"] == 2
    assert laminas[2]["orden"] == 3


def test_normalize_plan_orden_explicito_se_respeta():
    """A3: Si todas las laminas traen orden explicito, se respeta."""
    plan_raw = {
        "titulo": "Test Explicito",
        "carpeta_snake_case": "test_orden_explicito",
        "sesiones": [{
            "numero": 1,
            "titulo": "S1",
            "laminas": [
                {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": [], "orden": 5},
                {"id_kebab_case": "b", "tipo": "contenido", "objetivo": "o2", "insumos": [], "orden": 10}
            ]
        }]
    }
    plan = pra_helper.normalize_plan(plan_raw)
    laminas = plan["sesiones"][0]["laminas"]
    assert [l["orden"] for l in laminas] == [5, 10]


def test_save_plan_estricto_sin_orden_falla(run_cli, isolated_dir):
    """A3: PRA_PLAN_ESTRICTO=1 con plan sin orden debe fallar."""
    import os
    os.environ["PRA_PLAN_ESTRICTO"] = "1"
    try:
        plan_raw = {
            "titulo": "Test Estricto",
            "carpeta_snake_case": "test_estricto_orden",
            "sesiones": [{
                "numero": 1,
                "titulo": "S1",
                "laminas": [
                    {"id_kebab_case": "a", "tipo": "contenido", "objetivo": "o1", "insumos": []}
                ]
            }]
        }
        code, out = run_cli("save-plan", json.dumps(plan_raw))
        assert code == 2
    finally:
        os.environ.pop("PRA_PLAN_ESTRICTO", None)
