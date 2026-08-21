# -*- coding: utf-8 -*-
import pytest
from pra_helper import normalize_plan

def test_normalize_plan_with_model_fields():
    """Prueba la normalización usando los campos estándar definidos en el data-model.md."""
    plan = {
        "titulo": "Test Plan",
        "carpeta_snake_case": "test_folder",
        "idioma": "es",
        "resumen_general": "Resumen",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "Sesion 1",
                "objetivo_pedagogico": "Objetivo 1",
                "laminas": [
                    {
                        "orden": 1,
                        "id_kebab_case": "slide-one",
                        "tipo": "portada",
                        "objetivo": "Presentar",
                        "insumos": ["Insumo A"]
                    }
                ]
            }
        ]
    }
    norm = normalize_plan(plan)
    assert norm["titulo"] == "Test Plan"
    assert norm["carpeta_snake_case"] == "test_folder"
    assert norm["idioma"] == "es"
    assert norm["resumen_general"] == "Resumen"
    assert len(norm["sesiones"]) == 1
    
    ses = norm["sesiones"][0]
    assert ses["numero"] == 1
    assert ses["titulo"] == "Sesion 1"
    assert ses["objetivo_pedagogico"] == "Objetivo 1"
    assert len(ses["laminas"]) == 1
    
    lam = ses["laminas"][0]
    assert lam["orden"] == 1
    assert lam["id_kebab_case"] == "slide-one"
    assert lam["tipo"] == "portada"
    assert lam["objetivo"] == "Presentar"
    assert lam["insumos"] == ["Insumo A"]

def test_normalize_plan_with_alternative_template_fields():
    """Prueba la normalización usando los campos alternativos provenientes de plantillas de prompts."""
    plan_alt = {
        "titulo": "Test Alt Plan",
        "folder_name": "test_folder_alt",
        "idioma": "es",
        "resumen_general": "Resumen Alt",
        "sesiones": [
            {
                "nro": 2,
                "titulo_sesion": "Sesion Alt 2",
                "objetivos": ["Aprender X", "Aprender Y"],
                "laminas": [
                    {
                        "orden": 3,
                        "id": "slide-alt",
                        "tipo": "interactiva",
                        "objetivo_pedagogico": "Interactuar",
                        "insumos": ["Insumo B"]
                    }
                ]
            }
        ]
    }
    norm = normalize_plan(plan_alt)
    assert norm["carpeta_snake_case"] == "test_folder_alt"
    
    ses = norm["sesiones"][0]
    assert ses["numero"] == 2
    assert ses["titulo"] == "Sesion Alt 2"
    assert ses["objetivo_pedagogico"] == "Aprender X, Aprender Y"
    
    lam = ses["laminas"][0]
    assert lam["orden"] == 3
    assert lam["id_kebab_case"] == "slide-alt"
    assert lam["tipo"] == "interactiva"
    assert lam["objetivo"] == "Interactuar"
