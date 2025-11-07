from src.services.scoring_service import ScoringService

# Mock data
player = {
    'id': 'test-123',
    'name': 'Juan Pérez',
    'elo': 1520,
    'age': 28,
    'gender': 'MALE',
    'category': 'SEVENTH',
    'positions': ['FOREHAND', 'BACKHAND'],
    'location': {'lat': -31.4201, 'lon': -64.1888, 'zone': 'Nueva Córdoba'},
    'availability': [
        {'min': '18:00', 'max': '22:00'}
    ],
    'acceptance_rate': 0.85,
    'last_active_days': 2
}

request = {
    'match_id': 'match-456',
    'categories': ['SEVENTH', 'SIXTH'],
    'elo_range': [1400, 1600],
    'location': {'lat': -31.4250, 'lon': -64.1900, 'zone': 'Centro'},
    'match_time': '19:00',
    'required_time': 90,
    'preferred_position': 'FOREHAND'
}

# Test scoring
service = ScoringService()
result = service.calculate_match_score(
    player=player,
    request=request,
    vector_similarity=0.87
)

print("=" * 60)
print("TEST SCORING SERVICE")
print("=" * 60)
print(f"\nJugador: {player['name']}")
print(f"ELO: {player['elo']}")
print(f"Acceptance Rate: {player['acceptance_rate']}")
print(f"Last Active: {player['last_active_days']} días")
print(f"\nVector Similarity: 0.87")
print(f"\n{'SCORE BREAKDOWN':^60}")
print("-" * 60)
for key, value in result['breakdown'].items():
    print(f"{key:20s}: {value:.3f}")
print("-" * 60)
print(f"{'TOTAL':20s}: {result['total']:.3f}")
print(f"\nDistancia: {result['distance_km']} km")
print(f"\nRazones de compatibilidad:")
for reason in result['reasons']:
    print(f"  ✓ {reason}")
print("=" * 60)

# Test invitation message
organizer_name = "María González"
organizer_gender = "FEMALE"

message = service.generate_invitation_message(
    score=result['total'],
    distance_km=result['distance_km'],
    request=request,
    organizer_name=organizer_name,
    organizer_gender=organizer_gender
)

print("\n" + "=" * 60)
print("MENSAJE DE INVITACIÓN")
print("=" * 60)
print(f"Organizador: {organizer_name} ({organizer_gender})")
print(f"\nMensaje: {message}")
print("=" * 60)
