import difflib
import math


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculates clean text ratio using sequence matcher."""
    if not text1 or not text2:
        return 0.0
    t1 = text1.strip().lower()
    t2 = text2.strip().lower()
    return difflib.SequenceMatcher(None, t1, t2).ratio()


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculates great-circle distance between coordinates in meters."""
    r = 6371000.0  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return r * c
