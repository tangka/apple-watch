"""JavaScript block builder for the Apple Health HTML report."""
import json


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
  "bpm":"bpm","ms":"毫秒","mL/kg/min":"mL/kg/min",
  "hrs/night":"小时/晚","hrs":"小时","%":"%","br/min":"次/分",
  "hero.title":"你的健康数据，<br>数字说话",
  "days":"天","workouts":"次锻炼","Male":"男","Female":"女",
  "Generated":"生成于","age":"年龄",
  "gauge.desc1":"加权综合 · 6项指标 · 90天均值",
  "gauge.desc2":"步数20% · 睡眠20% · 静心率/HRV/摄氧量/运动各15%",
  "Monthly Average Daily Steps":"月均日步数",
  "Exercise Minutes / Week (monthly avg)":"每周运动时长（月均）",
  "Average Daily Distance (km)":"日均距离（公里）",
  "Resting Heart Rate (bpm)":"静息心率（bpm）",
  "HRV — SDNN (ms)":"心率变异性 — SDNN（毫秒）",
  "Walking Heart Rate (bpm)":"步行心率（bpm）",
  "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"最大摄氧量（毫升/千克/分钟）— Apple Watch 估算",
  "Monthly Average Sleep Duration (hrs/night)":"月均睡眠时长（小时/晚）",
  "Sleep Stages by Month — Stacked (hrs/night)":"月度睡眠阶段堆叠（小时/晚）",
  "Sleep Stages — 90-Day Average (hrs/night)":"睡眠阶段 — 90天均值（小时/晚）",
  "Blood Oxygen SpO₂ (%)":"血氧饱和度 SpO₂（%）",
  "Respiratory Rate (breaths/min, measured during sleep)":"呼吸频率（次/分钟，睡眠中测量）",
  "Monthly Average Body Mass (kg)":"月均体重（公斤）",
  "Workout Type Distribution":"锻炼类型分布",
  "Workouts per Month":"每月锻炼次数",
}};

const WO_TYPE_ZH = {{
  // 球类运动
  "AmericanFootball":"美式橄榄球","AustralianFootball":"澳式橄榄球",
  "Badminton":"羽毛球","Baseball":"棒球","Basketball":"篮球",
  "Bowling":"保龄球","Cricket":"板球","Curling":"冰壶",
  "Handball":"手球","Hockey":"曲棍球","Lacrosse":"长曲棍球",
  "Pickleball":"匹克球","Rugby":"橄榄球","Soccer":"足球",
  "Softball":"垒球","Squash":"壁球","TableTennis":"乒乓球",
  "Tennis":"网球","Volleyball":"排球",
  // 格斗 / 武术
  "Boxing":"拳击","Fencing":"击剑","MartialArts":"武术",
  "Wrestling":"摔跤","Kickboxing":"踢拳",
  // 跑步 / 步行 / 骑行
  "Running":"跑步","Walking":"步行","Cycling":"骑行",
  "HandCycling":"手摇自行车",
  "WheelchairWalkPace":"轮椅慢行","WheelchairRunPace":"轮椅快行",
  // 有氧 / 力量
  "CrossTraining":"综合训练","MixedCardio":"混合有氧",
  "HighIntensityIntervalTraining":"HIIT","JumpRope":"跳绳",
  "StepTraining":"踏步训练","Stairs":"爬楼梯",
  "StairClimbing":"登楼梯机","Elliptical":"椭圆机",
  "Rowing":"划船机","FunctionalStrengthTraining":"功能性力量训练",
  "TraditionalStrengthTraining":"传统力量训练",
  "CoreTraining":"核心训练","Flexibility":"柔韧性训练",
  // 身心 / 舞蹈
  "Yoga":"瑜伽","Pilates":"普拉提","Barre":"芭蕾把杆",
  "TaiChi":"太极拳","MindAndBody":"身心冥想",
  "Dance":"舞蹈","CardioDance":"有氧舞蹈","SocialDance":"社交舞",
  // 户外 / 登山
  "Hiking":"登山/徒步","Climbing":"攀岩",
  "CrossCountrySkiing":"越野滑雪","DownhillSkiing":"高山滑雪",
  "Snowboarding":"单板滑雪","SnowSports":"雪上运动",
  // 水上
  "Swimming":"游泳（室内/室外）","SwimmingOpenWater":"开放水域游泳",
  "WaterFitness":"水中健身","WaterPolo":"水球",
  "WaterSports":"水上运动","SurfingSports":"冲浪","Sailing":"帆船",
  "PaddleSports":"桨板/皮划艇","UnderwaterDiving":"潜水",
  // 冰上
  "SkatingSports":"冰/滑轮运动",
  // 其他竞技
  "Archery":"射箭","Golf":"高尔夫","Gymnastics":"体操",
  "Racquetball":"回力球","TrackAndField":"田径",
  "EquestrianSports":"马术","DiscSports":"飞盘运动",
  "RacketSports":"拍类运动",
  // 日常 / 特殊
  "Fishing":"钓鱼","Hunting":"狩猎","Play":"休闲游玩",
  "PreparationAndRecovery":"准备与恢复","Cooldown":"整理放松",
  "FitnessGaming":"健身游戏","Transition":"过渡（铁三）",
  "MixedMetabolicCardioTraining":"混合代谢有氧",
  "Other":"其他","Unknown":"未知",
}};
const WO_EN_LABELS = {js(wo['top_types'])};

let _lang = localStorage.getItem('aw-lang') || 'en';
function toggleLang() {{
  _lang = _lang === 'en' ? 'zh' : 'en';
  localStorage.setItem('aw-lang', _lang);
  document.documentElement.classList.toggle('zh', _lang === 'zh');
  _applyLang();
}}
function _applyLang() {{
  const dict = _lang === 'zh' ? ZH : {{}};
  document.querySelectorAll('[data-i18n]').forEach(el => {{
    const v = dict[el.dataset.i18n];
    el.innerHTML = v !== undefined ? v : el.dataset.i18nOrig;
  }});
  document.getElementById('langBtn').textContent = _lang === 'en' ? '中文' : 'EN';
  Object.values(Chart.instances).forEach(c => {{
    if (c.canvas && c.canvas.id === 'cWoTypes') {{
      c.data.labels = _lang === 'zh'
        ? WO_EN_LABELS.map(l => WO_TYPE_ZH[l] || l)
        : [...WO_EN_LABELS];
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
  document.querySelectorAll('[data-i18n]').forEach(el => {{
    el.dataset.i18nOrig = el.innerHTML;
  }});
  if (localStorage.getItem('aw-lang') === 'zh') {{
    document.documentElement.classList.add('zh');
  }}
  if (localStorage.getItem('aw-theme') === 'light') {{
    document.documentElement.classList.add('light');
    document.getElementById('themeBtn').textContent = '🌙';
  }}
  _applyLang();
}})();"""
