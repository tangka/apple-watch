---
name: apple-health
description: Analyze Apple Health export ZIP and generate an interactive HTML report with age/sex-adjusted benchmarks (AHA / WHO / AASM / ACSM / ESC). Use when the user wants to visualize their Apple Watch or iPhone Health data (steps, sleep, HRV, VO₂max, resting HR, etc.) or asks specific questions about long-term health metrics. The report auto-detects system language (EN / ZH / ES / FR / DE / JA / KO) and theme (light/dark) at runtime.
---

# Apple Health Analyzer

This skill runs a 3-stage pipeline against an Apple Health export ZIP:

1. **`health_parser.py`** — parses the export XML (typically 0.3–2 GB) into CSV/JSON
2. **`report_html.py`** — generates a self-contained interactive HTML report
3. Q&A mode — reads the parsed CSVs to answer specific questions

The export ZIP is named differently by region: **`export.zip`** for English-locale iPhones, **`导出.zip`** for Chinese-locale iPhones (likewise `export.xml` vs `导出.xml` inside). The parser auto-detects whichever `.xml` file the ZIP contains (skipping the small `export_cda.xml` CDA wrapper), so the user can pass any locale's export without renaming.

All Python scripts live next to this SKILL.md. They use `__file__` to resolve relative paths, so the directory is fully relocatable (e.g. clone into `~/.claude/skills/apple-health/` to install as a user-level skill).

---

## Locate the script directory

```bash
SCRIPT_DIR="$(dirname "$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$BASH_SOURCE")")"
# Fallback: SKILL.md sits alongside the scripts. If the runtime cannot infer
# its path, the user-level install path is the safest default:
[ -z "$SCRIPT_DIR" ] && SCRIPT_DIR="$HOME/.claude/skills/apple-health"
```

When the user invokes this skill explicitly (`/apple-health <path>`), `$ARGUMENTS` holds the input.

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

After opening the report, give a brief summary of the 5 hero metrics (steps, sleep duration, resting HR, HRV, VO₂max) with their status badges and benchmark interpretation. Always include the disclaimer that the data is from a consumer-grade wearable, not medical advice.

### 3. Report-only mode

Skip the parser and only run report + open. Use when `latest_parsed/daily_metrics.csv` already exists and the user just wants to regenerate (e.g. after a code change).

### 4. Q&A mode

Read CSVs from `$SCRIPT_DIR/latest_parsed/` to answer the question.

| File | Key columns |
|---|---|
| `daily_metrics.csv` | date, steps, resting_hr_bpm, hrv_sdnn_ms, vo2_max, sleep_hours, sleep_deep_h, sleep_rem_h, sleep_core_h, spo2, respiratory_rate, exercise_min, active_energy_kcal, distance_km, body_mass_kg |
| `monthly_trends.csv` | period, steps_avg, sleep_avg, rhr_avg, hrv_avg, vo2_avg, exercise_min_total |
| `workouts.csv` | type, start, end, duration_min, distance_km, energy_kcal |
| `sleep.csv` | night_date, in_bed_h, asleep_h, deep_h, rem_h, core_h, awake_h |
| `meta.json` | profile (date_of_birth, biological_sex, blood_type), date_range, total_days, total_workouts |

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
| ZIP path not found | Remind user: iPhone → Health app → profile icon → Export All Health Data. File is named `export.zip` (English locale) or `导出.zip` (Chinese locale) |
| No `.xml` found after extraction | Search recursively for any `.xml` in `latest_raw/`; skip `export_cda.xml` |
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
