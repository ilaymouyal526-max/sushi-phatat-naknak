"""Business-type playbook: which types pay well, which close easily, and what each wants from a website.

Data: `data/business_types.json` (from the Website Client Map research, 24 Nov 2026). Prices and ease are estimates.
Used by `find --type <id>` (search exactly that type), `types suggest` (what to offer the user today) and the
website-lead-finder subagent (pitch, look and must-have features per type).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .paths import home

DATA = Path(__file__).parent / "data" / "business_types.json"
QUADRANT_NAMES = {"sweet": "Sweet spot (easy, pays well)", "volume": "Volume (easy, cheap)",
                  "bigfish": "Big fish (hard, pays well)", "skip": "Skip for now (hard, cheap)"}


def _doc() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def load() -> list[dict]:
    doc = _doc()
    rule = doc["quadrant_rule"]
    out = []
    for t in doc["types"]:
        mid = math.sqrt(t["lo"] * t["hi"])
        q = (("sweet" if mid >= rule["price_split"] else "volume") if t["ease"] >= rule["ease_split"]
             else ("bigfish" if mid >= rule["price_split"] else "skip"))
        out.append({**t, "quadrant": q, "approach": doc["approach"][q]})
    return out


def get(key: str) -> dict | None:
    """Match by id, English or Hebrew name, or an alias (case-insensitive)."""
    k = (key or "").strip().lower()
    if not k:
        return None
    types = load()
    for t in types:
        if k == t["id"] or k == t["name"].lower() or k == t["he"] or k in [a.lower() for a in t["aliases"]]:
            return t
    for t in types:  # loose: the key appears in the name or an alias appears in the key
        if k in t["name"].lower() or any(a.lower() in k for a in t["aliases"] if len(a) > 3):
            return t
    return None


def filter_by_name(t: dict, leads: list[dict]) -> list[dict]:
    """Some types share OSM tags with others (aesthetic clinics are tagged like beauty salons); keep name matches."""
    kws = [k.lower() for k in (t.get("name_keywords") or [])]
    if not kws:
        return leads
    return [l for l in leads if any(k in f"{l.get('name', '')} {l.get('name_en', '')}".lower() for k in kws)]


def history() -> dict[str, str]:
    """{type_id: last run date} from run files in the leads folder and from lead-burn runs."""
    last: dict[str, str] = {}
    folder = home()
    if folder.exists():
        for p in folder.glob("*.json"):
            try:
                meta = json.loads(p.read_text(encoding="utf-8")).get("meta", {})
            except (ValueError, OSError):
                continue
            tid, when = meta.get("business_type"), (meta.get("created") or "")[:10]
            if tid and when > last.get(tid, ""):
                last[tid] = when
    try:
        from . import burn
        for r in burn.load().get("runs", []):
            tid, when = (r.get("target") or {}).get("type"), (r.get("finished") or "")[:10]
            if tid and when > last.get(tid, ""):
                last[tid] = when
    except (ValueError, OSError):
        pass
    return last


def suggest() -> list[dict]:
    """One type per quadrant (sweet spot first, never "skip"): the one not run for the longest."""
    last = history()
    out = []
    for q in ("sweet", "volume", "bigfish"):
        group = [t for t in load() if t["quadrant"] == q]
        # least recently run first (never run = ""); ties go to the best value, middle price x ease
        pick = min(group, key=lambda t: (last.get(t["id"], ""), -math.sqrt(t["lo"] * t["hi"]) * t["ease"]))
        out.append({"id": pick["id"], "name": pick["name"], "he": pick["he"], "quadrant": q,
                    "quadrant_name": QUADRANT_NAMES[q], "price": f"₪{pick['lo']:,}-₪{pick['hi']:,}",
                    "ease": pick["ease"], "last_run": last.get(pick["id"]) or "never", "pitch": pick["pitch"]})
    return out


def summary(t: dict) -> dict:
    return {"id": t["id"], "name": t["name"], "he": t["he"], "quadrant": t["quadrant"],
            "price": f"₪{t['lo']:,}-₪{t['hi']:,}", "ease": t["ease"]}


