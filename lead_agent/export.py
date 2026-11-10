"""Write scored leads to JSON (working file), CSV (Excel-friendly UTF-8) and a formatted XLSX."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

from .paths import home

SEEN = "seen.csv"
STATUSES = ["contacted", "replied", "meeting", "won", "lost", "no_reply", "not_interested"]

COLUMNS = [
    ("success_pct", "success_% (estimate)", 12),
    ("band", "band", 7),
    ("lead_type", "lead_type", 20),
    ("name", "name", 26),
    ("category", "category", 20),
    ("phone", "phone", 15),
    ("website", "website", 28),
    ("facebook", "facebook", 22),
    ("instagram", "instagram", 22),
    ("email", "email", 22),
    ("verified", "verified_online", 10),
    ("address", "address", 26),
    ("why", "why", 48),
    ("why_he", "why (עברית)", 40),
    ("outreach_he", "outreach_he", 60),
    ("status", "status", 13),
    ("notes", "notes", 24),
    ("maps_link", "google_maps", 14),
    ("search_link", "google_search", 14),
    ("signals", "signals", 40),
    ("lead_id", "lead_id", 18),
]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "leads"


def add_links(lead: dict) -> None:
    q = quote_plus(f"{lead['name']} {lead.get('city', '')}")
    lead["maps_link"] = f"https://www.google.com/maps/search/?api=1&query={q}"
    lead["search_link"] = f"https://www.google.com/search?q={q}"
    lead["verified"] = "yes" if lead.get("enriched") else "no"


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
    paths = {"json": base.with_suffix(".json"), "csv": base.with_suffix(".csv"), "xlsx": base.with_suffix(".xlsx")}
    carry_over_edits(leads, paths["xlsx"], fresh)
    for lead in leads:
        add_links(lead)
    paths["json"].write_text(json.dumps({"meta": meta, "leads": leads}, ensure_ascii=False, indent=1),
                             encoding="utf-8")
    with paths["csv"].open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[c[0] for c in COLUMNS])
        w.writeheader()
        for lead in leads:
            w.writerow(row_values(lead))
    write_xlsx(leads, paths["xlsx"])
    return paths


def write_xlsx(leads: list[dict], path: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append([c[0] for c in COLUMNS])
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
            if key in ("why", "why_he", "outreach_he"):
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        band_fill = PatternFill("solid", fgColor=fills.get(lead.get("band"), "FFFFFF"))
        ws.cell(row=r, column=1).fill = band_fill
        ws.cell(row=r, column=2).fill = band_fill
    # Friendly headers; learn.py reads the "status", "signals" and "lead_id" columns, whose headers equal their keys.
    for c, (_, header, width) in enumerate(COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(c)].width = width
        ws.cell(row=1, column=c, value=header)
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = ws.dimensions
    status_col = get_column_letter([c[0] for c in COLUMNS].index("status") + 1)
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{status_col}2:{status_col}{max(len(leads) + 1, 2)}")

    info = wb.create_sheet("How to use")
    for line in [
        "success_% is an ESTIMATE of the chance this business becomes a paying client after personal outreach.",
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
