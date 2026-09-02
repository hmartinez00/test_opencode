# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pra_helper
from pra_helper import load_json


def test_save_plan_deduplica_clases_css(run_cli, isolated_dir):
    """A2: La misma clase CSS en 2 laminas debe producir 1 sola entrada en class_registry."""
    plan = {
        "titulo": "Test Dedup",
        "carpeta_snake_case": "test_dedup",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "clases_css_requeridas": [
                        {"nombre": "cls-duplicada", "descripcion": "primera"}
                    ]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "clases_css_requeridas": [
                        {"nombre": "cls-duplicada", "descripcion": "segunda"}
                    ]
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code == 0

    registry = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_dedup" / "class_registry.json")
    entradas = [c for c in registry["clases"] if c["nombre"] == "cls-duplicada"]
    assert len(entradas) == 1


def test_save_plan_deduplica_comportamientos_js(run_cli, isolated_dir):
    """A2: El mismo comportamiento JS en 2 laminas debe producir 1 sola entrada en js_registry."""
    plan = {
        "titulo": "Test Dedup JS",
        "carpeta_snake_case": "test_dedup_js",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "comportamientos_js_requeridos": [
                        {"nombre": "js-dup", "descripcion": "primera"}
                    ]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "comportamientos_js_requeridos": [
                        {"nombre": "js-dup", "descripcion": "segunda"}
                    ]
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code == 0

    registry = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_dedup_js" / "js_registry.json")
    entradas = [j for j in registry["comportamientos"] if j["nombre"] == "js-dup"]
    assert len(entradas) == 1


def test_save_plan_mantiene_orden_primera_aparicion(run_cli, isolated_dir):
    """A2: Al deduplicar, se conserva la descripcion de la primera ocurrencia."""
    plan = {
        "titulo": "Test Orden",
        "carpeta_snake_case": "test_orden_dedup",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "clases_css_requeridas": [
                        {"nombre": "misma-clase", "descripcion": "primera"}
                    ]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "clases_css_requeridas": [
                        {"nombre": "misma-clase", "descripcion": "segunda"}
                    ]
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code == 0

    registry = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_orden_dedup" / "class_registry.json")
    entrada = [c for c in registry["clases"] if c["nombre"] == "misma-clase"][0]
    assert entrada["descripcion"] == "primera"


def test_save_plan_clases_string_deduplica(run_cli, isolated_dir):
    """A2: Clases como strings tambien se deduplican."""
    plan = {
        "titulo": "Test Str Dedup",
        "carpeta_snake_case": "test_str_dedup",
        "idioma": "es",
        "resumen_general": "test",
        "sesiones": [{
            "numero": 1,
            "titulo": "Sesion 1",
            "objetivo_pedagogico": "Obj",
            "laminas": [
                {
                    "orden": 1,
                    "id_kebab_case": "lamina-1",
                    "tipo": "contenido",
                    "objetivo": "Obj 1",
                    "insumos": [],
                    "clases_css_requeridas": ["text-center"]
                },
                {
                    "orden": 2,
                    "id_kebab_case": "lamina-2",
                    "tipo": "contenido",
                    "objetivo": "Obj 2",
                    "insumos": [],
                    "clases_css_requeridas": ["text-center"]
                }
            ]
        }]
    }
    code, out = run_cli("save-plan", json.dumps(plan))
    assert code == 0

    registry = load_json(Path(isolated_dir) / "product_samples" / "slides" / "test_str_dedup" / "class_registry.json")
    entradas = [c for c in registry["clases"] if c["nombre"] == "text-center"]
    assert len(entradas) == 1
