from machiatto.machiatto_dataclasses import NavigationBarItem

from ..backend.logics_users import get_users

main = NavigationBarItem(
    function=get_users,
    name="Usuarios",
    key="sidebar_users",
)

users = NavigationBarItem(
    function=get_users,
    name="Usuarios",
    key="navbar_users",
)
