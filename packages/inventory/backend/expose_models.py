import flet as ft

from machiatto.datatable_orm import DatatableORM
from machiatto.machiatto_dataclasses import ButtonItem

from .. import models


# === Funciones ===
def saludar(self):
    self.ensure_store()  # Asegurar guardar cualquier cambio en formulario.
    indice = self.this_index  # Indice del registro actual.
    self.page.show_dialog(
        ft.AlertDialog(
            title=ft.Text("Mi Primer Botón"),
            content=ft.Text(f"¡Hola Mundo! Estamos en el record... {indice}"),
            actions=[
                ft.Button(
                    content=ft.Text("Cerrar"),
                    on_click=lambda self: self.page.pop_dialog()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
    )

# === Controllers Custom ===

mi_primer_boton = ButtonItem(
    string="¡Hola Mundo!",
    function=saludar
)


# === Vista DatatableORM ===
def get_inventory():
    model = models.inventory.Inventory
    return DatatableORM(
        model=model,
        controllers=[mi_primer_boton]
        )

def get_categories():
    model = models.category.Category
    return DatatableORM(
        model=model
    )
