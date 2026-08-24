# -*- coding: utf-8 -*-
import os
import sys
import json
from unittest import mock
import pytest
from pathlib import Path

# Iteracion 004: los modulos resuelven OUTPUT_BASE_DIR al importar; se limpia
# la variable ANTES de importar para garantizar el default en toda la suite.
os.environ.pop("PRA_OUTPUT_DIR", None)

import pra_helper

ENCODING = "utf-8"

@pytest.fixture(autouse=True)
def salida_maestra_por_defecto(monkeypatch):
    """Iteracion 004: cada prueba corre con el subdirectorio maestro por defecto."""
    monkeypatch.delenv("PRA_OUTPUT_DIR", raising=False)

@pytest.fixture(autouse=True)
def isolated_dir(tmp_path, monkeypatch):
    """Fixture que cambia el CWD a un directorio temporal para cada prueba y lo restaura."""
    monkeypatch.chdir(tmp_path)
    return tmp_path

@pytest.fixture(autouse=True)
def disable_setup_utf8(monkeypatch):
    """Neutraliza setup_utf8() para que capsys pueda capturar STDOUT sin interferencias."""
    monkeypatch.setattr(pra_helper, "setup_utf8", lambda: None)
    try:
        import pra_orchestrator
        monkeypatch.setattr(pra_orchestrator, "setup_utf8", lambda: None)
    except ImportError:
        pass

@pytest.fixture
def run_cli(capsys):
    """Ejecuta el punto de entrada main() de pra_helper.py con argumentos simulados.
    Drena capsys en cada invocacion y retorna (codigo_salida, stdout)."""
    def _run(*argv):
        with mock.patch.object(sys, "argv", ["pra_helper.py", *argv]):
            with pytest.raises(SystemExit) as exc_info:
                pra_helper.main()
        captured = capsys.readouterr()
        return exc_info.value.code, captured.out
    return _run

@pytest.fixture
def run_orchestrator(capsys):
    """Ejecuta el punto de entrada main() de pra_orchestrator.py con argumentos simulados.
    Drena capsys en cada invocacion y retorna (codigo_salida, stdout)."""
    import pra_orchestrator
    def _run(*argv):
        with mock.patch.object(sys, "argv", ["pra_orchestrator.py", *argv]):
            try:
                codigo = pra_orchestrator.main()
            except SystemExit as e:
                codigo = e.code
        captured = capsys.readouterr()
        return codigo, captured.out
    return _run

@pytest.fixture
def sample_markdown_doc(isolated_dir):
    """Fixture que crea un documento fuente Markdown de prueba."""
    doc_path = isolated_dir / "documento_fuente.md"
    doc_path.write_text("# Introducción a Docker\nContenido de Docker aquí.", encoding=ENCODING)
    return doc_path

@pytest.fixture
def sample_plan_json_str():
    """Retorna una cadena JSON de plan maestro válida."""
    plan = {
        "titulo": "Introducción a Docker",
        "carpeta_snake_case": "intro_docker",
        "idioma": "es",
        "resumen_general": "Curso básico de Docker",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "Conceptos Básicos",
                "objetivo_pedagogico": "Aprender contenedores",
                "laminas": [
                    {
                        "orden": 1,
                        "id_kebab_case": "que-es-docker",
                        "tipo": "portada",
                        "objetivo": "Introducción general",
                        "clases_css_requeridas": ["text-center", "docker-blue"],
                        "comportamientos_js_requeridos": ["ripple-effect"]
                    },
                    {
                        "orden": 2,
                        "id_kebab_case": "arquitectura",
                        "tipo": "contenido",
                        "objetivo": "Explicar daemon y cliente"
                    }
                ]
            },
            {
                "numero": 2,
                "titulo": "Uso Práctico",
                "objetivo_pedagogico": "Ejecutar comandos",
                "laminas": [
                    {
                        "orden": 1,
                        "id_kebab_case": "comandos-basicos",
                        "tipo": "contenido",
                        "objetivo": "Mostrar docker run"
                    }
                ]
            }
        ]
    }
    return json.dumps(plan, ensure_ascii=False)

@pytest.fixture
def sample_llm_response_s1():
    """Retorna una respuesta LLM simulada válida de la Sesión 1 con los 5 bloques requeridos."""
    return """Aquí está la generación de las láminas para la sesión 1:

{{- sesion1/que-es-docker.blade.php -}}
<div class="text-center docker-blue">
    <h1>¿Qué es Docker?</h1>
    <p>Docker es una plataforma de contenedores.</p>
</div>

{{- sesion1/arquitectura.blade.php -}}
<div class="slide-architecture">
    <h2>Arquitectura de Docker</h2>
    <p>Cliente, Host y Registro.</p>
</div>

**BLOQUE 2**
```css
.docker-blue {
    color: #2496ed;
}
.slide-architecture {
    padding: 20px;
}
```

**BLOQUE 3**
```javascript
// Lamina que-es-docker
document.addEventListener('DOMContentLoaded', () => {
    console.log("Docker slide loaded");
});
```

**BLOQUE 4**
<x-slide view="sesion1.que-es-docker" data-title="¿Qué es Docker?" />
<x-slide view="sesion1.arquitectura" data-title="Arquitectura" />

**BLOQUE 5**
```json
{
  "nuevas_clases": [
    {"nombre": "docker-blue", "proposito": "Color oficial de Docker", "implementada": true},
    {"nombre": "slide-architecture", "proposito": "Estilos de slide de arquitectura", "implementada": true}
  ],
  "clases_materializadas": ["docker-blue", "slide-architecture"],
  "nuevos_comportamientos": [
    {"nombre": "ripple-effect", "proposito": "Efecto click", "implementada": true}
  ],
  "comportamientos_materializados": ["ripple-effect"]
}
```
"""

@pytest.fixture
def sample_invalid_llm_response_inline_css():
    """Retorna una respuesta LLM que viola la regla de Cero CSS Inline."""
    return """Aquí está la generación de la sesión 1 con CSS inline:

{{- sesion1/que-es-docker.blade.php -}}
<div style="color: red;">
    <h1>¿Qué es Docker?</h1>
</div>

**BLOQUE 2**
```css
/* vacío */
```

**BLOQUE 3**
```javascript
// vacío
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
