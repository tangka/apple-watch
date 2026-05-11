"""
Generate a self-contained HTML health report from parsed Apple Health CSVs.

Usage:
    python report_html.py --data ./output --out ./output/health_report.html

Visual style: Pudding.cool editorial narrative × GitHub Octoverse dark-neon.
Evidence-based benchmarks: AHA, WHO, AASM, ACSM, ESC.
"""
from __future__ import annotations

import argparse, csv, json, os, sys
from collections import defaultdict
from datetime import datetime, date


# ─────────────────────────────────────────── CLI ──

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, metavar="DIR")
    p.add_argument("--out",  metavar="PATH")
    return p.parse_args()


# ─────────────────────────────────────────── Benchmarks ──

BENCHMARKS = {
    "steps": {
        "label": "Daily Steps",  "unit": "steps/day",
        "accent": "#22d3ee",
        "levels": [(10000,None,"Highly Active","#4ade80"),(7500,9999,"Active","#86efac"),
                   (5000,7499,"Somewhat Active","#facc15"),(2500,4999,"Low Active","#fb923c"),
                   (0,2499,"Sedentary","#f87171")],
        "note": "≥7,000 steps/day → 50–70% lower all-cause mortality (Paluch 2022). AHA target: ≥10,000.",
        "source": "Paluch et al., JAMA Netw Open 2022; AHA",
        "url": "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2783711",
    },
    "exercise_min_week": {
        "label": "Exercise Min / Week",  "unit": "min/wk",
        "accent": "#22d3ee",
        "levels": [(150,None,"Meets Guidelines","#4ade80"),(75,149,"Partially Active","#facc15"),
                   (0,74,"Below Guidelines","#f87171")],
        "note": "≥150 min/wk moderate OR ≥75 min/wk vigorous + strength ×2/wk. Apple Watch Exercise Min = brisk-walk pace or above.",
        "source": "WHO 2020 Physical Activity Guidelines; AHA 2018",
        "url": "https://www.who.int/publications/i/item/9789240015128",
    },
    "resting_hr_bpm": {
        "label": "Resting Heart Rate",  "unit": "bpm",
        "accent": "#f472b6",
        "lower_is_better": True,
        "levels": [(0,59.9,"Athletic","#4ade80"),(60,70.9,"Optimal","#86efac"),
                   (71,85.9,"Normal","#a3e635"),(86,100.9,"Elevated","#facc15"),
                   (101,None,"Tachycardia","#f87171")],
        "note": "Normal: 60–100 bpm (AHA). Optimal zone 60–70 bpm is linked to lowest CV mortality risk.",
        "source": "AHA; Jouven et al., NEJM 2005",
        "url": "https://www.heart.org/en/health-topics/heart-rate",
    },
    "walking_hr_bpm": {
        "label": "Walking Heart Rate",  "unit": "bpm",
        "accent": "#fb7185",
        "lower_is_better": True,
        "levels": [(0,90.9,"Fit","#4ade80"),(91,110.9,"Average","#facc15"),
                   (111,None,"High","#f87171")],
        "note": "Lower walking HR reflects better aerobic fitness. Apple Watch records this during everyday walking throughout the day.",
        "source": "AHA; ACSM",
        "url": "https://www.heart.org/en/health-topics/heart-rate",
    },
    "hrv_sdnn_ms": {
        "label": "HRV — SDNN",  "unit": "ms",
        "accent": "#f472b6",
        "levels": [(50,None,"Good","#4ade80"),(30,49.9,"Fair","#facc15"),
                   (0,29.9,"Low","#f87171")],
        "note": "Higher SDNN = better autonomic balance. Trend matters more than absolute. Depressed by poor sleep, overtraining, alcohol, and stress.",
        "source": "ESC/NASPE Task Force, Eur Heart J 1996; Shaffer & Ginsberg, Front Public Health 2017",
        "url": "https://www.frontiersin.org/articles/10.3389/fpubh.2017.00258/full",
    },
    "vo2_max": {
        "label": "VO₂ Max",  "unit": "mL/kg/min",
        "accent": "#4ade80",
        "levels": [(48,None,"Excellent","#4ade80"),(42,47.9,"Good","#86efac"),
                   (37,41.9,"Fair","#facc15"),(33,36.9,"Poor","#fb923c"),
                   (0,32.9,"Very Poor","#f87171")],
        "note": "AHA/ACSM categories for adults ~40–49 (male ref; women ~10% lower). Apple Watch estimates indirectly. Low CRF is a major independent CV risk factor (AHA).",
        "source": "Ross et al., Circulation 2016; ACSM",
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000461",
    },
    "sleep_hours": {
        "label": "Sleep Duration",  "unit": "hrs/night",
        "accent": "#a78bfa",
        "levels": [(7,9,"Recommended","#4ade80"),(6,6.99,"Borderline","#facc15"),
                   (9,None,"Long Sleep","#facc15"),(0,5.99,"Insufficient","#f87171")],
        "note": "AASM/SRS: 7–9 hrs for adults. <7 hrs → elevated risk of obesity, diabetes, hypertension, and all-cause mortality.",
        "source": "Watson et al., Sleep 2015 (AASM/SRS); NSF 2015",
        "url": "https://aasm.org/seven-or-more-hours-of-sleep-per-night-a-health-necessity-for-adults/",
    },
    "sleep_deep_h": {
        "label": "Deep Sleep (N3)",  "unit": "hrs",
        "accent": "#818cf8",
        "levels": [(1.0,None,"Good","#4ade80"),(0.5,0.99,"Fair","#facc15"),
                   (0,0.49,"Low","#f87171")],
        "note": "N3 (slow-wave) = 13–23% of total sleep (~1.0–1.7 h for 7–8 h). Critical for physical restoration and immune function.",
        "source": "AASM Staging; Hirshkowitz et al., Sleep Health 2015",
        "url": "https://pubmed.ncbi.nlm.nih.gov/29073398/",
    },
    "sleep_rem_h": {
        "label": "REM Sleep",  "unit": "hrs",
        "accent": "#c084fc",
        "levels": [(1.5,None,"Good","#4ade80"),(0.8,1.49,"Fair","#facc15"),
                   (0,0.79,"Low","#f87171")],
        "note": "REM = 20–25% of total sleep (~1.5–2.0 h). Critical for memory consolidation and emotional regulation. Suppressed by alcohol and some medications.",
        "source": "AASM; Hirshkowitz et al., Sleep Health 2015",
        "url": "https://pubmed.ncbi.nlm.nih.gov/29073398/",
    },
    "spo2": {
        "label": "Blood Oxygen (SpO₂)",  "unit": "%",
        "accent": "#38bdf8",
        "levels": [(95,None,"Normal","#4ade80"),(90,94.9,"Borderline","#facc15"),
                   (0,89.9,"Low","#f87171")],
        "note": "Normal SpO₂ is 95–100% at sea level. SpO₂ <90% = hypoxemia, warrants medical evaluation (AHA/ATS).",
        "source": "AHA; ATS Statement; AASM",
        "url": "https://www.thoracic.org/statements/",
    },
    "respiratory_rate": {
        "label": "Respiratory Rate",  "unit": "br/min",
        "accent": "#38bdf8",
        "levels": [(12,19.9,"Normal","#4ade80"),(20,24.9,"Elevated","#facc15"),
                   (0,11.9,"Low","#facc15"),(25,None,"High","#f87171")],
        "note": "Normal resting rate: 12–20 breaths/min. Apple Watch measures during sleep.",
        "source": "AHA; NICE Clinical Guidelines",
        "url": "https://www.heart.org/",
    },
}


# ─────────────────────────────────────────── Helpers ──

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

def scale(field, v):
    if v is not None and field in SPO2_FIELDS and v <= 1.5:
        return round(v * 100, 1)
    return v

def recent_avg(daily, field, days=90):
    vals = [scale(field, flt(r.get(field)))
            for r in sorted(daily, key=lambda r: r["date"], reverse=True)[:days]]
    vals = [v for v in vals if v is not None and v > 0]
    return round(sum(vals)/len(vals), 1) if vals else None

def get_status(value, key):
    if value is None: return "No Data", "#475569"
    for lo, hi, label, color in BENCHMARKS.get(key, {}).get("levels", []):
        lo = lo if lo is not None else float("-inf")
        hi = hi if hi is not None else float("inf")
        if lo <= value <= hi: return label, color
    return "—", "#475569"

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

def js(v):
    if v is None:           return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, list): return "["+",".join(js(x) for x in v)+"]"
    if isinstance(v, str):  return '"'+v.replace('"','\\"')+'"'
    return str(v)

def fmt_num(v, decimals=1):
    if v is None: return "—"
    if decimals == 0: return f"{int(round(v)):,}"
    return f"{v:.{decimals}f}"


# ─────────────────────────────────────────── Insight generator ──

def make_insight(key, value, avgs=None):
    """Return (headline, detail, color) for editorial callout."""
    if value is None: return None
    label, color = get_status(value, key)
    bm = BENCHMARKS.get(key, {})

    if key == "steps":
        target = 7000
        diff = int(value - target)
        sign = "above" if diff >= 0 else "below"
        return (f"{fmt_num(value,0)} steps/day",
                f"That's {abs(diff):,} steps {sign} the 7,000-step threshold associated with 50–70% lower mortality risk (Paluch 2022).",
                color)

    if key == "exercise_min_week":
        target = 150
        met = value >= target
        return (f"{fmt_num(value,0)} min/week",
                f"{'Meets' if met else 'Below'} the WHO/AHA recommendation of ≥150 min/week of moderate-intensity activity.",
                color)

    if key == "resting_hr_bpm":
        return (f"{fmt_num(value,0)} bpm resting HR",
                f"AHA normal range: 60–100 bpm. Your value is in the '{label}' zone.",
                color)

    if key == "hrv_sdnn_ms":
        return (f"{fmt_num(value,0)} ms SDNN",
                f"HRV reflects autonomic nervous system balance. Higher = better. Trend over months is more informative than any single value.",
                color)

    if key == "vo2_max":
        return (f"{fmt_num(value,1)} mL/kg/min VO₂max",
                f"AHA/ACSM fitness category: '{label}'. True improvement requires sustained moderate-to-vigorous aerobic training.",
                color)

    if key == "sleep_hours":
        target_lo, target_hi = 7, 9
        if value < target_lo:
            return (f"{fmt_num(value,1)} hrs/night",
                    f"AASM recommends 7–9 hrs for adults. You're averaging {target_lo - value:.1f} hrs short of the minimum.",
                    color)
        return (f"{fmt_num(value,1)} hrs/night",
                f"Within the AASM-recommended 7–9 hr window. Consistent sleep timing matters as much as duration.",
                color)

    return (f"{fmt_num(value,1)} {bm.get('unit','')}",
            f"Status: {label} ({bm.get('source','')})",
            color)


# ─────────────────────────────────────────── HTML builder ──

def build_html(d):
    monthly    = d["monthly"]
    daily      = d["daily"]
    wo_rows    = d["workouts"]
    meta       = d["meta"]

    date_start = meta.get("date_range",{}).get("start","")
    date_end   = meta.get("date_range",{}).get("end","")
    total_days = meta.get("total_days", len(daily))
    generated  = meta.get("generated_at", datetime.now().isoformat())[:10]

    avgs = {k: recent_avg(daily, k, 90) for k in [
        "steps","resting_hr_bpm","walking_hr_bpm","hrv_sdnn_ms","vo2_max",
        "sleep_hours","sleep_deep_h","sleep_rem_h","sleep_core_h",
        "spo2","respiratory_rate","exercise_min","active_energy_kcal",
        "distance_km","body_mass_kg","sleep_awake_h",
    ]}
    # Weekly exercise
    weekly_ex = defaultdict(float)
    for r in sorted(daily, key=lambda x: x["date"], reverse=True)[:90]:
        v = flt(r.get("exercise_min"))
        if v:
            iso = date.fromisoformat(r["date"]).isocalendar()
            weekly_ex[f"{iso[0]}-{iso[1]:02d}"] += v
    avgs["exercise_min_week"] = round(sum(weekly_ex.values())/len(weekly_ex),0) if weekly_ex else None

    wo = workout_summary(wo_rows)

    # Monthly series
    mo_labels, mo_steps      = mo_series(monthly, "steps_avg")
    _, mo_sleep              = mo_series(monthly, "sleep_avg")
    _, mo_sleep_deep         = mo_series(monthly, "sleep_deep_avg")
    _, mo_sleep_rem          = mo_series(monthly, "sleep_rem_avg")
    _, mo_sleep_core         = mo_series(monthly, "sleep_core_avg")
    _, mo_rhr                = mo_series(monthly, "rhr_avg")
    _, mo_walk_hr            = mo_series(monthly, "walk_hr_avg")
    _, mo_hrv                = mo_series(monthly, "hrv_avg")
    _, mo_vo2                = mo_series(monthly, "vo2_avg")
    _, mo_spo2               = mo_series(monthly, "spo2_avg")
    _, mo_resp               = mo_series(monthly, "resp_avg")
    _, mo_dist               = mo_series(monthly, "distance_avg")
    _, mo_kcal               = mo_series(monthly, "active_kcal_avg")
    _, mo_weight             = mo_series(monthly, "weight_avg")
    _, mo_ex_weekly          = compute_weekly_ex(monthly)

    mo_short = [m[2:] for m in mo_labels]
    has_weight = any(v and v > 0 for v in mo_weight)

    # Build insight callouts
    def insight_html(key, value):
        r = make_insight(key, value, avgs)
        if not r: return ""
        head, detail, color = r
        return f"""<div class="insight" style="--accent:{color}">
  <div class="insight-head">{head}</div>
  <div class="insight-body">{detail}</div>
</div>"""

    # Stat card
    def stat_card(key, value, decimals=1, label_override=None):
        bm     = BENCHMARKS.get(key,{})
        title  = label_override or bm.get("label", key)
        unit   = bm.get("unit","")
        accent = bm.get("accent","#94a3b8")
        _, color = get_status(value, key)
        val_str = fmt_num(value, decimals)
        status, _  = get_status(value, key)
        src    = bm.get("source","")
        url    = bm.get("url","#")
        note   = bm.get("note","")[:100]+"…" if len(bm.get("note",""))>100 else bm.get("note","")
        return f"""<div class="stat-card" style="--accent:{accent}">
  <div class="sc-title">{title}</div>
  <div class="sc-value" style="color:{accent}">{val_str}</div>
  <div class="sc-unit">{unit}</div>
  <div class="sc-badge" style="color:{color};border-color:{color}44;background:{color}11">{status}</div>
  <div class="sc-note">{note}</div>
  <div class="sc-src"><a href="{url}" target="_blank">{src[:52]}</a></div>
</div>"""

    # Benchmark table
    def bm_block(key):
        bm = BENCHMARKS.get(key,{})
        rows = "".join(
            f'<tr><td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c};margin-right:6px;vertical-align:middle"></span>{lbl}</td>'
            f'<td style="color:#94a3b8">{lo}{"–"+str(hi) if hi else "+"} {bm.get("unit","")}</td></tr>'
            for lo,hi,lbl,c in bm.get("levels",[])
        )
        return f"""<div class="bm-block">
  <div class="bm-title">{bm.get("label",key)}</div>
  <table class="bm-tbl"><tbody>{rows}</tbody></table>
  <p class="bm-note">{bm.get("note","")}</p>
  <p class="bm-src">📎 <a href="{bm.get('url','#')}" target="_blank">{bm.get('source','')}</a></p>
</div>"""

    # Chart wrapper
    def chart(cid, title, height=130):
        return f"""<div class="chart-box">
  <div class="chart-title">{title}</div>
  <canvas id="{cid}" height="{height}"></canvas>
</div>"""

    # Section header
    def sec(icon, title, accent):
        return f'<div class="sec-head" style="--accent:{accent}"><span class="sec-icon">{icon}</span>{title}</div>'

    # Embed icon as base64 favicon
    import base64 as _b64
    _icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.svg")
    if os.path.exists(_icon_path):
        _icon_b64 = _b64.b64encode(open(_icon_path, "rb").read()).decode()
        _favicon  = f"data:image/svg+xml;base64,{_icon_b64}"
        _icon_img = f'<img src="{_favicon}" width="40" height="40" style="border-radius:8px;flex-shrink:0">'
    else:
        _favicon  = ""
        _icon_img = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Apple Health · {date_start} – {date_end}</title>
{"<link rel='icon' href='" + _favicon + "'>" if _favicon else ""}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#070d1a;
  --bg2:#0d1526;
  --surface:rgba(255,255,255,.04);
  --surface2:rgba(255,255,255,.07);
  --border:rgba(255,255,255,.08);
  --text:#e2e8f0;
  --muted:#64748b;
  --dim:#334155;
  --grid:rgba(255,255,255,.05);
  --radius:12px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);
  line-height:1.55;font-size:14px;overflow-x:hidden}}
a{{color:#7dd3fc;text-decoration:none}}
a:hover{{text-decoration:underline}}

/* ── HERO ── */
.hero{{
  position:relative;overflow:hidden;
  background:linear-gradient(160deg,#0a0f1e 0%,#0d1a3a 40%,#130d2e 100%);
  padding:56px 32px 48px;border-bottom:1px solid var(--border);
}}
.hero::before{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 50% at 70% 40%,rgba(99,102,241,.18) 0%,transparent 70%),
             radial-gradient(ellipse 40% 60% at 20% 80%,rgba(34,211,238,.10) 0%,transparent 60%);
  pointer-events:none;
}}
.hero-inner{{position:relative;max-width:1060px;margin:0 auto}}
.hero-eyebrow{{font-family:'Space Grotesk',sans-serif;font-size:.72rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:#7dd3fc;margin-bottom:14px}}
.hero h1{{font-family:'Space Grotesk',sans-serif;font-size:clamp(2rem,4vw,3rem);
  font-weight:700;line-height:1.1;
  background:linear-gradient(135deg,#e2e8f0 30%,#7dd3fc 70%,#a78bfa 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:10px}}
.hero-sub{{color:var(--muted);font-size:.88rem;margin-bottom:32px}}

/* Hero key stats strip */
.hero-strip{{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));
  gap:1px;background:var(--border);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;max-width:700px}}
.hs-cell{{background:var(--surface2);padding:14px 16px}}
.hs-val{{font-family:'JetBrains Mono',monospace;font-size:1.35rem;font-weight:600;
  line-height:1;color:#f1f5f9}}
.hs-lbl{{font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);margin-top:4px}}

/* ── WRAPPER ── */
.wrap{{max-width:1060px;margin:0 auto;padding:40px 24px 80px}}

/* ── SECTION ── */
.section{{margin-top:56px}}
.sec-head{{display:flex;align-items:center;gap:10px;
  font-family:'Space Grotesk',sans-serif;font-size:1.15rem;font-weight:700;
  color:#f1f5f9;padding-bottom:12px;
  border-bottom:1px solid var(--border);margin-bottom:24px;
  position:relative}}
.sec-head::after{{content:'';position:absolute;bottom:-1px;left:0;width:48px;
  height:2px;background:var(--accent);border-radius:2px}}
.sec-icon{{font-size:1.1rem}}

/* ── INSIGHT CALLOUT (Pudding-style editorial) ── */
.insight{{
  border-left:3px solid var(--accent);
  background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 8%,transparent),transparent 60%);
  padding:14px 20px;border-radius:0 var(--radius) var(--radius) 0;
  margin-bottom:20px;
}}
.insight-head{{font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:700;
  color:var(--accent);line-height:1.15;margin-bottom:6px}}
.insight-body{{font-size:.82rem;color:#94a3b8;line-height:1.5}}

/* ── STAT CARDS ── */
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));
  gap:12px;margin-bottom:24px}}
.stat-card{{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px 14px;
  position:relative;overflow:hidden;min-width:0;
  transition:border-color .2s;
}}
.stat-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:var(--accent);
}}
.stat-card:hover{{border-color:color-mix(in srgb,var(--accent) 40%,var(--border))}}
.sc-title{{font-size:.68rem;font-weight:600;text-transform:uppercase;
  letter-spacing:.05em;color:var(--muted);margin-bottom:8px}}
.sc-value{{
  font-family:'JetBrains Mono',monospace;
  font-size:clamp(1.35rem,5cqi,1.9rem);
  font-weight:600;line-height:1;
  white-space:nowrap;overflow:hidden;
}}
.sc-unit{{
  display:block;font-family:'Inter',sans-serif;
  font-size:.7rem;font-weight:400;color:var(--muted);margin-top:4px;
}}
.sc-badge{{display:inline-block;font-size:.67rem;font-weight:600;
  padding:2px 8px;border-radius:99px;border:1px solid;margin-top:8px}}
.sc-note{{font-size:.67rem;color:var(--dim);margin-top:6px;line-height:1.4}}
.sc-src{{font-size:.6rem;color:var(--dim);margin-top:4px}}

/* ── CHARTS ── */
.chart-box{{background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:18px 16px 12px;margin-bottom:16px}}
.chart-title{{font-family:'Space Grotesk',sans-serif;font-size:.78rem;
  font-weight:600;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;
  letter-spacing:.04em}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}

/* ── BENCHMARK GRID ── */
.bm-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:14px;margin-top:24px}}
.bm-block{{background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px}}
.bm-title{{font-family:'Space Grotesk',sans-serif;font-size:.8rem;font-weight:700;
  color:#e2e8f0;margin-bottom:10px}}
.bm-tbl{{width:100%;border-collapse:collapse;font-size:.75rem}}
.bm-tbl td{{padding:4px 6px;border-bottom:1px solid var(--grid)}}
.bm-tbl tr:last-child td{{border-bottom:none}}
.bm-note{{font-size:.7rem;color:var(--muted);margin-top:10px;line-height:1.45}}
.bm-src{{font-size:.65rem;color:var(--dim);margin-top:6px}}

/* ── DIVIDER ── */
.divider{{height:1px;background:var(--border);margin:56px 0}}

/* ── DISCLAIMER ── */
.disclaimer{{background:rgba(253,224,71,.06);border:1px solid rgba(253,224,71,.2);
  border-radius:var(--radius);padding:16px 20px;margin-top:48px;
  font-size:.78rem;color:#a16207;line-height:1.6}}

@media(max-width:660px){{
  .grid2,.grid3{{grid-template-columns:1fr}}
  .hero{{padding:36px 20px 32px}}
  .wrap{{padding:24px 16px 60px}}
  .hero h1{{font-size:1.7rem}}
}}
</style>
</head>
<body>

<!-- ═══════════════════ HERO ═══════════════════ -->
<div class="hero">
  <div class="hero-inner">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
      {_icon_img}
      <div class="hero-eyebrow" style="margin-bottom:0">Apple Watch · Health Report</div>
    </div>
    <h1>Your Health Data,<br>By the Numbers</h1>
    <div class="hero-sub">{date_start} – {date_end} &nbsp;·&nbsp; {total_days:,} days &nbsp;·&nbsp; {wo['total']} workouts &nbsp;·&nbsp; {wo['total_hours']} workout hours &nbsp;·&nbsp; Generated {generated}</div>
    <div class="hero-strip">
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['steps'],0)}</div><div class="hs-lbl">steps/day</div></div>
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['sleep_hours'],1)}</div><div class="hs-lbl">sleep hrs</div></div>
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['resting_hr_bpm'],0)}</div><div class="hs-lbl">resting HR</div></div>
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['hrv_sdnn_ms'],0)}</div><div class="hs-lbl">HRV ms</div></div>
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['vo2_max'],1)}</div><div class="hs-lbl">VO₂max</div></div>
      <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['exercise_min_week'],0)}</div><div class="hs-lbl">min/wk</div></div>
    </div>
  </div>
</div>

<div class="wrap">

<!-- ═══════════════════ ACTIVITY ═══════════════════ -->
<div class="section">
  {sec("🚶", "Activity", "#22d3ee")}
  {insight_html("steps", avgs["steps"])}
  {insight_html("exercise_min_week", avgs["exercise_min_week"])}

  <div class="cards">
    {stat_card("steps", avgs["steps"], 0)}
    {stat_card("exercise_min_week", avgs["exercise_min_week"], 0)}
  </div>

  {chart("cSteps", "Monthly Average Daily Steps", 120)}
  <div class="grid2">
    {chart("cEx", "Exercise Minutes / Week (monthly avg)", 130)}
    {chart("cDist", "Average Daily Distance (km)", 130)}
  </div>

  <div class="bm-grid">
    {bm_block("steps")}
    {bm_block("exercise_min_week")}
  </div>
</div>

<!-- ═══════════════════ CARDIOVASCULAR ═══════════════════ -->
<div class="section">
  {sec("❤️", "Cardiovascular Health", "#f472b6")}
  {insight_html("resting_hr_bpm", avgs["resting_hr_bpm"])}
  {insight_html("hrv_sdnn_ms", avgs["hrv_sdnn_ms"])}

  <div class="cards">
    {stat_card("resting_hr_bpm", avgs["resting_hr_bpm"], 0)}
    {stat_card("walking_hr_bpm", avgs["walking_hr_bpm"], 0)}
    {stat_card("hrv_sdnn_ms", avgs["hrv_sdnn_ms"], 0)}
  </div>

  <div class="grid2">
    {chart("cRHR",  "Resting Heart Rate (bpm)", 130)}
    {chart("cHRV",  "HRV — SDNN (ms)", 130)}
  </div>
  {chart("cWHR", "Walking Heart Rate (bpm)", 110)}

  <div class="bm-grid">
    {bm_block("resting_hr_bpm")}
    {bm_block("walking_hr_bpm")}
    {bm_block("hrv_sdnn_ms")}
  </div>
</div>

<!-- ═══════════════════ FITNESS ═══════════════════ -->
<div class="section">
  {sec("🫁", "Cardiorespiratory Fitness", "#4ade80")}
  {insight_html("vo2_max", avgs["vo2_max"])}

  <div class="cards">
    {stat_card("vo2_max", avgs["vo2_max"])}
  </div>
  {chart("cVO2", "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded", 110)}

  <div class="bm-grid">
    {bm_block("vo2_max")}
  </div>
</div>

<!-- ═══════════════════ SLEEP ═══════════════════ -->
<div class="section">
  {sec("🌙", "Sleep", "#a78bfa")}
  {insight_html("sleep_hours", avgs["sleep_hours"])}

  <div class="cards">
    {stat_card("sleep_hours", avgs["sleep_hours"])}
    {stat_card("sleep_deep_h", avgs["sleep_deep_h"])}
    {stat_card("sleep_rem_h",  avgs["sleep_rem_h"])}
  </div>

  {chart("cSleep", "Monthly Average Sleep Duration (hrs/night)", 110)}
  <div class="grid2">
    {chart("cSleepStack", "Sleep Stages by Month — Stacked (hrs/night)", 160)}
    {chart("cSleepBar",   "Sleep Stages — 90-Day Average (hrs/night)", 160)}
  </div>

  <div class="bm-grid">
    {bm_block("sleep_hours")}
    {bm_block("sleep_deep_h")}
    {bm_block("sleep_rem_h")}
  </div>
</div>

<!-- ═══════════════════ VITALS ═══════════════════ -->
<div class="section">
  {sec("🩺", "Vitals", "#38bdf8")}

  <div class="cards">
    {stat_card("spo2", avgs["spo2"])}
    {stat_card("respiratory_rate", avgs["respiratory_rate"])}
  </div>
  <div class="grid2">
    {chart("cSpo2", "Blood Oxygen SpO₂ (%)", 130)}
    {chart("cResp", "Respiratory Rate (breaths/min, measured during sleep)", 130)}
  </div>
  <div class="bm-grid">
    {bm_block("spo2")}
    {bm_block("respiratory_rate")}
  </div>
</div>

{"<div class='section'><div class='sec-head' style='--accent:#94a3b8'><span class='sec-icon'>⚖️</span>Body Weight</div>" + chart('cWeight','Monthly Average Body Mass (kg)',110) + "</div>" if has_weight else ""}

<!-- ═══════════════════ WORKOUTS ═══════════════════ -->
<div class="section">
  {sec("🏃", "Workouts", "#fb923c")}

  <div class="cards" style="grid-template-columns:repeat(auto-fill,minmax(140px,1fr))">
    <div class="stat-card" style="--accent:#fb923c">
      <div class="sc-title">Total Workouts</div>
      <div class="sc-value" style="color:#fb923c">{wo['total']}</div>
      <div class="sc-unit">sessions</div>
    </div>
    <div class="stat-card" style="--accent:#fb923c">
      <div class="sc-title">Total Hours</div>
      <div class="sc-value" style="color:#fb923c">{wo['total_hours']}</div>
      <div class="sc-unit">hours</div>
    </div>
    <div class="stat-card" style="--accent:#fb923c">
      <div class="sc-title">Total Distance</div>
      <div class="sc-value" style="color:#fb923c">{wo['total_km']}</div>
      <div class="sc-unit">km</div>
    </div>
  </div>

  <div class="grid2">
    {chart("cWoTypes", "Workout Type Distribution", 200)}
    {chart("cWoMo",    "Workouts per Month", 200)}
  </div>
</div>

<!-- DISCLAIMER -->
<div class="disclaimer">
  ⚠️ <strong>For wellness awareness only.</strong> This report is generated from consumer-grade wearable data and does not constitute medical advice. It cannot diagnose, treat, or prevent any medical condition. All benchmarks are population-level guidelines — individual targets should be set with a healthcare provider. Apple Watch metrics (VO₂ max, SpO₂, sleep stages) are estimates with lower accuracy than clinical instruments.
</div>

</div><!-- /wrap -->

<script>
// ── Chart.js dark theme defaults ──
Chart.defaults.color = '#64748b';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "Inter, system-ui, sans-serif";
Chart.defaults.font.size = 11;

const SCALE = {{
  x: {{ ticks: {{ maxTicksLimit: 10, color: '#475569' }},
        grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
  y: {{ ticks: {{ color: '#475569' }},
        grid: {{ color: 'rgba(255,255,255,0.04)' }} }}
}};

const MO = {js(mo_short)};

function hexAlpha(hex, a) {{
  // convert #rrggbb to rgba(r,g,b,a) safely
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${{r}},${{g}},${{b}},${{a}})`;
}}

function line(id, label, data, color, yMin, extra={{}}) {{
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {{
    type: 'line',
    data: {{ labels: MO, datasets: [{{
      label, data,
      borderColor: color,
      backgroundColor: hexAlpha(color, 0.13),
      tension: 0.4, fill: true,
      pointRadius: 2, pointHoverRadius: 5,
      borderWidth: 2.5, spanGaps: true,
    }}] }},
    options: {{
      responsive: true, animation: {{ duration: 600 }},
      plugins: {{ legend: {{ display: false }},
        tooltip: {{ backgroundColor: '#1e293b', titleColor: '#e2e8f0',
          bodyColor: '#94a3b8', borderColor: 'rgba(255,255,255,.1)', borderWidth: 1 }}
      }},
      scales: {{ x: SCALE.x, y: {{...SCALE.y, min: yMin}} }},
      ...extra
    }}
  }});
}}

line('cSteps', 'steps/day',   {js(mo_steps)},    '#22d3ee', 0);
line('cEx',    'min/week',    {js(mo_ex_weekly)}, '#67e8f9', 0);
line('cDist',  'km/day',      {js(mo_dist)},      '#06b6d4', 0);
line('cRHR',   'RHR bpm',     {js(mo_rhr)},       '#f472b6', 40);
line('cWHR',   'Walk HR bpm', {js(mo_walk_hr)},   '#fb7185', 50);
line('cHRV',   'SDNN ms',     {js(mo_hrv)},       '#e879f9', 0);
line('cVO2',   'VO₂max',      {js(mo_vo2)},       '#4ade80', 25);
line('cSleep', 'Sleep h',     {js(mo_sleep)},     '#a78bfa', 0);
line('cSpo2',  'SpO₂ %',      {js(mo_spo2)},      '#38bdf8', 88);
line('cResp',  'Resp rate',   {js(mo_resp)},      '#7dd3fc', 8);
{"line('cWeight','Weight kg'," + js(mo_weight) + ",'#94a3b8',40);" if has_weight else ""}

// Sleep stages stacked bar
new Chart(document.getElementById('cSleepStack'), {{
  type: 'bar',
  data: {{
    labels: MO,
    datasets: [
      {{ label:'Deep',  data:{js(mo_sleep_deep)},  backgroundColor:'#1d4ed8cc', spanGaps:true }},
      {{ label:'REM',   data:{js(mo_sleep_rem)},   backgroundColor:'#7c3aedcc', spanGaps:true }},
      {{ label:'Core',  data:{js(mo_sleep_core)},  backgroundColor:'#0891b2cc', spanGaps:true }},
    ]
  }},
  options: {{
    responsive: true, animation: {{ duration: 600 }},
    plugins: {{ legend: {{ labels: {{ color:'#94a3b8', boxWidth:12 }} }},
      tooltip: {{ backgroundColor:'#1e293b', titleColor:'#e2e8f0',
        bodyColor:'#94a3b8', borderColor:'rgba(255,255,255,.1)', borderWidth:1 }} }},
    scales: {{
      x: {{ stacked:true, ...SCALE.x, ticks:{{ ...SCALE.x.ticks, maxTicksLimit:8 }} }},
      y: {{ stacked:true, ...SCALE.y }}
    }}
  }}
}});

// Sleep stages 90d breakdown
new Chart(document.getElementById('cSleepBar'), {{
  type: 'bar',
  data: {{
    labels: ['Deep (N3)','REM','Core (N2)','Awake in bed'],
    datasets: [{{ label:'hrs/night (90-day avg)',
      data:[
        {avgs.get("sleep_deep_h") or 0},
        {avgs.get("sleep_rem_h")  or 0},
        {avgs.get("sleep_core_h") or 0},
        {recent_avg(daily, "sleep_awake_h", 90) or 0}
      ],
      backgroundColor:['#1d4ed8','#7c3aed','#0891b2','#f59e0b'],
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true, animation: {{ duration: 600 }},
    plugins: {{ legend: {{ display:false }},
      tooltip: {{ backgroundColor:'#1e293b', titleColor:'#e2e8f0',
        bodyColor:'#94a3b8', borderColor:'rgba(255,255,255,.1)', borderWidth:1 }} }},
    scales: {{ y: {{ ...SCALE.y, min:0 }}, x: {{ ...SCALE.x }} }}
  }}
}});

// Workout types (horizontal bar)
new Chart(document.getElementById('cWoTypes'), {{
  type: 'bar',
  data: {{
    labels: {js(wo['top_types'])},
    datasets: [{{ label:'Workouts', data:{js(wo['top_counts'])},
      backgroundColor:'#fb923c99', borderRadius:4, borderSkipped:false }}]
  }},
  options: {{
    indexAxis:'y', responsive:true, animation:{{ duration:600 }},
    plugins:{{ legend:{{ display:false }},
      tooltip:{{ backgroundColor:'#1e293b', titleColor:'#e2e8f0',
        bodyColor:'#94a3b8', borderColor:'rgba(255,255,255,.1)', borderWidth:1 }} }},
    scales:{{ x:{{ ...SCALE.x }}, y:{{ ticks:{{ color:'#94a3b8', font:{{ size:11 }} }},
      grid:{{ color:'rgba(255,255,255,0.04)' }} }} }}
  }}
}});

// Workouts per month
new Chart(document.getElementById('cWoMo'), {{
  type: 'bar',
  data: {{
    labels: {js([m[2:] for m in wo['mo_labels']])},
    datasets: [{{ label:'Workouts', data:{js(wo['mo_counts'])},
      backgroundColor:'#f97316bb', borderRadius:3 }}]
  }},
  options: {{
    responsive:true, animation:{{ duration:600 }},
    plugins:{{ legend:{{ display:false }},
      tooltip:{{ backgroundColor:'#1e293b', titleColor:'#e2e8f0',
        bodyColor:'#94a3b8', borderColor:'rgba(255,255,255,.1)', borderWidth:1 }} }},
    scales:{{
      x:{{ ...SCALE.x, ticks:{{ ...SCALE.x.ticks, maxTicksLimit:14 }} }},
      y:{{ ...SCALE.y }}
    }}
  }}
}});
</script>
</body>
</html>"""


# ─────────────────────────────────────────── main ──

def main():
    args     = parse_args()
    data_dir = os.path.abspath(args.data)
    out_path = args.out or os.path.join(data_dir, "health_report.html")

    if not os.path.exists(data_dir):
        sys.exit(f"ERROR: data directory not found: {data_dir}")

    print(f"loading data from {data_dir}")
    d = load_data(data_dir)
    if not d["daily"]:
        sys.exit("ERROR: daily_metrics.csv not found. Run health_parser.py first.")

    print("building HTML report…")
    html = build_html(d)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✓ Report: {out_path}")
    print(f'  open "{out_path}"')


if __name__ == "__main__":
    main()
