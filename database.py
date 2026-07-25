# database.py
"""
PARADIGMA 4 - Declarativo: Acceso a datos mediante SQL sobre SQLite.

Aquí describimos QUÉ datos queremos (SELECT ... WHERE ... ORDER BY ...),
no CÓMO recorrer listas manualmente para encontrarlos — eso es lo que
hace declarativo a SQL, a diferencia de un ciclo `for` imperativo.
"""

import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Crea las tablas si todavía no existen. No borra datos existentes."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT UNIQUE NOT NULL,
            autor TEXT NOT NULL,
            anio INTEGER,
            categoria TEXT,
            isbn TEXT,
            disponible INTEGER NOT NULL DEFAULT 1
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cuenta TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            carrera_depto TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_cuenta TEXT NOT NULL,
            libro_titulo TEXT NOT NULL,
            fecha_prestamo TEXT NOT NULL,
            fecha_devolucion TEXT NOT NULL,
            devuelto INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (usuario_cuenta) REFERENCES Usuarios(cuenta),
            FOREIGN KEY (libro_titulo) REFERENCES Libros(titulo)
        );
    """)
    conn.commit()
    conn.close()


# ============================================================
# SINCRONIZACIÓN INICIAL
# ============================================================

def sincronizar_catalogo_inicial(catalogo_libros) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Libros;")
    if cur.fetchone()[0] == 0:
        for l in catalogo_libros:
            cur.execute(
                "INSERT INTO Libros (titulo, autor, anio, categoria, isbn, disponible) VALUES (?, ?, ?, ?, ?, ?);",
                (l.titulo, l.autor, l.anio, l.categoria, l.codigo_isbn, 1),
            )
        conn.commit()
    conn.close()


def sincronizar_usuarios_inicial(usuarios_base) -> None:
    conn = get_connection()
    cur = conn.cursor()
    for u in usuarios_base:
        cur.execute(
            "INSERT OR IGNORE INTO Usuarios (cuenta, nombre, tipo, carrera_depto) VALUES (?, ?, ?, ?);",
            (u.cuenta, u.nombre, u.obtener_tipo(), u.carrera_o_depto),
        )
    conn.commit()
    conn.close()


def cargar_disponibilidad_libros() -> dict:
    """Devuelve {titulo: bool_disponible} desde la BD, para sincronizar el catálogo en memoria."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT titulo, disponible FROM Libros;")
    resultado = {titulo: bool(disp) for titulo, disp in cur.fetchall()}
    conn.close()
    return resultado


def cargar_prestamos_guardados() -> list:
    """Devuelve una lista de dicts con los préstamos guardados en disco."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT usuario_cuenta, libro_titulo, fecha_prestamo, fecha_devolucion, devuelto FROM Prestamos ORDER BY id;")
    filas = cur.fetchall()
    conn.close()
    return [
        {
            "usuario_cuenta": r[0],
            "libro_titulo": r[1],
            "fecha_prestamo": r[2],
            "fecha_devolucion": r[3],
            "devuelto": bool(r[4]),
        }
        for r in filas
    ]


# ============================================================
# OPERACIONES DE ESCRITURA (INSERT / UPDATE / DELETE)
# ============================================================

def registrar_usuario_si_no_existe(usuario) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO Usuarios (cuenta, nombre, tipo, carrera_depto) VALUES (?, ?, ?, ?);",
        (usuario.cuenta, usuario.nombre, usuario.obtener_tipo(), usuario.carrera_o_depto),
    )
    conn.commit()
    conn.close()


def guardar_prestamo(prestamo) -> int:
    """Inserta el préstamo en la BD y devuelve su id generado."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Prestamos (usuario_cuenta, libro_titulo, fecha_prestamo, fecha_devolucion, devuelto) VALUES (?, ?, ?, ?, ?);",
        (
            prestamo.usuario.cuenta,
            prestamo.libro.titulo,
            prestamo.fecha_prestamo.strftime("%Y-%m-%d"),
            prestamo.fecha_devolucion.strftime("%Y-%m-%d"),
            0,
        ),
    )
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def actualizar_disponibilidad_libro(titulo: str, disponible: bool) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Libros SET disponible = ? WHERE titulo = ?;", (1 if disponible else 0, titulo))
    conn.commit()
    conn.close()


def marcar_prestamo_devuelto(usuario_cuenta: str, libro_titulo: str, fecha_prestamo: str) -> None:
    """Marca como devuelto el préstamo más reciente que coincida (aún no devuelto)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE Prestamos SET devuelto = 1
           WHERE id = (
               SELECT id FROM Prestamos
               WHERE usuario_cuenta = ? AND libro_titulo = ? AND fecha_prestamo = ? AND devuelto = 0
               ORDER BY id DESC LIMIT 1
           );""",
        (usuario_cuenta, libro_titulo, fecha_prestamo),
    )
    conn.commit()
    conn.close()


def eliminar_prestamo(usuario_cuenta: str, libro_titulo: str, fecha_prestamo: str) -> None:
    """Elimina el registro de préstamo (usado cuando se elimina desde la interfaz)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """DELETE FROM Prestamos WHERE id = (
               SELECT id FROM Prestamos
               WHERE usuario_cuenta = ? AND libro_titulo = ? AND fecha_prestamo = ?
               ORDER BY id DESC LIMIT 1
           );""",
        (usuario_cuenta, libro_titulo, fecha_prestamo),
    )
    conn.commit()
    conn.close()


# ============================================================
# CONSULTAS DECLARATIVAS 
# ============================================================

SQL_DISPONIBLES = (
    "SELECT titulo, autor, categoria, anio\n"
    "FROM Libros\n"
    "WHERE disponible = 1\n"
    "ORDER BY categoria, titulo;"
)

SQL_VENCIDOS = (
    "SELECT u.nombre, l.titulo, p.fecha_devolucion\n"
    "FROM Prestamos p\n"
    "JOIN Usuarios u ON p.usuario_cuenta = u.cuenta\n"
    "JOIN Libros l ON p.libro_titulo = l.titulo\n"
    "WHERE p.devuelto = 0 AND p.fecha_devolucion < date('now')\n"
    "ORDER BY p.fecha_devolucion ASC;"
)

SQL_MAS_PRESTADO = (
    "SELECT l.categoria, l.titulo, l.autor, COUNT(p.id) AS total_prestamos\n"
    "FROM Prestamos p\n"
    "JOIN Libros l ON p.libro_titulo = l.titulo\n"
    "GROUP BY l.titulo\n"
    "ORDER BY total_prestamos DESC;"
)

SQL_HISTORIAL = (
    "SELECT u.nombre, l.titulo, p.fecha_prestamo, p.fecha_devolucion, p.devuelto\n"
    "FROM Prestamos p\n"
    "JOIN Usuarios u ON p.usuario_cuenta = u.cuenta\n"
    "JOIN Libros l ON p.libro_titulo = l.titulo\n"
    "ORDER BY p.fecha_prestamo DESC;"
)


def ejecutar_consulta(sql_text: str) -> list:
    """Ejecuta cualquiera de las consultas declaradas arriba y devuelve las filas crudas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql_text)
    filas = cur.fetchall()
    conn.close()
    return filas
