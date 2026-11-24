"""Daily call plan: who to call when, inside each lead's best window, plus a calendar (.ics) file."""

from __future__ import annotations

import datetime as dt
import json
import uuid
from pathlib import Path

from . import call_times, calls, scripts_he
from .paths import home

SLOT = 8          # minutes per call
BLOCK_GAP = 20    # calls closer than this belong to the same calendar block
PRIORITY = {"callback": 0, "retry": 1, "Hot": 2, "Warm": 3}


def all_leads() -> list[dict]:
    """Latest version of every lead across all run files in the leads folder."""
    seen: dict[str, dict] = {}
    for p in sorted(home().glob("*.json"), key=lambda x: x.stat().st_mtime):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if not isinstance(data, dict) or "leads" not in data:
            continue
        for lead in data["leads"]:
            lead["_run"] = str(p)
            seen[lead["lead_id"]] = lead
    return list(seen.values())


def _free(occupied: list[int], minute: int) -> bool:
    return all(abs(minute - o) >= SLOT for o in occupied)


def _slots(windows, personal_hours: dict | None, not_before: int) -> list[int]:
    out = []
    for s, e in windows:
        t = max(s, not_before)
        t += (-t) % 5  # round up to 5 minutes
        while t + SLOT <= e:
            out.append(t)
            t += SLOT
    if personal_hours:  # your own answer rates first, then earliest
        out.sort(key=lambda m: (-personal_hours.get(str(m // 60), personal_hours.get(m // 60, 0)), m))
    return out


def build(day: dt.date, max_calls: int = 25, now: dt.datetime | None = None,
          leads: list[dict] | None = None) -> dict:
    now = now or calls.now_il()
    leads = leads if leads is not None else all_leads()
    dnc = calls.load_dnc()
    rows = calls.load()
    hist = calls.history_by_lead(rows)
    stats = calls.personal_stats(rows)
    not_before = (now.hour * 60 + now.minute) if day == now.date() else 0
    end_of_day = dt.datetime.combine(day, dt.time(23, 59))

    queue = []
    for lead in leads:
        if not lead.get("phone") or calls.is_dnc(lead, dnc):
            continue
        call_times.annotate(lead, stats)
        fu = calls.follow_up(lead, hist.get(lead["lead_id"], []), now)
        state = fu["state"]
        if state in ("done", "stop"):
            continue
        if state == "callback":
            if not fu["next"] or fu["next"].date() != day:
                continue
            prio = PRIORITY["callback"]
        elif state == "retry":
            if not fu["next"] or fu["next"] > end_of_day:
                continue
            prio = PRIORITY["retry"]
        else:
            if lead.get("band") not in ("Hot", "Warm"):
                continue
            prio = PRIORITY[lead["band"]]
        queue.append((prio, not lead.get("enriched"), -float(lead.get("success_pct") or 0), lead, fu))
    queue.sort(key=lambda q: q[:3])

    occupied: list[int] = []
    entries, skipped = [], 0
    for prio, _, _, lead, fu in queue:
        if len(entries) >= max_calls:
            skipped += 1
            continue
        best, _, _, note = call_times.day_windows(lead["call_schedule"], day)
        minute = None
        if fu["state"] == "callback":
            target = fu["next"].hour * 60 + fu["next"].minute
            for delta in range(0, 60, 2):
                for m in (target + delta, target - delta):
                    if m >= not_before and _free(occupied, m):
                        minute = m
                        break
                if minute is not None:
                    break
        else:
            floor = not_before
            if fu["state"] == "retry" and fu["next"] and fu["next"].date() == day:
                floor = max(floor, fu["next"].hour * 60 + fu["next"].minute)
            pstats = stats.get(lead.get("call_profile")) or {}
            personal = pstats.get("hours") if pstats.get("calls", 0) >= 20 else None
            minute = next((m for m in _slots(best, personal, floor) if _free(occupied, m)), None)
        if minute is None:
            skipped += 1
            continue
        occupied.append(minute)
        kind = {0: "callback", 1: "retry"}.get(prio, "new")
        scripts_he.fill(lead)
        entries.append({"time": dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=minute),
                        "kind": kind, "lead": lead, "note": note, "follow_up": fu})
    entries.sort(key=lambda e: e["time"])

    day_best, _, _, day_note = call_times.day_windows(call_times.annotate({})["call_schedule"], day)
    return {"date": day, "entries": entries, "skipped": skipped, "blocks": blocks(entries),
            "day_note": day_note if not day_best else "", "queue": len(queue)}


def blocks(entries: list[dict]) -> list[dict]:
    out: list[dict] = []
    for e in entries:
        if out and (e["time"] - out[-1]["entries"][-1]["time"]).total_seconds() <= BLOCK_GAP * 60:
            out[-1]["entries"].append(e)
        else:
            out.append({"entries": [e]})
    for b in out:
        b["start"] = b["entries"][0]["time"]
        b["end"] = b["entries"][-1]["time"] + dt.timedelta(minutes=SLOT)
    return out


def next_workday(day: dt.date) -> dt.date:
    sched = call_times.annotate({})["call_schedule"]
    for i in range(1, 15):
        d = day + dt.timedelta(days=i)
        if call_times.day_windows(sched, d)[0]:
            return d
    return day + dt.timedelta(days=1)


# ------------------------------------------------------------------ calendar file
def _utc(local: dt.datetime) -> str:
    from zoneinfo import ZoneInfo
    aware = local.replace(tzinfo=ZoneInfo("Asia/Jerusalem"))
    return aware.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _esc(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r", "").replace("\n", "\\n"))


def _fold(line: str) -> list[str]:
    """RFC 5545: lines longer than 75 octets continue on the next line, starting with a space."""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > (75 if not out else 74):
            out.append(cur)
            cur, size = "", 0
        cur += ch
        size += n
    out.append(cur)
    return [out[0]] + [" " + x for x in out[1:]]


def _event(start: dt.datetime, end: dt.datetime, summary: str, description: str, alarm_min: int) -> list[str]:
    return [
        "BEGIN:VEVENT",
        f"UID:{uuid.uuid4()}@lead-agent",
        f"DTSTAMP:{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}",
        f"DTSTART:{_utc(start)}",
        f"DTEND:{_utc(end)}",
        f"SUMMARY:{_esc(summary)}",
        f"DESCRIPTION:{_esc(description)}",
        "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(summary)}", f"TRIGGER:-PT{alarm_min}M", "END:VALARM",
        "END:VEVENT",
    ]


def to_ics(result: dict) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//lead_agent//call plan//HE", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", "X-WR-CALNAME:שיחות לידים"]
    for b in result["blocks"]:
        n = len(b["entries"])
        desc = "\n".join(f"{e['time']:%H:%M} {e['lead']['name']} – {e['lead'].get('phone', '')} – "
                         f"{(e['lead'].get('why_he') or '').split(';')[0]}" for e in b["entries"])
        lines += _event(b["start"], b["end"], f"📞 בלוק שיחות ({n} {'ליד' if n == 1 else 'לידים'})", desc, 5)
    for e in result["entries"]:
        if e["kind"] == "callback":
            lead = e["lead"]
            lines += _event(e["time"], e["time"] + dt.timedelta(minutes=SLOT),
                            f"🔁 לחזור ל{lead['name']}",
                            f"{lead.get('phone', '')}\nביקשו שנחזור בשעה הזאת.\n{lead.get('why_he', '')}", 10)
    lines.append("END:VCALENDAR")
    return "\r\n".join(sum((_fold(l) for l in lines), [])) + "\r\n"


def write(result: dict, out_dir: Path | None = None) -> dict[str, Path]:
    from .cards import render_plan
    out_dir = out_dir or home()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / f"plan-{result['date'].isoformat()}"
    paths = {"html": base.with_suffix(".html"), "ics": base.with_suffix(".ics")}
    paths["html"].write_text(render_plan(result), encoding="utf-8")
    paths["ics"].write_text(to_ics(result), encoding="utf-8", newline="")
    return paths
