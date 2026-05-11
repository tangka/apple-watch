"""Data interpretation layer: benchmarks, scoring, and status lookup."""

BENCHMARKS = {
    "steps": {
        "label": "Daily Steps",  "unit": "steps/day",
        "accent": "#22d3ee",
        "levels": [(10000,None,"Highly Active","#4ade80"),(7500,9999,"Active","#86efac"),
                   (5000,7499,"Somewhat Active","#facc15"),(2500,4999,"Low Active","#fb923c"),
                   (0,2499,"Sedentary","#f87171")],
        "note": "≥7,000 steps/day → 50–70% lower all-cause mortality (Paluch 2022). AHA target: ≥10,000.",
        "note_zh": "≥7,000步/天与全因死亡率降低50–70%相关（Paluch 2022）。AHA目标：≥10,000步。",
        "source": "Paluch et al., JAMA Netw Open 2022; AHA",
        "url": "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2783711",
    },
    "exercise_min_week": {
        "label": "Exercise Min / Week",  "unit": "min/wk",
        "accent": "#22d3ee",
        "levels": [(150,None,"Meets Guidelines","#4ade80"),(75,149,"Partially Active","#facc15"),
                   (0,74,"Below Guidelines","#f87171")],
        "note": "≥150 min/wk moderate OR ≥75 min/wk vigorous + strength ×2/wk. Apple Watch Exercise Min = brisk-walk pace or above.",
        "note_zh": "每周≥150分钟中等强度 或 ≥75分钟高强度 + 每周2次力量训练。Apple Watch 运动分钟 = 快走配速及以上。",
        "source": "WHO 2020 Physical Activity Guidelines; AHA 2018",
        "url": "https://www.who.int/publications/i/item/9789240015128",
    },
    "resting_hr_bpm": {
        "label": "Resting Heart Rate",  "unit": "bpm",
        "accent": "#f472b6",
        "lower_is_better": True,
        "levels": [(0,59.9,"Athletic","#4ade80"),(60,70.9,"Optimal","#86efac"),
                   (71,85.9,"Normal","#a3e635"),(86,100.9,"Elevated","#facc15"),
                   (101,None,"Tachycardia","#f87171")],
        "note": "Normal: 60–100 bpm (AHA). Optimal zone 60–70 bpm is linked to lowest CV mortality risk.",
        "note_zh": "AHA正常范围：60–100 bpm。60–70 bpm区间与最低心血管死亡率相关。",
        "source": "AHA; Jouven et al., NEJM 2005",
        "url": "https://www.heart.org/en/health-topics/heart-rate",
    },
    "walking_hr_bpm": {
        "label": "Walking Heart Rate",  "unit": "bpm",
        "accent": "#fb7185",
        "lower_is_better": True,
        "levels": [(0,90.9,"Fit","#4ade80"),(91,110.9,"Average","#facc15"),
                   (111,None,"High","#f87171")],
        "note": "Lower walking HR reflects better aerobic fitness. Apple Watch records this during everyday walking throughout the day.",
        "note_zh": "步行心率越低反映有氧适能越好。Apple Watch 在日常步行中全天记录。",
        "source": "AHA; ACSM",
        "url": "https://www.heart.org/en/health-topics/heart-rate",
    },
    "hrv_sdnn_ms": {
        "label": "HRV — SDNN",  "unit": "ms",
        "accent": "#f472b6",
        "levels": [(50,None,"Good","#4ade80"),(30,49.9,"Fair","#facc15"),
                   (0,29.9,"Low","#f87171")],
        "note": "Higher SDNN = better autonomic balance. Trend matters more than absolute. Depressed by poor sleep, overtraining, alcohol, and stress.",
        "note_zh": "SDNN越高表示自主神经平衡越好。趋势比绝对值更重要。差睡眠、过度训练、饮酒和压力均会降低HRV。",
        "source": "ESC/NASPE Task Force, Eur Heart J 1996; Shaffer & Ginsberg, Front Public Health 2017",
        "url": "https://www.frontiersin.org/articles/10.3389/fpubh.2017.00258/full",
    },
    "vo2_max": {
        "label": "VO₂ Max",  "unit": "mL/kg/min",
        "accent": "#4ade80",
        "levels": [(48,None,"Excellent","#4ade80"),(42,47.9,"Good","#86efac"),
                   (37,41.9,"Fair","#facc15"),(33,36.9,"Poor","#fb923c"),
                   (0,32.9,"Very Poor","#f87171")],
        "note": "AHA/ACSM categories for adults ~40–49 (male ref; women ~10% lower). Apple Watch estimates indirectly. Low CRF is a major independent CV risk factor (AHA).",
        "note_zh": "AHA/ACSM成人心肺适能评级（约40–49岁男性参考；女性约低10%）。Apple Watch间接估算。低心肺适能是独立心血管风险因素（AHA）。",
        "source": "Ross et al., Circulation 2016; ACSM",
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000461",
    },
    "sleep_hours": {
        "label": "Sleep Duration",  "unit": "hrs/night",
        "accent": "#a78bfa",
        "levels": [(7,9,"Recommended","#4ade80"),(6,6.99,"Borderline","#facc15"),
                   (9,None,"Long Sleep","#facc15"),(0,5.99,"Insufficient","#f87171")],
        "note": "AASM/SRS: 7–9 hrs for adults. <7 hrs → elevated risk of obesity, diabetes, hypertension, and all-cause mortality.",
        "note_zh": "AASM/SRS推荐成人7–9小时睡眠。<7小时→肥胖、糖尿病、高血压及全因死亡率风险升高。",
        "source": "Watson et al., Sleep 2015 (AASM/SRS); NSF 2015",
        "url": "https://aasm.org/seven-or-more-hours-of-sleep-per-night-a-health-necessity-for-adults/",
    },
    "sleep_deep_h": {
        "label": "Deep Sleep (N3)",  "unit": "hrs",
        "accent": "#818cf8",
        "levels": [(1.0,None,"Good","#4ade80"),(0.5,0.99,"Fair","#facc15"),
                   (0,0.49,"Low","#f87171")],
        "note": "N3 (slow-wave) = 13–23% of total sleep (~1.0–1.7 h for 7–8 h). Critical for physical restoration and immune function.",
        "note_zh": "N3（慢波睡眠）= 总睡眠的13–23%（7–8小时约1.0–1.7小时）。对身体恢复和免疫功能至关重要。",
        "source": "AASM Staging; Hirshkowitz et al., Sleep Health 2015",
        "url": "https://pubmed.ncbi.nlm.nih.gov/29073398/",
    },
    "sleep_rem_h": {
        "label": "REM Sleep",  "unit": "hrs",
        "accent": "#c084fc",
        "levels": [(1.5,None,"Good","#4ade80"),(0.8,1.49,"Fair","#facc15"),
                   (0,0.79,"Low","#f87171")],
        "note": "REM = 20–25% of total sleep (~1.5–2.0 h). Critical for memory consolidation and emotional regulation. Suppressed by alcohol and some medications.",
        "note_zh": "REM = 总睡眠的20–25%（约1.5–2.0小时）。对记忆巩固和情绪调节至关重要。酒精和部分药物会抑制REM。",
        "source": "AASM; Hirshkowitz et al., Sleep Health 2015",
        "url": "https://pubmed.ncbi.nlm.nih.gov/29073398/",
    },
    "spo2": {
        "label": "Blood Oxygen (SpO₂)",  "unit": "%",
        "accent": "#38bdf8",
        "levels": [(95,None,"Normal","#4ade80"),(90,94.9,"Borderline","#facc15"),
                   (0,89.9,"Low","#f87171")],
        "note": "Normal SpO₂ is 95–100% at sea level. SpO₂ <90% = hypoxemia, warrants medical evaluation (AHA/ATS).",
        "note_zh": "正常血氧饱和度：海平面95–100%。SpO₂<90% = 低氧血症，需就医评估（AHA/ATS）。",
        "source": "AHA; ATS Statement; AASM",
        "url": "https://www.thoracic.org/statements/",
    },
    "respiratory_rate": {
        "label": "Respiratory Rate",  "unit": "br/min",
        "accent": "#38bdf8",
        "levels": [(12,19.9,"Normal","#4ade80"),(20,24.9,"Elevated","#facc15"),
                   (0,11.9,"Low","#facc15"),(25,None,"High","#f87171")],
        "note": "Normal resting rate: 12–20 breaths/min. Apple Watch measures during sleep.",
        "note_zh": "正常静息呼吸频率：12–20次/分钟。Apple Watch在睡眠中测量。",
        "source": "AHA; NICE Clinical Guidelines",
        "url": "https://www.heart.org/",
    },
}


_E,_G,_FA,_P,_VP = "#4ade80","#86efac","#facc15","#fb923c","#f87171"

# VO₂max — ACSM (Ross et al. Circulation 2016)
VO2MAX_LEVELS = {
    "male": {
        (20,29): [(51.1,None,"Excellent",_E),(45.4,51.0,"Good",_G),(41.7,45.3,"Fair",_FA),(37.1,41.6,"Poor",_P),(0,37.0,"Very Poor",_VP)],
        (30,39): [(49.3,None,"Excellent",_E),(43.9,49.2,"Good",_G),(39.9,43.8,"Fair",_FA),(35.7,39.8,"Poor",_P),(0,35.6,"Very Poor",_VP)],
        (40,49): [(47.2,None,"Excellent",_E),(41.8,47.1,"Good",_G),(37.1,41.7,"Fair",_FA),(33.0,37.0,"Poor",_P),(0,32.9,"Very Poor",_VP)],
        (50,59): [(43.4,None,"Excellent",_E),(38.1,43.3,"Good",_G),(33.9,38.0,"Fair",_FA),(30.2,33.8,"Poor",_P),(0,30.1,"Very Poor",_VP)],
        (60,99): [(41.0,None,"Excellent",_E),(35.8,40.9,"Good",_G),(31.5,35.7,"Fair",_FA),(26.9,31.4,"Poor",_P),(0,26.8,"Very Poor",_VP)],
    },
    "female": {
        (20,29): [(43.9,None,"Excellent",_E),(39.5,43.8,"Good",_G),(36.1,39.4,"Fair",_FA),(32.3,36.0,"Poor",_P),(0,32.2,"Very Poor",_VP)],
        (30,39): [(42.4,None,"Excellent",_E),(37.8,42.3,"Good",_G),(34.6,37.7,"Fair",_FA),(31.5,34.5,"Poor",_P),(0,31.4,"Very Poor",_VP)],
        (40,49): [(39.9,None,"Excellent",_E),(36.3,39.8,"Good",_G),(33.0,36.2,"Fair",_FA),(29.4,32.9,"Poor",_P),(0,29.3,"Very Poor",_VP)],
        (50,59): [(36.7,None,"Excellent",_E),(32.3,36.6,"Good",_G),(29.4,32.2,"Fair",_FA),(25.9,29.3,"Poor",_P),(0,25.8,"Very Poor",_VP)],
        (60,99): [(33.0,None,"Excellent",_E),(29.4,32.9,"Good",_G),(27.2,29.3,"Fair",_FA),(23.7,27.1,"Poor",_P),(0,23.6,"Very Poor",_VP)],
    },
}

# HRV SDNN — age+sex adjusted (Shaffer & Ginsberg, Front Public Health 2017;
# Nunan et al., Ann Noninvasive Electrocardiol 2010; Apple Watch population norms)
HRV_LEVELS = {
    "male": {
        (20,29): [(50,None,"Good",_E),(25,49.9,"Fair",_FA),(0,24.9,"Low",_VP)],
        (30,39): [(45,None,"Good",_E),(22,44.9,"Fair",_FA),(0,21.9,"Low",_VP)],
        (40,49): [(38,None,"Good",_E),(18,37.9,"Fair",_FA),(0,17.9,"Low",_VP)],
        (50,59): [(32,None,"Good",_E),(15,31.9,"Fair",_FA),(0,14.9,"Low",_VP)],
        (60,99): [(26,None,"Good",_E),(12,25.9,"Fair",_FA),(0,11.9,"Low",_VP)],
    },
    "female": {
        (20,29): [(45,None,"Good",_E),(22,44.9,"Fair",_FA),(0,21.9,"Low",_VP)],
        (30,39): [(40,None,"Good",_E),(18,39.9,"Fair",_FA),(0,17.9,"Low",_VP)],
        (40,49): [(32,None,"Good",_E),(15,31.9,"Fair",_FA),(0,14.9,"Low",_VP)],
        (50,59): [(26,None,"Good",_E),(12,25.9,"Fair",_FA),(0,11.9,"Low",_VP)],
        (60,99): [(20,None,"Good",_E),(10,19.9,"Fair",_FA),(0, 9.9,"Low",_VP)],
    },
}

# Deep sleep N3 — age adjusted (Hirshkowitz et al. Sleep Health 2015; AASM)
# N3 declines from ~20% of sleep in young adults to ~5–10% by age 60+
SLEEP_DEEP_LEVELS = {
    (20,39): [(1.0,None,"Good",_E),(0.5,0.99,"Fair",_FA),(0,0.49,"Low",_VP)],
    (40,59): [(0.7,None,"Good",_E),(0.3,0.69,"Fair",_FA),(0,0.29,"Low",_VP)],
    (60,99): [(0.4,None,"Good",_E),(0.2,0.39,"Fair",_FA),(0,0.19,"Low",_VP)],
}

# Walking HR — mild age adjustment (max HR declines ~0.7 bpm/yr; Tanaka et al. JACC 2001)
WALK_HR_LEVELS = {
    (20,39): [(0,90.9,"Fit",_E),(91,110.9,"Average",_FA),(111,None,"High",_VP)],
    (40,49): [(0,93.9,"Fit",_E),(94,112.9,"Average",_FA),(113,None,"High",_VP)],
    (50,59): [(0,97.9,"Fit",_E),(98,116.9,"Average",_FA),(117,None,"High",_VP)],
    (60,99): [(0,102.9,"Fit",_E),(103,120.9,"Average",_FA),(121,None,"High",_VP)],
}

# Steps — adjusted for 60+ (Paluch 2022 age-stratified analysis)
STEPS_LEVELS_60PLUS = [
    (8000,None,"Highly Active","#4ade80"),(6000,7999,"Active","#86efac"),
    (4000,5999,"Somewhat Active","#facc15"),(2000,3999,"Low Active","#fb923c"),
    (0,1999,"Sedentary","#f87171"),
]

def _age_tbl(table, age, sex=None):
    """Lookup levels from an age-keyed table, with optional sex dimension."""
    a = age or 30
    if sex is not None:
        sex_key = "female" if (sex or "").lower() in ("female","f") else "male"
        table = table.get(sex_key, next(iter(table.values())))
    for (lo, hi), levels in table.items():
        if lo <= a <= hi:
            return levels
    return next(iter(table.values()))

def apply_profile_benchmarks(age, sex):
    """Update all age/sex-sensitive BENCHMARKS entries in-place."""
    a = age or 30
    sex_display = sex.title() if sex else "Adult"

    BENCHMARKS["vo2_max"]["levels"] = _age_tbl(VO2MAX_LEVELS, a, sex)
    BENCHMARKS["vo2_max"]["note"] = (
        f"ACSM norms for {sex_display}, age {a}. "
        "Low CRF is a strong independent CV risk factor (AHA). "
        "Apple Watch estimates via outdoor walk/run (±3–5 mL/kg/min vs lab)."
    )
    BENCHMARKS["vo2_max"]["note_zh"] = (
        f"ACSM {sex_display}性年龄{a}岁标准。"
        "低心肺适能是强独立心血管风险因素（AHA）。"
        "Apple Watch通过户外步行/跑步估算（与实验室相比误差±3–5 mL/kg/min）。"
    )

    BENCHMARKS["hrv_sdnn_ms"]["levels"] = _age_tbl(HRV_LEVELS, a, sex)
    BENCHMARKS["hrv_sdnn_ms"]["note"] = (
        f"Age-adjusted norms for {sex_display}, age {a} "
        "(Shaffer & Ginsberg 2017; Nunan 2010). "
        "HRV declines ~1–2% per year with age. Trend over months matters more than any single value."
    )
    BENCHMARKS["hrv_sdnn_ms"]["note_zh"] = (
        f"{sex_display}性年龄{a}岁标准（Shaffer & Ginsberg 2017；Nunan 2010）。"
        "HRV随年龄每年下降约1–2%。月度趋势比单次数值更重要。"
    )

    BENCHMARKS["sleep_deep_h"]["levels"] = _age_tbl(SLEEP_DEEP_LEVELS, a)
    BENCHMARKS["sleep_deep_h"]["note"] = (
        f"N3 (slow-wave) naturally declines with age; target adjusted for age {a}. "
        "Critical for physical restoration, immune function, and memory consolidation (AASM)."
    )
    BENCHMARKS["sleep_deep_h"]["note_zh"] = (
        f"N3（慢波睡眠）随年龄自然下降，已根据年龄{a}岁调整目标。"
        "对身体恢复、免疫功能和记忆巩固至关重要（AASM）。"
    )

    BENCHMARKS["walking_hr_bpm"]["levels"] = _age_tbl(WALK_HR_LEVELS, a)
    BENCHMARKS["walking_hr_bpm"]["note"] = (
        f"Lower walking HR reflects better aerobic fitness (age {a}). "
        "Max HR ≈ 208 − 0.7×age (Tanaka 2001); thresholds adjusted accordingly."
    )
    BENCHMARKS["walking_hr_bpm"]["note_zh"] = (
        f"步行心率越低反映有氧适能越好（年龄{a}岁）。"
        "最大心率 ≈ 208 − 0.7×年龄（Tanaka 2001），阈值据此调整。"
    )

    if a >= 60:
        BENCHMARKS["steps"]["levels"] = STEPS_LEVELS_60PLUS
        BENCHMARKS["steps"]["note"] = (
            "≥6,000 steps/day associated with 50–70% lower all-cause mortality in adults 60+ "
            "(Paluch 2022 age-stratified analysis). AHA target: ≥8,000."
        )
        BENCHMARKS["steps"]["note_zh"] = (
            "≥6,000步/天与60岁以上人群全因死亡率降低50–70%相关"
            "（Paluch 2022年龄分层分析）。AHA目标：≥8,000步。"
        )


SCORE_MAP = {
    "steps":             {"Highly Active":100,"Active":78,"Somewhat Active":56,"Low Active":34,"Sedentary":12},
    "exercise_min_week": {"Meets Guidelines":100,"Partially Active":58,"Below Guidelines":18},
    "resting_hr_bpm":    {"Athletic":100,"Optimal":85,"Normal":65,"Elevated":35,"Tachycardia":10},
    "hrv_sdnn_ms":       {"Good":100,"Fair":58,"Low":18},
    "vo2_max":           {"Excellent":100,"Good":78,"Fair":56,"Poor":34,"Very Poor":12},
    "sleep_hours":       {"Recommended":100,"Long Sleep":65,"Borderline":50,"Insufficient":18},
}
SCORE_WEIGHTS = {
    "steps":0.20,"exercise_min_week":0.15,"resting_hr_bpm":0.15,
    "hrv_sdnn_ms":0.15,"vo2_max":0.15,"sleep_hours":0.20,
}

def compute_health_score(avgs):
    tw = ws = 0.0
    for key, w in SCORE_WEIGHTS.items():
        v = avgs.get(key)
        if v is None: continue
        label, _ = get_status(v, key)
        s = SCORE_MAP.get(key, {}).get(label)
        if s is None: continue
        ws += s * w; tw += w
    if tw < 0.3: return None
    return round(ws / tw)

def score_grade(score):
    if score is None: return "—", "#475569", "No Data"
    if score >= 85:   return "A", "#4ade80",  "Excellent"
    if score >= 70:   return "B", "#86efac",  "Good"
    if score >= 55:   return "C", "#facc15",  "Fair"
    if score >= 40:   return "D", "#fb923c",  "Below Average"
    return                        "F", "#f87171",  "Poor"

def get_status(value, key):
    if value is None: return "No Data", "#475569"
    for lo, hi, label, color in BENCHMARKS.get(key, {}).get("levels", []):
        lo = lo if lo is not None else float("-inf")
        hi = hi if hi is not None else float("inf")
        if lo <= value <= hi: return label, color
    return "—", "#475569"
