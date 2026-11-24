"""Where your own data lives. Override with the LEAD_AGENT_HOME environment variable."""

import os
from pathlib import Path

PACKAGE_DATA = Path(__file__).parent / "data"
BASELINE = PACKAGE_DATA / "weights.json"


def home() -> Path:
    """Folder for lead sheets, seen.csv, outcomes.csv and learned weights (default: ./leads)."""
    return Path(os.environ.get("LEAD_AGENT_HOME") or Path.cwd() / "leads")


def learned_weights() -> Path:
    return home() / "weights.learned.json"


def outcomes() -> Path:
    return home() / "outcomes.csv"
