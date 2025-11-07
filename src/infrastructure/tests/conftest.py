import os
import sys
from pathlib import Path
import pytest

# Añadir root del repo al sys.path (solo si no está)
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def ensure_env_keys(monkeypatch):
    if not os.environ.get("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-xxx")
    if not os.environ.get("PINECONE_API_KEY"):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-test-xxx")
    if not os.environ.get("PINECONE_ENVIRONMENT"):
        monkeypatch.setenv("PINECONE_ENVIRONMENT", "us-east-1")


@pytest.fixture(autouse=True)
def reset_singletons():
    # OpenAI
    try:
        from src.infrastructure.external.openai_client import OpenAIClient
        import src.infrastructure.external.openai_client as oc_mod
        OpenAIClient._instance = None  # type: ignore[attr-defined]
        OpenAIClient._initialized = False  # type: ignore[attr-defined]
        oc_mod.openai_client = None
    except Exception:
        pass

    # Pinecone
    try:
        from src.infrastructure.external.pinecone_client import PineconeClient
        import src.infrastructure.external.pinecone_client as pc_mod
        PineconeClient._instance = None  # type: ignore[attr-defined]
        PineconeClient._initialized = False  # type: ignore[attr-defined]
        pc_mod.pinecone_client = None
    except Exception:
        pass
