import psycopg2
from src.config import config
from src.external.pinecone_client import pinecone_client

def init_database():
    print("Inicializando base de datos...")
    
    conn = psycopg2.connect(config.DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            elo INTEGER NOT NULL,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL,
            category VARCHAR(20) NOT NULL,
            positions JSONB NOT NULL,
            location JSONB NOT NULL,
            availability JSONB,
            acceptance_rate FLOAT NOT NULL DEFAULT 0.5,
            last_active_days INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_elo ON players(elo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_category ON players(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_gender ON players(gender)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_acceptance_rate ON players(acceptance_rate DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_last_active ON players(last_active_days)")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✓ Base de datos PostgreSQL inicializada")

def clean_pinecone():
    print("Limpiando Pinecone...")
    pinecone_client.initialize_index()
    pinecone_client.index.delete(delete_all=True)
    print("✓ Pinecone limpiado")

if __name__ == "__main__":
    import sys
    config.validate()
    
    if "--clean-pinecone" in sys.argv:
        clean_pinecone()
    else:
        init_database()
