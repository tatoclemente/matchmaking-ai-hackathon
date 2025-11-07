# Archivo vacío para que Python reconozca como paquete
from typing import List, Dict, Any
from src.infrastructure.services.openai_service import OpenAIService
from src.infrastructure.services.pinecone_service import PineconeService
from src.services.scoring_service import ScoringService

class MatchmakingService:
    def __init__(self, openai_service: OpenAIService, pinecone_service: PineconeService, scoring_service: ScoringService, player_repository=None):
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
        self.scoring_service = scoring_service
        self.player_repository = player_repository
        
        if self.player_repository is None:
            from src.services.player_repository import PlayerRepository
            self.player_repository = PlayerRepository()
    
    def _build_request_description(self, request: Dict[str, Any]) -> str:
        """Construir texto descriptivo del partido para embedding"""
        parts = []
        
        if request.get('location', {}).get('zone'):
            parts.append(f"Partido en {request['location']['zone']}")
        
        if request.get('elo_range'):
            parts.append(f"ELO entre {request['elo_range'][0]} y {request['elo_range'][1]}")
        
        if request.get('match_time'):
            parts.append(f"Horario {request['match_time']}")
        
        if request.get('categories'):
            cats = ', '.join(request['categories'])
            parts.append(f"Categorías: {cats}")
        
        if request.get('preferred_position'):
            parts.append(f"Posición preferida: {request['preferred_position']}")
        
        if request.get('gender_preference'):
            parts.append(f"Género: {request['gender_preference']}")
        
        return ". ".join(parts) if parts else "Partido de pádel"
    
    async def find_candidates(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Pipeline completo de matchmaking:
        1. Crear embedding del request
        2. Buscar similares en Pinecone (top 50)
        3. Calcular scoring con ScoringService
        4. Ordenar y retornar top 20
        """
        # 1. Crear embedding del request
        request_text = self._build_request_description(request)
        embedding_response = self.openai_service.generate_embedding(request_text)
        request_embedding = embedding_response.embedding
        
        # 2. Buscar en Pinecone
        filters = {}
        if request.get('min_elo') and request.get('max_elo'):
            filters['elo'] = {'$gte': request['min_elo'], '$lte': request['max_elo']}
        
        search_result = self.pinecone_service.search(
            vector=request_embedding,
            top_k=50,
            filters=filters if filters else None
        )
        
        # 3. Enriquecer con datos de base de datos
        player_ids = [match['id'] for match in search_result['matches']]
        db_players = self.player_repository.get_players_by_ids(player_ids)
        
        # 4. Calcular scoring para cada candidato
        candidates = []
        for match in search_result['matches']:
            player_id = match['id']
            db_data = db_players.get(player_id, {})
            
            # Combinar datos de Pinecone con datos de DB
            player_data = {
                'id': player_id,
                'elo': db_data.get('elo', match.get('metadata', {}).get('elo', 1500)),
                'location': db_data.get('location', {}),
                'positions': db_data.get('positions', []),
                'acceptance_rate': db_data.get('acceptance_rate', 0.5),
                'last_active_days': db_data.get('last_active_days', 30),
                'availability': db_data.get('availability', [])
            }
            
            score_result = self.scoring_service.calculate_match_score(
                player=player_data,
                request=request,
                vector_similarity=match['score']
            )
            
            candidates.append({
                'player_id': match['id'],
                'score': score_result['total'],
                'distance_km': score_result['distance_km'],
                'reasons': score_result['reasons'],
                'metadata': match.get('metadata', {})
            })
        
        # 5. Ordenar por score y retornar top 20
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:20]
