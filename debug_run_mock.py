import os, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, r'C:\laragon\www\test_opencode')
import pra_orchestrator as po

# simulate tests fixture: create temp dir and env
base = Path(tempfile.mkdtemp())
print('TMP', base)
os.chdir(base)
(base / 'product_samples' / 'slides').mkdir(parents=True)
os.environ['PRA_OUTPUT_DIR'] = str(base / 'product_samples' / 'slides')

doc = base / 'documento_fuente.md'
doc.write_text('# Introducción a Docker\nContenido de Docker aquí.', encoding='utf-8')
po._ejecutar_pytest = lambda: (0, 'pra_helper.py  320  38  91%\n30 passed in 0.42s\n')

print('START')
rc = po.main(['run', 'documento_fuente.md', '--backend', 'mock'])
print('RC', rc)
print('STATE_EXISTS', (base / po.STATE_FILE).exists())
if (base / po.STATE_FILE).exists():
    print((base / po.STATE_FILE).read_text(encoding='utf-8'))
print('LIST ROOT', sorted(p.name for p in base.iterdir()))
print('LIST BASE', sorted(p.name for p in (base / 'product_samples' / 'slides').iterdir()))
