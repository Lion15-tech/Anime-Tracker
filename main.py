import flet as ft

def main(page: ft.Page):
    page.title = "Anime Tracker"
    
    animes = {}

    mensaje = ft.Text("")
    campo_nombre = ft.TextField(
        label = "Nombre del anime"
    )
    lista_animes = ft.Text("")

    def agregar_anime(e):
        #Se guarda con mayusculas para luego mostrar este nombre
        nombre = campo_nombre.value.strip().title() #por si el usuario pone el nombre en minusculas

        #Nombre en minusculas para buscar y comparar con las keys
        busqueda_nombre = campo_nombre.value.strip().lower()

        #Que si haya puesto un nombre
        if not campo_nombre.value.strip():
            mensaje.value = "Debes escribir un nombre"
            page.update()
            return       

        #Para revisar si existe
        ya_existe = False       #Empezamos asumiendo que el anime NO existe
        for anime in animes:                           
            if anime.lower() == busqueda_nombre:    #Si el guardado en minúsculas coincide con el nuevo en minúsculas
                ya_existe = True
                break

        if ya_existe:
            mensaje.value = "Ese anime ya existe"     
            page.update()                             
            return
                                    
        else:
            #Si no existía, lo agregamos al diccionario
            animes[nombre] = {
                "calificacion": None
            }
            mensaje.value = f"{nombre} agregado con exito!"
            lista_animes.value = "\n".join(animes.keys())
            campo_nombre.value = ""
            page.update()

    #Boton para que sirva la función de agregar_anime
    boton = ft.ElevatedButton(
        "Agregar Anime",
        on_click = agregar_anime
    )
    
    #Se añaden todos los componentes a la página en el orden en el que aparecerán 
    page.add(
        campo_nombre,
        boton,
        mensaje,
        lista_animes
    )

#Se ejecuta el código
ft.run(main)
