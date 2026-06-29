# Modulos Python
import datetime
import uuid
from typing import List

# Modulos Terceros
import flet as ft

# Propios
from pancakes.models.model import PanCakesORM

from .search_bar_orm import SearchBarORM

# datetime.now().astimezone() detecta automáticamente el offset del sistema
fecha_local = datetime.datetime.now().astimezone()

# Extraemos la información de la zona horaria (el offset)
tz_sistema = fecha_local.tzinfo


class DatatableORM(ft.Column):
    """
    Atributos:

    model; El modelo renderizado, funciones, vistas, ... etc.
    controllers; Lista 'Peticion de componentes'.
    filters; Lista 'Peticion de filtros'.

    current_page; Ubicacion de Pagina.
    max_rows; Maximo de filas renderizadas por hoja.
    container; Query devuelto (Paquete de datos) vector = max_rows.
    table; Nombre de la tabla del modelo pasado.
    columns; Lista de tablas [strings, ... ].
    flet_columns; Columnas del query (listadas como objetos Flet).
    rows; Filas transpuestas crudas.
    flet_rows; Filas del query (listadas como objetos Flet).
    length; Largo del vector devuelto por el query actual.
    counter;
    form_controls;
    alert;

    """

    def __init__(
        self,
        model: PanCakesORM,
        controllers: List = None,
        search_bar: SearchBarORM = None
    ):
        super().__init__()
        self.model = model
        self.controllers = controllers
        self.search_bar = search_bar

        self.current_page = 1
        self.max_rows = 15
        self.container = None
        self.table = None
        self.columns = []
        self.flet_columns = []
        self.rows = []
        self.flet_rows = []
        self.length = 0
        self.counter = 1
        # Almacena los campos widgets de vista formulario 'invocada'
        self.form_controls = []
        self.alert = ft.AlertDialog()
        self.close_alert = ft.TextButton(
            "Cerrar", on_click=lambda e: self.page.pop_dialog()
        )

        # Metodos
        self._calculate_chunk_()
        self._fetch_data_()
        self._construct_flet_columns_()
        self._construct_flet_rows_()
        self._vector_length_()
        self._header_container_widget_()
        self._create_entry_widget_()
        self._table_widget_()
        self._table_container_()
        self._sidebar_()
        self._layout_()

    # === Metodos inicializacion ===

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
        self.container = self.model.chunk(**self.chunk).all().container()

    def _construct_flet_columns_(self) -> None:
        """Extracción de columnas; Lista de columnas Flet"""
        self.table = self.model._table
        self.columns = []
        for column, metadata in self.container[self.table].items():
            validate = ((column != "@main_table@"), (column != "@depends@"))
            if all(validate):
                self.columns.append(column)

        self.flet_columns = [
            ft.DataColumn(
                label=ft.Text(str(self.container[self.table][COL]["label"]))
            )
            for COL in self.columns
        ]

    def _construct_flet_rows_(self) -> None:
        """Extraer y construir las filas del query devuelto actual"""
        raw = []  # Extraccion
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

    def _header_container_widget_(self) -> None:
        """Contiene el contador de paagina"""

        # Contador Numerico
        self.counter = ft.Text(value=self.current_page)
        # Conjunto de componentes (boton, numero, boton)
        self.header_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(content="-", on_click=self._counter_manager_),
                    self.counter,
                    ft.Button(content="+", on_click=self._counter_manager_),
                ]
            )
        )
        if self.search_bar is None:
            search_bar = SearchBarORM(model=self.model)
            self.header_container.content.controls.append(search_bar)

    def _create_entry_widget_(self) -> None:
        """Boton de nuevo registro, genera instancia de formulario vacio"""
        self.create_entry_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(
                        content="Nuevo",
                        on_click=lambda e: self.create_entry(e),
                        icon=ft.Icons.ADD,
                    )
                ]
            )
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
                        controls=[self.datatable], scroll=ft.ScrollMode.ADAPTIVE
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
                self.counter.value = self.current_page
                self.update()
        if e.control.content == "+":
            self.current_page_cache = self.current_page
            self.container_cache = self.container
            self.current_page += 1
            self._calculate_chunk_()
            self._fetch_data_()
            self._construct_flet_rows_()
            self._vector_length_()
            # Esta validación es delicada; Si el row no es un None -> Continuar.
            if self.length >= 1 and self.rows[0][0] is not None:
                self.datatable.rows = self.flet_rows
                self.counter.value = self.current_page
                self.update()
            else:
                self.current_page = self.current_page_cache
                self.container = self.container_cache
                self._construct_flet_rows_()
                self.datatable.rows = self.flet_rows
                self.counter.value = self.current_page
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
        for row in self.flet_rows:
            row.selected = False
        self.datatable.rows = self.flet_rows
        status = self.sidebar_container.visible
        if status:
            self.sidebar_container.visible = not self.sidebar_container.visible
            self.sidebar_container.content = None
        else:
            e.control.selected = not e.control.selected
            self.sidebar_container.visible = not self.sidebar_container.visible
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

            # Resto de widgets
            else:
                column = PARTS[1]
                position = int(PARTS[2])
                required = PARTS[3]

            # Extraccion de valor segun tipo de objeto
            if isinstance(field, ft.TextField):
                value = field.value
            elif isinstance(field, ft.Switch):
                value = field.value
            elif isinstance(field, ft.Button):
                value = field.data.value
                if isinstance(value, datetime.datetime):
                    value = value.replace(tzinfo=tz_sistema).date()
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
                        NEW_MODEL.filter(**domain).all(ids=True).raw(align=True)
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
                value = value.replace(tzinfo=tz_sistema)
                timestamp_union[position] = value

        merged = data | timestamp_union
        sorted_dict = dict(sorted(merged.items()))

        # Creacion lista final de datos ordenados.
        data = []
        for k, value in sorted_dict.items():
            data.append(value)

        if update:
            kwargs = {}
            # El indice de la fila actual.
            current_row_index = data.pop(0)
            # Iteracion de los datos ordenados sin el index.
            for index, elemento in enumerate(data, start=1):
                arg = f"{TABLE}__{self.columns[index]}__{self.columns[0]}__same"
                kwargs.update({arg: (elemento, current_row_index)})
            self.model.u(**kwargs)
        else:
            # kwargs - modelo actual
            kwargs = {TABLE: [tuple(data)]}
            # Insertar datos modelo actual
            self.model.i(**kwargs)

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

    def required_alert(self, campos: list | str = "Aun No Hay Campos") -> None:
        """Funcion construye la alerta de campo requerido en tiempo real."""
        self.alert.title = "Restriccion"
        self.alert.content = ft.Text(
            value=f"Los siguientes campos son requeridos: {campos}"
        )
        self.alert.actions = [self.close_alert]
        self.alert.open = True
        self.page.show_dialog(self.alert)

    def uncharted_field(self) -> None:
        """Levanta error si algun widget flet no es procesado"""
        self.alert.title = "Tipo de dato invalido"
        self.alert.content = (
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
        self.alert.content = (
            "Al intentar organizar el input en widgets "
            "TIMESTAMP. No se completo la indexacion de diccionarios."
            f"Widget {widget}"
        )
        self.alert.actions = [self.close_alert]
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
                value="Vista Formulario", weight=ft.FontWeight.W_900
            )
        )

        # Resetear bandera si es una primera insercion de un modelo limpio.
        if update_data is not None:
            UPDATE = True if update_data[self.columns[0]] else False

        # Titulo 'Vista Formulario'
        controls = [TITLE]

        # Limpia widget formularios antiguos
        self.form_controls = []

        # Iteracion de 'nombre columnas' crudas
        for COL in self.columns:
            # Extraccion de metadata y restricciones
            field_type = self.container[TABLE][COL].get("sql_type", "").upper()
            field_read_only = self.container[TABLE][COL].get("readonly", False)
            field_required = self.container[TABLE][COL].get("required", False)
            sec_table = self.container[TABLE][COL].get("second_table", False)
            field_position = self.container[TABLE][COL].get("position", "")
            field_name = self.container[TABLE][COL].get("label", "")
            default = self.container[TABLE][COL].get("default", None)

            # Si existe N:1 -> Definimos un nombre de columna para el query
            if sec_table:
                name = (
                    f"{sec_table}__{MODEL._metadata[sec_table]['columns'][1]}"
                )
            else:
                name = None

            # Required puede ser usado para validar. Aunque pydantic ya lo hace.
            required = "TRUE" if field_required else "FALSE"

            if update_data is not None:
                field_default = update_data.get(COL, default)

            else:
                field_default = self.container[TABLE][COL].get("default", None)

            # Extraccion de restricciones unicas de campo
            constraints = MODEL._metadata[TABLE]["schema"][COL]["constraints"]
            max_length = constraints.get("max_length", None)
            ge = constraints.get("ge", False)
            gt = constraints.get("gt", False)
            le = constraints.get("le", False)
            lt = constraints.get("lt", False)

            # Position es una llave unica que almacena metadata 'procesamiento'.
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
                        value=field_default,
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
                        on_click=lambda e: self.page.show_dialog(date_picker),
                        icon=ft.Icons.CALENDAR_MONTH,
                        data=date_picker,
                    )
                    time_component = ft.Button(
                        content=f"{field_name}",
                        key=f"TIME__{position}",
                        disabled=field_read_only,
                        on_click=lambda e: self.page.show_dialog(time_picker),
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
                        search = element[0][0] if element else None
                        try:
                            indice = OPTIONS.index(*search)
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

        # Boton de guardar (Comienzo de controladores)
        controls.insert(
            0,
            ft.Button(
                content="Guardar Cambios",
                key="save",
                icon=ft.Icons.SAVE,
                on_click=lambda e: self.save_changes(e, update=UPDATE),
            ),
        )

        # RENDERIZA DINAMICO 1:N SOBRE UN CONTENEDOR CON SCROLLIN.
        # AUN EN CONSTRUCCIÓN
        for k, v in MODEL.schema.items():
            value = v["metadata"]["sql_type"]
            if value == ONE2MANY:
                controls.append(ft.TextField(value=value))

        # Se declara una vista de scroll vertical para los formularios.
        self.form_widget = ft.ListView(
            controls=[ft.Column(controls=controls, spacing=20, expand=True)],
            expand=True,
            horizontal=False,
        )

    # === CAPA SUPERIOR; MONTAR WIDGETS ===
    def _layout_(self) -> None:
        header = ft.Row(
            controls=[self.header_container, self.create_entry_container],
            expand=1,
        )
        content = ft.Row(
            controls=[self.datatable_container, self.sidebar_container],
            expand=11,
        )
        self.expand = True
        self.controls.extend([header, content])
