# Checklist de Requisitos: Consolidacion de Presentaciones PRA

## Especificacion

- [ ] La spec define el problema de alineamiento entre artefactos PRA y producto Laravel.
- [ ] Se define la fase `consolidate` dentro del flujo.
- [ ] Se distingue el estado interno del producto final.
- [ ] Se definen criterios de aceptacion independientes.

## Manifest

- [ ] Se genera un unico `manifest.blade.php`.
- [ ] El manifest usa layout y secciones Blade validas.
- [ ] Las laminas aparecen una sola vez y en orden del plan.
- [ ] Se normalizan referencias `sesionN` a `sessionN`.
- [ ] Se generan referencias `global.nombre` cuando corresponda.
- [ ] Se rechazan comentarios Blade invalidos.

## Directorios y assets

- [ ] Las vistas de sesiones se ubican en `sessionN/`.
- [ ] Las vistas compartidas se ubican en `global/`.
- [ ] Existe `assets/styles.blade.php`.
- [ ] Existe `assets/scripts.blade.php`.
- [ ] Los fragmentos CSS y JS se ubican bajo `assets/styles_blade/`.
- [ ] Todos los includes apuntan a archivos existentes.

## Constitucion

- [ ] No existe CSS inline en las vistas finales.
- [ ] Los comportamientos JS estan acotados a sus laminas.
- [ ] Las escrituras se realizan a traves de `pra_helper.py`.
- [ ] Se conserva el orden plan-first.
- [ ] La documentacion nueva esta en espanol.

## Orquestacion y ZIP

- [ ] `consolidate` se ejecuta antes de `pytest` y `zip`.
- [ ] `resume` puede reintentar la consolidacion.
- [ ] Un fallo de consolidacion bloquea el empaquetado.
- [ ] `outputs.zip` contiene la estructura consolidada.
- [ ] `outputs.zip` no se incluye a si mismo.
- [ ] Los artefactos de control quedan fuera del ZIP.

## Pruebas

- [ ] Existen pruebas unitarias de normalizacion.
- [ ] Existen pruebas de manifest y duplicados.
- [ ] Existen pruebas de assets.
- [ ] Existen pruebas de validaciones constitucionales.
- [ ] Existe prueba E2E de `run` y `resume`.
- [ ] La suite completa pasa.
- [ ] La cobertura de ambos modulos es >= 85%.
