"""When to call each lead: best windows, rush hours to avoid, opening hours, Israeli week + holidays.

Days use the JavaScript convention so the same schedule drives Python and the phone page:
0 = Sunday … 5 = Friday, 6 = Saturday. Times are minutes after midnight, Israel time.
Sources and which windows are inferred: RESEARCH.md ("When to call").
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from . import holidays

DAY_LETTERS = ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ש'"]
DAY_NAMES = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
COURTESY = (7 * 60 + 30, 20 * 60 + 30)  # never call before 07:30 or after 20:30
FRIDAY_END = 11 * 60
SUNDAY_START = 10 * 60
WORKDAYS = (0, 1, 2, 3, 4)


def hm(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def fmt(minutes: int) -> str:
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass(frozen=True)
class Profile:
    key: str
    label_he: str
    best: tuple[tuple[str, str], ...]
    avoid: tuple[tuple[str, str], ...]
    avoid_reason_he: str
    tip_he: str
    premises: bool = True            # phone rings at the venue → trim to opening hours
    best_days: tuple[int, ...] = WORKDAYS
    busy_days: tuple[int, ...] = ()  # whole day counts as rush
    friday_ok: bool = True
    month_avoid: tuple[int, int] | None = None  # days of month to avoid (accountants)
    sourced: bool = False            # True = directly from a source, False = inferred (see RESEARCH.md)


P = Profile
PROFILES: dict[str, Profile] = {p.key: p for p in [
    P("restaurant", "מסעדה", (("10:00", "11:30"), ("15:00", "17:00")), (("12:00", "14:30"), ("18:30", "21:30")),
      "שעות הארוחות", "לא להתקשר באמצע ארוחת צהריים או ערב. בין הצהריים לערב הבעלים הכי פנויים.", sourced=True),
    P("cafe", "בית קפה / מאפייה", (("10:30", "11:30"), ("14:30", "16:30")), (("07:30", "10:00"), ("12:00", "14:00")),
      "בוקר וצהריים", "אחרי עומס הבוקר ולפני הצהריים יש חלון קצר ושקט."),
    P("bar", "בר / פאב", (("14:00", "17:00"),), (("20:00", "23:59"),),
      "משמרת ערב", "לתפוס את הבעלים לפני פתיחת הערב (הכנות, ספקים)."),
    P("beauty", "מספרה / יופי", (("09:00", "10:00"), ("13:00", "15:00")), (("16:30", "20:00"),),
      "אחר הצהריים והערב", "עדיף וואטסאפ קודם. בשיחה – לשאול מתי יש הפסקה בין לקוחות.",
      best_days=(0, 1, 2, 3), busy_days=(4, 5), friday_ok=False),
    P("clinic", "מרפאה / קליניקה", (("08:00", "09:00"), ("13:00", "14:30")), (("09:00", "12:30"), ("16:00", "19:00")),
      "שעות קבלת מטופלים", "בדרך כלל עונה מזכירה – לשאול מתי הרופא/ה פנוי/ה ולחזור אז."),
    P("trades", "בעל מקצוע", (("07:30", "08:30"), ("17:00", "18:30")), (("09:00", "16:00"),),
      "בעבודה בשטח", "לפני שיוצאים לעבודה או בסוף היום. הטלפון הוא נייד, לא של חנות.", premises=False),
    P("garage", "מוסך / צמיגים", (("12:30", "15:00"),), (("07:30", "09:30"), ("16:00", "18:00")),
      "קבלת רכבים בבוקר ומסירה אחה\"צ", "באמצע היום, אחרי שכל הרכבים נכנסו."),
    P("school", "בית ספר לנהיגה / מוזיקה / שפות", (("09:00", "12:00"),), (("14:00", "20:00"),),
      "שיעורים אחר הצהריים", "בבוקר, לפני שהשיעורים מתחילים."),
    P("office", "משרד / שירותים מקצועיים", (("10:00", "12:00"), ("14:00", "16:00")), (("08:00", "09:30"),),
      "פתיחת היום", "באמצע השבוע, אחרי שהיום התחיל."),
    P("accountant", "רואה חשבון / יועץ מס", (("10:00", "12:00"), ("14:00", "16:00")), (("08:00", "09:30"),),
      "פתיחת היום", "להימנע מה-10 עד ה-15 בחודש (דיווחי מע\"מ) ומעונת הדוחות השנתיים.", month_avoid=(10, 15)),
    P("fitness", "חדר כושר / סטודיו", (("10:00", "15:00"),), (("06:00", "09:00"), ("17:00", "21:00")),
      "אימוני בוקר וערב", "באמצע היום, כשהסטודיו ריק."),
    P("retail", "חנות", (("10:00", "12:00"),), (("17:00", "20:00"),),
      "שעות קנייה אחה\"צ", "בבוקר, אחרי פתיחה, כשאין קונים.", friday_ok=False),
    P("hotel", "מלון / צימר", (("12:00", "14:00"),), (("10:00", "12:00"), ("14:00", "17:00")),
      "צ'ק-אאוט וצ'ק-אין", "באמצע השבוע, בין צ'ק-אאוט לצ'ק-אין.", best_days=(0, 1, 2, 3), busy_days=(4, 5)),
    P("default", "עסק", (("10:00", "11:30"), ("14:30", "16:30")), (("12:30", "14:00"),),
      "הפסקת צהריים", "אמצע השבוע ובאמצע הבוקר עובדים הכי טוב.", sourced=True),
]}

CATEGORY_PROFILE = {
    "restaurant": "restaurant", "fast_food": "restaurant", "food_court": "restaurant",
    "cafe": "cafe", "bakery": "cafe", "deli": "cafe", "pastry": "cafe", "confectionery": "cafe",
    "ice_cream": "cafe", "coffee": "cafe",
    "bar": "bar", "pub": "bar", "nightclub": "bar",
    "hairdresser": "beauty", "beauty": "beauty", "cosmetics": "beauty", "massage": "beauty", "spa": "beauty",
    "tattoo": "beauty", "perfumery": "beauty",
    "dentist": "clinic", "clinic": "clinic", "doctors": "clinic", "veterinary": "clinic",
    "optician": "clinic", "hearing_aids": "clinic",
    "car_repair": "garage", "tyres": "garage", "car_wash": "garage", "car_parts": "garage",
    "motorcycle": "garage", "car": "garage",
    "driving_school": "school", "music_school": "school", "language_school": "school", "prep_school": "school",
    "accountant": "accountant", "tax_advisor": "accountant",
    "fitness_centre": "fitness", "sports_centre": "fitness", "dance": "fitness", "dojo": "fitness",
    "hotel": "hotel", "guest_house": "hotel", "hostel": "hotel", "apartment": "hotel",
    "locksmith": "trades",
}


def profile_for(category: str) -> Profile:
    key, _, value = (category or "").partition("=")
    if value in CATEGORY_PROFILE:
        return PROFILES[CATEGORY_PROFILE[value]]
    if key == "craft":
        return PROFILES["trades"]
    if key == "healthcare":
        return PROFILES["clinic"]
    if key == "office":
        return PROFILES["office"]
    if key == "shop":
        return PROFILES["retail"]
    return PROFILES["default"]


# ---------------------------------------------------------------- opening hours (common OSM syntax)
OSM_DAYS = {"Su": 0, "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6}
TIME_RANGE = re.compile(r"^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$")


def _days(spec: str) -> list[int] | None:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            if a not in OSM_DAYS or b not in OSM_DAYS:
                return None
            i = OSM_DAYS[a]
            while True:
                out.append(i)
                if i == OSM_DAYS[b]:
                    break
                i = (i + 1) % 7
        elif part in OSM_DAYS:
            out.append(OSM_DAYS[part])
        else:
            return None
    return out


def parse_opening_hours(text: str) -> dict[int, list[list[int]]] | None:
    """'Su-Th 09:00-19:00; Fr 09:00-14:00' -> {0: [[540, 1140]], …}. None if not understood."""
    text = (text or "").strip()
    if not text:
        return None
    if text == "24/7":
        return {d: [[0, 24 * 60]] for d in range(7)}
    hours: dict[int, list[list[int]]] = {d: [] for d in range(7)}
    for rule in [r.strip() for r in text.split(";") if r.strip()]:
        if rule.startswith("PH"):
            continue  # public holidays are handled by holidays.py
        m = re.match(r"^([A-Za-z,\- ]+?)\s+(.+)$", rule)
        if m and _days(m.group(1).replace(" ", "")) is not None:
            days, times = _days(m.group(1).replace(" ", "")), m.group(2).strip()
        elif TIME_RANGE.match(rule.split(",")[0].strip()):
            days, times = list(range(7)), rule
        else:
            return None
        if times.lower() in ("off", "closed"):
            for d in days:
                hours[d] = []
            continue
        ranges = []
        for tr in times.split(","):
            tm = TIME_RANGE.match(tr.strip())
            if not tm:
                return None
            s, e = hm(tm.group(1)), hm(tm.group(2))
            if e <= s:
                e = 24 * 60  # past midnight: only the part before midnight matters for calling
            ranges.append([s, e])
        for d in days:
            hours[d] = ranges
    return hours


# ---------------------------------------------------------------- window arithmetic
def _intersect(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            s, e = max(s1, s2), min(e1, e2)
            if e - s >= 15:
                out.append([s, e])
    return sorted(out)


def _clip(ranges, lo, hi):
    return _intersect(ranges, [[lo, hi]])


def in_ranges(ranges, minute: int) -> bool:
    return any(s <= minute < e for s, e in ranges)


def build_schedule(prof: Profile, opening: dict | None) -> dict:
    """Weekly schedule {'best': {day: ranges}, 'avoid': {...}, 'open': {...} | None}."""
    best_w = [[hm(s), hm(e)] for s, e in prof.best]
    avoid_w = [[hm(s), hm(e) if e != "23:59" else 24 * 60] for s, e in prof.avoid]
    best, avoid = {}, {}
    for d in range(7):
        if d == 6:
            best[d], avoid[d] = [], [[0, 24 * 60]]
            continue
        b = best_w if d in prof.best_days else []
        if d == 0 and prof.premises:
            shifted = _clip(b, SUNDAY_START, 24 * 60)
            b = shifted or b
        if d == 5:
            b = _clip(b, 0, FRIDAY_END) if prof.friday_ok else []
            if prof.friday_ok and not b:
                b = [[9 * 60, FRIDAY_END]]
        a = [[0, 24 * 60]] if d in prof.busy_days else list(avoid_w)
        if d == 5:
            a = a + [[FRIDAY_END, 24 * 60]]
        if prof.premises and opening is not None:
            open_d = opening.get(d, [])
            if not open_d:
                b = []
            else:
                trimmed = _intersect(b, open_d)
                if not trimmed and b:
                    # e.g. a bar that opens at 19:00: the first half hour after opening
                    s = open_d[0][0]
                    trimmed = [[s, s + 30]]
                b = trimmed
        if d == 5:
            b = _clip(b, 0, FRIDAY_END)  # never into Friday afternoon / Shabbat eve
        best[d] = _clip(b, *COURTESY)
        avoid[d] = a
    return {"best": best, "avoid": avoid,
            "open": None if (opening is None or not prof.premises) else opening,
            "month_avoid": list(prof.month_avoid) if prof.month_avoid else None}


def _get(per_day: dict, day: int) -> list:
    """Schedules loaded back from JSON have string day keys."""
    return per_day.get(day, per_day.get(str(day), []))


def day_windows(schedule: dict, day: dt.date) -> tuple[list, list, dict | None, str]:
    """(best, avoid, open_or_None, note) for a specific date, applying Israeli holidays."""
    dow = (day.weekday() + 1) % 7
    hol = holidays.on(day)
    if hol and hol["kind"] in holidays.NO_CALLS:
        return [], [[0, 24 * 60]], None, f"{hol['name_he']} – לא מתקשרים היום"
    if dow == 6:
        return [], [[0, 24 * 60]], None, "שבת – לא מתקשרים"
    key = 5 if (hol and hol["kind"] == "eve") else dow
    best = _get(schedule["best"], key)
    avoid = _get(schedule["avoid"], key)
    opening = _get(schedule["open"], key) if schedule.get("open") is not None else None
    note = ""
    ma = schedule.get("month_avoid")
    if ma and ma[0] <= day.day <= ma[1]:
        return [], avoid, opening, "ימי דיווח מע\"מ – עדיף אחרי ה-15 בחודש"
    if hol and hol["kind"] == "eve":
        note = f"{hol['name_he']} – יום קצר, רק עד 11:00"
    elif hol and hol["kind"] == "low":
        note = f"{hol['name_he']} – הרבה בעלי עסקים לא זמינים"
    return best, avoid, opening, note


def next_good(schedule: dict, after: dt.datetime, skip_window: tuple[str, int] | None = None,
              horizon_days: int = 10) -> dt.datetime | None:
    """Start of the next best window after `after` (naive Israel time). `skip_window` = (date, window start)."""
    for i in range(horizon_days):
        day = after.date() + dt.timedelta(days=i)
        best, _, _, _ = day_windows(schedule, day)
        for s, e in best:
            if skip_window and skip_window == (day.isoformat(), s):
                continue
            start = dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=s)
            end = dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=e)
            if end - dt.timedelta(minutes=10) <= after:
                continue
            return max(start, after) if start < after else start
    return None


# ---------------------------------------------------------------- human text
def _fmt_ranges(ranges) -> str:
    # ASCII hyphen on purpose: inside Hebrew text, "07:30-08:30" stays in order (bidi treats it as one number),
    # while an en dash would make it display as "08:30–07:30".
    return " · ".join(f"{fmt(s)}-{fmt(e)}" for s, e in ranges)


def _group_days(per_day: dict[int, str]) -> str:
    parts, d = [], 0
    while d < 7:
        text = per_day.get(d, "")
        if not text:
            d += 1
            continue
        e = d
        while e + 1 < 7 and per_day.get(e + 1, "") == text:
            e += 1
        days = DAY_LETTERS[d] if d == e else f"{DAY_LETTERS[d]}–{DAY_LETTERS[e]}"
        parts.append(f"{days} {text}")
        d = e + 1
    return " | ".join(parts)


def hours_he(text: str) -> str:
    """'Su-Th 7:30-17:00; Fr 7:30-13:00' -> "א'–ה' 07:30-17:00 | ו' 07:30-13:00"; raw text if not understood."""
    parsed = parse_opening_hours(text)
    if parsed is None:
        return text or ""
    if all(r == [[0, 1440]] for r in parsed.values()):
        return "24/7"
    out = _group_days({d: _fmt_ranges(r) for d, r in parsed.items()})
    closed = [DAY_LETTERS[d] for d in range(7) if not parsed.get(d)]
    return out + (f" | סגור: {', '.join(closed)}" if closed else "")


def describe(prof: Profile, schedule: dict) -> tuple[str, str, str]:
    best = _group_days({d: _fmt_ranges(r) for d, r in schedule["best"].items()})
    avoid_ranges = [[hm(s), hm(e) if e != "23:59" else 24 * 60] for s, e in prof.avoid]
    avoid = f"{_fmt_ranges(avoid_ranges)} ({prof.avoid_reason_he})" if avoid_ranges else ""
    if prof.busy_days:
        avoid += f" · {'–'.join(DAY_LETTERS[d] for d in (prof.busy_days[0], prof.busy_days[-1]))} ימים עמוסים"
    if not prof.friday_ok:
        avoid += " · לא בשישי"
    tip = prof.tip_he
    return best or "לא נמצא חלון מתאים – לבדוק שעות פתיחה", avoid.strip(" ·"), tip


def annotate(lead: dict, personal: dict | None = None) -> dict:
    """Add call_profile, call_best, call_avoid, call_tip, call_schedule (+ personal best hours)."""
    prof = profile_for(lead.get("category", ""))
    opening = parse_opening_hours(lead.get("opening_hours", ""))
    schedule = build_schedule(prof, opening)
    best, avoid, tip = describe(prof, schedule)
    lead.update({"call_profile": prof.key, "call_best": best, "call_avoid": avoid, "call_tip": tip,
                 "opening_he": hours_he(lead.get("opening_hours", "")),
                 "call_schedule": schedule, "call_personal": ""})
    stats = (personal or {}).get(prof.key)
    if stats and stats.get("calls", 0) >= 20 and stats.get("top"):
        h, rate, n = stats["top"]
        lead["call_personal"] = f"לפי השיחות שלך: הכי עונים {h:02d}:00-{h + 1:02d}:00 ({round(rate * 100)}%, {n} שיחות)"
    return lead
