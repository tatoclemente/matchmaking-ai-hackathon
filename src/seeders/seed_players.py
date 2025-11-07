import uuid
import random
import numpy as np
import json
import psycopg2
import psycopg2.extras
from faker import Faker
from typing import List, Dict, Any
from src.config import config
from src.external.openai_client import openai_client
from src.external.pinecone_client import pinecone_client

fake = Faker('es_AR')

CATEGORIES = [
    {"name": "NINTH", "min_elo": 0, "max_elo": 1199, "weight": 0.05},
    {"name": "EIGHTH", "min_elo": 1200, "max_elo": 1499, "weight": 0.08},
    {"name": "SEVENTH", "min_elo": 1500, "max_elo": 1799, "weight": 0.12},
    {"name": "SIXTH", "min_elo": 1800, "max_elo": 2099, "weight": 0.20},
    {"name": "FIFTH", "min_elo": 2100, "max_elo": 2399, "weight": 0.25},
    {"name": "FOURTH", "min_elo": 2400, "max_elo": 2699, "weight": 0.15},
    {"name": "THIRD", "min_elo": 2700, "max_elo": 2999, "weight": 0.10},
    {"name": "SECOND", "min_elo": 3000, "max_elo": 3299, "weight": 0.03},
    {"name": "FIRST", "min_elo": 3300, "max_elo": 3800, "weight": 0.02},
]
POSITIONS = ["FOREHAND", "BACKHAND"]
GENDERS = ["MALE", "FEMALE"]
ZONES = ["Nueva Córdoba", "Centro", "Cerro de las Rosas", "Güemes", "Alta Córdoba", "Alberdi", "General Paz"]

def generate_time_slots() -> List[Dict[str, str]]:
    if random.random() < 0.3:
        return []
    
    slots = []
    num_slots = random.randint(1, 3)
    for _ in range(num_slots):
        start_hour = random.randint(8, 20)
        end_hour = start_hour + random.randint(2, 4)
        slots.append({
            'min': f"{start_hour:02d}:00",
            'max': f"{min(end_hour, 23):02d}:00"
        })
    return slots

def generate_player() -> Dict[str, Any]:
    # Seleccionar categoría con distribución ponderada
    category = random.choices(CATEGORIES, weights=[c["weight"] for c in CATEGORIES])[0]
    
    # Generar ELO dentro del rango de la categoría
    elo_range = category["max_elo"] - category["min_elo"]
    elo_center = category["min_elo"] + elo_range / 2
    elo = int(np.random.normal(elo_center, elo_range / 4))
    elo = max(category["min_elo"], min(category["max_elo"], elo))
    
    return {
        'id': str(uuid.uuid4()),
        'name': fake.name(),
        'elo': elo,
        'age': random.randint(18, 60),
        'gender': random.choice(GENDERS),
        'category': category["name"],
        'positions': random.sample(POSITIONS, k=random.randint(1, 2)),
        'location': {
            'lat': -31.4201 + random.uniform(-0.05, 0.05),
            'lon': -64.1888 + random.uniform(-0.05, 0.05),
            'zone': random.choice(ZONES)
        },
        'availability': generate_time_slots(),
        'acceptance_rate': float(np.random.beta(8, 2)),
        'last_active_days': int(np.random.exponential(5))
    }

def build_player_description(player: Dict[str, Any]) -> str:
    parts = [
        f"Jugador de pádel categoría {player['category']}",
        f"ELO {player['elo']}",
        f"Edad {player['age']} años",
        f"Género {player['gender']}",
        f"Juega de {' y '.join(player['positions'])}",
        f"Zona {player['location']['zone']}"
    ]
    
    if player['availability']:
        times = [f"{slot['min']}-{slot['max']}" for slot in player['availability']]
        parts.append(f"Disponible {', '.join(times)}")
    
    if player['acceptance_rate'] > 0.8:
        parts.append("Jugador muy confiable y activo")
    elif player['acceptance_rate'] < 0.4:
        parts.append("Jugador ocasional")
    
    if player['last_active_days'] < 3:
        parts.append("Usuario muy activo")
    
    return ". ".join(parts)

def clean_data():
    """Limpiar datos existentes de PostgreSQL y Pinecone"""
    print("Limpiando datos existentes...")
    
    # Limpiar PostgreSQL
    conn = psycopg2.connect(config.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ PostgreSQL limpiado")
    
    # Limpiar Pinecone
    pinecone_client.initialize_index()
    pinecone_client.index.delete(delete_all=True)
    print("✓ Pinecone limpiado")

def seed_players(num_players: int = 1000, batch_size: int = 100, clean: bool = True):
    if clean:
        clean_data()
    
    print(f"Generando {num_players} jugadores...")
    
    conn = psycopg2.connect(config.DATABASE_URL)
    cursor = conn.cursor()
    
    pinecone_client.initialize_index()
    
    for batch_start in range(0, num_players, batch_size):
        batch_end = min(batch_start + batch_size, num_players)
        batch_players = [generate_player() for _ in range(batch_end - batch_start)]
        
        print(f"Procesando batch {batch_start}-{batch_end}...")
        
        # Insertar en PostgreSQL
        for player in batch_players:
            cursor.execute("""
                INSERT INTO players (id, name, elo, age, gender, category, positions, location, availability, acceptance_rate, last_active_days)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                player['id'],
                player['name'],
                player['elo'],
                player['age'],
                player['gender'],
                player['category'],
                psycopg2.extras.Json(player['positions']),
                psycopg2.extras.Json(player['location']),
                psycopg2.extras.Json(player['availability']),
                player['acceptance_rate'],
                player['last_active_days']
            ))
        
        conn.commit()
        
        # Generar embeddings en batch
        descriptions = [build_player_description(p) for p in batch_players]
        embeddings = openai_client.create_embeddings_batch(descriptions)
        
        # Preparar vectores para Pinecone
        vectors = []
        for player, embedding in zip(batch_players, embeddings):
            vectors.append({
                'id': player['id'],
                'values': embedding,
                'metadata': {
                    'name': player['name'],
                    'elo': player['elo'],
                    'category': player['category'],
                    'gender': player['gender'],
                    'age': player['age'],
                    'zone': player['location']['zone'],
                    'positions': player['positions']
                }
            })
        
        pinecone_client.upsert_vectors(vectors)
        
        print(f"✓ Batch {batch_start}-{batch_end} completado")
    
    cursor.close()
    conn.close()
    
    print(f"✓ {num_players} jugadores creados exitosamente")

if __name__ == "__main__":
    import sys
    config.validate()
    
    # Opciones: python -m src.seeders.seed_players [--no-clean]
    clean = "--no-clean" not in sys.argv
    seed_players(1000, clean=clean)
