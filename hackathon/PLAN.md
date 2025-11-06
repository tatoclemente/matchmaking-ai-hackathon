# 🚀 HACKATHON PLAN - MATCHMAKING IA (1 DÍA)

## 📋 OBJETIVO
Crear microservicio de matchmaking con IA real para emparejar jugadores de PADER usando embeddings y scoring inteligente.

---

## 🏗️ ARQUITECTURA

```
matchmaking-ai/
├── src/
│   ├── models/           # Pydantic models
│   ├── services/         # IA + Matchmaking logic  
│   ├── external/         # Pinecone + OpenAI clients
│   ├── database/         # PostgreSQL connection (local mock)
│   ├── seeders/          # Mock data generators
│   └── routers/          # FastAPI endpoints
├── docker-compose.yml    # PostgreSQL local
├── requirements.txt
└── .env
```

---

## 👥 DIVISIÓN DE TRABAJO (8 DEVS)

### **TEAM 1: Core Models (2 devs - 2h)**
**Responsables:** Dev1, Dev2

#### Archivos a crear:
- `src/models/player.py`
- `src/models/match_request.py` 
- `src/models/candidate.py`


#### Tareas:
```python
# models/player.py
class Player(BaseModel):
    id: str
    name: str
    elo: int                    # 800-3300+
    age: int                    # 18-60
    gender: str                 # "MALE", "FEMALE"
    category: str               # "NINTH", "EIGHTH", "SEVENTH", "SIXTH", "FIFTH", "FOURTH", "THIRD", "SECOND", "FIRST"
    positions: List[str]        # ["FOREHAND", "BACKHAND"] - puede tener una o ambas preferencias
    location: dict              # {"lat": float, "lon": float, "zone": str} # zone = locality o city.name
    availability: Optional[List[dict]] = None  # [{"min": "13:00", "max": "15:00"}, {"min": "19:00", "max": "22:00"}]
    acceptance_rate: float      # 0.0-1.0 - tasa de aceptación de invitaciones (viene de DB)
    last_active_days: int       # Días desde última actividad (viene de DB)

# models/match_request.py
class MatchRequest(BaseModel):
    match_id: str               # UUID del partido
    categories: List[str]       # ["SEVENTH", "SIXTH", "FIFTH"] - categorías aceptadas
    elo_range: List[int]        # [1400, 1800] - rango de ELO aceptado
    age_range: Optional[List[int]] = None  # [25, 35] - opcional
    gender_preference: str      # "MALE", "FEMALE", "MIXED"
    required_players: int       # Cuántos jugadores necesita (1-3)
    location: dict              # {"lat": float, "lon": float, "zone": str}
    match_time: str             # "18:00" - hora de inicio del partido
    required_time: int          # 90 - duración mínima requerida en minutos
    preferred_position: Optional[str] = None  # "FOREHAND" o "BACKHAND" - si falta una posición específica

# models/candidate.py
class Candidate(BaseModel):
    player_id: str
    player_name: str
    score: float              # 0.0 - 1.0
    distance_km: float
    elo: int
    elo_diff: int
    acceptance_rate: float
    reasons: List[str]        # Por qué es buen candidato
    invitation_message: str   # Mensaje personalizado para la invitación
    compatibility_summary: str # Resumen de compatibilidad
```

---

### **TEAM 2: External Services (2 devs - 3h)**
**Responsables:** Dev3, Dev4

#### Archivos a crear:
- `src/external/openai_client.py`
- `src/external/pinecone_client.py`
- `src/database/db_client.py`
- `src/external/config.py`

#### Tareas:
```python
# external/openai_client.py
class EmbeddingService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def create_player_embedding(self, player: Player) -> List[float]:
        """
        Crear embedding del jugador considerando:
        - ELO y categoría
        - Edad y género
        - Posiciones preferidas
        - Zona geográfica
        - Patrones de disponibilidad
        """
        text = self._build_player_description(player)
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding  # 1536 dimensiones
    
    def create_request_embedding(self, request: MatchRequest) -> List[float]:
        """
        Crear embedding del request considerando:
        - Categorías y rango ELO aceptado
        - Preferencias de género y edad
        - Ubicación del partido
        - Horario y duración
        - Posición preferida (si se especifica)
        """
        text = self._build_request_description(request)
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

# external/pinecone_client.py
class VectorStore:
    def __init__(self, api_key: str, index_name: str):
        from pinecone import Pinecone
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
    
    def upsert_player(self, player_id: str, embedding: List[float], metadata: dict):
        """Guardar embedding del jugador con metadata para filtrado"""
        self.index.upsert(vectors=[{
            "id": player_id,
            "values": embedding,
            "metadata": metadata  # elo, category, gender, zone, etc.
        }])
    
    def search_similar(self, query_embedding: List[float], 
                      filters: dict = None, top_k: int = 50) -> List[dict]:
        """Buscar jugadores similares con filtros opcionales"""
        return self.index.query(
            vector=query_embedding,
            filter=filters,
            top_k=top_k,
            include_metadata=True
        )
    
    def delete_player(self, player_id: str):
        """Eliminar jugador del índice"""
        self.index.delete(ids=[player_id])

# database/db_client.py
class DatabaseClient:
    """
    Cliente para PostgreSQL local (mock de la DB de PADER)
    En producción, esto consultaría la DB real del servidor principal
    """
    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
    
    def get_player_metrics(self, player_id: str) -> dict:
        """Obtener acceptance_rate y last_active_days"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT acceptance_rate, last_active_days 
            FROM players 
            WHERE id = %s
        """, (player_id,))
        result = cursor.fetchone()
        return {
            "acceptance_rate": result[0] if result else 0.5,
            "last_active_days": result[1] if result else 999
        }
    
    def get_all_players(self) -> List[dict]:
        """Obtener todos los jugadores para indexar"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM players")
        return cursor.fetchall()
```

#### Variables de entorno necesarias:
```bash
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=matchmaking-players
PINECONE_ENVIRONMENT=us-east-1
DATABASE_URL=postgresql://user:pass@localhost:5432/pader_mock
```

---

### **TEAM 3: IA Matchmaking (2 devs - 4h)**
**Responsables:** Dev5, Dev6

#### Archivos a crear:
- `src/services/matchmaking_service.py`
- `src/services/scoring_service.py`
- `src/utils/geo_utils.py`
- `src/utils/time_utils.py`

#### Tareas:
```python
# services/matchmaking_service.py
class MatchmakingService:
    def __init__(self, embedding_service, vector_store, scoring_service, db_client):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.scoring_service = scoring_service
        self.db_client = db_client
    
    def find_candidates(self, request: MatchRequest) -> List[Candidate]:
        """
        Pipeline de matchmaking:
        1. Crear embedding del request
        2. Buscar similares en Pinecone (top 50)
        3. Aplicar filtros obligatorios
        4. Enriquecer con datos de DB (acceptance_rate, last_active)
        5. Calcular scoring final
        6. Ordenar por score y retornar top N
        """
        # 1. Embedding del request
        request_embedding = self.embedding_service.create_request_embedding(request)
        
        # 2. Búsqueda vectorial con filtros básicos
        filters = self._build_pinecone_filters(request)
        similar_players = self.vector_store.search_similar(
            query_embedding=request_embedding,
            filters=filters,
            top_k=50
        )
        
        # 3. Filtrado adicional (ELO range, edad, etc.)
        filtered = self._apply_hard_filters(similar_players, request)
        
        # 4. Enriquecer con métricas de DB
        enriched = self._enrich_with_db_metrics(filtered)
        
        # 5. Scoring final
        candidates = []
        for player_data in enriched:
            score = self.scoring_service.calculate_match_score(
                player=player_data,
                request=request,
                vector_similarity=player_data['similarity']
            )
            candidates.append(Candidate(
                player_id=player_data['id'],
                player_name=player_data['name'],
                score=score['total'],
                distance_km=score['distance_km'],
                elo=player_data['elo'],
                elo_diff=abs(player_data['elo'] - sum(request.elo_range) / 2),
                acceptance_rate=player_data['acceptance_rate'],
                reasons=score['reasons']
            ))
        
        # 6. Ordenar por score (acceptance_rate como desempate)
        candidates.sort(key=lambda x: (x.score, x.acceptance_rate), reverse=True)
        
        return candidates[:20]  # Top 20 para invitaciones automáticas

# services/scoring_service.py
class ScoringService:
    def calculate_match_score(self, player: dict, request: MatchRequest, 
                            vector_similarity: float) -> dict:
        """
        Algoritmo de scoring con pesos:
        - Similitud vectorial (embeddings): 40%
        - ELO compatibility: 20%
        - Distancia geográfica: 15%
        - Disponibilidad horaria: 10%
        - Acceptance rate: 10%
        - Activity frequency: 5%
        """
        scores = {}
        reasons = []
        
        # 1. Similitud vectorial (40%)
        scores['vector'] = vector_similarity * 0.4
        if vector_similarity > 0.85:
            reasons.append("Perfil muy compatible")
        
        # 2. ELO compatibility (20%)
        elo_center = sum(request.elo_range) / 2
        elo_diff = abs(player['elo'] - elo_center)
        elo_tolerance = (request.elo_range[1] - request.elo_range[0]) / 2
        scores['elo'] = max(0, 1 - elo_diff / elo_tolerance) * 0.2
        if elo_diff < 100:
            reasons.append("Nivel muy similar")
        
        # 3. Distancia geográfica (15%)
        from utils.geo_utils import haversine_distance
        distance = haversine_distance(
            player['location']['lat'], player['location']['lon'],
            request.location['lat'], request.location['lon']
        )
        scores['distance'] = (1 / (1 + distance / 10)) * 0.15
        scores['distance_km'] = distance
        if distance < 3:
            reasons.append("Muy cerca del partido")
        
        # 4. Disponibilidad horaria (10%)
        from utils.time_utils import check_time_availability
        time_score = check_time_availability(
            player.get('availability'),
            request.match_time,
            request.required_time
        )
        scores['time'] = time_score * 0.1
        if time_score > 0.8:
            reasons.append("Horario perfecto")
        
        # 5. Acceptance rate (10%)
        scores['acceptance'] = player.get('acceptance_rate', 0.5) * 0.1
        if player.get('acceptance_rate', 0) > 0.8:
            reasons.append("Alta tasa de aceptación")
        
        # 6. Activity frequency (5%)
        last_active = player.get('last_active_days', 999)
        activity_score = max(0, 1 - last_active / 30)  # Penalizar >30 días
        scores['activity'] = activity_score * 0.05
        if last_active < 3:
            reasons.append("Usuario muy activo")
        
        # 7. Posición preferida (bonus si aplica)
        if request.preferred_position:
            if request.preferred_position in player.get('positions', []):
                scores['position_bonus'] = 0.05
                reasons.append(f"Juega de {request.preferred_position.lower()}")
            else:
                scores['position_bonus'] = -0.05
        
        total = sum(scores.values())
        
        return {
            'total': round(total, 3),
            'breakdown': scores,
            'reasons': reasons,
            'distance_km': round(distance, 2)
        }

# utils/geo_utils.py
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcular distancia en km entre dos coordenadas"""
    R = 6371  # Radio de la Tierra en km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

# utils/time_utils.py
from datetime import datetime, timedelta

def check_time_availability(player_availability: List[dict], 
                           match_time: str, 
                           required_minutes: int) -> float:
    """
    Verificar si el jugador está disponible en el horario del partido
    Retorna score 0.0-1.0
    """
    if not player_availability:
        return 0.5  # Si no especificó, asumir disponibilidad media
    
    match_start = datetime.strptime(match_time, "%H:%M")
    match_end = match_start + timedelta(minutes=required_minutes)
    
    for slot in player_availability:
        slot_start = datetime.strptime(slot['min'], "%H:%M")
        slot_end = datetime.strptime(slot['max'], "%H:%M")
        
        # Verificar si el partido cabe en el slot
        if slot_start <= match_start and match_end <= slot_end:
            return 1.0  # Disponibilidad perfecta
        
        # Verificar overlap parcial
        if (slot_start <= match_start < slot_end) or (slot_start < match_end <= slot_end):
            overlap_minutes = min(match_end, slot_end) - max(match_start, slot_start)
            return overlap_minutes.seconds / 60 / required_minutes
    
    return 0.0  # No hay overlap
```

---

### **TEAM 4: API + Seeders (2 devs - 3h)**
**Responsables:** Dev7, Dev8

#### Archivos a crear:
- `src/routers/matchmaking.py`
- `src/seeders/player_seeder.py`
- `src/seeders/db_seeder.py`
- `src/main.py`

#### Tareas:
```python
# routers/matchmaking.py
from fastapi import APIRouter, HTTPException
from models.match_request import MatchRequest
from models.player import Player
from models.candidate import Candidate

router = APIRouter(prefix="/api/matchmaking", tags=["matchmaking"])

@router.post("/find_candidates", response_model=List[Candidate])
async def find_candidates(request: MatchRequest):
    """
    Endpoint principal: encontrar candidatos para un partido
    """
    try:
        matchmaking_service = get_matchmaking_service()
        candidates = matchmaking_service.find_candidates(request)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index_player", status_code=201)
async def index_player(player: Player):
    """
    Indexar un jugador en Pinecone
    """
    try:
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        
        embedding = embedding_service.create_player_embedding(player)
        metadata = {
            "elo": player.elo,
            "category": player.category,
            "gender": player.gender,
            "zone": player.location['zone']
        }
        vector_store.upsert_player(player.id, embedding, metadata)
        
        return {"message": "Player indexed successfully", "player_id": player.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed_players/{count}", status_code=201)
async def seed_players(count: int = 100):
    """
    Generar y indexar N jugadores mock
    """
    try:
        seeder = PlayerSeeder()
        db_seeder = DBSeeder()
        
        # Generar jugadores
        players = seeder.generate_realistic_players(count)
        
        # Guardar en DB mock
        db_seeder.insert_players(players)
        
        # Indexar en Pinecone
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        
        for player in players:
            embedding = embedding_service.create_player_embedding(player)
            metadata = {
                "elo": player.elo,
                "category": player.category,
                "gender": player.gender,
                "zone": player.location['zone']
            }
            vector_store.upsert_player(player.id, embedding, metadata)
        
        return {
            "message": f"{count} players seeded successfully",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Status del servicio"""
    return {
        "status": "healthy",
        "service": "matchmaking-ai",
        "version": "1.0.0"
    }

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import matchmaking

app = FastAPI(
    title="PADER Matchmaking AI",
    description="Microservicio de matchmaking con IA para PADER",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matchmaking.router)

@app.get("/")
async def root():
    return {"message": "PADER Matchmaking AI - Hackathon 2025"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

#### Seeders detallados:

```python
# seeders/player_seeder.py
import random
import uuid
from faker import Faker
from models.player import Player

fake = Faker('es_AR')

class PlayerSeeder:
    
    CATEGORIES = ["NINTH", "EIGHTH", "SEVENTH", "SIXTH", "FIFTH", "FOURTH", "THIRD", "SECOND", "FIRST"]
    
    CATEGORY_ELO_MAPPING = {
        "NINTH": (0, 1199),
        "EIGHTH": (1200, 1499),
        "SEVENTH": (1500, 1799),
        "SIXTH": (1800, 2099), 
        "FIFTH": (2100, 2399),
        "FOURTH": (2400, 2699),
        "THIRD": (2700, 2999),
        "SECOND": (3000, 3299),
        "FIRST": (3300, 9999),
    }
    
    CATEGORY_DISTRIBUTION = {
        "NINTH": 0.05,
        "EIGHTH": 0.15,
        "SEVENTH": 0.30,
        "SIXTH": 0.25,
        "FIFTH": 0.15,
        "FOURTH": 0.06,
        "THIRD": 0.03,
        "SECOND": 0.008,
        "FIRST": 0.002,
    }
    
    CORDOBA_ZONES = [
        {"name": "Alta Córdoba", "lat": -31.39095, "lon": -64.18428},
        {"name": "Gral. Paz", "lat": -31.41309, "lon": -64.16751},
        {"name": "Nueva Córdoba", "lat": -31.42647, "lon": -64.18722},
        {"name": "Jardín", "lat": -31.44671, "lon": -64.18257},
        {"name": "Cerro de las Rosas", "lat": -31.38234, "lon": -64.23456},
        {"name": "Arguello", "lat": -31.35678, "lon": -64.26789},
        {"name": "Villa Belgrano", "lat": -31.36789, "lon": -64.24567},
    ]
    
    AVAILABILITY_PATTERNS = [
        [{"min": "17:00", "max": "20:00"}],  # After work
        [{"min": "18:00", "max": "22:00"}],  # Evening
        [{"min": "19:00", "max": "23:00"}],  # Night
        [{"min": "16:00", "max": "23:00"}],  # Very flexible
        [{"min": "18:30", "max": "21:30"}],  # Limited evening
        [{"min": "13:30", "max": "15:30"}],  # After lunch
        [{"min": "17:00", "max": "19:00"}, {"min": "21:00", "max": "23:00"}],  # Split
        None,  # No especificó (10% de casos)
    ]
    
    POSITIONS = [
        ["FOREHAND"],
        ["BACKHAND"],
        ["FOREHAND", "BACKHAND"],  # Indistinto
    ]
    
    def generate_realistic_players(self, count: int) -> List[Player]:
        players = []
        
        for _ in range(count):
            # Seleccionar categoría según distribución
            category = random.choices(
                list(self.CATEGORY_DISTRIBUTION.keys()),
                weights=list(self.CATEGORY_DISTRIBUTION.values())
            )[0]
            
            # ELO dentro del rango de la categoría
            elo_min, elo_max = self.CATEGORY_ELO_MAPPING[category]
            elo = random.randint(elo_min, min(elo_max, elo_min + 300))
            
            # Datos básicos
            gender = random.choice(["MALE", "FEMALE"])
            age = random.randint(18, 60)
            
            # Ubicación
            location = random.choice(self.CORDOBA_ZONES).copy()
            # Agregar variación de ±0.01 grados (~1km)
            location['lat'] += random.uniform(-0.01, 0.01)
            location['lon'] += random.uniform(-0.01, 0.01)
            
            # Disponibilidad (90% tiene, 10% no especifica)
            availability = random.choice(self.AVAILABILITY_PATTERNS)
            
            # Posiciones
            positions = random.choice(self.POSITIONS)
            
            # Métricas de comportamiento
            # Jugadores más activos tienden a tener mejor acceptance_rate
            last_active_days = random.choices(
                [0, 1, 2, 3, 5, 7, 14, 30, 60],
                weights=[15, 15, 15, 10, 10, 10, 10, 10, 5]
            )[0]
            
            # Acceptance rate correlacionado con actividad
            if last_active_days <= 3:
                acceptance_rate = random.uniform(0.7, 1.0)
            elif last_active_days <= 7:
                acceptance_rate = random.uniform(0.5, 0.8)
            else:
                acceptance_rate = random.uniform(0.2, 0.6)
            
            player = Player(
                id=str(uuid.uuid4()),
                name=fake.name(),
                elo=elo,
                age=age,
                gender=gender,
                category=category,
                positions=positions,
                location=location,
                availability=availability,
                acceptance_rate=round(acceptance_rate, 2),
                last_active_days=last_active_days
            )
            
            players.append(player)
        
        return players

# seeders/db_seeder.py
import psycopg2
from models.player import Player

class DBSeeder:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def create_tables(self):
        """Crear tabla de jugadores mock"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255),
                elo INTEGER,
                age INTEGER,
                gender VARCHAR(10),
                category VARCHAR(20),
                positions JSONB,
                location JSONB,
                availability JSONB,
                acceptance_rate FLOAT,
                last_active_days INTEGER
            )
        """)
        self.conn.commit()
    
    def insert_players(self, players: List[Player]):
        """Insertar jugadores en la DB mock"""
        cursor = self.conn.cursor()
        for player in players:
            cursor.execute("""
                INSERT INTO players VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    acceptance_rate = EXCLUDED.acceptance_rate,
                    last_active_days = EXCLUDED.last_active_days
            """, (
                player.id, player.name, player.elo, player.age, player.gender,
                player.category, player.positions, player.location,
                player.availability, player.acceptance_rate, player.last_active_days
            ))
        self.conn.commit()
```

---

## 🔧 STACK TÉCNICO

| Componente | Tecnología | Setup Time |
|------------|------------|------------|
| **Backend** | FastAPI | 30min |
| **Embeddings** | OpenAI API (text-embedding-3-small) | 1h |
| **Vector DB** | Pinecone | 1h |
| **Database** | PostgreSQL (Docker local) | 30min |
| **Scoring** | Numpy/Pandas | 2h |
| **Mock Data** | Faker + Custom | 2h |

---

## 📊 ENDPOINTS FINALES

### `POST /api/matchmaking/find_candidates`
**Request:**
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "categories": ["SEVENTH", "SIXTH", "FIFTH"],
  "elo_range": [1400, 1800],
  "age_range": [25, 35],
  "gender_preference": "MALE",
  "required_players": 3,
  "location": {
    "lat": -31.42647,
    "lon": -64.18722,
    "zone": "Nueva Córdoba"
  },
  "match_time": "18:00",
  "required_time": 90,
  "preferred_position": "BACKHAND"
}
```

**Response:**
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidates": [
    {
      "player_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "player_name": "Juan Pérez",
      "score": 0.87,
      "distance_km": 1.2,
      "elo": 1520,
      "elo_diff": 20,
      "acceptance_rate": 0.92,
      "reasons": [
        "Perfil muy compatible",
        "Nivel muy similar",
        "Muy cerca del partido",
        "Horario perfecto",
        "Alta tasa de aceptación",
        "Usuario muy activo",
        "Juega de backhand"
      ]
    },
    {
      "player_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "player_name": "María González",
      "score": 0.82,
      "distance_km": 2.5,
      "elo": 1480,
      "elo_diff": 80,
      "acceptance_rate": 0.85,
      "reasons": [
        "Perfil muy compatible",
        "Muy cerca del partido",
        "Alta tasa de aceptación",
        "Juega de backhand"
      ]
    }
  ]
}
```

### `POST /api/matchmaking/index_player`
**Request:**
```json
{
  "id": "player_123",
  "name": "Juan Pérez",
  "elo": 1450,
  "age": 28,
  "gender": "MALE",
  "category": "SIXTH",
  "positions": ["FOREHAND", "BACKHAND"],
  "location": {
    "lat": -31.42647,
    "lon": -64.18722,
    "zone": "Nueva Córdoba"
  },
  "availability": [
    {"min": "18:00", "max": "22:00"}
  ],
  "acceptance_rate": 0.85,
  "last_active_days": 2
}
```

**Response:**
```json
{
  "message": "Player indexed successfully",
  "player_id": "player_123"
}
```

### `POST /api/matchmaking/seed_players/{count}`
Genera N jugadores mock y los indexa automáticamente.

**Response:**
```json
{
  "message": "100 players seeded successfully",
  "count": 100
}
```

### `GET /api/matchmaking/health`
**Response:**
```json
{
  "status": "healthy",
  "service": "matchmaking-ai",
  "version": "1.0.0"
}
```

---

## ⏰ TIMELINE HACKATHON

| Hora | Actividad | Teams |
|------|-----------|-------|
| **09:00-09:30** | Setup inicial + Git repo + Docker | Todos |
| **09:30-10:00** | Arquitectura + división tasks | Todos |
| **10:00-12:00** | Desarrollo paralelo | 4 teams |
| **12:00-13:00** | Almuerzo + integración | Todos |
| **13:00-15:00** | Testing + debugging | Todos |
| **15:00-16:00** | Seed 1000 players + refinamiento | Todos |
| **16:00-17:00** | Preparar demo + presentación | Todos |

---

## 🚀 DEMO FINAL

### Escenario de demostración:

#### 1. **Setup inicial (mostrar en pantalla)**
```bash
# Levantar PostgreSQL
docker-compose up -d

# Seed 1000 jugadores
POST /api/matchmaking/seed_players/1000
```

#### 2. **Caso de uso real**
**Historia:** "Martín creó un partido en Nueva Córdoba para las 19:00hs. Es categoría SEXTA (ELO 1850), necesita 3 jugadores más, y le falta un jugador de revés."

**Request:**
```json
{
  "match_id": "demo-match-001",
  "categories": ["SEVENTH", "SIXTH", "FIFTH"],
  "elo_range": [1600, 2000],
  "age_range": [25, 40],
  "gender_preference": "MALE",
  "required_players": 3,
  "location": {
    "lat": -31.42647,
    "lon": -64.18722,
    "zone": "Nueva Córdoba"
  },
  "match_time": "19:00",
  "required_time": 90,
  "preferred_position": "BACKHAND"
}
```

#### 3. **Mostrar resultados**
- Top 20 candidatos con scores
- Explicar por qué cada uno es buen match
- Simular: "PADER enviando invitaciones automáticamente..."
- Mostrar mensajes personalizados para cada candidato

#### 4. **Explicar el flujo automático**
- "Cuando Martín crea el partido, PADER automáticamente encuentra los 20 mejores candidatos"
- "Cada jugador recibe una invitación personalizada: 'Partido muy compatible en tu zona - 95% de match'"
- "Los jugadores solo ven: 'Te invitaron a un partido' con un botón 'Unirse'"
- "Sin búsqueda manual, sin fricción, experiencia mágica"

### Métricas a mostrar:
- ✅ **Tiempo de respuesta** <200ms
- ✅ **Precisión de matching** basada en similitud vectorial
- ✅ **Escalabilidad** (1000+ jugadores indexados)
- ✅ **IA real** (OpenAI embeddings + scoring inteligente)
- ✅ **Datos realistas** (distribución de categorías, zonas, horarios)

---

## 📦 REQUIREMENTS.TXT

```txt
fastapi[standard]==0.115.0
openai==1.54.0
pinecone-client==5.0.0
numpy==2.1.0
pandas==2.2.0
faker==30.8.0
python-dotenv==1.0.1
uvicorn[standard]==0.32.0
pydantic==2.9.0
psycopg2-binary==2.9.9
```

---

## 🔑 VARIABLES DE ENTORNO

```bash
# .env
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=matchmaking-players
PINECONE_ENVIRONMENT=us-east-1
DATABASE_URL=postgresql://pader:pader123@localhost:5432/pader_mock
```

---

## 🐳 DOCKER-COMPOSE.YML

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: pader_mock_db
    environment:
      POSTGRES_USER: pader
      POSTGRES_PASSWORD: pader123
      POSTGRES_DB: pader_mock
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## ✅ CHECKLIST FINAL

### Pre-hackathon:
- [ ] Crear cuenta OpenAI y obtener API key
- [ ] Crear cuenta Pinecone y crear índice "matchmaking-players" (1536 dimensiones)
- [ ] Configurar Git repo
- [ ] Definir estructura de carpetas
- [ ] Asignar teams y responsabilidades
- [ ] Instalar Docker

### Durante hackathon:
- [ ] Models completados (Team 1)
- [ ] External services funcionando (Team 2)  
- [ ] Algoritmo IA implementado (Team 3)
- [ ] API + seeders listos (Team 4)
- [ ] PostgreSQL corriendo en Docker
- [ ] Integración completa
- [ ] 1000+ jugadores indexados
- [ ] Testing de endpoints con Postman/Insomnia
- [ ] Demo funcionando

### Presentación:
- [ ] Explicar arquitectura IA
- [ ] Demo en vivo del matchmaking
- [ ] Mostrar métricas de performance
- [ ] Explicar scoring multi-dimensional
- [ ] Roadmap futuro (ver **EVOLUTION-ROADMAP.md** para plan completo de aprendizaje continuo)

---

## 🎯 OBJETIVOS DE ÉXITO

✅ **IA funcional** - Embeddings + scoring inteligente con 6 factores
✅ **Demo impresionante** - Matchmaking en tiempo real con datos realistas
✅ **Escalable** - Arquitectura para millones de jugadores
✅ **Realista** - Datos y algoritmos creíbles (distribución de categorías, zonas de Córdoba)
✅ **Presentable** - Story convincente para jueces
✅ **Tracking inteligente** - Prioriza jugadores confiables con alta acceptance_rate

---

## 🔮 ROADMAP FUTURO (mencionar en presentación)

**Ver documento completo:** **EVOLUTION-ROADMAP.md**

### Resumen de Fases:
- **Fase 1:** Integración con PADER + feedback real
- **Fase 2:** A/B testing y optimización automática de pesos
- **Fase 3:** Modelo predictivo de compatibilidad con ML
- **Fase 4:** Fine-tuning de embeddings con aprendizaje continuo
- **Fase 5:** IA avanzada con recomendaciones proactivas

### Evolución de Métricas:
```
Hackathon → Fase 1 → Fase 3 → Fase 5
   60%       70%      85%      95%   (Precisión)
   N/A       45%      70%      90%   (Aceptación)
```

**¡A HACKEAR! 🚀**
