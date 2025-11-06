# 🤖 INSTRUCCIONES PARA AGENTES DE IA

Este documento proporciona instrucciones específicas para agentes de IA que construirán el microservicio de matchmaking.

---

## 📋 Contexto General

Estás construyendo un **microservicio de matchmaking con IA** para PADER (plataforma de pádel). El sistema usa:
- **OpenAI embeddings** para capturar similitud semántica entre jugadores
- **Pinecone** para búsqueda vectorial eficiente
- **PostgreSQL** para datos estructurados
- **FastAPI** como framework web

---

## 🎯 Objetivo del Agente

Implementar componentes específicos del microservicio siguiendo las especificaciones exactas de los documentos de referencia.

---

## 📚 Documentos de Referencia (Orden de Lectura)

1. **PRODUCT-CONTEXT.md** → Entender el problema de negocio
2. **TECHNICAL-SPECS.md** → Especificaciones técnicas detalladas
3. **PLAN.md** → Código de ejemplo y estructura
4. **SETUP-BASE.md** → Configuración del entorno

---

## 🔧 Tareas por Componente

### TEAM 1: Models (Pydantic)

**Archivos a crear:**
- `src/models/player.py`
- `src/models/match_request.py`
- `src/models/candidate.py`

**Referencia:** TECHNICAL-SPECS.md → Sección "Modelos de Datos Detallados"

**Requisitos clave:**
- Usar Pydantic BaseModel
- Incluir validaciones de tipos
- Usar Enums para categorías, género, posiciones
- Incluir ejemplos en Config.json_schema_extra
- Todos los campos según especificación exacta

**Validaciones importantes:**
- `elo`: 800-3300+
- `age`: 18-60
- `acceptance_rate`: 0.0-1.0
- `category`: Enum con valores en inglés (NINTH, EIGHTH, etc.)
- `positions`: Lista de FOREHAND/BACKHAND

---

### TEAM 2: External Services

**Archivos a crear:**
- `src/external/openai_client.py`
- `src/external/pinecone_client.py`
- `src/database/db_client.py`
- `src/external/config.py`

**Referencia:** 
- TECHNICAL-SPECS.md → Sección "Algoritmo de Embeddings"
- PLAN.md → Team 2

**Requisitos clave:**

#### OpenAI Client:
- Usar modelo `text-embedding-3-small`
- Método `create_player_embedding(player: Player) -> List[float]`
- Método `create_request_embedding(request: MatchRequest) -> List[float]`
- Construir texto descriptivo según especificación
- Retornar vector de 1536 dimensiones

#### Pinecone Client:
- Método `upsert_player(player_id, embedding, metadata)`
- Método `search_similar(query_embedding, filters, top_k)`
- Método `delete_player(player_id)`
- Usar filtros metadata para optimizar búsqueda

#### Database Client:
- Conexión a PostgreSQL con psycopg2
- Método `get_player_metrics(player_id)` → acceptance_rate, last_active_days
- Método `get_all_players()` para indexación masiva
- Manejo de errores y conexiones

---

### TEAM 3: Matchmaking & Scoring

**Archivos a crear:**
- `src/services/matchmaking_service.py`
- `src/services/scoring_service.py`
- `src/utils/geo_utils.py`
- `src/utils/time_utils.py`

**Referencia:** TECHNICAL-SPECS.md → Sección "Algoritmo de Scoring Detallado"

**Requisitos clave:**

#### MatchmakingService:
Pipeline de 6 pasos:
1. Crear embedding del request
2. Buscar similares en Pinecone (top 50)
3. Aplicar filtros obligatorios (ELO range, edad)
4. Enriquecer con datos de DB
5. Calcular scoring final
6. Ordenar y retornar top N

#### ScoringService:
Algoritmo multi-dimensional con pesos exactos:
- Vector similarity: 40%
- ELO compatibility: 20%
- Geographic distance: 15%
- Time availability: 10%
- Acceptance rate: 10%
- Activity frequency: 5%
- Position bonus: ±5% (si aplica)

**Fórmulas exactas en TECHNICAL-SPECS.md**

#### Utilities:
- `haversine_distance()`: Calcular distancia en km
- `check_time_availability()`: Verificar overlap de horarios

---

### TEAM 4: API & Seeders

**Archivos a crear:**
- `src/routers/matchmaking.py`
- `src/seeders/player_seeder.py`
- `src/seeders/db_seeder.py`
- `src/main.py`

**Referencia:** PLAN.md → Team 4

**Requisitos clave:**

#### Endpoints:
- `POST /api/matchmaking/find_candidates` → Retorna List[Candidate]
- `POST /api/matchmaking/index_player` → Indexa jugador en Pinecone
- `POST /api/matchmaking/seed_players/{count}` → Genera N jugadores mock
- `GET /api/matchmaking/health` → Status del servicio

#### PlayerSeeder:
- Distribución realista de categorías (ver PLAN.md)
- Zonas de Córdoba con coordenadas reales
- Patrones de disponibilidad variados
- Correlación entre actividad y acceptance_rate
- Método `generate_realistic_players(count: int) -> List[Player]`

#### DBSeeder:
- Inserción en PostgreSQL
- Manejo de conflictos (ON CONFLICT)
- Método `insert_players(players: List[Player])`

---

## ⚠️ Reglas Críticas para el Agente

### 1. Seguir Especificaciones Exactas
- NO inventar campos adicionales
- NO cambiar nombres de métodos
- NO modificar pesos del scoring
- Usar tipos exactos según Pydantic models

### 2. Manejo de Errores
```python
# Siempre usar try-except en servicios
try:
    result = external_service.call()
except SpecificError as e:
    raise CustomError(f"Context: {str(e)}")
```

### 3. Validaciones
- Validar inputs con Pydantic
- Verificar rangos (ELO, edad, acceptance_rate)
- Manejar casos None/Optional

### 4. Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing request: {request.match_id}")
logger.error(f"Error in service: {str(e)}")
```

### 5. Type Hints
```python
# SIEMPRE usar type hints
def calculate_score(player: dict, request: MatchRequest) -> dict:
    ...
```

---

## 🧪 Testing

### Unit Tests Requeridos
```python
# test_scoring_service.py
def test_calculate_elo_score():
    # Verificar que score está en rango correcto
    assert 0.0 <= score <= 0.2

def test_calculate_distance_score():
    # Verificar fórmula de distancia
    assert score decreases with distance

# test_geo_utils.py
def test_haversine_distance():
    # Verificar cálculo correcto
    assert 1.0 <= distance <= 2.0
```

### Integration Tests
```python
# test_matchmaking_integration.py
async def test_find_candidates_e2e():
    # Test completo del pipeline
    response = await client.post("/api/matchmaking/find_candidates", ...)
    assert response.status_code == 200
    assert len(response.json()["candidates"]) > 0
```

---

## 📊 Datos de Ejemplo

### Player Mock
```python
{
    "id": "uuid-here",
    "name": "Juan Pérez",
    "elo": 1520,
    "age": 28,
    "gender": "MALE",
    "category": "SEVENTH",
    "positions": ["FOREHAND", "BACKHAND"],
    "location": {"lat": -31.42647, "lon": -64.18722, "zone": "Nueva Córdoba"},
    "availability": [{"min": "18:00", "max": "22:00"}],
    "acceptance_rate": 0.85,
    "last_active_days": 2
}
```

### MatchRequest Mock
```python
{
    "match_id": "match-uuid",
    "categories": ["SEVENTH", "SIXTH"],
    "elo_range": [1400, 1800],
    "age_range": [25, 35],
    "gender_preference": "MALE",
    "required_players": 3,
    "location": {"lat": -31.42647, "lon": -64.18722, "zone": "Nueva Córdoba"},
    "match_time": "19:00",
    "required_time": 90,
    "preferred_position": "BACKHAND"
}
```

---

## 🔍 Verificación de Implementación

### Checklist por Componente

#### Models ✅
- [ ] Todos los campos según especificación
- [ ] Enums definidos correctamente
- [ ] Validaciones de rangos
- [ ] Type hints completos
- [ ] Ejemplos en Config

#### External Services ✅
- [ ] OpenAI retorna 1536 dimensiones
- [ ] Pinecone usa filtros metadata
- [ ] Database maneja errores
- [ ] Config valida env vars

#### Matchmaking & Scoring ✅
- [ ] Pipeline de 6 pasos implementado
- [ ] Pesos exactos del scoring (40%, 20%, 15%, 10%, 10%, 5%)
- [ ] Fórmulas matemáticas correctas
- [ ] Manejo de casos edge (sin availability, etc.)

#### API & Seeders ✅
- [ ] Todos los endpoints funcionan
- [ ] Seeders generan datos realistas
- [ ] Distribución de categorías correcta
- [ ] CORS configurado

---

## 🚀 Orden de Implementación Recomendado

### Fase 1: Base (30 min)
1. Models (Player, MatchRequest, Candidate)
2. Config y env vars
3. Main.py con FastAPI básica

### Fase 2: External (1h)
1. Database client
2. OpenAI client
3. Pinecone client

### Fase 3: Business Logic (2h)
1. Geo y time utils
2. Scoring service
3. Matchmaking service

### Fase 4: API & Data (1h)
1. Routers
2. Seeders
3. Integration

### Fase 5: Testing (30 min)
1. Unit tests
2. Integration tests
3. Verificación end-to-end

---

## 💡 Tips para el Agente

### Cuando implementes embeddings:
```python
# Construir texto descriptivo rico
text = f"Jugador de pádel categoría {player.category}, "
text += f"ELO {player.elo}, "
text += f"Edad {player.age} años, "
# ... más contexto según TECHNICAL-SPECS.md
```

### Cuando implementes scoring:
```python
# Usar las fórmulas exactas
elo_score = max(0, 1 - elo_diff / elo_tolerance) * 0.20
distance_score = (1 / (1 + distance_km / 10)) * 0.15
# ... según TECHNICAL-SPECS.md
```

### Cuando implementes seeders:
```python
# Usar distribución realista
category = random.choices(
    list(CATEGORY_DISTRIBUTION.keys()),
    weights=list(CATEGORY_DISTRIBUTION.values())
)[0]
```

---

## 🎯 Criterios de Éxito

### Funcional
- ✅ Todos los endpoints responden correctamente
- ✅ Embeddings se generan sin errores
- ✅ Scoring retorna valores 0.0-1.0
- ✅ Seeders generan 1000+ jugadores

### Performance
- ✅ Latencia < 200ms para find_candidates
- ✅ Sin memory leaks
- ✅ Manejo correcto de errores

### Calidad
- ✅ Type hints en todo el código
- ✅ Docstrings en funciones públicas
- ✅ Tests pasan al 100%
- ✅ Código sigue PEP 8

---

## 📞 Cuando Tengas Dudas

1. **Especificación técnica:** Consultar TECHNICAL-SPECS.md
2. **Código de ejemplo:** Consultar PLAN.md
3. **Contexto de negocio:** Consultar PRODUCT-CONTEXT.md
4. **Setup:** Consultar SETUP-BASE.md

---

## ⚡ Comando Rápido de Verificación

```bash
# Verificar que todo funciona
docker-compose up --build
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/matchmaking/seed_players/100
curl -X POST http://localhost:8000/api/matchmaking/find_candidates \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

**Este documento es tu guía completa. Sigue las especificaciones al pie de la letra y tendrás un microservicio funcional y profesional.** 🚀
