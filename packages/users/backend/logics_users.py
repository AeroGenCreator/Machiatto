import re
import sqlite3

import flet as ft

from machiatto.datatable_orm import DatatableORM
from machiatto.machiatto_dataclasses import InputField

from ..models.users import Users

# === LÓGICAS ===

def validar_correo(self) -> None:

    self.ensure_store()
    answer = self.response if self.response is not None else ""
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    if re.fullmatch(regex, answer) or answer == "":
        kw = {
            f"{self.table}__{self.columns[2]}__{self.columns[0]}__same":
            [answer, self.this_index]
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
                title=ft.Text(
                    value="No se completo la operación",
                    font_family="GeistSansBlack",
                    size=22,
                ),
                content=ft.Text(
                    (
                        f"Correo invalido '{answer}''. Para registro con id "
                        f"{self.this_index}. Ejemplo valido: "
                        "ejemplo@gmail.com."
                    )
                ),
                actions=[
                    ft.Button(
                        content=ft.Text(
                            value="Cerrar",
                            color=ft.Colors.WHITE,
                        ),
                        on_click=lambda self: self.page.pop_dialog(),
                        icon=ft.Icons.UNDO,
                        icon_color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_600
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
