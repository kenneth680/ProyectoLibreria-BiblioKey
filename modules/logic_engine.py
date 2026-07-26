# modules/logic_engine.py
"""
Paradigma Lógico (Declarativo / Motor de Inferencia).
Permite definir Hechos y Reglas para resolver consultas lógicas
mediante evaluación de condiciones.
"""

from typing import Dict, List, Set, Any


class FactsDB:
    def __init__(self):
        # Hechos: conjuntos de tuplas (relacion, *argumentos)
        self._facts: Set[tuple] = set()

    def add_fact(self, relation: str, *args) -> None:
        self._facts.add((relation, *args))

    def remove_fact(self, relation: str, *args) -> None:
        self._facts.discard((relation, *args))

    def has_fact(self, relation: str, *args) -> bool:
        return (relation, *args) in self._facts

    def query(self, relation: str) -> List[tuple]:
        return [f[1:] for f in self._facts if f[0] == relation]


class LogicEngine:
    """Motor de Inferencia Lógica de Biblioteca Universitaria."""

    def __init__(self):
        self.db = FactsDB()
        self._cargar_hechos_iniciales()

    def _cargar_hechos_iniciales(self):
        # Hechos base: (cuenta, tipo, esta_en_mora, prestamos_activos)
        self.db.add_fact("limite_libros", "Estudiante", 3)
        self.db.add_fact("limite_libros", "Docente", 5)
        self.db.add_fact("categoria_restringida", "Reserva Especial")

    def registrar_usuario_hecho(self, cuenta: str, tipo: str, prestamos_activos: int, en_mora: bool):
        self.db.add_fact("usuario", cuenta, tipo)
        self.db.add_fact("prestamos_activos", cuenta, prestamos_activos)
        if en_mora:
            self.db.add_fact("en_mora", cuenta)
        else:
            self.db.remove_fact("en_mora", cuenta)

    # -------------------------------------------------------------------
    # REGLAS LOGICAS DE DEDUCCION
    # -------------------------------------------------------------------

    def es_libre_de_mora(self, cuenta: str) -> bool:
        """Regla: libre_de_mora(X) :- \+ en_mora(X)."""
        return not self.db.has_fact("en_mora", cuenta)

    def tiene_cupo_disponible(self, cuenta: str, tipo_usuario: str, prestamos_actuales: int) -> bool:
        """
        Regla: tiene_cupo_disponible(Cuenta) :-
            limite_libros(Tipo, Max), Actuales < Max.
        """
        limite = 3 if tipo_usuario == "Estudiante" else 5
        return prestamos_actuales < limite

    def es_categoria_permitida(self, tipo_usuario: str, categoria_libro: str) -> bool:
        """
        Regla: categoria_permitida(Estudiante, Cat) :- \+ categoria_restringida(Cat).
        categoria_permitida(Docente, _).
        """
        if tipo_usuario == "Docente":
            return True
        return not self.db.has_fact("categoria_restringida", categoria_libro)

    def evaluar_elegibilidad_prestamo(self, cuenta: str, tipo_usuario: str,
                                      prestamos_actuales: int, en_mora: bool,
                                      categoria_libro: str) -> tuple[bool, str]:
        """
        Inferencia Lógica Compuesta:
        puede_prestar(Cuenta, Libro) :-
            libre_de_mora(Cuenta),
            tiene_cupo_disponible(Cuenta),
            categoria_permitida(Tipo, Categoria).
        """
        if en_mora or not self.es_libre_de_mora(cuenta):
            return False, "Deducción Lógica: Usuario bloqueado por estar en MORA."

        if not self.tiene_cupo_disponible(cuenta, tipo_usuario, prestamos_actuales):
            limite = 3 if tipo_usuario == "Estudiante" else 5
            return False, f"Deducción Lógica: Excedió el límite máximo de {limite} préstamos para {tipo_usuario}."

        if not self.es_categoria_permitida(tipo_usuario, categoria_libro):
            return False, f"Deducción Lógica: La categoría '{categoria_libro}' está restringida para estudiantes."

        return True, "Deducción Lógica: Préstamo AUTORIZADO según reglas de inferencia."

    def exportar_a_prolog(self, filepath: str = "rules/reglas_biblioteca.pl") -> str:
        """Genera/Actualiza dinámicamente el archivo de conocimiento en formato Prolog."""
        contenido = [
            "% Base de Conocimiento exportada desde LogicEngine",
            "% Paradigma Lógico Integrado",
            ""
        ]
        for relacion, *args in self.db._facts:
            args_str = ", ".join(f"'{a}'" if isinstance(a, str) else str(a) for a in args)
            contenido.append(f"{relacion}({args_str}).")
        return "\n".join(contenido)
