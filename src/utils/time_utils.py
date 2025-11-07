from datetime import datetime
from typing import List, Dict

def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M")


def has_partial_overlap(slot_a: Dict[str, str], slot_b: Dict[str, str]) -> bool:
    """Verifica si dos slots tienen algún solapamiento."""
    start_a, end_a = parse_time(slot_a["min"]), parse_time(slot_a["max"])
    start_b, end_b = parse_time(slot_b["min"]), parse_time(slot_b["max"])
    return not (end_a <= start_b or end_b <= start_a)


def calculate_overlap_minutes(slot_a: Dict[str, str], slot_b: Dict[str, str]) -> float:
    """Devuelve cuántos minutos de solapamiento hay entre dos slots."""
    start_a, end_a = parse_time(slot_a["min"]), parse_time(slot_a["max"])
    start_b, end_b = parse_time(slot_b["min"]), parse_time(slot_b["max"])

    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)

    overlap = (overlap_end - overlap_start).total_seconds() / 60
    return max(0, overlap)


def get_time_overlap_score(
    avail_a: List[Dict[str, str]], 
    avail_b: List[Dict[str, str]], 
    required_time: int = 90
) -> float:
    """
    Calcula la puntuación de solapamiento de tiempo entre dos jugadores.
    
    Retorna:
    - 1.0 → disponibilidad perfecta (≥90 min)
    - 0.8–0.99 → buena compatibilidad
    - <0.8 → difícil coincidir
    - 0.5 → si alguno no tiene horarios cargados
    """
    if not avail_a or not avail_b:
        return 0.5

    best_overlap = 0.0

    for slot_a in avail_a:
        for slot_b in avail_b:
            if has_partial_overlap(slot_a, slot_b):
                overlap_minutes = calculate_overlap_minutes(slot_a, slot_b)
                ratio = overlap_minutes / required_time
                best_overlap = max(best_overlap, min(ratio, 1.0))

    return round(best_overlap, 3)


def check_time_availability(player_availability: List[Dict], match_time: str, required_minutes: int) -> float:
    """Verificar disponibilidad horaria del jugador para el partido"""
    if not player_availability:
        return 0.5
    
    match_slot = {"min": match_time, "max": parse_time(match_time).strftime("%H:%M")}
    return get_time_overlap_score([match_slot], player_availability, required_minutes)
