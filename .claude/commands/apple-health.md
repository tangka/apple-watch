# Apple Health Analyzer

Analyze Apple Health export data and generate a comprehensive HTML health report, or answer specific health questions based on the data.

**Usage:**
- `/apple-health ~/Downloads/导出.zip` — full pipeline: extract → parse → HTML report
- `/apple-health --report` — regenerate HTML from already-parsed data (no re-parsing)
- `/apple-health q: <question>` — answer a specific health question from parsed data

---

## Setup — locate the project directory

The scripts live alongside this skill file. Determine SCRIPT_DIR by running:

```bash
SCRIPT_DIR="$(dirname "$(realpath ~/.claude/commands/apple-health.md)" 2>/dev/null || echo "$HOME/Desktop/tangka-code/apple-watch")"
```

All outputs go into the project:
- Extracted raw data → `$SCRIPT_DIR/latest_raw/`
- Parsed CSVs + JSON → `$SCRIPT_DIR/latest_parsed/`
- HTML report → `$SCRIPT_DIR/latest_parsed/health_report.html`

---

## Behavior

### 1. Detect mode from $ARGUMENTS

- Argument ends with `.zip` → **full pipeline mode**
- Argument is `--report` or empty with `latest_parsed/` already present → **report-only mode**
- Argument starts with `q:` → **Q&A mode**
- No argument and no existing data → ask user to provide the zip path

---

### 2. Full pipeline mode

Run these steps in order:

**Step 1 — Parse (60–120 s for a 1–2 GB XML file):**
```bash
python3 "$SCRIPT_DIR/health_parser.py" \
  --zip "$ZIP_PATH"
```
`--out` and `--raw` default to `$SCRIPT_DIR/latest_parsed/` and `$SCRIPT_DIR/latest_raw/` automatically — no need to pass them unless overriding.

Tell the user parsing takes 1–2 minutes and show progress output.

**Step 2 — Generate HTML report:**
```bash
python3 "$SCRIPT_DIR/report_html.py" \
  --data "$SCRIPT_DIR/latest_parsed"
```
Output defaults to `$SCRIPT_DIR/latest_parsed/health_report.html`.

**Step 3 — Open the report:**
```bash
open "$SCRIPT_DIR/latest_parsed/health_report.html"
```

Then give the user a brief summary of the 5 key metrics (steps, sleep, RHR, HRV, VO₂max) with benchmark context.

---

### 3. Report-only mode (`--report`)

Skip parsing, run only Steps 2–3 above. Use when `latest_parsed/daily_metrics.csv` already exists.

---

### 4. Q&A mode (`q: <question>`)

Read CSVs from `$SCRIPT_DIR/latest_parsed/` to answer the question.

Available files and key columns:
| File | Key columns |
|------|------------|
| `daily_metrics.csv` | date, steps, resting_hr_bpm, hrv_sdnn_ms, vo2_max, sleep_hours, sleep_deep_h, sleep_rem_h, sleep_core_h, spo2, respiratory_rate, exercise_min, active_energy_kcal, distance_km, body_mass_kg |
| `monthly_trends.csv` | period, steps_avg, sleep_avg, rhr_avg, hrv_avg, vo2_avg, exercise_min_total |
| `workouts.csv` | type, start, end, duration_min, distance_km, energy_kcal |
| `sleep.csv` | night_date, in_bed_h, asleep_h, deep_h, rem_h, core_h, awake_h |

**Note:** SpO₂ is stored as a decimal (0.97 = 97%) — multiply by 100 before comparing to benchmarks.

Evidence-based benchmarks to cite:
- **Steps**: Paluch et al. JAMA Netw Open 2022; AHA (≥7,000 steps → 50–70% lower mortality)
- **Exercise min**: WHO 2020 / AHA 2018 (≥150 min/wk moderate or ≥75 min/wk vigorous)
- **Resting HR**: AHA (normal 60–100 bpm; optimal 60–70 bpm)
- **HRV (SDNN)**: ESC/NASPE 1996; Shaffer & Ginsberg Front Public Health 2017
- **VO₂max**: Ross et al. Circulation 2016; ACSM fitness categories
- **Sleep**: AASM/SRS Consensus Watson et al. Sleep 2015 (7–9 h recommended)
- **Sleep stages**: AASM; Hirshkowitz et al. Sleep Health 2015
- **SpO₂**: AHA/ATS (≥95% normal; <90% = hypoxemia)
- **Respiratory rate**: AHA/NICE (12–20 breaths/min normal)

Always append:
> *Consumer-grade wearable data only — not medical advice. Consult a healthcare provider.*

---

### 5. Error handling

- Zip not found → remind user: iPhone → Health app → profile icon → Export All Health Data
- XML not found after extraction → search recursively for any `.xml` file in `latest_raw/`
- `daily_metrics.csv` empty → source filter may have excluded everything; suggest `--all-sources` flag
- `report_html.py` import error → check that `latest_parsed/meta.json` exists (re-run parser if missing)
