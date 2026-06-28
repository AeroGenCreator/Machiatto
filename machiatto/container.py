import flet as ft


class MainContainer(ft.Container):
    """
    Este contenedor debe manejar logins.
    """
    def __init__(self, contenido, pagina):
        super().__init__()
        self.border_radius = 10
        self.padding = 10
        self.contenido = contenido
        self.pagina = pagina
        # Lo mantengo en false mientras no desarrolle el login.
        self.expand=False
        self.montar_contenido()

    def montar_contenido(self):
        self.content = self.contenido
        self.pagina.update()


class ShellContaniner(ft.Container):
    """
    Este shell debe recibir una fila:
    La fila debe recibir 2 containers (dimen. 1 - 11)
    Container 1: Col: Siderbar inyecta topbar - default view / modulos.
    Container 2: Col: 2 Filas:
    Fila 1: Topbar:
    Fila 2: Panel tablas.
    """
    def __init__(self, contenido, pagina):
        super().__init__()
        self.border_radius = 10
        self.padding = 10
        self.contenido = contenido
        self.pagina = pagina
        self.expand = True
        self.montar_contenido()

    def montar_contenido(self):
        self.content = self.contenido
        self.pagina.update()
