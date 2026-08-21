# -*- coding: utf-8 -*-
import pytest
from pra_helper import merge_registry, load_json, save_json

def test_merge_registry_no_duplicates():
    """Prueba que merge_registry no agregue duplicados y retorne los nombres agregados."""
    existing = [
        {"nombre": "btn-primary", "descripcion": "Botón primario", "implementada": True},
        {"nombre": "text-muted", "descripcion": "Texto gris", "implementada": False}
    ]
    new_entries = [
        {"nombre": "btn-primary", "descripcion": "Duplicado", "implementada": True},
        {"nombre": "card-layout", "descripcion": "Nuevo Card Layout", "implementada": False}
    ]
    
    added = merge_registry(existing, new_entries, key_field="nombre")
    
    # Solo "card-layout" debió agregarse
    assert added == ["card-layout"]
    assert len(existing) == 3
    assert existing[-1]["nombre"] == "card-layout"

def test_save_and_load_json(tmp_path):
    """Prueba que las utilidades JSON guarden y carguen correctamente preservando UTF-8."""
    test_file = tmp_path / "test_data.json"
    data = {"clave": "valor_ñ_á_é"}
    
    save_json(test_file, data)
    assert test_file.exists()
    
    loaded = load_json(test_file)
    assert loaded == data
    assert loaded["clave"] == "valor_ñ_á_é"
