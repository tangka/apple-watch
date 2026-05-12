# Apple Health Report

> **Codex / Claude Code skill** — install once, then ask the agent to analyze an Apple Health export from anywhere.

Self-contained, evidence-based HTML reports from Apple Watch / iPhone Health exports, powered by an agent skill that orchestrates the full pipeline.

| | |
|---|---|
| **Input** | Apple Health export ZIP (Apple names it differently per locale — pass any path; the parser auto-detects the XML inside). |
| **Output** | One self-contained `health_report.html` file — no CDN, no network, no tracking |
| **Languages** | EN · 中文 · ES · FR · DE · 日本語 · 한국어 (auto-detected from system) |
| **Theme** | Light/dark (auto-detected from `prefers-color-scheme`) |
| **Benchmarks** | AHA / WHO / AASM / ACSM / ESC — age and sex-adjusted from the export's `<Me>` profile |
| **Privacy** | All processing local. Nothing leaves your machine. |

---

## Features

- **20+ metrics tracked** — steps, exercise minutes, distance, resting HR, walking HR, HRV (SDNN), VO₂max, sleep duration + stages (Deep / REM / Core / Awake), SpO₂, respiratory rate, body mass, workouts by type and frequency.
- **Composite health score** — weighted 6-metric gauge (steps 20% · sleep 20% · RHR/HRV/VO₂/exercise 15% each) with letter grade.
- **Per-metric editorial callouts** — short "what this means" sentence with status zone.
- **Age & sex-adjusted thresholds** — VO₂max, HRV, deep sleep targets, walking HR, and steps (60+) automatically pick the appropriate ACSM / Shaffer / Tanaka / Paluch reference band.
- **Full citation chain** — every benchmark links to its primary literature source.
- **Locked-down disclaimer** — every report includes a "not medical advice" footer in the viewer's language.

---

## Quick start

### 1. Get your data

iPhone → **Health** app → tap your profile icon (top-right) → **Export All Health Data**. Save the resulting ZIP somewhere you can find it — Apple names the file according to your iPhone's locale (`export.zip`, `导出.zip`, etc.), but any name works.

### 2. Run the pipeline

```bash
git clone <repo> apple-health
cd apple-health
python3 health_parser.py --zip ~/Downloads/<your-export>.zip
python3 report_html.py --data ./latest_parsed
open ./latest_parsed/health_report.html
```

Parser takes ~1 minute per GB of XML. The report generator runs in <1 s.

### 3. (Optional) Install as an Agents skill

Clone the repo to your Agents user-level skills directory:

```bash
git clone <repo> ~/.agents/skills/apple-health
```

Then restart the agent app. Skills are triggered from natural-language prompts; they do **not** create custom slash commands.

Examples:

```
use apple-health to analyze ~/Downloads/<your-export>.zip
用 apple-health 分析 ~/Downloads/导出.zip
use apple-health --report
use apple-health q: my best sleep month?
```

### 4. (Optional) Install as a Claude Code skill

Clone the repo to your user-level skills directory, then link the slash command:

```bash
# 1. Install the skill (auto-discovery via SKILL.md frontmatter)
git clone <repo> ~/.claude/skills/apple-health

# 2. Link the /apple-health slash command into your user-level commands dir
mkdir -p ~/.claude/commands
ln -sf ~/.claude/skills/apple-health/.claude/commands/apple-health.md ~/.claude/commands/apple-health.md
```

Then **restart Claude Code** to pick up the new command. From any working directory:

```
/apple-health ~/Downloads/<your-export>.zip
/apple-health --report                    # regenerate HTML only
/apple-health q: my best sleep month?    # Q&A from parsed CSVs
```

The skill also auto-invokes when you mention Apple Health analysis in natural language (no slash command needed), because the description in `SKILL.md` triggers Claude's skill discovery.

---

## File structure

```
apple-health/
├── SKILL.md              # Skill manifest (frontmatter + invocation logic)
├── README.md             # This file
├── i18n.py               # ALL translations — single source of truth (7 langs)
├── benchmarks.py         # Numeric thresholds, scoring, age/sex level tables
├── health_parser.py      # Streaming SAX XML parser → CSV/JSON
├── report_data.py        # CSV loading + aggregation helpers
├── report_html.py        # HTML builder
├── report_css.py         # Static CSS constant
├── report_js.py          # Chart.js + i18n runtime
├── icon.svg              # Hero/favicon graphic
├── vendor/               # Cached Chart.js (downloaded on first run)
├── latest_raw/           # Extracted XML (gitignored — personal data)
└── latest_parsed/        # Parsed CSVs + HTML report (gitignored)
```

---

## Adding a language

All translations live in **`i18n.py`** — to add e.g. Italian:

1. Add `"it"` to `LANGS = [...]`
2. Add `"it": "IT"` to `LANG_NAMES`
3. Add an `"it": {...}` entry to each of `SEX_NAMES`, `HEADER`, `STATIC`, `WO_TYPES`, `NOTES`, `NOTES_TEMPLATES`, `INSIGHT[*]['head'/'detail'/...]`, `DISCLAIMER`

Re-run `report_html.py`. The new language joins the auto-detection list (matches viewers whose system reports `it-IT`, `it-CH`, etc.).

---

## Architecture

```
                  Apple Health export ZIP
                          │
                  health_parser.py        ← streaming SAX (handles 2 GB+ XML)
                          │
            latest_parsed/{daily,monthly,workouts,sleep,sources,meta}
                          │
                  report_html.py
                  ├── report_data.py      ← loaders + 90-day rolling averages
                  ├── benchmarks.py       ← apply age/sex profile → status zones
                  ├── i18n.py             ← all text (7 languages)
                  ├── report_css.py
                  └── report_js.py        ← Chart.js + i18n + theme detection
                          │
                  latest_parsed/health_report.html
```

The HTML is **fully self-contained** — Chart.js is inlined from `vendor/chart.min.js` (downloaded once on first run), the favicon is base64-embedded, and the system font stack falls back gracefully when Inter / JetBrains Mono / Space Grotesk are unavailable.

---

## Privacy

This skill **never sends data anywhere**. The only network call is a one-time `pip`-free download of `vendor/chart.min.js` (~200 kB) on first report generation. After that, you can run the pipeline fully offline. Apple Health exports contain extremely personal data (every heart rate measurement, every workout location, every sleep night since you got the watch) — the `.gitignore` excludes `latest_raw/` and `latest_parsed/` to prevent accidental commits.

---

## Not medical advice

This report visualizes data from a consumer-grade wearable. It cannot diagnose, treat, or prevent any medical condition. All thresholds are population-level guidelines from peer-reviewed sources — individual targets should be set with a healthcare provider. Apple Watch metrics (VO₂max, SpO₂, sleep stages) are estimates with lower accuracy than clinical instruments.

---

## License

[MIT](LICENSE)
