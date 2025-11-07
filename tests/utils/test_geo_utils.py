from src.utils.geo_utils import haversine_distance
def test_haversine_distance():
    lat1, lon1 = -31.42647, -64.18722
    lat2, lon2 = -31.43647, -64.19722
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    assert 1.0 <= distance <= 2.0  # ~1.5km