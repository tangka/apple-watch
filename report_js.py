"""JavaScript block builder for the Apple Health HTML report.

All static-label and workout-type translations are pulled from i18n.py and
embedded in the JS as compact JSON objects. Dynamic text (insights, notes)
is embedded directly in HTML data attributes by report_html.py.
"""
import json
import i18n


def js(v):
    if v is None:           return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, list): return "["+",".join(js(x) for x in v)+"]"
    if isinstance(v, str):  return '"'+v.replace('"','\\"')+'"'
    return str(v)


def build_js(d):
    mo_short      = d['mo_short']
    mo_steps      = d['mo_steps']
    mo_sleep      = d['mo_sleep']
    mo_sleep_deep = d['mo_sleep_deep']
    mo_sleep_rem  = d['mo_sleep_rem']
    mo_sleep_core = d['mo_sleep_core']
    mo_rhr        = d['mo_rhr']
    mo_walk_hr    = d['mo_walk_hr']
    mo_hrv        = d['mo_hrv']
    mo_vo2        = d['mo_vo2']
    mo_spo2       = d['mo_spo2']
    mo_resp       = d['mo_resp']
    mo_dist       = d['mo_dist']
    mo_kcal       = d['mo_kcal']
    mo_ex_weekly  = d['mo_ex_weekly']
    mo_weight     = d.get('mo_weight', [])
    avgs          = d['avgs']
    wo            = d['wo']
    health_score  = d['health_score']
    has_weight    = d['has_weight']
    daily         = d['daily']

    from report_data import recent_avg

    # Serialize i18n tables for embedding in JS
    langs_json     = json.dumps(i18n.LANGS, ensure_ascii=False)
    lang_names_json = json.dumps(i18n.LANG_NAMES, ensure_ascii=False)
    static_json    = json.dumps(i18n.STATIC, ensure_ascii=False)
    wo_types_json  = json.dumps(i18n.WO_TYPES, ensure_ascii=False)

    return f"""\
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
  const START = Math.PI * 0.75;
  const SWEEP = Math.PI * 1.5;

  const ZONES = [
    [0.00, 0.20, '#f87171'], [0.20, 0.40, '#fb923c'],
    [0.40, 0.60, '#facc15'], [0.60, 0.80, '#86efac'],
    [0.80, 1.00, '#4ade80'],
  ];
  function zoneColor(p) {{
    for (const [a,b,c] of ZONES) if (p <= b + 0.001) return c;
    return '#4ade80';
  }}

  function draw(pct) {{
    ctx.clearRect(0, 0, W, H);
    ctx.beginPath(); ctx.arc(cx, cy, R, START, START + SWEEP);
    ctx.strokeStyle = 'rgba(255,255,255,0.07)';
    ctx.lineWidth = LW; ctx.lineCap = 'butt'; ctx.stroke();
    for (const [zs, ze, col] of ZONES) {{
      ctx.beginPath();
      ctx.arc(cx, cy, R, START + SWEEP * zs, START + SWEEP * Math.min(ze, 1));
      ctx.strokeStyle = col + '2a';
      ctx.lineWidth = LW; ctx.lineCap = 'butt'; ctx.stroke();
    }}
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
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = '#374151';
    ctx.font = `${{Math.round(R * 0.13)}}px Inter, sans-serif`;
    for (const [frac, txt] of [[0,'0'],[0.5,'50'],[1,'100']]) {{
      const a = START + SWEEP * frac;
      const lr = R + LW * 0.9;
      ctx.fillText(txt, cx + lr * Math.cos(a), cy + lr * Math.sin(a));
    }}
    if (pct > 0) {{
      ctx.beginPath(); ctx.arc(cx, cy, R, START, START + SWEEP * pct);
      ctx.strokeStyle = zoneColor(pct);
      ctx.lineWidth = LW - 4; ctx.lineCap = 'round'; ctx.stroke();
      const tipA = START + SWEEP * pct;
      const tx = cx + R * Math.cos(tipA), ty = cy + R * Math.sin(tipA);
      const grd = ctx.createRadialGradient(tx, ty, 0, tx, ty, LW * 1.4);
      grd.addColorStop(0, zoneColor(pct) + 'aa');
      grd.addColorStop(1, 'transparent');
      ctx.fillStyle = grd;
      ctx.beginPath(); ctx.arc(tx, ty, LW * 1.4, 0, Math.PI * 2); ctx.fill();
    }}
    const needleA = START + SWEEP * pct;
    const nlen = R - LW * 0.5 - 4;
    const nx = cx + nlen * Math.cos(needleA), ny = cy + nlen * Math.sin(needleA);
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(nx, ny);
    ctx.strokeStyle = '#f1f5f9'; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#f1f5f9'; ctx.fill();
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = zoneColor(pct);
    ctx.font = `bold ${{Math.round(R * 0.52)}}px 'JetBrains Mono','SF Mono',monospace`;
    ctx.fillText(Math.round(pct * 100), cx, cy - R * 0.32);
  }}

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

// ════════════════════════════════════════════════════════════════════
// i18n — all translations sourced from i18n.py
// ════════════════════════════════════════════════════════════════════
const LANGS      = {langs_json};
const LANG_NAMES = {lang_names_json};
const STATIC     = {static_json};
const WO_TYPES   = {wo_types_json};
const WO_EN_LABELS = {js(wo['top_types'])};

let _lang = localStorage.getItem('aw-lang') || 'en';
if (!LANGS.includes(_lang)) _lang = 'en';

function toggleLang() {{
  const i = LANGS.indexOf(_lang);
  _lang = LANGS[(i + 1) % LANGS.length];
  localStorage.setItem('aw-lang', _lang);
  document.documentElement.lang = _lang;
  _applyLang();
}}

function _applyLang() {{
  const dict = STATIC[_lang] || {{}};
  // Static labels — look up by EN key
  document.querySelectorAll('[data-i18n]').forEach(el => {{
    const v = dict[el.dataset.i18n];
    el.innerHTML = v !== undefined ? v : el.dataset.i18nOrig;
  }});
  // Dynamic multi-lang text — JSON dict baked into the element
  document.querySelectorAll('[data-i18n-json]').forEach(el => {{
    let table;
    try {{ table = JSON.parse(el.dataset.i18nJson); }} catch(e) {{ return; }}
    const v = table[_lang] ?? table.en;
    if (v !== undefined) el.innerHTML = v;
  }});
  // Button: show NEXT language name as a hint of where the cycle goes
  const nextLang = LANGS[(LANGS.indexOf(_lang) + 1) % LANGS.length];
  document.getElementById('langBtn').textContent = LANG_NAMES[nextLang] || nextLang;
  // Workout types chart
  Object.values(Chart.instances).forEach(c => {{
    if (c.canvas && c.canvas.id === 'cWoTypes') {{
      const map = WO_TYPES[_lang] || {{}};
      c.data.labels = _lang === 'en'
        ? [...WO_EN_LABELS]
        : WO_EN_LABELS.map(l => map[l] || l);
      c.update('none');
    }}
  }});
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
  // Save original (EN) innerHTML so we can restore when switching back to EN
  document.querySelectorAll('[data-i18n]').forEach(el => {{
    el.dataset.i18nOrig = el.innerHTML;
  }});
  if (localStorage.getItem('aw-theme') === 'light') {{
    document.documentElement.classList.add('light');
    document.getElementById('themeBtn').textContent = '🌙';
  }}
  document.documentElement.lang = _lang;
  _applyLang();
}})();"""
