# Archivo vacío para que Python reconozca como paquete
from typing import List, Dict, Any
from sqlalchemy import text
from src.infrastructure.database.connection import SessionLocal

class PlayerRepository:
    def get_players_by_ids(self, player_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Obtener datos de jugadores desde la base de datos por IDs"""
        if not player_ids:
            return {}
        
        db = SessionLocal()
        try:
            # Query SQL con SQLAlchemy text()
            query = text("""
                SELECT id, name, elo, age, gender, category, 
                       positions, location, availability, 
                       acceptance_rate, last_active_days
                FROM players
                WHERE id = ANY(:ids)
            """)
            
            result = db.execute(query, {"ids": player_ids})
            
            players = {}
            for row in result:
                players[str(row[0])] = {
                    'id': str(row[0]),
                    'name': row[1],
                    'elo': int(row[2]) if row[2] else 1500,
                    'age': int(row[3]) if row[3] else 25,
                    'gender': row[4],
                    'category': row[5],
                    'positions': row[6] if row[6] else [],
                    'location': row[7] if row[7] else {},
                    'availability': row[8] if row[8] else [],
                    'acceptance_rate': float(row[9]) if row[9] else 0.5,
                    'last_active_days': int(row[10]) if row[10] else 30
                }
            
            return players
        finally:
            db.close()
