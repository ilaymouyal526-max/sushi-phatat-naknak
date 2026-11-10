"""Turn a lead's data + website audit into signals, a success %, a band and plain reasons."""

from __future__ import annotations

import datetime as dt
import json
import math
from .paths import BASELINE, learned_weights

HIGH_VALUE = {
    "dentist", "clinic", "doctors", "veterinary", "optician", "hearing_aids", "hairdresser", "beauty",
    "massage", "spa", "tattoo", "cosmetics", "lawyer", "accountant", "estate_agent", "architect",
    "insurance", "tax_advisor", "notary", "financial", "fitness_centre", "dance", "dojo", "sports_centre",
    "restaurant", "cafe", "bakery", "pastry", "car_repair", "driving_school", "music_school",
    "language_school", "prep_school", "hotel", "guest_house", "florist", "furniture", "kitchen",
    "interior_decoration", "jewelry", "photo", "tailor", "locksmith", "bed", "curtain", "lighting",
}
HIGH_VALUE_KEYS = {"healthcare", "craft"}
LOW_VALUE = {
    "kiosk", "convenience", "atm", "vending_machine", "lottery", "newsagent", "e-cigarette", "tobacco",
    "supermarket", "pharmacy", "fuel", "charging_station",
}

REASONS = {
    "no_website": ("No own website found", "לא נמצא לעסק אתר אינטרנט"),
    "site_dead": ("Listed website is down", "האתר הרשום לא עובד"),
    "ssl_error": ("Website shows a security warning", "האתר מציג אזהרת אבטחה"),
    "no_https": ("Website is not secure (no HTTPS)", "האתר לא מאובטח (אין HTTPS)"),
    "no_mobile": ("Website is not mobile-friendly", "האתר לא מותאם לנייד"),
    "stale_site": ("Website looks outdated (old © year)", "האתר נראה לא מעודכן"),
    "slow_site": ("Website is slow to load", "האתר נטען לאט"),
    "free_builder": ("Runs on a free builder subdomain", "האתר על דומיין חינמי של בונה אתרים"),
    "no_booking_or_whatsapp": ("No online booking or WhatsApp button", "אין זימון תורים אונליין או כפתור וואטסאפ"),
    "no_contact_capture": ("No contact form / click-to-call", "אין טופס יצירת קשר או חיוג בלחיצה"),
    "has_phone": ("Has a phone number to call", "יש מספר טלפון"),
    "has_social": ("Active on social media", "פעיל ברשתות החברתיות"),
    "has_email": ("Has an email", "יש כתובת מייל"),
    "has_hours": ("Active business (hours listed)", "עסק פעיל"),
    "high_value_cat": ("High-value, booking-driven category", "תחום עם ערך גבוה ותורים"),
    "low_value_cat": ("Low-budget category", "תחום עם תקציב נמוך"),
    "modern_complete": ("Already has a modern site with booking/chat", "כבר יש אתר מודרני עם זימון/צ'אט"),
    "no_contact": ("No way to contact found", "לא נמצאה דרך ליצור קשר"),
}


def load_weights() -> dict:
    learned = learned_weights()
    path = learned if learned.exists() else BASELINE
    return json.loads(path.read_text(encoding="utf-8"))


def category_value(category: str) -> str:
    key, _, value = category.partition("=")
    if value in LOW_VALUE:
        return "low"
    if value in HIGH_VALUE or key in HIGH_VALUE_KEYS:
        return "high"
    return "neutral"


def extract_signals(lead: dict, today: dt.date | None = None) -> list[str]:
    today = today or dt.date.today()
    a = lead.get("audit") or {"site_status": "none"}
    status = a.get("site_status", "none")
    sig: list[str] = []
    site_up = status in ("ok", "ssl_error")
    site_exists = site_up or status in ("blocked", "unchecked")

    if not lead.get("website") or status == "none":
        sig.append("no_website")
    elif status in ("dead", "timeout"):
        sig.append("site_dead")
    if status == "ssl_error":
        sig.append("ssl_error")
    if site_up:
        if status == "ok" and not a.get("https", True):
            sig.append("no_https")
        if not a.get("has_viewport", True):
            sig.append("no_mobile")
        year = a.get("copyright_year")
        if year and year <= today.year - 3:
            sig.append("stale_site")
        if (a.get("load_seconds") or 0) > 4:
            sig.append("slow_site")
        if a.get("free_builder"):
            sig.append("free_builder")
        if not a.get("has_booking") and not a.get("has_whatsapp"):
            sig.append("no_booking_or_whatsapp")
        if not any(a.get(k) for k in ("has_form", "has_tel_link", "has_whatsapp", "has_chat")):
            sig.append("no_contact_capture")
        if (status == "ok" and a.get("https") and a.get("has_viewport")
                and (a.get("has_booking") or a.get("has_whatsapp") or a.get("has_chat"))
                and not (year and year <= today.year - 3)):
            sig.append("modern_complete")

    if lead.get("phone"):
        sig.append("has_phone")
    if lead.get("facebook") or lead.get("instagram"):
        sig.append("has_social")
    if lead.get("email"):
        sig.append("has_email")
    if lead.get("opening_hours"):
        sig.append("has_hours")
    value = category_value(lead.get("category", ""))
    if value == "high":
        sig.append("high_value_cat")
    elif value == "low":
        sig.append("low_value_cat")
    if not any(lead.get(k) for k in ("phone", "email", "facebook", "instagram")) and not site_exists:
        sig.append("no_contact")
    return sig


def contributions(signals: list[str], weights: dict) -> tuple[float, dict[str, float]]:
    """Return (log_odds, per-feature effective contribution) applying group caps."""
    feats = weights["features"]
    groups = weights.get("groups", {})
    contrib: dict[str, float] = {}
    group_sum: dict[str, float] = {}
    for s in signals:
        f = feats.get(s)
        if not f:
            continue
        contrib[s] = f["weight"]
        if f.get("group"):
            group_sum[f["group"]] = group_sum.get(f["group"], 0.0) + f["weight"]
    for g, total in group_sum.items():
        cap = groups.get(g, {}).get("cap")
        if cap is not None and total > cap:
            scale = cap / total
            for s in contrib:
                if feats[s].get("group") == g:
                    contrib[s] *= scale
    return weights["intercept"] + sum(contrib.values()), contrib


def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def lead_type(signals: list[str]) -> str:
    s = set(signals)
    if "no_website" in s:
        return "WEBSITE"
    redesign = s & {"site_dead", "ssl_error", "no_https", "no_mobile", "stale_site", "free_builder"}
    automation = s & {"no_booking_or_whatsapp", "no_contact_capture"}
    if redesign and automation:
        return "REDESIGN+AUTOMATION"
    if redesign:
        return "REDESIGN"
    if automation:
        return "AUTOMATION"
    return "LOW_FIT"


def score_lead(lead: dict, weights: dict | None = None) -> dict:
    weights = weights or load_weights()
    signals = extract_signals(lead)
    z, contrib = contributions(signals, weights)
    pct = round(100 * sigmoid(z), 1)
    bands = weights.get("bands", {"hot": 7.0, "warm": 3.5})
    band = "Hot" if pct >= bands["hot"] else "Warm" if pct >= bands["warm"] else "Cold"
    top = sorted((c for c in contrib.items() if c[1] > 0), key=lambda kv: -kv[1])[:3]
    neg = [k for k, v in contrib.items() if v < 0]
    why_keys = [k for k, _ in top] + neg[:1]
    lead.update({
        "signals": signals,
        "success_pct": pct,
        "band": band,
        "lead_type": lead_type(signals),
        "why": "; ".join(REASONS[k][0] for k in why_keys),
        "why_he": "; ".join(REASONS[k][1] for k in why_keys),
        "weights_version": weights.get("version", ""),
    })
    return lead


def score_all(leads: list[dict]) -> list[dict]:
    weights = load_weights()
    for lead in leads:
        score_lead(lead, weights)
    leads.sort(key=lambda l: -l["success_pct"])
    return leads
