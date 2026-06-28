"""
Carga interactiva de modulos.

Se carga:
1. Boton para barra lateral. Accion de menu principal.
2. Carga de los NavigationBarItem's
3. Modelos para poder ejecutarlos.
"""

# Modulos Python
import importlib
from pathlib import Path

# La ruta aqui es estatica. Modificar para ser leida desde un .env
IMPORT_COMPLEMENT = "packages"
PATH = Path.cwd() / IMPORT_COMPLEMENT
MANIFEST_KEY_WORD = "__manifest__.py"
METADATA_KEY_WORD = "PACKAGE"


def read_manifest(path=PATH):

    # Guarda: Nombre Directorio / Ruta Importación Al Manifest Python
    manifest = {}

    for directory in path.iterdir():
        for file in directory.iterdir():
            if file.name == MANIFEST_KEY_WORD:
                line = f"{IMPORT_COMPLEMENT}.{directory.name}.__manifest__"
                manifest.update({directory.name: line})

    # Importacion de cada __manifest__ por paquete declarado.
    container_items = {}
    sidebar_button = {}
    dynamic_models = []

    # Se importa el modulo y se accede al diccionario del __manifest__
    for directory_name, manifest_path in manifest.items():
        module = importlib.import_module(manifest_path)
        metadata = getattr(module, METADATA_KEY_WORD, None)

        if metadata is None:
            raise ValueError("Error while accessing manifest metadata.")

        # Extraccion de parametros de paquetes.
        CONTAINER_ITEMS = metadata.get("container", None)
        DYNAMIC_MODELS = metadata.get("models", None)
        SIDEBAR_BUTTON = metadata.get("menu", None)
        NAME = metadata.get("name", None)

        # Validar que todo contenga data.
        validate = (
            (CONTAINER_ITEMS is None),
            (DYNAMIC_MODELS is None),
            (SIDEBAR_BUTTON is None),
            (NAME is None),
        )

        if any(validate):
            raise ValueError("Error, no data extracted in metadata.")

        # Creacion de diccionarios etiquetados.

        # === {"Paquete": {"ruta": ["instancias", ...]}} ===
        container_items.update({NAME: CONTAINER_ITEMS})
        # === {"Paquete": {kwargs}} ===
        sidebar_button.update({NAME: SIDEBAR_BUTTON})
        # === {"Modelo": "ruta"} ===
        dynamic_models.extend(DYNAMIC_MODELS)

    # Se retornan las lecturas separadas
    return container_items, sidebar_button, dynamic_models


def load_models(models_list: list):
    """
    Ejemplo de lista de modelos. Leido desde el __manifest__.py
    [
        {
            'Inventory': 'packages.inventory.models.inventory',
            'Category': 'packages.inventory.models.category'
        }
    ]
    """
    # Iterar diccionarios de la lista.
    for dictionary in models_list:
        # Para cada diccionario importar los modelos.
        for class_name, path in dictionary.items():
            module = importlib.import_module(path)
            CLASS = getattr(module, class_name, None)
            # Si alguna ruta no se resuleve, mostrar error.
            if CLASS is None:
                raise (
                    f"Cannot import the following model: {class_name}."
                    "Make sure to be specific with the route and the class."
                )


def mapper(content: dict, sidebar_button: dict):
    """
    Ejemplo de ruta a las instancias de "topbar" - "contenido respuesta"
    {
        'inventory': {
            'packages.inventory.views.items': [
                'inventory', 'category'
            ]
        }
    }

    {
        'inventory': {
            'label': 'Inventario',
            'route': 'packages.inventory',
            'icons': 'all_inbox'
        }
    }

    ============================================================================
    Ejemplo de salida:
    [
        {
            'inventory': {
                'sidebar': {
                    'label': 'Inventario',
                    'icon': 'ALL_INBOX',
                    'function': get_inventory
                },
                'navigation': {
                    'inventory': get_inventory,
                    'category': get_categories
                }
            }
        }
    ]
    """
    # Iterar paquetes:
    mapped_controllers = []
    for package, data in content.items():
        # Diccionario por modulo
        dicc = {}
        dicc[package] = {}

        # Armar boton sidebar
        sidebar_declaration = sidebar_button.get(package, None)
        if sidebar_declaration is None:
            raise KeyError(f"No Sidebar controllers found for {package}.")

        label = sidebar_declaration.get("label", None)
        path = sidebar_declaration.get("path", None)
        icon = sidebar_declaration.get("icon", "ALL_INBOX")
        function = sidebar_declaration.get("function", None)

        file = importlib.import_module(path)
        event = getattr(file, function, None)

        validate = ((label is None), (event is None))
        if any(validate):
            raise ValueError("__manifest__; 'menu' declaration error.")

        dicc[package]["sidebar"] = {
            "label": label,
            "icon": icon,
            "function": event.function,
        }

        dicc[package]["navigation"] = {}
        for controller_path, controllers in data.items():
            module = importlib.import_module(controller_path)
            for control in controllers:
                function = getattr(module, control, None)
                if function is None:
                    raise ValueError(f"Invalid function found in {control}.")

                dicc[package]["navigation"].update({control: function.function})

        mapped_controllers.append(dicc)

    return mapped_controllers
