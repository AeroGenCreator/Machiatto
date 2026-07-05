import flet as ft

def main(page: ft.Page):
    page.title = "Lista de Tags en Flet"
    page.padding = 20

    # SOLUCIÓN: Usamos ft.Row con wrap=True
    tags_container = ft.Row(
        wrap=True,
        spacing=8,        # Espacio horizontal entre tags
        run_spacing=8,    # Espacio vertical entre líneas de tags
    )

    # Función para eliminar un tag específico al hacer clic en su 'X'
    def delete_tag(e):
        tags_container.controls.remove(e.control)
        page.update()

    # Función para agregar un nuevo tag desde el Input
    def add_tag_click(e):
        if tag_input.value.strip():
            # Creamos un nuevo Chip
            new_chip = ft.Chip(
                label=ft.Text(tag_input.value.strip()),
                on_delete=delete_tag, # Agrega el botón "X" para borrar
            )
            tags_container.controls.append(new_chip)
            tag_input.value = "" # Limpiamos el input
            page.update()

    # Función para ITERAR y leer los valores individuales
    def obtener_valores_tags(e):
        lista_valores = [chip.label.value for chip in tags_container.controls]
        resultado_txt.value = f"Valores individuales: {lista_valores}"
        page.update()

    # --- Elementos de la Interfaz ---
    tag_input = ft.TextField(label="Nuevo Tag", width=200, on_submit=add_tag_click)
    btn_add = ft.IconButton(icon=ft.Icons.ADD, on_click=add_tag_click)
    btn_iterar = ft.ElevatedButton("Iterar / Guardar Valores", on_click=obtener_valores_tags)
    resultado_txt = ft.Text(size=16, color="green", weight=ft.FontWeight.BOLD)

    # Agregamos todo a la página
    page.add(
        ft.Text("Ingresa tags (presiona Enter o el botón +):", size=16),
        ft.Row([tag_input, btn_add]),
        ft.Divider(),
        tags_container, # Aquí se verán los tags agrupados envoltura automática
        ft.Divider(),
        btn_iterar,
        resultado_txt
    )

ft.run(main)