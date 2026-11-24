"""Use leftover Claude plan usage before it resets: decide when to ask, which city to search, what to remember.

The /lead-burn skill drives this. Each check reads the plan's reset time (from the session's rate-limit info),
calls `decide`, and either schedules the next check, or notifies the user and asks permission to run the
lead-finder subagent in the last hour before the reset. Nothing runs without a "go" from the user.

State lives in `lead_agent/state/burn.json`, which is committed so it survives container restarts. The repo is
public, so it holds **no lead data**: only settings, the rotation position, run counts and salted hashes of lead
ids (so later runs skip leads already delivered, or that said no, even after `leads/` is lost).
Override the path with $LEAD_BURN_STATE.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

IL = ZoneInfo("Asia/Jerusalem")
DEFAULT_STATE = Path(__file__).parent / "state" / "burn.json"
WINDOW_MIN = 300  # the plan's usage window is 5 hours

CITIES = ["tel aviv", "ramat gan", "haifa", "jerusalem", "rishon lezion", "petah tikva", "netanya", "holon",
          "herzliya", "kfar saba", "raanana", "rehovot", "ashdod", "beer sheva", "modiin", "givatayim"]
CATEGORIES = ["beauty", "health", "trades", "auto", "fitness", "professional"]

DEFAULTS = {
    "enabled": True,
    "notify_minutes_before": 70,   # ask this long before the reset
    "stop_minutes_before": 5,      # the run must finish this long before the reset
    "min_minutes_to_run": 25,      # less time than this left: don't bother asking
    "quiet_hours": ["23:00", "08:00"],  # Israel time: never notify inside this range
    "verify_count": 40,            # leads the subagent verifies + writes openers for, per run
    "targets": [[city, cat] for cat in CATEGORIES for city in CITIES],
    "next_target": 0,
    "asked_for": None,             # resets_at (epoch s) we already asked about
    "runs": [],                    # [{resets_at, target, finished, delivered, hot, warm, verified}]
    "seen": [],                    # hashed lead ids delivered by burn runs
    "dnc": [],                     # hashed lead ids that said "not interested"
}


def state_path() -> Path:
    return Path(os.environ.get("LEAD_BURN_STATE") or DEFAULT_STATE)


def load() -> dict:
    p = state_path()
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {**DEFAULTS, **data}


def save(state: dict) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def hash_id(lead_id: str) -> str:
    return hashlib.sha256(f"lead-burn:{lead_id}".encode()).hexdigest()[:16]


def seen_key(lead_id: str, focus: str = "website") -> str:
    """App runs remember leads separately, so a business found for a website can still be found for the app."""
    return f"app:{lead_id}" if focus == "app" else lead_id


def remembered(lead_id: str, state: dict | None = None, focus: str = "website") -> str | None:
    """'seen' / 'dnc' if a burn run delivered this lead before (for this focus) or it said no, else None."""
    state = state if state is not None else (load() if state_path().exists() else {})
    if hash_id(lead_id) in set(state.get("dnc", ())):
        return "dnc"
    if hash_id(seen_key(lead_id, focus)) in set(state.get("seen", ())):
        return "seen"
    return None


def _in_quiet(t: dt.datetime, quiet: list[str]) -> bool:
    start, end = (dt.time.fromisoformat(x) for x in quiet)
    now = t.time()
    return (start <= now or now < end) if start > end else (start <= now < end)


def _fmt(epoch: float) -> str:
    return dt.datetime.fromtimestamp(epoch, IL).strftime("%a %H:%M")


def decide(now: float, resets_at: float | None, status: str, overage: bool = False,
           state: dict | None = None) -> dict:
    """What a check should do now.

    action: notify  → ask the user (push notification) whether to run before `resets_at`
            wait    → nothing to do yet; schedule the next check at `next_check`
            skip    → this window is not worth it (reason); next check at `next_check`
            off     → disabled; schedule nothing
    Times are epoch seconds. `status` is the plan's rate-limit status ("allowed", "allowed_warning", "rejected").
    """
    st = {**DEFAULTS, **(state or {})}
    if not st["enabled"]:
        return {"action": "off", "reason": "lead-burn is turned off"}
    notify = st["notify_minutes_before"] * 60
    after_reset = (WINDOW_MIN * 60) - notify  # T-notify of a window that starts right at the reset

    def out(action, reason, next_check, **kw):
        res = {"action": action, "reason": reason, "next_check": int(next_check),
               "next_check_il": _fmt(next_check)}
        if resets_at:
            res.update(resets_at=int(resets_at), resets_il=_fmt(resets_at),
                       minutes_left=int((resets_at - now) // 60))
        res.update(kw)
        return res

    if not resets_at or resets_at <= now:
        return out("wait", "no reset time for the current window yet", now + after_reset)
    left = resets_at - now
    if left > notify + 15 * 60:
        return out("wait", "too early in this window", resets_at - notify)
    if st.get("asked_for") == int(resets_at):
        return out("wait", "already asked about this window", resets_at + after_reset)
    if overage or status != "allowed":
        return out("skip", f"usage is low or limited (status {status}{', overage' if overage else ''})",
                   resets_at + after_reset)
    if left < st["min_minutes_to_run"] * 60:
        return out("skip", "too little time left before the reset", resets_at + after_reset)
    if _in_quiet(dt.datetime.fromtimestamp(now, IL), st["quiet_hours"]):
        return out("skip", "quiet hours", resets_at + after_reset)
    deadline = resets_at - st["stop_minutes_before"] * 60
    return out("notify", "plenty of usage left and the reset is close", resets_at + after_reset,
               deadline=int(deadline), deadline_il=_fmt(deadline), target=current_target(st),
               verify_count=st["verify_count"])


def current_target(state: dict | None = None) -> dict:
    st = state if state is not None else load()
    targets = st["targets"] or DEFAULTS["targets"]
    city, cat = targets[st["next_target"] % len(targets)]
    return {"city": city, "category": cat, "index": st["next_target"] % len(targets)}


def mark_asked(resets_at: int) -> dict:
    st = load()
    st["asked_for"] = int(resets_at)
    save(st)
    return {"asked_for": st["asked_for"]}


def finish(run_json: Path | None, resets_at: int | None, target: dict | None,
           dnc_csv: Path | None = None, advance: bool = True, focus: str = "website") -> dict:
    """Record a finished run: counts only, hashed lead ids, and move the rotation on."""
    st = load()
    entry = {"resets_at": resets_at, "finished": dt.datetime.now(IL).isoformat(timespec="minutes"),
             "target": target, "focus": focus}
    if run_json and run_json.exists():
        data = json.loads(run_json.read_text(encoding="utf-8"))
        leads = data.get("leads", [])
        seen = set(st["seen"])
        st["seen"] = st["seen"] + [h for h in (hash_id(seen_key(l["lead_id"], focus)) for l in leads)
                                   if h not in seen]
        entry.update(delivered=len(leads), hot=sum(l.get("band") == "Hot" for l in leads),
                     warm=sum(l.get("band") == "Warm" for l in leads),
                     verified=sum((l.get("verified") or l.get("verified_online")) == "yes" for l in leads))
    if dnc_csv and dnc_csv.exists():
        with dnc_csv.open(encoding="utf-8") as f:
            ids = [r["lead_id"] for r in csv.DictReader(f) if r.get("lead_id")]
        have = set(st["dnc"])
        st["dnc"] = st["dnc"] + [h for h in map(hash_id, ids) if h not in have]
    if advance:
        st["next_target"] = (st["next_target"] + 1) % len(st["targets"] or DEFAULTS["targets"])
    st["runs"] = (st["runs"] + [entry])[-50:]
    save(st)
    return {"recorded": entry, "next_target": current_target(st)}


def status() -> dict:
    st = load()
    return {"enabled": st["enabled"], "next_target": current_target(st), "verify_count": st["verify_count"],
            "notify_minutes_before": st["notify_minutes_before"], "quiet_hours": st["quiet_hours"],
            "runs": len(st["runs"]), "last_run": st["runs"][-1] if st["runs"] else None,
            "remembered_leads": len(st["seen"]), "remembered_dnc": len(st["dnc"])}


def configure(**changes) -> dict:
    st = load()
    for k, v in changes.items():
        if v is not None:
            st[k] = v
    save(st)
    return status()
