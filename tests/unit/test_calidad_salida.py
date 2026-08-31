# -*- coding: utf-8 -*-
"""Pruebas unitarias de calidad de salida (iteracion 007):
interpolacion, envoltura de fragmentos y titulos legibles."""
import pra_helper


def test_titulo_legible_convierte_guiones_en_espacios():
    assert pra_helper.titulo_legible("s1-listas-teoria") == "S1 Listas Teoria"


def test_titulo_legible_reto_final():
    assert pra_helper.titulo_legible("s1-retofinal-contactos") == "S1 Retofinal Contactos"


def test_envolver_css_con_style():
    css = ".docker-blue { color: red; }"
    envuelto = pra_helper._envolver_fragmento("css", css)
    assert envuelto.startswith("<style>")
    assert envuelto.endswith("</style>")
    assert ".docker-blue" in envuelto


def test_envolver_js_con_script():
    js = "console.log('hola');"
    envuelto = pra_helper._envolver_fragmento("js", js)
    assert envuelto.startswith("<script>")
    assert envuelto.endswith("</script>")
    assert "console.log" in envuelto


def test_no_duplica_envoltura_css():
    css = "<style>\n.x { }\n</style>"
    envuelto = pra_helper._envolver_fragmento("css", css)
    assert envuelto.count("<style>") == 1
    assert envuelto.count("</style>") == 1


def test_no_duplica_envoltura_js():
    js = "<script>\nfoo()\n</script>"
    envuelto = pra_helper._envolver_fragmento("js", js)
    assert envuelto.count("<script>") == 1
    assert envuelto.count("</script>") == 1


def test_constante_entrypoint_usa_llave_unica():
    prefijo = "presentation.slides.{$presentation->folder_name}"
    assert pra_helper.ENTRYPOINT_PREFIX == prefijo
    assert "{{$presentation->folder_name}}" not in pra_helper.ENTRYPOINT_PREFIX
