# modules/functional_engine.py
"""
Paradigma Funcional - Motor Analítico e Inmutable de Biblioteca Universitaria.
Principios Clave:
1. Inmutabilidad: Ninguna función modifica las colecciones originales; retornan colecciones nuevas.
2. Funciones de Orden Superior: filter, map, reduce con expresiones lambda.
3. Funciones Puras: Salida determinada únicamente por las entradas, sin efectos secundarios.
4. Recursividad: Recorrido de estructuras jerárquicas (Facultad -> Departamento -> Carrera).
"""

from functools import reduce
from typing import List, Dict, Any


# ------------------------------------------------------------------
# 1. FILTER + LAMBDA (Funciones puras de filtrado)
# ------------------------------------------------------------------
def obtener_prestamos_vencidos(lista_prestamos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aísla inmutablemente préstamos en mora usando filter + lambda."""
    return list(filter(lambda p: p.get("esta_vencido", False), lista_prestamos))


def obtener_libros_por_categoria(lista_libros: List[Dict[str, Any]], categoria: str) -> List[Dict[str, Any]]:
    """Filtra libros de una categoría específica sin alterar el catálogo."""
    return list(filter(lambda l: l.get("categoria") == categoria, lista_libros))


# ------------------------------------------------------------------
# 2. MAP + LAMBDA (Transformación de datos)
# ------------------------------------------------------------------
def formatear_catalogo_para_reporte(lista_libros: List[Dict[str, Any]]) -> List[str]:
    """Transforma dicts de libros a cadenas 'Título - Autor [Categoría]'."""
    return list(map(
        lambda l: f"{l['titulo']} - {l['autor']} [{l['categoria']}]",
        lista_libros
    ))


def extraer_titulos_unicos(lista_prestamos: List[Dict[str, Any]]) -> List[str]:
    """Transforma préstamos a títulos usando map y luego deduplica funcionalmente."""
    titulos = list(map(lambda p: p.get("titulo", ""), lista_prestamos))
    return list(set(titulos))


# ------------------------------------------------------------------
# 3. REDUCE + LAMBDA (Agregación de Métricas)
# ------------------------------------------------------------------
def calcular_total_dias_mora(lista_prestamos: List[Dict[str, Any]]) -> int:
    """Suma total de días en mora utilizando reduce + lambda."""
    vencidos = obtener_prestamos_vencidos(lista_prestamos)
    return reduce(
        lambda acumulador, p: acumulador + p.get("dias_mora", 1),
        vencidos,
        0
    )


# ------------------------------------------------------------------
# 4. RECURSIVIDAD (Estructuras Jerárquicas Complejas)
# ------------------------------------------------------------------
def total_prestamos_recursivo(nodo_jerarquico: Dict[str, Any]) -> int:
    """
    Recorre recursivamente una estructura jerárquica (Facultad -> Departamentos -> Carreras)
    sumando préstamos acumulados sin bucles de control manual de nivel.
    """
    total = nodo_jerarquico.get("prestamos", 0)
    for departamento in nodo_jerarquico.get("departamentos", []):
        total += total_prestamos_recursivo(departamento)
    for carrera in nodo_jerarquico.get("carreras", []):
        total += total_prestamos_recursivo(carrera)
    return total


def buscar_subnodo_recursivo(nodo: Dict[str, Any], nombre_buscado: str) -> Dict[str, Any] | None:
    """Busca recursivamente un nodo (departamento o carrera) por su nombre."""
    if nodo.get("nombre") == nombre_buscado:
        return nodo
    
    subnodos = nodo.get("departamentos", []) + nodo.get("carreras", [])
    for sub in subnodos:
        resultado = buscar_subnodo_recursivo(sub, nombre_buscado)
        if resultado is not None:
            return resultado
            
    return None
