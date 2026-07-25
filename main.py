"""
==================================================================
Sistema Inteligente de Biblioteca Universitaria (BiblioKEY)
Integración Total de los 5 Paradigmas de Programación
Kenneth Ramirez 20241900233
Yankel Martinez 20251900146
Elda Velasquez 20241930024
==================================================================
1. Imperativo: Control de flujo secuencial, validaciones y ciclo de vida.
2. POO: Entidades encapsuladas (Usuario, Estudiante, Docente, Libro, Prestamo) con polimorfismo.
3. Funcional: Inmutabilidad, filter, map, reduce, lambdas y recursividad.
4. Declarativo: EventBus desacoplado con oyentes reactivos.
5. Lógico: Motor de inferencia (Facts/Rules) y deducción de elegibilidad.
==================================================================
"""

import sys
from datetime import date, timedelta
from typing import List

# Importación de Módulos del Sistema
from models.usuario import Estudiante, Docente, Usuario
from models.libro import Libro
from models.prestamo import Prestamo
from modules.functional_engine import (
    obtener_prestamos_vencidos,
    formatear_catalogo_para_reporte,
    total_prestamos_recursivo,
)
from modules.logic_engine import LogicEngine
from events.event_bus import bus_global, Event


# ============================================================
# 1. CATALOGO DE LIBROS Y USUARIOS INICIALES (POO + Estado Base)
# ============================================================

CATALOGO_LIBROS: List[Libro] = [
    Libro("Introduction to Algorithms", "Thomas H. Cormen", 2022, "Ciencia de la Computacion"),
    Libro("Artificial Intelligence: A Modern Approach", "Stuart Russell", 2020, "Ciencia de la Computacion"),
    Libro("Clean Code", "Robert C. Martin", 2008, "Ciencia de la Computacion"),
    Libro("Capital in the Twenty-First Century", "Thomas Piketty", 2014, "Economia y Finanzas"),
    Libro("Thinking, Fast and Slow", "Daniel Kahneman", 2011, "Economia y Finanzas"),
    Libro("Principles of Economics", "N. Gregory Mankiw", 2020, "Economia y Finanzas"),
    Libro("Don Quijote de la Mancha", "Miguel de Cervantes", 2015, "Literatura Universal"),
    Libro("Cien anios de soledad", "Gabriel Garcia Marquez", 2017, "Literatura Universal"),
    Libro("1984", "George Orwell", 2021, "Literatura Universal"),
    Libro("Manuscrito Raro de Calculo", "Isaac Newton", 1704, "Reserva Especial"),
]

USUARIOS_REGISTRADOS: List[Usuario] = [
    Estudiante("20241930024", "Elda Velasquez", "Psicología"),
    Estudiante("20241900233", "Kenneth Ramirez", "Desarrollo Local"),
    Docente("DOC-123", "Evan Romero", "Sistemas"),
    Estudiante("20251900146", "Yankel Martinez", "Sistemas"),
]

PRESTAMOS_HISTORIAL: List[Prestamo] = []

# Inicializar Motor Lógico
motor_logico = LogicEngine()

# Cargar hechos iniciales en el motor lógico
for u in USUARIOS_REGISTRADOS:
    motor_logico.registrar_usuario_hecho(u.cuenta, u.obtener_tipo(), prestamos_activos=0, en_mora=False)


# ============================================================
# 2. PARADIGMA ORIENTADO A OBJETOS
# ============================================================

def listener_prestamo_creado(event: Event):
    """Reacción automática al crear un préstamo (Actualización de auditoría)."""
    prestamo_dict = event.data.get("prestamo")
    print(f"   [EVENTO REACTIVO] Préstamo Registrado: '{prestamo_dict['titulo']}' -> Usuario: {prestamo_dict['usuario']}")


def listener_alerta_mora(event: Event):
    """Reacción automática cuando se detecta un préstamo vencido."""
    cuenta = event.data.get("cuenta")
    print(f"   [EVENTO REACTIVO] Alerta de Mora Emitida para la Cuenta: {cuenta}")


# Suscripción al bus de eventos
bus_global.subscribe("PRESTAMO_CREADO", listener_prestamo_creado)
bus_global.subscribe("ALERTA_MORA", listener_alerta_mora)


# ============================================================
# 3. PARADIGMA IMPERATIVO: FLUJO PRINCIPAL DE REGISTRO
# ============================================================

def registrar_nuevo_prestamo_imperativo(cuenta_usuario: str, titulo_libro: str, dias_custom: int = None) -> bool:
    """
    Función Imperativa: Valida procedimentalmente las condiciones,
    invoca al Motor Lógico, modifica el estado y emite eventos reactivos.
    """
    print(f"\n--- [IMPERATIVO] Solicitando Préstamo: Cuenta={cuenta_usuario}, Libro='{titulo_libro}' ---")

    # 1. Búsqueda imperativa de usuario y libro
    usuario = next((u for u in USUARIOS_REGISTRADOS if u.cuenta == cuenta_usuario), None)
    if not usuario:
        print(f"❌ Error Imperativo: Usuario con cuenta {cuenta_usuario} no encontrado.")
        return False

    libro = next((l for l in CATALOGO_LIBROS if l.titulo == titulo_libro), None)
    if not libro:
        print(f"❌ Error Imperativo: Libro '{titulo_libro}' no disponible en catálogo.")
        return False

    if not libro.disponible:
        print(f"❌ Error Imperativo: El libro '{titulo_libro}' ya está prestado.")
        return False

    # 2. Conteo de préstamos activos y estado de mora para el Motor Lógico
    prestamos_usuario = [p for p in PRESTAMOS_HISTORIAL if p.usuario.cuenta == cuenta_usuario and not p.devuelto]
    prestamos_activos_cnt = len(prestamos_usuario)
    esta_en_mora = any(p.esta_vencido() for p in prestamos_usuario)

    # 3. Evaluación en el PARADIGMA LÓGICO
    autorizado, razon_logica = motor_logico.evaluar_elegibilidad_prestamo(
        cuenta=usuario.cuenta,
        tipo_usuario=usuario.obtener_tipo(),
        prestamos_actuales=prestamos_activos_cnt,
        en_mora=esta_en_mora,
        categoria_libro=libro.categoria
    )

    print(f"   [MOTOR LÓGICO]: {razon_logica}")

    if not autorizado:
        print(" Solicitud Rechazada por deducción lógica.")
        return False

    # 4. Creación POO + Polimorfismo (Cálculo de días)
    dias_maximos = dias_custom if dias_custom is not None else usuario.obtener_dias_maximos_prestamo()
    nuevo_prestamo = Prestamo(usuario, libro, fecha_prestamo=date.today(), dias_permitidos=dias_maximos)
    libro.prestar()
    PRESTAMOS_HISTORIAL.append(nuevo_prestamo)

    # 5. Publicación de Evento (PARADIGMA REACTIVO)
    bus_global.publish("PRESTAMO_CREADO", {"prestamo": nuevo_prestamo.to_dict()})
    return True


# ============================================================
# 4. DEMOSTRACIÓN COMPLETA DE LOS 5 PARADIGMAS
# ============================================================

def ejecutar_demostracion_sistema():
    print("=" * 70)
    print("  SISTEMA INTELIGENTE DE BIBLIOTECA UNIVERSITARIA (BiblioRUA)")
    print(" Integración de 5 Paradigmas: Imperativo | POO | Funcional | Eventos | Lógico")
    print("=" * 70)

    # A. Demostración POO + Polimorfismo
    print("\n--- 1. PARADIGMA ORIENTADO A OBJETOS (Polimorfismo de Días) ---")
    for u in USUARIOS_REGISTRADOS:
        print(f"  • {u} -> Días Permitidos Polimórficos: {u.obtener_dias_maximos_prestamo()} días")

    # B. Demostración Registro Imperativo + Motor Lógico + Eventos
    print("\n--- 2. REGISTRO IMPERATIVO CON REGLAS LÓGICAS Y EVENTOS ---")

    # Caso 1: Estudiante solicita libro normal (Autorizado)
    registrar_nuevo_prestamo_imperativo("20201001", "Clean Code")

    # Caso 2: Estudiante solicita libro de 'Reserva Especial' (Rechazado por Motor Lógico)
    registrar_nuevo_prestamo_imperativo("20201001", "Manuscrito Raro de Calculo")

    # Caso 3: Docente solicita libro de 'Reserva Especial' (Autorizado para Docentes)
    registrar_nuevo_prestamo_imperativo("DOC001", "Manuscrito Raro de Calculo")

    # C. Simulando Préstamo Vencido y Alerta de Mora
    print("\n--- 3. SIMULACIÓN DE MORA Y EVENTO REACTIVO ---")
    # Forzar vencimiento a un préstamo existente
    if PRESTAMOS_HISTORIAL:
        p_vencido = PRESTAMOS_HISTORIAL[0]
        p_vencido._fecha_devolucion = date.today() - timedelta(days=5)  # Hace 5 días
        print(f"   Préstamo de '{p_vencido.libro.titulo}' marcado como vencido manualmente.")
        bus_global.publish("ALERTA_MORA", {"cuenta": p_vencido.usuario.cuenta})

    # D. PARADIGMA FUNCIONAL (Auditoría e Inmutabilidad)
    print("\n--- 4. PARADIGMA FUNCIONAL (Filter, Map, Reduce y Recursividad) ---")
    
    # Preparar datos inmutables (dicts) para el motor funcional
    prestamos_dicts = [p.to_dict() for p in PRESTAMOS_HISTORIAL]
    libros_dicts = [l.to_dict() for l in CATALOGO_LIBROS]

    # Filter + Lambda
    vencidos = obtener_prestamos_vencidos(prestamos_dicts)
    print(f"\n  [FILTER + LAMBDA] Préstamos Vencidos Detectados ({len(vencidos)}):")
    for v in vencidos:
        print(f"    - {v['titulo']} (Usuario: {v['usuario']})")

    # Map + Lambda
    catalogo_formateado = formatear_catalogo_para_reporte(libros_dicts[:4])
    print(f"\n  [MAP + LAMBDA] Catálogo Formateado (Primeros 4):")
    for linea in catalogo_formateado:
        print(f"    - {linea}")

    # Recursividad sobre Estructura Jerárquica Universitaria
    estructura_facultad = {
        "nombre": "Facultad de Ingenieria",
        "prestamos": 0,
        "departamentos": [
            {
                "nombre": "Ingenieria en Sistemas",
                "prestamos": 0,
                "carreras": [
                    {"nombre": "Sistemas Grado", "prestamos": 14},
                    {"nombre": "Sistemas Posgrado", "prestamos": 6},
                ],
            },
            {
                "nombre": "Ingenieria Civil",
                "prestamos": 0,
                "carreras": [
                    {"nombre": "Civil Grado", "prestamos": 9},
                ],
            },
        ],
    }
    total_recursivo = total_prestamos_recursivo(estructura_facultad)
    print(f"\n  [RECURSIVIDAD FUNCIONAL] Total Préstamos Jerárquicos ({estructura_facultad['nombre']}): {total_recursivo}")

    # E. PARADIGMA LÓGICO EXPORTACION PROLOG
    print("\n--- 5. PARADIGMA LÓGICO (Exportación a Prolog) ---")
    prolog_code = motor_logico.exportar_a_prolog()
    print("   Vista previa de hechos generados para Prolog:")
    for line in prolog_code.splitlines()[:5]:
        print(f"    {line}")
    print("   Base de datos lógica lista para validación en SWI-Prolog.")

    print("\n" + "=" * 70)
    print("  ¡Demostración de los 5 Paradigmas completada con éxito!")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_demostracion_sistema()
