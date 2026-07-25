# models/prestamo.py
"""
Paradigma Orientado a Objetos: Entidad Prestamo que vincula Usuario y Libro.
"""

from datetime import date, timedelta
from models.usuario import Usuario
from models.libro import Libro


class Prestamo:
    def __init__(self, usuario: Usuario, libro: Libro, fecha_prestamo: date = None, dias_permitidos: int = None):
        self._usuario = usuario
        self._libro = libro
        self._fecha_prestamo = fecha_prestamo or date.today()
        
        # Si no se especifican días, se usa el cálculo polimórfico del Usuario
        dias = dias_permitidos if dias_permitidos is not None else usuario.obtener_dias_maximos_prestamo()
        self._fecha_devolucion = self._fecha_prestamo + timedelta(days=dias)
        self._devuelto = False

    @property
    def usuario(self) -> Usuario:
        return self._usuario

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def fecha_prestamo(self) -> date:
        return self._fecha_prestamo

    @property
    def fecha_devolucion(self) -> date:
        return self._fecha_devolucion

    @property
    def devuelto(self) -> bool:
        return self._devuelto

    def marcar_devuelto(self) -> None:
        self._devuelto = True
        self._libro.devolver()

    def esta_vencido(self, fecha_referencia: date = None) -> bool:
        if self._devuelto:
            return False
        ref = fecha_referencia or date.today()
        return ref > self._fecha_devolucion

    def dias_restantes(self, fecha_referencia: date = None) -> int:
        ref = fecha_referencia or date.today()
        return (self._fecha_devolucion - ref).days

    def obtener_estado_info(self, fecha_referencia: date = None) -> tuple[str, str]:
        if self._devuelto:
            return "Devuelto", "success"
        dias = self.dias_restantes(fecha_referencia)
        if dias < 0:
            return "Atrasado", "danger"
        elif dias <= 2:
            return "Por vencer", "warning"
        else:
            return "Vigente", "success"

    def calcular_multa(self, tarifa_por_dia: float = 15.0, fecha_referencia: date = None) -> float:
        """Calcula el monto de la penalización por días de atraso."""
        if self._devuelto or not self.esta_vencido(fecha_referencia):
            return 0.0
        dias_atraso = abs(self.dias_restantes(fecha_referencia))
        return dias_atraso * tarifa_por_dia

    def to_dict(self) -> dict:
        return {
            "titulo": self._libro.titulo,
            "autor": self._libro.autor,
            "usuario": self._usuario.nombre,
            "carne": self._usuario.cuenta,
            "tipo_usuario": self._usuario.obtener_tipo(),
            "fecha_prestamo": self._fecha_prestamo.strftime("%Y-%m-%d"),
            "fecha_devolucion": self._fecha_devolucion.strftime("%Y-%m-%d"),
            "esta_vencido": self.esta_vencido(),
            "devuelto": self._devuelto,
        }

    def __repr__(self) -> str:
        return f"<Prestamo: '{self._libro.titulo}' prestado a {self._usuario.nombre}>"
