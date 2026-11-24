"""Israeli holidays that change when (and whether) to call. Data: data/holidays_il.json (from Hebcal)."""

from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data" / "holidays_il.json"

# closed / sensitive: no calls · eve: like Friday (until 11:00) · low: allowed, but owners often away
NO_CALLS = {"closed", "sensitive"}


@lru_cache(maxsize=1)
def table() -> dict[str, dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))["days"]


def on(day: dt.date) -> dict | None:
    """Holiday info for a date, or None. {'kind': ..., 'name': ..., 'name_he': ...}"""
    return table().get(day.isoformat())


def upcoming(start: dt.date, days: int = 400) -> dict[str, dict]:
    """Holidays from `start` for `days` days. Embedded in the cards page for the live badge."""
    end = start + dt.timedelta(days=days)
    return {d: {"kind": v["kind"], "name_he": v["name_he"]} for d, v in table().items()
            if start.isoformat() <= d <= end.isoformat()}
