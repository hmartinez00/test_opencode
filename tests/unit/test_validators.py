# -*- coding: utf-8 -*-
import pytest
from pra_helper import (
    validate_no_inline_css,
    validate_kebab_id,
    validate_folder_name,
    validate_plan_schema
)

def test_validate_no_inline_css_valid():
    """Prueba que el contenido sin CSS inline pase la validación."""
    content = '<div class="my-class">Hola Mundo</div>'
    is_valid, error = validate_no_inline_css(content, "slide-1")
    assert is_valid is True
    assert error == ""

def test_validate_no_inline_css_invalid():
    """Prueba que el contenido con CSS inline sea rechazado."""
    content_double_quotes = '<div style="color: red;">Hola</div>'
    is_valid, error = validate_no_inline_css(content_double_quotes, "slide-1")
    assert is_valid is False
    assert "Violacion de Cero CSS Inline" in error

    content_single_quotes = "<div style='color: red;'>Hola</div>"
    is_valid, error = validate_no_inline_css(content_single_quotes, "slide-2")
    assert is_valid is False
    assert "Violacion de Cero CSS Inline" in error

    content_spaces = '<div style  =  "color: red;">Hola</div>'
    is_valid, error = validate_no_inline_css(content_spaces, "slide-3")
    assert is_valid is False
    assert "Violacion de Cero CSS Inline" in error

def test_validate_kebab_id():
    """Prueba que la validación de kebab-case funcione correctamente."""
    assert validate_kebab_id("slide-id-1") is True
    assert validate_kebab_id("intro") is True
    assert validate_kebab_id("Slide-id") is False
    assert validate_kebab_id("slide_id") is False
    assert validate_kebab_id("-slide") is False
    assert validate_kebab_id("slide-") is False

def test_validate_folder_name():
    """Prueba que la validación de nombre de carpeta (snake_case) funcione."""
    assert validate_folder_name("intro_docker") is True
    assert validate_folder_name("intro123") is True
    assert validate_folder_name("intro-docker") is False
    assert validate_folder_name("IntroDocker") is False
    assert validate_folder_name("_intro") is False

def test_validate_plan_schema_valid():
    """Prueba un plan con esquema válido."""
    valid_plan = {
        "titulo": "Mi Presentación",
        "carpeta_snake_case": "mi_presentacion",
        "idioma": "es",
        "resumen_general": "Resumen",
        "sesiones": [
            {
                "titulo": "Sesion 1",
                "laminas": [
                    {
                        "id_kebab_case": "slide-one",
                        "tipo": "portada"
                    }
                ]
            }
        ]
    }
    errors = validate_plan_schema(valid_plan)
    assert len(errors) == 0

def test_validate_plan_schema_invalid():
    """Prueba planes inválidos para gatillar errores."""
    # Faltan campos raíz obligatorios
    invalid_plan_1 = {
        "idioma": "es",
        "resumen_general": "Resumen",
        "sesiones": []
    }
    errors = validate_plan_schema(invalid_plan_1)
    assert any("titulo" in e for e in errors)
    assert any("carpeta_snake_case" in e for e in errors)
    assert any("al menos una sesion" in e for e in errors)

    # Sesión sin láminas y lámina con ID inválido
    invalid_plan_2 = {
        "titulo": "Mi Presentación",
        "carpeta_snake_case": "mi_presentacion",
        "idioma": "es",
        "resumen_general": "Resumen",
        "sesiones": [
            {
                "titulo": "Sesión 1",
                "laminas": [
                    {
                        "id": "Slide-ID-Invalido",
                        "tipo": "tipo_desconocido"
                    }
                ]
            }
        ]
    }
    errors = validate_plan_schema(invalid_plan_2)
    assert any("no es kebab-case valido" in e for e in errors)
    assert any("no valido (permitidos" in e for e in errors)
