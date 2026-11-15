"""Command line: find / show / merge / learn.

  python -m lead_agent find "Tel Aviv" --category beauty --limit 50
  python -m lead_agent show leads/2026-11-10-tel-aviv-beauty.json --top 30
  python -m lead_agent merge leads/....json updates.json
  python -m lead_agent learn leads/....xlsx
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import audit, calls, cities, export, learn, osm, paths, plan, score

EDITABLE = {"phone", "website", "facebook", "instagram", "email", "opening_hours", "outreach_he", "notes",
            "status", "address", "call_script_he", "missed_he"}


def _print(obj) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


def _compact(lead: dict) -> dict:
    keys = ["lead_id", "name", "category", "city", "address", "phone", "email", "website", "facebook",
            "instagram", "directory_page", "enriched", "success_pct", "band", "lead_type", "why", "outreach_he",
            "opening_hours", "call_best", "call_avoid", "next_try"]
    out = {k: lead.get(k) for k in keys if lead.get(k) not in (None, "")}
    a = lead.get("audit") or {}
    if a.get("site_status") not in (None, "none"):
        out["site"] = {k: a[k] for k in ("site_status", "https", "has_viewport", "copyright_year",
                                         "has_booking", "has_whatsapp", "has_form", "load_seconds")
                       if k in a}
    return out


def cmd_find(args) -> int:
    if args.bbox:
        bbox = tuple(float(x) for x in args.bbox.split(","))
        city = args.city or "custom"
    else:
        city, bbox = cities.resolve_bbox(args.city)
    out_dir = Path(args.out_dir) if args.out_dir else paths.home()
    print(f"Searching OpenStreetMap: {city} / {args.category} …", file=sys.stderr)
    leads, stats = osm.find_businesses(bbox, args.category, city)
    seen = set() if args.include_seen else export.load_seen(out_dir)
    before = len(leads)
    leads = [l for l in leads if l["lead_id"] not in seen]
    stats["skipped_already_delivered"] = before - len(leads)
    dnc = calls.load_dnc()
    before = len(leads)
    leads = [l for l in leads if not calls.is_dnc(l, dnc)]
    stats["skipped_do_not_contact"] = before - len(leads)
    with_site = sum(1 for l in leads if l.get("website"))
    if args.no_audit:
        for l in leads:
            l["audit"] = {"site_status": "unchecked"} if l.get("website") else {"site_status": "none"}
    else:
        print(f"Checking {with_site} websites …", file=sys.stderr)
        audit.audit_many(leads)
    score.score_all(leads)
    leads = leads[: args.limit]
    stats.update({"websites_checked": with_site, "delivered": len(leads),
                  "hot": sum(l["band"] == "Hot" for l in leads),
                  "warm": sum(l["band"] == "Warm" for l in leads)})
    base = out_dir / f"{dt.date.today().isoformat()}-{export.slug(city)}-{export.slug(args.category)}"
    meta = {"city": city, "category": args.category, "bbox": bbox, "created": dt.datetime.now().isoformat(),
            "stats": stats, "weights_version": score.load_weights().get("version")}
    files = export.write_all(leads, base, meta)
    export.mark_seen(out_dir, [l["lead_id"] for l in leads])
    _print({"files": {k: str(v) for k, v in files.items()}, "stats": stats,
            "top": [_compact(l) for l in leads[: args.show]]})
    return 0


def _load_run(path: Path) -> tuple[dict, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["meta"], data["leads"]


def cmd_show(args) -> int:
    _, leads = _load_run(Path(args.run))
    if args.needs_enrichment:
        leads = [l for l in leads if not l.get("phone") or not (l.get("website") or l.get("facebook")
                                                                   or l.get("instagram"))]
    if args.band:
        leads = [l for l in leads if l.get("band", "").lower() in args.band.lower().split(",")]
    _print([_compact(l) for l in leads[: args.top]])
    return 0


def cmd_merge(args) -> int:
    run_path = Path(args.run)
    meta, leads = _load_run(run_path)
    updates = json.loads(Path(args.updates).read_text(encoding="utf-8"))
    if isinstance(updates, list):
        updates = {u["lead_id"]: u for u in updates}
    by_id = {l["lead_id"]: l for l in leads}
    reaudit, changed, unknown, fresh = [], 0, [], {}
    for lead_id, fields in updates.items():
        lead = by_id.get(lead_id)
        if not lead:
            unknown.append(lead_id)
            continue
        for k, v in fields.items():
            if k in EDITABLE and v not in (None, ""):
                if k == "website" and v != lead.get("website"):
                    reaudit.append(lead)
                lead[k] = v
                fresh.setdefault(lead_id, set()).add(k)
                if k in ("call_script_he", "missed_he"):
                    lead.pop("call_script_auto" if k == "call_script_he" else "missed_auto", None)
        lead["enriched"] = True
        changed += 1
    for lead in reaudit:
        lead["audit"] = audit.audit_site(lead["website"])
    score.score_all(leads)
    meta.setdefault("stats", {})["enriched"] = sum(1 for l in leads if l.get("enriched"))
    files = export.write_all(leads, run_path.with_suffix(""), meta, fresh)
    _print({"updated": changed, "websites_rechecked": len(reaudit), "unknown_ids": unknown,
            "files": {k: str(v) for k, v in files.items()},
            "top": [_compact(l) for l in leads[: args.show]]})
    return 0


def _refresh_runs(lead_ids: set[str]) -> list[str]:
    """Rewrite the sheets/pages of runs containing these leads so attempts / next try / status update."""
    done = []
    for p in sorted(paths.home().glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(data, dict) or "leads" not in data:
            continue
        if any(l.get("lead_id") in lead_ids for l in data["leads"]):
            export.write_all(data["leads"], p.with_suffix(""), data.get("meta", {}))
            done.append(str(p.with_suffix(".xlsx")))
    return done


def cmd_log(args) -> int:
    if args.action == "add":
        at = calls.parse_time(args.at) if args.at else None
        cb = calls.parse_time(args.callback) if args.callback else None
        row = calls.add(args.lead_id, args.result, at=at, callback_at=cb, note=args.note or "")
        lead, _ = calls.find_lead(args.lead_id)
        fu = calls.follow_up(lead or {"lead_id": args.lead_id},
                             calls.history_by_lead().get(args.lead_id, []))
        _print({"logged": row, "next": fu["text"], "updated": _refresh_runs({args.lead_id})})
    elif args.action == "import":
        before = {r["lead_id"] for r in calls.load()}
        added, dup = calls.import_file(Path(args.file))
        ids = {r["lead_id"] for r in calls.load()} | before
        _print({"imported": added, "duplicates_skipped": dup, "updated": _refresh_runs(ids)})
    else:
        hist = calls.history_by_lead()
        stats = calls.personal_stats()
        _print({"leads_called": len(hist), "calls": sum(len(h) for h in hist.values()),
                "do_not_contact": sum(1 for x in calls.load_dnc() if not x.startswith("phone:")),
                "personal_best_hours": {k: v["top"] for k, v in stats.items() if v.get("top")},
                "recent": calls.load()[-10:]})
    return 0


def cmd_plan(args) -> int:
    import datetime as dt
    day = dt.date.fromisoformat(args.date) if args.date else calls.now_il().date()
    result = plan.build(day, max_calls=args.max)
    if not result["entries"] and result["day_note"]:
        nxt = plan.next_workday(day)
        _print({"date": day.isoformat(), "no_calls": result["day_note"], "next_workday": nxt.isoformat()})
        if not args.date:
            result = plan.build(nxt, max_calls=args.max)
        else:
            return 0
    files = plan.write(result)
    _print({"date": result["date"].isoformat(), "calls": len(result["entries"]), "not_fitted": result["skipped"],
            "blocks": [f"{b['start']:%H:%M}-{b['end']:%H:%M} ({len(b['entries'])})" for b in result["blocks"]],
            "files": {k: str(v) for k, v in files.items()},
            "schedule": [{"time": f"{e['time']:%H:%M}", "kind": e["kind"], "name": e["lead"]["name"],
                          "phone": e["lead"].get("phone"), "band": e["lead"].get("band"),
                          "why": (e["lead"].get("why_he") or "").split(";")[0]} for e in result["entries"]]})
    return 0


def cmd_learn(args) -> int:
    _print(learn.learn(Path(args.file) if args.file else None))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lead_agent", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("find", help="find, audit and score businesses in a city")
    f.add_argument("city", nargs="?", default="", help='city name in English or Hebrew, e.g. "Tel Aviv"')
    f.add_argument("--category", default="all",
                   help="all | " + " | ".join(osm.CATEGORY_GROUPS) + " | raw OSM value (e.g. dentist); comma-separated ok")
    f.add_argument("--limit", type=int, default=150, help="max leads in the output (best first)")
    f.add_argument("--bbox", help="south,west,north,east instead of a city")
    f.add_argument("--include-seen", action="store_true", help="include leads delivered in earlier runs")
    f.add_argument("--no-audit", action="store_true", help="skip website checks (fast, less accurate)")
    f.add_argument("--out-dir", default=None, help="default: ./leads or $LEAD_AGENT_HOME")
    f.add_argument("--show", type=int, default=10, help="how many top leads to print")
    f.set_defaults(func=cmd_find)

    s = sub.add_parser("show", help="print leads from a run file")
    s.add_argument("run")
    s.add_argument("--top", type=int, default=30)
    s.add_argument("--band", help="Hot,Warm,Cold filter")
    s.add_argument("--needs-enrichment", action="store_true", help="only leads missing phone or web presence")
    s.set_defaults(func=cmd_show)

    m = sub.add_parser("merge", help="merge enrichment / outreach drafts into a run and rescore")
    m.add_argument("run")
    m.add_argument("updates", help="JSON: {lead_id: {phone, website, facebook, instagram, email, outreach_he, notes}}")
    m.add_argument("--show", type=int, default=10)
    m.set_defaults(func=cmd_merge)

    l = sub.add_parser("learn", help="ingest won/lost statuses from a lead sheet and recalibrate")
    l.add_argument("file", nargs="?", help="leads .xlsx or .csv with the status column filled")
    l.set_defaults(func=cmd_learn)

    lg = sub.add_parser("log", help="record calls: add / import / show")
    lsub = lg.add_subparsers(dest="action", required=True)
    la = lsub.add_parser("add", help="log one call")
    la.add_argument("lead_id")
    la.add_argument("result", choices=calls.RESULTS)
    la.add_argument("--at", help='when (Israel time), e.g. "2026-11-17 10:20"; default now')
    la.add_argument("--callback", help='for call_back: when to call again, e.g. "2026-11-18 15:30" or "15:30"')
    la.add_argument("--note")
    li = lsub.add_parser("import", help="import the call log exported from the phone page")
    li.add_argument("file")
    lsub.add_parser("show", help="summary of logged calls and your best hours")
    lg.set_defaults(func=cmd_log)

    pl = sub.add_parser("plan", help="daily call plan (HTML + calendar .ics)")
    pl.add_argument("--date", help="YYYY-MM-DD (default: today, or the next working day)")
    pl.add_argument("--max", type=int, default=25, help="max calls in the plan")
    pl.set_defaults(func=cmd_plan)

    args = p.parse_args(argv)
    if args.cmd == "find" and not args.city and not args.bbox:
        p.error("find needs a city or --bbox")
    return args.func(args)
