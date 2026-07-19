from pancakes.models.model import PanCakesORM
from pancakes.sql import datatype


class Category(PanCakesORM):

    # === MODELO CONFIG ===

    _table = "category"
    _depends = "self"

    # === MODELO CAMPOS ===

    name = datatype.Char(comment="Nombre Categoria", required=True, unique=True)
    activo = datatype.Bool(comment="Activo")
    inventory_ids = datatype.One2Many(
        references="inventory", inverse_column="category_id"
    )
