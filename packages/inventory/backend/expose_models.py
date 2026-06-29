from machiatto.datatable_orm import DatatableORM

from .. import models


def get_inventory():
    model = models.inventory.Inventory
    return DatatableORM(
        model=model
        )

def get_categories():
    model = models.category.Category
    return DatatableORM(
        model=model
    )
