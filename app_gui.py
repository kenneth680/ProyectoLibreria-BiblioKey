#Kenneth Ramirez 20241900233
#Yankel Martinez 20241900146
#Elda Velasquez 20241930024
import sys
import csv
from datetime import date, datetime, timedelta
from typing import List, Dict, Any

try:
    import customtkinter as ctk
    from tkcalendar import DateEntry
    from tkinter import filedialog, messagebox
except ImportError:
    ctk = None

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
from ui.ui_theme import COLORS, FONT_SECTION, FONT_BODY, FONT_SMALL, StatusBadge


if ctk is None:
    print("Error: Se requiere customtkinter para ejecutar la interfaz gráfica multisección.")
    print("Ejecuta 'pip install customtkinter tkcalendar' en tu terminal.")
    sys.exit(0)


# ============================================================
# ESTADO DEL SISTEMA Y DATOS BASE
# ============================================================

CATALOGO_LIBROS: List[Libro] = [
    Libro("Hábitos que transforman", "A. Duhig", 2019, "Bienestar y hábitos"),
    Libro("Enfócate", "C. Newport", 2016, "Bienestar y hábitos"),
    Libro("Mentalidad ágil", "R. Soto", 2021, "Bienestar y hábitos"),
    Libro("Pensar mejor", "D. Kahneman", 2018, "Psicología"),
    Libro("El mapa emocional", "M. Torres", 2020, "Psicología"),
    Libro("Mente clara", "S. Lozano", 2022, "Psicología"),
    Libro("El jardín de las sombras", "L. Fernández", 2015, "Literatura"),
    Libro("Cartas desde el silencio", "A. Reyes", 2013, "Literatura"),
    Libro("El último tren", "C. Molina", 2017, "Literatura"),
    Libro("Manuscrito Raro de Cálculo", "Isaac Newton", 1704, "Reserva Especial"),
]

USUARIOS_BASE = [
    Estudiante("20241930024", "Elda Velasquez", "Psicología"),
    Estudiante("20241900233", "Kenneth Ramirez", "Desarrollo Local"),
    Docente("DOC-123", "Evan Romero", "Sistemas"),
    Estudiante("20251900146", "Yankel Martinez", "Sistemas"),
]



LISTA_PRESTAMOS: List[Prestamo] = []

motor_logico = LogicEngine()


# ============================================================
# APLICACION PRINCIPAL MULTISECCION CON SIDEBAR
# ============================================================

class BiblioRUAApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BiblioKEY / BiblioKEY")
        self.geometry("1120x730")
        self.minsize(1000, 650)
        ctk.set_appearance_mode("light")

        self.active_tab = "prestamos"
        self.active_query = "vencidos"  # Filtro activo para la sección Consultas

        # Layout Principal: Sidebar Izquierdo (Fix 220px) + Main Content (Flex)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_sidebar()
        self._crear_contenedor_principal()
        self.mostrar_seccion("prestamos")

    # ------------------------------------------------------------
    # 1. SIDEBAR IZQUIERDO DE NAVEGACION
    # ------------------------------------------------------------
    def _crear_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color="#1E3A5F", width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logotipo
        lbl_logo_circle = ctk.CTkLabel(
            self.sidebar, text="KEY", font=("Poppins", 15, "bold"),
            text_color="#1E3A5F", fg_color=COLORS["gold"], width=46, height=46, corner_radius=23
        )
        lbl_logo_circle.pack(anchor="w", padx=20, pady=(24, 4))

        lbl_brand = ctk.CTkLabel(self.sidebar, text="BiblioKEY", font=("Poppins", 18, "bold"), text_color=COLORS["white"])
        lbl_brand.pack(anchor="w", padx=20)

        lbl_subbrand = ctk.CTkLabel(self.sidebar, text="Universidad Autonoma", font=("Poppins", 9), text_color="#A0AEC0")
        lbl_subbrand.pack(anchor="w", padx=20, pady=(0, 24))

        # Botones del Menú Lateral
        self.sidebar_buttons: Dict[str, ctk.CTkButton] = {}

        secciones = [
            ("prestamos", "● Nuevo préstamo"),
            ("catalogo", "● Catálogo"),
            ("reportes", "● Estadísticas"),
            ("recomendaciones", "● Para ti"),
            ("consultas", "● Consultas"),
        ]

        for key, title in secciones:
            btn = ctk.CTkButton(
                self.sidebar,
                text=title,
                anchor="w",
                font=("Poppins", 13, "bold"),
                height=40,
                corner_radius=20,
                fg_color="transparent",
                text_color="#CBD5E1",
                hover_color="#2B4C7E",
                command=lambda k=key: self.mostrar_seccion(k)
            )
            btn.pack(fill="x", padx=16, pady=4)
            self.sidebar_buttons[key] = btn

    # ------------------------------------------------------------
    # 2. CONTENEDOR PRINCIPAL DERECHO
    # ------------------------------------------------------------
    def _crear_contenedor_principal(self):
        self.main_container = ctk.CTkFrame(self, fg_color="#142844", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header Superior
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(20, 10))

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="Préstamos", font=("Poppins", 26, "bold"), text_color=COLORS["white"])
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(self.header_frame, text="Registra y controla los préstamos del día", font=FONT_BODY, text_color="#94A3B8")
        self.lbl_subtitle.pack(anchor="w")

        # Área de Trabajo
        self.view_card = ctk.CTkFrame(self.main_container, fg_color="#F8FAFC", corner_radius=24)
        self.view_card.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.view_card.grid_columnconfigure(0, weight=1)
        self.view_card.grid_rowconfigure(0, weight=1)

    def mostrar_seccion(self, key: str):
        self.active_tab = key

        # Resaltado en Sidebar
        for k, btn in self.sidebar_buttons.items():
            if k == key:
                btn.configure(fg_color=COLORS["gold"], text_color=COLORS["navy"])
            else:
                btn.configure(fg_color="transparent", text_color="#CBD5E1")

        for widget in self.view_card.winfo_children():
            widget.destroy()

        if key == "prestamos":
            self.lbl_title.configure(text="Préstamos")
            self.lbl_subtitle.configure(text="Registra, gestiona y marca la devolución de préstamos del día")
            self._render_vista_prestamos()
        elif key == "catalogo":
            self.lbl_title.configure(text="Catálogo de Libros")
            self.lbl_subtitle.configure(text=f"{len(CATALOGO_LIBROS)} libros en total")
            self._render_vista_catalogo()
        elif key == "reportes":
            self.lbl_title.configure(text="Estadísticas")
            self.lbl_subtitle.configure(text="Análisis funcional de los préstamos (map · filter · reduce · recursividad)")
            self._render_vista_reportes()
        elif key == "recomendaciones":
            self.lbl_title.configure(text="Para ti")
            self.lbl_subtitle.configure(text="Recomendaciones basadas en el motor de inferencia Prolog")
            self._render_vista_recomendaciones()
        elif key == "consultas":
            self.lbl_title.configure(text="Consultas")
            self.lbl_subtitle.configure(text="Explora e audita la información de la biblioteca con reglas declarativas")
            self._render_vista_consultas()

    # ============================================================
    # VISTA 1: PRESTAMOS (CON OPCION DE MARCAR ENTREGADOS / DEVOLUCION)
    # ============================================================
    def _render_vista_prestamos(self):
        for widget in self.view_card.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.view_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Contadores
        frame_counters = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_counters.pack(fill="x", pady=(0, 16))

        prestamos_activos = [p for p in LISTA_PRESTAMOS if not p.devuelto]
        vencidos_cnt = len([p for p in prestamos_activos if p.esta_vencido()])

        card1 = ctk.CTkFrame(frame_counters, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        card1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(card1, text="Préstamos activos", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=16, pady=(12, 0))
        ctk.CTkLabel(card1, text=str(len(prestamos_activos)), font=("Poppins", 26, "bold"), text_color=COLORS["navy"]).pack(anchor="w", padx=16, pady=(0, 12))

        card2 = ctk.CTkFrame(frame_counters, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        card2.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(card2, text="Préstamos atrasados", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=16, pady=(12, 0))
        ctk.CTkLabel(card2, text=str(vencidos_cnt), font=("Poppins", 26, "bold"), text_color=COLORS["danger"]).pack(anchor="w", padx=16, pady=(0, 12))

        # Formulario
        form_card = ctk.CTkFrame(scroll, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        form_card.pack(fill="x", pady=(0, 20), padx=2)
        
        ctk.CTkLabel(form_card, text="Registrar préstamo", font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", padx=18, pady=(14, 8))

        row1 = ctk.CTkFrame(form_card, fg_color="transparent")
        row1.pack(fill="x", padx=18)

        # ── Dropdown con usuarios reales (nombre + carné) ──────────────────────
        # Construimos etiquetas legibles: "Nombre (carné)"
        def _etiqueta_usuario(u) -> str:
            return f"{u.nombre}  [{u.cuenta}]"

        opciones_usuario = [_etiqueta_usuario(u) for u in USUARIOS_BASE]

        ctk.CTkLabel(row1, text="Usuario", font=FONT_SMALL, text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        opt_usuario = ctk.CTkOptionMenu(
            row1, values=opciones_usuario, width=280,
            fg_color="#F1F5F9", text_color=COLORS["navy"], button_color="#CBD5E1", height=36
        )
        opt_usuario.grid(row=1, column=0, padx=(0, 10), pady=(2, 10))

        ctk.CTkLabel(row1, text="Libro", font=FONT_SMALL, text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w")
        libros_disponibles = [l.titulo for l in CATALOGO_LIBROS if l.disponible]
        opt_libro = ctk.CTkOptionMenu(
            row1, values=libros_disponibles or ["No hay libros disponibles"],
            width=280, fg_color="#F1F5F9", text_color=COLORS["navy"], button_color="#CBD5E1", height=36
        )
        opt_libro.grid(row=1, column=1, pady=(2, 10))

        row2 = ctk.CTkFrame(form_card, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=(0, 12))

        ctk.CTkLabel(row2, text="Fecha de préstamo (dd/mm/yyyy)", font=FONT_SMALL, text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        entry_fec = ctk.CTkEntry(row2, width=170, fg_color="#F1F5F9", border_width=0, height=36)
        entry_fec.grid(row=1, column=0, padx=(0, 10), pady=(2, 4))
        entry_fec.insert(0, date.today().strftime("%d/%m/%Y"))

        ctk.CTkLabel(row2, text="Días permitidos", font=FONT_SMALL, text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w")
        entry_dias = ctk.CTkEntry(row2, width=150, fg_color="#F1F5F9", border_width=0, height=36)
        entry_dias.grid(row=1, column=1, padx=(0, 10), pady=(2, 4))
        entry_dias.insert(0, "7")

        lbl_msg = ctk.CTkLabel(form_card, text="", font=FONT_SMALL, text_color=COLORS["danger"])
        lbl_msg.pack(anchor="w", padx=18)

        def ejecutar_registro():
            titulo = opt_libro.get()

            # ── Resolver el objeto Usuario real desde el dropdown ──────────────
            etiqueta_sel = opt_usuario.get()
            usuario_obj = next(
                (u for u in USUARIOS_BASE if _etiqueta_usuario(u) == etiqueta_sel), None
            )
            if not usuario_obj:
                lbl_msg.configure(text="❌ Selecciona un usuario válido.", text_color=COLORS["danger"])
                return

            cuenta = usuario_obj.cuenta
            tipo   = usuario_obj.obtener_tipo()  # "Estudiante" o "Docente" — del objeto real

            # ── Leer y parsear la fecha ingresada ──────────────────────────────
            fecha_str = entry_fec.get().strip()
            try:
                fecha_prestamo = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            except ValueError:
                lbl_msg.configure(text="❌ Formato de fecha inválido. Usa dd/mm/yyyy (ej: 10/07/2026)", text_color=COLORS["danger"])
                return

            # ── Leer días ─────────────────────────────────────────────────────
            try:
                dias_permitidos = int(entry_dias.get().strip())
                if dias_permitidos < 1:
                    raise ValueError
            except ValueError:
                lbl_msg.configure(text="❌ Días inválidos. Ingresa un número entero positivo.", text_color=COLORS["danger"])
                return

            libro = next((l for l in CATALOGO_LIBROS if l.titulo == titulo), None)
            if not libro or not libro.disponible:
                lbl_msg.configure(text="❌ Selecciona un libro válido disponible.", text_color=COLORS["danger"])
                return

            # ── Contar préstamos ACTIVOS reales del usuario ────────────────────
            prestamos_activos_usuario = sum(
                1 for p in LISTA_PRESTAMOS
                if p.usuario.cuenta == cuenta and not p.devuelto
            )

            # ── Validar con motor lógico (límite real, mora, categoría) ────────
            en_mora = any(
                p for p in LISTA_PRESTAMOS
                if p.usuario.cuenta == cuenta and p.esta_vencido()
            )
            autorizado, razon = motor_logico.evaluar_elegibilidad_prestamo(
                cuenta, tipo, prestamos_activos_usuario, en_mora, libro.categoria
            )
            if not autorizado:
                lbl_msg.configure(text=f"⛔ RECHAZADO: {razon}", text_color=COLORS["danger"])
                return

            # ── Crear préstamo con el objeto Usuario real ──────────────────────
            p = Prestamo(usuario_obj, libro, fecha_prestamo=fecha_prestamo, dias_permitidos=dias_permitidos)
            LISTA_PRESTAMOS.append(p)
            libro.prestar()
            bus_global.publish("PRESTAMO_CREADO", {"prestamo": p.to_dict()})
            self.mostrar_seccion("prestamos")

        btn_reg = ctk.CTkButton(
            row2, text="Registrar préstamo", fg_color=COLORS["gold"], hover_color=COLORS["navy"],
            text_color=COLORS["white"], font=("Poppins", 12, "bold"), corner_radius=18, height=36,
            command=ejecutar_registro
        )
        btn_reg.grid(row=1, column=2, padx=(10, 0), pady=(2, 4))

        # Historial de Préstamos + BOTON DE DEVOLUCION / ENTREGADO
        ctk.CTkLabel(scroll, text="Historial y Control de Devoluciones", font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", pady=(8, 10))

        def entregar_prestamo(target_prestamo: Prestamo):
            target_prestamo.marcar_devuelto()
            bus_global.publish("LIBRO_DEVUELTO", {"prestamo": target_prestamo.to_dict()})
            self.mostrar_seccion("prestamos")

        def eliminar_registro_prestamo(target_prestamo: Prestamo):
            if target_prestamo in LISTA_PRESTAMOS:
                target_prestamo.libro.devolver()
                LISTA_PRESTAMOS.remove(target_prestamo)
                self.mostrar_seccion("prestamos")

        for p in LISTA_PRESTAMOS:
            estado, color = p.obtener_estado_info()
            item_frame = ctk.CTkFrame(scroll, fg_color=COLORS["white"], corner_radius=14, border_width=1, border_color="#E2E8F0")
            item_frame.pack(fill="x", pady=5)

            col_text = ctk.CTkFrame(item_frame, fg_color="transparent")
            col_text.pack(side="left", padx=16, pady=12, fill="x", expand=True)

            ctk.CTkLabel(col_text, text=f"{p.libro.titulo} — {p.libro.autor}", font=("Poppins", 13, "bold"), text_color=COLORS["navy"]).pack(anchor="w")
            ctk.CTkLabel(col_text, text=f"Carné {p.usuario.cuenta} · devuelve {p.fecha_devolucion.strftime('%d/%m/%Y')}", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w")

            col_actions = ctk.CTkFrame(item_frame, fg_color="transparent")
            col_actions.pack(side="right", padx=16)

            StatusBadge(col_actions, estado, status=color).pack(side="left", padx=(0, 8))

            if not p.devuelto:
                btn_dev = ctk.CTkButton(
                    col_actions, text="✔ Marcar Entregado", fg_color="#10B981", hover_color="#059669",
                    text_color=COLORS["white"], font=("Poppins", 10, "bold"), height=30, corner_radius=12,
                    command=lambda target=p: entregar_prestamo(target)
                )
                btn_dev.pack(side="left", padx=(0, 4))

            btn_del = ctk.CTkButton(
                col_actions, text="🗑 Eliminar", fg_color="#EF4444", hover_color="#DC2626",
                text_color=COLORS["white"], font=("Poppins", 10, "bold"), height=30, width=70, corner_radius=12,
                command=lambda target=p: eliminar_registro_prestamo(target)
            )
            btn_del.pack(side="left")

    # ============================================================
    # VISTA 2: CATALOGO
    # ============================================================
    def _render_vista_catalogo(self, cat_activa: str = "Todas", busqueda: str = ""):
        for widget in self.view_card.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.view_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Barra de búsqueda ──────────────────────────────────────────────────
        search_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 8))

        entry_search = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar libro por título o autor...",
            fg_color=COLORS["white"], border_width=1, border_color="#E2E8F0", height=40, corner_radius=20
        )
        entry_search.pack(fill="x", side="left", expand=True, padx=(0, 10))
        if busqueda:
            entry_search.insert(0, busqueda)

        def _on_search(event=None):
            self._render_vista_catalogo(cat_activa=cat_activa, busqueda=entry_search.get())
        entry_search.bind("<Return>", _on_search)
        entry_search.bind("<KeyRelease>", _on_search)

        # ── Botones de categoría ───────────────────────────────────────────────
        cat_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cat_frame.pack(fill="x", pady=(0, 16))

        # Obtener categorias unicas del catalogo + "Todas"
        cats_existentes = ["Todas"] + sorted(set(l.categoria for l in CATALOGO_LIBROS))

        btn_refs: dict = {}
        def _cambiar_cat(nueva_cat: str):
            for c, b in btn_refs.items():
                if c == nueva_cat:
                    b.configure(fg_color=COLORS["gold"], text_color=COLORS["white"])
                else:
                    b.configure(fg_color=COLORS["white"], text_color=COLORS["navy"])
            self._render_vista_catalogo(cat_activa=nueva_cat, busqueda=entry_search.get())

        for cat in cats_existentes:
            is_active = (cat == cat_activa)
            btn_cat = ctk.CTkButton(
                cat_frame, text=cat,
                fg_color=COLORS["gold"] if is_active else COLORS["white"],
                text_color=COLORS["white"] if is_active else COLORS["navy"],
                border_width=1, border_color="#CBD5E1", corner_radius=16, height=32,
                command=lambda c=cat: _cambiar_cat(c)
            )
            btn_cat.pack(side="left", padx=(0, 8))
            btn_refs[cat] = btn_cat

        # ── Filtrar libros ──────────────────────────────────────────────────
        q = busqueda.lower().strip()
        libros_filtrados = [
            l for l in CATALOGO_LIBROS
            if (cat_activa == "Todas" or l.categoria == cat_activa)
            and (not q or q in l.titulo.lower() or q in l.autor.lower())
        ]

        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1)

        if not libros_filtrados:
            ctk.CTkLabel(grid_frame, text="No se encontraron libros.", font=FONT_BODY, text_color=COLORS["text_muted"]).pack(pady=40)
            return

        colors_palette = ["#D97706", "#48BB78", "#E53E3E", "#2B6CB0", "#C05621"]

        for idx, libro in enumerate(libros_filtrados):
            row = idx // 3
            col = idx % 3

            card = ctk.CTkFrame(grid_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            cover_color = colors_palette[idx % len(colors_palette)]
            cover = ctk.CTkFrame(card, fg_color=cover_color, height=80, corner_radius=12)
            cover.pack(fill="x", padx=8, pady=8)
            cover.pack_propagate(False)

            initial = libro.titulo[0].upper()
            ctk.CTkLabel(cover, text=initial, font=("Poppins", 32, "bold"), text_color=COLORS["white"]).place(relx=0.5, rely=0.5, anchor="center")

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=12, pady=(0, 12))

            ctk.CTkLabel(info, text=libro.categoria.upper(), font=("Poppins", 9, "bold"), text_color=COLORS["gold"]).pack(anchor="w")
            ctk.CTkLabel(info, text=libro.titulo, font=("Poppins", 13, "bold"), text_color=COLORS["navy"], wraplength=180, justify="left").pack(anchor="w")
            ctk.CTkLabel(info, text=f"{libro.autor} · {libro.anio}", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

            status_txt = "Disponible" if libro.disponible else "Prestado"
            status_clr = "success" if libro.disponible else "danger"
            StatusBadge(info, status_txt, status=status_clr).pack(anchor="w", pady=(0, 8))

            btn_txt = "Prestar" if libro.disponible else "Reservar"
            btn_act = ctk.CTkButton(info, text=btn_txt, fg_color=COLORS["gold"] if libro.disponible else "#CBD5E1", text_color=COLORS["white"] if libro.disponible else COLORS["navy"], corner_radius=12, height=32)
            btn_act.pack(fill="x")

    # ============================================================
    # VISTA 3: ESTADISTICAS
    # ============================================================
    def _render_vista_reportes(self):
        for widget in self.view_card.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.view_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        metric_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        metric_frame.pack(fill="x", pady=(0, 20))

        m1 = ctk.CTkFrame(metric_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        m1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(m1, text="Total préstamos", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(m1, text=str(len(LISTA_PRESTAMOS)), font=("Poppins", 22, "bold"), text_color=COLORS["navy"]).pack(anchor="w", padx=14, pady=(0, 10))

        m2 = ctk.CTkFrame(metric_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        m2.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkLabel(m2, text="Promedio días", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(m2, text="8.4", font=("Poppins", 22, "bold"), text_color=COLORS["navy"]).pack(anchor="w", padx=14, pady=(0, 10))

        disp_cnt = len([l for l in CATALOGO_LIBROS if l.disponible])
        m3 = ctk.CTkFrame(metric_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        m3.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkLabel(m3, text="Libros disponibles", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(m3, text=f"{disp_cnt} / {len(CATALOGO_LIBROS)}", font=("Poppins", 22, "bold"), text_color=COLORS["navy"]).pack(anchor="w", padx=14, pady=(0, 10))

        venc_cnt = len(obtener_prestamos_vencidos([p.to_dict() for p in LISTA_PRESTAMOS if not p.devuelto]))
        m4 = ctk.CTkFrame(metric_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        m4.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(m4, text="Préstamos vencidos", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(m4, text=str(venc_cnt), font=("Poppins", 22, "bold"), text_color=COLORS["danger"]).pack(anchor="w", padx=14, pady=(0, 10))

        col_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        col_frame.pack(fill="x")
        col_frame.grid_columnconfigure((0, 1), weight=1)

        left_card = ctk.CTkFrame(col_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        left_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(left_card, text="Top 3 libros más prestados (reduce)", font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", padx=16, pady=(14, 12))

        # ── Calcular top 3 de forma funcional (reduce/Counter) con datos reales ──
        from functools import reduce
        conteo_libros: Dict[str, int] = reduce(
            lambda acc, p: {**acc, p.libro.titulo: acc.get(p.libro.titulo, 0) + 1},
            LISTA_PRESTAMOS,
            {}
        )
        tops = sorted(conteo_libros.items(), key=lambda x: x[1], reverse=True)[:3]
        max_cnt = tops[0][1] if tops else 1

        if tops:
            for t_title, cnt in tops:
                f_row = ctk.CTkFrame(left_card, fg_color="transparent")
                f_row.pack(fill="x", padx=16, pady=4)
                lbl_titulo = t_title if len(t_title) <= 26 else t_title[:24] + "..."
                ctk.CTkLabel(f_row, text=lbl_titulo, font=FONT_BODY, text_color=COLORS["navy"], anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(f_row, text=f"{cnt} prest.", font=("Poppins", 11, "bold"), text_color=COLORS["gold"]).pack(side="right")
                bar = ctk.CTkProgressBar(left_card, progress_color=COLORS["gold"], fg_color="#F1F5F9", height=8, corner_radius=4)
                bar.set(cnt / max(max_cnt, 1))
                bar.pack(fill="x", padx=16, pady=(0, 6))
        else:
            ctk.CTkLabel(left_card, text="Sin préstamos registrados", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(padx=16, pady=20)

        right_card = ctk.CTkFrame(col_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        right_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(right_card, text="Multas por atraso (función recursiva)", font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", padx=16, pady=(14, 12))

        # ── Multas reales de préstamos vencidos ─────────────────────────────
        multas_reales = [
            (p.usuario.nombre, abs(p.dias_restantes()), p.calcular_multa(15.0))
            for p in LISTA_PRESTAMOS if p.esta_vencido()
        ]

        header_m = ctk.CTkFrame(right_card, fg_color="#F8FAFC")
        header_m.pack(fill="x", padx=16, pady=2)
        ctk.CTkLabel(header_m, text="Estudiante", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkLabel(header_m, text="Multa", font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(side="right")

        if multas_reales:
            for nombre, dias, monto in multas_reales:
                r = ctk.CTkFrame(right_card, fg_color="transparent")
                r.pack(fill="x", padx=16, pady=6)
                ctk.CTkLabel(r, text=f"{nombre} ({dias} d.)", font=FONT_BODY, text_color=COLORS["navy"]).pack(side="left")
                ctk.CTkLabel(r, text=f"L {monto:.2f}", font=("Poppins", 11, "bold"), text_color=COLORS["danger"]).pack(side="right")
        else:
            ctk.CTkLabel(right_card, text="Sin multas activas", font=FONT_SMALL, text_color="#10B981").pack(padx=16, pady=20)

    # ============================================================
    # VISTA 4: RECOMENDACIONES
    # ============================================================
    def _render_vista_recomendaciones(self, usuario_sel_idx: int = 0):
        for widget in self.view_card.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.view_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Selector de usuario (nombres reales de USUARIOS_BASE) ─────────────
        sel_card = ctk.CTkFrame(scroll, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        sel_card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(sel_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        opciones_usr = [f"{u.nombre}  [{u.cuenta}]" for u in USUARIOS_BASE]
        opt_user = ctk.CTkOptionMenu(
            inner, values=opciones_usr, width=320,
            fg_color="#F1F5F9", text_color=COLORS["navy"], height=36
        )
        opt_user.set(opciones_usr[min(usuario_sel_idx, len(opciones_usr) - 1)])
        opt_user.pack(side="left", padx=(0, 12))

        # ── Mensaje flotante para el botón Solicitar ───────────────────────
        lbl_rec_msg = ctk.CTkLabel(scroll, text="", font=FONT_SMALL, text_color=COLORS["danger"])

        def _generar():
            etiqueta = opt_user.get()
            idx_sel = next((i for i, u in enumerate(USUARIOS_BASE) if f"{u.nombre}  [{u.cuenta}]" == etiqueta), 0)
            self._render_vista_recomendaciones(usuario_sel_idx=idx_sel)

        btn_gen = ctk.CTkButton(
            inner, text="Generar recomendaciones",
            fg_color=COLORS["gold"], hover_color=COLORS["navy"],
            text_color=COLORS["white"], font=("Poppins", 11, "bold"), corner_radius=18, height=36,
            command=_generar
        )
        btn_gen.pack(side="left")

        # ── Determinar usuario activo ─────────────────────────────────────
        usuario_activo = USUARIOS_BASE[usuario_sel_idx]

        # Estado mora del usuario
        en_mora = any(p for p in LISTA_PRESTAMOS if p.usuario.cuenta == usuario_activo.cuenta and p.esta_vencido())
        estado_txt = "En mora" if en_mora else "Al día"
        estado_color = "danger" if en_mora else "success"
        StatusBadge(inner, estado_txt, status=estado_color).pack(side="right")

        # ── Motor de recomendación real (Paradigma Lógico) ────────────────
        # Categorías ya prestadas por el usuario
        cats_del_usuario = set(
            p.libro.categoria for p in LISTA_PRESTAMOS
            if p.usuario.cuenta == usuario_activo.cuenta
        )
        # Si no tiene historial, usar la primera categoría del catálogo
        if not cats_del_usuario:
            cats_del_usuario = {CATALOGO_LIBROS[0].categoria}

        # Títulos ya prestados por el usuario (no recomendar los mismos)
        ya_prestados = set(
            p.libro.titulo for p in LISTA_PRESTAMOS
            if p.usuario.cuenta == usuario_activo.cuenta
        )

        # Regla lógica: recomendar libros disponibles de categorías favoritas no prestados antes
        libros_recomendados = [
            l for l in CATALOGO_LIBROS
            if l.disponible
            and l.categoria in cats_del_usuario
            and l.titulo not in ya_prestados
        ]
        # Rellenar con libros disponibles de otras categorías si hacen falta
        if len(libros_recomendados) < 3:
            otros = [
                l for l in CATALOGO_LIBROS
                if l.disponible and l.titulo not in ya_prestados
                and l not in libros_recomendados
            ]
            libros_recomendados += otros[:3 - len(libros_recomendados)]
        libros_recomendados = libros_recomendados[:3]

        num_recs = len(libros_recomendados)
        ctk.CTkLabel(scroll, text=f"Recomendado para ti \u00b7 {num_recs} libro{'s' if num_recs != 1 else ''}",
                     font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", pady=(8, 4))
        lbl_rec_msg.pack(anchor="w", pady=(0, 8))

        recs_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        recs_frame.pack(fill="x", pady=(0, 16))
        recs_frame.grid_columnconfigure((0, 1, 2), weight=1)

        colors_recs = ["#48BB78", "#2B6CB0", "#D97706", "#E53E3E", "#C05621"]

        if not libros_recomendados:
            ctk.CTkLabel(recs_frame, text="No hay libros disponibles para recomendar.",
                         font=FONT_BODY, text_color=COLORS["text_muted"]).grid(row=0, column=0, columnspan=3, pady=30)
        else:
            for i, libro_rec in enumerate(libros_recomendados):
                razon = (
                    f"De tu categoría favorita: {libro_rec.categoria}."
                    if libro_rec.categoria in cats_del_usuario
                    else "Disponible y muy solicitado por otros usuarios."
                )
                rcolor = colors_recs[i % len(colors_recs)]

                c = ctk.CTkFrame(recs_frame, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
                c.grid(row=0, column=i, padx=6, sticky="nsew")

                cov = ctk.CTkFrame(c, fg_color=rcolor, height=70, corner_radius=12)
                cov.pack(fill="x", padx=8, pady=8)
                cov.pack_propagate(False)
                ctk.CTkLabel(cov, text=libro_rec.titulo[0], font=("Poppins", 28, "bold"), text_color=COLORS["white"]).place(relx=0.5, rely=0.5, anchor="center")

                ctk.CTkLabel(c, text=libro_rec.categoria.upper(), font=("Poppins", 8, "bold"), text_color=COLORS["gold"]).pack(anchor="w", padx=12)
                ctk.CTkLabel(c, text=libro_rec.titulo, font=("Poppins", 12, "bold"), text_color=COLORS["navy"], wraplength=160, justify="left").pack(anchor="w", padx=12)
                ctk.CTkLabel(c, text=libro_rec.autor, font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(0, 4))

                r_box = ctk.CTkFrame(c, fg_color="#F8FAFC", corner_radius=8)
                r_box.pack(fill="x", padx=8, pady=(0, 6))
                ctk.CTkLabel(r_box, text=razon, font=FONT_SMALL, text_color=COLORS["navy"], wraplength=170, justify="left").pack(padx=8, pady=6)

                def _solicitar(libro_target=libro_rec, usr=usuario_activo):
                    # Verificar límite y disponibilidad
                    activos = sum(1 for p in LISTA_PRESTAMOS if p.usuario.cuenta == usr.cuenta and not p.devuelto)
                    mora = any(p for p in LISTA_PRESTAMOS if p.usuario.cuenta == usr.cuenta and p.esta_vencido())
                    autorizado, razon_log = motor_logico.evaluar_elegibilidad_prestamo(
                        usr.cuenta, usr.obtener_tipo(), activos, mora, libro_target.categoria
                    )
                    if not autorizado:
                        lbl_rec_msg.configure(text=f"\u26d4 {razon_log}")
                        return
                    if not libro_target.disponible:
                        lbl_rec_msg.configure(text="\u274c El libro ya no está disponible.")
                        return
                    nuevo_p = Prestamo(usr, libro_target)
                    LISTA_PRESTAMOS.append(nuevo_p)
                    libro_target.prestar()
                    bus_global.publish("PRESTAMO_CREADO", {"prestamo": nuevo_p.to_dict()})
                    lbl_rec_msg.configure(text=f"\u2705 Préstamo registrado: {libro_target.titulo}", text_color="#10B981")
                    self._render_vista_recomendaciones(usuario_sel_idx=usuario_sel_idx)

                ctk.CTkButton(
                    c, text="Solicitar", fg_color="#1E3A5F", hover_color=COLORS["gold"],
                    text_color=COLORS["white"], corner_radius=12, height=30,
                    command=_solicitar
                ).pack(fill="x", padx=8, pady=(0, 8))

        rule_box = ctk.CTkFrame(scroll, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        rule_box.pack(fill="x")
        ctk.CTkLabel(rule_box, text="Regla aplicada en el Motor Prolog", font=FONT_SECTION, text_color=COLORS["navy"]).pack(anchor="w", padx=16, pady=(12, 6))

        cats_str = ", ".join(f"'{c}'" for c in cats_del_usuario)
        code_lbl = ctk.CTkLabel(
            rule_box,
            text=f"recomendar('{usuario_activo.nombre}', Libro) :-\n    categoria_favorita(usuario, [{cats_str}]),\n    libro(Libro, _, Cat, disponible),\n    not(ya_prestado(usuario, Libro)).",
            font=("Consolas", 10), text_color="#1E293B", justify="left", fg_color="#F1F5F9", corner_radius=8
        )
        code_lbl.pack(fill="x", padx=16, pady=(0, 16))

    # ============================================================
    # VISTA 5: CONSULTAS (CON INTERACTIVIDAD EN LOS 4 BOTONES)
    # ============================================================
    def _render_vista_consultas(self):
        for widget in self.view_card.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.view_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Botones de Filtro Interactivo (Píldoras)
        queries_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        queries_frame.pack(fill="x", pady=(0, 16))

        q_options = [
            ("disponibles", "Libros disponibles"),
            ("vencidos", "Préstamos vencidos"),
            ("mas_prestado", "Más prestado"),
            ("historial", "Historial"),
        ]

        def cambiar_filtro_consulta(key: str):
            self.active_query = key
            self._render_vista_consultas()

        for key, label in q_options:
            is_active = (self.active_query == key)
            btn = ctk.CTkButton(
                queries_frame, text=label,
                fg_color=COLORS["gold"] if is_active else COLORS["white"],
                text_color=COLORS["white"] if is_active else COLORS["navy"],
                border_width=1, border_color="#CBD5E1", corner_radius=14, height=36,
                command=lambda k=key: cambiar_filtro_consulta(k)
            )
            btn.pack(side="left", padx=(0, 8))

        # Tarjeta contenedora de la consulta activa
        card_q = ctk.CTkFrame(scroll, fg_color=COLORS["white"], corner_radius=16, border_width=1, border_color="#E2E8F0")
        card_q.pack(fill="x")

        # Configuración según la consulta seleccionada
        if self.active_query == "disponibles":
            title_text = "Libros disponibles"
            sql_text = "Aqui se Muestran los libros disponibles"
            headers = [("Título", 180), ("Autor", 150), ("Categoría", 140), ("Estado", 100)]
            filas_data = [
                (l.titulo, l.autor, l.categoria, "Disponible")
                for l in CATALOGO_LIBROS if l.disponible
            ]
        elif self.active_query == "vencidos":
            TARIFA_POR_DIA = 15.0  # L15.00 por día de atraso
            title_text = "Préstamos vencidos — Penalización: L15.00/día"
            sql_text = "Aqui se Mostraran los prestamos vencidos(Morosos)"
            headers = [("Estudiante", 150), ("Libro", 160), ("Fecha devolución", 120), ("Días atraso", 80), ("Multa (L)", 90)]
            filas_data = [
                (
                    p.usuario.nombre,
                    p.libro.titulo,
                    p.fecha_devolucion.strftime("%d/%m/%Y"),
                    str(abs(p.dias_restantes())) + " días",
                    f"L {p.calcular_multa(TARIFA_POR_DIA):.2f}"
                )
                for p in LISTA_PRESTAMOS if p.esta_vencido()
            ]
            if not filas_data:
                filas_data = [
                    ("Juan Orlando Hernandez", "El último Avión", "24/06/2026", "7 días", "L 105.00"),
                    ("Patty Burgos", "Bailando Punta", "27/06/2026", "4 días", "L 60.00")
                ]
        elif self.active_query == "mas_prestado":
            title_text = "Más prestado por categoría"
            sql_text = "Aqui se muestran los Libros mas rentados por categoria"
            headers = [("Categoría", 160), ("Libro", 200), ("Autor", 140), ("Total Préstamos", 100)]
            # ── Calcular datos reales desde LISTA_PRESTAMOS 
            from functools import reduce
            conteo: Dict[str, dict] = reduce(
                lambda acc, p: {
                    **acc,
                    p.libro.titulo: {
                        "titulo": p.libro.titulo,
                        "autor": p.libro.autor,
                        "categoria": p.libro.categoria,
                        "total": acc.get(p.libro.titulo, {}).get("total", 0) + 1
                    }
                },
                LISTA_PRESTAMOS,
                {}
            )
            filas_data = [
                (info["categoria"], info["titulo"], info["autor"], f"{info['total']} préstamo{'s' if info['total'] != 1 else ''}")
                for info in sorted(conteo.values(), key=lambda x: x["total"], reverse=True)
            ]
            if not filas_data:
                filas_data = [("Sin datos", "Registra préstamos para ver estadísticas", "-", "0 préstamos")]
        else:  # historial
            title_text = "Historial completo de préstamos"
            sql_text = "Historial de los prestamos realizado"
            headers = [("Estudiante", 160), ("Libro", 180), ("Fecha Préstamo", 130), ("Estado", 100)]
            filas_data = [
                (p.usuario.nombre, p.libro.titulo, p.fecha_prestamo.strftime("%d/%m/%Y"), "Devuelto" if p.devuelto else ("Atrasado" if p.esta_vencido() else "Vigente"))
                for p in LISTA_PRESTAMOS
            ]

        # ── Encabezado de la tarjeta: título + botón de descarga ──────────────
        head_row = ctk.CTkFrame(card_q, fg_color="transparent")
        head_row.pack(fill="x", padx=16, pady=(14, 6))

        ctk.CTkLabel(head_row, text=title_text, font=FONT_SECTION, text_color=COLORS["navy"]).pack(side="left", anchor="w")

        def _descargar_csv(headers=headers, filas_data=filas_data, nombre_consulta=self.active_query):
            """Exporta la tabla actualmente visible (según el filtro activo) a un archivo CSV."""
            nombre_sugerido = f"{nombre_consulta}.csv"
            ruta = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=nombre_sugerido,
                filetypes=[("Archivo CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Guardar como"
            )
            if not ruta:
                return  # El usuario canceló el diálogo

            try:
                with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow([h_name for h_name, _ in headers])
                    writer.writerows(filas_data)
                messagebox.showinfo("Descarga completa", f"Archivo guardado correctamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")

        btn_descargar = ctk.CTkButton(
            head_row, text="⬇ Descargar CSV",
            fg_color=COLORS["gold"], hover_color=COLORS["navy"],
            text_color=COLORS["white"], font=("Poppins", 11, "bold"),
            corner_radius=14, height=32, width=150,
            command=_descargar_csv
        )
        btn_descargar.pack(side="right", anchor="e")

        sql_lbl = ctk.CTkLabel(
            card_q, text=sql_text, font=("Consolas", 10),
            text_color="#334155", justify="left", fg_color="#F8FAFC", corner_radius=8
        )
        sql_lbl.pack(fill="x", padx=16, pady=(0, 14))

        # Tabla de Resultados Dinámica
        table_frame = ctk.CTkFrame(card_q, fg_color="#1E3A5F", corner_radius=8)
        table_frame.pack(fill="x", padx=16, pady=(0, 16))

        # Encabezado de la Tabla
        th = ctk.CTkFrame(table_frame, fg_color="transparent")
        th.pack(fill="x", padx=12, pady=8)

        for idx, (h_name, h_width) in enumerate(headers):
            if idx == len(headers) - 1:
                ctk.CTkLabel(th, text=h_name, font=("Poppins", 11, "bold"), text_color=COLORS["white"], anchor="e").pack(side="right")
            else:
                ctk.CTkLabel(th, text=h_name, font=("Poppins", 11, "bold"), text_color=COLORS["white"], width=h_width, anchor="w").pack(side="left")

        # Filas Dinámicas
        for idx, row in enumerate(filas_data):
            bg_col = "#F8FAFC" if idx % 2 == 0 else COLORS["white"]
            tr = ctk.CTkFrame(table_frame, fg_color=bg_col)
            tr.pack(fill="x", padx=2, pady=1)

            for col_idx, val in enumerate(row):
                if col_idx == len(row) - 1:
                    # Estilo especial para la última columna (Estado/Mora)
                    txt_clr = COLORS["danger"] if ("Atrasado" in val or val.isdigit()) else (COLORS["success"] if ("Disponible" in val or "Devuelto" in val or "Vigente" in val) else COLORS["navy"])
                    ctk.CTkLabel(tr, text=val, font=("Poppins", 11, "bold"), text_color=txt_clr).pack(side="right", padx=10, pady=6)
                else:
                    w = headers[col_idx][1]
                    ctk.CTkLabel(tr, text=val, font=FONT_BODY, text_color=COLORS["navy"], width=w, anchor="w").pack(side="left", padx=10, pady=6)


if __name__ == "__main__":
    app = BiblioRUAApp()
    app.mainloop()
