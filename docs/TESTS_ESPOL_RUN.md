# Ejecución de la suite de tests — módulo AGV (ESPOL)

- **Fecha:** 27-oct-2026 · Ejecutada por el lead (Aion CLI) en Docker
- **Comando:** `docker run --rm -v ./agv-espol:/work -w /work python:3.11-slim bash -c "pip install -q -r requirements.txt pytest && PYTHONPATH=. python -m pytest tests -q"`
- **Resultado:** ✅ **171 passed + 93 subtests passed, 0 fallos** (10,19 s)

## Nota
- `pytest` no estaba en `requirements.txt` (se instaló junto a las deps en el contenedor).
- El host local falla por dependencias ausentes (Streamlit) — por eso se ejecuta en contenedor efímero.
- Conteo previo (grep): 171 funciones `def test_` en 15 archivos — coincide con la ejecución real.

## Cifra combinada del monorepo
**260 tests, todos en verde**: 89/89 (gemelo nestlink) + 171/171 (módulo AGV de ESPOL).
