"""
Test de integración completa del flujo de matchmaking
"""
from src.services.matchmaking_service import MatchmakingService
from src.services.scoring_service import ScoringService
from src.services.request_adapter import adapt_router_request_to_scoring

# Mock de servicios externos
class MockOpenAIService:
    def generate_embedding(self, text: str):
        # Retornar embedding fake de 1536 dimensiones
        class EmbeddingResponse:
            embedding = [0.1] * 1536
            model = "text-embedding-3-small"
            dimensions = 1536
        return EmbeddingResponse()

class MockPineconeService:
    def search(self, vector, top_k=50, filters=None):
        # Retornar 3 candidatos mock
        return {
            'matches': [
                {
                    'id': 'player_1',
                    'score': 0.89,
                    'metadata': {
                        'name': 'Juan Pérez',
                        'elo': 1520,
                        'location': {'lat': -31.4201, 'lon': -64.1888, 'zone': 'Nueva Córdoba'},
                        'positions': ['FOREHAND', 'BACKHAND'],
                        'acceptance_rate': 0.85,
                        'last_active_days': 2,
                        'availability': [{'min': '18:00', 'max': '22:00'}]
                    }
                },
                {
                    'id': 'player_2',
                    'score': 0.82,
                    'metadata': {
                        'name': 'María González',
                        'elo': 1480,
                        'location': {'lat': -31.4250, 'lon': -64.1900, 'zone': 'Centro'},
                        'positions': ['BACKHAND'],
                        'acceptance_rate': 0.78,
                        'last_active_days': 5,
                        'availability': [{'min': '19:00', 'max': '21:00'}]
                    }
                },
                {
                    'id': 'player_3',
                    'score': 0.75,
                    'metadata': {
                        'name': 'Carlos Rodríguez',
                        'elo': 1550,
                        'location': {'lat': -31.4100, 'lon': -64.1800, 'zone': 'Cerro'},
                        'positions': ['FOREHAND'],
                        'acceptance_rate': 0.92,
                        'last_active_days': 1,
                        'availability': [{'min': '17:00', 'max': '23:00'}]
                    }
                }
            ],
            'count': 3
        }

async def test_matchmaking_integration():
    """Test completo del flujo de matchmaking"""
    
    # 1. Request del router (formato API)
    router_request = {
        'match_id': 'test-123',
        'required_players': 2,
        'min_elo': 1400,
        'max_elo': 1600,
        'zone': 'Nueva Córdoba',
        'latitude': -31.4201,
        'longitude': -64.1888,
        'time_slot': '19:00',
        'duration': 90,
        'categories': ['SEVENTH', 'SIXTH'],
        'gender_preference': 'MIXED',
        'preferred_position': 'FOREHAND'
    }
    
    print("=" * 70)
    print("TEST INTEGRACIÓN MATCHMAKING")
    print("=" * 70)
    print(f"\n📥 Request recibido:")
    print(f"   Match ID: {router_request['match_id']}")
    print(f"   ELO Range: {router_request['min_elo']}-{router_request['max_elo']}")
    print(f"   Zona: {router_request['zone']}")
    print(f"   Horario: {router_request['time_slot']}")
    
    # 2. Adaptar request
    adapted_request = adapt_router_request_to_scoring(router_request)
    print(f"\n✅ Request adaptado al formato de scoring")
    
    # 3. Inicializar servicios (con mocks)
    openai_service = MockOpenAIService()
    pinecone_service = MockPineconeService()
    scoring_service = ScoringService()
    matchmaking_service = MatchmakingService(openai_service, pinecone_service, scoring_service)
    
    print(f"\n🔧 Servicios inicializados:")
    print(f"   - OpenAI Service (mock)")
    print(f"   - Pinecone Service (mock)")
    print(f"   - Scoring Service (real)")
    
    # 4. Ejecutar búsqueda
    print(f"\n🔍 Buscando candidatos...")
    candidates = await matchmaking_service.find_candidates(adapted_request)
    
    # 5. Validar resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   Total candidatos encontrados: {len(candidates)}")
    print(f"\n{'='*70}")
    
    assert len(candidates) > 0, "Debería encontrar al menos 1 candidato"
    assert len(candidates) <= 20, "No debería retornar más de 20 candidatos"
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n🎾 Candidato #{i}:")
        print(f"   Player ID: {candidate['player_id']}")
        print(f"   Score: {candidate['score']:.3f}")
        print(f"   Distancia: {candidate['distance_km']:.2f} km")
        print(f"   Razones:")
        for reason in candidate['reasons']:
            print(f"      ✓ {reason}")
        
        # Validaciones
        assert 0 <= candidate['score'] <= 1, f"Score debe estar entre 0 y 1, got {candidate['score']}"
        assert candidate['distance_km'] >= 0, "Distancia no puede ser negativa"
        assert len(candidate['reasons']) > 0, "Debe tener al menos una razón"
        assert 'metadata' in candidate, "Debe incluir metadata"
    
    # 6. Validar ordenamiento
    scores = [c['score'] for c in candidates]
    assert scores == sorted(scores, reverse=True), "Candidatos deben estar ordenados por score descendente"
    
    print(f"\n{'='*70}")
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 70)
    print(f"\n🎯 Flujo completo verificado:")
    print(f"   1. ✓ Request adaptado correctamente")
    print(f"   2. ✓ Embedding generado (mock)")
    print(f"   3. ✓ Búsqueda en Pinecone (mock)")
    print(f"   4. ✓ Scoring calculado (real)")
    print(f"   5. ✓ Candidatos ordenados por score")
    print(f"   6. ✓ Top {len(candidates)} retornados")
    print("=" * 70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_matchmaking_integration())
