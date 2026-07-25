# P2_Orientado_Objetos/libro.py
"""
PARADIGMA 2: ORIENTADO A OBJETOS (POO)
Entidad Libro con métodos para manipular disponibilidad.
"""


class Libro:
    def __init__(self, titulo: str, autor: str, anio: int, categoria: str, codigo_isbn: str = ""):
        self._titulo = titulo
        self._autor = autor
        self._anio = anio
        self._categoria = categoria
        self._codigo_isbn = codigo_isbn or f"ISBN-{abs(hash(titulo)) % 100000:05d}"
        self._disponible = True

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def autor(self) -> str:
        return self._autor

    @property
    def anio(self) -> int:
        return self._anio

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def codigo_isbn(self) -> str:
        return self._codigo_isbn

    @property
    def disponible(self) -> bool:
        return self._disponible

    def prestar(self) -> None:
        self._disponible = False

    def devolver(self) -> None:
        self._disponible = True

    def to_dict(self) -> dict:
        return {
            "titulo": self._titulo,
            "autor": self._autor,
            "anio": self._anio,
            "categoria": self._categoria,
            "isbn": self._codigo_isbn,
            "disponible": self._disponible,
        }

    def __repr__(self) -> str:
        return f"<Libro: '{self._titulo}' de {self._autor} ({self._categoria})>"
