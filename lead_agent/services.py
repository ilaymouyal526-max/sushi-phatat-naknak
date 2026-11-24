"""What else to offer a lead, by type of business: services, sourced numbers, laws, prices and questions.

The content lives in two editable files: data/services_he.json (services, groups, questions, OSM mapping)
and data/facts_he.json (numbers with sources, legal notes, price ranges). This module only reads and picks.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads((DATA / "services_he.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def facts() -> dict:
    return json.loads((DATA / "facts_he.json").read_text(encoding="utf-8"))


def _osm_group(category: str) -> str:
    """'amenity=dentist' -> 'health', using the finder's own category groups (osm.CATEGORY_GROUPS)."""
    from .osm import CATEGORY_GROUPS
    key, _, value = category.partition("=")
    for name, spec in CATEGORY_GROUPS.items():
        values = spec.get(key, [])
        if value and ("*" in values or value in values):
            return name
    return ""


def group_for(lead: dict) -> str:
    """OSM category ('shop=hairdresser') -> service group ('hair'); 'default' when unknown.

    An exact tag in 'map' wins; otherwise the finder's category group is mapped through 'osm_groups'."""
    cat = catalog()
    category = str(lead.get("category", "")).strip()
    g = cat["map"].get(category) or cat.get("osm_groups", {}).get(_osm_group(category), "default")
    return g if g in cat["groups"] else "default"


def _gaps(lead: dict) -> set[str]:
    signals = lead.get("signals") or []
    if isinstance(signals, str):
        signals = [s.strip() for s in signals.split(",")]
    return set(signals)


def top_services(lead: dict, n: int = 3) -> list[dict]:
    """The n services to raise on a call with this lead, best first.

    A lead with no working site gets the site first; one whose site has no booking gets booking first.
    The rest follow the group's own order (most useful for that type of business first)."""
    cat = catalog()
    order = list(cat["groups"][group_for(lead)]["services"])
    gaps = _gaps(lead)
    first: list[str] = []
    if lead.get("lead_type") in ("WEBSITE", "REDESIGN", "REDESIGN+AUTOMATION") or "site_dead" in gaps:
        first.append("site")
    if "booking" in order and ("no_booking_or_whatsapp" in gaps or lead.get("lead_type") == "WEBSITE"):
        first.append("booking")
    picked = []
    for sid in first + order:
        if sid in cat["services"] and sid not in picked:
            picked.append(sid)
    return [dict(cat["services"][sid], id=sid) for sid in picked[:n]]


def upsell_text(lead: dict, n: int = 3) -> str:
    return " · ".join(s["name_he"] for s in top_services(lead, n))


def pack(group: str) -> dict:
    """Everything the call sheet shows for one group: services (with price text), facts, laws, questions."""
    cat, f = catalog(), facts()
    g = cat["groups"].get(group) or cat["groups"]["default"]
    services, fact_ids, legal_ids = [], [], []
    for sid in g["services"]:
        s = dict(cat["services"][sid], id=sid)
        p = f["prices"].get(s.get("price") or "")
        s["price_info"] = p
        services.append(s)
        fact_ids += [x for x in s.get("facts", []) if x not in fact_ids]
        legal_ids += [x for x in s.get("legal", []) if x not in legal_ids]
    # Numbers that apply to every business, or to this group, even if no listed service points at them.
    for fid, fact in f["facts"].items():
        if fid not in fact_ids and ("*" in fact.get("groups", []) or group in fact.get("groups", [])):
            fact_ids.append(fid)
    return {
        "group": group,
        "label_he": g["label_he"],
        "services": services,
        "facts": [dict(f["facts"][i], id=i) for i in fact_ids],
        "legal": [dict(f["legal"][i], id=i) for i in legal_ids],
        "questions_he": list(g.get("questions_he", [])) + list(cat.get("common_questions_he", [])),
    }
