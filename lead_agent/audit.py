"""Check a business's own website for the gaps a website/automation seller can fix."""

from __future__ import annotations

import datetime as dt
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; lead-agent/0.1; website quality check)",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
}

BOOKING_PATTERNS = re.compile(
    r"calendly\.com|setmore\.com|simplybook|booksy\.com|fresha\.com|vagaro\.com|acuityscheduling|"
    r"tor4you|mytor|easy\.co\.il/.*(?:book|tor)|meetings\.hubspot|square\.site/book|zimmer|"
    r"tabit\.cloud|ontopo|rest\.co\.il|10bis|wolt\.com|mishloha|"
    r"bookingtor|appointlet|youcanbook\.me|picktime|zcal\.co|cal\.com/",
    re.I,
)
BOOKING_TEXT = re.compile(
    r"קביעת תור|לקביעת תור|הזמנת תור|זימון תור|הזמן תור|הזמנת שולחן|הזמנת מקום|"
    r"book (?:now|online|an appointment)|book a table|schedule (?:an )?appointment|order online",
    re.I,
)
WHATSAPP = re.compile(r"wa\.me/|api\.whatsapp\.com|whatsapp://|web\.whatsapp\.com/send|chat\.whatsapp", re.I)
CHAT_WIDGETS = re.compile(
    r"tawk\.to|intercom|crisp\.chat|tidio|livechatinc|manychat|zendesk|drift\.com|hubspot.*conversations|"
    r"elfsight.*whatsapp|getbutton\.io|smartsupp|chatra|botpress|landbot",
    re.I,
)
ANALYTICS = re.compile(r"googletagmanager\.com|google-analytics\.com|gtag\(|fbq\(|clarity\.ms|hotjar", re.I)
FREE_BUILDER_HOSTS = re.compile(
    r"\.wixsite\.com|\.business\.site|sites\.google\.com|\.wordpress\.com|\.weebly\.com|\.blogspot\.|"
    r"\.godaddysites\.com|\.square\.site|\.webnode\.|\.jimdosite\.com|\.mozello\.|\.site123\.me|\.ucoz\.",
    re.I,
)
COPYRIGHT = re.compile(r"(?:©|&copy;|copyright|כל הזכויות שמורות)[^0-9]{0,40}((?:19|20)\d{2})(?:\s*[-–]\s*((?:19|20)\d{2}))?",
                       re.I)


def normalise_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url.lstrip("/")
    return url


def analyse_html(html: str, final_url: str) -> dict:
    """Pure function: extract quality/automation signals from page HTML (tested offline)."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    hrefs = " ".join(a.get("href", "") for a in soup.find_all("a"))
    srcs = " ".join(t.get("src", "") for t in soup.find_all(["script", "iframe"]))
    blob = " ".join([hrefs, srcs, html[:400_000]])

    years = []
    for m in COPYRIGHT.finditer(text):
        years += [int(y) for y in m.groups() if y]
    this_year = dt.date.today().year
    years = [y for y in years if 1995 <= y <= this_year]

    generator = soup.find("meta", attrs={"name": re.compile("^generator$", re.I)})
    viewport = soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)})
    return {
        "has_viewport": viewport is not None,
        "copyright_year": max(years) if years else None,
        "has_booking": bool(BOOKING_PATTERNS.search(blob) or BOOKING_TEXT.search(text)),
        "has_whatsapp": bool(WHATSAPP.search(blob)),
        "has_tel_link": "tel:" in hrefs.lower(),
        "has_form": soup.find("form") is not None,
        "has_chat": bool(CHAT_WIDGETS.search(blob)),
        "has_analytics": bool(ANALYTICS.search(blob)),
        "free_builder": bool(FREE_BUILDER_HOSTS.search(final_url)),
        "generator": (generator.get("content", "") if generator else "")[:60],
        "title": (soup.title.string.strip() if soup.title and soup.title.string else "")[:120],
    }


def audit_site(url: str, timeout: float = 12.0) -> dict:
    """Fetch the site and return signals. site_status: ok | blocked | dead | ssl_error | timeout | none."""
    url = normalise_url(url)
    if not url:
        return {"site_status": "none"}
    candidates = [url]
    if url.lower().startswith("https://"):
        candidates.append("http://" + url[8:])
    last_status = "dead"
    for i, candidate in enumerate(candidates):
        start = time.monotonic()
        try:
            resp = requests.get(candidate, headers=HEADERS, timeout=timeout, allow_redirects=True)
        except requests.exceptions.SSLError:
            # Certificate problem on https. Try plain http to see if the site exists at all.
            last_status = "ssl_error"
            continue
        except requests.exceptions.Timeout:
            last_status = "timeout" if last_status != "ssl_error" else last_status
            continue
        except requests.RequestException:
            if last_status not in ("ssl_error", "timeout"):
                last_status = "dead"
            continue
        elapsed = time.monotonic() - start
        if resp.status_code in (401, 403, 429, 503):
            # Bot protection (e.g. Cloudflare): the site exists, we just can't inspect it.
            return {"site_status": "blocked", "final_url": resp.url, "http_status": resp.status_code}
        if resp.status_code >= 400:
            last_status = "dead" if last_status != "ssl_error" else last_status
            continue
        ctype = resp.headers.get("content-type", "")
        result = analyse_html(resp.text if "html" in ctype or not ctype else "", resp.url)
        result.update({
            "site_status": "ssl_error" if last_status == "ssl_error" else "ok",
            "https": resp.url.lower().startswith("https://"),
            "load_seconds": round(elapsed, 2),
            "final_url": resp.url,
        })
        return result
    return {"site_status": last_status}


def audit_many(leads: list[dict], workers: int = 8) -> None:
    """Audit every lead's website in place (adds lead['audit'])."""
    todo = [lead for lead in leads if lead.get("website")]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for lead, result in zip(todo, pool.map(lambda l: audit_site(l["website"]), todo)):
            lead["audit"] = result
    for lead in leads:
        lead.setdefault("audit", {"site_status": "none"})
