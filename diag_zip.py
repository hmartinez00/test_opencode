import json, os, tempfile, sys
from pathlib import Path
sys.path.insert(0, r'C:\laragon\www\test_opencode')
import pra_helper

tmp = Path(tempfile.mkdtemp())
os.chdir(tmp)
base = tmp / 'product_samples' / 'slides'
base.mkdir(parents=True)
os.environ['PRA_OUTPUT_DIR'] = str(base)
plan = {
    'titulo': 'Introducción a Docker',
    'carpeta_snake_case': 'intro_docker',
    'idioma': 'es',
    'resumen_general': 'Curso básico',
    'sesiones': [
        {
            'numero': 1,
            'titulo': 'Conceptos Básicos',
            'objetivo_pedagogico': 'Aprender',
            'laminas': [
                {'orden':1,'id_kebab_case':'que-es-docker','tipo':'portada','objetivo':'Intro','clases_css_requeridas':['text-center','docker-blue'],'comportamientos_js_requeridos':['ripple-effect']},
                {'orden':2,'id_kebab_case':'arquitectura','tipo':'contenido','objetivo':'Explicar','clases_css_requeridas':['slide-architecture'],'comportamientos_js_requeridos':[]}
            ]
        }
    ]
}

sys.argv=['pra_helper.py', 'save-plan', json.dumps(plan)]
try:
    pra_helper.main()
except SystemExit as e:
    print('save_exit', e.code)

resp = '''Aquí está la generación de las láminas para la sesión 1:
{{- sesion1/que-es-docker.blade.php -}}
<div class="text-center docker-blue"><h1>¿Qué es Docker?</h1></div>

{{- sesion1/arquitectura.blade.php -}}
<div class="slide-architecture"><h2>Arquitectura</h2></div>

**BLOQUE 2**
```css
.docker-blue { color: #2496ed; }
.slide-architecture { padding: 20px; }
```

**BLOQUE 3**
```javascript
// Lamina que-es-docker
document.addEventListener('DOMContentLoaded', () => { console.log("Docker slide loaded"); });
```

**BLOQUE 4**
<x-slide view="sesion1.que-es-docker" data-title="¿Qué es Docker?" />
<x-slide view="sesion1.arquitectura" data-title="Arquitectura" />

**BLOQUE 5**
```json
{
  "nuevas_clases": [{"nombre": "docker-blue", "proposito": "Color oficial de Docker", "implementada": true},{"nombre": "slide-architecture", "proposito": "Estilo arquitectura", "implementada": true}],
  "clases_materializadas": ["docker-blue", "slide-architecture"],
  "nuevos_comportamientos": [{"nombre": "ripple-effect", "proposito": "Efecto click", "implementada": true}],
  "comportamientos_materializados": ["ripple-effect"]
}
'''

sys.argv=['pra_helper.py', 'process-session', '1', resp]
try:
    pra_helper.main()
except SystemExit as e:
    print('proc_exit', e.code)

print('ROOT_ITEMS', [x.name for x in tmp.iterdir()])
print('BASE_ITEMS', [x.name for x in base.iterdir()])
print('PROJ_ITEMS', [x.name for x in (base/'intro_docker').iterdir()])

sys.argv=['pra_helper.py', 'zip']
try:
    pra_helper.main()
except SystemExit as e:
    print('zip_exit', e.code)

print('ZIP_EXISTS', (base/'intro_docker'/'outputs.zip').exists())
print('ZIP_SIZE', (base/'intro_docker'/'outputs.zip').stat().st_size if (base/'intro_docker'/'outputs.zip').exists() else 'N/A')
