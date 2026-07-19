import flet as ft
from pancakes.models.model import PanCakesORM


class DatatableOne2Many(ft.Container):
    """
    Contenedor Flet.
    Contiene una tabla.
    Requiere de un model PanCakesORM para renderizar vista.
    """

    def __init__(self, model: PanCakesORM, pagina: ft.Page):
        super().__init__()

        # Atributos de herencia
        self.expand = True

        # Atributos nuevos
        self.model = model
        self.pagina = pagina
        self.topbar_container = ft.Container(
            expand=1,
            content=ft.Row(
                controls=[],
                expand=True,
            ),
            border_radius=10,
        )
        self.current_page = 1
        self.less = ft.IconButton()
        self.counter = ft.Text()
        self.more = ft.IconButton()
        self.main_column = ft.Column()

        # Metodos de inicialización
        self._inti_page_counter_()
        self._mount_layout_()

    # === WIDGETS ===

    def _inti_page_counter_(self):
        """Contador de pagina (widget)"""
        self.less.icon = ft.Icons.REMOVE
        self.less.key = "less"
        self.less.on_click = self.navigate_page

        self.counter.value = str(self.current_page)
        self.counter.font_family = "GeistMonoMedium"
        self.counter.alignment = ft.MainAxisAlignment.CENTER

        self.more.icon = ft.Icons.ADD
        self.more.key = "more"
        self.more.on_click = self.navigate_page

        self.topbar_container.content.controls.extend(
            [self.less, self.counter, self.more]
        )

    # === FUNCIONES ===

    def navigate_page(self, e):
        pass

    # === MONTAR COMPONENTES ===
    def _mount_layout_(self):
        self.main_column.controls = [self.topbar_container]
        self.content = self.main_column
        self.pagina.update()
