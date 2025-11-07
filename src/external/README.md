# Arquitectura recomendada para `OpenAI` client (embeddings)

A continuación tienes una propuesta concreta y práctica para mejorar y organizar el cliente de OpenAI usado en este proyecto. Incluye la separación en capas, los contratos de datos y recomendaciones de librerías y mejoras (retries, cache, rate-limit, tests).

## Estructura por capas
- `src/external/` — Cliente de bajo nivel (wrapper del SDK): singleton, manejo de errores, timeouts y retries.
- `src/schemas/` — DTOs / validaciones (p. ej. Pydantic): `EmbeddingRequest`, `EmbeddingResponse`, `BatchRequest`, `ClientConfig`.
- `src/services/` — Lógica de negocio: validaciones, batching, deduplicación, composición de perfiles, caching y métricas.
- `src/utils/` — Utilidades transversales: `retry.py`, `cache.py`, `rate_limit.py`, `hashing.py`.

## Modelos de datos (contratos)
- `EmbeddingRequest`:
  - `text: str`
  - `model?: str = "text-embedding-3-small"`
- `EmbeddingResponse`:
  - `embedding: List[float]`
  - `model: str`
  - `dimensions: int`
- `BatchEmbeddingRequest`:
  - `texts: List[str]`
  - `model?: str`
- `ClientConfig`:
  - `api_key: str`
  - `timeout: int`
  - `max_retries: int`
  - `model: str`
  - `max_batch_size: int`

Ventajas: validación temprana, fácil serialización para cache, contratos claros para tests.

## Responsabilidades por capa
- External (client): únicamente llamadas al SDK/HTTP API, normaliza respuestas y mapea errores a excepciones del dominio. Implementa retries y timeouts.
- Services: validaciones (texto no vacío, límites de batch), orquestación de batches, caching (LRU/Redis), rate-limiting y metrics/logs.
- Schemas: validaciones y transformaciones ligeras.

## Recomendaciones técnicas
- Singleton con método de inicialización `get_instance(config=None)` para permitir inyección en tests.
- Retries exponenciales (10s timeout por request + tenacity o backoff). Reintentar en 429 y 5xx.
- Cache local LRU para evitar llamadas repetidas; Redis para multi-instances. Key = `sha256(model + text)`.
- Rate limiter (token-bucket o `aiolimiter` si async) para respetar límites del proveedor.
- Batching: soportar hasta `max_batch_size` (p. ej. 100). Si se envía más, dividir internamente.
- Manejo de errores: mapear a `OpenAIServiceError`, `OpenAIRateLimitError`, `OpenAITransientError`.

## Observabilidad y tests
- Instrumentar latencias, contadores de éxito/fracaso y número de retries.
- Tests unitarios: mockear `external` para testear `service` (happy path + errores). Integration tests opcionales con clave de test.

## Ejemplo de uso (firma sugerida)
- `client = OpenAIClient.get_instance(config)`
- `client.create_embedding(EmbeddingRequest(text="...")) -> EmbeddingResponse`
- `service.generate_embedding(text)` — llamará al client, aplicará caché y validaciones.

## Siguientes pasos sugeridos
1. Añadir `src/schemas/embedding.py` (Pydantic) y `src/utils/retry.py`.
2. Refactorizar `src/external/openai_client.py` para exponer `get_instance(config)` y normalizar respuestas.
3. Reescribir `src/services/openai_service.py` usando los contratos y agregando caching/rate-limit.
4. Escribir tests unitarios y de integración.

Si quieres, comienzo ahora mismo implementando el `schema` + `client.get_instance()` y un `service` básico; dime si prefieres depender de Pydantic/tenacity o solo stdlib.
