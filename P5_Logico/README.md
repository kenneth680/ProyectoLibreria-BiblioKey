# Paradigma 5 — Lógico / Declarativo

## ¿Qué es?
El **paradigma lógico** (o declarativo) describe *qué* se quiere resolver
mediante hechos y reglas, dejando al motor de inferencia el *cómo* encontrar
la solución. El lenguaje de referencia es **Prolog**, donde el programa es una
base de conocimientos de hechos y reglas.

## Archivos del paradigma

| Archivo | Descripción |
|---|---|
| `logic_engine.py` | Motor de inferencia en Python (emula Prolog) |
| `reglas_biblioteca.pl` | Base de conocimientos nativa en Prolog |

## Principios aplicados

### Hechos (Facts)
Declaraciones atómicas de verdad sobre el dominio:
```prolog
% En Prolog (reglas_biblioteca.pl)
libro("Hábitos que transforman", "A. Duhig", "Bienestar", disponible).
usuario("20221004512", estudiante, al_dia).
```

### Reglas (Rules)
Relaciones derivadas mediante unificación y backtracking:
```prolog
% Regla: puede prestar si está al día y hay disponibilidad
puede_prestar(Usuario, Libro) :-
    usuario(Usuario, _, al_dia),
    libro(Libro, _, _, disponible).

% Regla: recomendar libro si es de la categoría favorita
recomendar(Estudiante, Libro) :-
    categoria_favorita(Estudiante, Cat),
    libro(Libro, _, Cat, disponible),
    not(ya_prestado(Estudiante, Libro)).
```

### Motor de Inferencia en Python (`logic_engine.py`)
Para integración directa sin instalar SWI-Prolog, el sistema incluye un motor
de inferencia Python que emula el comportamiento lógico:
```python
motor = LogicEngine()
motor.agregar_hecho("usuario", ("20221004512", "estudiante", "al_dia"))
motor.agregar_regla("puede_prestar", ...)
autorizado, razon = motor.evaluar_elegibilidad_prestamo(cuenta, tipo, ...)
```

### Integración con Prolog externo
El archivo `reglas_biblioteca.pl` puede ejecutarse con SWI-Prolog de manera
externa como complemento de validación del sistema:
```bash
swipl -g "consult('reglas_biblioteca.pl'), puede_prestar('20221004512', 'Hábitos que transforman'), halt."
```

## Archivos relacionados (en el proyecto)
- [`logic_engine.py`](../modules/logic_engine.py)
- [`reglas_biblioteca.pl`](../rules/reglas_biblioteca.pl)
