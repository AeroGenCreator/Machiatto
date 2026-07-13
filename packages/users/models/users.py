"""
Comentario importante del desarrollador. 🐍
Este modelo es utilizado por el framework al momento de construir
la aplicacion. No se recomienda elminar o alterarlo.
"""

# Modulos Python
import os
import sqlite3

# Dependecias
from dotenv import load_dotenv
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


def init_users():
    load_dotenv()
    ADMIN = os.getenv("ADMIN", "admin")
    PASSW = os.getenv("PASSW", "admin")
    EMAIL = os.getenv("EMAIL", None)

    try:
        Users.i(users=[(None, ADMIN, EMAIL, PASSW, True)])
        return "Machiatto Users' Schema Created"
    except sqlite3.IntegrityError:
        return "Machiatto Users' Schema Loaded"
