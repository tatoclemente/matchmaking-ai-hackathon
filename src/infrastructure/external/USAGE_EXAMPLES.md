# 📚 Guía de Uso - Embedding Service con Patrón Adapter

## 🎯 ¿Por qué usar el patrón Adapter?

### Ventajas:
1. **🔄 Flexibilidad**: Cambiar de proveedor (OpenAI → Anthropic) sin tocar el código
2. **🧪 Testing**: Mockear fácilmente para tests
3. **🛡️ Abstracción**: El resto del código no conoce detalles de implementación
4. **📦 Separación de responsabilidades**: Cada clase tiene un propósito claro

---

## 📁 Estructura de Archivos

```
src/external/
├── embedding_provider.py      # 🎯 Interfaz abstracta (contrato)
├── openai_adapter.py          # 🤖 Implementación para OpenAI
├── embedding_service.py       # 🔧 Servicio de alto nivel
├── factories.py               # 🏭 Creación de instancias
└── __init__.py                # 📦 Exports públicos
```

### Responsabilidades:

| Archivo | Responsabilidad |
|---------|----------------|
| `embedding_provider.py` | Define la interfaz que todos los providers deben implementar |
| `openai_adapter.py` | Adapter específico para OpenAI API |
| `embedding_service.py` | Lógica de negocio (construir textos descriptivos) |
| `factories.py` | Crear instancias según configuración |

---

## 🚀 Ejemplos de Uso

### 1️⃣ Uso Básico (Más Simple)

```python
from src.external import get_embedding_service
from src.models.player import Player

# Obtener servicio (usa OpenAI por defecto)
embedding_service = get_embedding_service()

# Crear embedding de un jugador
player = Player(
    id="player-123",
    name="Juan Pérez",
    elo=1520,
    age=28,
    gender="MALE",
    category="SEVENTH",
    positions=["FOREHAND"],
    location={"lat": -31.42, "lon": -64.18, "zone": "Nueva Córdoba"},
    acceptance_rate=0.85,
    last_active_days=2
)

embedding = embedding_service.create_player_embedding(player)
print(f"✅ Embedding creado: {len(embedding)} dimensiones")
# Output: ✅ Embedding creado: 1536 dimensiones
```

### 2️⃣ Uso con Factory (Más Control)

```python
from src.external import EmbeddingServiceFactory

# Crear servicio con configuración específica
embedding_service = EmbeddingServiceFactory.create_service(
    provider_type="openai",
    model="text-embedding-3-small"
)

# Usar el servicio
embedding = embedding_service.create_player_embedding(player)
```

### 3️⃣ Uso Directo del Adapter (Más Bajo Nivel)

```python
from src.external import OpenAIAdapter, EmbeddingService

# Crear adapter manualmente
adapter = OpenAIAdapter.get_instance(
    api_key="sk-proj-...",
    model="text-embedding-3-small"
)

# Crear servicio con el adapter
service = EmbeddingService(provider=adapter)

# Usar
embedding = service.create_player_embedding(player)
```

### 4️⃣ Crear Embedding de Match Request

```python
from src.external import get_embedding_service
from src.models.match_request import MatchRequest

service = get_embedding_service()

match_request = MatchRequest(
    match_id="match-123",
    categories=["SEVENTH", "SIXTH"],
    elo_range=[1400, 1800],
    gender_preference="MALE",
    required_players=3,
    location={"lat": -31.42, "lon": -64.18, "zone": "Nueva Córdoba"},
    match_time="19:00",
    required_time=90
)

embedding = service.create_request_embedding(match_request)
print(f"✅ Match embedding: {len(embedding)} dims")
```

### 5️⃣ Batch Processing (Múltiples Jugadores)

```python
from src.external import get_embedding_service

service = get_embedding_service()

# Lista de jugadores
players = [player1, player2, player3, ...]  # hasta 100

# Crear embeddings en batch (más eficiente)
embeddings = service.create_players_embeddings_batch(players)

print(f"✅ Creados {len(embeddings)} embeddings")

# Usar los embeddings
for player, embedding in zip(players, embeddings):
    # Guardar en Pinecone, etc.
    print(f"Player {player.id}: {len(embedding)} dims")
```

---

## 🔧 Integración con Matchmaking Service

### En `src/services/matchmaking_service.py`:

```python
from src.external import get_embedding_service
from src.external.pinecone_client import VectorStore
from src.models.match_request import MatchRequest

class MatchmakingService:
    def __init__(self):
        # Obtener servicio de embeddings
        self.embedding_service = get_embedding_service()
        self.vector_store = VectorStore.get_instance()
    
    async def find_candidates(self, request: MatchRequest):
        # 1. Crear embedding del request
        request_embedding = self.embedding_service.create_request_embedding(request)
        
        # 2. Buscar en Pinecone
        similar_players = self.vector_store.search_similar(
            query_embedding=request_embedding,
            top_k=50
        )
        
        # 3. Continuar con scoring, etc.
        # ...
```

---

## 🧪 Testing con Mocks

### Crear un Mock Provider:

```python
# tests/mocks/mock_embedding_provider.py
from src.external import EmbeddingProvider
from typing import List

class MockEmbeddingProvider(EmbeddingProvider):
    """Mock provider para testing"""
    
    def create_embedding(self, text: str) -> List[float]:
        # Retornar embedding fake de 1536 dimensiones
        return [0.1] * 1536
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        return 1536
    
    def get_provider_name(self) -> str:
        return "Mock"
    
    def validate_health(self) -> bool:
        return True
```

### Usar en Tests:

```python
# tests/test_matchmaking_service.py
import pytest
from src.services.matchmaking_service import MatchmakingService
from src.external import EmbeddingService
from tests.mocks.mock_embedding_provider import MockEmbeddingProvider

def test_find_candidates():
    # Crear servicio con mock provider
    mock_provider = MockEmbeddingProvider()
    embedding_service = EmbeddingService(provider=mock_provider)
    
    # Inyectar en MatchmakingService
    matchmaking = MatchmakingService()
    matchmaking.embedding_service = embedding_service
    
    # Test sin llamar a OpenAI real
    candidates = matchmaking.find_candidates(request)
    
    assert len(candidates) > 0
```

---

## 🔄 Cambiar de Proveedor (Futuro)

### Cuando implementes Anthropic:

1. **Crear el adapter**:

```python
# src/external/anthropic_adapter.py
from .embedding_provider import EmbeddingProvider

class AnthropicAdapter(EmbeddingProvider):
    def __init__(self, api_key: str):
        # Implementar con Anthropic API
        pass
    
    def create_embedding(self, text: str):
        # Llamar a Anthropic
        pass
    
    # ... implementar todos los métodos abstractos
```

2. **Actualizar factory**:

```python
# En factories.py
def _create_anthropic_provider(**kwargs):
    from .anthropic_adapter import AnthropicAdapter
    api_key = kwargs.get("api_key", config.ANTHROPIC_API_KEY)
    return AnthropicAdapter(api_key=api_key)
```

3. **Usar el nuevo proveedor**:

```python
# En tu código
service = EmbeddingServiceFactory.create_service(
    provider_type="anthropic"  # ← Solo cambiar esto!
)

# Todo el resto del código sigue igual
embedding = service.create_player_embedding(player)
```

---

## ⚙️ Configuración

### Variables de Entorno:

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx  # Futuro
COHERE_API_KEY=xxxxxxxxxxxxx            # Futuro
```

### En `src/config.py`:

```python
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # ... otras configs
```

---

## 🎯 Mejores Prácticas

### ✅ DO:
```python
# Usar la factory
service = get_embedding_service()

# Reutilizar la instancia singleton
embedding1 = service.create_player_embedding(player1)
embedding2 = service.create_player_embedding(player2)
```

### ❌ DON'T:
```python
# No crear instancias directamente cada vez
service1 = EmbeddingService(OpenAIAdapter.get_instance(...))
service2 = EmbeddingService(OpenAIAdapter.get_instance(...))

# No llamar al constructor de Adapter directamente
adapter = OpenAIAdapter(api_key="...")  # ❌ Usa get_instance()
```

---

## 🐛 Manejo de Errores

```python
from src.external import (
    get_embedding_service,
    EmbeddingError,
    RateLimitError,
    ProviderUnavailableError
)

service = get_embedding_service()

try:
    embedding = service.create_player_embedding(player)
    
except RateLimitError as e:
    # Implementar exponential backoff
    print(f"⚠️ Rate limit: {e}")
    time.sleep(5)
    # Reintentar...
    
except ProviderUnavailableError as e:
    # Fallback a otro proveedor
    print(f"❌ OpenAI no disponible: {e}")
    # Intentar con Anthropic, etc.
    
except EmbeddingError as e:
    # Error genérico
    print(f"❌ Error creando embedding: {e}")
```

---

## 📊 Health Checks

```python
from src.external import get_embedding_service

service = get_embedding_service()

# Verificar que el servicio está funcionando
if service.validate_health():
    print("✅ Embedding service is healthy")
else:
    print("❌ Embedding service is down")

# Info del proveedor
print(f"Provider: {service.get_provider_name()}")
print(f"Dimension: {service.get_embedding_dimension()}")
```

---

## 🚀 Performance

### Optimización con Batch:

```python
# ❌ Lento - Crear embeddings uno por uno
for player in players:
    embedding = service.create_player_embedding(player)
    # Guardar en Pinecone...

# ✅ Rápido - Batch processing
embeddings = service.create_players_embeddings_batch(players)
for player, embedding in zip(players, embeddings):
    # Guardar en Pinecone...
```

**Benchmark**:
- Individual: ~100ms por embedding
- Batch (100 players): ~800ms total = ~8ms por embedding ⚡

---

## 📝 Resumen

### Flujo de Datos:

```
Player/MatchRequest
        ↓
EmbeddingService._build_description()
        ↓
"Jugador de pádel categoría SEVENTH, ELO 1520..."
        ↓
EmbeddingService.create_*_embedding()
        ↓
EmbeddingProvider.create_embedding()  ← Interface
        ↓
OpenAIAdapter.create_embedding()      ← Implementación
        ↓
OpenAI API
        ↓
[0.023, -0.012, ..., 0.045]  ← 1536 floats
```

### Ventajas del Diseño:

1. ✅ **Desacoplamiento**: Cambiar provider sin tocar business logic
2. ✅ **Testing**: Mockear fácilmente
3. ✅ **Mantenibilidad**: Cada clase tiene una responsabilidad clara
4. ✅ **Escalabilidad**: Agregar nuevos providers es trivial
5. ✅ **Type Safety**: Interfaces bien definidas

---

¡Listo para usar! 🚀

