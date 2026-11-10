"""Find local businesses in a bounding box via OpenStreetMap's free Overpass API."""

from __future__ import annotations

import sys
import time

import requests

from .cities import USER_AGENT

# Public Overpass endpoints, tried in order. maps.mail.ru answered reliably in testing;
# the others are kept as fallbacks.
MIRRORS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# Category groups -> {osm_key: [values]}. "*" means any value for that key.
CATEGORY_GROUPS: dict[str, dict[str, list[str]]] = {
    "beauty": {
        "shop": ["hairdresser", "beauty", "cosmetics", "massage", "tattoo", "perfumery"],
        "amenity": ["spa"],
        "leisure": ["spa"],
    },
    "health": {
        "amenity": ["dentist", "clinic", "doctors", "veterinary", "pharmacy"],
        "healthcare": ["*"],
        "shop": ["optician", "hearing_aids", "medical_supply"],
    },
    "food": {
        "amenity": ["restaurant", "cafe", "fast_food", "bar", "pub", "ice_cream"],
        "shop": ["bakery", "deli", "confectionery", "pastry", "butcher", "cheese", "wine", "coffee"],
    },
    "trades": {
        "craft": ["*"],
        "shop": ["hardware", "doityourself", "locksmith", "trade"],
    },
    "fitness": {
        "leisure": ["fitness_centre", "sports_centre", "dance"],
        "amenity": ["dojo"],
    },
    "professional": {
        "office": ["lawyer", "accountant", "insurance", "estate_agent", "architect", "tax_advisor",
                   "financial", "notary", "travel_agent", "company", "consulting", "it"],
    },
    "retail": {
        "shop": ["clothes", "shoes", "jewelry", "florist", "furniture", "electronics", "gift", "toys",
                 "pet", "bicycle", "books", "interior_decoration", "kitchen", "bed", "boutique",
                 "mobile_phone", "computer", "photo", "art", "music", "sports", "outdoor", "bag",
                 "fabric", "curtain", "lighting", "garden_centre", "baby_goods", "dry_cleaning",
                 "laundry", "copyshop", "tailor"],
    },
    "auto": {
        "shop": ["car_repair", "car", "tyres", "car_parts", "motorcycle"],
        "amenity": ["car_wash", "driving_school"],
    },
    "education": {
        "amenity": ["driving_school", "music_school", "language_school", "prep_school"],
    },
    "hospitality": {
        "tourism": ["hotel", "guest_house", "hostel", "apartment"],
    },
}

TAG_KEYS = ["shop", "amenity", "craft", "office", "healthcare", "leisure", "tourism"]


def resolve_categories(category: str) -> dict[str, list[str]]:
    """'all', a group name, a comma list of groups, or a raw OSM value like 'hairdresser'."""
    merged: dict[str, set[str]] = {}

    def add(spec: dict[str, list[str]]) -> None:
        for k, vals in spec.items():
            merged.setdefault(k, set()).update(vals)

    for part in [p.strip().lower() for p in category.split(",") if p.strip()]:
        if part == "all":
            for spec in CATEGORY_GROUPS.values():
                add(spec)
        elif part in CATEGORY_GROUPS:
            add(CATEGORY_GROUPS[part])
        else:  # raw OSM value, e.g. "dentist" -> match it under any business key
            add({k: [part] for k in TAG_KEYS})
    return {k: sorted(v) for k, v in merged.items()}


def build_query(bbox: tuple[float, float, float, float], spec: dict[str, list[str]], timeout: int = 90) -> str:
    s, w, n, e = bbox
    box = f"({s},{w},{n},{e})"
    lines = []
    for key, vals in spec.items():
        if "*" in vals:
            lines.append(f'  nwr["{key}"]["name"]{box};')
        else:
            regex = "|".join(vals)
            lines.append(f'  nwr["{key}"~"^({regex})$"]["name"]{box};')
    return f"[out:json][timeout:{timeout}];\n(\n" + "\n".join(lines) + "\n);\nout center tags;"


def fetch(query: str, retries_per_mirror: int = 1, timeout: int = 120) -> list[dict]:
    errors = []
    for url in MIRRORS:
        for attempt in range(retries_per_mirror + 1):
            try:
                resp = requests.get(url, params={"data": query}, headers={"User-Agent": USER_AGENT},
                                    timeout=timeout)
                if resp.status_code == 200 and resp.text.lstrip().startswith("{"):
                    print(f"  OpenStreetMap answered via {url.split('/')[2]}", file=sys.stderr)
                    return resp.json().get("elements", [])
                errors.append(f"{url}: HTTP {resp.status_code}")
            except requests.RequestException as exc:
                errors.append(f"{url}: {type(exc).__name__}")
                print(f"  {url.split('/')[2]} failed ({type(exc).__name__}), trying next…", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("All Overpass mirrors failed:\n  " + "\n  ".join(errors))


SOCIAL_HOSTS = ("facebook.com", "fb.com", "instagram.com", "linktr.ee", "tiktok.com")
# Directory listings are not the business's own website: a business whose only "site" is one of these
# is still a website lead.
DIRECTORY_HOSTS = ("easy.co.il", "b144.co.il", "d.co.il", "zap.co.il", "rest.co.il", "2eat.co.il",
                   "wolt.com", "10bis.co.il", "google.com/maps", "goo.gl/maps", "maps.app.goo.gl",
                   "yelp.com", "tripadvisor.")
# Institutions and services that don't buy small-business websites.
EXCLUDED_VALUES = {"hospital", "university", "college", "school", "kindergarten", "police", "townhall",
                   "post_office", "bank", "atm", "place_of_worship", "social_facility", "blood_donation",
                   "laboratory"}


def _first(tags: dict, *keys: str) -> str:
    for k in keys:
        if tags.get(k):
            return tags[k].split(";")[0].strip()
    return ""


def element_to_lead(el: dict, city: str) -> dict | None:
    tags = el.get("tags", {})
    if tags.get("brand") or tags.get("brand:wikidata") or tags.get("operator:wikidata"):
        return None  # chain / franchise: they buy websites at HQ level
    if any(tags.get(k) in EXCLUDED_VALUES for k in TAG_KEYS) or tags.get("government"):
        return None
    name = tags.get("name:he") or tags.get("name") or tags.get("name:en")
    if not name:
        return None
    category = next((f"{k}={tags[k]}" for k in TAG_KEYS if tags.get(k)), "")
    website = _first(tags, "website", "contact:website", "url")
    facebook = _first(tags, "contact:facebook", "facebook")
    instagram = _first(tags, "contact:instagram", "instagram")
    if website and any(h in website.lower() for h in SOCIAL_HOSTS):
        if "instagram" in website.lower() and not instagram:
            instagram = website
        elif not facebook:
            facebook = website
        website = ""
    directory = ""
    if website and any(h in website.lower() for h in DIRECTORY_HOSTS):
        directory, website = website, ""
    street = " ".join(x for x in [tags.get("addr:street", ""), tags.get("addr:housenumber", "")] if x)
    address = ", ".join(x for x in [street, tags.get("addr:city", "")] if x)
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    return {
        "lead_id": f"osm:{el['type']}/{el['id']}",
        "name": name,
        "name_en": tags.get("name:en", "") if tags.get("name:en") != name else "",
        "category": category,
        "city": city,
        "address": address,
        "phone": _first(tags, "phone", "contact:phone", "mobile", "contact:mobile"),
        "email": _first(tags, "email", "contact:email"),
        "website": website,
        "facebook": facebook,
        "instagram": instagram,
        "directory_page": directory,
        "opening_hours": tags.get("opening_hours", ""),
        "lat": lat,
        "lon": lon,
    }


def find_businesses(bbox, category: str, city: str) -> tuple[list[dict], dict]:
    """Return (leads, stats). Stats counts raw elements and exclusions."""
    elements = fetch(build_query(bbox, resolve_categories(category)))
    leads, seen_keys, chains = [], set(), 0
    for el in elements:
        lead = element_to_lead(el, city)
        if lead is None:
            if el.get("tags", {}).get("brand") or el.get("tags", {}).get("brand:wikidata"):
                chains += 1
            continue
        key = (lead["name"].strip().lower(), lead["address"].lower() or lead["lead_id"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        leads.append(lead)
    return leads, {"osm_elements": len(elements), "chains_excluded": chains, "businesses": len(leads)}
