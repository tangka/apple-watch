# /apple-health

Explicit slash-command entry point for the **apple-health skill**. The skill's
authoritative instructions live in `SKILL.md` at the project root — read it
first, then follow the routing below.

## Routing $ARGUMENTS

| Pattern | Mode |
|---|---|
| `*.zip` (path to Apple Health export) | full pipeline — parse + report + open |
| `--report` or empty + `latest_parsed/` exists | report-only — skip parsing |
| starts with `q: <question>` | Q&A from parsed CSVs |
| empty + no parsed data | ask the user for the export ZIP path |

## Locate scripts

The Python scripts (`health_parser.py`, `report_html.py`, …) sit alongside
this command file's parent project. Resolve `$SCRIPT_DIR` from the
project-root marker (presence of `SKILL.md`):

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)"
[ ! -f "$SCRIPT_DIR/SKILL.md" ] && SCRIPT_DIR="$HOME/.claude/skills/apple-health"
```

## Commands

```bash
# Full pipeline (parse takes ~1 min per GB of XML)
python3 "$SCRIPT_DIR/health_parser.py" --zip "$ZIP_PATH"
python3 "$SCRIPT_DIR/report_html.py"   --data "$SCRIPT_DIR/latest_parsed"
open "$SCRIPT_DIR/latest_parsed/health_report.html"
```

After opening the report, brief the user on the 5 hero metrics (steps,
sleep, RHR, HRV, VO₂max) with status and benchmark context. Always
include the "not medical advice" disclaimer.

For Q&A mode, read `latest_parsed/*.csv` directly. See `SKILL.md` for the
column schema and benchmark citation list. **SpO₂ is decimal (0.97 = 97%)
— scale before comparing.**
