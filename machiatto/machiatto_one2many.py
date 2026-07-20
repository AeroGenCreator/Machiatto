import flet as ft
from pancakes.models.model import PanCakesORM


class DatatableOne2Many(ft.Container):
    """
    Contenedor Flet.
    Contiene una tabla.
    Requiere de un model PanCakesORM para renderizar vista.
    """

    def __init__(
        self,
        model: PanCakesORM,
        second_table: str,
        pagina: ft.Page,
        reference: int,
    ):
        super().__init__()

        # Atributos de herencia
        self.expand = True

        # Atributos nuevos
        self.model = model
        self.pagina = pagina
        self.second_table = second_table
        self.reference = reference
        self.query = {}
        self.chunk = {}
        self.columns = []
        self.flet_columns = []
        self.flet_rows = []
        self.datatable: ft.DataTable = None
        self.datatable_spine = ft.Column()
        self.datatable_width = ft.Row()
        self.datatable_container = ft.Container()
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
        self.spine = ft.Column()

        # Metodos de inicialización
        self._inti_page_counter_()
        self._init_columns_()
        self._chunk_()
        self._fetch_data_()
        self._init_rows_()
        self._init_datatable_()
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

    def _init_datatable_(self):
        self.datatable = ft.DataTable(
            columns=self.flet_columns, rows=self.flet_rows
        )

        # Fila del datatable
        self.datatable_width.controls = self.datatable
        self.datatable_width.scroll = ft.ScrollMode.AUTO

        # Columna del datatable
        self.datatable_spine.controls = self.datatable_width
        self.datatable_spine.scroll = ft.ScrollMode.AUTO

        # Container del datatable
        self.datatable_container.content = self.datatable_spine
        self.datatable_container.expand = 11
        self.datatable_container.border_radius = 10
        self.datatable_container.bgcolor = ft.Colors.SURFACE_CONTAINER_LOWEST

    # === CONSTRUCCIÓN COLUMNAS ===

    def _init_columns_(self):
        self.columns = self.model._metadata[self.model._table]["columns"]
        self.flet_columns = [
            ft.DataColumn(
                label=ft.Text(
                    value=col,
                    font_family="GeistSansBlack",
                )
            )
            for col in self.columns
        ]

    # === Fetch a la Base de Datos ===

    def _chunk_(self):
        """Cálcula el rango del chunk"""
        if self.current_page == 1:
            self.chunk = {"limit": 15, "offset": 0}
        else:
            limit = 15
            self.chunk = {
                "limit": (limit * self.current_page),
                "offset": ((limit * self.current_page) - limit),
            }

    def _fetch_data_(self):
        """Realiza el query"""
        field = f"{self.model._table}__{self.second_table}_id__same"
        domain = {field: self.reference}
        self.query = (
            self.model.filter(**domain).chunk(**self.chunk).all().container()
        )

    # === CONSTRUCCIÓN DE FILAS ===

    def _init_rows_(self):
        raw = []
        for field, metadata in self.query[self.model._table].items():
            validate = ((field != "@main_table@"), (field != "@depends@"))
            if all(validate):
                raw.append(metadata["vector"])

        # Filas crudas transpuestas
        rows = list(zip(*raw))

        # Filas FLet
        self.flet_rows = [
            ft.DataRow(
                on_select_change=self.this_row,
                selected=False,
                cells=[
                    ft.DataCell(
                        ft.Text(value=cell, font_family="GeistSansRegular")
                    )
                    for cell in row
                ],
            )
            for row in rows
        ]

    # === FUNCIONES ===

    def navigate_page(self, e):
        """Navegar registros en constante de 15s"""
        counter = e.control.key
        if counter == "less":
            if self.current_page == 1:
                return
            else:
                self.current_page -= 1
                self.counter.value = str(self.current_page)
                self._chunk_()
                self._fetch_data_()
                self._init_rows_()
                self.datatable.rows = self.flet_rows
                self.pagina.update()
        if counter == "more":
            field = f"{self.model._table}__{self.second_table}_id__same"
            domain = {field: self.reference}
            self.saved_page = self.current_page
            self.saved_rows = self.flet_rows
            self.current_page += 1
            self._chunk_()
            row, col = (
                self.model.filter(**domain).chunk(**self.chunk).all().raw()
            )
            if not row:
                self.current_page = self.saved_page
                self._chunk_()
            else:
                self.counter.value = str(self.current_page)
                self._fetch_data_()
                self._init_rows_()
                self.datatable.rows = self.flet_rows
                self.pagina.update()

    def this_row(self, e):
        pass

    # === MONTAR COMPONENTES ===
    def _mount_layout_(self):
        self.spine.controls = [self.topbar_container, self.datatable_container]
        self.content = self.spine
        self.pagina.update()
