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

"""
Componente: 📋
Recibe un modelo de PanCakesORM -> Construye vistas 'Tabla - Formulario'.
"""

# ============================================================================

# Modulos
import datetime
import re
import uuid
from functools import partial
from typing import Callable, List, Optional

import flet as ft
from pancakes.models.model import PanCakesORM
from pydantic import ValidationError

from . import machiatto_dataclasses

# ============================================================================

def calculo_de_fecha():
    # datetime.now().astimezone() detecta automáticamente el offset del sistema
    fecha_local = datetime.datetime.now().astimezone()

    # Extraemos la información de la zona horaria (el offset)
    return fecha_local.tzinfo


class DatatableORM(ft.Column):
    """
    Atributos:

    model; El modelo renderizado, funciones, vistas, ... etc.
    controllers; Lista 'Peticion de componentes'.
    advanced_domain; Bandera - Tenemos un filtro avanzado activo.

    current_page; Ubicacion de Pagina.
    max_rows; Maximo de filas renderizadas por hoja.
    container; Query devuelto (Paquete de datos) vector = max_rows.
    table; Nombre de la tabla del modelo pasado.
    columns; Lista de tablas [strings, ... ].
    flet_columns; Columnas del query (listadas como objetos Flet).
    rows; Filas transpuestas crudas.
    flet_rows; Filas del query (listadas como objetos Flet).
    length; Largo del vector devuelto por el query actual.
    counter; Widget - Muestra el numero de pagina actual.
    form_controls;
    alert;

    """

    def __init__(
        self,
        model: PanCakesORM,
        controllers: List = [],
    ):
        super().__init__()
        self.model = model
        self.controllers = controllers
        self.advanced_domain = False
        self.search_bar = None
        self.custom_domain = ft.Button(
            content=ft.Text(
                value="Dominios",
                font_family="GeistMonoMedium"
            ),
            key="custom_domain",
            icon=ft.Icons.FILTER_LIST
        )

        self.this_row = None
        self.this_index = "IDxxx1"
        self.name_domain = False
        self.current_page = 1
        self.max_rows = 15
        self.container = None
        self.table = self.model._table
        self.columns = []
        self.flet_columns = []
        self.rows = []
        self.flet_rows = []
        self.length = 0
        self.counter: Optional[ft.Text | None] = None
        # Almacena los campos widgets de vista formulario 'invocada'
        self.form_controls = []
        self.alert = ft.AlertDialog()
        self.close_alert = ft.TextButton(
            ft.Text(
                value="Cerrar",
                font_family="GeistMonoMedium"
            ),
            on_click=lambda e: self.page.pop_dialog()
        )
        self.domain_select_column: Optional[None | ft.Dropdown] = None
        self.model_labels = self.model._metadata[self.table]["comments"]
        self.domain_select_operator: Optional[None | ft.Dropdown] = None

        # Operadores Conversiones y Conjuntos de validacion segun categoria.
        self.OPERATORS = {
            "same": "=",
            "lt": "<",
            "ltsm": "<=",
            "gt": ">",
            "gtsm": ">=",
            "diff": "<>",
            "in": "IN",
            "notin": "NOT IN",
            "btwn": "BETWEEN",
            "is": "IS",
            "isnot": "IS NOT",
            "like": "LIKE",
            "notlike": "NOT LIKE",
        }

        self.SG_OPERATORS = {
            "same",
            "lt",
            "ltsm",
            "gt",
            "gtsm",
            "diff",
            "is",
            "isnot",
            "like",
            "notlike"
        }

        self.ITER_OPERATORS = {
            "in",
            "notin"
        }

        self.RANGE_OPERATORS = {
            "btwn"
        }

        self.FLOAT_EXPR = r"[0-9]+\.[0-9]+"
        self.INTEGER_EXPR = r'[0-9]+'

        # Metodos
        self._widget_operators_()
        self._widget_singular_iterable_range_()
        self._calculate_chunk_()
        self._fetch_data_()
        self._construct_flet_columns_()
        self._construct_flet_rows_()
        self._vector_length_()
        self._search_bar_widget_()
        self._header_container_widget_()
        self._create_entry_widget_()
        self._table_widget_()
        self._table_container_()
        self._sidebar_()
        self._layout_()

    # === Metodos inicializacion ===
    def _widget_operators_(self):
        """ Construye widget 'Desplegable' -> Selector de operador. """
        self.domain_select_operator = ft.Dropdown(
            menu_height=300,
            width=700,
            value=self.OPERATORS["same"],
            options=[
                ft.DropdownOption(
                    key=exp,
                    text=mean,
                    trailing_icon=ft.Icons.COMPARE_ARROWS,
                )
                for exp, mean in self.OPERATORS.items()
            ]
        )

    def add_tags(self, e):
        """Agrega valores sobre una fila; Permite filtrar por iterables."""
        if self.tag_field.value:
            new_chip = ft.Chip(
                label=self.tag_field.value.strip(),
                on_delete=self.delete_chip
            )
            self.tags_container.content.controls.append(new_chip)
            self.tag_field.value = ""
            self.page.update()

    def delete_chip(self, e):
        """Elimina etiqueta seleccionada"""
        self.tags_container.content.controls.remove(e.control)
        self.page.update()

    def _widget_singular_iterable_range_(self):
        """
        Tipos validos:
        1. Singular
        2. Iterable
        3. Couple
        El separador de iterables debe ser la coma ','.
        """

        # === SINGULAR ===
        # Input singular | Construcción del widget
        self.singular_input = ft.TextField(value="")
        self.SINGULAR = ft.ExpansionPanel(
            can_tap_header=True,
            header=ft.ListTile(title=ft.Text(
                    value="Solo un valor.",
                    font_family="GeistMonoMedium"
                )
            ),
            content=ft.Container(
                expand=True,
                padding=10,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[self.singular_input]
                ),
            )
        )

        # === ITERABLES ===
        # Input para valores iterables
        self.tag_field = ft.TextField(value=None)
        # Fila que aloja etiquetas de valores.
        self.tags_container = ft.Container(
            expand=True,
            content=ft.Row(
                wrap=True,
                spacing=8,
                run_spacing=8,
                controls=[]
            )
        )

        # Aloja los desplegables; (3 opciones)
        self.domain_datatype_selector = ft.ExpansionPanelList(
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
            spacing=8,
        )

        self.ITERABLES = ft.ExpansionPanel(
            can_tap_header=True,
            header=ft.ListTile(
                title=ft.Text(
                    value="Lista de valores.",
                    font_family="GeistMonoMedium"
                )
            ),
            content=ft.Container(
                expand=True,
                padding=10,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            controls=[
                                self.tag_field,
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    on_click=self.add_tags
                                ),
                            ]
                        ),
                        self.tags_container
                    ]
                )
            )
        )

        # === RANGOS ===
        self.first_range = ft.TextField(value="")
        self.second_range = ft.TextField(value="")
        self.RANGE = ft.ExpansionPanel(
            can_tap_header=True,
            header=ft.ListTile(
                title=ft.Text(
                    value="Rango de 2 valores.",
                    font_family="GeistMonoMedium"
                )
            ),
            content=ft.Container(
                padding=10,
                expand=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        self.first_range, self.second_range
                    ]
                )
            )
        )

        # Asignacion al componente desplegable de lista
        self.domain_datatype_selector.controls.append(self.SINGULAR)
        self.domain_datatype_selector.controls.append(self.ITERABLES)
        self.domain_datatype_selector.controls.append(self.RANGE)

        # Se coloca en una columna de flet
        self.datatype_selector_column = ft.Column(
            controls=[self.domain_datatype_selector],
        )

        # Se coloca en un contenedor flet (Para estilos).
        self.domain_datatype_container = ft.Container(
            padding=2,
            border_radius=10,
            content=self.datatype_selector_column,
            expand=True,
        )

    def _calculate_chunk_(self) -> None:
        """Tranforma indices 0,1,2 en rangos 20,40,60 etc..."""
        if self.current_page > 1:
            limit = self.max_rows
            offset = (self.max_rows * self.current_page) - self.max_rows
            self.chunk = {"offset": offset, "limit": limit}
        else:
            self.chunk = {"offset": 0, "limit": self.max_rows}

    def _fetch_data_(self) -> None:
        """Carga toda la tabla en memoria"""
        if self.name_domain and not self.advanced_domain:
            self.container = (
                self.model.chunk(**self.chunk)
                .filter(**self.name_domain)
                .all()
                .container()
            )
        elif self.advanced_domain:
            self.container = (
                self.model
                .chunk(**self.chunk)
                .filter(**self.advanced_domain)
                .all()
                .container()
            )
        else:
            self.container = self.model.chunk(**self.chunk).all().container()

    def _construct_flet_columns_(self) -> None:
        """Extracción de columnas; Lista de columnas Flet"""
        self.columns = []
        if self.container is not None:
            for column, metadata in self.container[self.table].items():
                validate = ((column != "@main_table@"), (column != "@depends@"))
                if all(validate):
                    self.columns.append(column)

            self.flet_columns = [
                ft.DataColumn(
                    label=ft.Text(
                        str(self.container[self.table][COL]["label"]),
                        font_family="GeistSansBlack",
                    )
                )
                for COL in self.columns
            ]
        if self.columns:
            self.domain_select_column = ft.Dropdown(
                width=700,
                menu_height=300,
                value=self.columns[0],
                options=[
                    ft.DropdownOption(
                        key=col,
                        text=self.model_labels[i],
                        trailing_icon=ft.Icons.VIEW_COLUMN
                    )
                    for i, col in enumerate(self.columns)
                ]
            )

    def _construct_flet_rows_(self) -> None:
        """Extraer y construir las filas del query devuelto actual"""
        raw = []  # Extraccion
        if self.container is not None:
            for field, metadata in self.container[self.table].items():
                validate = ((field != "@main_table@"), (field != "@depends@"))
                if all(validate):
                    raw.append(metadata["vector"])

        # Filas crudas transpuestas
        self.rows = list(zip(*raw))

        # Filas FLet
        self.flet_rows = [
            ft.DataRow(
                on_select_change=self.current_row,  # Seleccion fila.
                selected=False,  # Este argumento muestra el check
                cells=[ft.DataCell(ft.Text(cell)) for cell in row],
            )
            for row in self.rows
        ]

    def _vector_length_(self) -> None:
        """Largo del query actual (vector)"""
        self.length = len(self.rows) if self.rows else 0

    def _word_pattern_search_(self, pattern):
        """Query a la base de datos; registros que coincidan con patron"""
        # Siempre se toma la primer columna del modelo como el nombre.
        name_field = self.model._metadata[self.table]["columns"][1]
        kwargs = {f"{self.table}__{name_field}__like": f"%{pattern}%"}
        row, col = self.model.filter(**kwargs).all().raw(align=True)
        # Si no hay data devuelve lista vacia.
        return row[1] if row else []

    async def _handle_tile_click_(self, e) -> None:
        """Evento: click sobre item de la searchbar"""

        # Item seleccionado:
        selection = e.control.data
        # Se asigna el item como valor de la busqueda.
        if self.search_bar is not None:
            self.search_bar.value = selection
            # Columna nombre del modelo actual.
            name_field = self.model._metadata[self.table]["columns"][1]
            # Dominio del query:
            domain = {f"{self.table}__{name_field}__like": selection}
            self.advanced_domain = False
            self.name_domain = domain
            # Se extrae la información:
            self.current_page = 1
            self._calculate_chunk_()
            self._fetch_data_()
            self._construct_flet_rows_()
            self.datatable.rows = self.flet_rows
            await self.search_bar.close_view()
            self.counter.value = str(self.current_page)
            self.update()

    def _build_search_bar_tiles_(self, items):
        """
        Construye las opciones a mostrar en la searchbar:
        Esta construcción esta optimizada porque solo construye según el query
        de opciones que se ajustan al patrón de busqueda.
        """
        # Se ocupan ft.ListTile() para rellena la lista
        bar_tiles: list[ft.Control] = [
            ft.ListTile(
                title=ft.Text(item),
                data=item,
                on_click=self._handle_tile_click_,
            )
            for item in items
        ]
        return bar_tiles

    def handle_search_bar_change(self, e) -> None:
        """Se dispara cuando se escribe sobre la searchbar"""
        pattern = e.control.value
        options = self._word_pattern_search_(pattern=pattern)
        if options:
            if self.search_bar is not None:
                self.search_bar.controls = self._build_search_bar_tiles_(
                    items=options
                )

    async def _handle_search_bar_tap_(self, e) -> None:
        """Se dispara cuando se hace click en la searchbar"""
        if self.search_bar is not None:
            await self.search_bar.open_view()

    def _search_bar_widget_(self):
        """Construcción del widget 'searchbar'."""
        self.search_bar = ft.SearchBar(
            bar_hint_text="Filtrar por nombre...",
            view_hint_text="Escribir nombre de registro...",
            on_change=self.handle_search_bar_change,
            on_tap=self._handle_search_bar_tap_,
        )

    def _header_container_widget_(self) -> None:
        """
        Monta los widgets alojados en el contenedor de la primera fila
        de contenidos:
        Esta fila representa la barra de opciones.
        1. Contador de pagina
        2. Filtro por nombre
        3. Filtro avanzado
        """

        # Contador Numerico
        self.counter = ft.Text(
            value=str(self.current_page),
            font_family="GeistSansBold",
        )
        # Conjunto de componentes (boton, numero, boton)
        self.top_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(content="-", on_click=self._counter_manager_),
                    self.counter,
                    ft.Button(content="+", on_click=self._counter_manager_),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            expand=9,
            border_radius=5,
            padding=5,
        )

        # Se asigna la funcion para dominio avanzado.
        self.custom_domain.on_click = self.domain_dialog
        # Se monta la barra de busqueda y el dominio avanzado.
        if self.search_bar is not None:
            assert isinstance(self.top_container.content, ft.Row)
            self.top_container.content.controls.append(self.search_bar)
            self.top_container.content.controls.append(self.custom_domain)

    def _create_entry_widget_(self) -> None:
        """Boton de nuevo registro, genera instancia de formulario vacio"""
        self.create_entry_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text(
                            value="Agregar Registro",
                            font_family="GeistMonoMedium",
                        ),
                        on_click=lambda e: self.create_entry(e),
                        icon=ft.Icons.ADD,
                    )
                ]
            ),
            expand=2,
        )

    def _table_widget_(self):
        """Instancia 'Datatable, permite alterar filas.'"""
        self.datatable = ft.DataTable(
            columns=self.flet_columns,
            rows=self.flet_rows,
            show_checkbox_column=True,
        )

    def _table_container_(self):
        """
        Se envuelve el componente datatable con un Row
        Permite el scroll horizontal con ADAPTIVE
        Se coloca en un container con scroll vertical.
        """
        self.datatable_container = ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Row(
                        controls=[self.datatable],
                        scroll=ft.ScrollMode.ADAPTIVE
                    )
                ],
                expand=True,
                horizontal=False,  # Permite 'scroll' horizontal
            ),
            bgcolor=ft.Colors.BLACK_12,
            border_radius=10,
            padding=5,
            expand=1,
        )

    # Contenedor Side Bar
    def _sidebar_(self):
        """Contendor dinamico, vista formulario se monta en este contenedor"""
        self.sidebar_container = ft.Container(
            content=None,
            bgcolor=ft.Colors.BLACK_12,
            border_radius=10,
            padding=5,
            expand=1,
            visible=False,  # Este campo controla si se muestra o no.
        )

    # === FUNCIONES Y LOGICA ===

    def _counter_manager_(self, e) -> None:
        """
        Evalua el tipo de evento (avanzar, retroceder)
        Crea copias de 'current_page' & 'container'
        Se altera el contador, se realizar el query.
        Si la cuenta y el query son validos; los muestra
        De lo contrario regresa al estado original usando los respaldos.
        """
        if e.control.content == "-":
            if self.current_page > 1:
                self.current_page -= 1
                self._calculate_chunk_()
                self._fetch_data_()
                self._construct_flet_rows_()
                self.datatable.rows = self.flet_rows
                if self.counter is not None:
                    self.counter.value = str(self.current_page)
                self.update()
        if e.control.content == "+":
            self.current_page_cache = self.current_page
            self.container_cache = self.container
            self.current_page += 1
            self._calculate_chunk_()
            self._fetch_data_()
            self._construct_flet_rows_()
            self._vector_length_()
            # Validación delicada; Si el row no es un None -> Continuar.
            if self.length >= 1 and self.rows[0][0] is not None:
                self.datatable.rows = self.flet_rows
                if self.counter is not None:
                    self.counter.value = str(self.current_page)
                self.update()
            else:
                self.current_page = self.current_page_cache
                self.container = self.container_cache
                self._construct_flet_rows_()
                self.datatable.rows = self.flet_rows
                if self.counter is not None:
                    self.counter.value = str(self.current_page)
                self.update()

    def create_entry(self, e):
        """
        Si se presiona:
        'Nuevo' -> Genera Formulario Limpio del Modelo -> Abre Vista
        Si se presiona Segunda Vez:
        -> Se borra el formulario -> Cierra Vista
        """
        status = self.sidebar_container.visible
        if status:
            self.sidebar_container.visible = not self.sidebar_container.visible
            self.sidebar_container.content = None
        else:
            self.sidebar_container.visible = not self.sidebar_container.visible
            self.form()
            self.sidebar_container.content = self.form_widget
        self.update()

    def current_row(self, e) -> None:
        """
        Se dispara si se selecciona una fila del datatable:
        1. Limpia el estado de seleccion en todas las filas (Elimina bug visual)
        2. Si no Sidebar -> Formulario & Seleccion fila actual, abre Sidebar.
        3. Si Sidebar -> Cierra Sidebar, limpia contenido, no selecciona fila.
        """

        self.this_row = e  # Guarda la fila actual y su indice.
        self.this_index = self.this_row.control.cells[0].content.value

        for row in self.flet_rows:
            row.selected = False
        self.datatable.rows = self.flet_rows
        status = self.sidebar_container.visible
        if status:
            # Si se tiene un formulario resetear.
            self.this_row = None
            self.this_index = "IDxxx1"
            self.response = ""
            self.sidebar_container.visible = (
                not self.sidebar_container.visible
            )
            self.sidebar_container.content = None
        else:
            e.control.selected = not e.control.selected
            self.sidebar_container.visible = (
                not self.sidebar_container.visible
            )
            current_row = [v.content.value for v in e.control.cells]
            update_data = dict(zip(self.columns, current_row))
            self.form(update_data=update_data)
            self.sidebar_container.content = self.form_widget
        self.update()


    def save_changes(self, e, update=False) -> None:
        # Status Barra lateral
        status = self.sidebar_container.visible

        # INSERT MODELO ACTUAL
        MODEL = self.model
        TABLE = self.table
        data = {}
        timestamp = {}
        for field in self.form_controls:

            # key -> metada [datetime][tabla, col, posicion & validacion]:
            PARTS = field.key.split("__")

            # En caso de ser un widget dividido (TIMESTAMP)
            if len(PARTS) == 6:
                widget = PARTS[0]
                column = PARTS[2]
                position = int(PARTS[3])
                required = PARTS[4]
                value = field.data.value
                if required == "TRUE" and value is None:
                    self.required_alert(column)
                    return

                if TABLE not in timestamp:
                    timestamp[TABLE] = {}

                if column not in timestamp[TABLE]:
                    timestamp[TABLE][column] = {"position": position}

                if widget == "DATE":
                    timestamp[TABLE][column]["date"] = value
                elif widget == "TIME":
                    timestamp[TABLE][column]["time"] = value
                else:
                    self.timestamp_error(widget)
                    return

            # Si en el formulario existe llave de 1:N saltar.
            elif len(PARTS) == 1:
                continue

            # Resto de widgets
            else:
                column = PARTS[1]
                position = int(PARTS[2])
                required = PARTS[3]

            # Extraccion de valor segun tipo de objeto
            if isinstance(field, ft.TextField):
                value = field.value
            elif isinstance(field, ft.Switch):
                value = int(field.value)
            elif isinstance(field, ft.Button):
                value = field.data.value
                if isinstance(value, datetime.datetime):
                    value = value.replace(tzinfo=calculo_de_fecha()).date()
            elif isinstance(field, ft.Dropdown):
                value = field.value
                TYPE = MODEL._metadata[TABLE]["schema"][column]["metadata"][
                    "sql_type"
                ]
                REFERENCES = MODEL._metadata[TABLE]["schema"][column][
                    "metadata"
                ]["foreign_key"]["second_table"]
                NAME = MODEL._metadata[REFERENCES]["columns"][1]
                NEW_MODEL = MODEL._family[REFERENCES]
                if TYPE == "FOREIGN KEY" and value is not None:
                    domain = {f"{REFERENCES}__{NAME}__same": value}
                    row, col = (
                        NEW_MODEL.
                        filter(**domain)
                        .all(ids=True)
                        .raw(align=True)
                    )

                    if row:
                        value = row[0][0]
            else:
                self.uncharted_field()
                return

            if required == "TRUE" and value is None:
                self.required_alert(column)
                return

            data[position] = value

        timestamp_union = {}
        # Union de datos timestamp
        for table, item in timestamp.items():
            for column, meta in item.items():
                position = meta.get("position", "")
                date_part = meta.get("date", "")
                time_part = meta.get("time", "")

                validate = ((date_part is None), (time_part is None))
                if any(validate):
                    self.required_alert(campos=[column, position])
                    return

                value = datetime.datetime.combine(date_part, time_part)
                value = value.replace(tzinfo=calculo_de_fecha())
                timestamp_union[position] = value

        merged = data | timestamp_union
        sorted_dict = dict(sorted(merged.items()))

        # Creacion lista final de datos ordenados.
        data = []
        for k, value in sorted_dict.items():
            data.append(value)

        if update:
            kwargs = {}
            # El indice de la fila actual existe en self.this_row
            # Iteracion de los datos ordenados sin el index.
            data.pop(0)
            for index, elemento in enumerate(data, start=1):
                arg = f"{TABLE}__{self.columns[index]}__{self.columns[0]}__same"
                kwargs.update({arg: (elemento, self.this_index)})
            try:
                self.model.u(**kwargs)
            except ValidationError as exc:
                msg = repr(exc.errors()[0])
                self.alert = ft.AlertDialog()
                self.alert.title = ft.Text("¡Error a nivel ORM! - Rollback")
                self.alert.content = ft.Text(msg)
                self.alert.actions = [
                    ft.Button(
                        content=ft.Text(value="Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
                self.page.show_dialog(self.alert)
                return
            except Exception as e:
                self.alert = ft.AlertDialog()
                self.alert.title = ft.Text("¡Error a nivel ORM! - Rollback")
                self.alert.content = ft.Text(f"{e}")
                self.alert.actions = [
                    ft.Button(
                        content=ft.Text(value="Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
                self.page.show_dialog(self.alert)
                return
        else:
            # kwargs - modelo actual
            kwargs = {TABLE: [tuple(data)]}
            # Insertar datos modelo actual
            try:
                self.model.i(**kwargs)
            except ValidationError as exc:
                msg = repr(exc.errors()[0])
                self.alert = ft.AlertDialog()
                self.alert.title = ft.Text("¡Error a nivel ORM! - Rollback")
                self.alert.content = ft.Text(msg)
                self.alert.actions = [
                    ft.Button(
                        content=ft.Text(value="Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
                self.page.show_dialog(self.alert)
                return
            except Exception as e:
                self.alert = ft.AlertDialog()
                self.alert.title = ft.Text("¡Error a nivel ORM! - Rollback")
                self.alert.content = ft.Text(f"{e}")
                self.alert.actions = [
                    ft.Button(
                        content=ft.Text(value="Cerrar"),
                        on_click=lambda self: self.page.pop_dialog()
                    )
                ]
                self.page.show_dialog(self.alert)
                return

        # Cerrar sidebar - Limpiar contenido
        if status:
            self.sidebar_container.visible = not self.sidebar_container.visible
            self.sidebar_container.content = None

        # Refrescar el frontend
        self._calculate_chunk_()
        self._fetch_data_()
        self._construct_flet_rows_()
        self._vector_length_()
        self.datatable.rows = self.flet_rows
        self.update()

    def delete_entry(self):
        self.page.pop_dialog()
        name = self.model._metadata[self.table]["columns"][0]
        data = None
        for wid in self.form_controls:
            PARTS = wid.key.split("__")
            if name in PARTS:
                data = wid.value
        if data is not None and isinstance(data, int):
            domain = {f"{self.table}__{name}__same": data}
            self.model.d(**domain)
            status = self.sidebar_container.visible
            if status:
                self.sidebar_container.visible = False
                self.sidebar_container.content = None
            # Refrescar el frontend
            self._calculate_chunk_()
            self._fetch_data_()
            self._construct_flet_rows_()
            self._vector_length_()
            self.datatable.rows = self.flet_rows
        else:
            self.impossible_delete()
        self.update()

    def domain_dialog(self, e):
        self.alert = ft.AlertDialog()
        self._widget_singular_iterable_range_()
        self.alert.title = ft.Text(
            value="Dominios Avanzados",
            font_family="Barlow",
            size=30
        )
        msg = (
            "1. Especifique el campo por el cual desea hacer el filtro.\n"
            "2. Seleccione un operado de comparacion.\n"
            "3. Agregue el 'dato' o 'datos' de referencia en los deplegables.\n\n"
            "Importante: El operador y el tipo de dato trabajan estrictamente en "
            "conjunto segun la situacion. Ej. 'name', '=', 'Omar'. "
        )
        self.alert.content = ft.Text(
            value=msg,
            italic=False,
            size=20
        )
        validate = (
            (self.domain_select_column is not None),
            (self.domain_select_operator is not None)
        )
        if all(validate):
            # Se agrega un espaciado entre los controles del pop-up!
            self.alert.actions_overflow_button_spacing = 10

            # Se crea y agrega contenedor para selección de campos y operadores.
            self.domain_fields_operators_container = ft.Container(
                expand=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=self.domain_select_column,
                        ),
                        ft.Container(
                            expand=True,
                            content=self.domain_select_operator,
                        ),
                    ]
                )
            )
            self.alert.actions.insert(0, self.domain_fields_operators_container)

            # Se agrega el contenedor de desplegables (Tipos de datos)
            self.alert.actions.append(self.domain_datatype_container)

            # Se agregan los botones de accion para "Dominios Avanzados"
            self.domain_buttons_container = ft.Container(
                expand=True,
                content=ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Text(value="Aplicar Dominio"),
                            on_click=self.action_advance_domain,
                            icon=ft.Icons.MANAGE_SEARCH,
                        ),
                        ft.Button(
                            content=ft.Text(value="Salir"),
                            on_click=lambda self: self.page.pop_dialog(),
                            icon=ft.Icons.UNDO,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    tight=True
                )
            )
            self.alert.actions.append(self.domain_buttons_container)

        self.page.show_dialog(self.alert)

    def action_advance_domain(self):
        """
        Dispara el evento de dominio avanzado:
        Evalua coincidencia entre operadores y datos.
        Limpia y parse los datos.
        Genea un Kwargs para un query filtrado.
        Pinta las lineas en la GUI.
        """

        def query_avanzado(valores: list[any] | str = None):
            if valores is not None:
                kw = {f"{self.table}__{FD}__{OP}": valores}
                self.advanced_domain = kw
                self.page.pop_dialog()
                self.current_page = 1
                if self.counter is not None:
                    self.counter.value = str(self.current_page)
                self._calculate_chunk_()
                self._fetch_data_()
                self._construct_flet_rows_()
                self._vector_length_()
                self.datatable.rows = self.flet_rows
                self.update()
                return

        validate_field_operator = (
            (self.domain_select_column.value),
            (self.domain_select_operator.value)
        )
        if all(validate_field_operator):
            FD = self.domain_select_column.value
            OP = self.domain_select_operator.value
            VL = ""

            if OP in self.SG_OPERATORS:
                if self.singular_input.value:
                    VL = self.singular_input.value
                else:
                    self.bad_domain(operator=OP)
                    return

            elif OP in self.ITER_OPERATORS:
                if self.tags_container.content.controls:
                    VL = []
                    for v in self.tags_container.content.controls:
                        VL.append(v.label)
                else:
                    self.bad_domain(operator=OP)
                    return

            elif OP in self.RANGE_OPERATORS:
                validate_range = (
                    (self.first_range.value), (self.second_range.value)
                )
                if all(validate_range):
                    VL = [self.first_range.value, self.second_range.value]
                else:
                    self.bad_domain(operator=OP)
                    return
            else:
                self.bad_domain(operator=OP)
                return

            # Conversion de datos segun su coincidencia con patron caracteres.
            # import ipdb; ipdb.set_trace()

            PFL = []  # Parsed float list
            PIL = []  # Parsed integer list

            if isinstance(VL, list):
                for item in VL:
                    result = re.search(self.FLOAT_EXPR, item)
                    if result:
                        if result.group() == item:
                            PFL.append(float(item))
                    else:
                        break

                if len(PFL) == len(VL):
                    query_avanzado(valores=PFL)
                    return

                for item in VL:
                    result = re.search(self.INTEGER_EXPR, item)
                    if result:
                        if result.group() == item:
                            PIL.append(int(item))
                    else:
                        break

                if len(PIL) == len(VL):
                    query_avanzado(valores=PIL)
                    return

                else:
                    self.bad_domain(operator=OP)
                    return

            else:

                es_float = re.search(self.FLOAT_EXPR, VL)
                if es_float:
                    if es_float.group() == VL:
                     query_avanzado(valores=float(VL))
                     return

                es_integer = re.search(self.INTEGER_EXPR, VL)
                if es_integer:
                    if es_integer.group() == VL:
                        query_avanzado(valores=VL)
                        return

                if OP in {"is", "isnot"} and VL == "":
                    VL = None
                query_avanzado(valores=VL)
                return

    def bad_domain(self, operator):
        self.alert = ft.AlertDialog()
        self.alert.title = ft.Text(
            color=ft.Colors.RED_600,
            value="Uso Incorrecto de Operadores",
            font_family="Barlow",
            size=24,
        )
        msg = (
            "Se esta intentando aplicar dominio avanzado usando un operador "
            "no compatible con el tipo de dato o "
            "sin especificar ningun dato en absoluto. OP: "
            f"{self.OPERATORS[operator]}. "
            "Para completar su solicitu debe relacionar operadores "
            "singulares con datos singulares. Ej. 'price', '>', '100'. "
            "Iterables  con datos lista: "
            "Ej. 'price', 'NOT IN', '[30, 40, 50]'. "
            "Rangos con 2 valores: "
            "Ej. 'date', 'BETWEEN', [2026-01-01, 2026-02-01]."
        )
        self.alert.actions = ft.Button(
            content=ft.Text("Cerrar"),
            on_click=lambda self: self.page.pop_dialog()
        )
        self.alert.content = ft.Text(value=msg, size=18, italic=False)
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def accept_changes(self, e):
        self.alert.title = ft.Text(
            value="Acción Peligrosa",
            font_family="GeistSansBlack",
            size=22,
        )
        msg = (
            "Estas por eliminar un registro de manera permanente "
            "de la base de datos. Aceptar esta accion hara imposible "
            "cualquier tipo de respaldo futuro."
        )
        accept = ft.Button(
            content=ft.Text(
                value="Aceptar",
                font_family="GeistMonoMedium"
            ),
            on_click=self.delete_entry,
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
        )
        self.alert.content = ft.Text(
            value=msg,
            font_family="GeistSansRegular"
        )
        self.alert.actions = [accept]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def required_alert(self, campos: list | str = "Aun No Hay Campos") -> None:
        """Funcion construye la alerta de campo requerido en tiempo real."""
        self.alert.title = ft.Text(value="Restricción")
        self.alert.content = ft.Text(
            value=f"Los siguientes campos son requeridos: {campos}"
        )
        self.alert.actions = [self.close_alert]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def uncharted_field(self) -> None:
        """Levanta error si algun widget flet no es procesado"""
        self.alert.title = "Tipo de dato invalido"
        self.alert.content = ft.Text(
            "Instancia de Flet no procesada. "
            "Posible error al invocar el metodo 'save_changes'"
        )
        self.alert.actions = [self.close_alert]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def timestamp_error(self, widget) -> None:
        """Alerta por si en algun momento los widgets de TIMESTAMP
        no se procesan como diccionario de datos."""
        self.alert.title = "Error Procesos 'TIMESTAMP'"
        self.alert.content = ft.Text(
            "Al intentar organizar el input en widgets "
            "TIMESTAMP. No se completo la indexacion de diccionarios."
            f"Widget {widget}"
        )
        self.alert.actions = [self.close_alert]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def impossible_delete(self):
        self.alert = ft.AlertDialog()
        self.alert.title = ft.Text(
            value="¡Imposible de completar!",
            font_family="GeistSansBlack",
            size=22,
        )
        msg = (
            "El registro no se pudo eliminar. "
            "No se encontró un indice númerico por el cual filtrar. "
            "Posible causa: Ejecutar esta acción sobre registros vacios. "
            "Algún otro error - restricción a nivel SQL puede ser el culpable. "
            "Se recomienda revisar función 'delete_entry'."
        )
        self.alert.content = ft.Text(
            value=msg,
            font_family="GeistSansRegular"
        )
        self.alert.actions = [
            ft.Button(
                bgcolor=ft.Colors.RED_600,
                content=ft.Text(
                    value="Cerrar",
                    font_family="GeistMonoMedium",
                    color=ft.Colors.WHITE
                ),
                on_click=lambda self: self.page.pop_dialog()
            )
        ]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    # === FORMULARIO ===

    def form(self, update_data=None) -> None:
        """Creacion de formulario 'Nuevo' o 'Registro'"""

        # Constantes
        # Bandera, controlar el tipo de insercion de datos.
        UPDATE = False if update_data is None else True
        MODEL = self.model
        TABLE = self.table
        ONE2MANY = "1:N"

        TITLE = ft.Container(
            content=ft.Text(
                value="Vista Formulario",
                font_family="GeistSansBlack",
                size=22
            )
        )

        # Resetear bandera si es una primera insercion de un modelo limpio.
        if update_data is not None:
            UPDATE = True if update_data[self.columns[0]] else False

        # Titulo 'Vista Formulario'
        controls: List[ft.Control] = [TITLE]

        # Limpia widget formularios antiguos
        self.form_controls = []

        # Iteracion de 'nombre columnas' crudas
        for COL in self.columns:
            # Asegurarse de que container sea distinto de None.
            if self.container is not None:
                # Extraccion de metadata y restricciones
                field_type = (
                    self.container[TABLE][COL].get("sql_type", "").upper()
                )
                field_read_only = self.container[TABLE][COL].get(
                    "readonly", False
                )
                field_required = self.container[TABLE][COL].get(
                    "required", False
                )
                sec_table = self.container[TABLE][COL].get(
                    "second_table", False
                )
                field_position = self.container[TABLE][COL].get("position", "")
                field_name = self.container[TABLE][COL].get("label", "")
                default = self.container[TABLE][COL].get("default", None)

                # Si existe N:1 -> Definimos un nombre de columna para el query
                if sec_table:
                    exp = "columns"
                    name = f"{sec_table}__{MODEL._metadata[sec_table][exp][1]}"
                else:
                    name = None

                # Required puede ser usado para validar. Pydantic lo hace igual.
                required = "TRUE" if field_required else "FALSE"

                if update_data is not None:
                    field_default = update_data.get(COL, default)

                else:
                    field_default = self.container[TABLE][COL].get(
                        "default", None
                    )

                # Extraccion de restricciones unicas de campo
                constraints = MODEL._metadata[TABLE]["schema"][COL][
                    "constraints"
                ]
                max_length = constraints.get("max_length", None)
                ge = constraints.get("ge", False)
                gt = constraints.get("gt", False)
                le = constraints.get("le", False)
                lt = constraints.get("lt", False)

                # Position: llave unica que almacena metadata 'procesamiento'.
                COL_LABEL = MODEL._metadata[TABLE]["columns"][field_position]
                position = (
                    f"{TABLE}__"  # Nombre de Tabla
                    f"{COL_LABEL}__"  # Columna "en crudo"
                    f"{str(field_position)}__"  # Posicion en la tabla
                    f"{required}__"  # Si es campo requerido
                    f"{str(uuid.uuid4())}"  # Codigo unico
                )

                # Se renderizan todos los widgets (segun el campo pasado)
                if field_type == "TEXT":
                    component = ft.TextField(
                        label=field_name,
                        key=position,
                        disabled=field_read_only,
                        value=field_default,
                    )
                    self.form_controls.append(component)

                elif field_type == "VARCHAR":
                    component = ft.TextField(
                        label=field_name,
                        key=position,
                        disabled=field_read_only,
                        max_length=max_length,
                        value=field_default,
                    )
                    self.form_controls.append(component)

                elif field_type == "INTEGER":
                    component = ft.TextField(
                        label=field_name,
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^[0-9]*$",
                            replacement_string="",
                        ),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        key=position,
                        disabled=field_read_only,
                        value=field_default,
                    )
                    self.form_controls.append(component)

                elif field_type == "FLOAT":
                    component = ft.TextField(
                        label=field_name,
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^\d*\.?\d*$",
                            replacement_string="",
                        ),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        key=position,
                        disabled=field_read_only,
                        value=field_default,
                    )
                    self.form_controls.append(component)

                elif field_type == "BOOLEAN":
                    VAL = field_default if field_default is not None else True
                    component = ft.Switch(
                        label=field_name,
                        key=position,
                        disabled=field_read_only,
                        value=VAL,
                    )
                    self.form_controls.append(component)

                elif field_type == "DATE":
                    validate = (
                        (field_default is not None),
                        (not isinstance(field_default, datetime.date)),
                    )
                    if all(validate):
                        FORMAT = "%Y-%m-%d"
                        field_default = datetime.datetime.strptime(
                            field_default, FORMAT
                        )

                    if field_read_only:
                        component = ft.TextField(
                            label=field_name,
                            key=position,
                            read_only=field_read_only,
                            value=str(field_default),
                        )

                    else:
                        picker = ft.DatePicker(value=field_default)
                        component = ft.Button(
                            content=f"{field_name}",
                            key=position,
                            disabled=field_read_only,
                            on_click=lambda e: self.page.show_dialog(picker),
                            icon=ft.Icons.CALENDAR_MONTH,
                            data=picker,
                        )

                    self.form_controls.append(component)

                elif field_type == "TIMESTAMP":
                    if field_read_only or default:
                        field_read_only = True
                        component = ft.TextField(
                            label=field_name,
                            key=position,
                            disabled=field_read_only,
                            value=field_default,
                        )
                        self.form_controls.append(component)

                    else:
                        date_picker = ft.DatePicker(value=None)
                        time_picker = ft.TimePicker(value=None)
                        date_component = ft.Button(
                            content=f"{field_name}",
                            key=f"DATE__{position}",
                            disabled=field_read_only,
                            on_click=lambda e: self.page.show_dialog(
                                date_picker
                            ),
                            icon=ft.Icons.CALENDAR_MONTH,
                            data=date_picker,
                        )
                        time_component = ft.Button(
                            content=f"{field_name}",
                            key=f"TIME__{position}",
                            disabled=field_read_only,
                            on_click=lambda e: self.page.show_dialog(
                                time_picker
                            ),
                            icon=ft.Icons.TIMER,
                            data=time_picker,
                        )

                        self.form_controls.append(date_component)
                        self.form_controls.append(time_component)

                elif field_type == "FOREIGN KEY":
                    sub_model = MODEL._family[sec_table]
                    sub_table = sub_model._table
                    ROW, COL = sub_model.select(name).all().raw(align=True)

                    selection = None
                    if ROW:
                        OPTIONS = list(ROW[0])
                        if field_default:
                            domain = {
                                f"{sub_table}__{sub_table}_id__same": int(
                                    field_default
                                )
                            }
                            element = (
                                sub_model.select(name)
                                .filter(**domain)
                                .all()
                                .raw(align=True)
                            )
                            search_var = element[0][0] if element else None
                            if search_var is not None:
                                try:
                                    indice = OPTIONS.index(*search_var)
                                    selection = OPTIONS[indice]
                                except IndexError:
                                    selection = None

                    else:
                        OPTIONS = []

                    component = ft.Dropdown(
                        label=field_name,
                        key=position,
                        value=selection,
                        options=[
                            ft.DropdownOption(key=str(op), text=str(op))
                            for op in OPTIONS
                        ],
                    )

                    self.form_controls.append(component)

                else:
                    raise TypeError(f"Unknown passed datatype {field_type}.")

        # Controles formulario de campo, fusion con controles estaticos.
        controls.extend(self.form_controls)

        # Estetica: Boton "Guardar" y "Eliminar" siempre al comienzo.
        form_header = ft.Row()
        save_button = ft.Button(
                content=ft.Text(
                    value="Guardar Cambios",
                    font_family="GeistMonoMedium"
                ),
                key="save",
                icon=ft.Icons.SAVE,
                on_click=lambda e: self.save_changes(e, update=UPDATE),
            )

        delete_button = ft.Button(
                content=ft.Text(
                    color=ft.Colors.WHITE,
                    value="Eliminar Registro",
                    font_family="GeistMonoMedium",
                ),
                key="delete",
                bgcolor=ft.Colors.RED_600,
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.WHITE,
                on_click=self.accept_changes,
            )
        form_header.controls = [save_button, delete_button]
        controls.insert(0,form_header)

        # RENDERIZA DINAMICO 1:N SOBRE UN CONTENEDOR CON SCROLLIN.
        # AUN EN CONSTRUCCIÓN
        for k, v in MODEL.schema.items():
            value = v["metadata"]["sql_type"]
            if value == ONE2MANY:
                COL_SCHEMA = [f._schema for f in MODEL._fields if f._name == k]
                # Con el esquema se puede acceder a la segunda tabla.
                # Con lasegunda tabla se puede acceder al modelo.
                # Crear un objeto renderizado de (Tablas) para campos 1:N
                # No se puede este mismo porque va a generar circular reference.
                controls.append(
                    ft.TextField(
                        value=COL_SCHEMA, key=f"1:M{str(uuid.uuid4())}"
                    )
                )

        # Construcción de elementos en la GUI personalizados.
        if self.controllers:
            for OBJECT in self.controllers:

                if isinstance(
                    OBJECT, (
                        machiatto_dataclasses.ButtonItem,
                        machiatto_dataclasses.InputField,
                    )
                ):

                    # Renderizado: Boton Personalizado.
                    if isinstance(OBJECT, machiatto_dataclasses.ButtonItem):
                        string = OBJECT.string or ""
                        controls.append(
                            ft.Button(
                                content=ft.Text(
                                    value=string,
                                    font_family="GeistMonoMedium"
                                ),
                                on_click=partial(OBJECT.function, self),
                                key="developer_controller"
                            )
                        )
                    if isinstance(OBJECT, machiatto_dataclasses.InputField):
                        VALUE = ft.Text(OBJECT.value) if OBJECT.value else None
                        RESPONSE = ft.TextField(
                            label=ft.Text(OBJECT.string) or None,
                            value=VALUE
                        )
                        controls.append(
                            ft.Container(
                                expand=True,
                                border_radius=10,
                                content=ft.Row(
                                    controls=[
                                        RESPONSE,
                                        ft.Button(
                                            content=ft.Text(
                                                value="Enviar",
                                                font_family="GeistMonoMedium"
                                            ),
                                            icon=ft.Icons.CHECK,
                                            on_click=lambda e, res=RESPONSE:
                                                self.send_response(
                                                e,
                                                response=res,
                                                function=OBJECT.function
                                            )
                                        ),
                                    ]
                                )
                            )
                        )

                else:
                    msg = (
                        "Solicitud de widget invalida. Se paso un componente "
                        "a la lista de controladores 'DatatableORM' "
                        "que no es valido para ser renderizado en la GUI. "
                        "revisar la listas de componentes validos por "
                        "'Machiatto Framework'."
                    )
                    raise ValueError(msg)

        # Se declara una vista de scroll vertical para los formularios.
        self.form_widget = ft.ListView(
            controls=[
                ft.Column(
                    controls=controls,
                    spacing=20,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                )
            ],
            expand=False,
            horizontal=False,
        )

    def send_response(self, e, response: ft.TextField, function: Callable):
        self.response = response.value
        function(self)

    # === GUARDADO CONTROLADORES PERSONALIZADOS ===
    def ensure_store(self) -> None:
        """ Para cualquier controlador personalizado, lo primero
        que se debe hacer es asegurar el guardado para obtener el 'id'."""
        if self.this_index is not None and self.this_index != "IDxxx1":
            self.save_changes(e=self.this_row, update=True)
        else:
            self.save_changes(e=False, update=False)
            ICOL = self.columns[0]
            CTAB = self.table
            line = [f"{CTAB}__{ICOL}__desc"]
            irow, icol = self.model.sort(*line).chunk(limit=1).all().raw()
            self.this_index = irow[0][0]

    # === REFRESCAR LA TABLA ===
    def refresh(self):
        # Cerrar sidebar - Limpiar contenido
        status = self.sidebar_container.visible
        if status:
            self.sidebar_container.visible = not self.sidebar_container.visible
            self.sidebar_container.content = None
            self.this_row = None
            self.this_index = "IDxxx1"
            self.response = ""

        # Refrescar el frontend
        self._calculate_chunk_()
        self._fetch_data_()
        self._construct_flet_rows_()
        self._vector_length_()
        self.datatable.rows = self.flet_rows
        self.update()

    # === CAPA SUPERIOR; MONTAR WIDGETS ===
    def _layout_(self) -> None:
        header = ft.Row(
            controls=[self.top_container, self.create_entry_container],
            expand=1,
        )
        content = ft.Row(
            controls=[self.datatable_container, self.sidebar_container],
            expand=11,
        )
        self.expand = True
        self.controls.extend([header, content])
