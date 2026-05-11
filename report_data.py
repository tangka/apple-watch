"""Data loading and aggregation layer for Apple Health CSVs."""
from __future__ import annotations

import csv, json, os
from collections import defaultdict
from datetime import date


def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, encoding="utf-8") as f: return list(csv.DictReader(f))

def flt(v):
    try: return float(v) if v not in ("", None, "None") else None
    except: return None

def load_data(data_dir):
    return dict(
        monthly  = load_csv(os.path.join(data_dir, "monthly_trends.csv")),
        daily    = load_csv(os.path.join(data_dir, "daily_metrics.csv")),
        workouts = load_csv(os.path.join(data_dir, "workouts.csv")),
        meta     = json.load(open(os.path.join(data_dir, "meta.json"), encoding="utf-8"))
                   if os.path.exists(os.path.join(data_dir, "meta.json")) else {},
    )

SPO2_FIELDS = {"spo2", "spo2_avg"}

# Sleep tracking requires sustained wrist contact through the night. Days with
# very short recorded sleep (< 1 h) almost always mean the watch was off the
# wrist for most of the night, not a real 17-minute "sleep" night. The 1 h
# threshold is intentionally conservative so that genuine insomnia nights
# (people who only sleep 1–2 hours) are still counted.
SLEEP_FIELDS = {"sleep_hours", "sleep_deep_h", "sleep_rem_h", "sleep_core_h", "sleep_awake_h"}
MIN_SLEEP_HOURS = 1.0


def scale(field, v):
    if v is not None and field in SPO2_FIELDS and v <= 1.5:
        return round(v * 100, 1)
    return v

def recent_avg(daily, field, days=90):
    rows = sorted(daily, key=lambda r: r["date"], reverse=True)[:days]
    # Drop watch-not-worn nights for any sleep-related metric.
    if field in SLEEP_FIELDS:
        rows = [r for r in rows if (flt(r.get("sleep_hours")) or 0) >= MIN_SLEEP_HOURS]
    vals = [scale(field, flt(r.get(field))) for r in rows]
    vals = [v for v in vals if v is not None and v > 0]
    return round(sum(vals)/len(vals), 1) if vals else None

def mo_series(monthly, field):
    labels, values = [], []
    for r in monthly:
        labels.append(r["period"])
        v = flt(r.get(field))
        values.append(scale(field, v))
    return labels, values

def compute_weekly_ex(monthly):
    _, values = [], []
    labels = []
    for r in monthly:
        total = flt(r.get("exercise_min_total"))
        days  = flt(r.get("exercise_min_days")) or flt(r.get("steps_days"))
        labels.append(r["period"])
        values.append(round(total / days * 7, 0) if total and days else None)
    return labels, values

def workout_summary(wo_rows):
    type_count = defaultdict(int)
    type_min   = defaultdict(float)
    total_min  = total_km = 0.0
    mo_count   = defaultdict(int)
    for r in wo_rows:
        t   = r.get("type","Unknown") or "Unknown"
        dur = flt(r.get("duration_min")) or 0
        km  = flt(r.get("distance_km"))  or 0
        type_count[t] += 1; type_min[t] += dur
        total_min += dur;   total_km += km
        mo = r.get("start","")[:7]
        if mo: mo_count[mo] += 1
    top = sorted(type_count.items(), key=lambda x:-x[1])[:8]
    return dict(
        total       = len(wo_rows),
        total_hours = round(total_min/60,1),
        total_km    = round(total_km,1),
        top_types   = [t for t,_ in top],
        top_counts  = [c for _,c in top],
        mo_labels   = sorted(mo_count),
        mo_counts   = [mo_count[k] for k in sorted(mo_count)],
    )
