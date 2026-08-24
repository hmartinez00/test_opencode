#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pra_orchestrator.py - Orquestador Automatico del Flujo PRA

Coordina de punta a punta el flujo completo PRA delegando toda mutacion de
artefactos en los comandos CLI de pra_helper.py (caja negra via subprocess):

    run <documento> [--backend mock|opencode] [--max-retries N] [--timeout-s S]
        init -> save-plan -> [prompt-session N -> LLM -> process-session N]*
        -> pytest (calidad) -> zip
    resume   Reanuda una corrida interrumpida desde la ultima fase valida.
    status   Muestra un resumen legible del estado de orquestacion.

Codigos de salida estandar:
    0 exito | 1 validacion incumplida tras reintentos | 2 estado/secuencialidad
    3 backend LLM no disponible | 4 uso incorrecto de la CLI

El orquestador SOLO escribe sus artefactos de control propios:
    - orchestration_state.json  (escritura atomica)
    - orchestration_log.txt     (auditoria append-only)
Ambos quedan fuera de outputs.zip (el motor empaqueta solo el directorio del proyecto).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

ENCODING = "utf-8"
STATE_FILE = "orchestration_state.json"
LOG_FILE = "orchestration_log.txt"
REPO_ROOT = Path(__file__).resolve().parent
HELPER_PATH = REPO_ROOT / "pra_helper.py"
MOCKS_DIR = REPO_ROOT / "mocks_llm"

INLINE_STYLE_PATTERN = re.compile(r'style\s*=\s*["\']')
COVERAGE_ROW_PATTERN = re.compile(r"pra_helper\.py\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)%")
COVERAGE_MINIMA = 85.0
STDERR_MAX_CHARS = 500
# Subdirectorio maestro que aloja todos los proyectos generados (iteracion 004).
# Mismo default y variable de entorno que en pra_helper.py (D-405).
OUTPUT_BASE_DIR = Path(os.environ.get("PRA_OUTPUT_DIR", "output_projects"))

EXIT_OK = 0
EXIT_VALIDACION = 1
EXIT_ESTADO = 2
EXIT_BACKEND = 3
EXIT_USO = 4

ESTADO_PENDIENTE = "pendiente"
ESTADO_EN_CURSO = "en_curso"
ESTADO_COMPLETADA = "completada"
ESTADO_FALLIDA = "fallida"

BACKENDS_VALIDOS = ("mock", "opencode")

TRANSICIONES_VALIDAS = {
    (ESTADO_PENDIENTE, ESTADO_EN_CURSO),
    (ESTADO_EN_CURSO, ESTADO_COMPLETADA),
    (ESTADO_EN_CURSO, ESTADO_FALLIDA),
    (ESTADO_FALLIDA, ESTADO_EN_CURSO),
}


class BackendError(Exception):
    """El backend LLM no pudo generar una respuesta utilizable."""


# ============================================================
# Estado de orquestacion (persistencia atomica) - T302
# ============================================================

def _ahora():
    return datetime.now().isoformat(timespec="seconds")


def _fase_nueva():
    return {"estado": ESTADO_PENDIENTE, "intentos": 0, "ultimo_error": None}


def nuevo_estado(documento, backend, max_reintentos):
    """Construye el estado inicial de una corrida."""
    return {
        "version": "1.0",
        "documento_fuente": str(Path(documento).resolve()),
        "backend": backend,
        "max_reintentos": max_reintentos,
        "iniciada_en": _ahora(),
        "actualizada_en": _ahora(),
        "fases": {
            "init": _fase_nueva(),
            "save_plan": _fase_nueva(),
            "sesiones": [],
            "pytest": _fase_nueva(),
            "zip": _fase_nueva(),
        },
    }


def cargar_estado():
    """Carga orchestration_state.json; None si no existe o esta corrupto."""
    ruta = Path(STATE_FILE)
    if not ruta.exists():
        return None
    try:
        estado = json.loads(ruta.read_text(encoding=ENCODING))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(estado, dict) or not isinstance(estado.get("fases"), dict):
        return None
    return estado


def guardar_estado(estado):
    """Persiste el estado con escritura atomica (archivo temporal + os.replace)."""
    estado["actualizada_en"] = _ahora()
    destino = Path(STATE_FILE)
    fd, tmp = tempfile.mkstemp(dir=str(destino.parent), prefix=".state_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=ENCODING) as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, destino)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def aplicar_transicion(fase, nuevo_estado_txt):
    """Aplica una transicion validandola contra el automata de estados."""
    par = (fase["estado"], nuevo_estado_txt)
    if par not in TRANSICIONES_VALIDAS:
        raise ValueError(f"Transicion invalida: '{par[0]}' -> '{par[1]}'")
    fase["estado"] = nuevo_estado_txt


def iniciar_fase(fase):
    aplicar_transicion(fase, ESTADO_EN_CURSO)


def completar_fase(fase):
    aplicar_transicion(fase, ESTADO_COMPLETADA)


def fallar_fase(fase, error):
    aplicar_transicion(fase, ESTADO_FALLIDA)
    fase["ultimo_error"] = error


def resetear_fase(fase):
    """Normaliza una fase a pendiente (uso exclusivo del flujo resume)."""
    fase["estado"] = ESTADO_PENDIENTE
    fase["intentos"] = 0
    fase["ultimo_error"] = None


def sesion_en_estado(estado, numero):
    """Obtiene (o crea, manteniendo el orden) la entrada de sesion N en el estado."""
    for s in estado["fases"]["sesiones"]:
        if s["numero"] == numero:
            return s
    nueva = {"numero": numero, "estado": ESTADO_PENDIENTE, "intentos": 0, "validaciones": None}
    estado["fases"]["sesiones"].append(nueva)
    estado["fases"]["sesiones"].sort(key=lambda x: x["numero"])
    return nueva


# ============================================================
# Log de auditoria (append-only) - T303
# ============================================================

def registrar_log(fase, intento, resultado, motivo="", duracion_s=0.0):
    linea = (
        f"{datetime.now().isoformat(timespec='milliseconds')} | {fase} | "
        f"intento={intento} | resultado={resultado} | "
        f'motivo="{motivo}" | duracion_s={duracion_s:.2f}\n'
    )
    with open(LOG_FILE, "a", encoding=ENCODING) as f:
        f.write(linea)


# ============================================================
# Utilidades puras
# ============================================================

JSON_FENCE_PATTERN = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def extraer_json(respuesta):
    """Extrae el primer objeto JSON valido de una respuesta LLM."""
    candidatas = [respuesta.strip()]
    candidatas.extend(m.strip() for m in JSON_FENCE_PATTERN.findall(respuesta))
    inicio = respuesta.find("{")
    fin = respuesta.rfind("}")
    if inicio != -1 and fin > inicio:
        candidatas.append(respuesta[inicio : fin + 1])
    for cand in candidatas:
        try:
            obj = json.loads(cand)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def construir_prompt_reflexion(prompt_original, fase_desc, codigo_retorno,
                               validaciones, detalle, intento, max_reintentos):
    """Anexa al prompt original el diagnostico del fallo para el reintento."""
    anexo = [
        "",
        f"## REINTENTO {intento}/{max_reintentos} - DIAGNOSTICO DEL FALLO ANTERIOR",
        f"- Fase: {fase_desc}",
        f"- Codigo de retorno: {codigo_retorno}",
        "- Validaciones incumplidas: "
        + ("; ".join(validaciones) if validaciones else "ninguna declarada"),
        f'- Detalle STDERR: "{(detalle or "").strip()[:STDERR_MAX_CHARS]}"',
        "INSTRUCCION: Corrige UNICAMENTE el problema descrito y regenera "
        "la respuesta COMPLETA con los 5 bloques.",
    ]
    return prompt_original.rstrip() + "\n" + "\n".join(anexo) + "\n"


def parsear_resumen_pytest(salida):
    """Parsea (passed, failed, errores, cobertura_pct) del resumen pytest-cov."""
    cobertura = None
    m = COVERAGE_ROW_PATTERN.search(salida)
    if m:
        cobertura = float(m.group(1))
    resumen = ""
    for linea in reversed(salida.splitlines()):
        if re.search(r"\b(passed|failed|error)", linea):
            resumen = linea
            break
    pm = re.search(r"(\d+)\s+passed", resumen)
    fm = re.search(r"(\d+)\s+failed", resumen)
    em = re.search(r"(\d+)\s+errors?", resumen)
    passed = int(pm.group(1)) if pm else 0
    failed = int(fm.group(1)) if fm else 0
    errores = int(em.group(1)) if em else 0
    return passed, failed, errores, cobertura


# ============================================================
# Backends LLM intercambiables - T304/T305/T306
# ============================================================

class LLMBackend(ABC):
    """Contrato comun de todo backend LLM."""

    @abstractmethod
    def generar(self, prompt, clave=""):
        """Retorna la respuesta textual del LLM para el prompt dado."""


class MockBackend(LLMBackend):
    """Backend determinista: fixtures estaticas o secuencia programada."""

    def __init__(self, fixtures_dir=None, secuencia=None):
        self.fixtures_dir = Path(fixtures_dir) if fixtures_dir else MOCKS_DIR
        self.secuencia = list(secuencia) if secuencia is not None else None

    def generar(self, prompt, clave=""):
        if self.secuencia is not None:
            if not self.secuencia:
                raise BackendError("Secuencia mock agotada")
            return self.secuencia.pop(0)
        ruta = self.fixtures_dir / f"{clave}.txt"
        if not clave or not ruta.exists():
            raise BackendError(
                f"Fixture mock no encontrada: {clave}.txt en {self.fixtures_dir}"
            )
        return ruta.read_text(encoding=ENCODING)


class OpenCodeBackend(LLMBackend):
    """Backend real: invoca la CLI de OpenCode en modo no interactivo."""

    def __init__(self, timeout_s=300, binario="opencode"):
        self.timeout_s = timeout_s
        self.binario = binario

    def generar(self, prompt, clave=""):
        try:
            proc = subprocess.run(
                [self.binario, "run", prompt],
                capture_output=True,
                timeout=self.timeout_s,
            )
        except FileNotFoundError:
            raise BackendError(f"CLI '{self.binario}' no encontrada en PATH")
        except subprocess.TimeoutExpired:
            raise BackendError(f"Timeout de {self.timeout_s}s agotado en backend opencode")
        if proc.returncode != 0:
            stderr_txt = (proc.stderr or b"").decode(ENCODING, errors="replace")
            raise BackendError(
                f"opencode retorno codigo {proc.returncode}: {stderr_txt[:STDERR_MAX_CHARS]}"
            )
        return (proc.stdout or b"").decode(ENCODING, errors="replace")


def crear_backend(nombre, timeout_s=300):
    """Fabrica de backends; lanza BackendError ante nombres desconocidos."""
    if nombre == "mock":
        return MockBackend()
    if nombre == "opencode":
        return OpenCodeBackend(timeout_s=timeout_s)
    raise BackendError(f"Backend desconocido: {nombre}")


# ============================================================
# Delegacion en pra_helper.py y verificacion de calidad - T308
# ============================================================

def run_helper(*args):
    """Invoca un comando CLI de pra_helper.py; retorna (codigo, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(HELPER_PATH), *args],
        capture_output=True,
    )
    out = (proc.stdout or b"").decode(ENCODING, errors="replace")
    err = (proc.stderr or b"").decode(ENCODING, errors="replace")
    return proc.returncode, out, err


def _ejecutar_pytest():
    """Ejecuta la suite con cobertura desde la raiz del repositorio PRA."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--cov=pra_helper",
         "--cov-report=term-missing", "-q"],
        capture_output=True,
        cwd=str(REPO_ROOT),
    )
    out = (proc.stdout or b"").decode(ENCODING, errors="replace")
    return proc.returncode, out


def buscar_proyecto():
    """Localiza el directorio activo buscando presentation_plan.json.
    Prioriza el subdirectorio maestro (OUTPUT_BASE_DIR); si no hay proyectos
    alli, aplica fallback sobre la raiz para proyectos legacy (iteracion 004)."""
    cwd = Path.cwd()
    base = cwd / OUTPUT_BASE_DIR
    scopes = [base] if base == cwd else [base, cwd]
    for scope in scopes:
        if not scope.is_dir():
            continue
        for item in sorted(scope.iterdir()):
            if item.is_dir() and (item / "presentation_plan.json").exists():
                return item
    return None


def sesiones_del_plan():
    """Lee las sesiones del plan guardado ([] si no hay proyecto legible)."""
    project_dir = buscar_proyecto()
    if not project_dir:
        return []
    try:
        plan = json.loads(
            (project_dir / "presentation_plan.json").read_text(encoding=ENCODING)
        )
    except (OSError, json.JSONDecodeError):
        return []
    return plan.get("sesiones", [])


# ============================================================
# Puerta de validacion constitucional post-sesion - T310
# ============================================================

def validar_post_sesion(numero):
    """Puerta post-sesion: exit code, regex anti CSS inline y laminas completas."""
    reporte = {
        "exit_code_ok": True,
        "sin_css_inline": True,
        "laminas_faltantes": [],
        "detalle": "",
    }
    project_dir = buscar_proyecto()
    if not project_dir:
        reporte["sin_css_inline"] = False
        reporte["detalle"] = "No se encontro directorio de proyecto con presentation_plan.json"
        return reporte
    try:
        plan = json.loads(
            (project_dir / "presentation_plan.json").read_text(encoding=ENCODING)
        )
    except (OSError, json.JSONDecodeError) as e:
        reporte["sin_css_inline"] = False
        reporte["detalle"] = f"Error leyendo plan: {e}"
        return reporte
    sesion = next((s for s in plan.get("sesiones", []) if s.get("numero") == numero), None)
    esperadas = [
        lamina.get("id_kebab_case") or lamina.get("id", "")
        for lamina in (sesion or {}).get("laminas", [])
    ]
    sesion_dir = project_dir / f"sesion{numero}"
    presentes = set()
    sufijo_blade = ".blade.php"
    if sesion_dir.exists():
        for blade in sorted(sesion_dir.glob(f"*{sufijo_blade}")):
            presentes.add(blade.name[: -len(sufijo_blade)])
            contenido = blade.read_text(encoding=ENCODING, errors="replace")
            if INLINE_STYLE_PATTERN.search(contenido):
                reporte["sin_css_inline"] = False
                reporte["detalle"] += f"CSS inline detectado en {blade.name}; "
    reporte["laminas_faltantes"] = [lid for lid in esperadas if lid and lid not in presentes]
    return reporte


def reporte_valido(reporte):
    """La puerta se supera solo si todas las validaciones pasan."""
    return (
        reporte["exit_code_ok"]
        and reporte["sin_css_inline"]
        and not reporte["laminas_faltantes"]
    )


# ============================================================
# Motor del bucle de fases - T308/T309/T311
# ============================================================

class Orquestador:
    def __init__(self, backend, max_reintentos=3):
        self.backend = backend
        self.max_reintentos = max_reintentos
        self.prompt_plan = None

    def _log_intento(self, nombre_fase, intento, ok, motivo, t0):
        registrar_log(nombre_fase, intento, "OK" if ok else "FALLO", motivo,
                      time.time() - t0)

    # ---------------- Fase: init ----------------
    def fase_init(self, estado):
        fase = estado["fases"]["init"]
        iniciar_fase(fase)
        fase["intentos"] = 1
        guardar_estado(estado)
        print("[FASE] init: generando prompt del Plan Maestro...")
        t0 = time.time()
        codigo, out, err = run_helper("init", estado["documento_fuente"])
        if codigo != 0:
            detalle = (out.strip() + " " + err.strip()).strip()[:STDERR_MAX_CHARS]
            fallar_fase(fase, detalle)
            guardar_estado(estado)
            self._log_intento("init", 1, False, detalle, t0)
            print("[FASE] init: FALLO")
            return EXIT_ESTADO
        self.prompt_plan = out
        completar_fase(fase)
        guardar_estado(estado)
        self._log_intento("init", 1, True, "", t0)
        print("[FASE] init: OK")
        return EXIT_OK

    # ---------------- Fase: save-plan (con reintentos) ----------------
    def fase_save_plan(self, estado):
        fase = estado["fases"]["save_plan"]
        iniciar_fase(fase)
        guardar_estado(estado)
        print("[FASE] save-plan: solicitando plan maestro al LLM...")
        prompt_base = self.prompt_plan or ""
        prompt_actual = prompt_base
        for intento in range(1, self.max_reintentos + 1):
            fase["intentos"] = intento
            guardar_estado(estado)
            t0 = time.time()
            try:
                respuesta = self.backend.generar(prompt_actual, clave="plan")
            except BackendError as e:
                fallar_fase(fase, str(e))
                guardar_estado(estado)
                self._log_intento("save-plan", intento, False, str(e), t0)
                print(f"[FASE] save-plan: BACKEND NO DISPONIBLE ({e})")
                return EXIT_BACKEND
            plan_json = extraer_json(respuesta)
            if plan_json is None:
                motivo = "La respuesta no contiene un objeto JSON parseable"
                self._log_intento("save-plan", intento, False, motivo, t0)
                prompt_actual = construir_prompt_reflexion(
                    prompt_base, "save-plan", 1, ["JSON malformado"], motivo,
                    intento, self.max_reintentos,
                )
                print(f"[FASE] save-plan: intento {intento} rechazado ({motivo})")
                continue
            codigo, out, err = run_helper(
                "save-plan", json.dumps(plan_json, ensure_ascii=False)
            )
            detalle = (out.strip() + " " + err.strip()).strip()[:STDERR_MAX_CHARS]
            if codigo == 0:
                completar_fase(fase)
                guardar_estado(estado)
                self._log_intento("save-plan", intento, True, "", t0)
                print("[FASE] save-plan: OK")
                return EXIT_OK
            if codigo == 2:
                fallar_fase(fase, detalle)
                guardar_estado(estado)
                self._log_intento("save-plan", intento, False, detalle, t0)
                print(f"[FASE] save-plan: ESQUEMA INVALIDO -> {detalle}")
                return EXIT_ESTADO
            motivo = f"Codigo {codigo} del motor: {detalle}"
            self._log_intento("save-plan", intento, False, motivo, t0)
            prompt_actual = construir_prompt_reflexion(
                prompt_base, "save-plan", codigo,
                ["Plan rechazado por pra_helper"], detalle,
                intento, self.max_reintentos,
            )
            print(f"[FASE] save-plan: intento {intento} rechazado por el motor")
        fallar_fase(fase, "Reintentos agotados sin obtener un plan valido")
        guardar_estado(estado)
        print("[FASE] save-plan: FALLO tras agotar reintentos")
        return EXIT_VALIDACION

    # ---------------- Fase: sesion N (con reintentos y reflexion) ----------------
    def fase_session(self, estado, numero):
        sesion_f = sesion_en_estado(estado, numero)
        iniciar_fase(sesion_f)
        guardar_estado(estado)
        nombre_fase = f"sesion{numero}"
        print(f"[FASE] sesion {numero}: compilando prompt...")
        codigo, out, err = run_helper("prompt-session", str(numero))
        if codigo != 0:
            detalle = (out.strip() + " " + err.strip()).strip()[:STDERR_MAX_CHARS]
            fallar_fase(sesion_f, detalle)
            guardar_estado(estado)
            registrar_log(nombre_fase, 0, "FALLO", detalle, 0.0)
            print(f"[FASE] sesion {numero}: FALLO compilando prompt")
            return EXIT_ESTADO
        prompt_base = out
        prompt_actual = prompt_base
        for intento in range(1, self.max_reintentos + 1):
            sesion_f["intentos"] = intento
            guardar_estado(estado)
            t0 = time.time()
            try:
                respuesta = self.backend.generar(prompt_actual, clave=f"sesion{numero}")
            except BackendError as e:
                fallar_fase(sesion_f, str(e))
                guardar_estado(estado)
                self._log_intento(nombre_fase, intento, False, str(e), t0)
                print(f"[FASE] sesion {numero}: BACKEND NO DISPONIBLE ({e})")
                return EXIT_BACKEND
            codigo, out, err = run_helper("process-session", str(numero), respuesta)
            if codigo == 0:
                reporte = validar_post_sesion(numero)
                sesion_f["validaciones"] = reporte
                guardar_estado(estado)
                if reporte_valido(reporte):
                    completar_fase(sesion_f)
                    guardar_estado(estado)
                    self._log_intento(nombre_fase, intento, True, "", t0)
                    print(f"[FASE] sesion {numero}: OK (intento {intento})")
                    return EXIT_OK
                incumplidas = []
                if not reporte["sin_css_inline"]:
                    incumplidas.append("Cero CSS Inline")
                if reporte["laminas_faltantes"]:
                    incumplidas.append(
                        "Laminas faltantes: " + ", ".join(reporte["laminas_faltantes"])
                    )
                motivo = "; ".join(incumplidas)
                detalle = reporte["detalle"].strip() or motivo
                self._log_intento(nombre_fase, intento, False, motivo, t0)
                prompt_actual = construir_prompt_reflexion(
                    prompt_base, f"process-session {numero}", codigo,
                    incumplidas, detalle, intento, self.max_reintentos,
                )
                print(f"[FASE] sesion {numero}: intento {intento} invalido ({motivo})")
                continue
            detalle = (out.strip() + " " + err.strip()).strip()[:STDERR_MAX_CHARS]
            motivo = f"Codigo {codigo} del motor"
            self._log_intento(nombre_fase, intento, False, f"{motivo}: {detalle}", t0)
            prompt_actual = construir_prompt_reflexion(
                prompt_base, f"process-session {numero}", codigo,
                [motivo], detalle, intento, self.max_reintentos,
            )
            print(f"[FASE] sesion {numero}: intento {intento} rechazado por el motor")
        fallar_fase(sesion_f, "Reintentos agotados sin superar la puerta constitucional")
        guardar_estado(estado)
        print(f"[FASE] sesion {numero}: FALLO tras agotar reintentos")
        return EXIT_VALIDACION


    # ---------------- Fase: pytest (calidad) - T312 ----------------
    def fase_pytest(self, estado):
        fase = estado["fases"]["pytest"]
        iniciar_fase(fase)
        fase["intentos"] = 1
        guardar_estado(estado)
        print("[FASE] pytest: verificando calidad (suite + cobertura)...")
        t0 = time.time()
        codigo, salida = _ejecutar_pytest()
        passed, failed, errores, cobertura = parsear_resumen_pytest(salida)
        motivos = []
        if codigo != 0:
            motivos.append(f"pytest retorno codigo {codigo}")
        if failed or errores:
            motivos.append(f"fallos={failed}, errores={errores}")
        if passed == 0:
            motivos.append("cero pruebas ejecutadas")
        if cobertura is None:
            motivos.append("cobertura de pra_helper no detectable")
        elif cobertura < COVERAGE_MINIMA:
            motivos.append(f"cobertura insuficiente ({cobertura}% < {COVERAGE_MINIMA}%)")
        if motivos:
            detalle = "; ".join(motivos)
            fallar_fase(fase, detalle)
            guardar_estado(estado)
            self._log_intento("pytest", 1, False, detalle, t0)
            print(f"[FASE] pytest: FALLO -> {detalle}")
            return EXIT_VALIDACION
        completar_fase(fase)
        guardar_estado(estado)
        self._log_intento("pytest", 1, True, "", t0)
        print(f"[FASE] pytest: OK (passed={passed}, cobertura={cobertura}%)")
        return EXIT_OK

    # ---------------- Fase: zip (empaquetado) - T312 ----------------
    def fase_zip(self, estado):
        fase = estado["fases"]["zip"]
        iniciar_fase(fase)
        fase["intentos"] = 1
        guardar_estado(estado)
        print("[FASE] zip: empaquetando entregable...")
        t0 = time.time()
        codigo, out, err = run_helper("zip")
        ruta_zip = Path.cwd() / OUTPUT_BASE_DIR / "outputs.zip"
        if codigo != 0 or not ruta_zip.exists():
            detalle = ((out.strip() + " " + err.strip()).strip()
                       or f"outputs.zip no fue generado (codigo {codigo})")[:STDERR_MAX_CHARS]
            fallar_fase(fase, detalle)
            guardar_estado(estado)
            self._log_intento("zip", 1, False, detalle, t0)
            print("[FASE] zip: FALLO")
            return EXIT_VALIDACION
        completar_fase(fase)
        guardar_estado(estado)
        self._log_intento("zip", 1, True, "", t0)
        print("[FASE] zip: OK -> outputs.zip")
        return EXIT_OK

    # ---------------- Pipeline completo (run / resume) ----------------
    def ejecutar_desde_estado(self, estado):
        """Ejecuta las fases pendientes respetando la secuencialidad estricta."""
        fases = estado["fases"]
        if (fases["init"]["estado"] != ESTADO_COMPLETADA
                or fases["save_plan"]["estado"] != ESTADO_COMPLETADA):
            resetear_fase(fases["init"])
            resetear_fase(fases["save_plan"])
            guardar_estado(estado)
            rc = self.fase_init(estado)
            if rc != EXIT_OK:
                return rc
            rc = self.fase_save_plan(estado)
            if rc != EXIT_OK:
                return rc
        numeros = sorted(int(s.get("numero", 0)) for s in sesiones_del_plan())
        if not numeros:
            print("[ERROR] El plan guardado no contiene sesiones.")
            return EXIT_ESTADO
        for n in numeros:
            sesion_f = sesion_en_estado(estado, n)
            if sesion_f["estado"] != ESTADO_COMPLETADA:
                rc = self.fase_session(estado, n)
                if rc != EXIT_OK:
                    return rc
        if fases["pytest"]["estado"] != ESTADO_COMPLETADA:
            rc = self.fase_pytest(estado)
            if rc != EXIT_OK:
                return rc
        if fases["zip"]["estado"] != ESTADO_COMPLETADA:
            rc = self.fase_zip(estado)
            if rc != EXIT_OK:
                return rc
        print("[FIN] Corrida completada: outputs.zip listo para integrarse en Laravel.")
        return EXIT_OK


# ============================================================
# Interfaz CLI - T301/T313
# ============================================================

def setup_utf8():
    """Configura stdout/stderr para UTF-8 en Windows."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=ENCODING, errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=ENCODING, errors="replace")


class ParserOrquestador(argparse.ArgumentParser):
    """ArgumentParser que usa el codigo de salida 4 en errores de uso."""

    def error(self, mensaje):
        self.print_usage(sys.stderr)
        print(f"error: {mensaje}", file=sys.stderr)
        sys.exit(EXIT_USO)


def construir_parser():
    parser = ParserOrquestador(
        prog="pra_orchestrator.py",
        description="Orquestador Automatico del Flujo PRA",
    )
    sub = parser.add_subparsers(dest="comando")

    p_run = sub.add_parser("run", help="Ejecucion desatendida completa del flujo PRA")
    p_run.add_argument("documento", help="Ruta al documento fuente (.md, .txt, ...)")
    p_run.add_argument("--backend", choices=list(BACKENDS_VALIDOS), default="mock",
                       help="Backend LLM a utilizar (default: mock)")
    p_run.add_argument("--max-retries", type=int, default=3,
                       help="Maximo de intentos por fase/sesion (default: 3)")
    p_run.add_argument("--timeout-s", type=int, default=300,
                       help="Timeout del backend opencode en segundos (default: 300)")

    sub.add_parser("resume", help="Reanudar una corrida interrumpida")
    sub.add_parser("status", help="Mostrar el estado actual de orquestacion")
    return parser


def cmd_run(args):
    documento = Path(args.documento)
    if not documento.exists():
        print(f"error: Documento fuente no encontrado: {documento}", file=sys.stderr)
        return EXIT_USO
    if args.max_retries < 1:
        print("error: --max-retries debe ser >= 1", file=sys.stderr)
        return EXIT_USO
    estado = nuevo_estado(documento, args.backend, args.max_retries)
    guardar_estado(estado)
    try:
        backend = crear_backend(args.backend, timeout_s=args.timeout_s)
    except BackendError as e:
        print(f"error: {e}", file=sys.stderr)
        return EXIT_BACKEND
    orquestador = Orquestador(backend, args.max_retries)
    return orquestador.ejecutar_desde_estado(estado)


def cmd_resume(args):
    estado = cargar_estado()
    if estado is None:
        print("error: No hay corrida activa (orchestration_state.json ausente o corrupto)",
              file=sys.stderr)
        return EXIT_ESTADO
    try:
        backend = crear_backend(estado.get("backend", "mock"))
    except BackendError as e:
        print(f"error: {e}", file=sys.stderr)
        return EXIT_BACKEND
    orquestador = Orquestador(backend, int(estado.get("max_reintentos", 3)))
    print("[RESUME] Reanudando corrida desde la ultima fase valida...")
    return orquestador.ejecutar_desde_estado(estado)


def cmd_status(args):
    estado = cargar_estado()
    if estado is None:
        print("error: No hay corrida activa (orchestration_state.json ausente o corrupto)",
              file=sys.stderr)
        return EXIT_ESTADO
    fases = estado["fases"]
    print(f"Corrida: {Path(estado['documento_fuente']).name} "
          f"| backend={estado.get('backend')} | max_reintentos={estado.get('max_reintentos')}")
    print(f"{'Fase':<14}{'Estado':<14}Intentos")
    for nombre in ("init", "save_plan"):
        fase = fases[nombre]
        print(f"{nombre:<14}{fase['estado']:<14}{fase['intentos']}")
    for s in sorted(fases["sesiones"], key=lambda x: x["numero"]):
        print(f"{'sesion ' + str(s['numero']):<14}{s['estado']:<14}{s['intentos']}")
    for nombre in ("pytest", "zip"):
        fase = fases[nombre]
        print(f"{nombre:<14}{fase['estado']:<14}{fase['intentos']}")
    return EXIT_OK


def main(argv=None):
    setup_utf8()
    parser = construir_parser()
    args = parser.parse_args(argv)
    if args.comando == "run":
        return cmd_run(args)
    if args.comando == "resume":
        return cmd_resume(args)
    if args.comando == "status":
        return cmd_status(args)
    parser.print_help(sys.stderr)
    return EXIT_USO


if __name__ == "__main__":
    sys.exit(main())




