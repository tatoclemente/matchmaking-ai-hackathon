"""Conexión SQLAlchemy centralizada y segura."""
from typing import Iterator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from src.infrastructure.config import config

logger = logging.getLogger(__name__)


def _create_engine_safe():
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurada en el entorno")
    try:
        # future=True habilita la API 2.0
        engine_ = create_engine(config.DATABASE_URL, pool_pre_ping=True, future=True)
        return engine_
    except Exception as e:
        logger.error("Error creando engine SQLAlchemy: %s", e)
        raise


engine = _create_engine_safe()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db() -> Iterator[Session]:
    """Yield de sesión por request. Cierra siempre al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
