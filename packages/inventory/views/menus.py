from machiatto.machiatto_dataclasses import NavigationBarItem

from ..backend.logics import get_categories, get_inventory

# ============================================================================

main = NavigationBarItem(
    name="Inventario",
    key="sidebar_inventario",
    function=get_inventory
)

# ============================================================================

inventory = NavigationBarItem(
    name="Inventario",
    key="inventario",
    function=get_inventory
)
category = NavigationBarItem(
    name="Inventario",
    key="categoria",
    function=get_categories
)

# ============================================================================
