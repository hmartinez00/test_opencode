# -*- coding: utf-8 -*-
import pytest
from pra_helper import parse_llm_response

def test_parse_llm_response_valid(sample_llm_response_s1):
    """Prueba el parseo exitoso de una respuesta LLM estándar bien estructurada."""
    blocks = parse_llm_response(sample_llm_response_s1)
    
    # Verificar láminas Blade
    assert len(blocks["laminas"]) == 2
    assert blocks["laminas"][0]["id"] == "que-es-docker"
    assert "<h1>¿Qué es Docker?</h1>" in blocks["laminas"][0]["content"]
    assert blocks["laminas"][1]["id"] == "arquitectura"
    assert "<p>Cliente, Host y Registro.</p>" in blocks["laminas"][1]["content"]
    
    # Verificar estilos CSS
    assert ".docker-blue" in blocks["estilos_css"]
    assert ".slide-architecture" in blocks["estilos_css"]
    
    # Verificar scripts JS
    assert "Docker slide loaded" in blocks["scripts_js"]
    
    # Verificar entradas manifest
    assert len(blocks["manifest_entries"]) == 2
    assert blocks["manifest_entries"][0]["view"] == "sesion1.que-es-docker"
    assert blocks["manifest_entries"][0]["data_title"] == "¿Qué es Docker?"
    assert blocks["manifest_entries"][1]["view"] == "sesion1.arquitectura"
    assert blocks["manifest_entries"][1]["data_title"] == "Arquitectura"
    
    # Verificar actualizaciones de registros
    reg = blocks["registry_updates"]
    assert len(reg["nuevas_clases"]) == 2
    assert reg["nuevas_clases"][0]["nombre"] == "docker-blue"
    assert reg["clases_materializadas"] == ["docker-blue", "slide-architecture"]
    assert len(reg["nuevos_comportamientos"]) == 1
    assert reg["nuevos_comportamientos"][0]["nombre"] == "ripple-effect"
    assert reg["comportamientos_materializados"] == ["ripple-effect"]

def test_parse_llm_response_empty_or_missing_blocks():
    """Prueba que el parser se comporte de forma robusta ante bloques faltantes o vacíos."""
    response = """Respuesta con bloques vacíos o ausentes.
    
    {{-- sesion1/simple.blade.php --}}
    <div>Contenido simple</div>
    """
    blocks = parse_llm_response(response)
    
    assert len(blocks["laminas"]) == 1
    assert blocks["laminas"][0]["id"] == "simple"
    assert blocks["estilos_css"] == ""
    assert blocks["scripts_js"] == ""
    assert len(blocks["manifest_entries"]) == 0
    assert blocks["registry_updates"]["nuevas_clases"] == []
