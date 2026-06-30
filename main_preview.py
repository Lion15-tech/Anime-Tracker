"""
main_preview.py
----------------
ESTE ARCHIVO ES TEMPORAL. No es el main.py definitivo del proyecto
(ese lo construiremos al final, con navegación completa entre
vistas). Su único propósito es renderizar algunos componentes ya
construidos (anime_card, section_header, primary_button, etc.) para
que puedas ver el estilo P5R en pantalla y pedir ajustes antes de
seguir construyendo las vistas reales.

Cómo correrlo:
    1. Asegúrate de tener Flet instalado:  pip install flet
    2. Desde la carpeta del proyecto:      python main_preview.py
       (o "flet run main_preview.py" si prefieres ver hot-reload)
"""

import flet as ft

import database as db
import components as comp
from theme import Colors, Spacing, get_page_theme


def main(page: ft.Page) -> None:
    # --- Configuración base de la página ---
    page.title = "AnimeList P5R — Vista previa de estilo"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_page_theme()
    page.bgcolor = Colors.BLACK
    page.padding = Spacing.MD
    page.scroll = ft.ScrollMode.AUTO

    # --- Preparamos datos reales de tu lista para la prueba ---
    db.init_db()
    db.seed_database()  # No duplica nada si ya existen los 84 registros

    todos = db.get_all_animes()

    # Tomamos algunos ejemplos variados para ver distintos estados/casos:
    # uno completado y calificado, uno "viendo", uno pendiente sin calificar.
    ejemplo_completado = next((a for a in todos if a.estado == "Completado"), None)
    ejemplo_viendo = next((a for a in todos if a.estado == "Viendo"), None)
    ejemplo_pendiente = next((a for a in todos if a.estado == "Pendiente"), None)

    # Simulamos que el usuario ya calificó y marcó como favorito el
    # primer ejemplo, solo para ver cómo se ve una tarjeta "llena"
    # (esto es temporal, no se guarda permanentemente para el preview)
    if ejemplo_completado:
        ejemplo_completado.calificacion = 9.5
        ejemplo_completado.favorito = True
        ejemplo_completado.comentario = "Excelente animación y banda sonora."

    # --- Callback de prueba: solo imprime en consola, sin lógica real aún ---
    def manejar_click_tarjeta(anime_id: int) -> None:
        print(f"[preview] Se tocó la tarjeta del anime id={anime_id}")

    def manejar_toggle_favorito(anime_id: int) -> None:
        print(f"[preview] Se intentó cambiar favorito del anime id={anime_id}")

    def manejar_click_boton(e: ft.ControlEvent) -> None:
        print("[preview] Se tocó el botón primario")

    # --- Armamos la pantalla de prueba ---
    tarjetas_ejemplo = []
    for anime in (ejemplo_completado, ejemplo_viendo, ejemplo_pendiente):
        if anime is not None:
            tarjetas_ejemplo.append(
                comp.anime_card(
                    anime,
                    on_click=manejar_click_tarjeta,
                    on_toggle_favorite=manejar_toggle_favorito,
                )
            )

    page.add(
        ft.Column(
            spacing=Spacing.LG,
            controls=[
                comp.section_header("Vista previa de estilo"),
                ft.Text(
                    f"Total de animes/películas en tu base de datos: {len(todos)}",
                    color=Colors.WHITE_OFF,
                    size=12,
                ),
                comp.section_header("Ejemplos de tarjeta"),
                ft.Column(controls=tarjetas_ejemplo, spacing=Spacing.SM),
                comp.section_header("Botón primario"),
                comp.primary_button("Agregar anime", on_click=manejar_click_boton, icon=ft.Icons.ADD),
                comp.section_header("Estado vacío (ejemplo)"),
                comp.empty_state("No hay animes que coincidan con este filtro."),
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)
