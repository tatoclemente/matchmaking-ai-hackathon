"""
Script de prueba para el sistema de excepciones.

Ejecutar: python -m src.test_exceptions
"""

from src.exceptions import (
    PlayerNotFoundError,
    ValidationError,
    OpenAIRateLimitError,
    NoCandidatesFoundError,
    InvalidEloRangeError,
    DatabaseConnectionError
)
from src.messages import ErrorMessages, SuccessMessages, format_message


def test_exceptions():
    """Probar que las excepciones se crean correctamente"""
    
    print("🧪 Testing Exception System\n")
    
    # Test 1: PlayerNotFoundError
    print("1️⃣ PlayerNotFoundError")
    try:
        raise PlayerNotFoundError(player_id="test-123")
    except PlayerNotFoundError as e:
        print(f"   ✅ Code: {e.error_code}")
        print(f"   ✅ Status: {e.status_code}")
        print(f"   ✅ Message: {e.message}")
        print(f"   ✅ Details: {e.details}\n")
    
    # Test 2: ValidationError
    print("2️⃣ ValidationError")
    try:
        raise ValidationError(
            message="ELO inválido",
            details={"field": "elo", "value": 9999}
        )
    except ValidationError as e:
        print(f"   ✅ Code: {e.error_code}")
        print(f"   ✅ Status: {e.status_code}")
        print(f"   ✅ Message: {e.message}")
        print(f"   ✅ Details: {e.details}\n")
    
    # Test 3: OpenAIRateLimitError
    print("3️⃣ OpenAIRateLimitError")
    try:
        raise OpenAIRateLimitError(retry_after=60)
    except OpenAIRateLimitError as e:
        print(f"   ✅ Code: {e.error_code}")
        print(f"   ✅ Status: {e.status_code}")
        print(f"   ✅ Message: {e.message}")
        print(f"   ✅ Details: {e.details}\n")
    
    # Test 4: Format Messages
    print("4️⃣ Format Messages")
    msg = format_message(
        ErrorMessages.PLAYER_NOT_FOUND,
        player_id="abc-456"
    )
    print(f"   ✅ Formatted: {msg}\n")
    
    msg2 = format_message(
        SuccessMessages.PLAYERS_SEEDED,
        count=100
    )
    print(f"   ✅ Formatted: {msg2}\n")
    
    # Test 5: Hierarchy
    print("5️⃣ Exception Hierarchy")
    try:
        raise InvalidEloRangeError(min_elo=2000, max_elo=1500)
    except ValidationError as e:  # Catch por clase padre
        print(f"   ✅ Caught by parent class: ValidationError")
        print(f"   ✅ Actual type: {type(e).__name__}")
        print(f"   ✅ Message: {e.message}\n")
    
    # Test 6: Database Error
    print("6️⃣ DatabaseConnectionError")
    try:
        raise DatabaseConnectionError()
    except DatabaseConnectionError as e:
        print(f"   ✅ Code: {e.error_code}")
        print(f"   ✅ Status: {e.status_code}")
        print(f"   ✅ Message: {e.message}\n")
    
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_exceptions()

