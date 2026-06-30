"""
database.py
------------
Capa de acceso a datos del proyecto AnimeList P5R.

Responsabilidad única de este archivo: hablar con SQLite.
NO importa Flet, NO sabe nada de colores ni de pantallas.
Cualquier otro módulo que necesite datos llama a las funciones de aquí.

Esquema de la tabla `animes`:
    id            INTEGER  -> PK autoincremental
    titulo        TEXT     -> nombre del anime/película
    tipo          TEXT     -> "Anime" | "Película"
    estado        TEXT     -> "Pendiente" | "Viendo" | "Completado"
    calificacion  REAL     -> 0.0 a 10.0 (0 = sin calificar)
    favorito      INTEGER  -> 0 o 1 (se usa como booleano)
    comentario    TEXT     -> notas personales del usuario
"""

import sqlite3
from pathlib import Path

from models import Anime, ESTADOS_VALIDOS, TIPOS_VALIDOS  # noqa: F401  (se re-exportan para quien importe database)

# Ruta del archivo de base de datos. Vive junto a este script.
# (Cuando empaquetemos para móvil, ajustaremos esta ruta a la carpeta
# de almacenamiento de la app; por ahora, local es lo más simple).
DB_PATH = Path(__file__).parent / "animelist.db"


def get_connection() -> sqlite3.Connection:
    """
    Crea y devuelve una conexión a la base de datos.
    row_factory = sqlite3.Row permite acceder a columnas por nombre,
    ej. row["titulo"], en lugar de por índice numérico.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Crea la tabla `animes` si no existe todavía.
    Se debe llamar una sola vez al arrancar la app (lo hará main.py).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS animes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo        TEXT    NOT NULL,
            tipo          TEXT    NOT NULL DEFAULT 'Anime',
            estado        TEXT    NOT NULL DEFAULT 'Pendiente',
            calificacion  REAL    NOT NULL DEFAULT 0,
            favorito      INTEGER NOT NULL DEFAULT 0,
            comentario    TEXT    NOT NULL DEFAULT ''
        )
        """
    )
    conn.commit()
    conn.close()


def insert_anime(
    titulo: str,
    tipo: str = "Anime",
    estado: str = "Pendiente",
    calificacion: float = 0.0,
    favorito: bool = False,
    comentario: str = "",
) -> int:
    """
    Inserta un nuevo registro y devuelve el id generado.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO animes (titulo, tipo, estado, calificacion, favorito, comentario)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (titulo, tipo, estado, calificacion, int(favorito), comentario),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_animes(tipo: str | None = None, estado: str | None = None) -> list[Anime]:
    """
    Devuelve todos los registros como objetos Anime, con filtros
    opcionales por tipo y/o estado. Útil para la pantalla principal
    cuando el usuario filtre por "Solo pendientes", "Solo películas", etc.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM animes WHERE 1=1"
    params: list = []

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if estado:
        query += " AND estado = ?"
        params.append(estado)

    query += " ORDER BY favorito DESC, titulo ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [Anime.from_row(row) for row in rows]


def get_anime_by_id(anime_id: int) -> Anime | None:
    """Devuelve un único registro como objeto Anime por su id, o None si no existe."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM animes WHERE id = ?", (anime_id,))
    row = cursor.fetchone()
    conn.close()
    return Anime.from_row(row) if row is not None else None


def update_anime(
    anime_id: int,
    titulo: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    calificacion: float | None = None,
    favorito: bool | None = None,
    comentario: str | None = None,
) -> None:
    """
    Actualiza solo los campos que se pasen (distintos de None).
    Esto permite, por ejemplo, llamar:
        update_anime(5, calificacion=9.5)
    sin tener que reescribir el resto de los campos del anime.
    """
    actual = get_anime_by_id(anime_id)
    if actual is None:
        raise ValueError(f"No existe un anime con id={anime_id}")

    nuevo_titulo = titulo if titulo is not None else actual.titulo
    nuevo_tipo = tipo if tipo is not None else actual.tipo
    nuevo_estado = estado if estado is not None else actual.estado
    nueva_calificacion = calificacion if calificacion is not None else actual.calificacion
    nuevo_favorito = int(favorito) if favorito is not None else int(actual.favorito)
    nuevo_comentario = comentario if comentario is not None else actual.comentario

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE animes
        SET titulo = ?, tipo = ?, estado = ?, calificacion = ?, favorito = ?, comentario = ?
        WHERE id = ?
        """,
        (nuevo_titulo, nuevo_tipo, nuevo_estado, nueva_calificacion, nuevo_favorito, nuevo_comentario, anime_id),
    )
    conn.commit()
    conn.close()


def delete_anime(anime_id: int) -> None:
    """Elimina un registro por id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM animes WHERE id = ?", (anime_id,))
    conn.commit()
    conn.close()


def count_animes() -> int:
    """Devuelve cuántos registros hay en total. Se usa para decidir si hace falta sembrar datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM animes")
    total = cursor.fetchone()[0]
    conn.close()
    return total


# ---------------------------------------------------------------------------
# SEED: precarga de la lista personal del usuario.
# Solo se ejecuta si la tabla está vacía, para no duplicar datos cada
# vez que se abra la app.
# ---------------------------------------------------------------------------

# (titulo, tipo, estado) -- calificacion, favorito y comentario quedan
# en blanco/default para que el usuario los llene desde la app.
LISTA_INICIAL = [
    # --- Animes vistos (Completado) ---
    ("Cyberpunk Edgerunners", "Anime", "Completado"),
    ("Demon Slayer", "Anime", "Completado"),
    ("Los diarios de la boticaria", "Anime", "Completado"),
    ("Jujutsu Kaisen", "Anime", "Completado"),
    ("Oshi no Ko", "Anime", "Completado"),
    ("JoJo's Bizarre Adventure", "Anime", "Completado"),
    ("Spy x Family", "Anime", "Completado"),
    ("El ascenso del héroe del escudo", "Anime", "Completado"),
    ("My Hero Academia", "Anime", "Completado"),
    ("Call of the Night", "Anime", "Completado"),
    ("Frieren: Beyond Journey's End", "Anime", "Completado"),
    ("Zom 100", "Anime", "Completado"),
    ("Secrets of the Silent Witch", "Anime", "Completado"),
    ("Rascal Does Not Dream of Bunny Girl Senpai", "Anime", "Completado"),
    ("My Dress-Up Darling", "Anime", "Completado"),
    ("Kaguya-sama: Love is War", "Anime", "Completado"),
    ("Kaoru Hana wa Rin to Saku", "Anime", "Completado"),
    ("Mashle", "Anime", "Completado"),
    ("Gachiakuta", "Anime", "Viendo"),
    ("Shingeki no Kyojin", "Anime", "Completado"),
    ("Blue Box", "Anime", "Completado"),
    ("The Eminence in Shadow", "Anime", "Completado"),
    ("Komi-san no puede comunicarse", "Anime", "Completado"),
    ("Kimi ni Todoke", "Anime", "Viendo"),
    ("La asesina del romance", "Anime", "Completado"),
    ("Dan Da Dan", "Anime", "Completado"),
    ("Sakamoto Days", "Anime", "Completado"),
    ("Solo Leveling", "Anime", "Completado"),
    ("Lazarus", "Anime", "Completado"),
    ("Chainsaw Man", "Anime", "Completado"),
    ("Bocchi the Rock!", "Anime", "Completado"),
    ("Your Lie in April", "Anime", "Completado"),
    ("Tengoku Daimakyou", "Anime", "Completado"),
    ("Horimiya", "Anime", "Completado"),
    ("Tokidoki Bosotto Russia-go de Dereru Tonari no Alya-san", "Anime", "Completado"),
    ("To Be Hero X", "Anime", "Completado"),
    ("Devil May Cry (Netflix)", "Anime", "Completado"),
    ("Super Cube", "Anime", "Completado"),
    ("Las quintillizas", "Anime", "Completado"),
    ("You and I are Polar Opposites", "Anime", "Completado"),
    ("Sword Art Online", "Anime", "Completado"),
    ("86 - Eighty Six", "Anime", "Completado"),
    ("Re:Zero", "Anime", "Completado"),
    ("The Daily Life of the Immortal King", "Anime", "Completado"),
    ("Aishiteru Game wo Owarasetai", "Anime", "Completado"),
    ("Classroom of the Elite", "Anime", "Completado"),

    # --- Películas vistas (Completado) ---
    ("Your Name", "Película", "Completado"),
    ("Suzume", "Película", "Completado"),
    ("Weathering with You", "Película", "Completado"),
    ("Quiero comerme tu páncreas", "Película", "Completado"),
    ("Una voz silenciosa", "Película", "Completado"),
    ("Burbujas", "Película", "Completado"),
    ("Amor de gata", "Película", "Completado"),
    ("Josee to Tora to Sakana-tachi", "Película", "Completado"),
    ("Ride Your Wave", "Película", "Completado"),
    ("Natsu e no Tunnel, Sayonara no Deguchi", "Película", "Completado"),

    # --- Animes pendientes ---
    ("Violet Evergarden", "Anime", "Pendiente"),
    ("Doctor Stone", "Anime", "Pendiente"),
    ("Gnosia", "Anime", "Pendiente"),
    ("Fumetsu no Anata e", "Anime", "Pendiente"),
    ("Sanda", "Anime", "Pendiente"),
    ("Kaiju No. 8", "Anime", "Pendiente"),
    ("Clevatess", "Anime", "Pendiente"),
    ("Witch Watch", "Anime", "Pendiente"),
    ("Death Note", "Anime", "Pendiente"),
    ("Uma Musume", "Anime", "Pendiente"),
    ("Wind Breaker", "Anime", "Pendiente"),
    ("Mob Psycho 100", "Anime", "Pendiente"),
    ("Black Clover", "Anime", "Pendiente"),
    ("Tragones y Mazmorras", "Anime", "Pendiente"),
    ("Evangelion", "Anime", "Pendiente"),
    ("No Game No Life", "Anime", "Pendiente"),
    ("Charlotte", "Anime", "Pendiente"),
    ("Rebelión Lunar", "Anime", "Pendiente"),
    ("Suki na Ko ga Megane wo Wasureta", "Anime", "Pendiente"),
    ("Mushoku Tensei", "Anime", "Pendiente"),
    ("Fire Force", "Anime", "Pendiente"),
    ("Toradora!", "Anime", "Pendiente"),
    ("Steins;Gate", "Anime", "Pendiente"),
    ("Nisekoi", "Anime", "Pendiente"),
    ("High Card", "Anime", "Pendiente"),
    ("Mata Korosarete Shimatta", "Anime", "Pendiente"),
    ("Boku ga Aishita Subete no Kimi e", "Anime", "Pendiente"),
    ("Aura: Koga Maryuin's Last War", "Anime", "Pendiente"),
]


def seed_database() -> None:
    """
    Inserta la lista inicial del usuario, pero solo si la tabla está
    vacía (para que al reabrir la app no se dupliquen los 84 registros).
    """
    if count_animes() > 0:
        return  # Ya hay datos, no se vuelve a sembrar.

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO animes (titulo, tipo, estado, calificacion, favorito, comentario)
        VALUES (?, ?, ?, 0, 0, '')
        """,
        LISTA_INICIAL,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Prueba rápida manual: inicializa, siembra y muestra un resumen.
    # Ejecuta este archivo directo (python database.py) para verificar
    # que todo funciona antes de conectarlo con la UI.
    init_db()
    seed_database()
    todos = get_all_animes()
    print(f"Total de registros en la base de datos: {len(todos)}")
    print(f"Pendientes: {len(get_all_animes(estado='Pendiente'))}")
    print(f"Completados: {len(get_all_animes(estado='Completado'))}")
    print(f"Viendo: {len(get_all_animes(estado='Viendo'))}")
    print(f"Películas: {len(get_all_animes(tipo='Película'))}")
