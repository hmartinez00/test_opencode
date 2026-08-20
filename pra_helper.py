#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pra_helper.py - Motor de Automatizacion Progresiva de Presentaciones PRA
Punto unico de escritura de archivos del proyecto. Todos los agentes de IA
delegan la creacion y mutacion de archivos exclusivamente a este script.

Uso: python pra_helper.py <comando> [argumentos]

Comandos:
  --init <doc>              Inicializa proyecto y genera prompt del Plan Maestro
  --save-plan <json>        Guarda plan maestro e inicializa registros
  --prompt-session <N>      Compila prompt adaptado para la Sesion N
  --process-session <N> <r> Procesa respuesta LLM y escribe archivos
  --zip                     Empaqueta proyecto en outputs.zip
"""

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ENCODING = "utf-8"
JSON_INDENT = 2
SLIDE_TYPES = {"portada", "contenido", "interactiva", "cierre"}
KEBAB_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
FOLDER_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
INLINE_STYLE_PATTERN = re.compile(r'style\s*=\s*["\']')
REGISTRY_CLASS_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


# ============================================================
# Utilidades JSON (T005)
# ============================================================

def load_json(path):
    """Carga un archivo JSON y retorna su contenido."""
    with open(path, encoding=ENCODING) as f:
        return json.load(f)


def save_json(path, data):
    """Guarda datos en formato JSON con indentacion de 2 espacios."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=JSON_INDENT)
        f.write("\n")


def merge_registry(existing, new_entries, key_field="nombre"):
    """Fusiona entradas nuevas en un registro sin duplicar por key_field."""
    existing_keys = {e[key_field] for e in existing}
    added = []
    for entry in new_entries:
        if entry[key_field] not in existing_keys:
            existing.append(entry)
            existing_keys.add(entry[key_field])
            added.append(entry[key_field])
    return added


# ============================================================
# Validaciones (T006 - Cero CSS Inline)
# ============================================================

def validate_no_inline_css(content, slide_id=""):
    """Valida que el contenido no contenga atributos style inline.
    Retorna (es_valido, mensaje_error)."""
    match = INLINE_STYLE_PATTERN.search(content)
    if match:
        return False, (
            f"Violacion de Cero CSS Inline en lamina '{slide_id}': "
            f"se detecto atributo style en posicion {match.start()}"
        )
    return True, ""


def validate_kebab_id(slide_id):
    """Valida que un ID de lamina sea kebab-case valido."""
    return bool(KEBAB_PATTERN.match(slide_id))


def validate_folder_name(name):
    """Valida que un nombre de carpeta sea snake_case valido."""
    return bool(FOLDER_PATTERN.match(name))


def validate_plan_schema(plan):
    """Valida la estructura basica de un PresentationPlan."""
    errors = []
    if not plan.get("titulo"):
        errors.append("Campo 'titulo' requerido o vacio")
    folder = plan.get("carpeta_snake_case") or plan.get("folder_name")
    if not folder:
        errors.append("Campo 'carpeta_snake_case' o 'folder_name' requerido")
    if not plan.get("idioma"):
        errors.append("Campo 'idioma' requerido")
    if not plan.get("resumen_general"):
        errors.append("Campo 'resumen_general' requerido")
    sesiones = plan.get("sesiones", [])
    if not sesiones:
        errors.append("Debe haber al menos una sesion en el plan")
    for i, sesion in enumerate(sesiones):
        if not sesion.get("titulo") and not sesion.get("titulo_sesion"):
            errors.append(f"Sesion {i+1}: titulo requerido")
        laminas = sesion.get("laminas", [])
        if not laminas:
            errors.append(f"Sesion {i+1}: debe tener al menos una lamina")
        for j, lamina in enumerate(laminas):
            lid = lamina.get("id_kebab_case") or lamina.get("id")
            if not lid:
                errors.append(f"Sesion {i+1}, Lamina {j+1}: id requerido")
            elif not validate_kebab_id(lid):
                errors.append(f"Sesion {i+1}, Lamina {j+1}: id '{lid}' no es kebab-case valido")
            if lamina.get("tipo") and lamina["tipo"] not in SLIDE_TYPES:
                errors.append(
                    f"Sesion {i+1}, Lamina {j+1}: tipo '{lamina['tipo']}' "
                    f"no valido (permitidos: {', '.join(SLIDE_TYPES)})"
                )
    return errors


def normalize_plan(plan):
    """Normaliza un plan maestro para usar los nombres de campo del data-model.md."""
    normalized = {
        "titulo": plan.get("titulo", ""),
        "carpeta_snake_case": plan.get("carpeta_snake_case") or plan.get("folder_name", ""),
        "idioma": plan.get("idioma", "es"),
        "resumen_general": plan.get("resumen_general", ""),
        "sesiones": [],
    }
    for sesion in plan.get("sesiones", []):
        s = {
            "numero": sesion.get("numero") or sesion.get("nro", 0),
            "titulo": sesion.get("titulo") or sesion.get("titulo_sesion", ""),
            "objetivo_pedagogico": (
                sesion.get("objetivo_pedagogico")
                or (", ".join(sesion.get("objetivos", [])) if sesion.get("objetivos") else "")
            ),
            "laminas": [],
        }
        for lamina in sesion.get("laminas", []):
            l = {
                "orden": lamina.get("orden", 0),
                "id_kebab_case": lamina.get("id_kebab_case") or lamina.get("id", ""),
                "tipo": lamina.get("tipo", "contenido"),
                "objetivo": lamina.get("objetivo") or lamina.get("objetivo_pedagogico", ""),
                "insumos": lamina.get("insumos", []),
            }
            s["laminas"].append(l)
        normalized["sesiones"].append(s)
    return normalized


def get_project_dir(plan):
    """Retorna el Path del directorio del proyecto segun el plan."""
    folder = plan.get("carpeta_snake_case") or plan.get("folder_name", "")
    return Path.cwd() / folder


# ============================================================
# Comando: --init (T007)
# ============================================================

def cmd_init(args):
    """Inicializa la estructura del proyecto y genera prompt del Plan Maestro."""
    doc_path = Path(args.doc)
    if not doc_path.exists():
        print(json.dumps({"error": f"Documento fuente no encontrado: {doc_path}"}))
        sys.exit(1)

    try:
        content = doc_path.read_text(encoding=ENCODING)
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo documento: {e}"}))
        sys.exit(1)

    prompt_template_path = Path(__file__).parent / "research_prompts_templates" / "presentation_plan_meta_prompt.md"
    if not prompt_template_path.exists():
        prompt_template_path = Path(r"C:\laragon\www\test\test\test_opencode\research_prompts_templates\presentation_plan_meta_prompt.md")
    if prompt_template_path.exists():
        template = prompt_template_path.read_text(encoding=ENCODING)
    else:
        template = "No se encontro la plantilla presentation_plan_meta_prompt.md"

    compiled_prompt = f"{template}\n\n---\n\n**CONTENIDO DEL DOCUMENTO FUENTE:**\n\n{content}"
    print(compiled_prompt)
    sys.exit(0)


# ============================================================
# Comando: --save-plan (T008)
# ============================================================

def cmd_save_plan(args):
    """Guarda el plan maestro e inicializa registros y estructura de carpetas."""
    try:
        plan_raw = json.loads(args.json_plan)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Error de parseo JSON: {e}"}))
        sys.exit(1)

    errors = validate_plan_schema(plan_raw)
    if errors:
        print(json.dumps({"error": "Errores de validacion", "detalles": errors}))
        sys.exit(2)

    plan = normalize_plan(plan_raw)
    project_dir = get_project_dir(plan)

    try:
        project_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(json.dumps({"error": f"Error creando directorio: {e}"}))
        sys.exit(3)

    created_files = []

    plan_path = project_dir / "presentation_plan.json"
    save_json(plan_path, plan)
    created_files.append(str(plan_path))

    class_registry = {"clases": []}
    for sesion in plan["sesiones"]:
        for lamina in sesion.get("laminas", []):
            for clase in lamina.get("clases_css_requeridas", []):
                if isinstance(clase, str):
                    clase = {"nombre": clase, "descripcion": "", "implementada": False, "sesion_creacion": sesion["numero"]}
                elif isinstance(clase, dict):
                    clase.setdefault("implementada", False)
                    clase.setdefault("sesion_creacion", sesion["numero"])
                class_registry["clases"].append(clase)
    class_registry_path = project_dir / "class_registry.json"
    save_json(class_registry_path, class_registry)
    created_files.append(str(class_registry_path))

    js_registry = {"comportamientos": []}
    for sesion in plan["sesiones"]:
        for lamina in sesion.get("laminas", []):
            for comp in lamina.get("comportamientos_js_requeridos", []):
                if isinstance(comp, str):
                    comp = {"nombre": comp, "descripcion": "", "implementada": False, "sesion_creacion": sesion["numero"]}
                elif isinstance(comp, dict):
                    comp.setdefault("implementada", False)
                    comp.setdefault("sesion_creacion", sesion["numero"])
                js_registry["comportamientos"].append(comp)
    js_registry_path = project_dir / "js_registry.json"
    save_json(js_registry_path, js_registry)
    created_files.append(str(js_registry_path))

    manifest_lines = []
    manifest_lines.append("{{-- Manifest de Presentacion - Generado por PRA --}}\n")
    for sesion in plan["sesiones"]:
        num = sesion["numero"]
        titulo = sesion["titulo"]
        manifest_lines.append(f'{{-- Sesion {num}: {titulo} --}}')
        manifest_lines.append(f'<section data-title="{titulo}" data-session="sesion{num}">')
        for lamina in sesion.get("laminas", []):
            lid = lamina["id_kebab_case"]
            data_title = lamina.get("data_title", lamina.get("titulo", lid))
            manifest_lines.append(f'    <x-slide view="sesion{num}.{lid}" data-title="{data_title}" />')
        manifest_lines.append("</section>\n")
    manifest_path = project_dir / "manifest_draft.blade.php"
    manifest_path.write_text("\n".join(manifest_lines), encoding=ENCODING)
    created_files.append(str(manifest_path))

    for sesion in plan["sesiones"]:
        num = sesion["numero"]
        sesion_dir = project_dir / f"sesion{num}"
        sesion_dir.mkdir(parents=True, exist_ok=True)
        created_files.append(str(sesion_dir))

    for folder_name in ["styles_additions", "scripts_additions", "manifest_additions"]:
        folder = project_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        created_files.append(str(folder))

    (project_dir / "styles.blade.php").write_text(
        "{{-- Estilos Acumulados - Generado por PRA --}}\n", encoding=ENCODING
    )
    created_files.append(str(project_dir / "styles.blade.php"))

    (project_dir / "scripts.blade.php").write_text(
        "{{-- Scripts Acumulados - Generado por PRA --}}\n", encoding=ENCODING
    )
    created_files.append(str(project_dir / "scripts.blade.php"))

    result = {
        "status": "exito",
        "proyecto": str(project_dir),
        "archivos_creados": created_files,
        "sesiones_inicializadas": len(plan["sesiones"]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=JSON_INDENT))
    sys.exit(0)


# ============================================================
# Comando: --prompt-session (T010 + T014)
# ============================================================

def find_project_dir():
    """Busca el directorio del proyecto activo buscando presentation_plan.json."""
    cwd = Path.cwd()
    for item in cwd.iterdir():
        if item.is_dir() and (item / "presentation_plan.json").exists():
            return item
    return None


def cmd_prompt_session(args):
    """Compila el prompt adaptado para la generacion de laminas de una sesion."""
    n = args.n
    project_dir = find_project_dir()
    if not project_dir:
        print(json.dumps({"error": "No se encontro directorio de proyecto con presentation_plan.json"}))
        sys.exit(1)

    try:
        plan = load_json(project_dir / "presentation_plan.json")
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo plan: {e}"}))
        sys.exit(3)

    sesion = None
    for s in plan.get("sesiones", []):
        if s.get("numero") == n:
            sesion = s
            break

    if not sesion:
        print(json.dumps({"error": f"Sesion {n} no encontrada en el plan"}))
        sys.exit(1)

    if n > 1:
        prev_exists = any(s.get("numero") == n - 1 for s in plan.get("sesiones", []))
        prev_dir = project_dir / f"sesion{n-1}"
        if prev_exists and not prev_dir.exists():
            print(json.dumps({"error": f"Sesion {n-1} no completada (directorio no existe)"}))
            sys.exit(2)
        if prev_dir.exists():
            blade_files = list(prev_dir.glob("*.blade.php"))
            if not blade_files:
                print(json.dumps({"error": f"Sesion {n-1} no completada (sin laminas Blade generadas)"}))
                sys.exit(2)

    try:
        class_registry = load_json(project_dir / "class_registry.json")
        js_registry = load_json(project_dir / "js_registry.json")
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo registros: {e}"}))
        sys.exit(3)

    slide_template_path = Path(r"C:\laragon\www\test\test\test_opencode\research_prompts_templates\presentation_slide_meta_prompt.md")
    if not slide_template_path.exists():
        slide_template_path = Path(__file__).parent / "research_prompts_templates" / "presentation_slide_meta_prompt.md"

    if slide_template_path.exists():
        template = slide_template_path.read_text(encoding=ENCODING)
    else:
        template = "Plantilla presentation_slide_meta_prompt.md no encontrada"

    session_number = sesion["numero"]
    session_title = sesion["titulo"]
    project_title = plan.get("titulo", "")
    folder_name = plan.get("carpeta_snake_case", "")
    objetivos = sesion.get("objetivo_pedagogico", "")
    laminas_json = json.dumps(sesion.get("laminas", []), ensure_ascii=False, indent=JSON_INDENT)
    classes_implemented = [c for c in class_registry.get("clases", []) if c.get("implementada")]
    classes_pending = [c for c in class_registry.get("clases", []) if not c.get("implementada")]
    js_implemented = [j for j in js_registry.get("comportamientos", []) if j.get("implementada")]
    js_pending = [j for j in js_registry.get("comportamientos", []) if not j.get("implementada")]

    compiled = template
    compiled = compiled.replace("{{session_number}}", str(session_number))
    compiled = compiled.replace("{{session_title}}", session_title)
    compiled = compiled.replace("{{project_title}}", project_title)
    compiled = compiled.replace("{{folder_name}}", folder_name)
    compiled = compiled.replace("{{objetivos}}", objetivos)
    compiled = compiled.replace("{{laminas_json}}", laminas_json)
    compiled = compiled.replace(
        "{{class_registry_actual}}",
        json.dumps({"implementadas": classes_implemented, "pendientes": classes_pending}, ensure_ascii=False, indent=JSON_INDENT)
    )
    compiled = compiled.replace(
        "{{js_registry_actual}}",
        json.dumps({"implementados": js_implemented, "pendientes": js_pending}, ensure_ascii=False, indent=JSON_INDENT)
    )

    print(compiled)
    sys.exit(0)


# ============================================================
# Comando: --process-session (T011 + T012 + T016)
# ============================================================

def parse_llm_response(response_text):
    """Parsea la respuesta del LLM en 5 bloques delimitados."""
    blocks = {
        "laminas": [],
        "estilos_css": "",
        "scripts_js": "",
        "manifest_entries": [],
        "registry_updates": {"nuevas_clases": [], "clases_materializadas": [],
                             "nuevos_comportamientos": [], "comportamientos_materializados": []},
    }

    blade_pattern = re.compile(
        r"\{\{-+\s*sesion\d+/([\w-]+)\.blade\.php\s*-+\}\}\s*\n(.*?)(?=\{\{-+\s*sesion\d+/|\*\*BLOQUE\s+[2345]|$)",
        re.DOTALL
    )
    for match in blade_pattern.finditer(response_text):
        slide_id = match.group(1)
        content = match.group(2).strip()
        blocks["laminas"].append({"id": slide_id, "content": content})

    css_pattern = re.compile(r"```css\s*\n(.*?)```", re.DOTALL)
    css_match = css_pattern.search(response_text)
    if css_match:
        blocks["estilos_css"] = css_match.group(1).strip()

    js_pattern = re.compile(r"```javascript\s*\n(.*?)```", re.DOTALL)
    js_match = js_pattern.search(response_text)
    if js_match:
        blocks["scripts_js"] = js_match.group(1).strip()

    manifest_pattern = re.compile(r"<x-slide\s+[^>]*view=\"([^\"]+)\"[^>]*(?:data-title=\"([^\"]+)\")?[^>]*/>")
    for m in manifest_pattern.finditer(response_text):
        view = m.group(1)
        data_title = m.group(2) or ""
        blocks["manifest_entries"].append({"view": view, "data_title": data_title})

    registry_pattern = re.compile(r"```json\s*\n(\{[^`]*\"nuevas_clases\"[^`]*)\```", re.DOTALL)
    reg_match = registry_pattern.search(response_text)
    if reg_match:
        try:
            reg_data = json.loads(reg_match.group(1))
            blocks["registry_updates"] = {
                "nuevas_clases": reg_data.get("nuevas_clases", []),
                "clases_materializadas": reg_data.get("clases_materializadas", []),
                "nuevos_comportamientos": reg_data.get("nuevos_comportamientos", []),
                "comportamientos_materializados": reg_data.get("comportamientos_materializados", []),
            }
        except json.JSONDecodeError:
            pass

    return blocks


def cmd_process_session(args):
    """Procesa la respuesta del LLM y escribe archivos de la sesion."""
    n = args.n
    response_text = args.respuesta_llm
    project_dir = find_project_dir()

    if not project_dir:
        print(json.dumps({"error": "No se encontro directorio de proyecto"}))
        sys.exit(4)

    try:
        plan = load_json(project_dir / "presentation_plan.json")
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo plan: {e}"}))
        sys.exit(4)

    sesion = None
    for s in plan.get("sesiones", []):
        if s.get("numero") == n:
            sesion = s
            break

    if not sesion:
        print(json.dumps({"error": f"Sesion {n} no encontrada en el plan"}))
        sys.exit(1)

    blocks = parse_llm_response(response_text)

    if not blocks["laminas"]:
        print(json.dumps({"error": "No se pudieron parsear laminas de la respuesta LLM"}))
        sys.exit(1)

    violations = []
    created_files = []
    sesion_dir = project_dir / f"sesion{n}"
    sesion_dir.mkdir(parents=True, exist_ok=True)

    for lamina in blocks["laminas"]:
        slide_id = lamina["id"]
        content = lamina["content"]
        is_valid, error_msg = validate_no_inline_css(content, slide_id)
        if not is_valid:
            violations.append(error_msg)
            continue
        blade_path = sesion_dir / f"{slide_id}.blade.php"
        blade_path.write_text(content, encoding=ENCODING)
        created_files.append(str(blade_path))

    if violations:
        print(json.dumps({
            "error": "Violaciones de Cero CSS Inline detectadas",
            "violaciones": violations,
        }))
        sys.exit(2)

    css_content = blocks.get("estilos_css", "")
    if css_content:
        styles_path = project_dir / "styles.blade.php"
        existing_styles = styles_path.read_text(encoding=ENCODING) if styles_path.exists() else ""
        styles_path.write_text(existing_styles + "\n" + css_content + "\n", encoding=ENCODING)
        created_files.append(str(styles_path))

        styles_additions = project_dir / "styles_additions" / f"sesion{n}_styles.css"
        styles_additions.write_text(css_content, encoding=ENCODING)
        created_files.append(str(styles_additions))

    js_content = blocks.get("scripts_js", "")
    if js_content:
        scripts_path = project_dir / "scripts.blade.php"
        existing_scripts = scripts_path.read_text(encoding=ENCODING) if scripts_path.exists() else ""
        scripts_path.write_text(existing_scripts + "\n" + js_content + "\n", encoding=ENCODING)
        created_files.append(str(scripts_path))

        scripts_additions = project_dir / "scripts_additions" / f"sesion{n}_scripts.js"
        scripts_additions.write_text(js_content, encoding=ENCODING)
        created_files.append(str(scripts_additions))

    class_registry_path = project_dir / "class_registry.json"
    js_registry_path = project_dir / "js_registry.json"

    try:
        class_registry = load_json(class_registry_path)
        js_registry = load_json(js_registry_path)
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo registros: {e}"}))
        sys.exit(3)

    reg_updates = blocks.get("registry_updates", {})
    added_classes = []

    for nueva in reg_updates.get("nuevas_clases", []):
        entry = {
            "nombre": nueva.get("nombre", ""),
            "descripcion": nueva.get("proposito") or nueva.get("descripcion", ""),
            "implementada": nueva.get("implementada", True),
            "sesion_creacion": n,
        }
        if entry["nombre"]:
            class_registry["clases"].append(entry)
            added_classes.append(entry["nombre"])

    for mat_name in reg_updates.get("clases_materializadas", []):
        for clase in class_registry["clases"]:
            if clase["nombre"] == mat_name:
                clase["implementada"] = True
                break

    added_js = []
    for nuevo in reg_updates.get("nuevos_comportamientos", []):
        entry = {
            "nombre": nuevo.get("nombre", ""),
            "descripcion": nuevo.get("proposito") or nuevo.get("descripcion", ""),
            "implementada": nuevo.get("implementada", True),
            "sesion_creacion": n,
        }
        if entry["nombre"]:
            js_registry["comportamientos"].append(entry)
            added_js.append(entry["nombre"])

    for mat_name in reg_updates.get("comportamientos_materializados", []):
        for comp in js_registry["comportamientos"]:
            if comp["nombre"] == mat_name:
                comp["implementada"] = True
                break

    save_json(class_registry_path, class_registry)
    save_json(js_registry_path, js_registry)
    created_files.append(str(class_registry_path))
    created_files.append(str(js_registry_path))

    manifest_entries = blocks.get("manifest_entries", [])
    if manifest_entries:
        manifest_lines = [f"{{-- Manifest Sesion {n} - Generado por PRA --}}\n"]
        for entry in manifest_entries:
            view = entry["view"]
            data_title = entry["data_title"]
            manifest_lines.append(f'<x-slide view="{view}" data-title="{data_title}" />')
        manifest_additions = project_dir / "manifest_additions" / f"sesion{n}.blade.php"
        manifest_additions.write_text("\n".join(manifest_lines) + "\n", encoding=ENCODING)
        created_files.append(str(manifest_additions))

        manifest_draft = project_dir / "manifest_draft.blade.php"
        if manifest_draft.exists():
            existing_manifest = manifest_draft.read_text(encoding=ENCODING)
            new_section = f"\n{{-- Sesion {n} completada --}}\n"
            for entry in manifest_entries:
                new_section += f'<x-slide view="{entry["view"]}" data-title="{entry["data_title"]}" />\n'
            manifest_draft.write_text(existing_manifest + new_section, encoding=ENCODING)
            created_files.append(str(manifest_draft))

    result = {
        "status": "exito",
        "sesion_procesada": n,
        "archivos_creados": created_files,
        "laminas_escritas": len(blocks["laminas"]),
        "clases_agregadas": added_classes,
        "comportamientos_agregados": added_js,
        "violaciones_css_inline": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=JSON_INDENT))
    sys.exit(0)


# ============================================================
# Comando: --zip (T017)
# ============================================================

def cmd_zip(args):
    """Empaqueta el proyecto activo en un archivo outputs.zip."""
    project_dir = find_project_dir()
    if not project_dir:
        print(json.dumps({"error": "No se encontro directorio de proyecto"}))
        sys.exit(1)

    try:
        plan = load_json(project_dir / "presentation_plan.json")
    except Exception as e:
        print(json.dumps({"error": f"Error leyendo plan: {e}"}))
        sys.exit(1)

    has_completed = False
    for sesion in plan.get("sesiones", []):
        num = sesion.get("numero", 0)
        sesion_dir = project_dir / f"sesion{num}"
        if sesion_dir.exists() and list(sesion_dir.glob("*.blade.php")):
            has_completed = True
            break

    if not has_completed:
        print(json.dumps({"error": "No hay sesiones completadas para empaquetar"}))
        sys.exit(1)

    zip_path = Path.cwd() / "outputs.zip"
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_dir.parent)
                    zf.write(file_path, arcname)
    except Exception as e:
        print(json.dumps({"error": f"Error creando ZIP: {e}"}))
        sys.exit(2)

    result = {
        "status": "exito",
        "archivo": str(zip_path),
        "tamano_bytes": zip_path.stat().st_size,
    }
    print(json.dumps(result, ensure_ascii=False, indent=JSON_INDENT))
    sys.exit(0)


# ============================================================
# Punto de Entrada Principal
# ============================================================

def setup_utf8():
    """Configura stdout para usar UTF-8 en Windows."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=ENCODING, errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=ENCODING, errors="replace")


def main():
    setup_utf8()
    parser = argparse.ArgumentParser(
        description="pra_helper.py - Motor de Automatizacion PRA"
    )
    subparsers = parser.add_subparsers(dest="comando")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("doc", help="Ruta al documento fuente")

    save_parser = subparsers.add_parser("save-plan")
    save_parser.add_argument("json_plan", help="JSON con el plan maestro")

    prompt_parser = subparsers.add_parser("prompt-session")
    prompt_parser.add_argument("n", type=int, help="Numero de sesion")

    process_parser = subparsers.add_parser("process-session")
    process_parser.add_argument("n", type=int, help="Numero de sesion")
    process_parser.add_argument("respuesta_llm", help="Respuesta completa del LLM")

    subparsers.add_parser("zip")

    args = parser.parse_args()

    if args.comando == "init":
        cmd_init(args)
    elif args.comando == "save-plan":
        cmd_save_plan(args)
    elif args.comando == "prompt-session":
        cmd_prompt_session(args)
    elif args.comando == "process-session":
        cmd_process_session(args)
    elif args.comando == "zip":
        cmd_zip(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
