# ¡Bienvenido a Machiatto!

![image](assets/banner.png)

**Machiatto** es un motor de codigo abierto pensado para la construcción rápida de software `aplicación` para pequeñas y medianas empresas. En la actualidad **machiatto** utiliza como motor de bases de datos `Sqlite3` impulsado por `PanCakesORM` como el cerebro de coordinación de modelos y logica de consultas y relaciones. El `frontend` de **machiatto** esta montado sobre componentes `Flet` los cuales han sido construidos para representar los modelos declarados brindando un tipo de vista `Tabla-Formulario`. Es debido a todo lo anterior que `Machiatto Framework` requiere puramente de `Python3+`, olvdidate de `HTML`, `CSS`, `JavaScript`, `SQL`, o algun otro lenguaje para la construccion de aplicaciones, con `Machiatto` tendras una caja de herramientas poderosa para la construcción de software.

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

**Machiatto** Renderiza un side menu y un contenedor de elemento a izquierda y derecha de la pantalla. A traves de de un gestor de modulos, **Machiatto** monta y desmonta paquetes de ERP, (CRM, Contactos, Contabilidad, RH, etc ...).

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