---
name: apple-health
description: Analyze Apple Health export ZIP and generate an interactive HTML report with age/sex-adjusted benchmarks (AHA / WHO / AASM / ACSM / ESC). Use when the user wants to visualize their Apple Watch or iPhone Health data (steps, sleep, HRV, VO₂max, resting HR, etc.) or asks specific questions about long-term health metrics. The report auto-detects system language (EN / ZH / ES / FR / DE / JA / KO) and theme (light/dark) at runtime.
---

# Apple Health Analyzer

This skill runs a 3-stage pipeline against an Apple Health export ZIP:

1. **`health_parser.py`** — parses the export XML (typically 0.3–2 GB) into CSV/JSON
2. **`report_html.py`** — generates a self-contained interactive HTML report
3. Q&A mode — reads the parsed CSVs to answer specific questions

Apple names the export differently depending on the iPhone's locale (e.g. `export.zip` in English, `导出.zip` in Chinese, etc.). The user supplies the ZIP path; the parser doesn't care about the name. After extraction, `find_xml_in_dir()` picks up whichever `.xml` file the archive contains (skipping the small `export_cda.xml` CDA wrapper).

All Python scripts live next to this SKILL.md. They use `__file__` to resolve relative paths, so the directory is fully relocatable (e.g. clone into `~/.codex/skills/apple-health/` to install as a Codex user-level skill, or `~/.claude/skills/apple-health/` for Claude Code).

---

## Locate the script directory

```bash
SCRIPT_DIR="$(dirname "$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$BASH_SOURCE")")"
# Fallback: SKILL.md sits alongside the scripts. If the runtime cannot infer
# its path, prefer the Codex user-level install path, then Claude Code.
[ -z "$SCRIPT_DIR" ] && SCRIPT_DIR="$HOME/.codex/skills/apple-health"
[ ! -f "$SCRIPT_DIR/SKILL.md" ] && SCRIPT_DIR="$HOME/.claude/skills/apple-health"
```

Codex skills do not register custom slash commands. In Codex, users should invoke this skill with natural language such as `use apple-health to analyze ~/Downloads/export.zip` or `用 apple-health 分析 ~/Downloads/导出.zip`. Claude Code users may optionally install the separate `.claude/commands/apple-health.md` slash command.

Default output locations (created if missing):
- Extracted raw data → `$SCRIPT_DIR/latest_raw/`
- Parsed CSVs + JSON → `$SCRIPT_DIR/latest_parsed/`
- HTML report → `$SCRIPT_DIR/latest_parsed/health_report.html`

---

## Modes

### 1. Detect mode from input

| Input pattern | Mode |
|---|---|
| Ends with `.zip` | full pipeline (parse + report) |
| `--report` or empty + `latest_parsed/` exists | report-only (skip parser) |
| Starts with `q:` | Q&A mode |
| Empty + no existing data | ask user for the export ZIP path |

### 2. Full pipeline

```bash
python3 "$SCRIPT_DIR/health_parser.py" --zip "$ZIP_PATH"
python3 "$SCRIPT_DIR/report_html.py" --data "$SCRIPT_DIR/latest_parsed"
open "$SCRIPT_DIR/latest_parsed/health_report.html"
```

Tell the user the parser takes ~1 minute per GB of XML. Stream its progress (it prints record counts every 500k records).

After opening the report, compute and display the health score, then give a brief summary of the 5 hero metrics. Use this snippet to get the score:

```python
import sys, json
from collections import defaultdict
from datetime import date
sys.path.insert(0, SCRIPT_DIR)
from benchmarks import apply_profile_benchmarks, get_status, compute_health_score, score_grade, SCORE_MAP, SCORE_WEIGHTS
from report_data import load_csv, flt, recent_avg

data_dir = SCRIPT_DIR + "/latest_parsed"
daily = load_csv(f"{data_dir}/daily_metrics.csv")
meta  = json.load(open(f"{data_dir}/meta.json"))
profile = meta.get("profile", {})
dob_str = profile.get("date_of_birth"); sex = profile.get("biological_sex","")
age = None
if dob_str:
    d = date.fromisoformat(dob_str); today = date.today()
    age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
if age: apply_profile_benchmarks(age, sex)
avgs = {k: recent_avg(daily, k, 90) for k in ["steps","resting_hr_bpm","walking_hr_bpm","hrv_sdnn_ms","vo2_max","sleep_hours"]}
weekly_ex = defaultdict(float)
for r in sorted(daily, key=lambda x: x["date"], reverse=True)[:90]:
    v = flt(r.get("exercise_min"))
    if v:
        iso = date.fromisoformat(r["date"]).isocalendar()
        weekly_ex[f"{iso[0]}-{iso[1]:02d}"] += v
avgs["exercise_min_week"] = round(sum(weekly_ex.values())/len(weekly_ex),0) if weekly_ex else None
score = compute_health_score(avgs); grade, _, gcat = score_grade(score)
print(score, grade, gcat)
```

Show the score prominently at the top of the reply, e.g. **健康评分：82 / 100 · B · Good**，then the 5 hero metrics (steps, sleep duration, resting HR, HRV, VO₂max) with their status badges and benchmark interpretation. Always include the disclaimer that the data is from a consumer-grade wearable, not medical advice.

### 3. Report-only mode

Skip the parser and only run report + open. Use when `latest_parsed/daily_metrics.csv` already exists and the user just wants to regenerate (e.g. after a code change).

### 4. Q&A mode

Read CSVs from `$SCRIPT_DIR/latest_parsed/` to answer the question.

| File | Possible columns (subset of) |
|---|---|
| `daily_metrics.csv` | date, steps, resting_hr_bpm, walking_hr_bpm, hrv_sdnn_ms, vo2_max, heart_rate_bpm, sleep_hours, sleep_deep_h, sleep_rem_h, sleep_core_h, sleep_awake_h, sleep_in_bed_h, spo2, respiratory_rate, exercise_min, stand_min, active_energy_kcal, basal_energy_kcal, distance_km, flights, env_audio_db, body_mass_kg |
| `monthly_trends.csv` | period, steps_avg, sleep_avg, rhr_avg, hrv_avg, vo2_avg, exercise_min_total, plus per-metric `_avg`/`_days` counterparts |
| `workouts.csv` | type, start, end, duration_min, distance_km, energy_kcal |
| `sleep.csv` | night_date, in_bed_h, asleep_h, deep_h, rem_h, core_h, awake_h |
| `meta.json` | profile (date_of_birth, biological_sex, blood_type), date_range, total_days, total_workouts |

**Schema note:** `daily_metrics.csv` is built dynamically — a column appears only if the export contained data for that metric type. Always read the header row to discover what's actually present (e.g. someone who never logs body weight on their watch will have no `body_mass_kg` column).

**Important:** SpO₂ is stored as a decimal (0.97 = 97%) — multiply by 100 before comparing to benchmarks. The parser does NOT pre-scale this value.

Benchmarks live in `benchmarks.py` (numeric thresholds) and `i18n.py` (per-language text). For consistency, cite these sources when interpreting metrics:

- **Steps** — Paluch et al. *JAMA Netw Open* 2022; AHA
- **Exercise min** — WHO 2020 Physical Activity Guidelines; AHA 2018
- **Resting HR** — AHA; Jouven et al. *NEJM* 2005
- **HRV (SDNN)** — ESC/NASPE *Eur Heart J* 1996; Shaffer & Ginsberg *Front Public Health* 2017
- **VO₂max** — Ross et al. *Circulation* 2016; ACSM
- **Sleep** — AASM/SRS Watson et al. *Sleep* 2015
- **Sleep stages** — AASM; Hirshkowitz et al. *Sleep Health* 2015
- **SpO₂** — AHA / ATS / AASM
- **Respiratory rate** — AHA; NICE

Always append:

> *Consumer-grade wearable data only — not medical advice. Consult a healthcare provider for medical decisions.*

---

## Error handling

| Symptom | Action |
|---|---|
| ZIP path not found | Remind user: iPhone → Health app → profile icon → Export All Health Data. The exported filename is localized by Apple — whatever the user got is fine, just pass the path |
| No `.xml` found after extraction | The parser already skips `export_cda.xml` and picks the other `.xml`; verify the ZIP isn't corrupted |
| `daily_metrics.csv` empty | Source filter may have excluded all data; suggest re-running with `--all-sources` |
| Report import error | Verify `latest_parsed/meta.json` exists; if missing, re-run the parser |
| `vendor/chart.min.js` missing | The first `report_html.py` run downloads it automatically. Requires network access |

---

## Architecture notes (for code changes / Q&A about internals)

- `i18n.py` — **single source of truth for all human-readable text**: UI labels, benchmark notes, insight templates, workout type names, disclaimers, for 7 languages. To add a language: add one entry to each top-level dict.
- `benchmarks.py` — numeric thresholds, scoring weights, age/sex-stratified level tables. Zero text content.
- `report_data.py` — CSV loading + aggregation helpers.
- `report_html.py` — HTML structure + insight/card/benchmark block builders. Imports `i18n` for translations.
- `report_js.py` — embeds Chart.js charts + i18n tables; reads system language via `navigator.languages` and theme via `prefers-color-scheme` at runtime. **No language/theme buttons** — the report auto-conforms to the viewer's system.
- `report_css.py` — static CSS constant.
- `health_parser.py` — streaming XML SAX parser with source filtering and `<Me>` profile extraction.
