# Archivo vacío para que Python reconozca como paquete
from typing import Dict, Any

def adapt_router_request_to_scoring(router_request: Dict[str, Any]) -> Dict[str, Any]:
    """Adapta el formato del router al formato esperado por scoring_service"""
    adapted = {
        'match_id': router_request.get('match_id'),
        'elo_range': [
            router_request.get('min_elo', 0),
            router_request.get('max_elo', 3000)
        ],
        'location': {
            'lat': router_request.get('latitude', 0.0),
            'lon': router_request.get('longitude', 0.0),
            'zone': router_request.get('zone', '')
        },
        'match_time': router_request.get('time_slot', '18:00'),
        'required_time': router_request.get('duration', 90),
        'preferred_position': router_request.get('preferred_position'),
        'categories': router_request.get('categories', []),
        'gender_preference': router_request.get('gender_preference', 'MIXED')
    }
    
    # También agregar campos para matchmaking_service
    adapted['min_elo'] = adapted['elo_range'][0]
    adapted['max_elo'] = adapted['elo_range'][1]
    
    return adapted
