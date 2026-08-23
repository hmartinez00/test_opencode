# -*- coding: utf-8 -*-
"""Pruebas unitarias de la puerta de validacion post-sesion (T310/T315)."""
import json
from pathlib import Path

import pra_orchestrator as po


def crear_proyecto(isolated_dir, laminas=None, contenidos=None, plan_valido=True):
    """Crea un arbol minimo de proyecto PRA para validar puertas post-sesion."""
    laminas = laminas if laminas is not None else ["que-es-docker", "arquitectura"]
    contenidos = contenidos or {}
    proyecto = isolated_dir / "intro_docker"
    sesion_dir = proyecto / "sesion1"
    sesion_dir.mkdir(parents=True)
    plan = {
        "titulo": "T",
        "carpeta_snake_case": "intro_docker",
        "idioma": "es",
        "resumen_general": "r",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "S1",
                "objetivo_pedagogico": "o",
                "laminas": [
                    {"orden": i + 1, "id_kebab_case": lid, "tipo": "contenido"}
                    for i, lid in enumerate(laminas)
                ],
            }
        ],
    }
    ruta_plan = proyecto / "presentation_plan.json"
    if plan_valido:
        ruta_plan.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    else:
        ruta_plan.write_text("{plan roto", encoding="utf-8")
    for lid in contenidos:
        (sesion_dir / f"{lid}.blade.php").write_text(contenidos[lid], encoding="utf-8")
    return proyecto


def test_puerta_ok_con_laminas_completas(isolated_dir):
    crear_proyecto(
        isolated_dir,
        contenidos={
            "que-es-docker": '<div class="a">hola</div>',
            "arquitectura": '<div class="b">mundo</div>',
        },
    )
    reporte = po.validar_post_sesion(1)
    assert reporte["exit_code_ok"] is True
    assert reporte["sin_css_inline"] is True
    assert reporte["laminas_faltantes"] == []
    assert po.reporte_valido(reporte) is True


def test_puerta_detecta_css_inline(isolated_dir):
    crear_proyecto(
        isolated_dir,
        laminas=["que-es-docker"],
        contenidos={"que-es-docker": '<div style="color: red;">x</div>'},
    )
    reporte = po.validar_post_sesion(1)
    assert reporte["sin_css_inline"] is False
    assert "que-es-docker.blade.php" in reporte["detalle"]
    assert po.reporte_valido(reporte) is False


def test_puerta_detecta_laminas_faltantes(isolated_dir):
    crear_proyecto(isolated_dir, laminas=["que-es-docker", "arquitectura"],
                   contenidos={"que-es-docker": "<div>x</div>"})
    reporte = po.validar_post_sesion(1)
    assert reporte["laminas_faltantes"] == ["arquitectura"]
    assert po.reporte_valido(reporte) is False


def test_puerta_sin_directorio_de_proyecto(isolated_dir):
    reporte = po.validar_post_sesion(1)
    assert reporte["sin_css_inline"] is False
    assert "No se encontro directorio" in reporte["detalle"]
    assert po.reporte_valido(reporte) is False


def test_puerta_con_plan_ilegible(isolated_dir):
    crear_proyecto(isolated_dir, plan_valido=False)
    reporte = po.validar_post_sesion(1)
    assert reporte["sin_css_inline"] is False
    assert "Error leyendo plan" in reporte["detalle"]


def test_puerta_sesion_sin_directorio_aun(isolated_dir):
    crear_proyecto(isolated_dir)  # sin contenidos -> sesion1 sin blades
    reporte = po.validar_post_sesion(1)
    assert sorted(reporte["laminas_faltantes"]) == ["arquitectura", "que-es-docker"]


def test_reporte_valido_exige_todas_las_condiciones():
    base = {"exit_code_ok": True, "sin_css_inline": True, "laminas_faltantes": [], "detalle": ""}
    assert po.reporte_valido(base) is True
    assert po.reporte_valido({**base, "exit_code_ok": False}) is False
    assert po.reporte_valido({**base, "sin_css_inline": False}) is False
    assert po.reporte_valido({**base, "laminas_faltantes": ["x"]}) is False


def test_buscar_proyecto_encuentra_carpeta_activa(isolated_dir):
    assert po.buscar_proyecto() is None
    crear_proyecto(isolated_dir)
    encontrado = po.buscar_proyecto()
    assert encontrado is not None and encontrado.name == "intro_docker"


def test_sesiones_del_plan_lee_numeros(isolated_dir):
    assert po.sesiones_del_plan() == []
    crear_proyecto(isolated_dir)
    assert [s["numero"] for s in po.sesiones_del_plan()] == [1]
