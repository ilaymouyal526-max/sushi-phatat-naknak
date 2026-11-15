"""Fallback Hebrew call scripts, 'missed you' WhatsApp messages and objection answers.

Claude writes personal versions during /find-leads (call_script_he, missed_he); these templates fill in
for leads it hasn't personalised yet, using the real gaps found for each lead.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

OBJECTIONS = Path(__file__).parent / "data" / "objections_he.json"

CATEGORY_HE = {
    "hairdresser": "מספרה", "beauty": "קוסמטיקאית", "cosmetics": "קוסמטיקה", "massage": "עיסוי", "spa": "ספא",
    "tattoo": "קעקועים", "dentist": "רופא שיניים", "clinic": "מרפאה", "doctors": "רופא", "veterinary": "וטרינר",
    "optician": "אופטיקה", "restaurant": "מסעדה", "cafe": "בית קפה", "fast_food": "מזון מהיר", "bar": "בר",
    "pub": "פאב", "bakery": "מאפייה", "car_repair": "מוסך", "tyres": "פנצ'ריה", "car_wash": "שטיפת רכב",
    "driving_school": "בית ספר לנהיגה", "music_school": "בית ספר למוזיקה", "lawyer": "עורך דין",
    "accountant": "רואה חשבון", "estate_agent": "תיווך", "insurance": "סוכן ביטוח", "architect": "אדריכל",
    "fitness_centre": "חדר כושר", "dance": "סטודיו לריקוד", "hotel": "מלון", "guest_house": "צימר",
    "florist": "חנות פרחים", "furniture": "רהיטים", "jewelry": "תכשיטים", "clothes": "חנות בגדים",
    "electrician": "חשמלאי", "plumber": "אינסטלטור", "carpenter": "נגר", "locksmith": "מנעולן",
    "photographer": "צלם", "painter": "צבעי", "gardener": "גנן", "hvac": "מיזוג אוויר", "pet_grooming": "מספרת כלבים",
}


def category_he(lead: dict) -> str:
    value = (lead.get("category", "").split("=")[-1] or "")
    return CATEGORY_HE.get(value, "עסק כמו שלכם")


def city_he(lead: dict) -> str:
    from .cities import ALIASES
    key = str(lead.get("city", "")).lower()
    for alias, canonical in ALIASES.items():
        if canonical == key and any("\u0590" <= ch <= "\u05ff" for ch in alias):
            return alias
    return lead.get("city", "") or "האזור"

GAPS = [  # (signal, how to say it), most important first
    ("no_website", "אין לעסק אתר משלו"),
    ("site_dead", "האתר שלכם לא נפתח"),
    ("ssl_error", "האתר מציג לגולשים אזהרת אבטחה"),
    ("no_mobile", "האתר לא מותאם לנייד"),
    ("stale_site", "האתר לא עודכן כבר כמה שנים"),
    ("free_builder", "האתר יושב על כתובת חינמית של בונה אתרים"),
    ("no_booking_or_whatsapp", "אין אפשרות לקבוע תור או לכתוב בוואטסאפ ישר מהאתר"),
    ("no_contact_capture", "אין באתר טופס או כפתור חיוג"),
]

QUESTIONS = {
    "WEBSITE": ("איך לקוחות חדשים מוצאים אתכם היום?", "קורה שמישהו שואל אם יש לכם אתר, או מחפש אתכם בגוגל ולא מוצא?"),
    "REDESIGN": ("כמה פניות מגיעות היום דרך האתר?", "מתי בפעם האחרונה מישהו עדכן אותו?"),
    "AUTOMATION": ("איך לקוחות קובעים אצלכם היום – רק בטלפון?", "קורה שמפספסים שיחות כשאתם עם לקוח, או שאנשים שוכחים להגיע?"),
}
BENEFIT = {
    "WEBSITE": "אתר פשוט שמביא פניות מגוגל",
    "REDESIGN": "אתר מהיר ומותאם לנייד שמביא יותר פניות",
    "AUTOMATION": "זימון תורים אונליין ותזכורות אוטומטיות בוואטסאפ",
}


def main_gap(lead: dict) -> str:
    signals = set(lead.get("signals") or [])
    return next((text for sig, text in GAPS if sig in signals), "יש מקום להביא לכם יותר פניות מהאינטרנט")


def _kind(lead: dict) -> str:
    t = lead.get("lead_type", "")
    if t.startswith("REDESIGN"):
        return "REDESIGN"
    return t if t in QUESTIONS else "WEBSITE"


def call_script(lead: dict) -> str:
    kind = _kind(lead)
    q1, q2 = QUESTIONS[kind]
    return "\n".join([
        f"1. פתיחה: \"היי, מדבר/ת [השם שלך]. אני מתקשר/ת כי ראיתי ש{main_gap(lead)}. "
        f"אפשר 30 שניות להסביר למה זה חשוב?\"",
        f"2. שאלה: \"{q1}\"",
        f"3. שאלה: \"{q2}\"",
        f"4. הצעה: \"אני עושה {BENEFIT[kind]} לעסקים כמו שלכם.\"",
        "5. צעד הבא: \"אפשר לשלוח לך בוואטסאפ דוגמה קצרה איך זה ייראה אצלכם?\"",
        "אם אומרים לא – להודות ולא לחזור שוב.",
    ])


def missed_message(lead: dict) -> str:
    kind = _kind(lead)
    return (f"היי, כאן [השם שלך]. ניסיתי להתקשר אליכם קודם – ראיתי ש{main_gap(lead)}, "
            f"ואני עושה {BENEFIT[kind]} לעסקים כמו שלכם. מתאים שאשלח דוגמה קצרה? "
            "אם לא רלוונטי, רק תגידו ולא אפנה שוב.")


@lru_cache(maxsize=1)
def _objections() -> list[dict]:
    return json.loads(OBJECTIONS.read_text(encoding="utf-8"))["objections"]


def objections_for(lead: dict) -> list[tuple[str, str]]:
    kind = _kind(lead)
    category, city = category_he(lead), city_he(lead)
    out = []
    for o in _objections():
        answer = o.get("by_type", {}).get(kind, o["a"])
        answer = answer.replace("{gap}", main_gap(lead)).replace("{category}", category).replace("{city}", city)
        out.append((o["q"], answer))
    return out


def fill(lead: dict) -> None:
    """Fill call_script_he / missed_he with templates where Claude hasn't written personal ones."""
    if not lead.get("call_script_he"):
        lead["call_script_he"] = call_script(lead)
        lead["call_script_auto"] = True
    if not lead.get("missed_he"):
        lead["missed_he"] = missed_message(lead)
        lead["missed_auto"] = True
