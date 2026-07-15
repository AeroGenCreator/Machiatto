PACKAGE = {
    "name": "users",
    "menu":
        {
        "label": "Usuarios",
        "path": "packages.users.views.menus",
        "icon": "people",
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
