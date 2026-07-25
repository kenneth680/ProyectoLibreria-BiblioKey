# P3_Funcional/functional_engine.py
"""
PARADIGMA 3: PROGRAMACION FUNCIONAL
Inmutabilidad, filter, map, reduce, lambdas y recursividad sobre estructuras jerárquicas.
"""

from functools import reduce
from typing import List, Dict, Any


def obtener_prestamos_vencidos(lista_prestamos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aísla inmutablemente préstamos en mora usando filter + lambda."""
    return list(filter(lambda p: p.get("esta_vencido", False), lista_prestamos))


def obtener_libros_por_categoria(lista_libros: List[Dict[str, Any]], categoria: str) -> List[Dict[str, Any]]:
    """Filtra libros de una categoría específica sin alterar el catálogo."""
    return list(filter(lambda l: l.get("categoria") == categoria, lista_libros))


def formatear_catalogo_para_reporte(lista_libros: List[Dict[str, Any]]) -> List[str]:
    """Transforma dicts de libros a cadenas usando map + lambda."""
    return list(map(
        lambda l: f"{l['titulo']} - {l['autor']} [{l['categoria']}]",
        lista_libros
    ))


def calcular_total_dias_mora(lista_prestamos: List[Dict[str, Any]]) -> int:
    """Suma total de días en mora utilizando reduce + lambda."""
    vencidos = obtener_prestamos_vencidos(lista_prestamos)
    return reduce(
        lambda acumulador, p: acumulador + p.get("dias_mora", 1),
        vencidos,
        0
    )


def total_prestamos_recursivo(nodo_jerarquico: Dict[str, Any]) -> int:
    """
    Recorre recursivamente una estructura jerárquica (Facultad -> Departamentos -> Carreras)
    sumando préstamos acumulados.
    """
    total = nodo_jerarquico.get("prestamos", 0)
    for departamento in nodo_jerarquico.get("departamentos", []):
        total += total_prestamos_recursivo(departamento)
    for carrera in nodo_jerarquico.get("carreras", []):
        total += total_prestamos_recursivo(carrera)
    return total
