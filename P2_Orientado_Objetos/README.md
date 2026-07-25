# Paradigma 2 — Orientado a Objetos (POO)

## ¿Qué es?
El **paradigma orientado a objetos** organiza el software en torno a *objetos*
que encapsulan datos (atributos) y comportamiento (métodos). Los pilares
aplicados en BiblioKEY son: **Encapsulamiento**, **Herencia** y **Polimorfismo**.

## Archivos del paradigma

| Archivo | Clase principal | Descripción |
|---|---|---|
| `usuario.py` | `Usuario`, `Estudiante`, `Docente` | Jerarquía de usuarios con herencia |
| `libro.py` | `Libro` | Entidad con atributos encapsulados |
| `prestamo.py` | `Prestamo` | Vincula `Usuario` + `Libro` con lógica de negocio |

## Principios aplicados

### Encapsulamiento
Todos los atributos son privados (`_atributo`) y se exponen vía `@property`:
```python
class Libro:
    def __init__(self, titulo, autor, anio, categoria):
        self._titulo = titulo        # privado
        self._disponible = True

    @property
    def titulo(self) -> str:        # acceso controlado
        return self._titulo
```

### Herencia y Polimorfismo
`Estudiante` y `Docente` heredan de la clase abstracta `Usuario` y sobrescriben
`obtener_dias_maximos_prestamo()` de forma diferente (polimorfismo):
```python
class Estudiante(Usuario):
    def obtener_dias_maximos_prestamo(self) -> int:
        return 7   # 7 días

class Docente(Usuario):
    def obtener_dias_maximos_prestamo(self) -> int:
        return 30  # 30 días
```

## Archivos relacionados (en el proyecto)
- [`usuario.py`](../models/usuario.py)
- [`libro.py`](../models/libro.py)
- [`prestamo.py`](../models/prestamo.py)
