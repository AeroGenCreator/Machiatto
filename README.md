# 🔥 ClayPy _[PanCakesORM]() & [Flet]()_ Framework para ERP's

![image](assets/banner.png)

A traves de _ClayPy_ es posible el desarrollo de paquetes SQL -> LOGICA -> FLET a traves de el acomplamiento y desacoplamiento de modulos almacenados en el directorio packages.

## Inicion Rapido

### Manifest

```python
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
```

## Graphic User Interface

_ClayPy_ Renderiza un side menu y un contenedor de elemento a izquierda y derecha de la pantalla. A traves de de un gestor de modulos, _ClayPay_ monta y desmonta paquetes de ERP, (CRM, Contactos, Contabilidad, RH, etc ...).

Cada modulo declaradado a travez del `__manifest__.py` montara sus vistas, logica, modelos. ClayPay unicamente se encargara de gestionar rutas, renderizar elementos GUI, y de proveer al programador de algunos elementos extra como `DataTableORM` una clase que renderiza el siguiente menu al pasarle una paquete de datos `container` nativo de `PanCakesORM`. 

![image](assets/application/mounted-module.png)

## 🏗️ Jerarquía de directorios

```txt
.
└── ClayPy/
    ├── framework/
    │   └── package_loader.py
    ├── packages/
    │   └── inventory/
    │       └── __manifest__.py
    ├── requirements/
    ├── app_shell/
    ├── .gitignore
    ├── app.py
    └── README.md
``` 