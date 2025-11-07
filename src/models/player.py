from typing import List, Optional, Literal, TypedDict
from pydantic import BaseModel
from enum import Enum

class LocationDict(TypedDict):
    lat: float      # -90 to 90
    lon: float      # -180 to 180
    zone: str       # Nombre de la zona

class TimeSlot(BaseModel):
    min: str        # "HH:MM" formato 24h
    max: str        # "HH:MM" formato 24h

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

class PositionEnum(str, Enum):
    FOREHAND = "FOREHAND"
    BACKHAND = "BACKHAND"


class Player(BaseModel):
    id: str                              # UUID
    name: str                            # Nombre completo
    elo: int                             # 800-3300+
    age: int                             # 18-60
    gender: Literal["MALE", "FEMALE"]    # Género
    category: CategoryEnum               # NINTH...FIRST
    positions: List[PositionEnum]        # [FOREHAND, BACKHAND]
    location: LocationDict               # {lat, lon, zone}
    availability: Optional[List[TimeSlot]] = None
    acceptance_rate: float               # 0.0-1.0
    last_active_days: int                # 0-999

