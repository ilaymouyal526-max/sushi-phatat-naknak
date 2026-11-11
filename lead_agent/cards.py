"""Phone-friendly lead cards: one self-contained HTML file per run (no external scripts or fonts)."""

from __future__ import annotations

import html
import re
from urllib.parse import quote

BAND_LABEL = {"Hot": "🔥 Hot", "Warm": "Warm", "Cold": "Cold"}


def phone_e164(phone: str) -> str:
    """Israeli phone -> digits in international form without '+', e.g. '0546559181' -> '972546559181'."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("00972"):
        digits = digits[2:]
    if digits.startswith("972"):
        pass
    elif digits.startswith("0"):
        digits = "972" + digits[1:]
    elif len(digits) in (8, 9):
        digits = "972" + digits
    else:
        return ""
    return digits if 11 <= len(digits) <= 12 else ""


def is_mobile(e164: str) -> bool:
    """Israeli mobile numbers are 05x locally, i.e. 9725x internationally. Landlines can't get WhatsApp."""
    return e164.startswith("9725") and len(e164) == 12


def _safe_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.I):
        if re.match(r"^[\w.-]+\.[a-z]{2,}(/|$)", url, re.I):
            url = "https://" + url
        else:
            return ""
    return url


def _social_url(value: str, host: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.lower().startswith("http") or host in value.lower():
        return _safe_url(value)
    return f"https://www.{host}/{quote(value.lstrip('@'))}"


def _e(text) -> str:
    return html.escape("" if text is None else str(text))


def _card(lead: dict) -> str:
    band = lead.get("band", "Cold")
    e164 = phone_e164(lead.get("phone", ""))
    buttons = []
    if e164:
        buttons.append(f'<a class="btn call" href="tel:+{e164}">📞 Call · {_e(lead.get("phone"))}</a>')
        if is_mobile(e164):
            wa = f"https://wa.me/{e164}"
            if lead.get("outreach_he"):
                wa += "?text=" + quote(str(lead["outreach_he"]))
            buttons.append(f'<a class="btn wa" href="{_e(wa)}" target="_blank" rel="noopener">WhatsApp</a>')
    links = [
        ("Website", _safe_url(lead.get("website", ""))),
        ("Facebook", _social_url(lead.get("facebook", ""), "facebook.com")),
        ("Instagram", _social_url(lead.get("instagram", ""), "instagram.com")),
        ("Listing", _safe_url(lead.get("directory_page", ""))),
        ("Map", _safe_url(lead.get("maps_link", ""))),
    ]
    buttons += [f'<a class="btn" href="{_e(u)}" target="_blank" rel="noopener">{n}</a>' for n, u in links if u]

    category = (lead.get("category", "").split("=")[-1] or "").replace("_", " ")
    meta = " · ".join(_e(x) for x in [category, lead.get("address", "")] if x)
    reasons = "".join(f"<li>{_e(r.strip())}</li>" for r in str(lead.get("why_he", "")).split(";") if r.strip())
    opener = ""
    if lead.get("outreach_he"):
        opener = (f'<div class="opener"><div class="label">הודעת פתיחה · Opener</div>'
                  f'<p dir="rtl">{_e(lead["outreach_he"])}</p>'
                  f'<button type="button" class="copy">Copy</button></div>')
    verified = '<span class="tag ok">✓ verified online</span>' if lead.get("enriched") else \
        '<span class="tag">not verified yet</span>'
    notes = f'<p class="notes" dir="auto">{_e(lead["notes"])}</p>' if lead.get("notes") else ""
    return f"""
<article class="card" data-band="{_e(band)}">
  <header>
    <h2 dir="auto">{_e(lead.get("name"))}</h2>
    <span class="badge {_e(band.lower())}">{_e(BAND_LABEL.get(band, band))} · {_e(lead.get("success_pct"))}%</span>
  </header>
  <p class="meta" dir="auto">{meta}</p>
  <p class="sell"><span class="pill">{_e(lead.get("sell") or lead.get("lead_type"))}</span> {verified}</p>
  <ul class="why" dir="rtl">{reasons}</ul>
  {notes}
  {opener}
  <nav class="actions">{"".join(buttons) or '<span class="muted">No contact details found yet</span>'}</nav>
</article>"""


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--text:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#1d4ed8;
--hot:#fde2e1;--hot-t:#991b1b;--warm:#fef3c7;--warm-t:#92400e;--cold:#eef0f3;--cold-t:#374151;
--wa:#16a34a;--chip:#fff;--chip-on:#111827;--chip-on-t:#fff;--opener:#f1f5ff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1115;--card:#181b21;--text:#e5e7eb;
--muted:#9ca3af;--line:#2a2f37;--accent:#93b4ff;--hot:#4a1d1d;--hot-t:#fecaca;--warm:#45330f;--warm-t:#fde68a;
--cold:#262a31;--cold-t:#d1d5db;--wa:#22c55e;--chip:#181b21;--chip-on:#e5e7eb;--chip-on-t:#111827;--opener:#1c2433}}
:root[data-theme="dark"]{--bg:#0f1115;--card:#181b21;--text:#e5e7eb;--muted:#9ca3af;--line:#2a2f37;--accent:#93b4ff;
--hot:#4a1d1d;--hot-t:#fecaca;--warm:#45330f;--warm-t:#fde68a;--cold:#262a31;--cold-t:#d1d5db;--wa:#22c55e;
--chip:#181b21;--chip-on:#e5e7eb;--chip-on-t:#111827;--opener:#1c2433}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 system-ui,-apple-system,"Segoe UI",Arial,sans-serif}
main{max-width:720px;margin:0 auto;padding:16px}
h1{font-size:1.3rem;margin:4px 0}
.sub,.muted,.meta{color:var(--muted);font-size:.9rem}
.note{font-size:.85rem;color:var(--muted);border-left:3px solid var(--line);padding-left:10px;margin:10px 0}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 16px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:1}
.chips button{border:1px solid var(--line);background:var(--chip);color:var(--text);border-radius:999px;padding:8px 14px;font:inherit;font-size:.9rem}
.chips button[aria-pressed="true"]{background:var(--chip-on);color:var(--chip-on-t);border-color:var(--chip-on)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}
.card header{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.card h2{font-size:1.1rem;margin:0;overflow-wrap:anywhere}
.badge{white-space:nowrap;font-weight:700;font-size:.85rem;padding:4px 10px;border-radius:999px}
.badge.hot{background:var(--hot);color:var(--hot-t)}.badge.warm{background:var(--warm);color:var(--warm-t)}
.badge.cold{background:var(--cold);color:var(--cold-t)}
.meta{margin:4px 0 8px;overflow-wrap:anywhere}
.pill{display:inline-block;background:var(--cold);border-radius:6px;padding:2px 8px;font-size:.85rem}
.tag{font-size:.8rem;color:var(--muted);margin-left:6px}.tag.ok{color:var(--wa)}
.why{margin:8px 0;padding-right:20px;padding-left:0}
.notes{font-size:.9rem;color:var(--muted);margin:6px 0}
.opener{background:var(--opener);border-radius:10px;padding:10px 12px;margin:10px 0}
.opener .label{font-size:.75rem;color:var(--muted);margin-bottom:4px}
.opener p{margin:0 0 8px;white-space:pre-wrap}
.copy{font:inherit;font-size:.85rem;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:8px;padding:6px 12px}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.btn{display:inline-block;text-decoration:none;color:var(--accent);border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:.9rem}
.btn.call{background:var(--accent);color:var(--card);border-color:var(--accent);font-weight:600}
.btn.wa{background:var(--wa);color:#fff;border-color:var(--wa);font-weight:600}
footer{font-size:.8rem;color:var(--muted);margin:20px 0 40px}
"""

JS = """
const chips=[...document.querySelectorAll('.chips button')];
chips.forEach(b=>b.addEventListener('click',()=>{
  chips.forEach(c=>c.setAttribute('aria-pressed',String(c===b)));
  const f=b.dataset.filter;
  document.querySelectorAll('.card').forEach(c=>{c.hidden=!(f==='all'||c.dataset.band===f)});
}));
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
  const t=b.previousElementSibling.textContent;
  try{await navigator.clipboard.writeText(t);b.textContent='Copied ✓'}
  catch(e){const r=document.createRange();r.selectNodeContents(b.previousElementSibling);
    const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected, now copy'}
  setTimeout(()=>b.textContent='Copy',2000);
}));
"""


def render_cards(leads: list[dict], meta: dict) -> str:
    counts = {b: sum(1 for l in leads if l.get("band") == b) for b in ("Hot", "Warm", "Cold")}
    city = str(meta.get("city", "")).title()
    category = meta.get("category", "")
    created = str(meta.get("created", ""))[:10]
    chips = "".join(
        f'<button type="button" data-filter="{f}" aria-pressed="{str(f == "all").lower()}">{label}</button>'
        for f, label in [("all", f"All {len(leads)}"), ("Hot", f"🔥 Hot {counts['Hot']}"),
                         ("Warm", f"Warm {counts['Warm']}"), ("Cold", f"Cold {counts['Cold']}")])
    cards = "".join(_card(l) for l in leads)
    return f"""<!doctype html>
<html lang="he" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Leads · {_e(city)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
  <h1>Leads · {_e(city)}</h1>
  <p class="sub">{_e(category)} · {_e(created)} · {len(leads)} businesses</p>
  <p class="note">The % is an <b>estimate</b> of the chance a business becomes a paying client after one personal
  message or call (Hot ≥ 7%, Warm ≥ 3.5%). Send messages yourself, one at a time, and stop if they say no.</p>
  <div class="chips" role="group" aria-label="Filter by rating">{chips}</div>
  {cards}
  <footer>Made by lead_agent from free OpenStreetMap data and website checks. Leads marked “not verified yet”
  haven't been checked online, so confirm they have no website before pitching one.</footer>
</main>
<script>{JS}</script>
</body>
</html>
"""
