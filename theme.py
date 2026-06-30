"""
theme.py
--------
Fuente única de verdad para la estética visual de la app, inspirada
en la interfaz de Persona 5 Royal: negro profundo, rojo vibrante,
blanco limpio, y formas angulares/diagonales en vez de bordes
redondeados.

Este archivo NO construye pantallas. Solo define colores, fuentes
y estilos reutilizables que `components.py` y las vistas importarán
directamente, ej.:

    from theme import Colors, TextStyles, Spacing
"""

import flet as ft


class Colors:
    """
    Paleta de colores. Deliberadamente reducida (negro, rojo, blanco
    + un par de grises de apoyo) para mantener la identidad visual
    fuerte y consistente de P5R, en vez de un set de colores genérico.
    """

    # --- Núcleo de la paleta ---
    BLACK = "#1A1A1A"          # Fondo principal de la app
    BLACK_SOFT = "#242424"     # Fondo de tarjetas/superficies elevadas
    BLACK_DEEP = "#0D0D0D"     # Fondos de máximo contraste (barras, headers)

    RED = "#E3131B"            # Rojo vibrante, color de acento principal
    RED_DARK = "#A50E14"       # Variante oscura del rojo (estados presionados/sombras)
    RED_GLOW = "#FF3B3B"       # Variante clara del rojo (hover/focus, resaltados)

    WHITE = "#FFFFFF"          # Texto principal sobre fondo negro
    WHITE_OFF = "#E8E8E8"      # Texto secundario, ligeramente apagado

    # --- Grises de apoyo (texto terciario, bordes sutiles, deshabilitado) ---
    GRAY = "#7A7A7A"
    GRAY_DARK = "#3D3D3D"

    # --- Colores funcionales, mapeados al estado de un anime ---
    # (estado_color_key en models.py devuelve "pendiente" | "viendo" | "completado")
    ESTADO = {
        "pendiente": GRAY,
        "viendo": RED,
        "completado": WHITE,
    }

    FAVORITO = RED_GLOW        # Color del ícono de estrella/corazón favorito
    ERROR = "#FF4C4C"          # Mensajes de validación/errores de formulario


class Fonts:
    """
    P5R usa una tipografía display condensada, en mayúsculas, con
    itálicas agresivas para títulos. Por ahora usamos una fuente del
    sistema como placeholder (BOLD + ITALIC simulan el efecto), y
    dejamos preparado el nombre `DISPLAY` para cuando agreguemos un
    archivo .ttf real en assets/fonts/ (ej. una condensada tipo
    "Anton", "Oswald" o "Bebas Neue", que son las que más se acercan
    al estilo del juego y son de uso libre).
    """

    # Nombre que se registrará en page.fonts cuando main.py cargue
    # un archivo .ttf real desde assets/fonts/. Hasta entonces, Flet
    # usará la fuente del sistema como fallback automático.
    DISPLAY = "P5R-Display"

    # Fuente para texto de cuerpo (legible, sin tanto carácter)
    BODY = None  # None = fuente por defecto de la plataforma


class Spacing:
    """
    Escala de espaciado consistente. Evita que cada vista invente
    sus propios números de padding/margin al azar.
    """

    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


class Shape:
    """
    Constantes para lograr el look angular/diagonal de P5R.
    Importante: en P5R casi no hay esquinas redondeadas; los cortes
    son diagonales y agresivos. components.py usará estos valores
    al construir Containers, Stacks y transformaciones rotadas.
    """

    BORDER_RADIUS_NONE = 0       # Las tarjetas/botones NO llevan esquinas redondeadas
    BORDER_RADIUS_SOFT = 2       # Excepción mínima para inputs de texto (legibilidad)

    SKEW_ANGLE_DEG = -8          # Ángulo de inclinación característico para bloques de acento
    DIVIDER_THICKNESS = 3        # Grosor de líneas divisorias estilo "recorte"


class TextStyles:
    """
    Estilos de texto pre-armados (ft.TextStyle). components.py y las
    vistas los usan así:

        ft.Text("DEMON SLAYER", style=TextStyles.title())
    """

    @staticmethod
    def title() -> ft.TextStyle:
        """Títulos grandes de pantalla, ej. encabezado de Home."""
        return ft.TextStyle(
            size=32,
            weight=ft.FontWeight.W_900,
            italic=True,
            color=Colors.WHITE,
            font_family=Fonts.DISPLAY,
        )

    @staticmethod
    def subtitle() -> ft.TextStyle:
        """Subtítulos de sección, ej. 'PENDIENTES', 'COMPLETADOS'."""
        return ft.TextStyle(
            size=18,
            weight=ft.FontWeight.BOLD,
            italic=True,
            color=Colors.RED,
            font_family=Fonts.DISPLAY,
        )

    @staticmethod
    def card_title() -> ft.TextStyle:
        """Título de cada tarjeta de anime en la lista."""
        return ft.TextStyle(
            size=16,
            weight=ft.FontWeight.BOLD,
            color=Colors.WHITE,
        )

    @staticmethod
    def body() -> ft.TextStyle:
        """Texto general, comentarios, descripciones."""
        return ft.TextStyle(
            size=14,
            weight=ft.FontWeight.NORMAL,
            color=Colors.WHITE_OFF,
        )

    @staticmethod
    def caption() -> ft.TextStyle:
        """Texto pequeño/secundario, ej. etiquetas de estado."""
        return ft.TextStyle(
            size=12,
            weight=ft.FontWeight.W_600,
            color=Colors.GRAY,
        )

    @staticmethod
    def button() -> ft.TextStyle:
        """Texto dentro de botones de acción."""
        return ft.TextStyle(
            size=14,
            weight=ft.FontWeight.W_800,
            italic=True,
            color=Colors.WHITE,
        )


# ---------------------------------------------------------------------------
# Tema general de la página (lo usará main.py al configurar ft.Page.theme)
# ---------------------------------------------------------------------------

def get_page_theme() -> ft.Theme:
    """
    Construye el ft.Theme base que main.py asignará a page.theme.
    Centraliza aquí el color_scheme para que toda la app (inputs,
    switches, sliders nativos de Flet) herede automáticamente la
    paleta P5R sin tener que configurarla widget por widget.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=Colors.RED,
            on_primary=Colors.WHITE,
            secondary=Colors.WHITE,
            on_secondary=Colors.BLACK,
            surface=Colors.BLACK_SOFT,
            on_surface=Colors.WHITE,
            error=Colors.ERROR,
        ),
        font_family=Fonts.DISPLAY,
    )
