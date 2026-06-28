from pancakes.models.model import PanCakesORM
from pancakes.sql import datatype


class Category(PanCakesORM):
    _table = "category"
    _depends = "self"

    # Campos
    name = datatype.Char(comment="Nombre Categoria", required=True, unique=True)
    inventory_ids = datatype.One2Many(
        references="inventory", inverse_column="category_id"
    )
