# 📡 API Routes - Matchmaking AI

## 🎯 Endpoints Disponibles

### Base URL
```
http://localhost:8000
```

---

## 🏠 Root Endpoints

### `GET /`
**Descripción:** Información básica del servicio  
**Response:**
```json
{
  "message": "PADER Matchmaking AI - Hackathon 2025",
  "status": "ready",
  "docs": "/docs"
}
```

### `GET /health`
**Descripción:** Health check global  
**Response:**
```json
{
  "status": "healthy",
  "service": "matchmaking-ai",
  "version": "1.0.0"
}
```

---

## 🎯 Matchmaking Endpoints

Base path: `/api/matchmaking`

### 1. `GET /api/matchmaking/health`
**Descripción:** Health check del servicio de matchmaking  
**Tags:** `matchmaking`  
**Response:** `HealthResponse`

```json
{
  "status": "healthy",
  "service": "matchmaking-ai",
  "version": "1.0.0"
}
```

---

### 2. `POST /api/matchmaking/find_candidates`
**Descripción:** **Endpoint principal** - Buscar candidatos para un partido usando IA  
**Tags:** `matchmaking`  
**Status:** `200 OK`  

**Request Body:** `MatchRequest`
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

**Response:** `MatchmakingResponse`
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidates": [
    {
      "player_id": "a1b2c3d4-...",
      "player_name": "Juan Pérez",
      "score": 0.87,
      "distance_km": 1.2,
      "elo": 1520,
      "elo_diff": 20,
      "acceptance_rate": 0.92,
      "reasons": [
        "Perfil muy compatible",
        "Nivel muy similar",
        "Muy cerca del partido"
      ],
      "invitation_message": "Partido muy compatible - 95% match",
      "compatibility_summary": "Nivel similar, cerca de tu ubicación"
    }
  ],
  "total_found": 15,
  "ready_for_invitations": true
}
```

**Errores:**
- `404`: No se encontraron candidatos
- `500`: Error en el proceso de matchmaking
- `501`: Servicio aún no implementado

---

### 3. `POST /api/matchmaking/index_player`
**Descripción:** Indexar un jugador en el sistema de embeddings  
**Tags:** `matchmaking`  
**Status:** `201 CREATED`

**Request Body:** `Player`
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

**Response:** `IndexPlayerResponse`
```json
{
  "message": "Player indexed successfully",
  "player_id": "player_123"
}
```

**Errores:**
- `500`: Error al indexar
- `501`: Servicio aún no implementado

---

### 4. `POST /api/matchmaking/seed_players/{count}`
**Descripción:** Generar y seed N jugadores mock  
**Tags:** `matchmaking`  
**Status:** `201 CREATED`

**Path Parameters:**
- `count` (int): Número de jugadores a generar (1-2000)

**Response:** `SeedResponse`
```json
{
  "message": "100 players seeded successfully",
  "count": 100
}
```

**Errores:**
- `400`: Count inválido (< 1 o > 2000)
- `500`: Error en el seeding
- `501`: Servicio aún no implementado

---

### 5. `GET /api/matchmaking/players/{player_id}`
**Descripción:** Obtener información de un jugador  
**Tags:** `matchmaking`  
**Status:** `200 OK`

**Path Parameters:**
- `player_id` (str): UUID del jugador

**Response:** `Player`
```json
{
  "id": "player_123",
  "name": "Juan Pérez",
  "elo": 1450,
  "age": 28,
  "gender": "MALE",
  "category": "SIXTH",
  "positions": ["FOREHAND", "BACKHAND"],
  "location": {...},
  "availability": [...],
  "acceptance_rate": 0.85,
  "last_active_days": 2
}
```

**Errores:**
- `404`: Jugador no encontrado
- `500`: Error obteniendo jugador
- `501`: Servicio aún no implementado

---

### 6. `DELETE /api/matchmaking/players/{player_id}`
**Descripción:** Eliminar un jugador del sistema  
**Tags:** `matchmaking`  
**Status:** `204 NO CONTENT`

**Path Parameters:**
- `player_id` (str): UUID del jugador

**Response:** Sin contenido

**Errores:**
- `404`: Jugador no encontrado
- `500`: Error al eliminar
- `501`: Servicio aún no implementado

---

### 7. `GET /api/matchmaking/stats`
**Descripción:** Obtener estadísticas del sistema  
**Tags:** `matchmaking`  
**Status:** `200 OK`

**Response:**
```json
{
  "total_players": 1000,
  "avg_elo": 1650,
  "total_matches": 5000,
  "avg_match_time": "15m",
  "success_rate": 0.85
}
```

**Errores:**
- `500`: Error obteniendo stats
- `501`: Servicio aún no implementado

---

## 🧪 Testing con cURL

### Health Check
```bash
curl http://localhost:8000/api/matchmaking/health
```

### Buscar Candidatos
```bash
curl -X POST http://localhost:8000/api/matchmaking/find_candidates \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "test-001",
    "categories": ["SEVENTH", "SIXTH"],
    "elo_range": [1400, 1800],
    "gender_preference": "MALE",
    "required_players": 3,
    "location": {
      "lat": -31.42647,
      "lon": -64.18722,
      "zone": "Nueva Córdoba"
    },
    "match_time": "19:00",
    "required_time": 90
  }'
```

### Seed Jugadores
```bash
curl -X POST http://localhost:8000/api/matchmaking/seed_players/100
```

---

## 📚 Documentación Interactiva

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

---

## 🔄 Estado de Implementación

| Endpoint | Controller | Service | Status |
|----------|-----------|---------|--------|
| `GET /health` | ✅ | ⏳ | Parcial |
| `POST /find_candidates` | ✅ | ⏳ | TODO |
| `POST /index_player` | ✅ | ⏳ | TODO |
| `POST /seed_players/{count}` | ✅ | ⏳ | TODO |
| `GET /players/{player_id}` | ✅ | ⏳ | TODO |
| `DELETE /players/{player_id}` | ✅ | ⏳ | TODO |
| `GET /stats` | ✅ | ⏳ | TODO |

**Leyenda:**
- ✅ Implementado
- ⏳ Pendiente
- 🔧 En progreso

---

## 📝 Notas de Implementación

### Servicios Necesarios

Para implementar estos endpoints necesitas crear:

1. **MatchmakingService** (`src/services/matchmaking_service.py`)
   - `find_candidates(request: MatchRequest) -> List[Candidate]`

2. **IndexingService** (`src/services/indexing_service.py`)
   - `index_player(player: Player) -> None`
   - `delete_player(player_id: str) -> None`

3. **SeedingService** (`src/services/seeding_service.py`)
   - `generate_players(count: int) -> List[Player]`
   - `seed_database(players: List[Player]) -> None`
   - `index_in_pinecone(players: List[Player]) -> None`

4. **PlayerService** (`src/services/player_service.py`)
   - `get_by_id(player_id: str) -> Player`

5. **StatsService** (`src/services/stats_service.py`)
   - `get_system_stats() -> dict`

---

## 🚀 Próximos Pasos

1. Implementar los servicios listados arriba
2. Conectar con OpenAI para embeddings
3. Configurar Pinecone para búsqueda vectorial
4. Conectar con PostgreSQL para métricas
5. Implementar seeding de datos
6. Testing end-to-end

---

**Todos los controllers están listos y esperando la implementación de los servicios!** 🎯

