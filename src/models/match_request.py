from typing import List, Optional, TypedDict, Tuple
from pydantic import BaseModel
from enum import Enum

class CategoryEnum(str, Enum):
    NINTH = "NINTH"
    EIGHTH = "EIGHTH"
    SEVENTH = "SEVENTH"
    SIXTH = "SIXTH"
    FIFTH = "FIFTH"
    FOURTH = "FOURTH"
    THIRD = "THIRD"
    SECOND = "SECOND"
    FIRST = "FIRST"

class GenderPreference(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    MIXED = "MIXED"

class LocationDict(TypedDict):
    lat: float      # -90 to 90
    lon: float      # -180 to 180
    zone: str       # Nombre de la zona

class PositionEnum(str, Enum):
    FOREHAND = "FOREHAND"
    BACKHAND = "BACKHAND"


class MatchRequest(BaseModel):
    match_id: str                        # UUID del partido
    categories: List[CategoryEnum]       # Categorías aceptadas
    elo_range: Tuple[int, int]          # (min, max)
    age_range: Optional[Tuple[int, int]] = None
    gender_preference: GenderPreference  # MALE, FEMALE, MIXED
    required_players: int                # 1-3
    location: LocationDict               # Ubicación del partido
    match_time: str                      # "HH:MM"
    required_time: int                   # Minutos (60-180)
    preferred_position: Optional[PositionEnum] = None