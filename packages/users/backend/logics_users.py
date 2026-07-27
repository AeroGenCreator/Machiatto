import sqlite3

import flet as ft
from email_validator import EmailNotValidError, validate_email

from machiatto.datatable_orm import DatatableORM
from machiatto.machiatto_dataclasses import InputField

from ..models.users import Users

# === LÓGICAS ===

def validar_correo(self) -> None:
    """Este codigo ilustra como construir controladores en el framework"""
    # Respalda la data en la base de datos.
    self.ensure_store()
    # Prepara el contenedor de errores.
    self.alert = ft.AlertDialog()
    # Los 'InputField' guardan la respuesta en 'self.response'.
    # Self response puede indexar la respuesta del usuario como atributo
    # Es obligatorio declararlo Ej: InputField(key='email')
    # Ahora 'email' existe en self.response
    answer = self.response.email if self.response.email is not None else ""
    try:
        # Siempre usar try, except cuando se usa el ORM.
        email = validate_email(answer, check_deliverability=False)
        kw = {
            f"{self.table}__{self.columns[2]}__{self.columns[0]}__same":
            [email.normalized, self.this_index]
        }
        self.model.u(**kw)
        self.refresh()
    except EmailNotValidError as e:
        self.alert.title = ft.Text(
            value="No se completo la operación",
            font_family="GeistSansBlack",
            size=22,
        )
        self.alert.content=ft.Text(
            str(e) + f" Indice del registro {self.this_index}"
        )
        self.alert.actions=[
            ft.Button(
                content=ft.Text(
                    value="Cerrar",
                    color=ft.Colors.WHITE
                ),
                on_click=lambda self: self.page.pop_dialog(),
                bgcolor=ft.Colors.RED_600,
                icon=ft.Icons.UNDO,
                icon_color=ft.Colors.WHITE,
            )
        ]
        self.page.show_dialog(self.alert)
    except sqlite3.IntegrityError as e:
        self.alert.title = ft.Text("Error a nivel de ORM")
        self.alert.content = ft.Text(e)
        self.alert.actions = [
            ft.Button(
                content=ft.Text(value="Cerrar"),
                on_click=lambda self: self.page.pop_dialog()
            )
        ]
        self.show_dialog(self.alert)

# === CONTROLADORES EXTRAS ===

correo_controller = InputField(
    string="Agregar Correo",
    value="",
    function=validar_correo,
    settings=None,
    key="email"
)

# === VISTA TABLA - FORMULARIO ===

def get_users():
    return DatatableORM(
        model=Users,
        controllers=[correo_controller]
    )
