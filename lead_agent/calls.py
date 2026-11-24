"""Call log: what happened on each call, follow-up suggestions, do-not-contact list, your own best hours.

Files (in the leads folder, git-ignored):
  calls.csv            one row per call attempt
  do_not_contact.csv   businesses that said no: never shown again
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path

from . import call_times
from .paths import home

RESULTS = ["answered", "no_answer", "call_back", "not_interested", "meeting", "won", "lost"]
RESULT_HE = {"answered": "ענה", "no_answer": "לא ענה", "call_back": "לחזור", "not_interested": "לא מעוניין",
             "meeting": "פגישה", "won": "נסגר ✓", "lost": "לא נסגר"}
FIELDS = ["lead_id", "at", "result", "callback_at", "note", "name", "profile"]
DONE = {"not_interested", "won", "lost"}
MAX_ATTEMPTS = 4
# How far each result moves the sheet's status (only ever upgraded, never downgraded).
STATUS_RANK = {"": 0, "contacted": 1, "replied": 2, "meeting": 3, "won": 4, "lost": 4, "no_reply": 4,
               "not_interested": 4}
RESULT_STATUS = {"no_answer": "contacted", "answered": "replied", "call_back": "replied", "meeting": "meeting",
                 "won": "won", "lost": "lost", "not_interested": "not_interested"}
PRIOR = {"best": 0.30, "other": 0.20, "avoid": 0.10}
SMOOTHING = 5.0


def calls_path() -> Path:
    return home() / "calls.csv"


def dnc_path() -> Path:
    return home() / "do_not_contact.csv"


def now_il() -> dt.datetime:
    """Current Israel time as a naive datetime (all log times are Israel time)."""
    from zoneinfo import ZoneInfo
    return dt.datetime.now(ZoneInfo("Asia/Jerusalem")).replace(tzinfo=None, second=0, microsecond=0)


def parse_time(text: str) -> dt.datetime | None:
    text = (text or "").strip().replace("T", " ")
    if not text:
        return None
    for f in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return dt.datetime.strptime(text[:19] if f.endswith("%S") else text[:16], f)
        except ValueError:
            continue
    if len(text) <= 5 and ":" in text:  # "15:30" = today
        h, m = text.split(":")
        return now_il().replace(hour=int(h), minute=int(m))
    return None


def load() -> list[dict]:
    p = calls_path()
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(rows: list[dict]) -> None:
    p = calls_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda r: (r["at"], r["lead_id"]))
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_dnc() -> set[str]:
    p = dnc_path()
    if not p.exists():
        return set()
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["lead_id"] for r in rows} | {f"phone:{r['phone']}" for r in rows if r.get("phone")}


def is_dnc(lead: dict, dnc: set[str]) -> bool:
    from .cards import phone_e164
    e164 = phone_e164(lead.get("phone", ""))
    return lead["lead_id"] in dnc or (bool(e164) and f"phone:{e164}" in dnc)


def _add_dnc(lead: dict | None, lead_id: str, name: str) -> None:
    from .cards import phone_e164
    p = dnc_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.exists()
    if lead_id in load_dnc():
        return
    with p.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["lead_id", "name", "phone", "date"])
        w.writerow([lead_id, name, phone_e164((lead or {}).get("phone", "")), now_il().date().isoformat()])


def find_lead(lead_id: str) -> tuple[dict | None, Path | None]:
    """Most recent run file containing this lead."""
    for p in sorted(home().glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if not isinstance(data, dict) or "leads" not in data:
            continue
        for lead in data["leads"]:
            if lead.get("lead_id") == lead_id:
                return lead, p
    return None, None


def add(lead_id: str, result: str, at: dt.datetime | None = None, callback_at: dt.datetime | None = None,
        note: str = "") -> dict:
    if result not in RESULTS:
        raise ValueError(f"result must be one of {', '.join(RESULTS)}")
    lead, _ = find_lead(lead_id)
    row = {"lead_id": lead_id, "at": (at or now_il()).strftime("%Y-%m-%d %H:%M"), "result": result,
           "callback_at": callback_at.strftime("%Y-%m-%d %H:%M") if callback_at else "", "note": note,
           "name": (lead or {}).get("name", ""),
           "profile": call_times.profile_for((lead or {}).get("category", "")).key}
    rows = load()
    rows.append(row)
    _save(rows)
    if result == "not_interested":
        _add_dnc(lead, lead_id, row["name"])
    return row


def import_file(path: Path) -> tuple[int, int]:
    """Import a call log exported from the phone page. Returns (added, duplicates)."""
    rows = load()
    seen = {(r["lead_id"], r["at"], r["result"]) for r in rows}
    added = dup = 0
    with path.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if not r.get("lead_id") or r.get("result") not in RESULTS:
                continue
            at = parse_time(r.get("at", ""))
            if not at:
                continue
            key = (r["lead_id"], at.strftime("%Y-%m-%d %H:%M"), r["result"])
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            lead, _ = find_lead(r["lead_id"])
            cb = parse_time(r.get("callback_at", ""))
            rows.append({"lead_id": r["lead_id"], "at": key[1], "result": r["result"],
                         "callback_at": cb.strftime("%Y-%m-%d %H:%M") if cb else "", "note": r.get("note", ""),
                         "name": r.get("name") or (lead or {}).get("name", ""),
                         "profile": r.get("profile") or call_times.profile_for((lead or {}).get("category", "")).key})
            if r["result"] == "not_interested":
                _add_dnc(lead, r["lead_id"], r.get("name", ""))
            added += 1
    _save(rows)
    return added, dup


def history_by_lead(rows: list[dict] | None = None) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows if rows is not None else load():
        out.setdefault(r["lead_id"], []).append(r)
    for h in out.values():
        h.sort(key=lambda r: r["at"])
    return out


def _window_of(schedule: dict, at: dt.datetime) -> tuple[str, int] | None:
    best, _, _, _ = call_times.day_windows(schedule, at.date())
    minute = at.hour * 60 + at.minute
    for s, e in best:
        if s <= minute < e:
            return at.date().isoformat(), s
    return None


def follow_up(lead: dict, history: list[dict], now: dt.datetime | None = None) -> dict:
    """{'state': new|retry|callback|done|stop, 'attempts': n, 'next': datetime|None, 'text': Hebrew}"""
    now = now or now_il()
    attempts = len(history)
    if not history:
        return {"state": "new", "attempts": 0, "next": None, "text": ""}
    last = history[-1]
    results = [h["result"] for h in history]
    if any(r in DONE for r in results):
        final = next(r for r in reversed(results) if r in DONE)
        return {"state": "done", "attempts": attempts, "next": None, "text": RESULT_HE[final]}
    if last["result"] == "meeting":
        return {"state": "done", "attempts": attempts, "next": None, "text": "נקבעה פגישה"}
    if last["result"] == "call_back" and last.get("callback_at"):
        cb = parse_time(last["callback_at"])
        return {"state": "callback", "attempts": attempts, "next": cb,
                "text": f"לחזור ב-{cb:%d/%m %H:%M}" if cb else "לחזור"}
    no_answers = results.count("no_answer")
    if no_answers >= MAX_ATTEMPTS:
        return {"state": "stop", "attempts": attempts, "next": None,
                "text": f"{no_answers} ניסיונות בלי מענה – לשלוח וואטסאפ ולעצור"}
    schedule = lead.get("call_schedule") or call_times.annotate(dict(lead))["call_schedule"]
    last_at = parse_time(last["at"]) or now
    earliest = max(now, last_at + dt.timedelta(hours=2))
    nxt = call_times.next_good(schedule, earliest, skip_window=_window_of(schedule, last_at))
    return {"state": "retry", "attempts": attempts, "next": nxt,
            "text": f"ניסיון {attempts + 1}: {nxt:%d/%m %H:%M}" if nxt else f"ניסיון {attempts + 1}"}


def apply_to_leads(leads: list[dict], rows: list[dict] | None = None) -> None:
    """Fill attempts / next_try / status on leads from the call log (status only ever moves forward)."""
    hist = history_by_lead(rows)
    for lead in leads:
        h = hist.get(lead["lead_id"], [])
        fu = follow_up(lead, h)
        lead["attempts"] = fu["attempts"] or ""
        lead["next_try"] = fu["text"]
        lead["follow_up_state"] = fu["state"]
        lead["call_log"] = [{"at": r["at"], "result": r["result"], "callback_at": r.get("callback_at", "")}
                            for r in h]
        for r in h:
            new = RESULT_STATUS.get(r["result"], "")
            if STATUS_RANK.get(new, 0) > STATUS_RANK.get(str(lead.get("status") or ""), 0):
                lead["status"] = new


def personal_stats(rows: list[dict] | None = None) -> dict:
    """Answer rate per profile and hour, smoothed toward the profile's expected rate."""
    rows = rows if rows is not None else load()
    by_profile: dict[str, dict[int, list[int]]] = {}
    for r in rows:
        at = parse_time(r["at"])
        if not at or not r.get("profile"):
            continue
        cell = by_profile.setdefault(r["profile"], {}).setdefault(at.hour, [0, 0])
        cell[0] += 1
        cell[1] += r["result"] != "no_answer"
    out = {}
    for key, hours in by_profile.items():
        prof = call_times.PROFILES.get(key, call_times.PROFILES["default"])
        sched = call_times.build_schedule(prof, None)["best"].get(2, [])  # a regular Tuesday
        avoid = [[call_times.hm(s), call_times.hm(e) if e != "23:59" else 1440] for s, e in prof.avoid]
        scores = {}
        for h, (n, ok) in hours.items():
            m = h * 60 + 30
            prior = PRIOR["best"] if call_times.in_ranges(sched, m) else \
                PRIOR["avoid"] if call_times.in_ranges(avoid, m) else PRIOR["other"]
            scores[h] = ((ok + prior * SMOOTHING) / (n + SMOOTHING), n)
        calls = sum(n for n, _ in hours.values())
        top = max(((h, s, n) for h, (s, n) in scores.items() if n >= 3), key=lambda t: t[1], default=None)
        out[key] = {"calls": calls, "hours": {h: round(s, 3) for h, (s, _) in scores.items()},
                    "top": [top[0], round(top[1], 3), top[2]] if top else None}
    return out
