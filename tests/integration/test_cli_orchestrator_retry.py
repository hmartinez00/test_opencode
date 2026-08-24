# -*- coding: utf-8 -*-
"""Pruebas de integracion del bucle de reintentos y reflexion de error (T317)."""
import json
from pathlib import Path

import pytest

import pra_orchestrator as po


COBERTURA_OK = "pra_helper.py  320  38  91%\n30 passed in 0.42s\n"

CONTAMINADA_S1 = """Sesion 1 con CSS inline prohibido:

{{- sesion1/que-es-docker.blade.php -}}
<div style="color: red;">
    <h1>¿Qué es Docker?</h1>
</div>

**BLOQUE 2**
```css
/* vacio */
```

**BLOQUE 3**
```javascript
// vacio
```

**BLOQUE 4**
<x-slide view="sesion1.que-es-docker" data-title="¿Qué es Docker?" />

**BLOQUE 5**
```json
{
  "nuevas_clases": [],
  "clases_materializadas": [],
  "nuevos_comportamientos": [],
  "comportamientos_materializados": []
}
```
"""


def respuestas_mock(con_contaminada=False):
    """Secuencia completa de llamadas al backend: plan, sesion1, sesion2."""
    mocks = po.MOCKS_DIR
    plan = (mocks / "plan.txt").read_text(encoding="utf-8")
    s1 = (mocks / "sesion1.txt").read_text(encoding="utf-8")
    s2 = (mocks / "sesion2.txt").read_text(encoding="utf-8")
    if con_contaminada:
        return [plan, CONTAMINADA_S1, s1, s2]
    return [plan, s1, s2]


@pytest.fixture
def entorno(isolated_dir, monkeypatch):
    doc = isolated_dir / "documento_fuente.md"
    doc.write_text("# Introducción a Docker\nContenido.", encoding="utf-8")
    monkeypatch.setattr(po, "_ejecutar_pytest", lambda: (0, COBERTURA_OK))
    return doc


def test_reintento_contaminada_luego_valida(run_orchestrator, entorno, isolated_dir, monkeypatch):
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(
            secuencia=respuestas_mock(con_contaminada=True)
        ),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock")

    assert codigo == 0
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    sesion1 = next(s for s in estado["fases"]["sesiones"] if s["numero"] == 1)
    assert sesion1["intentos"] == 2
    assert sesion1["estado"] == "completada"
    log = (isolated_dir / po.LOG_FILE).read_text(encoding="utf-8")
    assert "resultado=FALLO" in log
    assert "Cero CSS Inline" in log
    # La lamina corregida quedo escrita sin CSS inline
    lamina = isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker" / "sesion1" / "que-es-docker.blade.php"
    assert 'style="' not in lamina.read_text(encoding="utf-8")


def test_agotamiento_reintentos_aborta_con_codigo_1(run_orchestrator, entorno, isolated_dir, monkeypatch):
    plan = (po.MOCKS_DIR / "plan.txt").read_text(encoding="utf-8")
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(
            secuencia=[plan] + [CONTAMINADA_S1] * 3
        ),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "mock", "--max-retries", "3")

    assert codigo == 1
    estado = json.loads((isolated_dir / po.STATE_FILE).read_text(encoding="utf-8"))
    sesion1 = next(s for s in estado["fases"]["sesiones"] if s["numero"] == 1)
    assert sesion1["estado"] == "fallida"
    assert sesion1["intentos"] == 3
    assert estado["fases"]["zip"]["estado"] == "pendiente"
    assert not (isolated_dir / po.OUTPUT_BASE_DIR / "outputs.zip").exists()
    assert not (isolated_dir / "outputs.zip").exists()


def test_reanudar_tras_agotamiento_completa_la_corrida(run_orchestrator, entorno, isolated_dir, monkeypatch):
    plan = (po.MOCKS_DIR / "plan.txt").read_text(encoding="utf-8")
    s1 = (po.MOCKS_DIR / "sesion1.txt").read_text(encoding="utf-8")
    s2 = (po.MOCKS_DIR / "sesion2.txt").read_text(encoding="utf-8")

    # Corrida inicial: sesion 1 siempre contaminada -> fallida (codigo 1)
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(
            secuencia=[plan, CONTAMINADA_S1, CONTAMINADA_S1, CONTAMINADA_S1]
        ),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--max-retries", "3")
    assert codigo == 1

    # Reanudacion: respuestas validas para sesion 1 y 2 (fallida -> en_curso)
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(secuencia=[s1, s2]),
    )
    codigo, _ = run_orchestrator("resume")
    assert codigo == 0
    assert (isolated_dir / po.OUTPUT_BASE_DIR / "intro_docker" / "sesion2" / "comandos-basicos.blade.php").exists()


def test_backend_no_disponible_aborta_con_codigo_3(run_orchestrator, entorno, monkeypatch):
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.OpenCodeBackend(binario="binario-inexistente-pra"),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md", "--backend", "opencode")

    assert codigo == 3


def test_secuencia_vacia_es_backend_no_disponible(run_orchestrator, entorno, monkeypatch):
    monkeypatch.setattr(
        po, "crear_backend",
        lambda nombre, timeout_s=300: po.MockBackend(secuencia=[]),
    )
    codigo, _ = run_orchestrator("run", "documento_fuente.md")
    assert codigo == 3
