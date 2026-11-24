"""The app the app-lead-finder sells, described in one small JSON file.

The user is waiting on a handoff file from a friend who builds the app. Until it arrives, there is no profile and
`find --focus app` stops with a clear message. When the handoff arrives, a session reads it and writes the profile
(see `app_profile.example.json` for the fields).

Where the profile is looked up, first match wins:
  1. $LEAD_APP_PROFILE
  2. lead_agent/app_profile.json  (committed; the repo is PUBLIC, so only with the user's OK)
  3. leads/app_profile.json       (git-ignored, private, but lost when a cloud container resets)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .paths import home

EXAMPLE = Path(__file__).parent / "app_profile.example.json"
REQUIRED = ("app_name", "what_it_does", "categories", "good_signs")
WAITING = ("No app profile yet. The app-lead-finder needs the friend's handoff file first: when it arrives, "
           "ask Claude to read it and create the app profile (fields: see lead_agent/app_profile.example.json).")


def candidates() -> list[Path]:
    out = []
    if os.environ.get("LEAD_APP_PROFILE"):
        out.append(Path(os.environ["LEAD_APP_PROFILE"]))
    out += [Path(__file__).parent / "app_profile.json", home() / "app_profile.json"]
    return out


def path() -> Path | None:
    return next((p for p in candidates() if p.exists()), None)


def missing_fields(profile: dict) -> list[str]:
    return [k for k in REQUIRED if not profile.get(k)]


def load() -> dict:
    p = path()
    if not p:
        raise SystemExit(WAITING)
    profile = json.loads(p.read_text(encoding="utf-8"))
    missing = missing_fields(profile)
    if missing:
        raise SystemExit(f"The app profile at {p} is missing: {', '.join(missing)}. {WAITING}")
    return profile


def status() -> dict:
    p = path()
    if not p:
        return {"ready": False, "message": WAITING}
    profile = json.loads(p.read_text(encoding="utf-8"))
    missing = missing_fields(profile)
    return {"ready": not missing, "path": str(p), "app_name": profile.get("app_name"),
            "categories": profile.get("categories"), "missing": missing}
