"""
Módulo de base de datos.

Maneja conexiones a PostgreSQL y operaciones de base de datos.
"""

from .connection import get_connection, close_connection
from .init_db import initialize_database

__all__ = [
    "get_connection",
    "close_connection",
    "initialize_database",
]

