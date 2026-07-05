"""
Moldes Navegacion:

Permite solicitar la carga de modelos de manera responsiva.
1. En cada paquete: Se declaran estos paquetes para cada modelo del cual
se quiera generar una vista (Tabla - Formulario).
2. Se instancia. Se especifica la ruta desde el manifest.
================================================================================

Moldes Desarrollo:

Intanciar a partir de las siguientes clases permite empaquetar
componente (Flet - Logica Backend).

DataTableORM es capaz de desempaquetar estas instancias, acomodarlas en su
respectivo contenedor y renderizar widgets.

Esto conecta backend de un modulo con 'modelo' renderizado a travez de
DataTableORM.
"""

# Python
from dataclasses import dataclass
from typing import Callable


@dataclass
class NavigationBarItem:
    function: Callable
    name: str
    key: str

