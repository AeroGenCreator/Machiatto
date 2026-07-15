# ============================================================================
# Machiatto
# A modular business application framework for Python.
#
# Built on:
#   - PanCakesORM
#   - Flet
#
# Features:
#   - Module system
#   - MVC architecture
#   - Form and table views
#   - Advanced search and filters
#   - Declarative UI components
#
# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0
# ============================================================================

# ============================================================================
# Modulos
import flet as ft

from machiatto.machiatto_gear import MainGear
from machiatto.package_loader import load_models, mapper, read_manifest
from packages.users.models.users import init_users

# ============================================================================

# 1. Lectura de directorio 'packages'.
container_items, sidebar_buttons, dynamic_models = read_manifest()
# 2. Carga de todos los modelos declarados en el maniest
load_models(dynamic_models)
# 3. Mapea "Boton" | "evento"
modulos = mapper(content=container_items, sidebar_button=sidebar_buttons)
# 4. Paquete obligatorio: 'users'. Carga login keys.
STATUS = init_users()
print(STATUS)
# 5. Fuentes de la aplicación

FUENTES = {
    "GeistSansBlack": "fonts/geist_sans/Geist-Black.ttf",
    "GeistSansBold": "fonts/geist_sans/Geist-Bold.ttf",
    "GeistSansMedium": "fonts/geist_sans/Geist-Medium.ttf",
    "GeistSansRegular": "fonts/geist_sans/Geist-Regular.ttf",
    "GeistMonoBlack": "fonts/geist_mono/GeistMono-Black.ttf",
    "GeistMonoBold": "fonts/geist_mono/GeistMono-Bold.ttf",
    "GeistMonoMedium": "fonts/geist_mono/GeistMono-Medium.ttf",
    "GeistMonoRegular": "fonts/geist_mono/GeistMono-Regular.ttf",
    "GeistMonoItalic": "fonts/geist_mono/GeistMono-Italic.ttf",
}


# Contenedor Maestro
class MainContainer(ft.Container):
    """
    Contendor padre de la apliacion
    Engloba el cascaron de vistas construido
    para 'Machiato' framework.
    """
    def __init__(self, content):
        super().__init__()
        self.border_radius = 10
        self.padding = 10
        self.expand=True
        self.content = content
        self.update()


def main(page: ft.Page):
    """
    Ejecución principal de flet.
    1. Definición 'Pagina'.
    2. Monta 'MainContainer' en 'Pagina'.
    """
    page.fonts = FUENTES

    page.theme = ft.Theme(
        font_family="GeistSansRegular",
        color_scheme_seed=ft.Colors.AMBER
    )
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.AMBER)
    page.title = "Macchiato"
    page.window.width = 1080
    page.window.height = 720

    shell = MainGear(modulos=modulos, pagina=page)

    page.add(shell)

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
