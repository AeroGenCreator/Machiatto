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

import flet as ft

from packages.users.models.users import Users


class MainGear(ft.Row):
    """
    El eje principal se monta como una fila.
    La fila se carga con dos contenedores columna.
    La primer columna contiene el sidebar y navegación de modulos.
    La segunda columna contiene 2 contenedores fila.
    La primera fila contiene la navegación topbar de vistas.
    La segunda fila contiene el contenido de la vista.
    """
    def __init__(self, modulos, pagina):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER
        self.modulos = modulos
        self.pagina = pagina
        self.expand = True
        # sidebar contenedor
        self.sidebar = ft.Container(content=None)
        # navegador
        self.navegador = ft.Container(content=None)
        # contenido_vista_contendor
        self.contenido_vista = ft.Container(
            expand=10,
            content=ft.Column(),
            visible=True
        )
        # Modulo actual:
        self.current_module = None
        self.form()

    def navegar_modulo(self, e):
        boton = e.control
        index = boton.content
        metadata = getattr(self, self.current_module, None)
        if metadata is None:
            raise ValueError("Error when navigating topbar. No metadata.")
        function = metadata[index]
        view = function()
        self.tabla = ft.Container(
            content=ft.Row(
                controls=view
            ),
            expand=11
        )
        self.contenido_vista = ft.Container(
            content=ft.Column(
                controls=[self.navegador, self.tabla]
            ),
            expand=10
        )
        self.controls = [self.sidebar, self.contenido_vista]
        self.pagina.update()

    def construir_navegacion(self):
        self.navegador = ft.Container(
            content=ft.ListView(
                ft.Row(
                    controls=None
                )
            ),
            expand=1
        )
        if self.current_module is None:
            pass
        else:
            metadata = getattr(self, self.current_module, None)
            nav_buttons = []
            for label, function in metadata.items():
                nav_buttons.append(
                    ft.Button(
                        content=label,
                        on_click=self.navegar_modulo
                    )
                )

            self.navegador.content.controls.controls = nav_buttons

    def manejar_click(self, e):
        boton = e.control
        modulo = boton.key
        metadata = getattr(self, modulo, None)
        if metadata is None:
            ValueError("Unreachable metadata view.")
        first_key = list(metadata.keys())[0]
        function = metadata[first_key]
        view = function()
        self.current_module = modulo
        self.construir_navegacion()
        self.tabla = ft.Container(
            content=ft.Row(
                controls=view
            ),
            expand=11
        )
        self.contenido_vista = ft.Container(
            content=ft.Column(
                controls=[self.navegador, self.tabla]
            ),
            expand=10
        )
        self.controls = [self.sidebar, self.contenido_vista]
        self.pagina.update()

    def logout(self, e):
        """ Renderiza la pantalla de login """
        self.form()

    def construir_botones_sidebar(self):

        sidebar_botones = []

        sidebar_botones.append(
            ft.Button(
                content=ft.Text(
                    value="Cerrar Sesión"
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                on_click=self.logout,
                icon=ft.Icons.LOGOUT
            )
        )

        for element in self.modulos:
            for modulo, metadata in element.items():
                sidebar = metadata.get("sidebar", None)
                navigation = metadata.get("navigation", None)

                if sidebar is None or navigation is None:
                    raise ValueError("Empty metadata in modules. Stop Process")

                function = sidebar.get("function", None)
                label = sidebar.get("label", None)
                icon = sidebar.get("icon", "").upper()

                # No valido el icono porque este puede ser None.
                validate = ((function is None),(label is None))

                if any(validate):
                    raise ValueError("Sidebar empty metadata error.")

                button = ft.Button(
                    icon=getattr(ft.Icons, icon, "all_inbox"),
                    on_click=self.manejar_click,
                    content=ft.Text(
                        value=label,
                        font_family="Barlow",
                        size=18
                    ),
                    key=modulo,
                )

                sidebar_botones.append(button)

                # La instancia ahora almacena:
                # Modulo como atributo, metadata de navegacion como contenido.
                setattr(self, modulo, navigation)

        sidebar_botones.append(
            ft.Container(
                content=ft.Image(
                    src="../assets/application/icon.png",
                    fit=ft.BoxFit.CONTAIN,
                ),
                width=128,
                height=128,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border_radius=8
            )
        )

        # Aqui se maneja la arquitectura de montado
        self.sidebar = ft.Container(
            content=ft.Column(
                    controls=sidebar_botones,
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            padding=10,
            border_radius=10,
            expand=2,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

        self.wrapper = ft.Container(
            visible=True,
            expand=True,
            content=ft.Row(
                controls=[self.sidebar, self.contenido_vista]
            )
        )

        self.controls = self.wrapper
        self.pagina.update()

    def login(self):  # Funciona
        """
        Renderiza el formulario 'login'
        """
        kw = {
            "users__correo__same__and": self.email.value,
            "users__password__same__or": self.password.value,
            "users__nombre__same__and": self.email.value,
            "users__password__same": self.password.value
        }
        res, col = Users.filter(**kw).all().raw()
        if not res:
            self.pagina.show_dialog(
                ft.AlertDialog(
                    title=ft.Text(
                        size=22,
                        value="Credenciales invalidas",
                        font_family="Barlow"
                    ),
                    content=ft.Text(
                        value=(
                            "Correo o contraseña invalidos. "
                            "Intente de nuevo."
                        )
                    ),
                    actions=[
                        ft.Button(
                            content=ft.Text(
                                color=ft.Colors.WHITE,
                                value="Intentar de Nuevo"
                            ),
                            bgcolor=ft.Colors.RED_500,
                            on_click=lambda self: self.page.pop_dialog()
                        )
                    ]
                )
            )
        else:
            self.construir_botones_sidebar()

    def form(self):  # Funciona
        self.greetings = ft.Text(
            "¡Bienvenido!",
            size=40,
            weight=ft.FontWeight.W_700,
            font_family="Barlow"
        )
        self.email = ft.TextField(
            label=ft.Text(value="Correo Electronico"),
            autofill_hints=ft.Text("ejemplo@gmail.com"),
        )
        self.password = ft.TextField(
            label=ft.Text(value="Contraseña"),
            password=True
        )
        self.submit = ft.Button(
            content=ft.Text(value="Validar & Entrar"),
            icon=ft.Icons.LOGIN,
            on_click=self.login,
        )

        self.login_form = ft.Column(
            controls=[
                self.greetings,
                self.email,
                self.password,
                self.submit
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        self.controls = self.login_form
        self.pagina.update()
