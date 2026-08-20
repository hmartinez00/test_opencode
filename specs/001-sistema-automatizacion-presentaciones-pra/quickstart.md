# Guia de Validacion y Arranque Rapido: Sistema PRA

**Funcionalidad**: [Especificacion](./spec.md) | **Plan**: [Plan de Implementacion](./plan.md)

## Requisitos Previos

- Python 3.11+ instalado y disponible en PATH.
- Acceso a un LLM operativo desde OpenCode.
- Documento fuente de ejemplo (cualquier formato soportado: .md, .txt, .ipynb, .pdf).
- Directorio de trabajo limpio en `C:\laragon\www\test\test\test_opencode\`.

---

## Escenario de Prueba 1: Flujo Completo de la Sesion 1

### Paso 1: Inicializacion del proyecto

```bash
python pra_helper.py --init mi_documento_fuente.md
```

**Resultado esperado**:
- Se crea la carpeta del proyecto (ej. `mi_documento_fuente/`).
- Se imprime en STDOUT el prompt compilado del Plan Maestro en formato Markdown.

### Paso 2: Guardado del plan maestro

Tomar la respuesta JSON del LLM generada a partir del prompt del Paso 1 y ejecutar:

```bash
python pra_helper.py --save-plan '{"titulo":"Mi Presentacion","carpeta_snake_case":"mi_presentacion","idioma":"es","resumen_general":"...","sesiones":[{"numero":1,"titulo":"Sesion 1","objetivo_pedagogico":"...","laminas":[{"orden":1,"id_kebab_case":"intro","tipo":"portada","objetivo":"..."}]}]}'
```

**Resultado esperado**:
- Se crea `presentation_plan.json`.
- Se crean `class_registry.json` y `js_registry.json` con entradas iniciales.
- Se crean las subcarpetas `sesion1/`, `styles_additions/`, `scripts_additions/`, `manifest_additions/`.
- Se crea `manifest_draft.blade.php`.

### Paso 3: Compilacion del prompt de la Sesion 1

```bash
python pra_helper.py --prompt-session 1
```

**Resultado esperado**:
- Se imprime en STDOUT el prompt compilado con el contexto de la Sesion 1, laminas a generar, clases/registros existentes y plantilla maestra.

### Paso 4: Procesamiento de la respuesta LLM de la Sesion 1

Tomar la respuesta del LLM generada a partir del prompt del Paso 3 y ejecutar:

```bash
python pra_helper.py --process-session 1 "<respuesta_llm_completa>"
```

**Resultado esperado**:
- Se crean los archivos `sesion1/[slide-id].blade.php` por cada lamina.
- Se acumulan estilos en `styles.blade.php`.
- Se acumulan scripts en `scripts.blade.php`.
- Se crean respaldos en `styles_additions/` y `scripts_additions/`.
- Se actualizan `class_registry.json` y `js_registry.json` con `implementada: true`.
- Se crea `manifest_additions/sesion1.blade.php`.
- Se actualiza `manifest_draft.blade.php`.
- No se detectan violaciones de Cero CSS inline.

### Paso 5: Empaquetado

```bash
python pra_helper.py --zip
```

**Resultado esperado**:
- Se crea `outputs.zip` en la raiz del directorio de trabajo.
- El archivo contiene toda la estructura del proyecto.

---

## Escenario de Prueba 2: Validacion de Cumplimiento Constitucional

### Prueba de Cero CSS inline

Despues de ejecutar la Sesion 1 (Paso 4), ejecutar una busqueda regex en todos los archivos `.blade.php` de laminas:

```bash
grep -r 'style="' sesion1/
```

**Resultado esperado**: Sin resultados. Ningun archivo Blade contiene atributos `style="..."`.

### Prueba de Secuencialidad

Intentar compilar el prompt de la Sesion 2 sin haber completado la Sesion 1:

```bash
python pra_helper.py --prompt-session 2
```

**Resultado esperado**: Codigo de retorno `2` con mensaje de error indicando que la sesion anterior no esta completada.

---

## Escenario de Prueba 3: Verificacion de Registros

Despues de ejecutar la Sesion 1, verificar que los registros se actualizaron correctamente:

```bash
python -c "import json; data=json.load(open('class_registry.json')); print([c['nombre'] for c in data['clases'] if c['implementada']])"
```

**Resultado esperado**: Lista de clases que fueron implementadas en la Sesion 1.

```bash
python -c "import json; data=json.load(open('js_registry.json')); print([j['nombre'] for j in data['comportamientos'] if j['implementada']])"
```

**Resultado esperado**: Lista de comportamientos que fueron implementados en la Sesion 1.

---

## Referencias

- [Contrato CLI de pra_helper.py](./contracts/cli-contract.md): Especificacion detallada de cada comando.
- [Modelo de Datos](./data-model.md): Estructura de entidades y esquemas JSON.
- [Decisiones de Diseno](./research.md): Justificacion de las decisiones arquitectonicas.
