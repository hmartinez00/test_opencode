# -*- coding: utf-8 -*-
import json

import pra_helper


def test_audio_es_textual_y_no_se_generan_binarios(
    run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir
):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    respuesta = sample_llm_response_s1 + """
**BLOQUE 6 — Guion de narración
```text
[slide: 0] Contexto.
[slide: 1] Concepto.
```
"""
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", respuesta)[0] == 0
    assert run_cli("consolidate")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    audio_dir = project_dir / "assets" / "audio"
    assert all(path.suffix == ".txt" for path in audio_dir.iterdir())
    assert not list(audio_dir.glob("*.mp3"))
    assert not list(audio_dir.glob("*.wav"))
