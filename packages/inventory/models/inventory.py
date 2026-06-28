from pancakes.models.model import PanCakesORM
from pancakes.sql import datatype


class Inventory(PanCakesORM):
    _table = "inventory"
    _depends = ["category"]

    name = datatype.Char(comment="Nombre Producto", required=True)
    qty = datatype.Int(comment="Cantidad Stock", required=True)
    price = datatype.Float(comment="Precio Producto")
    saleable = datatype.Bool(comment="Es Vendible")
    extras = datatype.Text(comment="Notas Extras")
    sold = datatype.TimeStamp(comment="Fecha Hora Venta")
    registry = datatype.Date(comment="Fecha Ingreso")
    category_id = datatype.ForeignKey(
        comment="Producto Categoria M:1",
        second_table="category",
        column_id="category_id",
    )
