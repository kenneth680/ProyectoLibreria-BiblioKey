# Paradigma 1 — Imperativo / Procedimental

## ¿Qué es?
El **paradigma imperativo** describe el *cómo* se resuelve un problema mediante
secuencias ordenadas de instrucciones que modifican el estado del programa paso
a paso. El flujo de control es explícito: secuencias, condicionales y ciclos.

## Dónde se aplica en BiblioKEY

| Archivo principal | Rol en el sistema |
|---|---|
| `app_gui.py` | Punto de entrada e interfaz gráfica principal |
| `main.py` | Script de demostración en consola |

## Principios aplicados
- **Secuencia**: el sistema inicializa catálogo → usuarios → préstamos en orden
- **Selección**: `if/elif/else` para controlar flujo de registro y navegación
- **Iteración**: `for` para recorrer préstamos, libros y renderizar la UI
- **Estado mutable**: `LISTA_PRESTAMOS`, `CATALOGO_LIBROS` se actualizan directamente

## Ejemplo de código (app_gui.py)
```python
# Flujo imperativo: secuencia de pasos para registrar un préstamo
def ejecutar_registro():
    cuenta = entry_cuenta.get().strip()   # 1) Leer entrada
    fecha_prestamo = datetime.strptime(fecha_str, "%d/%m/%Y").date()  # 2) Parsear
    libro = next((l for l in CATALOGO_LIBROS if l.titulo == titulo), None)  # 3) Buscar
    p = Prestamo(u, libro, fecha_prestamo=fecha_prestamo)  # 4) Crear
    LISTA_PRESTAMOS.append(p)   # 5) Mutar estado
    libro.prestar()             # 6) Actualizar
```

## Archivos relacionados (en el proyecto)
- [`app_gui.py`](../app_gui.py)
- [`main.py`](../main.py)
