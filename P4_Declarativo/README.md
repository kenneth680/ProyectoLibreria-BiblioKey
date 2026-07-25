# Paradigma 4 — Declarativo

## ¿Qué es?
El **paradigma declarativo** es un modelo donde el programador describe
**qué** datos quiere obtener (una condición, una relación, un orden),
sin especificar **cómo** recorrer las estructuras para encontrarlos.
El motor que ejecuta la consulta (en este caso, el motor SQL de SQLite)
decide la forma de resolverla.

El ejemplo de referencia de este paradigma es **SQL**, y es lo que se
implementó de forma real en este proyecto: un módulo dedicado
(`database.py`) ejecuta consultas SQL contra una base de datos SQLite
que persiste en disco (`biblioteca.db`), en lugar de simular los datos
con listas de Python recorridas manualmente.

## Archivos del paradigma

| Archivo | Descripción |
|---|---|
| `database.py` | Acceso a datos: conexión SQLite, creación de tablas, consultas SQL declarativas |
| `biblioteca.db` | Archivo de base de datos generado automáticamente (persistente entre ejecuciones) |

## Principios aplicados

### Persistencia real en SQLite
A diferencia de las listas en memoria (`LISTA_PRESTAMOS`, `CATALOGO_LIBROS`),
los datos guardados en `biblioteca.db` **sobreviven** aunque se cierre el
programa. Al volver a abrir la aplicación, `database.py` reconstruye el
estado desde el archivo en disco.

```python
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
```

### Esquema de la base de datos

| Tabla | Columnas principales |
|---|---|
| `Libros` | `titulo`, `autor`, `anio`, `categoria`, `isbn`, `disponible` |
| `Usuarios` | `cuenta`, `nombre`, `tipo`, `carrera_depto` |
| `Prestamos` | `usuario_cuenta`, `libro_titulo`, `fecha_prestamo`, `fecha_devolucion`, `devuelto` |

`Prestamos` se relaciona con `Usuarios` y `Libros` mediante llaves foráneas
(`usuario_cuenta`, `libro_titulo`), lo que permite hacer `JOIN` reales
entre las tres tablas.

### Consultas declarativas reales
En vez de un `for` que recorre y compara manualmente, se **declara** la
condición y el motor SQL la resuelve:

```python
SQL_VENCIDOS = (
    "SELECT u.nombre, l.titulo, p.fecha_devolucion\n"
    "FROM Prestamos p\n"
    "JOIN Usuarios u ON p.usuario_cuenta = u.cuenta\n"
    "JOIN Libros l ON p.libro_titulo = l.titulo\n"
    "WHERE p.devuelto = 0 AND p.fecha_devolucion < date('now')\n"
    "ORDER BY p.fecha_devolucion ASC;"
)

def ejecutar_consulta(sql_text: str) -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql_text)
    filas = cur.fetchall()
    conn.close()
    return filas
```

### Consultas disponibles en el sistema

| Consulta | Constante en `database.py` | Uso |
|---|---|---|
| Libros disponibles | `SQL_DISPONIBLES` | `SELECT ... WHERE disponible = 1` |
| Préstamos vencidos | `SQL_VENCIDOS` | `JOIN` + `WHERE fecha_devolucion < date('now')` |
| Más prestado por categoría | `SQL_MAS_PRESTADO` | `JOIN` + `GROUP BY` + `ORDER BY` |
| Historial completo | `SQL_HISTORIAL` | `JOIN` de las 3 tablas ordenado por fecha |

### Operaciones de escritura
Cada acción de la interfaz que crea, entrega o elimina un préstamo
también actualiza la base de datos, para mantenerla sincronizada con
lo que se ve en pantalla:

```python
database.guardar_prestamo(p)                                   # INSERT
database.actualizar_disponibilidad_libro(libro.titulo, False)  # UPDATE
database.marcar_prestamo_devuelto(cuenta, titulo, fecha)       # UPDATE
database.eliminar_prestamo(cuenta, titulo, fecha)               # DELETE
```

## Archivos relacionados (en el proyecto)
- [`database.py`](../database.py)

---

# Extensión — Paradigma Reactivo

## ¿Qué es?
Como complemento al paradigma declarativo, el proyecto incluye un segundo
enfoque emparentado: el **paradigma reactivo**, aplicado a eventos en
lugar de a datos estáticos. El flujo del programa está determinado por
*eventos* (acciones del usuario, cambios de estado, etc.) en lugar de por
una secuencia lineal predefinida. Usa el patrón **Publicador/Suscriptor
(Observer)** para desacoplar componentes: en vez de indicar paso a paso
qué hacer cuando algo cambia, se **declara de antemano** una relación
entre un evento y su reacción, y esa reacción se dispara sola cuando el
evento ocurre.

## Archivos del paradigma

| Archivo | Descripción |
|---|---|
| `event_bus.py` | Bus global de eventos pub/sub |

## Principios aplicados

### EventBus — Publicador/Suscriptor
Cualquier módulo puede **publicar** un evento sin saber quién lo escucha.
Cualquier módulo puede **suscribirse** sin importar quién lo publicó:

```python
# Publicar evento (emisor no conoce a los suscriptores)
bus_global.publish("PRESTAMO_CREADO", {"prestamo": p.to_dict()})

# Suscribirse a un evento (suscriptor no conoce al emisor)
bus_global.subscribe("PRESTAMO_CREADO", lambda data: print(f"Nuevo: {data}"))
```

### Eventos del sistema BiblioKEY

| Evento | Cuándo se dispara | Datos adjuntos |
|---|---|---|
| `PRESTAMO_CREADO` | Al registrar un nuevo préstamo | `{prestamo: dict}` |
| `LIBRO_DEVUELTO` | Al marcar un préstamo como entregado | `{prestamo: dict}` |
| `MORA_DETECTADA` | Al detectar un libro vencido | `{prestamo: dict}` |

### Desacoplamiento reactivo
```
UI (form) ──publish──▶ EventBus ──notify──▶ Logger / Contador / Alerta
                                  ──notify──▶ Motor estadístico
                                  ──notify──▶ Sistema de multas
```

### Relación con el paradigma declarativo
Ambos paradigmas comparten la misma filosofía de fondo — *declarar una
relación en vez de programar los pasos* — pero se aplican a dominios
distintos: SQL (`database.py`) declara relaciones sobre **datos
persistentes**, mientras que el EventBus (`event_bus.py`) declara
relaciones sobre **eventos que ocurren en el tiempo**.

## Archivos relacionados (en el proyecto)
- [`event_bus.py`](../events/event_bus.py)
