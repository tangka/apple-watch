"""
Generate a self-contained HTML health report from parsed Apple Health CSVs.

Usage:
    python report_html.py --data ./output --out ./output/health_report.html

Visual style: Pudding.cool editorial narrative × GitHub Octoverse dark-neon.
Evidence-based benchmarks: AHA, WHO, AASM, ACSM, ESC.
"""
from __future__ import annotations

import argparse, hashlib, html as _html, json, os, sys, urllib.request
from collections import defaultdict
from datetime import datetime, date

from benchmarks import BENCHMARKS, apply_profile_benchmarks, get_status, compute_health_score, score_grade
from report_data import load_csv, flt, load_data, SPO2_FIELDS, scale, recent_avg, mo_series, compute_weekly_ex, workout_summary
from report_css import CSS
from report_js import build_js
import i18n


def i18n_attr(d):
    """Encode a {lang: text} dict as a safe HTML attribute value (JSON)."""
    return _html.escape(json.dumps(d, ensure_ascii=False), quote=True)

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CHARTJS_URL    = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
CHARTJS_CACHE  = os.path.join(SCRIPT_DIR, "vendor", "chart.min.js")
CHARTJS_SHA256 = "0e2326c6868072bec1592760c6729043caeea2960a2b46cee6a2192aac6abff0"

def get_chartjs() -> str:
    if os.path.exists(CHARTJS_CACHE):
        with open(CHARTJS_CACHE, "rb") as f:
            data = f.read()
        if hashlib.sha256(data).hexdigest() != CHARTJS_SHA256:
            sys.exit("ERROR: vendor/chart.min.js checksum mismatch — delete it and re-run to re-download")
        return data.decode("utf-8")
    print(f"downloading Chart.js → {CHARTJS_CACHE}")
    os.makedirs(os.path.dirname(CHARTJS_CACHE), exist_ok=True)
    urllib.request.urlretrieve(CHARTJS_URL, CHARTJS_CACHE)
    with open(CHARTJS_CACHE, "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != CHARTJS_SHA256:
        os.remove(CHARTJS_CACHE)
        sys.exit("ERROR: downloaded Chart.js checksum mismatch — possible CDN tampering")
    return data.decode("utf-8")


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
# All translations live in i18n.py. This function picks the right variant +
# placeholder values and delegates rendering to i18n.all_insight().

def make_insight(key, value, avgs=None):
    """Return ({lang: {"head": ..., "detail": ...}}, color) for editorial callout."""
    if value is None: return None
    label_en, color = get_status(value, key)

    if key == "steps":
        diff = int(value - 7000)
        variant = "above" if diff >= 0 else "below"
        params  = {"val": fmt_num(value, 0), "diff": f"{abs(diff):,}"}
    elif key == "exercise_min_week":
        variant = "yes" if value >= 150 else "no"
        params  = {"val": fmt_num(value, 0)}
    elif key == "resting_hr_bpm":
        variant, params = "default", {"val": fmt_num(value, 0), "label": label_en}
    elif key == "hrv_sdnn_ms":
        variant, params = "default", {"val": fmt_num(value, 0)}
    elif key == "vo2_max":
        variant, params = "default", {"val": fmt_num(value, 1), "label": label_en}
    elif key == "sleep_hours":
        if value < 7:
            variant, params = "short", {"val": fmt_num(value, 1), "short": f"{7-value:.1f}"}
        else:
            variant, params = "ok",    {"val": fmt_num(value, 1)}
    else:
        return None

    return i18n.all_insight(key, variant, params), color


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

    # Build insight callouts. Embeds all-language dict as JSON in data attrs;
    # JS picks the active language at render time.
    def insight_html(key, value):
        r = make_insight(key, value, avgs)
        if not r: return ""
        texts, color = r
        heads   = {lang: texts[lang]["head"]   for lang in i18n.LANGS}
        details = {lang: texts[lang]["detail"] for lang in i18n.LANGS}
        return f"""<div class="insight" style="--accent:{color}">
  <div class="insight-head" data-i18n-json="{i18n_attr(heads)}">{heads['en']}</div>
  <div class="insight-body" data-i18n-json="{i18n_attr(details)}">{details['en']}</div>
</div>"""

    # Stat card. Note text is resolved per-language via i18n.note_for_lang(),
    # truncated to 100 chars, and embedded as JSON data attr.
    def stat_card(key, value, decimals=1, label_override=None):
        bm     = BENCHMARKS.get(key,{})
        title  = label_override or bm.get("label", key)
        unit   = bm.get("unit","")
        accent = bm.get("accent","#94a3b8")
        status, color = get_status(value, key)
        val_str = fmt_num(value, decimals)
        src    = bm.get("source","")
        url    = bm.get("url","#")

        def _trunc(s, n=100): return s[:n]+"…" if len(s)>n else s
        notes = {lang: _trunc(i18n.note_for_lang(key, lang, age=age, sex=sex)) for lang in i18n.LANGS}
        return f"""<div class="stat-card" style="--accent:{accent}">
  <div class="sc-title" data-i18n="{title}">{title}</div>
  <div class="sc-value" style="color:{accent}">{val_str}</div>
  <div class="sc-unit" data-i18n="{unit}">{unit}</div>
  <div class="sc-badge" style="color:{color};border-color:{color}44;background:{color}11" data-i18n="{status}">{status}</div>
  <div class="sc-note" data-i18n-json="{i18n_attr(notes)}">{notes['en']}</div>
  <div class="sc-src"><a href="{url}" target="_blank">{src[:52]}</a></div>
</div>"""

    # Benchmark table — same note-translation pattern, full text (no truncation).
    def bm_block(key):
        bm = BENCHMARKS.get(key,{})
        rows = "".join(
            f'<tr><td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c};margin-right:6px;vertical-align:middle"></span><span data-i18n="{lbl}">{lbl}</span></td>'
            f'<td style="color:#94a3b8">{lo}{"–"+str(hi) if hi else "+"} <span data-i18n="{bm.get("unit","")}">{bm.get("unit","")}</span></td></tr>'
            for lo,hi,lbl,c in bm.get("levels",[])
        )
        notes = {lang: i18n.note_for_lang(key, lang, age=age, sex=sex) for lang in i18n.LANGS}
        return f"""<div class="bm-block">
  <div class="bm-title" data-i18n="{bm.get('label',key)}">{bm.get("label",key)}</div>
  <table class="bm-tbl"><tbody>{rows}</tbody></table>
  <p class="bm-note" data-i18n-json="{i18n_attr(notes)}">{notes['en']}</p>
  <p class="bm-src">📎 <a href="{bm.get('url','#')}" target="_blank">{bm.get('source','')}</a></p>
</div>"""

    # Chart wrapper
    def chart(cid, title, height=130):
        return f"""<div class="chart-box">
  <div class="chart-title" data-i18n="{title}">{title}</div>
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

    # Assemble JS data dict
    js_data = dict(
        mo_short=mo_short, mo_steps=mo_steps, mo_sleep=mo_sleep,
        mo_sleep_deep=mo_sleep_deep, mo_sleep_rem=mo_sleep_rem,
        mo_sleep_core=mo_sleep_core, mo_rhr=mo_rhr, mo_walk_hr=mo_walk_hr,
        mo_hrv=mo_hrv, mo_vo2=mo_vo2, mo_spo2=mo_spo2, mo_resp=mo_resp,
        mo_dist=mo_dist, mo_kcal=mo_kcal, mo_ex_weekly=mo_ex_weekly,
        mo_weight=mo_weight,
        avgs=avgs, wo=wo, health_score=health_score,
        has_weight=has_weight, daily=daily,
    )

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
{CSS}
</style>
</head>
<body>
<!-- Language and theme are detected from system preferences (navigator.language
     and prefers-color-scheme). No user controls. -->

<!-- ═══════════════════ HERO ═══════════════════ -->
<div class="hero">
  <div class="hero-inner">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
      {_icon_img}
      <div class="hero-eyebrow" style="margin-bottom:0" data-i18n-json="{i18n_attr(dict(i18n.HEADER))}">{i18n.HEADER['en']}</div>
    </div>
    <div class="hero-layout">
      <div class="hero-text">
        <h1 data-i18n="hero.title">Your Health Data,<br>By the Numbers</h1>
        <div class="hero-sub">
          {date_start} – {date_end} &nbsp;·&nbsp; {total_days:,} <span data-i18n="days">days</span> &nbsp;·&nbsp;
          {wo['total']} <span data-i18n="workouts">workouts</span> &nbsp;·&nbsp;
          {"<span data-i18n='Male'>Male</span>" if (sex or "").lower() == "male" else "<span data-i18n='Female'>Female</span>" if (sex or "").lower() == "female" else ""}{(", <span data-i18n='age'>age</span> " + str(age)) if age else ""} &nbsp;·&nbsp;
          <span data-i18n="Generated">Generated</span> {generated}
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
          <span data-i18n="gauge.desc1">Weighted composite · 6 metrics · 90&#8209;day avg</span><br>
          <span data-i18n="gauge.desc2">Steps 20% · Sleep 20% · RHR/HRV/VO₂/Ex 15% each</span>
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
  ⚠️ <strong data-i18n="For wellness awareness only.">For wellness awareness only.</strong> <span data-i18n-json="{i18n_attr(dict(i18n.DISCLAIMER))}">{i18n.DISCLAIMER['en']}</span>
</div>

</div><!-- /wrap -->

<script>
{build_js(js_data)}
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
