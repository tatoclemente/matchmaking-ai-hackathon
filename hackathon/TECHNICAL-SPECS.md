# 🔧 ESPECIFICACIONES TÉCNICAS - Microservicio Matchmaking IA

## Arquitectura General

### Patrón: Microservicio Independiente
```
┌──────────────────────────────────────────────────────────┐
│                    Matchmaking IA Service                 │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   FastAPI   │  │   Services   │  │   External     │  │
│  │   Routers   │→ │  (Business)  │→ │   Adapters     │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                            │              │
│                                            ▼              │
│                          ┌──────────────────────────┐    │
│                          │  Pinecone + PostgreSQL   │    │
│                          └──────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Capas de la Aplicación

#### 1. Presentation Layer (Routers)
- **Responsabilidad:** Recibir requests HTTP, validar input, retornar responses
- **Tecnología:** FastAPI routers
- **Archivos:** `src/routers/matchmaking.py`

#### 2. Business Layer (Services)
- **Responsabilidad:** Lógica de negocio, orquestación, scoring
- **Tecnología:** Python classes
- **Archivos:** 
  - `src/services/matchmaking_service.py`
  - `src/services/scoring_service.py`

#### 3. External Layer (Adapters)
- **Responsabilidad:** Comunicación con servicios externos
- **Tecnología:** Client libraries
- **Archivos:**
  - `src/external/openai_client.py`
  - `src/external/pinecone_client.py`
  - `src/database/db_client.py`

#### 4. Domain Layer (Models)
- **Responsabilidad:** Definición de entidades y contratos
- **Tecnología:** Pydantic models
- **Archivos:**
  - `src/models/player.py`
  - `src/models/match_request.py`
  - `src/models/candidate.py`

---

## Modelos de Datos Detallados

### Player Model
```python
class Player(BaseModel):
    id: str                              # UUID
    name: str                            # Nombre completo
    elo: int                             # 800-3300+
    age: int                             # 18-60
    gender: Literal["MALE", "FEMALE"]    # Género
    category: CategoryEnum               # NINTH...FIRST
    positions: List[PositionEnum]        # [FOREHAND, BACKHAND]
    location: LocationDict               # {lat, lon, zone}
    availability: Optional[List[TimeSlot]] = None
    acceptance_rate: float               # 0.0-1.0
    last_active_days: int                # 0-999

class LocationDict(TypedDict):
    lat: float      # -90 to 90
    lon: float      # -180 to 180
    zone: str       # Nombre de la zona

class TimeSlot(BaseModel):
    min: str        # "HH:MM" formato 24h
    max: str        # "HH:MM" formato 24h

class CategoryEnum(str, Enum):
    NINTH = "NINTH"
    EIGHTH = "EIGHTH"
    SEVENTH = "SEVENTH"
    SIXTH = "SIXTH"
    FIFTH = "FIFTH"
    FOURTH = "FOURTH"
    THIRD = "THIRD"
    SECOND = "SECOND"
    FIRST = "FIRST"

class PositionEnum(str, Enum):
    FOREHAND = "FOREHAND"
    BACKHAND = "BACKHAND"
```

### MatchRequest Model
```python
class MatchRequest(BaseModel):
    match_id: str                        # UUID del partido
    categories: List[CategoryEnum]       # Categorías aceptadas
    elo_range: Tuple[int, int]          # (min, max)
    age_range: Optional[Tuple[int, int]] = None
    gender_preference: GenderPreference  # MALE, FEMALE, MIXED
    required_players: int                # 1-3
    location: LocationDict               # Ubicación del partido
    match_time: str                      # "HH:MM"
    required_time: int                   # Minutos (60-180)
    preferred_position: Optional[PositionEnum] = None

class GenderPreference(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    MIXED = "MIXED"
```

### Candidate Model
```python
class Candidate(BaseModel):
    player_id: str
    player_name: str
    score: float                         # 0.0-1.0
    distance_km: float                   # Distancia en km
    elo: int
    elo_diff: int                        # Diferencia absoluta
    acceptance_rate: float               # 0.0-1.0
    reasons: List[str]                   # Razones de compatibilidad
    invitation_message: str              # Mensaje personalizado para invitación
    compatibility_summary: str           # Resumen de compatibilidad
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "a1b2c3d4-...",
                "player_name": "Juan Pérez",
                "score": 0.87,
                "distance_km": 1.2,
                "elo": 1520,
                "elo_diff": 20,
                "acceptance_rate": 0.92,
                "reasons": ["Perfil muy compatible", "Nivel muy similar"],
                "invitation_message": "Partido muy compatible en tu zona - 95% match",
                "compatibility_summary": "Nivel similar, cerca de tu ubicación"
            }
        }
```

---

## Algoritmo de Embeddings

### Construcción del texto descriptivo

#### Para Player:
```python
def _build_player_description(player: Player) -> str:
    """
    Construir texto que capture la esencia del jugador
    """
    parts = [
        f"Jugador de pádel categoría {player.category}",
        f"ELO {player.elo}",
        f"Edad {player.age} años",
        f"Género {player.gender}",
        f"Juega de {' y '.join(player.positions)}",
        f"Zona {player.location['zone']}",
    ]
    
    if player.availability:
        times = [f"{slot['min']}-{slot['max']}" for slot in player.availability]
        parts.append(f"Disponible {', '.join(times)}")
    
    # Agregar contexto de comportamiento
    if player.acceptance_rate > 0.8:
        parts.append("Jugador muy confiable y activo")
    elif player.acceptance_rate < 0.4:
        parts.append("Jugador ocasional")
    
    if player.last_active_days < 3:
        parts.append("Usuario muy activo")
    
    return ". ".join(parts)
```

#### Para MatchRequest:
```python
def _build_request_description(request: MatchRequest) -> str:
    """
    Construir texto que capture los requisitos del partido
    """
    parts = [
        f"Partido de pádel categorías {', '.join(request.categories)}",
        f"ELO entre {request.elo_range[0]} y {request.elo_range[1]}",
        f"Zona {request.location['zone']}",
        f"Horario {request.match_time}",
        f"Duración {request.required_time} minutos",
        f"Género {request.gender_preference}",
    ]
    
    if request.age_range:
        parts.append(f"Edad {request.age_range[0]}-{request.age_range[1]} años")
    
    if request.preferred_position:
        parts.append(f"Se busca jugador de {request.preferred_position}")
    
    return ". ".join(parts)
```

### Llamada a OpenAI
```python
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=description_text,
    encoding_format="float"
)
embedding = response.data[0].embedding  # List[float] de 1536 dimensiones
```

---

## Algoritmo de Scoring Detallado

### Fórmula General
```
score_total = Σ(factor_i × peso_i) + bonuses - penalties
```

### Factores y Pesos

#### 1. Vector Similarity (40%)
```python
# Similitud coseno entre embeddings (ya calculada por Pinecone)
vector_score = pinecone_similarity * 0.40

# Thresholds:
# > 0.85 → "Perfil muy compatible"
# > 0.70 → "Buen match"
# < 0.50 → Descartado
```

#### 2. ELO Compatibility (20%)
```python
elo_center = (elo_range[0] + elo_range[1]) / 2
elo_diff = abs(player.elo - elo_center)
elo_tolerance = (elo_range[1] - elo_range[0]) / 2

# Score lineal decreciente
elo_score = max(0, 1 - elo_diff / elo_tolerance) * 0.20

# Thresholds:
# diff < 100 → "Nivel muy similar"
# diff < 200 → "Nivel compatible"
# diff > 300 → Penalización
```

#### 3. Geographic Distance (15%)
```python
distance_km = haversine_distance(player.location, request.location)

# Función de decaimiento exponencial
distance_score = (1 / (1 + distance_km / 10)) * 0.15

# Thresholds:
# < 3km → "Muy cerca del partido"
# < 5km → "Cerca"
# > 10km → Penalización fuerte
```

#### 4. Time Availability (10%)
```python
# Verificar overlap entre availability y required time
match_start = parse_time(request.match_time)
match_end = match_start + timedelta(minutes=request.required_time)

overlap_score = 0.0
for slot in player.availability:
    slot_start = parse_time(slot['min'])
    slot_end = parse_time(slot['max'])
    
    if slot_start <= match_start and match_end <= slot_end:
        overlap_score = 1.0  # Disponibilidad perfecta
        break
    elif has_partial_overlap(slot, match_start, match_end):
        overlap_minutes = calculate_overlap(slot, match_start, match_end)
        overlap_score = max(overlap_score, overlap_minutes / request.required_time)

time_score = overlap_score * 0.10

# Si no especificó availability, asumir 0.5
if not player.availability:
    time_score = 0.5 * 0.10

# Thresholds:
# overlap = 1.0 → "Horario perfecto"
# overlap > 0.8 → "Horario compatible"
```

#### 5. Acceptance Rate (10%)
```python
acceptance_score = player.acceptance_rate * 0.10

# Thresholds:
# > 0.8 → "Alta tasa de aceptación"
# > 0.6 → "Confiable"
# < 0.4 → Penalización
```

#### 6. Activity Frequency (5%)
```python
# Penalizar inactividad
last_active = player.last_active_days
activity_score = max(0, 1 - last_active / 30) * 0.05

# Thresholds:
# < 3 días → "Usuario muy activo"
# < 7 días → "Usuario activo"
# > 30 días → Penalización máxima
```

### Bonuses y Penalties

#### Position Bonus (±5%)
```python
if request.preferred_position:
    if request.preferred_position in player.positions:
        position_bonus = 0.05
        reasons.append(f"Juega de {request.preferred_position.lower()}")
    else:
        position_penalty = -0.05
```

#### Age Compatibility Bonus (±2%)
```python
if request.age_range:
    if request.age_range[0] <= player.age <= request.age_range[1]:
        age_bonus = 0.02
    else:
        age_penalty = -0.02
```

### Score Final
```python
total_score = (
    vector_score +
    elo_score +
    distance_score +
    time_score +
    acceptance_score +
    activity_score +
    position_bonus +
    age_bonus
)

# Clamp entre 0.0 y 1.0
total_score = max(0.0, min(1.0, total_score))
```

---

## Flujo de Datos Completo

### 1. Request llega a FastAPI
```python
POST /api/matchmaking/find_candidates
Body: MatchRequest
```

### 2. Validación con Pydantic
```python
request = MatchRequest(**request_body)  # Auto-validación
```

### 3. Crear embedding del request
```python
embedding_service = get_embedding_service()
request_embedding = embedding_service.create_request_embedding(request)
# → List[float] de 1536 dimensiones
```

### 4. Búsqueda vectorial en Pinecone
```python
# Construir filtros metadata
filters = {
    "category": {"$in": request.categories},
    "gender": request.gender_preference if request.gender_preference != "MIXED" else None
}

# Query
results = pinecone_client.search_similar(
    query_embedding=request_embedding,
    filters=filters,
    top_k=50
)
# → List[{id, score, metadata}]
```

### 5. Filtrado adicional
```python
filtered = []
for result in results:
    player_elo = result['metadata']['elo']
    
    # Filtro ELO range
    if not (request.elo_range[0] <= player_elo <= request.elo_range[1]):
        continue
    
    # Filtro edad (si aplica)
    if request.age_range:
        player_age = result['metadata']['age']
        if not (request.age_range[0] <= player_age <= request.age_range[1]):
            continue
    
    filtered.append(result)
```

### 6. Enriquecer con datos de DB
```python
db_client = get_db_client()
enriched = []

for result in filtered:
    player_id = result['id']
    metrics = db_client.get_player_metrics(player_id)
    
    enriched.append({
        **result,
        'acceptance_rate': metrics['acceptance_rate'],
        'last_active_days': metrics['last_active_days']
    })
```

### 7. Calcular scoring
```python
scoring_service = get_scoring_service()
candidates = []

for player_data in enriched:
    score_result = scoring_service.calculate_match_score(
        player=player_data,
        request=request,
        vector_similarity=player_data['score']  # De Pinecone
    )
    
    candidates.append(Candidate(
        player_id=player_data['id'],
        player_name=player_data['metadata']['name'],
        score=score_result['total'],
        distance_km=score_result['distance_km'],
        elo=player_data['metadata']['elo'],
        elo_diff=abs(player_data['metadata']['elo'] - sum(request.elo_range) / 2),
        acceptance_rate=player_data['acceptance_rate'],
        reasons=score_result['reasons']
    ))
```

### 8. Ordenar y retornar
```python
# Ordenar por score (acceptance_rate como desempate)
candidates.sort(
    key=lambda x: (x.score, x.acceptance_rate),
    reverse=True
)

# Retornar top 20 para invitaciones automáticas
top_candidates = candidates[:20]

# Generar mensajes personalizados
for candidate in top_candidates:
    candidate.invitation_message = generate_invitation_message(candidate, request)
    candidate.compatibility_summary = generate_compatibility_summary(candidate)

return {
    "match_id": request.match_id,
    "candidates": top_candidates,
    "total_found": len(candidates),
    "ready_for_invitations": True
}
```

---

## Configuración de Pinecone

### Crear índice
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=PINECONE_API_KEY)

pc.create_index(
    name="matchmaking-players",
    dimension=1536,  # text-embedding-3-small
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
```

### Metadata schema
```python
metadata = {
    "name": str,
    "elo": int,
    "category": str,
    "gender": str,
    "age": int,
    "zone": str,
    "positions": List[str]
}
```

### Filtros soportados
```python
# Filtro por categoría
{"category": {"$in": ["SEVENTH", "SIXTH"]}}

# Filtro por género
{"gender": "MALE"}

# Filtro por zona
{"zone": "Nueva Córdoba"}

# Filtros combinados
{
    "$and": [
        {"category": {"$in": ["SEVENTH", "SIXTH"]}},
        {"gender": "MALE"},
        {"elo": {"$gte": 1400, "$lte": 1800}}
    ]
}
```

---

## Manejo de Errores

### Errores esperados
```python
class MatchmakingError(Exception):
    """Base exception"""
    pass

class EmbeddingError(MatchmakingError):
    """Error al crear embeddings"""
    pass

class VectorSearchError(MatchmakingError):
    """Error en búsqueda vectorial"""
    pass

class DatabaseError(MatchmakingError):
    """Error de base de datos"""
    pass

class NoCandidatesFoundError(MatchmakingError):
    """No se encontraron candidatos"""
    pass
```

### Manejo en FastAPI
```python
@router.post("/find_candidates")
async def find_candidates(request: MatchRequest):
    try:
        candidates = matchmaking_service.find_candidates(request)
        
        if not candidates:
            raise NoCandidatesFoundError("No candidates found for this match")
        
        return {"match_id": request.match_id, "candidates": candidates}
    
    except NoCandidatesFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except (EmbeddingError, VectorSearchError, DatabaseError) as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Testing Strategy

### Unit Tests
```python
# test_scoring_service.py
def test_calculate_elo_score():
    player = {"elo": 1500}
    request = MatchRequest(elo_range=[1400, 1600], ...)
    
    score = scoring_service._calculate_elo_score(player, request)
    
    assert 0.15 <= score <= 0.20  # 20% weight

# test_geo_utils.py
def test_haversine_distance():
    lat1, lon1 = -31.42647, -64.18722
    lat2, lon2 = -31.43647, -64.19722
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    assert 1.0 <= distance <= 2.0  # ~1.5km
```

### Integration Tests
```python
# test_matchmaking_integration.py
@pytest.mark.integration
async def test_find_candidates_e2e():
    # Seed test player
    player = Player(...)
    await index_player(player)
    
    # Create request
    request = MatchRequest(...)
    
    # Find candidates
    response = await client.post("/api/matchmaking/find_candidates", json=request.dict())
    
    assert response.status_code == 200
    assert len(response.json()["candidates"]) > 0
    assert response.json()["candidates"][0]["score"] > 0.5
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_player_embedding(player_id: str) -> List[float]:
    """Cache embeddings para evitar recalcular"""
    pass
```

### Batch Processing
```python
def index_players_batch(players: List[Player], batch_size: int = 100):
    """Indexar en lotes para mejor performance"""
    for i in range(0, len(players), batch_size):
        batch = players[i:i+batch_size]
        embeddings = embedding_service.create_embeddings_batch(batch)
        vector_store.upsert_batch(embeddings)
```

### Connection Pooling
```python
# PostgreSQL
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)
```

---

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=matchmaking-players
DATABASE_URL=postgresql://...

# Optional
LOG_LEVEL=INFO
MAX_CANDIDATES=50
CACHE_TTL=3600
```

---

**Este documento define la arquitectura técnica completa del microservicio. Seguir estas especificaciones garantiza un sistema robusto, escalable y mantenible.**
