"""Write scored leads to JSON (working file), CSV, a formatted XLSX and a phone-friendly HTML cards page."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

from .cards import render_cards

SEEN = "seen.csv"
STATUSES = ["contacted", "replied", "meeting", "won", "lost", "no_reply", "not_interested"]

# (key, header, width). Order is phone-first: what you need to act on comes before technical detail.
# The headers "outreach_he", "status", "notes", "signals" and "lead_id" are read back by name
# (carry_over_edits, learn.read_lead_file), so keep them exactly as they are.
COLUMNS = [
    ("name", "name / שם", 22),
    ("phone", "phone / טלפון", 15),
    ("rating", "rating / דירוג", 13),
    ("sell", "what to sell / מה למכור", 20),
    ("why_he", "why / למה", 40),
    ("outreach_he", "outreach_he", 55),
    ("website", "website", 26),
    ("facebook", "facebook", 22),
    ("instagram", "instagram", 22),
    ("email", "email", 22),
    ("address", "address / כתובת", 24),
    ("verified", "verified_online", 10),
    ("status", "status", 13),
    ("notes", "notes", 24),
    ("maps_link", "google_maps", 12),
    ("search_link", "google_search", 12),
    ("why", "why (English)", 44),
    ("category", "category", 20),
    ("success_pct", "success_pct", 11),
    ("band", "band", 7),
    ("signals", "signals", 36),
    ("lead_id", "lead_id", 18),
]

SELL_LABELS = {
    "WEBSITE": "אתר חדש · New website",
    "REDESIGN": "שדרוג אתר · Redesign",
    "AUTOMATION": "אוטומציה · Automation",
    "REDESIGN+AUTOMATION": "שדרוג + אוטומציה · Redesign + automation",
    "LOW_FIT": "התאמה נמוכה · Low fit",
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "leads"


def add_links(lead: dict) -> None:
    q = quote_plus(f"{lead['name']} {lead.get('city', '')}")
    lead["maps_link"] = f"https://www.google.com/maps/search/?api=1&query={q}"
    lead["search_link"] = f"https://www.google.com/search?q={q}"
    lead["verified"] = "yes" if lead.get("enriched") else "no"
    lead["rating"] = f"{lead.get('band', '')} · {lead.get('success_pct', 0)}%"
    lead["sell"] = SELL_LABELS.get(lead.get("lead_type", ""), lead.get("lead_type", ""))


def row_values(lead: dict) -> dict:
    out = {}
    for key, _, _ in COLUMNS:
        v = lead.get(key, "")
        out[key] = ",".join(v) if isinstance(v, list) else ("" if v is None else v)
    return out


def load_seen(directory: Path) -> set[str]:
    p = directory / SEEN
    if not p.exists():
        return set()
    return {line.strip() for line in p.read_text(encoding="utf-8").splitlines()[1:] if line.strip()}


def mark_seen(directory: Path, ids: list[str]) -> None:
    p = directory / SEEN
    existing = load_seen(directory)
    new = [i for i in ids if i not in existing]
    if not p.exists():
        p.write_text("lead_id\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        for i in new:
            f.write(i + "\n")


HAND_EDITED = ("status", "notes", "outreach_he")


def carry_over_edits(leads: list[dict], xlsx: Path, fresh: dict[str, set] | None = None) -> None:
    """Keep what you typed into an existing sheet (status, notes, edited outreach) when it is rewritten.

    `fresh` lists {lead_id: {fields}} that were just updated on purpose (e.g. by merge); those win.
    """
    fresh = fresh or {}
    if not xlsx.exists():
        return
    from openpyxl import load_workbook
    ws = load_workbook(xlsx, read_only=True).active
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[0]) if rows else []
    if "lead_id" not in header:
        return
    idx = {k: header.index(k) for k in HAND_EDITED if k in header}
    typed = {}
    for r in rows[1:]:
        lead_id = r[header.index("lead_id")]
        typed[lead_id] = {k: r[i] for k, i in idx.items() if r[i] not in (None, "")}
    for lead in leads:
        for k, v in typed.get(lead["lead_id"], {}).items():
            if k not in fresh.get(lead["lead_id"], set()):
                lead[k] = v


def write_all(leads: list[dict], base: Path, meta: dict, fresh: dict[str, set] | None = None) -> dict[str, Path]:
    base.parent.mkdir(parents=True, exist_ok=True)
    paths = {"json": base.with_suffix(".json"), "csv": base.with_suffix(".csv"), "xlsx": base.with_suffix(".xlsx"),
             "html": base.with_suffix(".html")}
    carry_over_edits(leads, paths["xlsx"], fresh)
    for lead in leads:
        add_links(lead)
    paths["json"].write_text(json.dumps({"meta": meta, "leads": leads}, ensure_ascii=False, indent=1),
                             encoding="utf-8")
    with paths["csv"].open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([c[1] for c in COLUMNS])
        for lead in leads:
            vals = row_values(lead)
            w.writerow([vals[c[0]] for c in COLUMNS])
    write_xlsx(leads, paths["xlsx"])
    paths["html"].write_text(render_cards(leads, meta), encoding="utf-8")
    return paths


WRAP = {"name", "sell", "why_he", "outreach_he", "address", "notes", "why"}


def write_xlsx(leads: list[dict], path: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append([c[1] for c in COLUMNS])
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F2937")
    fills = {"Hot": "FDE2E1", "Warm": "FEF3C7", "Cold": "F3F4F6"}
    link_cols = {"website", "facebook", "instagram", "maps_link", "search_link"}
    for r, lead in enumerate(leads, start=2):
        vals = row_values(lead)
        for c, (key, _, _) in enumerate(COLUMNS, start=1):
            v = vals[key]
            cell = ws.cell(row=r, column=c, value=v)
            if key in link_cols and v:
                url = v if str(v).startswith("http") else "https://" + str(v)
                cell.hyperlink = url
                cell.font = Font(color="1D4ED8", underline="single")
                if key in ("maps_link", "search_link"):
                    cell.value = "open"
            cell.alignment = Alignment(wrap_text=key in WRAP, vertical="top")
            if key == "rating":
                cell.fill = PatternFill("solid", fgColor=fills.get(lead.get("band"), "FFFFFF"))
                cell.font = Font(bold=True)
            elif key == "name":
                cell.font = Font(bold=True)
        ws.row_dimensions[r].height = 90 if vals["outreach_he"] else 48
    ws.row_dimensions[1].height = 30
    for c, (_, _, width) in enumerate(COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(c)].width = width
        ws.cell(row=1, column=c).alignment = Alignment(wrap_text=True, vertical="center")
    # Freeze only the header row and the name column: on a phone everything else can still scroll into view.
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    status_col = get_column_letter([c[0] for c in COLUMNS].index("status") + 1)
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{status_col}2:{status_col}{max(len(leads) + 1, 2)}")

    info = wb.create_sheet("How to use")
    for line in [
        "On a phone? Open the .html file from the same run instead: one card per lead with call/WhatsApp buttons.",
        "rating / success_pct is an ESTIMATE of the chance this business becomes a paying client after personal outreach.",
        "Hot >= 7%, Warm >= 3.5%. Baseline from published outreach benchmarks; improves as you log results.",
        "1. Contact Hot leads first, one at a time (call or one-to-one WhatsApp). Never bulk-send.",
        "2. Fill the status column: contacted / replied / meeting / won / lost / no_reply / not_interested.",
        "3. Run:  python -m lead_agent learn <this file>   (or /find-leads learn <file>) to recalibrate.",
        "Israeli spam law (Communications Law s.30A): send a single, personal opener asking if they're interested;",
        "stop immediately if they say no. Not legal advice.",
    ]:
        info.append([line])
    info.column_dimensions["A"].width = 120
    wb.save(path)
