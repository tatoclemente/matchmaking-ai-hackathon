from src.utils.time_utils import get_time_overlap_score

def test_time_overlap_score():
    player1 = {
        "availability": [
            {"min": "18:00", "max": "20:00"},
            {"min": "21:00", "max": "22:00"}
        ]
    }

    player2 = {
        "availability": [
            {"min": "19:00", "max": "21:30"}
        ]
    }

    required_time = 90  # minutos
    score = get_time_overlap_score(player1["availability"], player2["availability"], required_time)
    print("Overlap score:", score)


if __name__ == "__main__":
    test_time_overlap_score()
