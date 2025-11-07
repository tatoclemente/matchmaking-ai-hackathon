"""Inicialización y utilidades de la base de datos + limpieza de Pinecone.

Uso:
    python -m src.infrastructure.database.init_db          # Crear tablas
    python -m src.infrastructure.database.init_db --reset  # Truncar + recrear
    python -m src.infrastructure.database.init_db --clean-pinecone  # Vaciar vectores
"""
import psycopg2
from contextlib import closing
from src.infrastructure.config import config
from src.infrastructure.external.pinecone_client import init_pinecone_client, pinecone_client

def init_database():
    print("Inicializando base de datos...")
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada")

    with closing(psycopg2.connect(config.DATABASE_URL)) as conn, closing(conn.cursor()) as cursor:
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_zone ON players((location->>'zone'))")
        conn.commit()
    print("✓ Base de datos PostgreSQL inicializada")

def clean_pinecone():
    print("Limpiando Pinecone...")
    init_pinecone_client()
    assert pinecone_client is not None
    pinecone_client.initialize_index()
    if getattr(pinecone_client, "index", None) is not None:
        pinecone_client.index.delete(delete_all=True)  # type: ignore[attr-defined]
        print("✓ Pinecone limpiado")
    else:
        print("(Advertencia) Índice Pinecone no disponible")


def reset_environment():
    print("Reiniciando entorno (DB + Pinecone)...")
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada")
    with closing(psycopg2.connect(config.DATABASE_URL)) as conn, closing(conn.cursor()) as cursor:
        cursor.execute("TRUNCATE players")
        conn.commit()
    print("✓ Tabla players truncada")
    clean_pinecone()
    init_database()

if __name__ == "__main__":
    import sys
    config.validate()
    args = sys.argv[1:]
    if "--clean-pinecone" in args:
        clean_pinecone()
    elif "--reset" in args:
        reset_environment()
    else:
        init_database()
