"""
Apple Health export parser — stream-parses the export XML (1–2 GB) from a zip or directory.

Apple's exported ZIP and XML are named according to the iPhone's locale
(e.g. export.zip / 导出.zip / etc.). The parser doesn't care about names:
pass any locale's ZIP via --zip, and find_xml_in_dir() will pick up the
right .xml after extraction (skipping export_cda.xml).

Usage:
    python health_parser.py --zip ~/Downloads/<your-export>.zip --out ./output
    python health_parser.py --xml ./apple_health_export/<your-export>.xml --out ./output
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import time
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import iterparse


# ------------------------------------------------------------------ CLI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(SCRIPT_DIR, "latest_parsed")
DEFAULT_RAW = os.path.join(SCRIPT_DIR, "latest_raw")

def parse_args():
    p = argparse.ArgumentParser(description="Parse Apple Health export")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--zip", metavar="PATH", help="Path to Apple Health export zip")
    src.add_argument("--xml", metavar="PATH", help="Path to already-extracted export XML")
    p.add_argument("--out", metavar="DIR", default=DEFAULT_OUT,
                   help=f"Output directory for CSV/JSON files (default: {DEFAULT_OUT})")
    p.add_argument("--raw", metavar="DIR", default=DEFAULT_RAW,
                   help=f"Directory to extract zip into (default: {DEFAULT_RAW})")
    p.add_argument("--all-sources", action="store_true",
                   help="Include all data sources (default: Apple Watch only)")
    return p.parse_args()


# ------------------------------------------------------------------ unzip

SKIP_SUFFIX = "export_cda.xml"

def find_xml_in_dir(directory: str) -> str | None:
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".xml") and not f.endswith(SKIP_SUFFIX):
                return os.path.join(root, f)
    return None

def extract_zip(zip_path: str, dst: str) -> str:
    """Extract zip, return path to export XML."""
    os.makedirs(dst, exist_ok=True)
    t0 = time.time()
    extracted = 0
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        for info in infos:
            raw = info.filename
            if info.flag_bits & 0x800:
                name = raw
            else:
                try:
                    name = raw.encode("cp437").decode("utf-8")
                except UnicodeError:
                    try:
                        name = raw.encode("cp437").decode("gbk")
                    except UnicodeError:
                        name = raw
            if name.endswith(SKIP_SUFFIX):
                continue
            target = os.path.realpath(os.path.join(dst, name))
            if not target.startswith(os.path.realpath(dst) + os.sep):
                continue  # zip slip guard
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                while chunk := src.read(1024 * 1024):
                    out.write(chunk)
            extracted += 1
    print(f"extracted {extracted} files in {time.time()-t0:.1f}s → {dst}")
    xml = find_xml_in_dir(dst)
    if not xml:
        sys.exit(f"ERROR: no export XML found in {dst}")
    return xml


# ------------------------------------------------------------------ helpers

def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z")

def is_watch(source_name: str, device: str | None) -> bool:
    s = (source_name or "").lower()
    d = (device or "").lower()
    return "watch" in s or "watch" in d or "手表" in (source_name or "")

def floatish(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ metric maps

CUMULATIVE = {
    "HKQuantityTypeIdentifierStepCount":              "steps",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance_km",
    "HKQuantityTypeIdentifierActiveEnergyBurned":     "active_energy_kcal",
    "HKQuantityTypeIdentifierBasalEnergyBurned":      "basal_energy_kcal",
    "HKQuantityTypeIdentifierFlightsClimbed":         "flights",
    "HKQuantityTypeIdentifierAppleExerciseTime":      "exercise_min",
    "HKQuantityTypeIdentifierAppleStandTime":         "stand_min",
}
AVERAGED = {
    "HKQuantityTypeIdentifierHeartRate":                   "heart_rate_bpm",
    "HKQuantityTypeIdentifierRestingHeartRate":            "resting_hr_bpm",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage":     "walking_hr_bpm",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN":    "hrv_sdnn_ms",
    "HKQuantityTypeIdentifierVO2Max":                      "vo2_max",
    "HKQuantityTypeIdentifierBodyMass":                    "body_mass_kg",
    "HKQuantityTypeIdentifierOxygenSaturation":            "spo2",
    "HKQuantityTypeIdentifierRespiratoryRate":             "respiratory_rate",
    "HKQuantityTypeIdentifierBodyTemperature":             "body_temp_c",
    "HKQuantityTypeIdentifierEnvironmentalAudioExposure":  "env_audio_db",
    "HKQuantityTypeIdentifierHeadphoneAudioExposure":      "hp_audio_db",
}
SLEEP_TYPE = "HKCategoryTypeIdentifierSleepAnalysis"


# ------------------------------------------------------------------ parse

def parse_xml(xml_path: str, watch_only: bool, out_dir: str):
    day_sum: dict[tuple, float] = defaultdict(float)
    day_vals: dict[tuple, list] = defaultdict(list)
    sleep_nights: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    workouts: list[dict] = []
    source_counts: dict[str, int] = defaultdict(int)

    def sleep_bucket(v: str) -> str:
        return v.replace("HKCategoryValueSleepAnalysis", "")

    def night_key(edt: datetime) -> str:
        return edt.strftime("%Y-%m-%d")

    print(f"parsing {xml_path} ({os.path.getsize(xml_path)/1e9:.2f} GB)")
    t0 = time.time()
    n_rec = n_wo = 0
    me_profile: dict = {}

    ctx = iterparse(xml_path, events=("end",))
    for _, elem in ctx:
        tag = elem.tag
        if tag == "Record":
            n_rec += 1
            a = elem.attrib
            source = a.get("sourceName", "")
            device = a.get("device") or ""
            rtype = a.get("type", "")
            source_counts[source] += 1

            if watch_only and not is_watch(source, device):
                elem.clear(); continue

            sd = a.get("startDate")
            ed = a.get("endDate") or sd
            if not sd:
                elem.clear(); continue
            try:
                sdt = parse_dt(sd); edt = parse_dt(ed)
            except ValueError:
                elem.clear(); continue

            date_str = sdt.strftime("%Y-%m-%d")

            if rtype in CUMULATIVE:
                v = floatish(a.get("value"))
                if v is not None:
                    day_sum[(CUMULATIVE[rtype], date_str)] += v
            elif rtype in AVERAGED:
                v = floatish(a.get("value"))
                if v is not None:
                    day_vals[(AVERAGED[rtype], date_str)].append(v)
            elif rtype == SLEEP_TYPE:
                bucket = sleep_bucket(a.get("value", ""))
                secs = (edt - sdt).total_seconds()
                if secs > 0:
                    sleep_nights[night_key(edt)][bucket] += secs
            elem.clear()

        elif tag == "Workout":
            n_wo += 1
            a = elem.attrib
            source = a.get("sourceName", "")
            device = a.get("device") or ""
            if watch_only and not is_watch(source, device):
                elem.clear(); continue
            try:
                sdt = parse_dt(a["startDate"]); edt = parse_dt(a["endDate"])
            except (KeyError, ValueError):
                elem.clear(); continue

            distance_km = floatish(a.get("totalDistance"))
            distance_unit = a.get("totalDistanceUnit", "")
            energy_kcal = floatish(a.get("totalEnergyBurned"))
            energy_unit = a.get("totalEnergyBurnedUnit", "")
            for child in elem.findall("WorkoutStatistics"):
                ctype = child.attrib.get("type", "")
                csum = floatish(child.attrib.get("sum"))
                cunit = child.attrib.get("unit", "")
                if csum is None: continue
                if ctype in ("HKQuantityTypeIdentifierDistanceWalkingRunning",
                             "HKQuantityTypeIdentifierDistanceCycling"):
                    distance_km = (distance_km or 0) + csum
                    distance_unit = cunit or distance_unit
                elif ctype == "HKQuantityTypeIdentifierActiveEnergyBurned":
                    energy_kcal = (energy_kcal or 0) + csum
                    energy_unit = cunit or energy_unit
            workouts.append({
                "type": a.get("workoutActivityType", "").replace("HKWorkoutActivityType", ""),
                "start": sdt.strftime("%Y-%m-%d %H:%M:%S"),
                "end":   edt.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_min": round(floatish(a.get("duration")) or (edt-sdt).total_seconds()/60, 2),
                "distance_km":  round(distance_km, 3) if distance_km is not None else "",
                "distance_unit": distance_unit,
                "energy_kcal":  round(energy_kcal, 1) if energy_kcal is not None else "",
                "energy_unit":  energy_unit,
                "source": source,
            })
            elem.clear()
        elif tag == "Me":
            dob = elem.attrib.get("HKCharacteristicTypeIdentifierDateOfBirth", "")
            sex_raw = elem.attrib.get("HKCharacteristicTypeIdentifierBiologicalSex", "")
            blood_raw = elem.attrib.get("HKCharacteristicTypeIdentifierBloodType", "")
            if dob:      me_profile["date_of_birth"]   = dob
            if sex_raw:  me_profile["biological_sex"]  = sex_raw.replace("HKBiologicalSex","").lower()
            if blood_raw:me_profile["blood_type"]      = blood_raw.replace("HKBloodType","")
            elem.clear()
        elif tag == "ExportDate":
            elem.clear()

        if n_rec % 500_000 == 0 and n_rec:
            print(f"  …{n_rec:,} records, {n_wo:,} workouts, {time.time()-t0:.0f}s")

    print(f"parse done: {n_rec:,} records, {n_wo:,} workouts in {time.time()-t0:.1f}s")

    # ---- daily roll-up
    daily: dict[str, dict] = defaultdict(dict)
    for (m, d), s in day_sum.items():
        daily[d][m] = round(s, 3)
    for (m, d), vs in day_vals.items():
        daily[d][m] = round(statistics.mean(vs), 3) if vs else None

    for d, buckets in sleep_nights.items():
        asleep = sum(buckets.get(k, 0) for k in
                     ("Asleep","AsleepCore","AsleepDeep","AsleepREM","AsleepUnspecified"))
        daily[d]["sleep_hours"]    = round(asleep / 3600, 3)
        daily[d]["sleep_in_bed_h"] = round(buckets.get("InBed", 0) / 3600, 3)
        daily[d]["sleep_deep_h"]   = round(buckets.get("AsleepDeep", 0) / 3600, 3)
        daily[d]["sleep_rem_h"]    = round(buckets.get("AsleepREM", 0) / 3600, 3)
        daily[d]["sleep_core_h"]   = round(buckets.get("AsleepCore", 0) / 3600, 3)
        daily[d]["sleep_awake_h"]  = round(buckets.get("Awake", 0) / 3600, 3)

    dates = sorted(daily)
    date_range = (dates[0], dates[-1]) if dates else (None, None)
    print(f"daily date range: {date_range[0]} → {date_range[1]}  ({len(dates)} days)")

    # ---- monthly / yearly aggregates
    AVG_METRICS = [
        ("steps",              "steps"),
        ("sleep_hours",        "sleep"),
        ("sleep_deep_h",       "sleep_deep"),
        ("sleep_rem_h",        "sleep_rem"),
        ("sleep_core_h",       "sleep_core"),
        ("sleep_awake_h",      "sleep_awake"),
        ("resting_hr_bpm",     "rhr"),
        ("walking_hr_bpm",     "walk_hr"),
        ("hrv_sdnn_ms",        "hrv"),
        ("vo2_max",            "vo2"),
        ("spo2",               "spo2"),
        ("respiratory_rate",   "resp"),
        ("active_energy_kcal", "active_kcal"),
        ("distance_km",        "distance"),
        ("body_mass_kg",       "weight"),
    ]
    SUM_METRICS = [
        ("exercise_min", "exercise_min"),
    ]

    # Sleep tracking requires sustained overnight wear. Days with < 1 h recorded
    # sleep usually mean the watch was off the wrist. Threshold is conservative
    # so genuine insomnia nights (1–2 h actual sleep) are still counted.
    SLEEP_COLS = {"sleep_hours","sleep_deep_h","sleep_rem_h","sleep_core_h","sleep_awake_h"}
    MIN_SLEEP_HOURS = 1.0

    def aggregate(period_fn):
        bucket: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        bucket_sum: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for d in dates:
            p = period_fn(d)
            row = daily[d]
            night_worn = (row.get("sleep_hours") or 0) >= MIN_SLEEP_HOURS
            for col, key in AVG_METRICS:
                v = row.get(col)
                if v is not None and v > 0:
                    if col in SLEEP_COLS and not night_worn:
                        continue
                    bucket[p][key].append(v)
            for col, key in SUM_METRICS:
                v = row.get(col)
                if v is not None and v > 0:
                    bucket_sum[p][key] += v
                    bucket[p][f"{key}_days"].append(1)

        rows = []
        for p in sorted(set(list(bucket.keys()) + list(bucket_sum.keys()))):
            b = bucket[p]
            bs = bucket_sum[p]
            def avg(xs): return round(sum(xs)/len(xs), 2) if xs else None
            row = {"period": p}
            for _, key in AVG_METRICS:
                row[f"{key}_avg"]  = avg(b[key])
                row[f"{key}_days"] = len(b[key])
            for _, key in SUM_METRICS:
                row[f"{key}_total"] = round(bs[key], 1) if bs[key] else None
                row[f"{key}_days"]  = len(b[f"{key}_days"])
            rows.append(row)
        return rows

    monthly = aggregate(lambda d: d[:7])
    yearly  = aggregate(lambda d: d[:4])

    # ---- write outputs
    os.makedirs(out_dir, exist_ok=True)

    def write_csv(path, rows, fields):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows: w.writerow(r)
        print(f"wrote {path} ({len(rows)} rows)")

    trend_fields = (
        ["period"] +
        [f"{key}_{suffix}" for _, key in AVG_METRICS for suffix in ("avg", "days")] +
        [f"{key}_{suffix}" for _, key in SUM_METRICS for suffix in ("total", "days")]
    )
    write_csv(os.path.join(out_dir, "monthly_trends.csv"), monthly, trend_fields)
    write_csv(os.path.join(out_dir, "yearly_trends.csv"),  yearly,  trend_fields)

    # Daily wide table
    all_metric_cols = sorted({c for d in dates for c in daily[d]})
    with open(os.path.join(out_dir, "daily_metrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date"] + all_metric_cols)
        for d in dates:
            w.writerow([d] + [daily[d].get(c, "") for c in all_metric_cols])
    print(f"wrote daily_metrics.csv ({len(dates)} days × {len(all_metric_cols)} metrics)")

    # Workouts
    workouts_sorted = sorted(workouts, key=lambda x: x["start"])
    write_csv(os.path.join(out_dir, "workouts.csv"), workouts_sorted,
              ["type","start","end","duration_min","distance_km","distance_unit",
               "energy_kcal","energy_unit","source"])

    # Sleep
    sleep_rows = []
    for d in sorted(sleep_nights):
        b = sleep_nights[d]
        asleep = sum(b.get(k,0) for k in
                     ("Asleep","AsleepCore","AsleepDeep","AsleepREM","AsleepUnspecified"))
        sleep_rows.append({
            "night_date": d,
            "in_bed_h": round(b.get("InBed",0)/3600, 2),
            "asleep_h": round(asleep/3600, 2),
            "deep_h":   round(b.get("AsleepDeep",0)/3600, 2),
            "rem_h":    round(b.get("AsleepREM",0)/3600, 2),
            "core_h":   round(b.get("AsleepCore",0)/3600, 2),
            "awake_h":  round(b.get("Awake",0)/3600, 2),
        })
    write_csv(os.path.join(out_dir, "sleep.csv"), sleep_rows,
              ["night_date","in_bed_h","asleep_h","deep_h","rem_h","core_h","awake_h"])

    # Sources QA
    with open(os.path.join(out_dir, "sources.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_name", "record_count"])
        for s, c in sorted(source_counts.items(), key=lambda x: -x[1]):
            w.writerow([s, c])
    print(f"wrote sources.csv ({len(source_counts)} sources)")

    # Meta JSON
    meta = {
        "generated_at": datetime.now().isoformat(),
        "source_filter": "Apple Watch only" if watch_only else "all sources",
        "date_range": {"start": date_range[0], "end": date_range[1]},
        "total_days": len(dates),
        "total_workouts": len(workouts_sorted),
        "xml_path": xml_path,
        "out_dir": out_dir,
        "profile": me_profile,
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"wrote meta.json")
    print(f"\nALL DONE in {time.time()-t0:.1f}s → {out_dir}")
    return out_dir


# ------------------------------------------------------------------ main

def main():
    args = parse_args()
    out_dir = os.path.abspath(args.out)

    if args.zip:
        raw_dir  = os.path.abspath(args.raw)
        xml_path = extract_zip(os.path.abspath(args.zip), raw_dir)
    else:
        xml_path = os.path.abspath(args.xml)
        if not os.path.exists(xml_path):
            sys.exit(f"ERROR: XML not found: {xml_path}")

    parse_xml(xml_path, watch_only=not args.all_sources, out_dir=out_dir)


if __name__ == "__main__":
    main()
