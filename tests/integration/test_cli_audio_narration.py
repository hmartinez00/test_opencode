# -*- coding: utf-8 -*-
import json

import pytest
import pra_helper


@pytest.fixture
def initialized_audio_project(run_cli, sample_plan_json_str):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    code, _ = run_cli("save-plan", json.dumps(plan, ensure_ascii=False))
    assert code == 0


def respuesta_con_audio(sample_llm_response_s1):
    return sample_llm_response_s1 + """

**BLOQUE 6 — Guion de narración**
```text
[slide: 0] En esta apertura presentamos el contexto de Docker.
[slide: 1] Ahora explicamos el concepto central con un ejemplo.
```
"""


def test_process_session_crea_guion_de_audio(run_cli, initialized_audio_project, sample_llm_response_s1, isolated_dir):
    code, out = run_cli("process-session", "1", respuesta_con_audio(sample_llm_response_s1))

    assert code == 0
    payload = json.loads(out)
    assert payload["audio"]["archivo"] == "assets/audio/guion_sesion1.txt"
    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    audio = project_dir / "assets" / "audio" / "guion_sesion1.txt"
    assert audio.exists()
    assert "[slide: 0]" in audio.read_text(encoding="utf-8")
    assert (project_dir / "backup" / "fuente" / "assets" / "audio" / "guion_sesion1.txt").exists()


def test_process_session_sin_audio_falla_en_modo_estricto(
    run_cli, initialized_audio_project, sample_llm_response_s1, monkeypatch
):
    monkeypatch.setenv("PRA_AUDIO_ESTRICTO", "1")

    code, out = run_cli("process-session", "1", sample_llm_response_s1)

    assert code != 0
    payload = json.loads(out)
    assert "audio" in payload


def test_consolidate_bloquea_lamina_sin_audio(
    run_cli, initialized_audio_project, sample_llm_response_s1, isolated_dir
):
    assert run_cli("process-session", "1", respuesta_con_audio(sample_llm_response_s1))[0] == 0
    audio = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker" / "assets" / "audio" / "guion_sesion1.txt"
    audio.write_text("[slide: 0] Solo la primera.\n", encoding="utf-8")

    code, out = run_cli("consolidate")

    assert code != 0
    payload = json.loads(out)
    assert payload["ok"] is False
    assert payload["audio"]["faltantes"]
    assert not (isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker" / "manifest.blade.php").exists()


def test_cleanup_preserva_guion_de_audio(
    run_cli, sample_plan_json_str, sample_llm_response_s1, isolated_dir
):
    plan = json.loads(sample_plan_json_str)
    plan["sesiones"] = plan["sesiones"][:1]
    assert run_cli("save-plan", json.dumps(plan, ensure_ascii=False))[0] == 0
    assert run_cli("process-session", "1", respuesta_con_audio(sample_llm_response_s1))[0] == 0
    assert run_cli("consolidate")[0] == 0
    assert run_cli("limpiar")[0] == 0

    project_dir = isolated_dir / pra_helper.OUTPUT_BASE_DIR / "intro_docker"
    assert (project_dir / "assets/audio/guion_sesion1.txt").exists()
    assert (project_dir / "backup/fuente/assets/audio/guion_sesion1.txt").exists()
