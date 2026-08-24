# -*- coding: utf-8 -*-
"""Pruebas de integracion del override PRA_OUTPUT_DIR (iteracion 004 - US4)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pra_helper


def test_pra_output_dir_redirige_la_creacion_del_proyecto(isolated_dir):
    """US4 esc.1: con PRA_OUTPUT_DIR=custom_out el proyecto se crea bajo esa carpeta."""
    plan = {
        "titulo": "Demo",
        "carpeta_snake_case": "demo_curso",
        "idioma": "es",
        "resumen_general": "r",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "S1",
                "objetivo_pedagogico": "o",
                "laminas": [
                    {"orden": 1, "id_kebab_case": "lamina-a", "tipo": "portada"}
                ],
            }
        ],
    }
    env = {**os.environ, "PRA_OUTPUT_DIR": "custom_out"}
    script = Path(pra_helper.__file__).resolve()
    proc = subprocess.run(
        [sys.executable, str(script), "save-plan", json.dumps(plan)],
        capture_output=True,
        cwd=str(isolated_dir),
        env=env,
    )

    assert proc.returncode == 0
    payload = json.loads(proc.stdout.decode("utf-8"))
    assert payload["status"] == "exito"
    base = isolated_dir / "custom_out"
    assert (base / "demo_curso" / "presentation_plan.json").exists()
    # El default no se crea cuando hay override
    assert not (isolated_dir / pra_helper.OUTPUT_BASE_DIR).exists()
