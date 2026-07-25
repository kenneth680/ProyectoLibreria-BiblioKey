# 📚 BiblioKEY / BiblioRUA
### Sistema Inteligente de Biblioteca Universitaria
**Integración de los 5 Paradigmas de Programación**

---

## 🗂 Estructura del Proyecto por Paradigma

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
├── P4_Eventos/             ← Paradigma 4: Orientado a Eventos
│   ├── README.md
│   └── event_bus.py        (copia de referencia)
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
├── app_gui.py              ← 🚀 PUNTO DE ENTRADA (GUI)
└── main.py                 ← 🖥 Demo en consola
```

---

## 🚀 Cómo ejecutar

```bash
# Instalar dependencias
pip install customtkinter tkcalendar

# Iniciar la interfaz gráfica
python app_gui.py

# Demo en consola (sin GUI)
python main.py

# Ejecutar pruebas unitarias
python -m pytest tests/ -v
```

---

## 🧩 Los 5 Paradigmas en un vistazo

| # | Paradigma | Carpeta | Archivos clave | Concepto demostrado |
|---|---|---|---|---|
| 1 | **Imperativo** | `P1_Imperativo/` | `app_gui.py`, `main.py` | Secuencia, selección, iteración |
| 2 | **Orientado a Objetos** | `P2_Orientado_Objetos/` | `models/*.py` | Herencia, polimorfismo, encapsulamiento |
| 3 | **Funcional** | `P3_Funcional/` | `modules/functional_engine.py` | `filter`, `map`, `reduce`, recursividad, lambdas |
| 4 | **Orientado a Eventos** | `P4_Eventos/` | `events/event_bus.py` | Pub/Sub, Observer, reactividad |
| 5 | **Lógico** | `P5_Logico/` | `modules/logic_engine.py`, `rules/*.pl` | Hechos, reglas, inferencia, Prolog |

---

## ⚙ Multas por retraso

La tarifa de penalización es **L 15.00 por día** de atraso.  
Se calcula automáticamente en la sección **Consultas → Préstamos vencidos**.

---

## 📋 Características principales

- ✅ Registro de préstamos con **fecha personalizable** (para pruebas con fechas pasadas)
- ✅ Marcado de entregados y eliminación de registros
- ✅ Detección automática de libros vencidos con cálculo de multa
- ✅ Catálogo de libros con filtros por categoría
- ✅ Estadísticas funcionales (map · filter · reduce · recursividad)
- ✅ Recomendaciones basadas en motor Prolog
- ✅ Consultas declarativas tipo SQL con resultados dinámicos
