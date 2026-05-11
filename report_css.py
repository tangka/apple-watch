"""Static CSS for the Apple Health HTML report."""

CSS = """\
:root{
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
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.55;font-size:14px;overflow-x:hidden}
a{color:#7dd3fc;text-decoration:none}
a:hover{text-decoration:underline}

/* ── HERO ── */
.hero{
  position:relative;overflow:hidden;
  background:linear-gradient(160deg,#0a0f1e 0%,#0d1a3a 40%,#130d2e 100%);
  padding:56px 32px 48px;border-bottom:1px solid var(--border);
}
.hero-layout{display:flex;align-items:center;gap:40px;flex-wrap:wrap}
.hero-text{flex:1;min-width:260px}
.hero-gauge-wrap{
  flex-shrink:0;display:flex;flex-direction:column;align-items:center;gap:6px;
}
.gauge-grade-row{
  display:flex;align-items:baseline;gap:8px;
  font-family:'JetBrains Mono','SF Mono','Fira Code',monospace;
}
.hero::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 50% at 70% 40%,rgba(99,102,241,.18) 0%,transparent 70%),
             radial-gradient(ellipse 40% 60% at 20% 80%,rgba(34,211,238,.10) 0%,transparent 60%);
  pointer-events:none;
}
.hero-inner{position:relative;max-width:1060px;margin:0 auto}
.hero-eyebrow{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.72rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:#7dd3fc;margin-bottom:14px}
.hero h1{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:clamp(2rem,4vw,3rem);
  font-weight:700;line-height:1.1;
  background:linear-gradient(135deg,#e2e8f0 30%,#7dd3fc 70%,#a78bfa 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:10px}
.hero-sub{color:var(--muted);font-size:.88rem;margin-bottom:32px}

/* Hero key stats strip */
.hero-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));
  gap:1px;background:var(--border);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;max-width:700px}
.hs-cell{background:var(--surface2);padding:14px 16px}
.hs-val{font-family:'JetBrains Mono','SF Mono','Fira Code','Cascadia Code',monospace;font-size:1.35rem;font-weight:600;
  line-height:1;color:#f1f5f9}
.hs-lbl{font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);margin-top:4px}

/* ── WRAPPER ── */
.wrap{max-width:1060px;margin:0 auto;padding:40px 24px 80px}

/* ── SECTION ── */
.section{margin-top:56px}
.sec-head{display:flex;align-items:center;gap:10px;
  font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:1.15rem;font-weight:700;
  color:#f1f5f9;padding-bottom:12px;
  border-bottom:1px solid var(--border);margin-bottom:24px;
  position:relative}
.sec-head::after{content:'';position:absolute;bottom:-1px;left:0;width:48px;
  height:2px;background:var(--accent);border-radius:2px}
.sec-icon{font-size:1.1rem}

/* ── INSIGHT CALLOUT (Pudding-style editorial) ── */
.insight{
  border-left:3px solid var(--accent);
  background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 8%,transparent),transparent 60%);
  padding:14px 20px;border-radius:0 var(--radius) var(--radius) 0;
  margin-bottom:20px;
}
.insight-head{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:1.5rem;font-weight:700;
  color:var(--accent);line-height:1.15;margin-bottom:6px}
.insight-body{font-size:.82rem;color:#94a3b8;line-height:1.5}

/* ── STAT CARDS ── */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));
  gap:12px;margin-bottom:24px}
.stat-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px 14px;
  position:relative;overflow:hidden;min-width:0;
  transition:border-color .2s;
}
.stat-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:var(--accent);
}
.stat-card:hover{border-color:color-mix(in srgb,var(--accent) 40%,var(--border))}
.sc-title{font-size:.68rem;font-weight:600;text-transform:uppercase;
  letter-spacing:.05em;color:var(--muted);margin-bottom:8px}
.sc-value{
  font-family:'JetBrains Mono','SF Mono','Fira Code','Cascadia Code',monospace;
  font-size:clamp(1.35rem,5cqi,1.9rem);
  font-weight:600;line-height:1;
  white-space:nowrap;overflow:hidden;
}
.sc-unit{
  display:block;font-family:'Inter',sans-serif;
  font-size:.7rem;font-weight:400;color:var(--muted);margin-top:4px;
}
.sc-badge{display:inline-block;font-size:.67rem;font-weight:600;
  padding:2px 8px;border-radius:99px;border:1px solid;margin-top:8px}
.sc-note{font-size:.67rem;color:var(--dim);margin-top:6px;line-height:1.4}
.sc-src{font-size:.6rem;color:var(--dim);margin-top:4px}

/* ── CHARTS ── */
.chart-box{background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:18px 16px 12px;margin-bottom:16px}
.chart-title{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.78rem;
  font-weight:600;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;
  letter-spacing:.04em}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}

/* ── BENCHMARK GRID ── */
.bm-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:14px;margin-top:24px}
.bm-block{background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px}
.bm-title{font-family:'Space Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.8rem;font-weight:700;
  color:#e2e8f0;margin-bottom:10px}
.bm-tbl{width:100%;border-collapse:collapse;font-size:.75rem}
.bm-tbl td{padding:4px 6px;border-bottom:1px solid var(--grid)}
.bm-tbl tr:last-child td{border-bottom:none}
.bm-note{font-size:.7rem;color:var(--muted);margin-top:10px;line-height:1.45}
.bm-src{font-size:.65rem;color:var(--dim);margin-top:6px}

/* ── DIVIDER ── */
.divider{height:1px;background:var(--border);margin:56px 0}

/* ── DISCLAIMER ── */
.disclaimer{background:rgba(253,224,71,.06);border:1px solid rgba(253,224,71,.2);
  border-radius:var(--radius);padding:16px 20px;margin-top:48px;
  font-size:.78rem;color:#a16207;line-height:1.6}

html.light{
  --bg:#f8fafc; --bg2:#f1f5f9;
  --surface:rgba(0,0,0,.04); --surface2:rgba(0,0,0,.08);
  --border:rgba(0,0,0,.12); --text:#0f172a;
  --muted:#374151; --dim:#64748b; --grid:rgba(0,0,0,.07);
}
html.light .hero{
  background:linear-gradient(160deg,#e0f2fe 0%,#e0e7ff 40%,#ede9fe 100%);
  border-bottom-color:rgba(0,0,0,.1);
}
html.light a{color:#1d4ed8}
html.light .hero-eyebrow{color:#3b82f6}
html.light h1{
  background:linear-gradient(135deg,#0f172a 30%,#1d4ed8 70%,#7c3aed 100%);
  -webkit-background-clip:text;background-clip:text;
}
html.light .hs-val{color:#0f172a}
html.light .sec-head{color:#0f172a}
html.light .bm-title{color:#0f172a}
html.light .insight-body{color:#475569}
html.light .chart-title{color:#374151}
html.light .bm-tbl td{color:#374151 !important}
html.light .ctrl-btn{background:rgba(0,0,0,.06);border-color:rgba(0,0,0,.15)}
html.light .ctrl-btn:hover{background:rgba(0,0,0,.12)}
/* Controls bar */
.controls-bar{position:fixed;top:16px;right:16px;z-index:100;display:flex;gap:8px}
.ctrl-btn{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);
  border-radius:99px;padding:6px 14px;color:var(--text);font-size:.72rem;
  font-weight:600;cursor:pointer;backdrop-filter:blur(8px);
  transition:background .15s;font-family:inherit}
.ctrl-btn:hover{background:rgba(255,255,255,.18)}

@media(max-width:660px){
  .grid2,.grid3{grid-template-columns:1fr}
  .hero{padding:36px 20px 32px}
  .wrap{padding:24px 16px 60px}
  .hero h1{font-size:1.7rem}
}"""
