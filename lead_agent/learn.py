"""Recalibrate weights from your real outcomes.

Each outcome is (signals, won?). We fit the same capped logistic model by gradient descent, with an
L2 penalty pulling every weight back toward the research baseline. With few outcomes the baseline
dominates; with ~100+ your own results dominate.
"""

from __future__ import annotations

import copy
import csv
import datetime as dt
import json
from pathlib import Path

from .paths import BASELINE, learned_weights, outcomes as outcomes_path
from .score import contributions, sigmoid
WON = {"won", "closed", "client", "נסגר", "לקוח"}
LOST = {"lost", "no_reply", "not_interested", "no", "לא מעוניין", "לא ענה"}
PRIOR_STRENGTH = 8.0  # roughly "the baseline is worth this many outcomes per weight"


def label_for(status: str) -> int | None:
    s = (status or "").strip().lower()
    if s in WON:
        return 1
    if s in LOST:
        return 0
    return None  # contacted / replied / meeting / empty: still open


def read_lead_file(path: Path) -> list[dict]:
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True).active
        rows = list(ws.iter_rows(values_only=True))
        header = [str(h or "") for h in rows[0]]
        return [{header[i]: ("" if v is None else str(v)) for i, v in enumerate(r)} for r in rows[1:]]
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_outcomes() -> dict[str, dict]:
    path = outcomes_path()
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {r["lead_id"]: r for r in csv.DictReader(f)}


def save_outcomes(rows: dict[str, dict]) -> None:
    path = outcomes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lead_id", "signals", "label", "status", "date"])
        w.writeheader()
        for r in rows.values():
            w.writerow(r)


def ingest(path: Path) -> tuple[int, int]:
    """Add closed leads (won/lost) from a lead sheet to outcomes.csv. Returns (added_or_updated, open)."""
    outcomes = load_outcomes()
    changed = still_open = 0
    for row in read_lead_file(path):
        label = label_for(row.get("status", ""))
        if row.get("status") and label is None:
            still_open += 1
        if label is None or not row.get("lead_id"):
            continue
        outcomes[row["lead_id"]] = {
            "lead_id": row["lead_id"],
            "signals": row.get("signals", ""),
            "label": str(label),
            "status": row["status"].strip().lower(),
            "date": dt.date.today().isoformat(),
        }
        changed += 1
    save_outcomes(outcomes)
    return changed, still_open


def fit(samples: list[tuple[list[str], int]], baseline: dict, steps: int = 3000, lr: float = 0.05) -> dict:
    w = copy.deepcopy(baseline)
    feats = w["features"]
    names = list(feats)
    prior = {n: baseline["features"][n]["weight"] for n in names}
    prior_b = baseline["intercept"]
    lam = PRIOR_STRENGTH
    n = max(len(samples), 1)
    for _ in range(steps):
        grad = {k: 0.0 for k in names}
        grad_b = 0.0
        for signals, y in samples:
            z, contrib = contributions(signals, w)
            err = sigmoid(z) - y
            grad_b += err
            group_sum: dict[str, float] = {}
            for s in contrib:
                g = feats[s].get("group")
                if g:
                    group_sum[g] = group_sum.get(g, 0.0) + feats[s]["weight"]
            for s in contrib:
                g = feats[s].get("group")
                cap = w.get("groups", {}).get(g, {}).get("cap") if g else None
                if cap is not None and group_sum[g] > cap:
                    continue  # capped: this weight does not move the score
                grad[s] += err
        grad_b += lam * (w["intercept"] - prior_b) / 1.0
        w["intercept"] -= lr * grad_b / n
        for k in names:
            g = grad[k] + lam * (feats[k]["weight"] - prior[k])
            feats[k]["weight"] -= lr * g / n
    for k in names:
        feats[k]["weight"] = round(feats[k]["weight"], 4)
    w["intercept"] = round(w["intercept"], 4)
    return w


def learn(path: Path | None = None) -> dict:
    added, still_open = ingest(path) if path else (0, 0)
    outcomes = load_outcomes()
    samples = [([s for s in r["signals"].split(",") if s], int(r["label"])) for r in outcomes.values()]
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    wins = sum(y for _, y in samples)
    report = {"ingested": added, "still_open": still_open, "outcomes": len(samples), "wins": wins}
    if len(samples) < 5 or wins == 0:
        report["note"] = "Need at least 5 closed outcomes including 1 win before recalibrating; baseline still in use."
        return report
    learned = fit(samples, baseline)
    learned["version"] = f"learned-{dt.date.today().isoformat()}-n{len(samples)}"
    learned_weights().write_text(json.dumps(learned, ensure_ascii=False, indent=2), encoding="utf-8")
    observed = wins / len(samples)
    report.update({
        "observed_win_rate_pct": round(100 * observed, 1),
        "baseline_prior_pct": round(100 * sigmoid(baseline["intercept"]), 2),
        "new_prior_pct": round(100 * sigmoid(learned["intercept"]), 2),
        "biggest_changes": sorted(
            ((k, round(learned["features"][k]["weight"] - baseline["features"][k]["weight"], 3))
             for k in baseline["features"]), key=lambda kv: -abs(kv[1]))[:5],
        "saved": str(learned_weights()),
    })
    return report
