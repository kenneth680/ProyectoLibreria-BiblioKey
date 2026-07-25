# P2_Orientado_Objetos/usuario.py
"""
PARADIGMA 2: ORIENTADO A OBJETOS
Encapsulamiento, Herencia y Polimorfismo.
"""

from abc import ABC, abstractmethod


class Usuario(ABC):
    def __init__(self, cuenta: str, nombre: str, carrera_o_depto: str):
        self._cuenta = cuenta          # Atributo protegido (Encapsulamiento)
        self._nombre = nombre
        self._carrera_o_depto = carrera_o_depto
        self._sancionado = False

    @property
    def cuenta(self) -> str:
        return self._cuenta

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def carrera_o_depto(self) -> str:
        return self._carrera_o_depto

    @property
    def sancionado(self) -> bool:
        return self._sancionado

    def sancionar(self) -> None:
        self._sancionado = True

    def levantar_sancion(self) -> None:
        self._sancionado = False

    @abstractmethod
    def obtener_dias_maximos_prestamo(self) -> int:
        """Polimorfismo: Cada subclase define sus días permitidos."""
        pass

    @abstractmethod
    def obtener_tipo(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"<{self.obtener_tipo()}: {self._nombre} (Cuenta: {self._cuenta})>"


class Estudiante(Usuario):
    DIAS_PERMITIDOS_ESTUDIANTE = 7

    def __init__(self, cuenta: str, nombre: str, carrera: str, nivel_academico: str = "Grado"):
        super().__init__(cuenta, nombre, carrera)
        self._nivel_academico = nivel_academico

    def obtener_dias_maximos_prestamo(self) -> int:
        if self._nivel_academico.lower() == "posgrado":
            return self.DIAS_PERMITIDOS_ESTUDIANTE + 3
        return self.DIAS_PERMITIDOS_ESTUDIANTE

    def obtener_tipo(self) -> str:
        return "Estudiante"


class Docente(Usuario):
    DIAS_PERMITIDOS_DOCENTE = 15

    def __init__(self, cuenta: str, nombre: str, departamento: str, categoria: str = "Titular"):
        super().__init__(cuenta, nombre, departamento)
        self._categoria = categoria

    def obtener_dias_maximos_prestamo(self) -> int:
        return self.DIAS_PERMITIDOS_DOCENTE

    def obtener_tipo(self) -> str:
        return "Docente"
