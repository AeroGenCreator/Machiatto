# Lanzador de aplicacion

# Carga de metadata
import flet as ft

from machiatto.gear import MainGear
from machiatto.package_loader import load_models, mapper, read_manifest
from packages.users.models.users import init_users

# 1. Correccion; Lectura del manifest
container_items, sidebar_button, dynamic_models = read_manifest()
# 2. Carga de todos los modelos declarados en el maniest
load_models(dynamic_models)
# 3. Mapea "Boton" | "evento"
modulos = mapper(content=container_items, sidebar_button=sidebar_button)
# 4. Paquete obligatorio: 'users'. Carga login keys.
STATUS = init_users()

# Contenedor Maestro
class MainContainer(ft.Container):
    """
    Este contenedor debe manejar logins.
    """
    def __init__(self, content):
        super().__init__()
        self.border_radius = 10
        self.padding = 10
        self.expand=True
        self.content = self.content
        self.update()


def main(page: ft.Page):
    """
    Ejecución principal de flet.
    1. Definición de las paginas.
    2. Instancia de contenedores y vistas.
    """
    page.title = "Macchiato"
    page.window.width = 1080
    page.window.height = 720
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.GREY)

    shell = MainGear(modulos=modulos, pagina=page)

    page.add(shell)

if __name__ == "__main__":
    ft.run(main)
