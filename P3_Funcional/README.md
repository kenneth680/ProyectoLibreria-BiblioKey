# Paradigma 3 — Funcional

## ¿Qué es?
El **paradigma funcional** trata la computación como la evaluación de funciones
matemáticas puras. Sus pilares son: **inmutabilidad**, **funciones puras** (sin
efectos secundarios), y el uso de **funciones de orden superior** como `map`,
`filter` y `reduce`.

## Archivos del paradigma

| Archivo | Descripción |
|---|---|
| `functional_engine.py` | Motor analítico con funciones puras |

## Principios aplicados

### Funciones Puras e Inmutabilidad
Las funciones nunca modifican los datos de entrada; retornan nuevas colecciones:
```python
def obtener_prestamos_vencidos(prestamos: list[dict]) -> list[dict]:
    """Filter puro — no modifica la lista original."""
    return list(filter(lambda p: p.get("esta_vencido", False), prestamos))
```

### Funciones de Orden Superior
- **`filter`** → seleccionar libros disponibles / préstamos vencidos
- **`map`** → transformar estructuras de datos para reportes
- **`reduce`** → acumular contadores y estadísticas

```python
from functools import reduce

def total_prestamos_recursivo(prestamos: list[dict], acum: int = 0) -> int:
    """Recursividad pura para contar sin variables mutables."""
    if not prestamos:
        return acum
    return total_prestamos_recursivo(prestamos[1:], acum + 1)
```

### Lambdas
```python
categorias_unicas = list(set(map(lambda p: p["categoria"], prestamos)))
```

## Archivos relacionados (en el proyecto)
- [`functional_engine.py`](../modules/functional_engine.py)
