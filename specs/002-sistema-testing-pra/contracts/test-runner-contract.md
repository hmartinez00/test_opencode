# Contrato del Ejecutor de Pruebas (Test Runner Contract)

**Especificación de Interfaz de Pruebas para PRA**

---

## Comandos de Ejecución Estándar

### 1. Ejecución Completa de la Suite
```bash
pytest
```
- **Entrada**: Todos los archivos en `tests/` matching `test_*.py`.
- **Salida**: Resumen de ejecución en consola.
- **Código de Salida**: `0` si todos los tests pasan, `!= 0` si alguno falla.

### 2. Ejecución con Reporte de Cobertura
```bash
pytest --cov=pra_helper --cov-report=term-missing
```
- **Salida**: Tabla de cobertura por líneas y porcentaje global de `pra_helper.py`.
- **Criterio de Aceptación**: Porcentaje total de cobertura ≥ 85%.

### 3. Ejecución Aislada por Categorías
```bash
# Pruebas Unitarias únicamente
pytest tests/unit/

# Pruebas de Integración CLI únicamente
pytest tests/integration/

# Pruebas de Reglas Constitucionales únicamente
pytest tests/constitutional/
```

---

## Contrato de Fixtures Compartidas (`conftest.py`)

| Fixture | Tipo | Propósito / Garantía |
|---------|------|----------------------|
| `isolated_dir` | Autouse/Scope: function | Crea un `tmp_path`, cambia `os.chdir` a él y restaura el directorio al finalizar |
| `sample_markdown_doc` | Factory / Function | Retorna la ruta de un archivo Markdown fuente válido de prueba |
| `sample_plan_json_str` | Function | Retorna una cadena JSON válida del plan maestro |
| `sample_llm_response_s1` | Function | Retorna una respuesta LLM válida formateada en 5 bloques para la Sesión 1 |
| `sample_invalid_llm_response_inline_css` | Function | Retorna una respuesta LLM contaminada con `style="..."` para tests negativos |
