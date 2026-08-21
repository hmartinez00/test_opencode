# -*- coding: utf-8 -*-
import json


def test_cli_init_success(run_cli, sample_markdown_doc):
    """El comando init debe salir con codigo 0 e imprimir el prompt compilado con el documento."""
    code, out = run_cli("init", str(sample_markdown_doc))

    assert code == 0
    assert "Introducción a Docker" in out
    assert "CONTENIDO DEL DOCUMENTO FUENTE" in out


def test_cli_init_document_not_found(run_cli):
    """El comando init debe fallar con codigo 1 si el documento no existe."""
    code, out = run_cli("init", "no_existe_documento.md")

    assert code == 1
    payload = json.loads(out)
    assert "error" in payload
    assert "no encontrado" in payload["error"]
