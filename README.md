# BiblioKEY / BiblioKEY
### Sistema Inteligente de Biblioteca Universitaria
**Integración de los 5 Paradigmas de Programación**

---

##  Estructura del Proyecto por Paradigma

```
sistema_biblioteca_5_paradigmas/
│
├── P1_Imperativo/          ← Paradigma 1: Imperativo / Procedimental
│   └── README.md
│
├── P2_Orientado_Objetos/   ← Paradigma 2: Orientado a Objetos (POO)
│   ├── README.md
│   ├── usuario.py          (copia de referencia)
│   ├── libro.py            (copia de referencia)
│   └── prestamo.py         (copia de referencia)
│
├── P3_Funcional/           ← Paradigma 3: Funcional
│   ├── README.md
│   └── functional_engine.py (copia de referencia)
│
├── P4_Declarativo/             ← Paradigma 4: Declarativo
│   ├── README.md
│   ├── database.py          (copia de referencia — SQL real sobre SQLite)
│   └── event_bus.py        (copia de referencia — extensión: Reactivo)
│
├── P5_Logico/              ← Paradigma 5: Lógico / Declarativo
│   └── README.md
│
│── models/                 ← Clases POO (activas en runtime)
│   ├── usuario.py
│   ├── libro.py
│   └── prestamo.py
│
├── modules/                ← Motores (activos en runtime)
│   ├── functional_engine.py
│   └── logic_engine.py
│
├── events/                 ← EventBus (activo en runtime)
│   └── event_bus.py
│
├── rules/                  ← Reglas Prolog
│   └── reglas_biblioteca.pl
│
├── ui/                     ← Tema visual
│   └── ui_theme.py
│
├── tests/                  ← Pruebas unitarias
│   └── test_paradigmas.py
│
├── database.py             ←  Acceso a datos SQLite (activo en runtime)
├── biblioteca.db            ←  Base de datos persistente (se genera automáticamente)
├── app_gui.py              ←  PUNTO DE ENTRADA (GUI)
└── main.py                 ←  Demo en consola
```

---

##  Cómo ejecutar

```bash
# Instalar dependencias
pip install customtkinter tkcalendar

# Iniciar la interfaz gráfica
python app_gui.py

# Demo en consola (sin GUI)
python main.py
```

> ℹ La base de datos `biblioteca.db` se crea automáticamente en la primera
> ejecución (usa `sqlite3`, incluido en la librería estándar de Python — no
> requiere instalación adicional). Los préstamos, usuarios y disponibilidad
> de libros quedan guardados ahí y persisten aunque se cierre el programa.

---

##  Los 5 Paradigmas en un vistazo

| # | Paradigma | Carpeta | Archivos clave | Concepto demostrado |
|---|---|---|---|---|
| 1 | **Imperativo** | `P1_Imperativo/` | `app_gui.py`, `main.py` | Secuencia, selección, iteración |
| 2 | **Orientado a Objetos** | `P2_Orientado_Objetos/` | `models/*.py` | Herencia, polimorfismo, encapsulamiento |
| 3 | **Funcional** | `P3_Funcional/` | `modules/functional_engine.py` | `filter`, `map`, `reduce`, recursividad, lambdas |
| 4 | **Declarativo** | `P4_Declarativo/` | `database.py` (SQL sobre SQLite) + `event_bus.py` (extensión: Reactivo) | `SELECT`/`JOIN`/`WHERE`/`GROUP BY` reales, persistencia en disco, Pub/Sub |
| 5 | **Lógico** | `P5_Logico/` | `modules/logic_engine.py`, `rules/*.pl` | Hechos, reglas, inferencia, Prolog |

---

##  Multas por retraso

La tarifa de penalización es **L 15.00 por día** de atraso.  
Se calcula automáticamente en la sección **Consultas → Préstamos vencidos**.

---

##  Características principales

-  Registro de préstamos con fecha personalizabls
-  Marcado de entregados y eliminación de registros
-  Detección automática de libros vencidos con cálculo de multa
-  Catálogo de libros con filtros por categoría
-  Estadísticas funcionales (map · filter · reduce · recursividad)
-  Recomendaciones basadas en motor Prolog
-  Consultas declarativas reales en SQL, ejecutadas contra una base de datos SQLite (`database.py`)
-  Persistencia en disco: préstamos, usuarios y disponibilidad de libros se conservan entre sesiones (`biblioteca.db`)
