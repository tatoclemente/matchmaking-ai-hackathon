# 📚 Guía de Uso - Sistema de Excepciones

## 🎯 Arquitectura del Sistema

```
Request → Router → Service → raise AppException
                                      ↓
                            Exception Handler
                                      ↓
                            JSON Response Estandarizada
```

---

## 📦 Archivos del Sistema

```
src/
├── exceptions.py              # Excepciones custom
├── messages.py                # Mensajes centralizados
└── middleware/
    ├── __init__.py
    └── exception_handler.py   # Handler global
```

---

## 🔥 Cómo Usar las Excepciones

### 1. Import en tu servicio/router

```python
from src.exceptions import (
    PlayerNotFoundError,
    ValidationError,
    OpenAIRateLimitError,
    NoCandidatesFoundError
)
from src.messages import ErrorMessages, format_message
```

### 2. Lanzar excepciones en tu código

```python
# En un servicio
class PlayerService:
    def get_player(self, player_id: str) -> Player:
        player = db.query(Player).filter_by(id=player_id).first()
        
        if not player:
            # Lanzar excepción - el handler la capturará automáticamente
            raise PlayerNotFoundError(player_id=player_id)
        
        return player
```

### 3. Lanzar con mensajes custom

```python
# Usar mensajes del catálogo
from src.messages import ErrorMessages, format_message

if elo < 800 or elo > 3300:
    raise ValidationError(
        message=format_message(
            ErrorMessages.ELO_OUT_OF_RANGE,
            min=800,
            max=3300
        )
    )
```

---

## 📋 Catálogo de Excepciones

### ✅ Validación (400)

```python
from src.exceptions import ValidationError, InvalidInputError, MissingFieldError

# Validación genérica
raise ValidationError(message="El campo edad es inválido")

# Input inválido
raise InvalidInputError(message="UUID malformado", field="player_id")

# Campo faltante
raise MissingFieldError(field="elo")
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Campo requerido faltante: elo",
    "status_code": 400,
    "details": {
      "field": "elo"
    },
    "path": "/api/matchmaking/find_candidates"
  }
}
```

---

### 🔍 Not Found (404)

```python
from src.exceptions import PlayerNotFoundError, NoCandidatesFoundError

# Jugador no encontrado
raise PlayerNotFoundError(player_id="abc-123")

# No hay candidatos
raise NoCandidatesFoundError(match_id="match-456")
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Jugador no encontrado",
    "status_code": 404,
    "details": {
      "resource_type": "Player",
      "resource_id": "abc-123"
    },
    "path": "/api/matchmaking/players/abc-123"
  }
}
```

---

### 🔌 Servicios Externos (502, 503)

```python
from src.exceptions import OpenAIError, OpenAIRateLimitError, DatabaseError

# Error de OpenAI
raise OpenAIError(message="API key inválida")

# Rate limit
raise OpenAIRateLimitError(retry_after=60)

# Error de base de datos
raise DatabaseError(message="Timeout en query")
```

**Response (Rate Limit):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Error en servicio OpenAI: Rate limit excedido. Reintentar en 60 segundos",
    "status_code": 429,
    "details": {
      "service": "OpenAI",
      "retry_after": 60
    },
    "path": "/api/matchmaking/find_candidates"
  }
}
```

---

### 💼 Lógica de Negocio (409, 422)

```python
from src.exceptions import (
    InsufficientPlayersError,
    PlayerAlreadyIndexedError,
    InvalidEloRangeError
)

# Jugadores insuficientes
raise InsufficientPlayersError(required=3, available=1)

# Jugador duplicado
raise PlayerAlreadyIndexedError(player_id="player-123")

# Rango inválido
raise InvalidEloRangeError(min_elo=2000, max_elo=1500)
```

---

### 🔐 Autenticación (401, 403)

```python
from src.exceptions import AuthenticationError, InvalidAPIKeyError

# No autenticado
raise AuthenticationError(message="Token expirado")

# API Key inválida
raise InvalidAPIKeyError()
```

---

### 💥 Errores Internos (500)

```python
from src.exceptions import InternalError, ConfigurationError

# Error interno genérico
raise InternalError(message="Error inesperado en procesamiento")

# Configuración faltante
raise ConfigurationError(config_key="OPENAI_API_KEY")
```

---

## 🎨 Estructura de Response

### Response Exitosa
```json
{
  "success": true,
  "data": {
    "candidates": [...],
    "total_found": 10
  }
}
```

### Response de Error (Estandarizada)
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",           // Código único del error
    "message": "Mensaje descriptivo", // Mensaje legible
    "status_code": 400,               // HTTP status code
    "details": {                      // Detalles opcionales
      "field": "elo",
      "min": 800,
      "max": 3300
    },
    "path": "/api/endpoint"           // Path del request
  }
}
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Servicio de Matchmaking

```python
from src.exceptions import NoCandidatesFoundError, OpenAIError
from src.messages import ErrorMessages

class MatchmakingService:
    async def find_candidates(self, request: MatchRequest):
        try:
            # Crear embedding
            embedding = await self.openai_client.create_embedding(request)
        except Exception as e:
            # Convertir error genérico en excepción específica
            raise OpenAIError(message=str(e))
        
        # Buscar candidatos
        candidates = await self.pinecone.search(embedding)
        
        if not candidates:
            # Lanzar excepción específica
            raise NoCandidatesFoundError(match_id=request.match_id)
        
        return candidates
```

### Ejemplo 2: Validación en Router

```python
from fastapi import APIRouter
from src.exceptions import InvalidRangeError
from src.messages import ValidationMessages

router = APIRouter()

@router.post("/find_candidates")
async def find_candidates(request: MatchRequest):
    # Validación custom
    min_elo, max_elo = request.elo_range
    
    if min_elo >= max_elo:
        raise InvalidRangeError(
            field="elo_range",
            min_val=800,
            max_val=3300,
            current_val=f"[{min_elo}, {max_elo}]"
        )
    
    # El handler capturará cualquier excepción automáticamente
    candidates = await matchmaking_service.find_candidates(request)
    
    return {"success": True, "data": candidates}
```

### Ejemplo 3: Usar Mensajes Centralizados

```python
from src.messages import ErrorMessages, SuccessMessages, format_message

# En un servicio
class PlayerService:
    def index_player(self, player: Player):
        # Verificar si ya existe
        if self.player_exists(player.id):
            raise PlayerAlreadyIndexedError(player_id=player.id)
        
        # Indexar
        self.pinecone.upsert(player)
        
        # Retornar mensaje de éxito
        return {
            "message": format_message(
                SuccessMessages.PLAYER_INDEXED,
                player_id=player.id
            )
        }
```

---

## 🔧 Logging Automático

El exception handler **automáticamente logea** todos los errores:

```python
# Logs generados automáticamente:
# ERROR: AppException: PLAYER_NOT_FOUND - Jugador no encontrado
#   Extra: {
#     "error_code": "NOT_FOUND",
#     "status_code": 404,
#     "details": {"resource_type": "Player", "resource_id": "abc-123"},
#     "path": "/api/matchmaking/players/abc-123"
#   }
```

---

## ⚙️ Configuración

### Nivel de Logging

En desarrollo, los errores 500 incluyen traceback completo:

```python
# En development (DEBUG)
{
  "error": {
    "details": {
      "exception_type": "ValueError",
      "exception_message": "invalid literal for int()",
      "traceback": "Traceback (most recent call last):\n..."
    }
  }
}

# En production (INFO/WARNING)
{
  "error": {
    "message": "Error interno del servidor",
    "details": {}  // Sin información sensible
  }
}
```

---

## ✅ Checklist de Uso

### Al crear un nuevo servicio:

- [ ] Importar excepciones relevantes de `src.exceptions`
- [ ] Importar mensajes de `src.messages`
- [ ] Lanzar excepciones específicas (no genéricas)
- [ ] Incluir detalles útiles en las excepciones
- [ ] Usar `format_message()` para mensajes con variables
- [ ] NO hacer try-except innecesarios (el handler los captura)

### Al crear un nuevo error:

- [ ] Agregar excepción en `src/exceptions.py`
- [ ] Agregar mensajes en `src/messages.py`
- [ ] Heredar de la clase base correcta
- [ ] Definir `status_code` y `error_code` apropiados
- [ ] Incluir detalles útiles en el constructor

---

## 🚀 Ventajas del Sistema

1. ✅ **Respuestas consistentes** - Todas las respuestas de error tienen la misma estructura
2. ✅ **Logging automático** - No necesitas escribir logs manualmente
3. ✅ **Mensajes centralizados** - Fácil mantener y traducir mensajes
4. ✅ **Type-safe** - Todas las excepciones están tipadas
5. ✅ **Fácil debugging** - Detalles completos en development
6. ✅ **Seguro en producción** - No expone información sensible

---

**¡El sistema de excepciones está listo para usar!** 🎉

