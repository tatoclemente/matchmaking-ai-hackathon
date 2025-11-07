"""
Módulo de seeders.

Scripts para poblar la base de datos con datos de prueba.
"""

from .seed_players import seed_players

__all__ = [
    "seed_players",
]
