PACKAGE = {
    "name": "inventory",
    "menu":
        {
        "label": "Inventario",
        "path": "packages.inventory.views.items",
        "icons": "all_inbox",
        "function": "default"
        },
    "container": {
        "packages.inventory.views.items": ["inventory", "category"]
        },
    "models": [
        {
        "Inventory": "packages.inventory.models.inventory",
        "Category": "packages.inventory.models.category"
        },
    ]
}
