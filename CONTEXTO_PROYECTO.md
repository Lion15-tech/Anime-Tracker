# Contexto del Proyecto: AnimeList P5R

> Este documento es un resumen de traspaso. Pégalo como primer mensaje a Claude Code (o súbelo como archivo) para que tenga todo el contexto de arquitectura, decisiones de diseño y estado actual antes de seguir desarrollando.

## 1. Qué es este proyecto

App de escritorio/móvil hecha con **Python + Flet** para organizar listas personales de anime/películas vistas. El usuario ya tiene una lista real de ~84 títulos (46 animes vistos, 10 películas vistas, 28 pendientes) que está precargada en la base de datos.

Cada registro tiene 4 campos que el usuario rellena desde la app: **calificación** (0-10), **estado** (Pendiente/Viendo/Completado), **favorito** (sí/no), **comentario** (texto libre).

## 2. Dirección de arte (no negociable, ya decidida)

Estética **100% inspirada en Persona 5 Royal**:
- Paleta reducida a propósito: negro (`#1A1A1A`), rojo vibrante (`#E3131B`), blanco, + grises de apoyo. Nada de colores fuera de esta familia.
- **Cero esquinas redondeadas.** El look angular se logra con cortes diagonales (franjas rotadas y recortadas dentro de un `Stack` + `Container(clip_behavior=HARD_EDGE)`), no con `border_radius`.
- Tipografía pendiente de resolver: por ahora se usa la fuente del sistema con bold+italic como placeholder. Está pendiente elegir e integrar una fuente condensada (ej. Anton, Oswald, Bebas Neue) en `assets/fonts/`. **No se ha resuelto todavía — el usuario pidió posponerlo.**
- Toda decisión de color/tipografía/espaciado vive en `theme.py`. Ningún otro archivo debe usar colores "hardcodeados".

## 3. Arquitectura del proyecto (acordada y en construcción)

```
animelist_p5r/
├── main.py                  # AÚN NO CONSTRUIDO (es el último paso)
├── main_preview.py           # Archivo TEMPORAL de prueba visual (ver sección 5)
├── database.py                # ✅ Construido y probado
├── models.py                  # ✅ Construido y probado
├── theme.py                   # ✅ Construido y probado
├── components.py             # ✅ Construido y probado
├── views/                      # ❌ Pendiente
│   ├── home_view.py
│   ├── detail_view.py
│   └── add_view.py
├── navigation.py              # ❌ Pendiente
└── assets/fonts/                # ❌ Pendiente (fuente sin elegir aún)
```

### Responsabilidad de cada capa
- **`database.py`**: única capa que toca SQLite. Expone funciones `init_db()`, `seed_database()`, `get_all_animes(tipo=, estado=)`, `get_anime_by_id(id)`, `insert_anime(...)`, `update_anime(id, **campos)`, `delete_anime(id)`. **Importante:** estas funciones devuelven objetos `Anime` (de `models.py`), nunca `sqlite3.Row` crudo.
- **`models.py`**: define el dataclass `Anime` (el "contrato" de datos), con `Anime.from_row()` para convertir filas de SQLite, y propiedades de conveniencia como `calificacion_texto`, `estado_color_key`. También tiene `validar_anime()` para los formularios futuros.
- **`theme.py`**: fuente única de verdad visual. Expone `Colors`, `Fonts`, `Spacing`, `Shape`, `TextStyles`, y `get_page_theme()` (para `page.theme`).
- **`components.py`**: widgets reutilizables ya construidos: `anime_card()`, `status_badge()`, `rating_stars()`, `favorite_icon()`, `section_header()`, `primary_button()`, `empty_state()`. Reciben objetos `Anime` y callbacks; no conocen la base de datos.
- **Flujo de datos:** `database.py` → objetos `Anime` → las vistas los piden y arman `components.py` con ellos → `navigation.py` decide qué vista mostrar según `page.go("/ruta")` → `main.py` solo arranca todo.

## 4. Estado actual / próximos pasos

Ya construidos y revisados: `database.py`, `models.py`, `theme.py`, `components.py`.

**Siguiente paso pendiente:** construir `views/home_view.py` (pantalla principal con la lista de animes, usando `anime_card()` de `components.py`), y después `add_view.py`, `detail_view.py`, `navigation.py`, y finalmente `main.py`.

## 5. Sobre `main_preview.py`

Es un archivo **temporal**, no el `main.py` final. Su único propósito es renderizar algunos `anime_card()` de ejemplo (con datos reales de la base de datos) para validar visualmente el estilo P5R antes de construir las vistas completas. Se puede seguir usando para probar nuevos componentes, o eliminar una vez que `home_view.py` y `main.py` reales estén listos.

## 6. ⚠️ Notas críticas de entorno (ya resueltas, pero importantes)

El entorno donde se generó este código (un sandbox sin acceso a internet ni a Flet instalado) **no pudo ejecutar el código realmente**, solo validar sintaxis con `py_compile`. Por eso, al correr el código por primera vez en la máquina real del usuario, aparecieron errores de API porque el usuario tiene instalada la versión reciente de **Flet 1.0 (0.85.x)**, que tiene cambios "breaking" importantes respecto a la API "clásica" con la que se entrenó el modelo. Ya se corrigieron estos puntos, pero Claude Code debe tenerlos en cuenta para cualquier código nuevo que escriba en este proyecto:

- `ft.app(target=main)` → ahora es `ft.run(main)`.
- `ft.ColorScheme(...)` ya **no acepta** `background` ni `on_background` (deprecados por Flutter) → usar `surface`/`on_surface`.
- Los helpers de módulo en minúscula fueron **removidos** en Flet 0.85.0: `ft.padding.all/symmetric/only`, `ft.margin.*`, `ft.border.*`, `ft.border_radius.*` ya no existen. Ahora son **clases con mayúscula inicial**: `ft.Padding.all(...)`, `ft.Margin.symmetric(...)`, `ft.Border.only(...)`, `ft.BorderSide(...)`, `ft.BorderRadius.all(...)`.
- `ft.alignment.center` (minúscula) también cambió a `ft.Alignment.CENTER` en V1, aunque todavía no se ha usado en este proyecto — tenerlo en cuenta para vistas nuevas.
- `ft.Icons.NOMBRE` (mayúscula) es correcto en esta versión.

**Recomendación para Claude Code:** dado que tienes acceso real a la terminal del usuario, lo ideal es que verifiques la versión exacta instalada (`pip show flet`) y, ante cualquier duda de API, **ejecutes el código real** en vez de asumir — eso es justo la ventaja que tienes sobre la sesión anterior en el chat web.

Un bug específico que quedó pendiente de confirmar: `database.py` en algún punto del lado del usuario quedó desincronizado (una versión vieja que devolvía `sqlite3.Row` en vez de `Anime`), causando `'sqlite3.Row' object has no attribute 'estado'`. Se le indicó al usuario reemplazar el archivo por la versión corregida — vale la pena confirmar al arrancar que el `database.py` que tiene en disco coincide con el de este documento (sección 7) antes de seguir construyendo.

## 7. Datos ya cargados

`database.py` incluye un `seed_database()` con la lista completa y real del usuario (84 títulos: 46 animes vistos, 10 películas vistas, 28 pendientes), con sus estados correctos ya asignados (`Completado`, `Viendo` para los 2 recién empezados, `Pendiente` para el resto). Calificación, favorito y comentario quedan vacíos para que el usuario los rellene desde la app. **No se debe volver a pedir esta lista ni regenerar el seed** — ya existe y está probado (insertó correctamente 84 registros).

## 8. Preferencias de estilo de trabajo del usuario

- Comentarios y docstrings del código en **español**.
- El usuario prefiere avanzar **archivo por archivo**, confirmando cada uno antes de seguir al siguiente, en vez de recibir todo el proyecto de golpe.
- Le gusta que se pruebe/valide cada archivo antes de dárselo por terminado (en esta sesión se hizo con `py_compile` y pruebas funcionales de `database.py`; en VS Code se puede y se debe hacer la prueba real ejecutando la app).
