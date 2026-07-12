import re
import sqlite3

import flet as ft

from machiatto.datatable_orm import DatatableORM
from machiatto.machiatto_dataclasses import InputField

from ..models.users import Users

# === LÓGICAS ===

def validar_correo(self) -> None:

    self.ensure_store()
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    if re.fullmatch(regex, self.response):
        kw = {
            f"{self.table}__{self.columns[2]}__{self.columns[0]}__same":
            [self.response, self.this_index]
        }
        try:
            self.model.u(**kw)
        except sqlite3.IntegrityError as e:
            ft.AlertDialog(
                title=ft.Text("Error a nivel ORM - Actulización"),
                content=ft.Text(e),
                actions=[
                    ft.Button(
                        content=ft.Text("Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
            )
        self.refresh()

    else:
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("No se completo la operación"),
                content=ft.Text(
                    (
                        "Correo invalido. Para registro con id: "
                        f"'{self.this_index}'."
                    )
                ),
                actions=[
                    ft.Button(
                        content=ft.Text("Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
            )
        )

# === CONTROLADORES EXTRAS ===

correo_controller = InputField(
    string="Agregar Correo",
    value="",
    function=validar_correo,
    settings=None
)

# === VISTA TABLA - FORMULARIO ===

def get_users():
    return DatatableORM(
        model=Users,
        controllers=[correo_controller]
    )
