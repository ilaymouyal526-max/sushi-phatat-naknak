"""Israeli city bounding boxes (south, west, north, east) with a free Nominatim fallback."""

from __future__ import annotations

import requests

USER_AGENT = "lead-agent/0.1 (local business prospecting script)"

# Approximate municipal extents. Good enough for an Overpass bbox query.
CITIES: dict[str, tuple[float, float, float, float]] = {
    "tel aviv": (32.03, 34.74, 32.15, 34.85),
    "jerusalem": (31.70, 35.10, 31.88, 35.27),
    "haifa": (32.74, 34.95, 32.84, 35.08),
    "rishon lezion": (31.93, 34.74, 32.00, 34.83),
    "petah tikva": (32.06, 34.85, 32.12, 34.92),
    "ashdod": (31.75, 34.60, 31.85, 34.70),
    "netanya": (32.27, 34.83, 32.36, 34.89),
    "beer sheva": (31.21, 34.74, 31.30, 34.84),
    "holon": (31.99, 34.75, 32.04, 34.81),
    "bnei brak": (32.07, 34.82, 32.10, 34.85),
    "ramat gan": (32.04, 34.79, 32.11, 34.85),
    "givatayim": (32.06, 34.80, 32.08, 34.82),
    "rehovot": (31.87, 34.77, 31.92, 34.84),
    "bat yam": (32.00, 34.73, 32.03, 34.77),
    "ashkelon": (31.62, 34.52, 31.70, 34.61),
    "herzliya": (32.15, 34.77, 32.19, 34.86),
    "kfar saba": (32.16, 34.88, 32.20, 34.94),
    "raanana": (32.17, 34.85, 32.20, 34.89),
    "hod hasharon": (32.14, 34.87, 32.17, 34.92),
    "ramat hasharon": (32.13, 34.82, 32.15, 34.86),
    "hadera": (32.42, 34.87, 32.47, 34.95),
    "modiin": (31.87, 34.97, 31.92, 35.04),
    "nazareth": (32.68, 35.28, 32.72, 35.33),
    "tiberias": (32.76, 35.51, 32.81, 35.56),
    "afula": (32.59, 35.27, 32.62, 35.31),
    "nahariya": (32.99, 35.08, 33.03, 35.11),
    "kiryat gat": (31.59, 34.74, 31.63, 34.79),
    "eilat": (29.53, 34.92, 29.58, 34.98),
}

ALIASES: dict[str, str] = {
    "tel aviv-yafo": "tel aviv", "tel-aviv": "tel aviv", "tlv": "tel aviv", "תל אביב": "tel aviv",
    "תל אביב-יפו": "tel aviv", "ירושלים": "jerusalem", "חיפה": "haifa", "ראשון לציון": "rishon lezion",
    "rishon": "rishon lezion", "פתח תקווה": "petah tikva", "petach tikva": "petah tikva",
    "אשדוד": "ashdod", "נתניה": "netanya", "באר שבע": "beer sheva", "beersheba": "beer sheva",
    "be'er sheva": "beer sheva", "חולון": "holon", "בני ברק": "bnei brak", "רמת גן": "ramat gan",
    "גבעתיים": "givatayim", "רחובות": "rehovot", "בת ים": "bat yam", "אשקלון": "ashkelon",
    "הרצליה": "herzliya", "כפר סבא": "kfar saba", "רעננה": "raanana", "ra'anana": "raanana",
    "הוד השרון": "hod hasharon", "רמת השרון": "ramat hasharon", "חדרה": "hadera",
    "מודיעין": "modiin", "modi'in": "modiin", "נצרת": "nazareth", "טבריה": "tiberias",
    "עפולה": "afula", "נהריה": "nahariya", "קריית גת": "kiryat gat", "אילת": "eilat",
}


def normalise(name: str) -> str:
    key = " ".join(name.strip().lower().split())
    return ALIASES.get(key, key)


def resolve_bbox(city: str) -> tuple[str, tuple[float, float, float, float]]:
    """Return (canonical_name, bbox). Falls back to Nominatim for cities not in the table."""
    key = normalise(city)
    if key in CITIES:
        return key, CITIES[key]
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "countrycodes": "il", "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    hits = resp.json()
    if not hits:
        raise ValueError(f"Could not find city {city!r} in Israel. Try an English name or pass --bbox.")
    s, n, w, e = (float(x) for x in hits[0]["boundingbox"])
    return key, (s, w, n, e)
