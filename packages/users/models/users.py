"""
Comentario importante del desarrollador. 🐍
Este modelo es utilizado por el framework para construir
la aplicacion.

No se recomienda elminar o alterar su contenido.
"""
from pancakes.models.model import PanCakesORM
from pancakes.sql import datatype


class Users(PanCakesORM):
    # === MODELO CONFIG ===

    _table = "users"
    _depends = ["self"]

    # === MODELO CAMPOS ===

    nombre = datatype.Char(comment="Nombre", required=True, unique=True)
    correo = datatype.Char(
        comment="Correo", required=False, unique=True, readonly=True
    )
    password = datatype.Char(comment="Password", required=True, unique=True)
    activo = datatype.Bool(comment="Activo")
