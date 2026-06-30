"""
models.py
---------
Define la estructura de datos que viaja entre database.py y la UI.

Este archivo NO sabe nada de SQLite ni de Flet: es solo el "molde"
(contrato de datos) que usan ambas capas para entenderse entre sí.
"""

from dataclasses import dataclass, asdict
import sqlite3

# Fuente única de verdad para los valores permitidos.
# database.py los importa de aquí en lugar de redefinirlos.
ESTADOS_VALIDOS = ("Pendiente", "Viendo", "Completado")
TIPOS_VALIDOS = ("Anime", "Película")


@dataclass
class Anime:
    """
    Representa un único registro de la lista del usuario.
    Se construye normalmente a partir de una fila de SQLite con
    Anime.from_row(), o manualmente al crear un registro nuevo
    antes de guardarlo en la base de datos.
    """

    id: int
    titulo: str
    tipo: str = "Anime"
    estado: str = "Pendiente"
    calificacion: float = 0.0
    favorito: bool = False
    comentario: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Anime":
        """
        Convierte una fila cruda de sqlite3 (sqlite3.Row) en un
        objeto Anime. Aquí es donde se hace la traducción
        INTEGER (0/1) -> bool para el campo `favorito`.
        """
        return cls(
            id=row["id"],
            titulo=row["titulo"],
            tipo=row["tipo"],
            estado=row["estado"],
            calificacion=row["calificacion"],
            favorito=bool(row["favorito"]),
            comentario=row["comentario"],
        )

    @property
    def calificacion_texto(self) -> str:
        """
        Texto listo para mostrar en la UI.
        Si calificacion es 0, se interpreta como "todavía sin calificar"
        en vez de mostrar literalmente "0.0".
        """
        if self.calificacion <= 0:
            return "Sin calificar"
        return f"{self.calificacion:.1f} / 10"

    @property
    def es_pelicula(self) -> bool:
        """Atajo legible para la UI: evita comparar strings por todos lados."""
        return self.tipo == "Película"

    @property
    def estado_color_key(self) -> str:
        """
        Devuelve una clave corta según el estado, pensada para que
        theme.py la use luego y decida qué color de acento asignarle
        (ej. rojo para 'Viendo', blanco para 'Completado', gris para
        'Pendiente'). models.py NO decide el color, solo da la clave.
        """
        return {
            "Pendiente": "pendiente",
            "Viendo": "viendo",
            "Completado": "completado",
        }.get(self.estado, "pendiente")

    def to_dict(self) -> dict:
        """Útil si en algún momento necesitamos serializar a JSON (ej. exportar/respaldar)."""
        return asdict(self)


def validar_anime(titulo: str, tipo: str, estado: str, calificacion: float) -> list[str]:
    """
    Validaciones simples antes de guardar un registro (se usará desde
    add_view.py y detail_view.py). Devuelve una lista de errores;
    si la lista está vacía, los datos son válidos.
    """
    errores = []

    if not titulo or not titulo.strip():
        errores.append("El título no puede estar vacío.")

    if tipo not in TIPOS_VALIDOS:
        errores.append(f"Tipo inválido. Debe ser uno de: {', '.join(TIPOS_VALIDOS)}.")

    if estado not in ESTADOS_VALIDOS:
        errores.append(f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS_VALIDOS)}.")

    if not (0 <= calificacion <= 10):
        errores.append("La calificación debe estar entre 0 y 10.")

    return errores
