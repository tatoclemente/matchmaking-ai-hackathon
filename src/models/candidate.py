from typing import List, Literal
from pydantic import BaseModel


class Candidate(BaseModel):
    player_id: str
    player_name: str
    score: float                         # 0.0-1.0
    distance_km: float                   # Distancia en km
    elo: int
    elo_diff: int                        # Diferencia absoluta
    acceptance_rate: float               # 0.0-1.0
    reasons: List[str]                   # Razones de compatibilidad
    invitation_message: str              # Mensaje personalizado para invitación
    compatibility_summary: str           # Resumen de compatibilidad
    gender: Literal["MALE", "FEMALE"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "a1b2c3d4-...",
                "player_name": "Juan Pérez",
                "score": 0.87,
                "distance_km": 1.2,
                "elo": 1520,
                "elo_diff": 20,
                "acceptance_rate": 0.92,
                "reasons": ["Perfil muy compatible", "Nivel muy similar"],
                "invitation_message": "Partido muy compatible en tu zona - 95% match",
                "compatibility_summary": "Nivel similar, cerca de tu ubicación"
            }
        }
