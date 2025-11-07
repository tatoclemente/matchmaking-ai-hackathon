# Archivo vacío para que Python reconozca como paquete
from typing import Dict, List
from src.utils.geo_utils import haversine_distance
from src.utils.time_utils import check_time_availability

class ScoringService:
    def calculate_match_score(self, player: Dict, request: Dict, vector_similarity: float) -> Dict:
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
        elo_center = sum(request['elo_range']) / 2
        elo_diff = abs(player['elo'] - elo_center)
        elo_tolerance = (request['elo_range'][1] - request['elo_range'][0]) / 2
        scores['elo'] = max(0, 1 - elo_diff / elo_tolerance) * 0.2
        if elo_diff < 100:
            reasons.append("Nivel muy similar")
        
        # 3. Distancia geográfica (15%)
        try:
            player_loc = player.get('location', {})
            request_loc = request.get('location', {})
            distance = haversine_distance(
                player_loc.get('lat', 0.0), player_loc.get('lon', 0.0),
                request_loc.get('lat', 0.0), request_loc.get('lon', 0.0)
            )
        except Exception as e:
            print(f"Error calculando distancia: {e}")
            print(f"Player location: {player.get('location')}")
            print(f"Request location: {request.get('location')}")
            raise
        scores['distance'] = (1 / (1 + distance / 10)) * 0.15
        if distance < 3:
            reasons.append("Muy cerca del partido")
        
        # 4. Disponibilidad horaria (10%)
        time_score = check_time_availability(
            player.get('availability', []),
            request.get('match_time', '18:00'),
            request.get('required_time', 90)
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
        activity_score = max(0, 1 - last_active / 30)
        scores['activity'] = activity_score * 0.05
        if last_active < 3:
            reasons.append("Usuario muy activo")
        
        # 7. Posición preferida (bonus si aplica)
        if request.get('preferred_position'):
            if request['preferred_position'] in player.get('positions', []):
                scores['position_bonus'] = 0.05
                position_text = "drive" if request['preferred_position'] == "FOREHAND" else "revés"
                reasons.append(f"Juega de {position_text}")
            else:
                scores['position_bonus'] = -0.05
        
        total = sum(scores.values())
        
        return {
            'total': round(total, 3),
            'breakdown': scores,
            'reasons': reasons,
            'distance_km': round(distance, 2)
        }
    
    def generate_invitation_message(self, score: float, distance_km: float, request: Dict, organizer_name: str, organizer_gender: str) -> str:
        """Generar mensaje personalizado para invitación"""
        gender_text = "jugador" if organizer_gender == "MALE" else "jugadora"
        
        if score > 0.85:
            if distance_km < 3:
                return f"🎾 {organizer_name} te invita a jugar - Nivel similar, a {distance_km:.1f}km"
            return f"🎾 {organizer_name} organiza un partido de tu nivel y tu zona"
        
        elif score > 0.70:
            return f"🎾 {organizer_name} organiza partido en {request['location']['zone']} - {distance_km:.1f}km"
        
        else:
            return f"{organizer_name} busca {gender_text} - {request['location']['zone']} {request['match_time']}hs"
