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
import os
import sys

# Modulos
import flet as ft

# Ruta absoluta del fichero actual.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Establecer ruta raiz.
os.chdir(PROJECT_ROOT)

# Inyectamos la raíz en sys.path por si la librería busca módulos desde la raíz
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importacion de librerias: Rutas Corregidas
from machiatto.machiatto_gear import MainGear  # noqa: E402
from machiatto.package_loader import (  # noqa: E402
    load_models,
    mapper,
    read_manifest,
)

# ============================================================================

# 0. Asegurar que se carguen cursores GTK/GNOME
os.environ["GDK_BACKEND"] = "x11"
# 1. Ruta absoluta de este afichero.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 1. Lectura de directorio 'packages'.
container_items, sidebar_buttons, dynamic_models = read_manifest()
# 2. Carga de todos los modelos declarados en el maniest
load_models(dynamic_models)
# 3. Mapea "Boton" | "evento"
modulos = mapper(content=container_items, sidebar_button=sidebar_buttons)
# 4. Fuentes de la aplicación

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

def main(page: ft.Page):
    """
    Ejecución principal de flet.
    1. Definición 'Pagina'.
    2. Monta 'Shell' en 'Pagina'.
    """
    page.title = "Macchiato"
    page.fonts = FUENTES
    page.theme = ft.Theme(
        font_family="GeistSansRegular",
        color_scheme_seed=ft.Colors.AMBER
    )
    page.dark_theme = ft.Theme(
        font_family="GeistSansRegular",
        color_scheme_seed=ft.Colors.AMBER)

    shell = MainGear(modulos=modulos, pagina=page)
    page.add(shell)

if __name__ == "__main__":
    ft.app(main, assets_dir=str(BASE_DIR) + "/assets")
