% ===================================================================
% REGLAS Y HECHOS EN PROLOG (Paradigma Lógico)
# Sistema Inteligente de Biblioteca Universitaria (BiblioRUA)
% ===================================================================

% -------------------------------------------------------------------
% 1. HECHOS BASE (Fact Database)
% -------------------------------------------------------------------

% usuario_activo(Cuenta, Nombre, Tipo)
usuario_activo('20201001', 'Pedro', estudiante).
usuario_activo('20201002', 'Ana', estudiante).
usuario_activo('DOC001', 'Carlos', docente).
usuario_activo('20201003', 'Maria', estudiante).

% en_mora(Cuenta) - Cuentas con préstamos atrasados
en_mora('20201001').

% limite_libros(Tipo, MaxLibros)
limite_libros(estudiante, 3).
limite_libros(docente, 5).

% categoria_restringida(Categoria)
categoria_restringida('Reserva Especial').

% autorizacion_docente_requerida(Categoria)
autorizacion_docente_requerida('Reserva Especial').
autorizacion_docente_requerida('Investigacion').

% prestamos_activos(Cuenta, Cantidad)
prestamos_activos('20201001', 3).
prestamos_activos('20201002', 1).
prestamos_activos('DOC001', 2).
prestamos_activos('20201003', 0).


% -------------------------------------------------------------------
% 2. REGLAS LOGICAS DE DEDUCCION (Inference Rules)
% -------------------------------------------------------------------

% Una cuenta no tiene impedimento si no está en mora
libre_de_mora(Cuenta) :-
    \+ en_mora(Cuenta).

% Un usuario tiene cupo si sus préstamos activos son menores a su límite
tiene_cupo_disponible(Cuenta) :-
    usuario_activo(Cuenta, _, Tipo),
    limite_libros(Tipo, Maximo),
    prestamos_activos(Cuenta, Actuales),
    Actuales < Maximo.

% Regla Principal: Puede solicitar préstamo si está activo, libre de mora y tiene cupo
puede_solicitar_prestamo(Cuenta) :-
    usuario_activo(Cuenta, _, _),
    libre_de_mora(Cuenta),
    tiene_cupo_disponible(Cuenta).

% Regla de Aprobación de Categoría por Tipo de Usuario
categoria_permitida_para(estudiante, Categoria) :-
    \+ categoria_restringida(Categoria).

categoria_permitida_para(docente, _Categoria).

% Regla de Descuento/Exención de Multa por Primera Mora
elegible_exencion_multa(Cuenta) :-
    usuario_activo(Cuenta, _, docente).

elegible_exencion_multa(Cuenta) :-
    usuario_activo(Cuenta, _, estudiante),
    libre_de_mora(Cuenta).

% -------------------------------------------------------------------
% Ejemplos de consultas en SWI-Prolog:
% ?- puede_solicitar_prestamo('20201002'). -> true.
% ?- puede_solicitar_prestamo('20201001'). -> false. (por estar en mora)
% -------------------------------------------------------------------
