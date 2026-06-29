import flet as ft
from pancakes.models.model import PanCakesORM


class SearchBarORM(ft.SearchBar):
    def __init__(self, model: PanCakesORM, filters: list = None):
        super().__init__()
        self.filters = filters
        self.model = model
        self.columns = self.model._metadata[self.model._table]["columns"]
        self.bar_hint_text = "Filter selector..."
        self.view_hint_text="Choose a filter from the suggestions..."
        self.options = []
        self.construct_options()
        self.on_change = self.handle_change
        self.on_tap = self.handle_tap
        self.on_submit = None

    def search_by_name(self):
        pass

    def construct_options(self):
        self.options.insert(0, "Name Filter")
        self.controls = self.build_tiles(self.options)

    async def handle_tile_click(self, e: ft.Event[ft.ListTile]):
        await self.close_view()

    def build_tiles(self, items: list[str]) -> list[ft.Control]:
        return [
            ft.ListTile(
                title=ft.Text(item),
                data=item,
                on_click=self.handle_tile_click,
            )
            for item in items
        ]

    async def handle_change(self, e):
        query = e.control.value.strip().lower()
        filters = [
            option for option in self.options if query in option.lower()
        ] if query else self.options
        self.controls = self.build_tiles(filters)

    async def handle_tap(self, e: ft.Event[ft.SearchBar]):
        await self.open_view()
