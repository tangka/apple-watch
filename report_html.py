"""
Generate a self-contained HTML health report from parsed Apple Health CSVs.

Usage:
    python report_html.py --data ./output --out ./output/health_report.html

Visual style: Pudding.cool editorial narrative × GitHub Octoverse dark-neon.
Evidence-based benchmarks: AHA, WHO, AASM, ACSM, ESC.
"""
from __future__ import annotations

import argparse, os, sys, urllib.request
from collections import defaultdict
from datetime import datetime, date

from benchmarks import BENCHMARKS, apply_profile_benchmarks, get_status, compute_health_score, score_grade
from report_data import load_csv, flt, load_data, SPO2_FIELDS, scale, recent_avg, mo_series, compute_weekly_ex, workout_summary

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
CHARTJS_CACHE = os.path.join(SCRIPT_DIR, "vendor", "chart.min.js")

def get_chartjs() -> str:
    if os.path.exists(CHARTJS_CACHE):
        with open(CHARTJS_CACHE, encoding="utf-8") as f:
            return f.read()
    print(f"downloading Chart.js → {CHARTJS_CACHE}")
    os.makedirs(os.path.dirname(CHARTJS_CACHE), exist_ok=True)
    urllib.request.urlretrieve(CHARTJS_URL, CHARTJS_CACHE)
    with open(CHARTJS_CACHE, encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────── CLI ──

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, metavar="DIR")
    p.add_argument("--out",  metavar="PATH")
    return p.parse_args()


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

    # ── Profile: age / sex ──
    profile = meta.get("profile", {})
    dob_str = profile.get("date_of_birth", "")
    sex     = profile.get("biological_sex", "")   # "male" / "female"
    age     = None
    if dob_str:
        try:
            from datetime import date as _date
            dob_d = _date.fromisoformat(dob_str)
            today = _date.today()
            age = today.year - dob_d.year - ((today.month, today.day) < (dob_d.month, dob_d.day))
        except Exception:
            pass

    # Adjust all age/sex-sensitive benchmarks
    if age is not None:
        apply_profile_benchmarks(age, sex)

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

    health_score                = compute_health_score(avgs)
    grade, grade_color, grade_cat = score_grade(health_score)

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
  <div class="sc-title" data-i18n="{title}">{title}</div>
  <div class="sc-value" style="color:{accent}">{val_str}</div>
  <div class="sc-unit">{unit}</div>
  <div class="sc-badge" style="color:{color};border-color:{color}44;background:{color}11" data-i18n="{status}">{status}</div>
  <div class="sc-note">{note}</div>
  <div class="sc-src"><a href="{url}" target="_blank">{src[:52]}</a></div>
</div>"""

    # Benchmark table
    def bm_block(key):
        bm = BENCHMARKS.get(key,{})
        rows = "".join(
            f'<tr><td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c};margin-right:6px;vertical-align:middle"></span><span data-i18n="{lbl}">{lbl}</span></td>'
            f'<td style="color:#94a3b8">{lo}{"–"+str(hi) if hi else "+"} {bm.get("unit","")}</td></tr>'
            for lo,hi,lbl,c in bm.get("levels",[])
        )
        return f"""<div class="bm-block">
  <div class="bm-title" data-i18n="{bm.get('label',key)}">{bm.get("label",key)}</div>
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
        return f'<div class="sec-head" style="--accent:{accent}"><span class="sec-icon">{icon}</span><span data-i18n="{title}">{title}</span></div>'

    # Embed Chart.js inline
    _chartjs = get_chartjs()

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
<style>
/* System font stack — no external dependencies */
@font-face {{
  font-family: 'Space Grotesk';
  src: local('Space Grotesk'), local('SpaceGrotesk');
}}
</style>
<script>{_chartjs}</script>
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
body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.55;font-size:14px;overflow-x:hidden}}
a{{color:#7dd3fc;text-decoration:none}}
a:hover{{text-decoration:underline}}

/* ── HERO ── */
.hero{{
  position:relative;overflow:hidden;
  background:linear-gradient(160deg,#0a0f1e 0%,#0d1a3a 40%,#130d2e 100%);
  padding:56px 32px 48px;border-bottom:1px solid var(--border);
}}
.hero-layout{{display:flex;align-items:center;gap:40px;flex-wrap:wrap}}
.hero-text{{flex:1;min-width:260px}}
.hero-gauge-wrap{{
  flex-shrink:0;display:flex;flex-direction:column;align-items:center;gap:6px;
}}
.gauge-grade-row{{
  display:flex;align-items:baseline;gap:8px;
  font-family:'JetBrains Mono','SF Mono','Fira Code',monospace;
}}
.hero::before{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 50% at 70% 40%,rgba(99,102,241,.18) 0%,transparent 70%),
             radial-gradient(ellipse 40% 60% at 20% 80%,rgba(34,211,238,.10) 0%,transparent 60%);
  pointer-events:none;
}}
.hero-inner{{position:relative;max-width:1060px;margin:0 auto}}
.hero-eyebrow{{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.72rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:#7dd3fc;margin-bottom:14px}}
.hero h1{{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:clamp(2rem,4vw,3rem);
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
.hs-val{{font-family:'JetBrains Mono','SF Mono','Fira Code','Cascadia Code',monospace;font-size:1.35rem;font-weight:600;
  line-height:1;color:#f1f5f9}}
.hs-lbl{{font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);margin-top:4px}}

/* ── WRAPPER ── */
.wrap{{max-width:1060px;margin:0 auto;padding:40px 24px 80px}}

/* ── SECTION ── */
.section{{margin-top:56px}}
.sec-head{{display:flex;align-items:center;gap:10px;
  font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:1.15rem;font-weight:700;
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
.insight-head{{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:1.5rem;font-weight:700;
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
  font-family:'JetBrains Mono','SF Mono','Fira Code','Cascadia Code',monospace;
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
.chart-title{{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.78rem;
  font-weight:600;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;
  letter-spacing:.04em}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}

/* ── BENCHMARK GRID ── */
.bm-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:14px;margin-top:24px}}
.bm-block{{background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px}}
.bm-title{{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.8rem;font-weight:700;
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

html.light{{
  --bg:#f8fafc; --bg2:#f1f5f9;
  --surface:rgba(0,0,0,.04); --surface2:rgba(0,0,0,.08);
  --border:rgba(0,0,0,.12); --text:#0f172a;
  --muted:#374151; --dim:#64748b; --grid:rgba(0,0,0,.07);
}}
html.light .hero{{
  background:linear-gradient(160deg,#e0f2fe 0%,#e0e7ff 40%,#ede9fe 100%);
  border-bottom-color:rgba(0,0,0,.1);
}}
html.light a{{color:#1d4ed8}}
html.light .hero-eyebrow{{color:#3b82f6}}
html.light h1{{
  background:linear-gradient(135deg,#0f172a 30%,#1d4ed8 70%,#7c3aed 100%);
  -webkit-background-clip:text;background-clip:text;
}}
html.light .hs-val{{color:#0f172a}}
html.light .sec-head{{color:#0f172a}}
html.light .bm-title{{color:#0f172a}}
html.light .insight-body{{color:#475569}}
html.light .chart-title{{color:#374151}}
html.light .bm-tbl td{{color:#374151 !important}}
html.light .ctrl-btn{{background:rgba(0,0,0,.06);border-color:rgba(0,0,0,.15)}}
html.light .ctrl-btn:hover{{background:rgba(0,0,0,.12)}}
/* Controls bar */
.controls-bar{{position:fixed;top:16px;right:16px;z-index:100;display:flex;gap:8px}}
.ctrl-btn{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);
  border-radius:99px;padding:6px 14px;color:var(--text);font-size:.72rem;
  font-weight:600;cursor:pointer;backdrop-filter:blur(8px);
  transition:background .15s;font-family:inherit}}
.ctrl-btn:hover{{background:rgba(255,255,255,.18)}}

@media(max-width:660px){{
  .grid2,.grid3{{grid-template-columns:1fr}}
  .hero{{padding:36px 20px 32px}}
  .wrap{{padding:24px 16px 60px}}
  .hero h1{{font-size:1.7rem}}
}}
</style>
</head>
<body>
<div class="controls-bar">
  <button class="ctrl-btn" id="langBtn" onclick="toggleLang()">中文</button>
  <button class="ctrl-btn" id="themeBtn" onclick="toggleTheme()">☀️</button>
</div>

<!-- ═══════════════════ HERO ═══════════════════ -->
<div class="hero">
  <div class="hero-inner">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
      {_icon_img}
      <div class="hero-eyebrow" style="margin-bottom:0">Apple Watch · Health Report</div>
    </div>
    <div class="hero-layout">
      <div class="hero-text">
        <h1>Your Health Data,<br>By the Numbers</h1>
        <div class="hero-sub">
          {date_start} – {date_end} &nbsp;·&nbsp; {total_days:,} days &nbsp;·&nbsp;
          {wo['total']} workouts &nbsp;·&nbsp;
          {"Male" if (sex or "").lower() == "male" else "Female" if (sex or "").lower() == "female" else ""}{(", age " + str(age)) if age else ""} &nbsp;·&nbsp;
          Generated {generated}
        </div>
        <div class="hero-strip">
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['steps'],0)}</div><div class="hs-lbl" data-i18n="steps/day">steps/day</div></div>
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['sleep_hours'],1)}</div><div class="hs-lbl" data-i18n="sleep hrs">sleep hrs</div></div>
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['resting_hr_bpm'],0)}</div><div class="hs-lbl" data-i18n="resting HR">resting HR</div></div>
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['hrv_sdnn_ms'],0)}</div><div class="hs-lbl" data-i18n="HRV ms">HRV ms</div></div>
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['vo2_max'],1)}</div><div class="hs-lbl" data-i18n="VO₂max">VO₂max</div></div>
          <div class="hs-cell"><div class="hs-val">{fmt_num(avgs['exercise_min_week'],0)}</div><div class="hs-lbl" data-i18n="min/wk">min/wk</div></div>
        </div>
      </div>
      <div class="hero-gauge-wrap">
        <div style="font-family:'Space Grotesk',-apple-system,sans-serif;font-size:.62rem;
                    font-weight:600;letter-spacing:.10em;text-transform:uppercase;
                    color:#475569;margin-bottom:2px" data-i18n="Health Score">Health Score</div>
        <canvas id="gaugeCanvas" width="280" height="190"
                style="display:block"></canvas>
        <div class="gauge-grade-row">
          <span style="font-size:2.2rem;font-weight:700;color:{grade_color}">{grade}</span>
          <span style="font-size:.85rem;color:{grade_color};opacity:.8" data-i18n="{grade_cat}">{grade_cat}</span>
        </div>
        <div style="font-size:.62rem;color:#475569;text-align:center;line-height:1.55">
          Weighted composite · 6 metrics · 90&#8209;day avg<br>
          Steps 20% · Sleep 20% · RHR/HRV/VO₂/Ex 15% each
        </div>
      </div>
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
      <div class="sc-title" data-i18n="Total Workouts">Total Workouts</div>
      <div class="sc-value" style="color:#fb923c">{wo['total']}</div>
      <div class="sc-unit" data-i18n="sessions">sessions</div>
    </div>
    <div class="stat-card" style="--accent:#fb923c">
      <div class="sc-title" data-i18n="Total Hours">Total Hours</div>
      <div class="sc-value" style="color:#fb923c">{wo['total_hours']}</div>
      <div class="sc-unit" data-i18n="hours">hours</div>
    </div>
    <div class="stat-card" style="--accent:#fb923c">
      <div class="sc-title" data-i18n="Total Distance">Total Distance</div>
      <div class="sc-value" style="color:#fb923c">{wo['total_km']}</div>
      <div class="sc-unit" data-i18n="km">km</div>
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
Chart.defaults.font.family = "Inter, -apple-system, BlinkMacSystemFont, system-ui, sans-serif";
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

// ── Health score gauge ──
(function() {{
  const SCORE = {health_score if health_score is not None else 0};
  const canvas = document.getElementById('gaugeCanvas');
  if (!canvas || !SCORE) return;
  const ctx = canvas.getContext('2d');
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  const W0 = canvas.width, H0 = canvas.height;
  canvas.width  = W0 * DPR; canvas.height = H0 * DPR;
  canvas.style.width = W0 + 'px'; canvas.style.height = H0 + 'px';
  ctx.scale(DPR, DPR);

  const W = W0, H = H0;
  const cx = W / 2, cy = H * 0.84;
  const R  = Math.min(W * 0.40, cy * 0.90);
  const LW = Math.max(16, Math.round(R * 0.20));
  const START = Math.PI * 0.75;   // 135° from east → lower-left
  const SWEEP = Math.PI * 1.5;    // 270° sweep → lower-right

  const ZONES = [
    [0.00, 0.20, '#f87171'],
    [0.20, 0.40, '#fb923c'],
    [0.40, 0.60, '#facc15'],
    [0.60, 0.80, '#86efac'],
    [0.80, 1.00, '#4ade80'],
  ];
  function zoneColor(p) {{
    for (const [a,b,c] of ZONES) if (p <= b + 0.001) return c;
    return '#4ade80';
  }}

  function draw(pct) {{
    ctx.clearRect(0, 0, W, H);

    // ── background track ──
    ctx.beginPath();
    ctx.arc(cx, cy, R, START, START + SWEEP);
    ctx.strokeStyle = 'rgba(255,255,255,0.07)';
    ctx.lineWidth = LW; ctx.lineCap = 'butt'; ctx.stroke();

    // ── zone bands (dim) ──
    for (const [zs, ze, col] of ZONES) {{
      ctx.beginPath();
      ctx.arc(cx, cy, R, START + SWEEP * zs, START + SWEEP * Math.min(ze, 1));
      ctx.strokeStyle = col + '2a';
      ctx.lineWidth = LW; ctx.lineCap = 'butt'; ctx.stroke();
    }}

    // ── major tick marks ──
    for (let i = 0; i <= 20; i++) {{
      const a = START + SWEEP * (i / 20);
      const maj = i % 4 === 0;
      const r1 = R - LW * 0.45 - (maj ? 8 : 3);
      const r2 = R + LW * 0.45 + (maj ? 4 : 1);
      ctx.beginPath();
      ctx.moveTo(cx + r1 * Math.cos(a), cy + r1 * Math.sin(a));
      ctx.lineTo(cx + r2 * Math.cos(a), cy + r2 * Math.sin(a));
      ctx.strokeStyle = maj ? 'rgba(255,255,255,0.30)' : 'rgba(255,255,255,0.10)';
      ctx.lineWidth = maj ? 1.5 : 1; ctx.stroke();
    }}
    // tick labels at 0/50/100
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = '#374151';
    ctx.font = `${{Math.round(R * 0.13)}}px Inter, sans-serif`;
    for (const [frac, txt] of [[0,'0'],[0.5,'50'],[1,'100']]) {{
      const a = START + SWEEP * frac;
      const lr = R + LW * 0.9;
      ctx.fillText(txt, cx + lr * Math.cos(a), cy + lr * Math.sin(a));
    }}

    // ── score fill arc ──
    if (pct > 0) {{
      ctx.beginPath();
      ctx.arc(cx, cy, R, START, START + SWEEP * pct);
      ctx.strokeStyle = zoneColor(pct);
      ctx.lineWidth = LW - 4; ctx.lineCap = 'round'; ctx.stroke();

      // glow blob at tip
      const tipA = START + SWEEP * pct;
      const tx = cx + R * Math.cos(tipA), ty = cy + R * Math.sin(tipA);
      const grd = ctx.createRadialGradient(tx, ty, 0, tx, ty, LW * 1.4);
      grd.addColorStop(0, zoneColor(pct) + 'aa');
      grd.addColorStop(1, 'transparent');
      ctx.fillStyle = grd;
      ctx.beginPath(); ctx.arc(tx, ty, LW * 1.4, 0, Math.PI * 2); ctx.fill();
    }}

    // ── needle ──
    const needleA = START + SWEEP * pct;
    const nlen = R - LW * 0.5 - 4;
    const nx = cx + nlen * Math.cos(needleA), ny = cy + nlen * Math.sin(needleA);
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(nx, ny);
    ctx.strokeStyle = '#f1f5f9'; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#f1f5f9'; ctx.fill();

    // ── score number — centered in arc, well above needle base ──
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = zoneColor(pct);
    ctx.font = `bold ${{Math.round(R * 0.52)}}px 'JetBrains Mono','SF Mono',monospace`;
    ctx.fillText(Math.round(pct * 100), cx, cy - R * 0.32);
  }}

  // animated fill
  const target = SCORE / 100;
  let startT = null;
  const DUR = 1400;
  function frame(ts) {{
    if (!startT) startT = ts;
    const t = Math.min((ts - startT) / DUR, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    draw(target * ease);
    if (t < 1) requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();

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

const ALL_CHARTS = Object.values(Chart.instances);

// ── i18n ──
const ZH = {{
  "Activity":"运动活跃度","Cardiovascular Health":"心血管健康",
  "Cardiorespiratory Fitness":"心肺适能","Sleep":"睡眠",
  "Vitals":"生理指标","Body Weight":"体重","Workouts":"锻炼记录",
  "Daily Steps":"每日步数","Exercise Min / Week":"每周运动",
  "Resting Heart Rate":"静息心率","Walking Heart Rate":"步行心率",
  "HRV — SDNN":"心率变异性","VO₂ Max":"最大摄氧量",
  "Sleep Duration":"睡眠时长","Deep Sleep (N3)":"深度睡眠",
  "REM Sleep":"快眼动睡眠","Blood Oxygen (SpO₂)":"血氧饱和度",
  "Respiratory Rate":"呼吸频率",
  "Total Workouts":"总锻炼次数","Total Hours":"总时长","Total Distance":"总距离",
  "Highly Active":"非常活跃","Active":"活跃","Somewhat Active":"中等活跃",
  "Low Active":"低活跃","Sedentary":"久坐",
  "Meets Guidelines":"达标","Partially Active":"部分达标","Below Guidelines":"未达标",
  "Athletic":"运动员级","Optimal":"最优","Normal":"正常",
  "Elevated":"偏高","Tachycardia":"心动过速",
  "Fit":"体能好","Average":"一般","High":"偏高",
  "Good":"良好","Fair":"一般","Low":"偏低",
  "Excellent":"优秀","Poor":"较差","Very Poor":"很差",
  "Recommended":"推荐范围","Borderline":"边缘",
  "Long Sleep":"睡眠偏多","Insufficient":"睡眠不足",
  "No Data":"暂无数据","—":"—",
  "Below Average":"低于均值",
  "Health Score":"健康评分",
  "steps/day":"步/天","sleep hrs":"睡眠时长","resting HR":"静息心率",
  "HRV ms":"心率变异","VO₂max":"最大摄氧量","min/wk":"分钟/周",
  "sessions":"次","hours":"小时","km":"公里",
}};
let _lang = localStorage.getItem('aw-lang') || 'en';
function toggleLang() {{
  _lang = _lang === 'en' ? 'zh' : 'en';
  localStorage.setItem('aw-lang', _lang);
  _applyLang();
}}
function _applyLang() {{
  const dict = _lang === 'zh' ? ZH : {{}};
  document.querySelectorAll('[data-i18n]').forEach(el => {{
    el.textContent = dict[el.dataset.i18n] ?? el.dataset.i18n;
  }});
  document.getElementById('langBtn').textContent = _lang === 'en' ? '中文' : 'EN';
}}

// ── theme ──
function toggleTheme() {{
  const light = document.documentElement.classList.toggle('light');
  localStorage.setItem('aw-theme', light ? 'light' : 'dark');
  document.getElementById('themeBtn').textContent = light ? '🌙' : '☀️';
  const gc = light ? 'rgba(0,0,0,0.07)' : 'rgba(255,255,255,0.04)';
  const tc = '#475569';
  Object.values(Chart.instances).forEach(c => {{
    ['x','y'].forEach(ax => {{
      if (c.options.scales?.[ax]) {{
        c.options.scales[ax].grid.color = gc;
        c.options.scales[ax].ticks.color = tc;
      }}
    }});
    const tt = c.options.plugins?.tooltip;
    if (tt) {{
      tt.backgroundColor = light ? '#fff' : '#1e293b';
      tt.titleColor = light ? '#0f172a' : '#e2e8f0';
      tt.bodyColor = light ? '#475569' : '#94a3b8';
    }}
    c.update('none');
  }});
}}

// ── init ──
(function() {{
  if (localStorage.getItem('aw-theme') === 'light') {{
    document.documentElement.classList.add('light');
    document.getElementById('themeBtn').textContent = '🌙';
  }}
  _applyLang();
}})();
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
