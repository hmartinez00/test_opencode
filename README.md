# Presentation Automator (PRA) v1.0

Sistema de automatización para la generación modular y progresiva de presentaciones interactivas basadas en **Reveal.js**, empaquetadas en plantillas **Blade** para integración en frameworks Laravel.

## Filosofía

El sistema opera bajo el principio de **Plan Maestro + Construcción Progresiva por Sesiones**:

1. **Plan Maestro**: Se analiza un documento fuente y se genera un plan estructurado en JSON que define la presentación completa.
2. **Construcción por Sesiones**: Cada sesión se construye de forma secuencial, generando laminas Blade individuales con sus estilos y scripts asociados.
3. **Empaquetado**: Las sesiones completadas se comprimen en un archivo ZIP listo para integración en Laravel.

## Estructura del Proyecto

```
test_opencode/
├── research_prompts_templates/     # Plantillas maestras de prompts (junction)
│   ├── presentation_plan_meta_prompt.md
│   └── presentation_slide_meta_prompt.md
├── AGENTS.md                       # Directrices para agentes de IA
├── pra_helper.py                   # Motor de automatización (CLI)
├── SESION_PRA_RESUMEN.md           # Documento de contexto de sesión
├── specs/                          # Especificaciones y documentación
│   └── 001-sistema-automatizacion-presentaciones-pra/
│       ├── spec.md                 # Especificación funcional
│       ├── plan.md                 # Contexto técnico
│       ├── research.md             # Research de tecnologías
│       ├── data-model.md           # Modelo de datos y esquemas JSON
│       ├── quickstart.md           # Guía de validación E2E
│       ├── tasks.md                # 19 tareas en 7 fases
│       ├── contracts/
│       │   └── cli-contract.md     # Especificación CLI de pra_helper.py
│       └── checklists/
│           └── requirements.md     # Checklist de requerimientos
└── .specify/
    └── memory/
        └── constitution.md         # Constitución del proyecto
```

## Constitución del Proyecto

Cinco principios fundamentales que rigen el desarrollo:

1. **Cero CSS Inline**: Prohibido el uso de atributos `style="..."` dentro de las laminas Blade
2. **JavaScript Acotado**: Todo script debe estar encapsulado y acotado por lamina
3. **Preservación Determinista del Estado**: Solo `pra_helper.py` tiene permisos de escritura sobre archivos del proyecto generado
4. **Construcción Progresiva Secuencial**: La Sesión N no puede iniciarse hasta completar la Sesión N-1
5. **Documentación en Español**: Toda documentación técnica debe redactarse en español

## Instalación

### Prerrequisitos

- Python 3.10 o superior
- Git
- Acceso a un modelo LLM (GPT-4, Claude, etc.)

### Configuración

```bash
# Clonar el repositorio
git clone https://github.com/hmartinez00/test_opencode.git
cd test_opencode

# Verificar entorno
python --version
python pra_helper.py --help
```

## Uso

### Flujo Completo

```bash
# 1. Inicializar proyecto con documento fuente
python pra_helper.py init documento_fuente.md > prompt_plan.txt

# (Enviar prompt_plan.txt al LLM para generar el JSON del plan)

# 2. Guardar plan maestro
python pra_helper.py save-plan '{"titulo":"...","carpeta_snake_case":"...","idioma":"es",...}'

# 3. Para cada sesión N (empezando por 1):
#    a. Compilar prompt de la sesión
python pra_helper.py prompt-session 1 > prompt_sesion1.txt

#    (Enviar prompt al LLM, recibir respuesta completa)

#    b. Procesar respuesta del LLM
python pra_helper.py process-session 1 "respuesta_completa_del_llm..."

# 4. Repetir paso 3 para cada sesión

# 5. Empaquetar proyecto final
python pra_helper.py zip
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `init <doc>` | Lee documento fuente y genera prompt del Plan Maestro |
| `save-plan <json>` | Guarda plan maestro, inicializa registros y crea estructura |
| `prompt-session <N>` | Compila prompt adaptado para la generación de laminas de la sesión N |
| `process-session <N> <r>` | Procesa respuesta del LLM y escribe archivos Blade |
| `zip` | Empaqueta el proyecto en `outputs.zip` |

### Ejemplo Práctico

```bash
# Crear documento fuente
echo "Contenido sobre automatización de presentaciones" > mi_documento.md

# Inicializar
python pra_helper.py init mi_documento.md > prompt.txt

# Guardar plan (ejemplo con JSON simplificado)
python pra_helper.py save-plan '{
  "titulo": "Mi Presentación",
  "carpeta_snake_case": "mi_presentacion",
  "idioma": "es",
  "resumen_general": "Sistema para generar presentaciones",
  "sesiones": [{
    "numero": 1,
    "titulo": "Introducción",
    "objetivo_pedagogico": "Comprender el sistema",
    "laminas": [{
      "orden": 1,
      "id_kebab_case": "portada",
      "tipo": "portada",
      "objetivo": "Presentar título"
    }]
  }]
}'

# Generar prompt para sesión 1
python pra_helper.py prompt-session 1 > prompt_s1.txt

# Procesar respuesta del LLM
python pra_helper.py process-session 1 "respuesta_del_llm..."

# Empaquetar
python pra_helper.py zip
```

## Formato de Respuesta del LLM

El LLM debe generar una respuesta con 5 bloques delimitados:

```
{{- sesion1/slide-id.blade.php -}}
...contenido Blade...

**BLOQUE 2**
```css
...estilos CSS...
```

**BLOQUE 3**
```javascript
// ...scripts JavaScript...
```

**BLOQUE 4**
<x-slide view="sesion1.slide-id" data-title="Título" />

**BLOQUE 5**
```json
{
  "nuevas_clases": [{"nombre": "...", "proposito": "...", "implementada": true}],
  "clases_materializadas": ["nombre-clase"],
  "nuevos_comportamientos": [{"nombre": "...", "proposito": "...", "implementada": true}],
  "comportamientos_materializados": ["nombre-comportamiento"]
}
```
```

## Esquemas JSON

### PresentationPlan

```json
{
  "titulo": "string",
  "carpeta_snake_case": "string",
  "idioma": "es",
  "resumen_general": "string",
  "sesiones": [
    {
      "numero": 1,
      "titulo": "string",
      "objetivo_pedagogico": "string",
      "laminas": [
        {
          "orden": 1,
          "id_kebab_case": "string-kebab-case",
          "tipo": "portada|contenido|interactiva|cierre",
          "objetivo": "string",
          "insumos": []
        }
      ]
    }
  ]
}
```

### class_registry.json

```json
{
  "clases": [
    {
      "nombre": "clase-css",
      "descripcion": "Propósito de la clase",
      "implementada": true,
      "sesion_creacion": 1
    }
  ]
}
```

### js_registry.json

```json
{
  "comportamientos": [
    {
      "nombre": "comportamiento-js",
      "descripcion": "Propósito del comportamiento",
      "implementada": true,
      "sesion_creacion": 1
    }
  ]
}
```

## Documentación

- **AGENTS.md**: Directrices contextuales para agentes de IA
- **SESION_PRA_RESUMEN.md**: Documento de contexto completo de la sesión de desarrollo
- **specs/**: Especificaciones detalladas del sistema

## Licencia

Proyecto privado - Uso interno.
