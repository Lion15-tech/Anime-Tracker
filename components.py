"""
components.py
--------------
Widgets reutilizables que encarnan la estética visual de Persona 5
Royal: cortes diagonales, contraste fuerte negro/rojo/blanco, y
tipografía dinámica en mayúsculas.

Este archivo SOLO construye piezas visuales reutilizables. No conoce
la base de datos ni la navegación: recibe un objeto Anime (o datos
simples) y un callback, y devuelve un control de Flet ya armado.

Truco usado para el look "angular":
P5R no usa esquinas redondeadas; usa cortes diagonales agresivos.
En Flet logramos esto con un patrón simple y estable (no depende de
APIs de dibujo experimentales):
    1. Un ft.Container exterior con clip_behavior=HARD_EDGE
       (actúa como "ventana" rectangular que recorta lo que se
       salga de sus bordes).
    2. Dentro, un ft.Stack con una franja de color ROTADA
       (ft.Rotate) y posicionada fuera de los límites normales
       (left/top negativos). Al rotarla y quedar parcialmente fuera,
       el recorte del contenedor exterior genera el efecto de
       "flash diagonal" típico de los menús del juego.
"""

import math
from typing import Callable, Optional

import flet as ft

from models import Anime
from theme import Colors, Shape, Spacing, TextStyles


# ---------------------------------------------------------------------------
# Helper interno: la franja diagonal de acento (el "flash" rojo de P5R)
# ---------------------------------------------------------------------------

def _diagonal_accent(color: str = Colors.RED, size: int = 70) -> ft.Container:
    """
    Construye la franja diagonal decorativa que se coloca en una
    esquina de tarjetas/botones para simular el corte angular de P5R.
    Debe usarse siempre dentro de un ft.Stack, y ese Stack debe estar
    envuelto en un Container con clip_behavior=ft.ClipBehavior.HARD_EDGE
    para que el recorte se vea limpio.
    """
    return ft.Container(
        width=size,
        height=size,
        bgcolor=color,
        rotate=ft.Rotate(angle=math.radians(Shape.SKEW_ANGLE_DEG * 5)),
        left=-size * 0.35,
        top=-size * 0.35,
    )


# ---------------------------------------------------------------------------
# Badge de estado (Pendiente / Viendo / Completado)
# ---------------------------------------------------------------------------

def status_badge(estado: str) -> ft.Container:
    """
    Etiqueta angular con el estado del anime. El color se decide
    según el diccionario Colors.ESTADO, que ya está sincronizado con
    `estado_color_key` de models.py.
    """
    color_key = {"Pendiente": "pendiente", "Viendo": "viendo", "Completado": "completado"}.get(
        estado, "pendiente"
    )
    color = Colors.ESTADO[color_key]

    return ft.Container(
        content=ft.Text(
            estado.upper(),
            style=TextStyles.caption(),
            color=Colors.BLACK if color == Colors.WHITE else Colors.WHITE,
        ),
        bgcolor=color,
        padding=ft.Padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS / 2),
        border_radius=Shape.BORDER_RADIUS_NONE,
        # Leve inclinación para que incluso la etiqueta se sienta "dinámica"
        rotate=ft.Rotate(angle=math.radians(-3)),
    )


# ---------------------------------------------------------------------------
# Estrellas de calificación (escala 0-10 -> se muestra como 5 estrellas)
# ---------------------------------------------------------------------------

def rating_stars(calificacion: float, size: int = 16) -> ft.Row:
    """
    Convierte la calificación 0-10 a una fila de 5 estrellas
    (cada estrella = 2 puntos). Si calificacion es 0, muestra las
    5 estrellas vacías junto con el texto "Sin calificar".
    """
    estrellas_llenas = round(calificacion / 2)
    iconos = []

    for i in range(5):
        lleno = i < estrellas_llenas
        iconos.append(
            ft.Icon(
                name=ft.Icons.STAR if lleno else ft.Icons.STAR_BORDER,
                color=Colors.RED if lleno else Colors.GRAY,
                size=size,
            )
        )

    if calificacion <= 0:
        iconos.append(
            ft.Text("Sin calificar", style=TextStyles.caption(), italic=True)
        )

    return ft.Row(controls=iconos, spacing=2)


# ---------------------------------------------------------------------------
# Ícono de favorito
# ---------------------------------------------------------------------------

def favorite_icon(favorito: bool, on_click: Optional[Callable] = None, size: int = 22) -> ft.IconButton:
    """
    Ícono de corazón/estrella para marcar favoritos. Si se pasa
    on_click, se vuelve interactivo (para usarlo directo desde la
    tarjeta sin tener que entrar al detalle).
    """
    return ft.IconButton(
        icon=ft.Icons.FAVORITE if favorito else ft.Icons.FAVORITE_BORDER,
        icon_color=Colors.FAVORITO if favorito else Colors.GRAY,
        icon_size=size,
        on_click=on_click,
        tooltip="Quitar de favoritos" if favorito else "Marcar como favorito",
    )


# ---------------------------------------------------------------------------
# Tarjeta principal de anime (la pieza más importante de la Home)
# ---------------------------------------------------------------------------

def anime_card(
    anime: Anime,
    on_click: Optional[Callable[[int], None]] = None,
    on_toggle_favorite: Optional[Callable[[int], None]] = None,
) -> ft.Container:
    """
    Tarjeta angular para un anime/película. Al tocarla (fuera del
    ícono de favorito) se espera navegar al detalle.

    on_click recibe el id del anime.
    on_toggle_favorite recibe el id del anime (para marcar/desmarcar
    favorito sin abrir el detalle).
    """
    contenido = ft.Row(
        controls=[
            ft.Column(
                expand=True,
                spacing=4,
                controls=[
                    ft.Text(
                        anime.titulo.upper(),
                        style=TextStyles.card_title(),
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row(
                        controls=[
                            status_badge(anime.estado),
                            ft.Text(
                                anime.tipo,
                                style=TextStyles.caption(),
                            ),
                        ],
                        spacing=Spacing.SM,
                    ),
                    rating_stars(anime.calificacion),
                ],
            ),
            favorite_icon(
                favorito=anime.favorito,
                on_click=(lambda e: on_toggle_favorite(anime.id)) if on_toggle_favorite else None,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    tarjeta_base = ft.Container(
        content=contenido,
        bgcolor=Colors.BLACK_SOFT,
        padding=ft.Padding.all(Spacing.MD),
        border=ft.Border.only(left=ft.BorderSide(4, Colors.RED)),
        border_radius=Shape.BORDER_RADIUS_NONE,
    )

    # Stack + clip para el flash diagonal en la esquina superior derecha
    return ft.Container(
        content=ft.Stack(
            controls=[
                tarjeta_base,
                _diagonal_accent(color=Colors.RED_DARK, size=50),
            ]
        ),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        on_click=(lambda e: on_click(anime.id)) if on_click else None,
        ink=True,
        margin=ft.Margin.only(bottom=Spacing.SM),
    )


# ---------------------------------------------------------------------------
# Encabezado de sección (ej. "PENDIENTES", "FAVORITOS")
# ---------------------------------------------------------------------------

def section_header(texto: str) -> ft.Column:
    """
    Encabezado de sección con una línea de acento roja debajo,
    inspirado en los separadores de menú de P5R.
    """
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(texto.upper(), style=TextStyles.subtitle()),
            ft.Container(
                height=Shape.DIVIDER_THICKNESS,
                width=80,
                bgcolor=Colors.RED,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Botón primario angular
# ---------------------------------------------------------------------------

def primary_button(
    texto: str,
    on_click: Optional[Callable] = None,
    icon: Optional[str] = None,
    expand: bool = False,
) -> ft.Container:
    """
    Botón de acción principal (ej. "GUARDAR", "AGREGAR ANIME").
    Construido como Container en vez de ft.ElevatedButton para tener
    control total sobre el corte angular y el estilo de texto.
    """
    contenido = [ft.Text(texto.upper(), style=TextStyles.button())]
    if icon:
        contenido.insert(0, ft.Icon(name=icon, color=Colors.WHITE, size=18))

    return ft.Container(
        content=ft.Row(
            controls=contenido,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=Spacing.SM,
        ),
        bgcolor=Colors.RED,
        padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.SM),
        border_radius=Shape.BORDER_RADIUS_NONE,
        on_click=on_click,
        ink=True,
        expand=expand,
        # Pequeña inclinación para que incluso el botón se sienta "en movimiento"
        margin=ft.Margin.symmetric(vertical=Spacing.XS),
    )


# ---------------------------------------------------------------------------
# Estado vacío (ej. cuando un filtro no devuelve resultados)
# ---------------------------------------------------------------------------

def empty_state(mensaje: str, icon: str = ft.Icons.SEARCH_OFF) -> ft.Column:
    """Mensaje centrado para cuando una lista filtrada queda vacía."""
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=Spacing.SM,
        controls=[
            ft.Icon(name=icon, color=Colors.GRAY, size=48),
            ft.Text(mensaje, style=TextStyles.body(), text_align=ft.TextAlign.CENTER),
        ],
    )
