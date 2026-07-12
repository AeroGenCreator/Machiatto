PACKAGE = {
    "name": "users",
    "menu":
        {
        "label": "Usuarios",
        "path": "packages.users.views.menus",
        "icon": "person",
        "function": "main"
        },
    "container": {
        "packages.users.views.menus": ["users"]
        },
    "models": [
        {
        "Users": "packages.users.models.users",
        },
    ]
}
