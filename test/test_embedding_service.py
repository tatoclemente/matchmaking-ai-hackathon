"""
Tests para EmbeddingService usando Mock Providers.

Estos tests NO llaman a OpenAI API, usan mocks.
"""

import pytest
from src.external import EmbeddingService
from src.models.player import Player
from src.models.match_request import MatchRequest
from tests.mocks.mock_embedding_provider import (
    MockEmbeddingProvider,
    DeterministicMockProvider
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_provider():
    """Fixture que retorna un MockEmbeddingProvider."""
    return MockEmbeddingProvider(dimension=1536, fixed_value=0.1)


@pytest.fixture
def deterministic_provider():
    """Fixture que retorna un DeterministicMockProvider."""
    return DeterministicMockProvider(dimension=1536)


@pytest.fixture
def embedding_service(mock_provider):
    """Fixture que retorna EmbeddingService con mock provider."""
    return EmbeddingService(provider=mock_provider)


@pytest.fixture
def sample_player():
    """Fixture con un jugador de ejemplo."""
    return Player(
        id="player-123",
        name="Juan Pérez",
        elo=1520,
        age=28,
        gender="MALE",
        category="SEVENTH",
        positions=["FOREHAND", "BACKHAND"],
        location={"lat": -31.42, "lon": -64.18, "zone": "Nueva Córdoba"},
        availability=[{"min": "18:00", "max": "22:00"}],
        acceptance_rate=0.85,
        last_active_days=2
    )


@pytest.fixture
def sample_match_request():
    """Fixture con un match request de ejemplo."""
    return MatchRequest(
        match_id="match-123",
        categories=["SEVENTH", "SIXTH"],
        elo_range=[1400, 1800],
        age_range=[25, 35],
        gender_preference="MALE",
        required_players=3,
        location={"lat": -31.42, "lon": -64.18, "zone": "Nueva Córdoba"},
        match_time="19:00",
        required_time=90,
        preferred_position="BACKHAND"
    )


# ============================================================================
# Tests de Player Embeddings
# ============================================================================

def test_create_player_embedding_returns_correct_dimension(
    embedding_service,
    sample_player
):
    """Test que el embedding de player tiene la dimensión correcta."""
    embedding = embedding_service.create_player_embedding(sample_player)
    
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


def test_create_player_embedding_uses_provider(
    embedding_service,
    sample_player,
    mock_provider
):
    """Test que se llama al provider correctamente."""
    embedding_service.create_player_embedding(sample_player)
    
    # Verificar que el provider fue llamado
    assert mock_provider.get_call_count() == 1


def test_player_description_contains_key_info(
    embedding_service,
    sample_player,
    mock_provider
):
    """Test que la descripción del jugador contiene información clave."""
    embedding_service.create_player_embedding(sample_player)
    
    # Obtener el texto que se envió al provider
    description = mock_provider.get_last_text()
    
    # Verificar que contiene info clave
    assert "SEVENTH" in description
    assert "1520" in description
    assert "28 años" in description
    assert "MALE" in description
    assert "Nueva Córdoba" in description


def test_player_description_includes_availability(
    embedding_service,
    sample_player,
    mock_provider
):
    """Test que la disponibilidad se incluye en la descripción."""
    embedding_service.create_player_embedding(sample_player)
    
    description = mock_provider.get_last_text()
    assert "18:00-22:00" in description


def test_player_description_includes_behavior_context(
    embedding_service,
    sample_player,
    mock_provider
):
    """Test que se incluye contexto comportamental."""
    # Player con alta acceptance_rate
    sample_player.acceptance_rate = 0.9
    sample_player.last_active_days = 1
    
    embedding_service.create_player_embedding(sample_player)
    
    description = mock_provider.get_last_text()
    assert "confiable" in description.lower()
    assert "activo" in description.lower()


# ============================================================================
# Tests de Match Request Embeddings
# ============================================================================

def test_create_request_embedding_returns_correct_dimension(
    embedding_service,
    sample_match_request
):
    """Test que el embedding de request tiene la dimensión correcta."""
    embedding = embedding_service.create_request_embedding(sample_match_request)
    
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


def test_request_description_contains_key_info(
    embedding_service,
    sample_match_request,
    mock_provider
):
    """Test que la descripción del request contiene información clave."""
    embedding_service.create_request_embedding(sample_match_request)
    
    description = mock_provider.get_last_text()
    
    # Verificar info clave
    assert "SEVENTH" in description
    assert "SIXTH" in description
    assert "1400" in description
    assert "1800" in description
    assert "Nueva Córdoba" in description
    assert "19:00" in description
    assert "90 minutos" in description


def test_request_description_includes_optional_fields(
    embedding_service,
    sample_match_request,
    mock_provider
):
    """Test que se incluyen campos opcionales si están presentes."""
    embedding_service.create_request_embedding(sample_match_request)
    
    description = mock_provider.get_last_text()
    
    # Campos opcionales que están presentes
    assert "25" in description  # age_range
    assert "35" in description
    assert "BACKHAND" in description  # preferred_position


# ============================================================================
# Tests de Batch Processing
# ============================================================================

def test_create_players_embeddings_batch(
    embedding_service,
    sample_player,
    mock_provider
):
    """Test de batch processing de jugadores."""
    # Crear lista de 10 jugadores
    players = [sample_player for _ in range(10)]
    
    embeddings = embedding_service.create_players_embeddings_batch(players)
    
    # Verificar resultados
    assert len(embeddings) == 10
    assert all(len(emb) == 1536 for emb in embeddings)
    
    # Verificar que se llamó al provider con batch
    assert mock_provider.get_call_count() == 10


# ============================================================================
# Tests con Deterministic Provider
# ============================================================================

def test_different_players_have_different_embeddings(deterministic_provider):
    """Test que jugadores diferentes generan embeddings diferentes."""
    service = EmbeddingService(provider=deterministic_provider)
    
    player1 = Player(
        id="p1",
        name="Juan",
        elo=1500,
        age=25,
        gender="MALE",
        category="SEVENTH",
        positions=["FOREHAND"],
        location={"lat": -31.42, "lon": -64.18, "zone": "Zone A"},
        acceptance_rate=0.8,
        last_active_days=1
    )
    
    player2 = Player(
        id="p2",
        name="María",
        elo=1600,
        age=30,
        gender="FEMALE",
        category="SIXTH",
        positions=["BACKHAND"],
        location={"lat": -31.43, "lon": -64.19, "zone": "Zone B"},
        acceptance_rate=0.9,
        last_active_days=2
    )
    
    embedding1 = service.create_player_embedding(player1)
    embedding2 = service.create_player_embedding(player2)
    
    # Los embeddings deben ser diferentes
    assert embedding1 != embedding2


def test_same_player_has_same_embedding(deterministic_provider):
    """Test que el mismo jugador genera el mismo embedding (determinístico)."""
    service = EmbeddingService(provider=deterministic_provider)
    
    player = Player(
        id="p1",
        name="Juan",
        elo=1500,
        age=25,
        gender="MALE",
        category="SEVENTH",
        positions=["FOREHAND"],
        location={"lat": -31.42, "lon": -64.18, "zone": "Zone A"},
        acceptance_rate=0.8,
        last_active_days=1
    )
    
    embedding1 = service.create_player_embedding(player)
    embedding2 = service.create_player_embedding(player)
    
    # Deben ser idénticos
    assert embedding1 == embedding2


# ============================================================================
# Tests de Service Metadata
# ============================================================================

def test_get_embedding_dimension(embedding_service):
    """Test que retorna la dimensión correcta."""
    dimension = embedding_service.get_embedding_dimension()
    assert dimension == 1536


def test_get_provider_name(embedding_service):
    """Test que retorna el nombre del provider."""
    name = embedding_service.get_provider_name()
    assert name == "MockProvider"


def test_validate_health(embedding_service):
    """Test de health check."""
    is_healthy = embedding_service.validate_health()
    assert is_healthy is True


# ============================================================================
# Tests de Edge Cases
# ============================================================================

def test_player_without_availability(embedding_service, mock_provider):
    """Test con jugador sin disponibilidad."""
    player = Player(
        id="p1",
        name="Juan",
        elo=1500,
        age=25,
        gender="MALE",
        category="SEVENTH",
        positions=["FOREHAND"],
        location={"lat": -31.42, "lon": -64.18, "zone": "Zone A"},
        availability=None,  # Sin disponibilidad
        acceptance_rate=0.8,
        last_active_days=1
    )
    
    # No debe fallar
    embedding = embedding_service.create_player_embedding(player)
    assert len(embedding) == 1536


def test_request_without_optional_fields(embedding_service):
    """Test con request sin campos opcionales."""
    request = MatchRequest(
        match_id="m1",
        categories=["SEVENTH"],
        elo_range=[1400, 1800],
        gender_preference="MIXED",
        required_players=3,
        location={"lat": -31.42, "lon": -64.18, "zone": "Zone A"},
        match_time="19:00",
        required_time=90
        # Sin age_range ni preferred_position
    )
    
    # No debe fallar
    embedding = embedding_service.create_request_embedding(request)
    assert len(embedding) == 1536


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

