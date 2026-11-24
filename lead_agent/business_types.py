"""Business-type playbooks: which types pay well, which close easily, and what each wants.

Two playbooks, same shape:
  website  data/business_types.json  18 local business types, priced for a website (Website Client Map research)
  app      data/app_types.json       14 restaurant types, priced for an app, first year (App Client Map research)
Prices and ease are estimates. Used by `find --type <id>` (website playbook, or the app playbook with --focus app),
`types suggest [--app]` (what to offer the user today) and the two lead-finder subagents.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .paths import home

DATA = Path(__file__).parent / "data" / "business_types.json"
PLAYBOOKS = {"website": DATA, "app": Path(__file__).parent / "data" / "app_types.json"}
QUADRANT_NAMES = {"sweet": "Sweet spot (easy, pays well)", "volume": "Volume (easy, cheap)",
                  "bigfish": "Big fish (hard, pays well)", "skip": "Skip for now (hard, cheap)"}


def _doc(kind: str = "website") -> dict:
    return json.loads(PLAYBOOKS[kind].read_text(encoding="utf-8"))


def load(kind: str = "website") -> list[dict]:
    doc = _doc(kind)
    rule = doc["quadrant_rule"]
    out = []
    for t in doc["types"]:
        mid = math.sqrt(t["lo"] * t["hi"])
        q = (("sweet" if mid >= rule["price_split"] else "volume") if t["ease"] >= rule["ease_split"]
             else ("bigfish" if mid >= rule["price_split"] else "skip"))
        out.append({**t, "quadrant": q, "approach": doc["approach"][q], "playbook": kind})
    return out


def get(key: str, kind: str = "website") -> dict | None:
    """Match by id, English or Hebrew name, or an alias (case-insensitive)."""
    k = (key or "").strip().lower()
    if not k:
        return None
    types = load(kind)
    for t in types:
        if k == t["id"] or k == t["name"].lower() or k == t["he"] or k in [a.lower() for a in t["aliases"]]:
            return t
    for t in types:  # loose: the key appears in the name or an alias appears in the key
        if k in t["name"].lower() or any(a.lower() in k for a in t["aliases"] if len(a) > 3):
            return t
    return None


def filter_by_name(t: dict, leads: list[dict]) -> list[dict]:
    """Narrow leads to the type when its OSM tags are shared with other types.

    A lead is kept if its OSM cuisine matches (`cuisine`) or its name contains a keyword (`name_keywords`); a type with
    neither keeps everything. `min_branches` keeps only names that appear at that many addresses (small chains).
    """
    kws = [k.lower() for k in (t.get("name_keywords") or [])]
    cuisines = {c.lower() for c in (t.get("cuisine") or [])}
    if kws or cuisines:
        def match(l: dict) -> bool:
            lead_cuisines = {c.strip().lower() for c in (l.get("cuisine") or "").split(";") if c.strip()}
            name = f"{l.get('name', '')} {l.get('name_en', '')}".lower()
            return bool(lead_cuisines & cuisines) or any(k in name for k in kws)
        leads = [l for l in leads if match(l)]
    if t.get("min_branches"):
        norm = lambda l: " ".join(l.get("name", "").lower().split())
        counts: dict[str, int] = {}
        for l in leads:
            counts[norm(l)] = counts.get(norm(l), 0) + 1
        leads = [l for l in leads if counts[norm(l)] >= t["min_branches"]]
    return leads


def history(kind: str = "website") -> dict[str, str]:
    """{type_id: last run date} for one playbook, from run files in the leads folder and from lead-burn runs."""
    last: dict[str, str] = {}
    folder = home()
    if folder.exists():
        for p in folder.glob("*.json"):
            try:
                meta = json.loads(p.read_text(encoding="utf-8")).get("meta", {})
            except (ValueError, OSError):
                continue
            tid, when = meta.get("business_type"), (meta.get("created") or "")[:10]
            if meta.get("playbook", "website") != kind:
                continue
            if tid and when > last.get(tid, ""):
                last[tid] = when
    try:
        from . import burn
        for r in burn.load().get("runs", []):
            if (r.get("focus") == "app") != (kind == "app"):
                continue
            tid, when = (r.get("target") or {}).get("type"), (r.get("finished") or "")[:10]
            if tid and when > last.get(tid, ""):
                last[tid] = when
    except (ValueError, OSError):
        pass
    return last


def suggest(kind: str = "website") -> list[dict]:
    """One type per quadrant (sweet spot first, never "skip"): the one not run for the longest."""
    last = history(kind)
    out = []
    for q in ("sweet", "volume", "bigfish"):
        group = [t for t in load(kind) if t["quadrant"] == q]
        # least recently run first (never run = ""); ties go to the best value, middle price x ease
        pick = min(group, key=lambda t: (last.get(t["id"], ""), -math.sqrt(t["lo"] * t["hi"]) * t["ease"]))
        out.append({"id": pick["id"], "name": pick["name"], "he": pick["he"], "quadrant": q, "playbook": kind,
                    "quadrant_name": QUADRANT_NAMES[q], "price": f"₪{pick['lo']:,}-₪{pick['hi']:,}",
                    "ease": pick["ease"], "last_run": last.get(pick["id"]) or "never", "pitch": pick["pitch"]})
    return out


def summary(t: dict) -> dict:
    return {"id": t["id"], "name": t["name"], "he": t["he"], "quadrant": t["quadrant"], "playbook": t["playbook"],
            "price": f"₪{t['lo']:,}-₪{t['hi']:,}" + (" first year" if t["playbook"] == "app" else ""), "ease": t["ease"]}


