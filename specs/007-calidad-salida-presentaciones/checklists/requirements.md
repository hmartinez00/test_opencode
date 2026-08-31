# Checklist de Requisitos: Calidad de Salida de Presentaciones PRA

## Especificacion

- [ ] La spec documenta los 6 problemas detectados (P1-P6) con su causa.
- [ ] Se definen historias de usuario con prueba independiente y escenarios de aceptacion.
- [ ] Se definen criterios de exito verificables.
- [ ] Se documentan los casos extremos.

## Interpolacion de ruta (P1)

- [ ] `manifest.blade.php` usa `{$presentation->folder_name}`.
- [ ] `assets/styles.blade.php` usa `{$presentation->folder_name}`.
- [ ] `assets/scripts.blade.php` usa `{$presentation->folder_name}`.
- [ ] No existe `{{$presentation->folder_name}}` en los tres archivos.
- [ ] La interpolacion no aparece duplicada ni con llaves anidadas.

## Envoltura de assets (P2, P3)

- [ ] Cada `assets/styles_blade/css/*.blade.php` inicia con `<style>` y termina con `</style>`.
- [ ] Cada `assets/styles_blade/js/*.blade.php` inicia con `<script>` y termina con `</script>`.
- [ ] `consolidate` repetido no duplica la envoltura (idempotencia).
- [ ] Los fragmentos no quedan con doble envoltura.

## Respuesta por archivo (P4)

- [ ] `process-session N --respuesta-file <ruta>` procesa la respuesta del archivo.
- [ ] El posicional puede omitirse cuando se usa `--respuesta-file`.
- [ ] Se documenta y aplica la precedencia (archivo sobre posicional).
- [ ] `run_helper` usa archivo temporal para respuestas largas.
- [ ] El archivo temporal se limpia en `finally`.
- [ ] Respuesta larga (> 33000 chars) se procesa sin `WinError 206`.

## Seleccion de proyecto (P5)

- [ ] `PRA_ACTIVE_PROJECT` prioriza el proyecto indicado.
- [ ] Sin la variable, se conserva el comportamiento actual.
- [ ] Carpeta indicada inexistente -> fallback seguro.
- [ ] Aplicado en `pra_helper.py` y `pra_orchestrator.py`.

## Titulo de lamina (P6)

- [ ] Se usa `data_title`/`titulo` del plan cuando existe.
- [ ] Se deriva titulo legible cuando falta.
- [ ] El id crudo no se usa como `data-title` del manifest.

## Constitucion

- [ ] No existe CSS inline en las vistas finales.
- [ ] Los comportamientos JS estan acotados a sus laminas.
- [ ] Las escrituras se realizan a traves de `pra_helper.py`.
- [ ] Se conserva el orden plan-first.
- [ ] La documentacion nueva esta en espanol.

## Pruebas (TDD)

- [ ] Existen pruebas unitarias de `titulo_legible`.
- [ ] Existen pruebas unitarias de interpolacion.
- [ ] Existen pruebas de envoltura e idempotencia.
- [ ] Existen pruebas de `--respuesta-file` (corto y largo).
- [ ] Existen pruebas de `PRA_ACTIVE_PROJECT` (2 proyectos).
- [ ] Existe prueba E2E de `consolidate` con nuevos asserts.
- [ ] La suite completa pasa.
- [ ] La cobertura de ambos modulos es >= 85%.
