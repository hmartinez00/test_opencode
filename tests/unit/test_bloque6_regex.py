# -*- coding: utf-8 -*-
import pytest
import pra_helper


class TestBloque6RegexLineaEnBlanco:
    """A1: La regex del BLOQUE 6 debe tolerar linea en blanco antes del fence."""

    def test_bloque6_con_linea_en_blanco(self):
        respuesta = (
            "otro contenido\n"
            "**BLOQUE 6 — Guion de narracion**\n"
            "\n"
            "```text\n"
            "[slide: 0] Apertura.\n"
            "[slide: 1] Primer concepto.\n"
            "```\n"
        )
        bloques = pra_helper.parse_llm_response(respuesta)
        assert "guion_narrativo" in bloques
        assert "[slide: 0]" in bloques["guion_narrativo"]

    def test_bloque6_sin_linea_en_blanco(self):
        respuesta = (
            "**BLOQUE 6 — Guion de narracion**\n"
            "```text\n"
            "[slide: 0] Apertura.\n"
            "```\n"
        )
        bloques = pra_helper.parse_llm_response(respuesta)
        assert "[slide: 0]" in bloques["guion_narrativo"]

    def test_respuesta_sin_bloque6_devuelve_vacio(self):
        respuesta = (
            "```blade\n"
            "{{- sesion1/slide1.blade.php -}}\n"
            "```\n"
        )
        bloques = pra_helper.parse_llm_response(respuesta)
        assert bloques.get("guion_narrativo", "") == ""

    def test_bloque6_con_espacios_en_linea_blanca(self):
        respuesta = (
            "**BLOQUE 6 — Guion**\n"
            "   \t\n"
            "```text\n"
            "[slide: 0] Texto.\n"
            "```\n"
        )
        bloques = pra_helper.parse_llm_response(respuesta)
        assert "[slide: 0]" in bloques["guion_narrativo"]

    def test_bloque6_fence_sin_etiqueta(self):
        respuesta = (
            "**BLOQUE 6 — Guion**\n"
            "\n"
            "```\n"
            "[slide: 0] Texto.\n"
            "```\n"
        )
        bloques = pra_helper.parse_llm_response(respuesta)
        assert "[slide: 0]" in bloques["guion_narrativo"]
