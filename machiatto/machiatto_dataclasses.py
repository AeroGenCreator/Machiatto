# ============================================================================
# Machiatto
# A modular business application framework for Python.
#
# Built on:
#   - PanCakesORM
#   - Flet
#
# Features:
#   - Module system
#   - MVC architecture
#   - Form and table views
#   - Advanced search and filters
#   - Declarative UI components
#
# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0
# ============================================================================

"""
Moldes Navegacion && Accion 📦 :

==============================================================================

Moldes Navegacion:

Permite solicitar la carga de modelos de manera responsiva.
1. En cada paquete: Se declaran estos paquetes para cada modelo del cual
se quiera generar una vista (Tabla - Formulario).
2. Se instancia. Se especifica la ruta desde el manifest.
==============================================================================

Moldes Accion:

Intanciar a partir de las siguientes clases permite empaquetar
componente (Flet - Logica Backend).

DataTableORM es capaz de desempaquetar estas instancias, acomodarlas en su
respectivo contenedor y renderizar widgets mapeando su accion 'funciones'.

Esto conecta backend de un modulo con 'modelo' renderizado a travez de
DataTableORM.
"""

# Python
from dataclasses import dataclass
from typing import Callable, Optional

# ============================================================================

# Molde Navegacion

@dataclass
class NavigationBarItem:
    function: Callable
    name: str
    key: str

# ============================================================================

# Moldes Accion

# Renderizar flet.Button en formulario
@dataclass
class ButtonItem:
    string: str
    function: Callable

# Renderizar un flet.TextField en formulario
@dataclass
class InputField:
    string: str
    value: Optional[str]
    function: Callable
    settings: Optional[any]

# ============================================================================
