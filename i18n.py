"""Single source of truth for all human-readable text in the Apple Health report.

Translators only need to edit this file.

Structure
─────────
  LANGS, LANG_NAMES        — supported languages
  STATIC[lang][key]        — UI labels (sections, status levels, units, hero)
  WO_TYPES[lang][type]     — Apple HKWorkoutActivityType display names
  NOTES[metric][lang]      — Static benchmark notes (no interpolation)
  NOTES_TEMPLATES[metric][lang] — Dynamic notes with {sex},{age} placeholders
  SEX_NAMES[lang][m|f|x]   — Sex display strings for {sex} interpolation
  INSIGHT[metric]          — Insight callout templates per metric
    .head[lang]            — Headline template (uses {val})
    .detail[variant][lang] — Body template; variant key depends on metric:
                              steps:  above | below
                              exercise_min_week: yes | no
                              sleep_hours: short | ok
                              resting_hr_bpm, vo2_max, hrv_sdnn_ms: default
  DISCLAIMER[lang]         — Full disclaimer body
  HEADER[lang]             — Report header eyebrow text
"""

# ─────────────────────────────────────────────────────────────────────────────
# Supported languages
# ─────────────────────────────────────────────────────────────────────────────

LANGS = ["en", "zh", "es", "fr", "de", "ja", "ko"]

LANG_NAMES = {
    "en": "EN", "zh": "中文", "es": "ES", "fr": "FR",
    "de": "DE", "ja": "日本語", "ko": "한국어",
}


# ─────────────────────────────────────────────────────────────────────────────
# Sex display names (used in dynamic note interpolation)
# ─────────────────────────────────────────────────────────────────────────────

SEX_NAMES = {
    "en": {"male":"Male","female":"Female","other":"Adult"},
    "zh": {"male":"男","female":"女","other":"成人"},
    "es": {"male":"hombre","female":"mujer","other":"adulto"},
    "fr": {"male":"homme","female":"femme","other":"adulte"},
    "de": {"male":"Männlich","female":"Weiblich","other":"Erwachsene"},
    "ja": {"male":"男性","female":"女性","other":"成人"},
    "ko": {"male":"남성","female":"여성","other":"성인"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Report header eyebrow
# ─────────────────────────────────────────────────────────────────────────────

HEADER = {
    "en":"Apple Watch · Health Report",
    "zh":"Apple Watch · 健康报告",
    "es":"Apple Watch · Informe de salud",
    "fr":"Apple Watch · Rapport de santé",
    "de":"Apple Watch · Gesundheitsbericht",
    "ja":"Apple Watch · 健康レポート",
    "ko":"Apple Watch · 건강 보고서",
}


# ─────────────────────────────────────────────────────────────────────────────
# Static UI labels — key matches EN source, dict provides translations
# (Missing keys fall back to EN.)
# ─────────────────────────────────────────────────────────────────────────────

STATIC = {

"zh": {
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
    "Below Average":"低于均值","No Data":"暂无数据",
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
    "For wellness awareness only.":"仅供健康参考。",
},

"es": {
    "Activity":"Actividad","Cardiovascular Health":"Salud cardiovascular",
    "Cardiorespiratory Fitness":"Aptitud cardiorrespiratoria","Sleep":"Sueño",
    "Vitals":"Signos vitales","Body Weight":"Peso corporal","Workouts":"Entrenamientos",
    "Daily Steps":"Pasos diarios","Exercise Min / Week":"Min. ejercicio / semana",
    "Resting Heart Rate":"Frec. cardíaca en reposo","Walking Heart Rate":"Frec. cardíaca al caminar",
    "HRV — SDNN":"VFC — SDNN","VO₂ Max":"VO₂ máx.",
    "Sleep Duration":"Duración del sueño","Deep Sleep (N3)":"Sueño profundo (N3)",
    "REM Sleep":"Sueño REM","Blood Oxygen (SpO₂)":"Oxígeno en sangre (SpO₂)",
    "Respiratory Rate":"Frec. respiratoria",
    "Total Workouts":"Entrenamientos totales","Total Hours":"Horas totales","Total Distance":"Distancia total",
    "Highly Active":"Muy activo","Active":"Activo","Somewhat Active":"Moderadamente activo",
    "Low Active":"Poco activo","Sedentary":"Sedentario",
    "Meets Guidelines":"Cumple las guías","Partially Active":"Parcialmente activo","Below Guidelines":"Bajo las guías",
    "Athletic":"Atlético","Optimal":"Óptimo","Normal":"Normal",
    "Elevated":"Elevado","Tachycardia":"Taquicardia",
    "Fit":"En forma","Average":"Promedio","High":"Alto",
    "Good":"Bueno","Fair":"Regular","Low":"Bajo",
    "Excellent":"Excelente","Poor":"Bajo","Very Poor":"Muy bajo",
    "Recommended":"Recomendado","Borderline":"Límite",
    "Long Sleep":"Sueño prolongado","Insufficient":"Insuficiente",
    "Below Average":"Bajo el promedio","No Data":"Sin datos",
    "Health Score":"Puntuación de salud",
    "steps/day":"pasos/día","sleep hrs":"h. de sueño","resting HR":"FC en reposo",
    "HRV ms":"VFC ms","VO₂max":"VO₂máx.","min/wk":"min/sem.",
    "sessions":"sesiones","hours":"horas","km":"km",
    "bpm":"ppm","ms":"ms","mL/kg/min":"mL/kg/min",
    "hrs/night":"h/noche","hrs":"horas","%":"%","br/min":"resp./min",
    "hero.title":"Tus datos de salud,<br>en números",
    "days":"días","workouts":"entrenamientos","Male":"Hombre","Female":"Mujer",
    "Generated":"Generado","age":"edad",
    "gauge.desc1":"Compuesto ponderado · 6 métricas · prom. 90 días",
    "gauge.desc2":"Pasos 20% · Sueño 20% · FC/VFC/VO₂/Ej. 15% c/u",
    "Monthly Average Daily Steps":"Promedio mensual de pasos diarios",
    "Exercise Minutes / Week (monthly avg)":"Min. ejercicio / semana (prom. mensual)",
    "Average Daily Distance (km)":"Distancia diaria promedio (km)",
    "Resting Heart Rate (bpm)":"Frec. cardíaca en reposo (ppm)",
    "HRV — SDNN (ms)":"VFC — SDNN (ms)",
    "Walking Heart Rate (bpm)":"Frec. cardíaca al caminar (ppm)",
    "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"VO₂ máx. (mL/kg/min) — estimación Apple Watch",
    "Monthly Average Sleep Duration (hrs/night)":"Duración media del sueño (h/noche)",
    "Sleep Stages by Month — Stacked (hrs/night)":"Fases del sueño por mes — Apilado (h/noche)",
    "Sleep Stages — 90-Day Average (hrs/night)":"Fases del sueño — prom. 90 días (h/noche)",
    "Blood Oxygen SpO₂ (%)":"Oxígeno en sangre SpO₂ (%)",
    "Respiratory Rate (breaths/min, measured during sleep)":"Frec. respiratoria (resp./min, medida durante el sueño)",
    "Monthly Average Body Mass (kg)":"Peso corporal mensual promedio (kg)",
    "Workout Type Distribution":"Distribución de tipos de entrenamiento",
    "Workouts per Month":"Entrenamientos por mes",
    "For wellness awareness only.":"Solo para concienciación sobre el bienestar.",
},

"fr": {
    "Activity":"Activité","Cardiovascular Health":"Santé cardiovasculaire",
    "Cardiorespiratory Fitness":"Aptitude cardio-respiratoire","Sleep":"Sommeil",
    "Vitals":"Signes vitaux","Body Weight":"Poids corporel","Workouts":"Entraînements",
    "Daily Steps":"Pas quotidiens","Exercise Min / Week":"Min. exercice / semaine",
    "Resting Heart Rate":"Fréq. cardiaque au repos","Walking Heart Rate":"Fréq. cardiaque à la marche",
    "HRV — SDNN":"VRC — SDNN","VO₂ Max":"VO₂ max.",
    "Sleep Duration":"Durée du sommeil","Deep Sleep (N3)":"Sommeil profond (N3)",
    "REM Sleep":"Sommeil paradoxal","Blood Oxygen (SpO₂)":"Oxygène sanguin (SpO₂)",
    "Respiratory Rate":"Fréq. respiratoire",
    "Total Workouts":"Total entraînements","Total Hours":"Heures totales","Total Distance":"Distance totale",
    "Highly Active":"Très actif","Active":"Actif","Somewhat Active":"Modérément actif",
    "Low Active":"Peu actif","Sedentary":"Sédentaire",
    "Meets Guidelines":"Conforme aux recomm.","Partially Active":"Partiellement actif","Below Guidelines":"Sous les recomm.",
    "Athletic":"Athlétique","Optimal":"Optimal","Normal":"Normal",
    "Elevated":"Élevé","Tachycardia":"Tachycardie",
    "Fit":"En forme","Average":"Moyen","High":"Élevé",
    "Good":"Bien","Fair":"Correct","Low":"Bas",
    "Excellent":"Excellent","Poor":"Faible","Very Poor":"Très faible",
    "Recommended":"Recommandé","Borderline":"Limite",
    "Long Sleep":"Sommeil long","Insufficient":"Insuffisant",
    "Below Average":"Sous la moyenne","No Data":"Aucune donnée",
    "Health Score":"Score de santé",
    "steps/day":"pas/jour","sleep hrs":"h. de sommeil","resting HR":"FC au repos",
    "HRV ms":"VRC ms","VO₂max":"VO₂max.","min/wk":"min/sem.",
    "sessions":"séances","hours":"heures","km":"km",
    "bpm":"bpm","ms":"ms","mL/kg/min":"mL/kg/min",
    "hrs/night":"h/nuit","hrs":"heures","%":"%","br/min":"resp./min",
    "hero.title":"Vos données de santé,<br>en chiffres",
    "days":"jours","workouts":"entraînements","Male":"Homme","Female":"Femme",
    "Generated":"Généré","age":"âge",
    "gauge.desc1":"Composite pondéré · 6 métriques · moy. 90 j",
    "gauge.desc2":"Pas 20% · Sommeil 20% · FC/VRC/VO₂/Ex. 15% ch.",
    "Monthly Average Daily Steps":"Moyenne mensuelle des pas quotidiens",
    "Exercise Minutes / Week (monthly avg)":"Min. exercice / semaine (moy. mensuelle)",
    "Average Daily Distance (km)":"Distance quotidienne moyenne (km)",
    "Resting Heart Rate (bpm)":"Fréq. cardiaque au repos (bpm)",
    "HRV — SDNN (ms)":"VRC — SDNN (ms)",
    "Walking Heart Rate (bpm)":"Fréq. cardiaque à la marche (bpm)",
    "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"VO₂ max. (mL/kg/min) — estimation Apple Watch",
    "Monthly Average Sleep Duration (hrs/night)":"Durée moyenne du sommeil (h/nuit)",
    "Sleep Stages by Month — Stacked (hrs/night)":"Phases de sommeil par mois — Empilé (h/nuit)",
    "Sleep Stages — 90-Day Average (hrs/night)":"Phases de sommeil — moy. 90 j (h/nuit)",
    "Blood Oxygen SpO₂ (%)":"Oxygène sanguin SpO₂ (%)",
    "Respiratory Rate (breaths/min, measured during sleep)":"Fréq. respiratoire (resp./min, pendant le sommeil)",
    "Monthly Average Body Mass (kg)":"Poids corporel mensuel moyen (kg)",
    "Workout Type Distribution":"Répartition des types d'entraînement",
    "Workouts per Month":"Entraînements par mois",
    "For wellness awareness only.":"À titre informatif uniquement.",
},

"de": {
    "Activity":"Aktivität","Cardiovascular Health":"Herz-Kreislauf-Gesundheit",
    "Cardiorespiratory Fitness":"Kardiorespiratorische Fitness","Sleep":"Schlaf",
    "Vitals":"Vitalwerte","Body Weight":"Körpergewicht","Workouts":"Training",
    "Daily Steps":"Tägliche Schritte","Exercise Min / Week":"Trainingsmin. / Woche",
    "Resting Heart Rate":"Ruheherzfrequenz","Walking Heart Rate":"Gehherzfrequenz",
    "HRV — SDNN":"HRV — SDNN","VO₂ Max":"VO₂ max.",
    "Sleep Duration":"Schlafdauer","Deep Sleep (N3)":"Tiefschlaf (N3)",
    "REM Sleep":"REM-Schlaf","Blood Oxygen (SpO₂)":"Blutsauerstoff (SpO₂)",
    "Respiratory Rate":"Atemfrequenz",
    "Total Workouts":"Trainings gesamt","Total Hours":"Stunden gesamt","Total Distance":"Distanz gesamt",
    "Highly Active":"Sehr aktiv","Active":"Aktiv","Somewhat Active":"Mäßig aktiv",
    "Low Active":"Wenig aktiv","Sedentary":"Sitzend",
    "Meets Guidelines":"Empfehlung erfüllt","Partially Active":"Teilweise aktiv","Below Guidelines":"Unter der Empfehlung",
    "Athletic":"Athletisch","Optimal":"Optimal","Normal":"Normal",
    "Elevated":"Erhöht","Tachycardia":"Tachykardie",
    "Fit":"Fit","Average":"Durchschnittlich","High":"Hoch",
    "Good":"Gut","Fair":"Mäßig","Low":"Niedrig",
    "Excellent":"Ausgezeichnet","Poor":"Schlecht","Very Poor":"Sehr schlecht",
    "Recommended":"Empfohlen","Borderline":"Grenzwertig",
    "Long Sleep":"Langer Schlaf","Insufficient":"Unzureichend",
    "Below Average":"Unterdurchschnittlich","No Data":"Keine Daten",
    "Health Score":"Gesundheitsscore",
    "steps/day":"Schritte/Tag","sleep hrs":"Schlaf-Std.","resting HR":"Ruhepuls",
    "HRV ms":"HRV ms","VO₂max":"VO₂max.","min/wk":"Min./Wo.",
    "sessions":"Einheiten","hours":"Stunden","km":"km",
    "bpm":"Spm","ms":"ms","mL/kg/min":"mL/kg/min",
    "hrs/night":"Std./Nacht","hrs":"Std.","%":"%","br/min":"Atemz./min",
    "hero.title":"Deine Gesundheitsdaten,<br>in Zahlen",
    "days":"Tage","workouts":"Trainings","Male":"Männlich","Female":"Weiblich",
    "Generated":"Erstellt","age":"Alter",
    "gauge.desc1":"Gewichtetes Komposit · 6 Metriken · 90-Tage-Ø",
    "gauge.desc2":"Schritte 20% · Schlaf 20% · RHF/HRV/VO₂/Ex. je 15%",
    "Monthly Average Daily Steps":"Monatl. Durchschnitt täglicher Schritte",
    "Exercise Minutes / Week (monthly avg)":"Trainingsmin. / Woche (Monatsdurchschnitt)",
    "Average Daily Distance (km)":"Tägliche Durchschnittsdistanz (km)",
    "Resting Heart Rate (bpm)":"Ruheherzfrequenz (Spm)",
    "HRV — SDNN (ms)":"HRV — SDNN (ms)",
    "Walking Heart Rate (bpm)":"Gehherzfrequenz (Spm)",
    "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"VO₂ max. (mL/kg/min) — Apple Watch Schätzung",
    "Monthly Average Sleep Duration (hrs/night)":"Durchschnittliche Schlafdauer (Std./Nacht)",
    "Sleep Stages by Month — Stacked (hrs/night)":"Schlafphasen pro Monat — Gestapelt (Std./Nacht)",
    "Sleep Stages — 90-Day Average (hrs/night)":"Schlafphasen — 90-Tage-Ø (Std./Nacht)",
    "Blood Oxygen SpO₂ (%)":"Blutsauerstoff SpO₂ (%)",
    "Respiratory Rate (breaths/min, measured during sleep)":"Atemfrequenz (Atemz./min, im Schlaf gemessen)",
    "Monthly Average Body Mass (kg)":"Monatl. Durchschnittsgewicht (kg)",
    "Workout Type Distribution":"Trainingstyp-Verteilung",
    "Workouts per Month":"Trainings pro Monat",
    "For wellness awareness only.":"Nur zur Information über das Wohlbefinden.",
},

"ja": {
    "Activity":"アクティビティ","Cardiovascular Health":"心血管の健康",
    "Cardiorespiratory Fitness":"心肺機能","Sleep":"睡眠",
    "Vitals":"バイタル","Body Weight":"体重","Workouts":"ワークアウト",
    "Daily Steps":"1日の歩数","Exercise Min / Week":"運動分/週",
    "Resting Heart Rate":"安静時心拍数","Walking Heart Rate":"歩行時心拍数",
    "HRV — SDNN":"心拍変動 — SDNN","VO₂ Max":"VO₂最大値",
    "Sleep Duration":"睡眠時間","Deep Sleep (N3)":"深睡眠（N3）",
    "REM Sleep":"レム睡眠","Blood Oxygen (SpO₂)":"血中酸素濃度（SpO₂）",
    "Respiratory Rate":"呼吸数",
    "Total Workouts":"合計ワークアウト数","Total Hours":"合計時間","Total Distance":"合計距離",
    "Highly Active":"非常に活発","Active":"活発","Somewhat Active":"やや活発",
    "Low Active":"低活動","Sedentary":"座りがち",
    "Meets Guidelines":"基準達成","Partially Active":"部分的達成","Below Guidelines":"基準未達",
    "Athletic":"アスリート級","Optimal":"最適","Normal":"普通",
    "Elevated":"高め","Tachycardia":"頻脈",
    "Fit":"体力あり","Average":"平均","High":"高い",
    "Good":"良好","Fair":"普通","Low":"低い",
    "Excellent":"優秀","Poor":"低い","Very Poor":"非常に低い",
    "Recommended":"推奨範囲","Borderline":"境界",
    "Long Sleep":"睡眠過多","Insufficient":"不足",
    "Below Average":"平均以下","No Data":"データなし",
    "Health Score":"健康スコア",
    "steps/day":"歩/日","sleep hrs":"睡眠時間","resting HR":"安静心拍",
    "HRV ms":"HRV ms","VO₂max":"VO₂最大","min/wk":"分/週",
    "sessions":"回","hours":"時間","km":"km",
    "bpm":"bpm","ms":"ms","mL/kg/min":"mL/kg/min",
    "hrs/night":"時間/夜","hrs":"時間","%":"%","br/min":"回/分",
    "hero.title":"あなたの健康データ、<br>数字で見る",
    "days":"日間","workouts":"回","Male":"男性","Female":"女性",
    "Generated":"生成日","age":"歳",
    "gauge.desc1":"加重複合 · 6指標 · 90日平均",
    "gauge.desc2":"歩数20% · 睡眠20% · 安静HR/HRV/VO₂/運動 各15%",
    "Monthly Average Daily Steps":"月間平均日歩数",
    "Exercise Minutes / Week (monthly avg)":"週間運動時間（月間平均）",
    "Average Daily Distance (km)":"日平均距離（km）",
    "Resting Heart Rate (bpm)":"安静時心拍数（bpm）",
    "HRV — SDNN (ms)":"心拍変動 — SDNN（ms）",
    "Walking Heart Rate (bpm)":"歩行時心拍数（bpm）",
    "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"VO₂最大値（mL/kg/min）— Apple Watch推定",
    "Monthly Average Sleep Duration (hrs/night)":"月間平均睡眠時間（時間/夜）",
    "Sleep Stages by Month — Stacked (hrs/night)":"月別睡眠ステージ — 積み上げ（時間/夜）",
    "Sleep Stages — 90-Day Average (hrs/night)":"睡眠ステージ — 90日平均（時間/夜）",
    "Blood Oxygen SpO₂ (%)":"血中酸素濃度 SpO₂（%）",
    "Respiratory Rate (breaths/min, measured during sleep)":"呼吸数（回/分、睡眠中測定）",
    "Monthly Average Body Mass (kg)":"月間平均体重（kg）",
    "Workout Type Distribution":"ワークアウトタイプ別分布",
    "Workouts per Month":"月間ワークアウト数",
    "For wellness awareness only.":"健康情報の参考のみ。",
},

"ko": {
    "Activity":"활동","Cardiovascular Health":"심혈관 건강",
    "Cardiorespiratory Fitness":"심폐 능력","Sleep":"수면",
    "Vitals":"생체 신호","Body Weight":"체중","Workouts":"운동",
    "Daily Steps":"일일 걸음 수","Exercise Min / Week":"주간 운동 분",
    "Resting Heart Rate":"안정 시 심박수","Walking Heart Rate":"보행 심박수",
    "HRV — SDNN":"심박 변동성 — SDNN","VO₂ Max":"VO₂ 최대",
    "Sleep Duration":"수면 시간","Deep Sleep (N3)":"깊은 수면 (N3)",
    "REM Sleep":"렘 수면","Blood Oxygen (SpO₂)":"혈중 산소 (SpO₂)",
    "Respiratory Rate":"호흡수",
    "Total Workouts":"총 운동 횟수","Total Hours":"총 시간","Total Distance":"총 거리",
    "Highly Active":"매우 활동적","Active":"활동적","Somewhat Active":"보통 활동",
    "Low Active":"낮은 활동","Sedentary":"좌식 생활",
    "Meets Guidelines":"기준 충족","Partially Active":"부분 달성","Below Guidelines":"기준 미달",
    "Athletic":"운동선수 수준","Optimal":"최적","Normal":"정상",
    "Elevated":"높음","Tachycardia":"빈맥",
    "Fit":"체력 좋음","Average":"보통","High":"높음",
    "Good":"양호","Fair":"보통","Low":"낮음",
    "Excellent":"우수","Poor":"낮음","Very Poor":"매우 낮음",
    "Recommended":"권장","Borderline":"경계",
    "Long Sleep":"수면 과다","Insufficient":"부족",
    "Below Average":"평균 이하","No Data":"데이터 없음",
    "Health Score":"건강 점수",
    "steps/day":"걸음/일","sleep hrs":"수면 시간","resting HR":"안정 심박",
    "HRV ms":"HRV ms","VO₂max":"VO₂ 최대","min/wk":"분/주",
    "sessions":"회","hours":"시간","km":"km",
    "bpm":"bpm","ms":"ms","mL/kg/min":"mL/kg/min",
    "hrs/night":"시간/밤","hrs":"시간","%":"%","br/min":"회/분",
    "hero.title":"당신의 건강 데이터,<br>숫자로",
    "days":"일","workouts":"회","Male":"남성","Female":"여성",
    "Generated":"생성","age":"나이",
    "gauge.desc1":"가중 복합 · 6개 지표 · 90일 평균",
    "gauge.desc2":"걸음 20% · 수면 20% · 안정HR/HRV/VO₂/운동 각15%",
    "Monthly Average Daily Steps":"월간 평균 일일 걸음 수",
    "Exercise Minutes / Week (monthly avg)":"주간 운동 시간 (월간 평균)",
    "Average Daily Distance (km)":"일평균 이동 거리 (km)",
    "Resting Heart Rate (bpm)":"안정 시 심박수 (bpm)",
    "HRV — SDNN (ms)":"심박 변동성 — SDNN (ms)",
    "Walking Heart Rate (bpm)":"보행 심박수 (bpm)",
    "VO₂ Max (mL/kg/min) — Apple Watch estimate · gaps = no outdoor walk/run recorded":"VO₂ 최대 (mL/kg/min) — Apple Watch 추정",
    "Monthly Average Sleep Duration (hrs/night)":"월간 평균 수면 시간 (시간/밤)",
    "Sleep Stages by Month — Stacked (hrs/night)":"월별 수면 단계 — 누적 (시간/밤)",
    "Sleep Stages — 90-Day Average (hrs/night)":"수면 단계 — 90일 평균 (시간/밤)",
    "Blood Oxygen SpO₂ (%)":"혈중 산소 SpO₂ (%)",
    "Respiratory Rate (breaths/min, measured during sleep)":"호흡수 (회/분, 수면 중 측정)",
    "Monthly Average Body Mass (kg)":"월간 평균 체중 (kg)",
    "Workout Type Distribution":"운동 유형 분포",
    "Workouts per Month":"월간 운동 횟수",
    "For wellness awareness only.":"건강 정보 참고용입니다.",
},

}


# ─────────────────────────────────────────────────────────────────────────────
# Apple HKWorkoutActivityType display names (prefix stripped in parsed data)
# ─────────────────────────────────────────────────────────────────────────────

WO_TYPES = {

"zh": {
    "AmericanFootball":"美式橄榄球","AustralianFootball":"澳式橄榄球",
    "Badminton":"羽毛球","Baseball":"棒球","Basketball":"篮球",
    "Bowling":"保龄球","Cricket":"板球","Curling":"冰壶",
    "Handball":"手球","Hockey":"曲棍球","Lacrosse":"长曲棍球",
    "Pickleball":"匹克球","Rugby":"橄榄球","Soccer":"足球",
    "Softball":"垒球","Squash":"壁球","TableTennis":"乒乓球",
    "Tennis":"网球","Volleyball":"排球",
    "Boxing":"拳击","Fencing":"击剑","MartialArts":"武术",
    "Wrestling":"摔跤","Kickboxing":"踢拳",
    "Running":"跑步","Walking":"步行","Cycling":"骑行",
    "HandCycling":"手摇自行车",
    "WheelchairWalkPace":"轮椅慢行","WheelchairRunPace":"轮椅快行",
    "CrossTraining":"综合训练","MixedCardio":"混合有氧",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"跳绳",
    "StepTraining":"踏步训练","Stairs":"爬楼梯",
    "StairClimbing":"登楼梯机","Elliptical":"椭圆机",
    "Rowing":"划船机","FunctionalStrengthTraining":"功能性力量训练",
    "TraditionalStrengthTraining":"传统力量训练",
    "CoreTraining":"核心训练","Flexibility":"柔韧性训练",
    "Yoga":"瑜伽","Pilates":"普拉提","Barre":"芭蕾把杆",
    "TaiChi":"太极拳","MindAndBody":"身心冥想",
    "Dance":"舞蹈","CardioDance":"有氧舞蹈","SocialDance":"社交舞",
    "Hiking":"登山/徒步","Climbing":"攀岩",
    "CrossCountrySkiing":"越野滑雪","DownhillSkiing":"高山滑雪",
    "Snowboarding":"单板滑雪","SnowSports":"雪上运动",
    "Swimming":"游泳","SwimmingOpenWater":"开放水域游泳",
    "WaterFitness":"水中健身","WaterPolo":"水球",
    "WaterSports":"水上运动","SurfingSports":"冲浪","Sailing":"帆船",
    "PaddleSports":"桨板/皮划艇","UnderwaterDiving":"潜水",
    "SkatingSports":"冰/滑轮运动",
    "Archery":"射箭","Golf":"高尔夫","Gymnastics":"体操",
    "Racquetball":"回力球","TrackAndField":"田径",
    "EquestrianSports":"马术","DiscSports":"飞盘运动",
    "RacketSports":"拍类运动",
    "Fishing":"钓鱼","Hunting":"狩猎","Play":"休闲游玩",
    "PreparationAndRecovery":"准备与恢复","Cooldown":"整理放松",
    "FitnessGaming":"健身游戏","Transition":"过渡（铁三）",
    "MixedMetabolicCardioTraining":"混合代谢有氧",
    "Other":"其他","Unknown":"未知",
},

"es": {
    "AmericanFootball":"Fútbol americano","AustralianFootball":"Fútbol australiano",
    "Badminton":"Bádminton","Baseball":"Béisbol","Basketball":"Baloncesto",
    "Bowling":"Bolos","Cricket":"Críquet","Curling":"Curling",
    "Handball":"Balonmano","Hockey":"Hockey","Lacrosse":"Lacrosse",
    "Pickleball":"Pickleball","Rugby":"Rugby","Soccer":"Fútbol",
    "Softball":"Sóftbol","Squash":"Squash","TableTennis":"Tenis de mesa",
    "Tennis":"Tenis","Volleyball":"Voleibol",
    "Boxing":"Boxeo","Fencing":"Esgrima","MartialArts":"Artes marciales",
    "Wrestling":"Lucha","Kickboxing":"Kickboxing",
    "Running":"Correr","Walking":"Caminar","Cycling":"Ciclismo",
    "HandCycling":"Ciclismo manual",
    "WheelchairWalkPace":"Silla de ruedas (paseo)","WheelchairRunPace":"Silla de ruedas (carrera)",
    "CrossTraining":"Entren. cruzado","MixedCardio":"Cardio mixto",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"Saltar a la cuerda",
    "StepTraining":"Step","Stairs":"Escaleras",
    "StairClimbing":"Escaladora","Elliptical":"Elíptica",
    "Rowing":"Remo","FunctionalStrengthTraining":"Fuerza funcional",
    "TraditionalStrengthTraining":"Fuerza tradicional",
    "CoreTraining":"Entren. de core","Flexibility":"Flexibilidad",
    "Yoga":"Yoga","Pilates":"Pilates","Barre":"Barre",
    "TaiChi":"Tai chi","MindAndBody":"Mente y cuerpo",
    "Dance":"Baile","CardioDance":"Baile cardio","SocialDance":"Baile social",
    "Hiking":"Senderismo","Climbing":"Escalada",
    "CrossCountrySkiing":"Esquí de fondo","DownhillSkiing":"Esquí alpino",
    "Snowboarding":"Snowboard","SnowSports":"Deportes de nieve",
    "Swimming":"Natación","SwimmingOpenWater":"Natación en aguas abiertas",
    "WaterFitness":"Fitness acuático","WaterPolo":"Waterpolo",
    "WaterSports":"Deportes acuáticos","SurfingSports":"Surf","Sailing":"Vela",
    "PaddleSports":"Pádel/Kayak","UnderwaterDiving":"Buceo",
    "SkatingSports":"Patinaje",
    "Archery":"Tiro con arco","Golf":"Golf","Gymnastics":"Gimnasia",
    "Racquetball":"Racquetball","TrackAndField":"Atletismo",
    "EquestrianSports":"Equitación","DiscSports":"Disco volador",
    "RacketSports":"Deportes de raqueta",
    "Fishing":"Pesca","Hunting":"Caza","Play":"Juego",
    "PreparationAndRecovery":"Preparación y recuperación","Cooldown":"Enfriamiento",
    "FitnessGaming":"Fitness gaming","Transition":"Transición",
    "MixedMetabolicCardioTraining":"Cardio metabólico mixto",
    "Other":"Otro","Unknown":"Desconocido",
},

"fr": {
    "AmericanFootball":"Football américain","AustralianFootball":"Football australien",
    "Badminton":"Badminton","Baseball":"Baseball","Basketball":"Basket-ball",
    "Bowling":"Bowling","Cricket":"Cricket","Curling":"Curling",
    "Handball":"Handball","Hockey":"Hockey","Lacrosse":"Crosse",
    "Pickleball":"Pickleball","Rugby":"Rugby","Soccer":"Football",
    "Softball":"Softball","Squash":"Squash","TableTennis":"Tennis de table",
    "Tennis":"Tennis","Volleyball":"Volley-ball",
    "Boxing":"Boxe","Fencing":"Escrime","MartialArts":"Arts martiaux",
    "Wrestling":"Lutte","Kickboxing":"Kick-boxing",
    "Running":"Course","Walking":"Marche","Cycling":"Vélo",
    "HandCycling":"Handbike",
    "WheelchairWalkPace":"Fauteuil (allure marche)","WheelchairRunPace":"Fauteuil (allure course)",
    "CrossTraining":"Cross-training","MixedCardio":"Cardio mixte",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"Corde à sauter",
    "StepTraining":"Step","Stairs":"Escaliers",
    "StairClimbing":"Escalier mécanique","Elliptical":"Elliptique",
    "Rowing":"Rameur","FunctionalStrengthTraining":"Renforcement fonctionnel",
    "TraditionalStrengthTraining":"Musculation classique",
    "CoreTraining":"Gainage","Flexibility":"Souplesse",
    "Yoga":"Yoga","Pilates":"Pilates","Barre":"Barre",
    "TaiChi":"Tai-chi","MindAndBody":"Corps et esprit",
    "Dance":"Danse","CardioDance":"Danse cardio","SocialDance":"Danse de salon",
    "Hiking":"Randonnée","Climbing":"Escalade",
    "CrossCountrySkiing":"Ski de fond","DownhillSkiing":"Ski alpin",
    "Snowboarding":"Snowboard","SnowSports":"Sports de neige",
    "Swimming":"Natation","SwimmingOpenWater":"Nage en eau libre",
    "WaterFitness":"Aquagym","WaterPolo":"Water-polo",
    "WaterSports":"Sports nautiques","SurfingSports":"Surf","Sailing":"Voile",
    "PaddleSports":"Pagaie/Kayak","UnderwaterDiving":"Plongée",
    "SkatingSports":"Patinage",
    "Archery":"Tir à l'arc","Golf":"Golf","Gymnastics":"Gymnastique",
    "Racquetball":"Racquetball","TrackAndField":"Athlétisme",
    "EquestrianSports":"Équitation","DiscSports":"Disque volant",
    "RacketSports":"Sports de raquette",
    "Fishing":"Pêche","Hunting":"Chasse","Play":"Jeu",
    "PreparationAndRecovery":"Préparation et récupération","Cooldown":"Retour au calme",
    "FitnessGaming":"Jeu fitness","Transition":"Transition",
    "MixedMetabolicCardioTraining":"Cardio métabolique mixte",
    "Other":"Autre","Unknown":"Inconnu",
},

"de": {
    "AmericanFootball":"American Football","AustralianFootball":"Australian Football",
    "Badminton":"Badminton","Baseball":"Baseball","Basketball":"Basketball",
    "Bowling":"Bowling","Cricket":"Cricket","Curling":"Curling",
    "Handball":"Handball","Hockey":"Hockey","Lacrosse":"Lacrosse",
    "Pickleball":"Pickleball","Rugby":"Rugby","Soccer":"Fußball",
    "Softball":"Softball","Squash":"Squash","TableTennis":"Tischtennis",
    "Tennis":"Tennis","Volleyball":"Volleyball",
    "Boxing":"Boxen","Fencing":"Fechten","MartialArts":"Kampfsport",
    "Wrestling":"Ringen","Kickboxing":"Kickboxen",
    "Running":"Laufen","Walking":"Gehen","Cycling":"Radfahren",
    "HandCycling":"Handbike",
    "WheelchairWalkPace":"Rollstuhl (Gehtempo)","WheelchairRunPace":"Rollstuhl (Lauftempo)",
    "CrossTraining":"Cross-Training","MixedCardio":"Gemischtes Cardio",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"Seilspringen",
    "StepTraining":"Step-Training","Stairs":"Treppen",
    "StairClimbing":"Stepper","Elliptical":"Crosstrainer",
    "Rowing":"Rudern","FunctionalStrengthTraining":"Funktionelles Krafttraining",
    "TraditionalStrengthTraining":"Klassisches Krafttraining",
    "CoreTraining":"Core-Training","Flexibility":"Beweglichkeit",
    "Yoga":"Yoga","Pilates":"Pilates","Barre":"Barre",
    "TaiChi":"Tai-Chi","MindAndBody":"Körper & Geist",
    "Dance":"Tanz","CardioDance":"Cardio-Tanz","SocialDance":"Gesellschaftstanz",
    "Hiking":"Wandern","Climbing":"Klettern",
    "CrossCountrySkiing":"Langlauf","DownhillSkiing":"Ski Alpin",
    "Snowboarding":"Snowboard","SnowSports":"Wintersport",
    "Swimming":"Schwimmen","SwimmingOpenWater":"Freiwasserschwimmen",
    "WaterFitness":"Wassergymnastik","WaterPolo":"Wasserball",
    "WaterSports":"Wassersport","SurfingSports":"Surfen","Sailing":"Segeln",
    "PaddleSports":"Paddel/Kajak","UnderwaterDiving":"Tauchen",
    "SkatingSports":"Eis-/Rollsport",
    "Archery":"Bogenschießen","Golf":"Golf","Gymnastics":"Turnen",
    "Racquetball":"Racquetball","TrackAndField":"Leichtathletik",
    "EquestrianSports":"Reiten","DiscSports":"Frisbee",
    "RacketSports":"Schlägersport",
    "Fishing":"Angeln","Hunting":"Jagd","Play":"Spiel",
    "PreparationAndRecovery":"Vorbereitung & Erholung","Cooldown":"Abkühlung",
    "FitnessGaming":"Fitness-Gaming","Transition":"Wechsel (Triathlon)",
    "MixedMetabolicCardioTraining":"Gemischtes Stoffwechsel-Cardio",
    "Other":"Andere","Unknown":"Unbekannt",
},

"ja": {
    "AmericanFootball":"アメフト","AustralianFootball":"オーストラリアンフットボール",
    "Badminton":"バドミントン","Baseball":"野球","Basketball":"バスケットボール",
    "Bowling":"ボウリング","Cricket":"クリケット","Curling":"カーリング",
    "Handball":"ハンドボール","Hockey":"ホッケー","Lacrosse":"ラクロス",
    "Pickleball":"ピックルボール","Rugby":"ラグビー","Soccer":"サッカー",
    "Softball":"ソフトボール","Squash":"スカッシュ","TableTennis":"卓球",
    "Tennis":"テニス","Volleyball":"バレーボール",
    "Boxing":"ボクシング","Fencing":"フェンシング","MartialArts":"武術",
    "Wrestling":"レスリング","Kickboxing":"キックボクシング",
    "Running":"ランニング","Walking":"ウォーキング","Cycling":"サイクリング",
    "HandCycling":"ハンドサイクル",
    "WheelchairWalkPace":"車椅子（歩行）","WheelchairRunPace":"車椅子（走行）",
    "CrossTraining":"クロストレーニング","MixedCardio":"複合有酸素",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"縄跳び",
    "StepTraining":"ステップ","Stairs":"階段",
    "StairClimbing":"ステアクライマー","Elliptical":"エリプティカル",
    "Rowing":"ローイング","FunctionalStrengthTraining":"ファンクショナル筋トレ",
    "TraditionalStrengthTraining":"伝統的筋トレ",
    "CoreTraining":"コアトレーニング","Flexibility":"柔軟性",
    "Yoga":"ヨガ","Pilates":"ピラティス","Barre":"バー",
    "TaiChi":"太極拳","MindAndBody":"心と身体",
    "Dance":"ダンス","CardioDance":"カーディオダンス","SocialDance":"社交ダンス",
    "Hiking":"ハイキング","Climbing":"クライミング",
    "CrossCountrySkiing":"クロスカントリースキー","DownhillSkiing":"アルペンスキー",
    "Snowboarding":"スノーボード","SnowSports":"雪上スポーツ",
    "Swimming":"水泳","SwimmingOpenWater":"オープンウォータースイミング",
    "WaterFitness":"水中フィットネス","WaterPolo":"水球",
    "WaterSports":"水上スポーツ","SurfingSports":"サーフィン","Sailing":"セーリング",
    "PaddleSports":"パドル/カヤック","UnderwaterDiving":"ダイビング",
    "SkatingSports":"スケート",
    "Archery":"アーチェリー","Golf":"ゴルフ","Gymnastics":"体操",
    "Racquetball":"ラケットボール","TrackAndField":"陸上",
    "EquestrianSports":"乗馬","DiscSports":"ディスクスポーツ",
    "RacketSports":"ラケットスポーツ",
    "Fishing":"釣り","Hunting":"狩り","Play":"遊び",
    "PreparationAndRecovery":"準備と回復","Cooldown":"クールダウン",
    "FitnessGaming":"フィットネスゲーム","Transition":"トランジション",
    "MixedMetabolicCardioTraining":"複合代謝カーディオ",
    "Other":"その他","Unknown":"不明",
},

"ko": {
    "AmericanFootball":"미식축구","AustralianFootball":"호주식 풋볼",
    "Badminton":"배드민턴","Baseball":"야구","Basketball":"농구",
    "Bowling":"볼링","Cricket":"크리켓","Curling":"컬링",
    "Handball":"핸드볼","Hockey":"하키","Lacrosse":"라크로스",
    "Pickleball":"피클볼","Rugby":"럭비","Soccer":"축구",
    "Softball":"소프트볼","Squash":"스쿼시","TableTennis":"탁구",
    "Tennis":"테니스","Volleyball":"배구",
    "Boxing":"복싱","Fencing":"펜싱","MartialArts":"무술",
    "Wrestling":"레슬링","Kickboxing":"킥복싱",
    "Running":"달리기","Walking":"걷기","Cycling":"자전거",
    "HandCycling":"핸드사이클",
    "WheelchairWalkPace":"휠체어 (걷기)","WheelchairRunPace":"휠체어 (달리기)",
    "CrossTraining":"크로스 트레이닝","MixedCardio":"복합 유산소",
    "HighIntensityIntervalTraining":"HIIT","JumpRope":"줄넘기",
    "StepTraining":"스텝 트레이닝","Stairs":"계단",
    "StairClimbing":"스텝밀","Elliptical":"일립티컬",
    "Rowing":"로잉","FunctionalStrengthTraining":"기능성 근력 운동",
    "TraditionalStrengthTraining":"전통적 근력 운동",
    "CoreTraining":"코어 운동","Flexibility":"유연성",
    "Yoga":"요가","Pilates":"필라테스","Barre":"바",
    "TaiChi":"태극권","MindAndBody":"심신 운동",
    "Dance":"댄스","CardioDance":"카디오 댄스","SocialDance":"사교 댄스",
    "Hiking":"등산/하이킹","Climbing":"클라이밍",
    "CrossCountrySkiing":"크로스컨트리 스키","DownhillSkiing":"알파인 스키",
    "Snowboarding":"스노보드","SnowSports":"설상 스포츠",
    "Swimming":"수영","SwimmingOpenWater":"오픈워터 수영",
    "WaterFitness":"수중 운동","WaterPolo":"수구",
    "WaterSports":"수상 스포츠","SurfingSports":"서핑","Sailing":"세일링",
    "PaddleSports":"패들/카약","UnderwaterDiving":"다이빙",
    "SkatingSports":"스케이팅",
    "Archery":"양궁","Golf":"골프","Gymnastics":"체조",
    "Racquetball":"라켓볼","TrackAndField":"육상",
    "EquestrianSports":"승마","DiscSports":"디스크 스포츠",
    "RacketSports":"라켓 스포츠",
    "Fishing":"낚시","Hunting":"사냥","Play":"놀이",
    "PreparationAndRecovery":"준비 및 회복","Cooldown":"쿨다운",
    "FitnessGaming":"피트니스 게이밍","Transition":"전환 (트라이애슬론)",
    "MixedMetabolicCardioTraining":"복합 대사성 유산소",
    "Other":"기타","Unknown":"알 수 없음",
},

}


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark notes — keyed by metric, value is per-language dict.
# These are the static fallback notes. Dynamic age/sex variants live in
# NOTES_TEMPLATES and override these via render_note().
# ─────────────────────────────────────────────────────────────────────────────

NOTES = {
"steps": {
    "en":"≥7,000 steps/day → 50–70% lower all-cause mortality (Paluch 2022). AHA target: ≥10,000.",
    "zh":"≥7,000步/天与全因死亡率降低50–70%相关（Paluch 2022）。AHA目标：≥10,000步。",
    "es":"≥7.000 pasos/día → 50–70% menor mortalidad general (Paluch 2022). Objetivo AHA: ≥10.000.",
    "fr":"≥7 000 pas/jour → 50–70% de mortalité globale en moins (Paluch 2022). Objectif AHA : ≥10 000.",
    "de":"≥7.000 Schritte/Tag → 50–70% geringere Gesamtmortalität (Paluch 2022). AHA-Ziel: ≥10.000.",
    "ja":"≥7,000歩/日 → 全死因死亡率が50–70%低下（Paluch 2022）。AHA目標：≥10,000歩。",
    "ko":"≥7,000보/일 → 전체 사망률 50–70% 감소 (Paluch 2022). AHA 목표: ≥10,000보.",
},
"exercise_min_week": {
    "en":"≥150 min/wk moderate OR ≥75 min/wk vigorous + strength ×2/wk. Apple Watch Exercise Min = brisk-walk pace or above.",
    "zh":"每周≥150分钟中等强度 或 ≥75分钟高强度 + 每周2次力量训练。Apple Watch 运动分钟 = 快走配速及以上。",
    "es":"≥150 min/sem. moderado O ≥75 min/sem. vigoroso + fuerza ×2/sem. Min. ejercicio Apple Watch = ritmo de marcha rápida o superior.",
    "fr":"≥150 min/sem. modéré OU ≥75 min/sem. vigoureux + musculation ×2/sem. Min. exercice Apple Watch = allure de marche rapide ou plus.",
    "de":"≥150 Min./Wo. moderat ODER ≥75 Min./Wo. intensiv + Kraft 2×/Wo. Apple Watch Trainingsmin. = zügiges Gehtempo oder mehr.",
    "ja":"中強度週≥150分 もしくは 高強度週≥75分 + 週2回の筋トレ。Apple Watchの運動分 = 速歩以上のペース。",
    "ko":"중강도 주당 ≥150분 또는 고강도 주당 ≥75분 + 주 2회 근력 운동. Apple Watch 운동 분 = 빠른 걷기 페이스 이상.",
},
"resting_hr_bpm": {
    "en":"Normal: 60–100 bpm (AHA). Optimal zone 60–70 bpm is linked to lowest CV mortality risk.",
    "zh":"AHA正常范围：60–100 bpm。60–70 bpm区间与最低心血管死亡率相关。",
    "es":"Normal: 60–100 ppm (AHA). La zona óptima 60–70 ppm se asocia con la menor mortalidad cardiovascular.",
    "fr":"Normal : 60–100 bpm (AHA). La zone optimale 60–70 bpm est liée à la plus faible mortalité cardiovasculaire.",
    "de":"Normal: 60–100 Spm (AHA). Optimaler Bereich 60–70 Spm steht für niedrigste kardiovaskuläre Mortalität.",
    "ja":"正常範囲：60–100 bpm（AHA）。60–70 bpmは心血管死亡率最低と関連。",
    "ko":"정상 범위: 60–100 bpm (AHA). 최적 구간 60–70 bpm은 최저 심혈관 사망률과 연관.",
},
"walking_hr_bpm": {
    "en":"Lower walking HR reflects better aerobic fitness. Apple Watch records this during everyday walking throughout the day.",
    "zh":"步行心率越低反映有氧适能越好。Apple Watch 在日常步行中全天记录。",
    "es":"Una FC al caminar más baja refleja mejor aptitud aeróbica. Apple Watch la registra durante la marcha cotidiana a lo largo del día.",
    "fr":"Une FC à la marche plus basse reflète une meilleure aptitude aérobie. Apple Watch l'enregistre lors de la marche quotidienne.",
    "de":"Niedrigere Gehherzfrequenz spiegelt bessere aerobe Fitness wider. Apple Watch erfasst dies bei alltäglichem Gehen.",
    "ja":"歩行時心拍数が低いほど有酸素フィットネスが高い。Apple Watchは日常の歩行中に終日測定。",
    "ko":"보행 심박수가 낮을수록 유산소 능력이 우수. Apple Watch가 일상 보행 중 종일 측정.",
},
"hrv_sdnn_ms": {
    "en":"Higher SDNN = better autonomic balance. Trend matters more than absolute. Depressed by poor sleep, overtraining, alcohol, and stress.",
    "zh":"SDNN越高表示自主神经平衡越好。趋势比绝对值更重要。差睡眠、过度训练、饮酒和压力均会降低HRV。",
    "es":"SDNN más alto = mejor balance autonómico. La tendencia importa más que el valor absoluto. Reducido por mal sueño, sobreentrenamiento, alcohol y estrés.",
    "fr":"Plus SDNN est élevé, meilleur est l'équilibre autonome. La tendance compte plus que la valeur absolue. Diminué par mauvais sommeil, surentraînement, alcool et stress.",
    "de":"Höhere SDNN = bessere autonome Balance. Trend wichtiger als Absolutwert. Reduziert durch schlechten Schlaf, Übertraining, Alkohol und Stress.",
    "ja":"SDNNが高いほど自律神経バランスが良い。絶対値より傾向が重要。睡眠不足、オーバートレーニング、アルコール、ストレスで低下。",
    "ko":"SDNN이 높을수록 자율신경 균형이 양호. 절대값보다 추세가 중요. 수면 부족, 과훈련, 음주, 스트레스로 감소.",
},
"vo2_max": {
    "en":"AHA/ACSM categories for adults ~40–49 (male ref; women ~10% lower). Apple Watch estimates indirectly. Low CRF is a major independent CV risk factor (AHA).",
    "zh":"AHA/ACSM成人心肺适能评级（约40–49岁男性参考；女性约低10%）。Apple Watch间接估算。低心肺适能是独立心血管风险因素（AHA）。",
    "es":"Categorías AHA/ACSM para adultos ~40–49 (ref. masculina; mujeres ~10% menos). Apple Watch estima indirectamente. Baja CRF es un factor independiente importante de riesgo CV (AHA).",
    "fr":"Catégories AHA/ACSM pour adultes ~40–49 (réf. masculine ; femmes ~10% plus bas). Apple Watch estime indirectement. Une faible CRF est un facteur de risque CV indépendant majeur (AHA).",
    "de":"AHA/ACSM-Kategorien für Erwachsene ~40–49 (männliche Referenz; Frauen ~10% niedriger). Apple Watch schätzt indirekt. Niedrige CRF ist ein wichtiger unabhängiger kardiovaskulärer Risikofaktor (AHA).",
    "ja":"AHA/ACSM成人約40–49歳の分類（男性基準、女性は約10%低い）。Apple Watchは間接推定。低心肺適能は独立した主要な心血管リスク因子（AHA）。",
    "ko":"AHA/ACSM 성인 약 40–49세 분류 (남성 기준; 여성 약 10% 낮음). Apple Watch는 간접 추정. 낮은 심폐 능력은 주요 독립적 심혈관 위험 요인 (AHA).",
},
"sleep_hours": {
    "en":"AASM/SRS: 7–9 hrs for adults. <7 hrs → elevated risk of obesity, diabetes, hypertension, and all-cause mortality.",
    "zh":"AASM/SRS推荐成人7–9小时睡眠。<7小时→肥胖、糖尿病、高血压及全因死亡率风险升高。",
    "es":"AASM/SRS: 7–9 h para adultos. <7 h → mayor riesgo de obesidad, diabetes, hipertensión y mortalidad general.",
    "fr":"AASM/SRS : 7–9 h pour les adultes. <7 h → risque accru d'obésité, diabète, hypertension et mortalité globale.",
    "de":"AASM/SRS: 7–9 Std. für Erwachsene. <7 Std. → erhöhtes Risiko für Adipositas, Diabetes, Bluthochdruck und Gesamtmortalität.",
    "ja":"AASM/SRS：成人は7–9時間推奨。<7時間 → 肥満・糖尿病・高血圧・全死因死亡率のリスク上昇。",
    "ko":"AASM/SRS: 성인 7–9시간 권장. <7시간 → 비만, 당뇨, 고혈압, 전체 사망률 위험 증가.",
},
"sleep_deep_h": {
    "en":"N3 (slow-wave) = 13–23% of total sleep (~1.0–1.7 h for 7–8 h). Critical for physical restoration and immune function.",
    "zh":"N3（慢波睡眠）= 总睡眠的13–23%（7–8小时约1.0–1.7小时）。对身体恢复和免疫功能至关重要。",
    "es":"N3 (ondas lentas) = 13–23% del sueño total (~1,0–1,7 h para 7–8 h). Crítico para la recuperación física y la función inmune.",
    "fr":"N3 (ondes lentes) = 13–23 % du sommeil total (~1,0–1,7 h pour 7–8 h). Critique pour la récupération physique et la fonction immunitaire.",
    "de":"N3 (Tiefschlaf) = 13–23% des Gesamtschlafs (~1,0–1,7 Std. bei 7–8 Std.). Entscheidend für körperliche Erholung und Immunfunktion.",
    "ja":"N3（徐波睡眠）= 総睡眠の13–23%（7–8時間で約1.0–1.7時間）。身体回復と免疫機能に不可欠。",
    "ko":"N3 (서파 수면) = 총 수면의 13–23% (7–8시간 기준 약 1.0–1.7시간). 신체 회복과 면역 기능에 필수.",
},
"sleep_rem_h": {
    "en":"REM = 20–25% of total sleep (~1.5–2.0 h). Critical for memory consolidation and emotional regulation. Suppressed by alcohol and some medications.",
    "zh":"REM = 总睡眠的20–25%（约1.5–2.0小时）。对记忆巩固和情绪调节至关重要。酒精和部分药物会抑制REM。",
    "es":"REM = 20–25% del sueño total (~1,5–2,0 h). Crítico para la consolidación de la memoria y la regulación emocional. Suprimido por alcohol y algunos medicamentos.",
    "fr":"REM = 20–25 % du sommeil total (~1,5–2,0 h). Critique pour la consolidation de la mémoire et la régulation émotionnelle. Supprimé par l'alcool et certains médicaments.",
    "de":"REM = 20–25% des Gesamtschlafs (~1,5–2,0 Std.). Entscheidend für Gedächtniskonsolidierung und Emotionsregulation. Wird durch Alkohol und manche Medikamente unterdrückt.",
    "ja":"REM = 総睡眠の20–25%（約1.5–2.0時間）。記憶定着と情動調整に不可欠。アルコールや一部の薬物で抑制される。",
    "ko":"REM = 총 수면의 20–25% (약 1.5–2.0시간). 기억 강화와 정서 조절에 필수. 음주와 일부 약물로 억제됨.",
},
"spo2": {
    "en":"Normal SpO₂ is 95–100% at sea level. SpO₂ <90% = hypoxemia, warrants medical evaluation (AHA/ATS).",
    "zh":"正常血氧饱和度：海平面95–100%。SpO₂<90% = 低氧血症，需就医评估（AHA/ATS）。",
    "es":"SpO₂ normal: 95–100% al nivel del mar. SpO₂ <90% = hipoxemia, requiere evaluación médica (AHA/ATS).",
    "fr":"SpO₂ normal : 95–100% au niveau de la mer. SpO₂ <90% = hypoxémie, nécessite une évaluation médicale (AHA/ATS).",
    "de":"Normales SpO₂: 95–100% auf Meereshöhe. SpO₂ <90% = Hypoxämie, erfordert medizinische Abklärung (AHA/ATS).",
    "ja":"正常SpO₂：海抜0mで95–100%。SpO₂ <90% = 低酸素血症、医学的評価が必要（AHA/ATS）。",
    "ko":"정상 SpO₂: 해수면 기준 95–100%. SpO₂ <90% = 저산소혈증, 의학적 평가 필요 (AHA/ATS).",
},
"respiratory_rate": {
    "en":"Normal resting rate: 12–20 breaths/min. Apple Watch measures during sleep.",
    "zh":"正常静息呼吸频率：12–20次/分钟。Apple Watch在睡眠中测量。",
    "es":"Frec. respiratoria normal en reposo: 12–20 resp./min. Apple Watch mide durante el sueño.",
    "fr":"Fréq. respiratoire normale au repos : 12–20 resp./min. Apple Watch mesure pendant le sommeil.",
    "de":"Normale Ruhe-Atemfrequenz: 12–20 Atemz./min. Apple Watch misst während des Schlafs.",
    "ja":"安静時呼吸数：12–20回/分。Apple Watchは睡眠中に測定。",
    "ko":"안정 시 호흡수: 12–20회/분. Apple Watch는 수면 중 측정.",
},
}


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic benchmark notes — Python format strings with {sex} and {age}.
# When a metric appears here, it overrides NOTES for the rendered output.
# Special key "steps_60plus" replaces "steps" when age >= 60.
# ─────────────────────────────────────────────────────────────────────────────

NOTES_TEMPLATES = {

"vo2_max": {
    "en":"ACSM norms for {sex}, age {age}. Low CRF is a strong independent CV risk factor (AHA). Apple Watch estimates via outdoor walk/run (±3–5 mL/kg/min vs lab).",
    "zh":"ACSM {sex}性年龄{age}岁标准。低心肺适能是强独立心血管风险因素（AHA）。Apple Watch通过户外步行/跑步估算（与实验室相比误差±3–5 mL/kg/min）。",
    "es":"Normas ACSM para {sex}, edad {age}. Baja CRF es un factor independiente importante de riesgo CV (AHA). Apple Watch estima mediante marcha/carrera al aire libre (±3–5 mL/kg/min vs lab).",
    "fr":"Normes ACSM pour {sex}, âge {age}. Une CRF faible est un facteur de risque CV indépendant majeur (AHA). Apple Watch estime via marche/course en extérieur (±3–5 mL/kg/min vs labo).",
    "de":"ACSM-Normen für {sex}, Alter {age}. Niedrige CRF ist ein wichtiger unabhängiger CV-Risikofaktor (AHA). Apple Watch schätzt über Gehen/Laufen im Freien (±3–5 mL/kg/min vs Labor).",
    "ja":"ACSM基準 {sex} {age}歳。低心肺適能は独立した主要な心血管リスク因子（AHA）。Apple Watchは屋外歩行/走行で推定（実験室比±3–5 mL/kg/min）。",
    "ko":"ACSM 기준 {sex} {age}세. 낮은 심폐 능력은 주요 독립적 심혈관 위험 요인 (AHA). Apple Watch는 야외 걷기/달리기로 추정 (실험실 대비 ±3–5 mL/kg/min).",
},

"hrv_sdnn_ms": {
    "en":"Age-adjusted norms for {sex}, age {age} (Shaffer & Ginsberg 2017; Nunan 2010). HRV declines ~1–2% per year with age. Trend over months matters more than any single value.",
    "zh":"{sex}性年龄{age}岁标准（Shaffer & Ginsberg 2017；Nunan 2010）。HRV随年龄每年下降约1–2%。月度趋势比单次数值更重要。",
    "es":"Normas ajustadas por edad para {sex}, edad {age} (Shaffer & Ginsberg 2017; Nunan 2010). VFC disminuye ~1–2% por año con la edad. La tendencia mensual importa más que cualquier valor único.",
    "fr":"Normes ajustées par âge pour {sex}, âge {age} (Shaffer & Ginsberg 2017 ; Nunan 2010). VRC diminue d'environ 1–2 % par an avec l'âge. La tendance mensuelle compte plus que toute valeur unique.",
    "de":"Altersangepasste Normen für {sex}, Alter {age} (Shaffer & Ginsberg 2017; Nunan 2010). HRV sinkt ~1–2% pro Jahr mit dem Alter. Monatstrend wichtiger als einzelner Wert.",
    "ja":"年齢調整基準 {sex} {age}歳（Shaffer & Ginsberg 2017; Nunan 2010）。HRVは加齢で年に約1–2%低下。単一値より月間傾向が重要。",
    "ko":"연령 보정 기준 {sex} {age}세 (Shaffer & Ginsberg 2017; Nunan 2010). HRV는 연령에 따라 연 1–2% 감소. 단일 값보다 월간 추세가 중요.",
},

"sleep_deep_h": {
    "en":"N3 (slow-wave) naturally declines with age; target adjusted for age {age}. Critical for physical restoration, immune function, and memory consolidation (AASM).",
    "zh":"N3（慢波睡眠）随年龄自然下降，已根据年龄{age}岁调整目标。对身体恢复、免疫功能和记忆巩固至关重要（AASM）。",
    "es":"N3 (ondas lentas) disminuye naturalmente con la edad; objetivo ajustado para edad {age}. Crítico para la recuperación física, función inmune y consolidación de la memoria (AASM).",
    "fr":"N3 (ondes lentes) diminue naturellement avec l'âge ; objectif ajusté pour l'âge {age}. Critique pour la récupération physique, la fonction immunitaire et la consolidation de la mémoire (AASM).",
    "de":"N3 (Tiefschlaf) nimmt natürlich mit dem Alter ab; Ziel für Alter {age} angepasst. Entscheidend für körperliche Erholung, Immunfunktion und Gedächtniskonsolidierung (AASM).",
    "ja":"N3（徐波睡眠）は加齢で自然に減少；{age}歳に合わせて目標調整。身体回復、免疫機能、記憶定着に不可欠（AASM）。",
    "ko":"N3 (서파 수면)은 연령에 따라 자연 감소; {age}세 기준으로 목표 조정. 신체 회복, 면역 기능, 기억 강화에 필수 (AASM).",
},

"walking_hr_bpm": {
    "en":"Lower walking HR reflects better aerobic fitness (age {age}). Max HR ≈ 208 − 0.7×age (Tanaka 2001); thresholds adjusted accordingly.",
    "zh":"步行心率越低反映有氧适能越好（年龄{age}岁）。最大心率 ≈ 208 − 0.7×年龄（Tanaka 2001），阈值据此调整。",
    "es":"Menor FC al caminar refleja mejor aptitud aeróbica (edad {age}). FC máx. ≈ 208 − 0,7×edad (Tanaka 2001); umbrales ajustados.",
    "fr":"FC à la marche plus basse reflète une meilleure aptitude aérobie (âge {age}). FC max ≈ 208 − 0,7×âge (Tanaka 2001) ; seuils ajustés.",
    "de":"Niedrigere Gehherzfrequenz spiegelt bessere aerobe Fitness wider (Alter {age}). Max. HF ≈ 208 − 0,7×Alter (Tanaka 2001); Schwellen entsprechend angepasst.",
    "ja":"歩行時心拍が低いほど有酸素フィットネスが高い（{age}歳）。最大心拍 ≈ 208 − 0.7×年齢（Tanaka 2001）、閾値は調整済。",
    "ko":"보행 심박이 낮을수록 유산소 능력이 우수 ({age}세). 최대 심박 ≈ 208 − 0.7×나이 (Tanaka 2001); 임계값 조정됨.",
},

"steps_60plus": {
    "en":"≥6,000 steps/day associated with 50–70% lower all-cause mortality in adults 60+ (Paluch 2022 age-stratified analysis). AHA target: ≥8,000.",
    "zh":"≥6,000步/天与60岁以上人群全因死亡率降低50–70%相关（Paluch 2022年龄分层分析）。AHA目标：≥8,000步。",
    "es":"≥6.000 pasos/día asociados con 50–70% menor mortalidad general en adultos 60+ (Paluch 2022 análisis estratificado por edad). Objetivo AHA: ≥8.000.",
    "fr":"≥6 000 pas/jour associés à une mortalité globale 50–70% plus faible chez les adultes 60+ (Paluch 2022, analyse stratifiée par âge). Objectif AHA : ≥8 000.",
    "de":"≥6.000 Schritte/Tag mit 50–70% geringerer Gesamtmortalität bei Erwachsenen 60+ assoziiert (Paluch 2022, altersgeschichtete Analyse). AHA-Ziel: ≥8.000.",
    "ja":"≥6,000歩/日は60歳以上で全死因死亡率50–70%低下と関連（Paluch 2022 年齢層別解析）。AHA目標：≥8,000歩。",
    "ko":"≥6,000보/일은 60세 이상 성인의 전체 사망률 50–70% 감소와 연관 (Paluch 2022 연령 계층 분석). AHA 목표: ≥8,000보.",
},

}


# ─────────────────────────────────────────────────────────────────────────────
# Insight callout templates — head (short) + detail (sentence) per metric.
# Each detail can have variants; chosen by python logic in report_html.py
# Placeholders: {val}, {diff}, {short}, {label}
# ─────────────────────────────────────────────────────────────────────────────

INSIGHT = {

"steps": {
    "head": {
        "en":"{val} steps/day", "zh":"{val} 步/天", "es":"{val} pasos/día",
        "fr":"{val} pas/jour",  "de":"{val} Schritte/Tag",
        "ja":"{val} 歩/日",     "ko":"{val} 걸음/일",
    },
    "detail": {
        "above": {
            "en":"That's {diff} steps above the 7,000-step threshold associated with 50–70% lower mortality risk (Paluch 2022).",
            "zh":"比7,000步基准线多{diff}步。7,000步/天与全因死亡率降低50–70%相关（Paluch 2022）。",
            "es":"Eso es {diff} pasos por encima del umbral de 7.000 pasos asociado con un 50–70% menor riesgo de mortalidad (Paluch 2022).",
            "fr":"Soit {diff} pas au-dessus du seuil de 7 000 pas associé à un risque de mortalité 50–70% inférieur (Paluch 2022).",
            "de":"Das sind {diff} Schritte über der 7.000-Schritte-Schwelle, die mit 50–70% geringerem Mortalitätsrisiko verbunden ist (Paluch 2022).",
            "ja":"これは死亡率50–70%低下と関連する7,000歩基準線を{diff}歩上回っています（Paluch 2022）。",
            "ko":"이는 사망률 50–70% 감소와 연관된 7,000보 기준치보다 {diff}보 많습니다 (Paluch 2022).",
        },
        "below": {
            "en":"That's {diff} steps below the 7,000-step threshold associated with 50–70% lower mortality risk (Paluch 2022).",
            "zh":"比7,000步基准线少{diff}步。7,000步/天与全因死亡率降低50–70%相关（Paluch 2022）。",
            "es":"Eso es {diff} pasos por debajo del umbral de 7.000 pasos asociado con un 50–70% menor riesgo de mortalidad (Paluch 2022).",
            "fr":"Soit {diff} pas en dessous du seuil de 7 000 pas associé à un risque de mortalité 50–70% inférieur (Paluch 2022).",
            "de":"Das sind {diff} Schritte unter der 7.000-Schritte-Schwelle, die mit 50–70% geringerem Mortalitätsrisiko verbunden ist (Paluch 2022).",
            "ja":"これは死亡率50–70%低下と関連する7,000歩基準線を{diff}歩下回っています（Paluch 2022）。",
            "ko":"이는 사망률 50–70% 감소와 연관된 7,000보 기준치보다 {diff}보 적습니다 (Paluch 2022).",
        },
    },
},

"exercise_min_week": {
    "head": {
        "en":"{val} min/week", "zh":"{val} 分钟/周", "es":"{val} min/sem.",
        "fr":"{val} min/sem.", "de":"{val} Min./Wo.",
        "ja":"{val} 分/週",   "ko":"{val} 분/주",
    },
    "detail": {
        "yes": {
            "en":"Meets the WHO/AHA recommendation of ≥150 min/week of moderate-intensity activity.",
            "zh":"达到WHO/AHA推荐的每周≥150分钟中等强度运动目标。",
            "es":"Cumple la recomendación WHO/AHA de ≥150 min/semana de actividad de intensidad moderada.",
            "fr":"Atteint la recommandation WHO/AHA de ≥150 min/semaine d'activité d'intensité modérée.",
            "de":"Erfüllt die WHO/AHA-Empfehlung von ≥150 Min./Woche moderater Aktivität.",
            "ja":"中強度活動 週≥150分というWHO/AHAの推奨を達成しています。",
            "ko":"중강도 활동 주당 ≥150분이라는 WHO/AHA 권장을 충족합니다.",
        },
        "no": {
            "en":"Below the WHO/AHA recommendation of ≥150 min/week of moderate-intensity activity.",
            "zh":"低于WHO/AHA推荐的每周≥150分钟中等强度运动目标。",
            "es":"Por debajo de la recomendación WHO/AHA de ≥150 min/semana de actividad de intensidad moderada.",
            "fr":"Sous la recommandation WHO/AHA de ≥150 min/semaine d'activité d'intensité modérée.",
            "de":"Unter der WHO/AHA-Empfehlung von ≥150 Min./Woche moderater Aktivität.",
            "ja":"中強度活動 週≥150分というWHO/AHAの推奨を下回っています。",
            "ko":"중강도 활동 주당 ≥150분이라는 WHO/AHA 권장에 미달합니다.",
        },
    },
},

"resting_hr_bpm": {
    "head": {
        "en":"{val} bpm resting HR","zh":"静息心率 {val} bpm",
        "es":"FC en reposo {val} ppm","fr":"FC au repos {val} bpm",
        "de":"Ruhepuls {val} Spm","ja":"安静時心拍 {val} bpm",
        "ko":"안정 심박 {val} bpm",
    },
    "detail": {
        "default": {
            "en":"AHA normal range: 60–100 bpm. Your value is in the '{label}' zone.",
            "zh":"AHA正常范围：60–100 bpm。当前评级：{label}。",
            "es":"Rango normal AHA: 60–100 ppm. Tu valor está en la zona '{label}'.",
            "fr":"Plage normale AHA : 60–100 bpm. Votre valeur est dans la zone « {label} ».",
            "de":"AHA Normalbereich: 60–100 Spm. Dein Wert liegt im Bereich „{label}“.",
            "ja":"AHA正常範囲：60–100 bpm。現在の評価：{label}。",
            "ko":"AHA 정상 범위: 60–100 bpm. 현재 평가: {label}.",
        },
    },
},

"hrv_sdnn_ms": {
    "head": {
        "en":"{val} ms SDNN","zh":"HRV（SDNN）{val} 毫秒",
        "es":"{val} ms SDNN","fr":"{val} ms SDNN",
        "de":"{val} ms SDNN","ja":"SDNN {val} ms","ko":"SDNN {val} ms",
    },
    "detail": {
        "default": {
            "en":"HRV reflects autonomic nervous system balance. Higher = better. Trend over months is more informative than any single value.",
            "zh":"HRV反映自主神经系统平衡状态，数值越高越好。月度趋势比单次数值更有参考价值。",
            "es":"VFC refleja el equilibrio del sistema nervioso autónomo. Mayor = mejor. La tendencia mensual es más informativa que cualquier valor único.",
            "fr":"VRC reflète l'équilibre du système nerveux autonome. Plus élevé = mieux. La tendance mensuelle est plus informative qu'une valeur unique.",
            "de":"HRV spiegelt das Gleichgewicht des autonomen Nervensystems wider. Höher = besser. Monatstrend aussagekräftiger als Einzelwerte.",
            "ja":"HRVは自律神経系のバランスを反映。高いほど良好。月間傾向のほうが単一値より有用。",
            "ko":"HRV는 자율신경계 균형을 반영합니다. 높을수록 우수. 월간 추세가 단일 값보다 더 유의미합니다.",
        },
    },
},

"vo2_max": {
    "head": {
        "en":"{val} mL/kg/min VO₂max","zh":"最大摄氧量 {val} mL/kg/min",
        "es":"VO₂máx {val} mL/kg/min","fr":"VO₂max {val} mL/kg/min",
        "de":"VO₂max {val} mL/kg/min","ja":"VO₂最大値 {val} mL/kg/min",
        "ko":"VO₂ 최대 {val} mL/kg/min",
    },
    "detail": {
        "default": {
            "en":"AHA/ACSM fitness category: '{label}'. True improvement requires sustained moderate-to-vigorous aerobic training.",
            "zh":"AHA/ACSM心肺适能评级：{label}。持续提升需要规律的中高强度有氧训练。",
            "es":"Categoría de aptitud AHA/ACSM: '{label}'. La mejora real requiere entrenamiento aeróbico moderado a vigoroso sostenido.",
            "fr":"Catégorie d'aptitude AHA/ACSM : « {label} ». Une vraie amélioration nécessite un entraînement aérobie modéré à intense soutenu.",
            "de":"AHA/ACSM-Fitnesskategorie: „{label}“. Echte Verbesserung erfordert anhaltendes moderates bis intensives aerobes Training.",
            "ja":"AHA/ACSM心肺適能評価：{label}。真の向上には継続的な中〜高強度の有酸素トレーニングが必要。",
            "ko":"AHA/ACSM 심폐 능력 평가: {label}. 진정한 향상에는 지속적인 중-고강도 유산소 훈련이 필요합니다.",
        },
    },
},

"sleep_hours": {
    "head": {
        "en":"{val} hrs/night","zh":"{val} 小时/晚",
        "es":"{val} h/noche","fr":"{val} h/nuit",
        "de":"{val} Std./Nacht","ja":"{val} 時間/夜","ko":"{val} 시간/밤",
    },
    "detail": {
        "short": {
            "en":"AASM recommends 7–9 hrs for adults. You're averaging {short} hrs short of the minimum.",
            "zh":"AASM推荐成人7–9小时睡眠，当前平均比下限少{short}小时。",
            "es":"AASM recomienda 7–9 h para adultos. Tu promedio está {short} h por debajo del mínimo.",
            "fr":"AASM recommande 7–9 h pour les adultes. Vous êtes en moyenne à {short} h en dessous du minimum.",
            "de":"AASM empfiehlt 7–9 Std. für Erwachsene. Du liegst im Durchschnitt {short} Std. unter dem Minimum.",
            "ja":"AASMは成人に7–9時間を推奨。現在平均で下限を{short}時間下回っています。",
            "ko":"AASM은 성인에게 7–9시간을 권장합니다. 현재 평균이 하한보다 {short}시간 부족합니다.",
        },
        "ok": {
            "en":"Within the AASM-recommended 7–9 hr window. Consistent sleep timing matters as much as duration.",
            "zh":"处于AASM推荐的7–9小时范围内。规律的作息时间与睡眠时长同样重要。",
            "es":"Dentro del rango AASM recomendado de 7–9 h. La regularidad horaria importa tanto como la duración.",
            "fr":"Dans la plage recommandée AASM de 7–9 h. La régularité des horaires compte autant que la durée.",
            "de":"Im AASM-empfohlenen Bereich von 7–9 Std. Konstante Schlafzeiten sind ebenso wichtig wie die Dauer.",
            "ja":"AASM推奨の7–9時間の範囲内。睡眠時間の規則性は長さと同じくらい重要です。",
            "ko":"AASM 권장 7–9시간 범위 내. 일관된 수면 시간 규칙이 수면 시간만큼 중요합니다.",
        },
    },
},

}


# ─────────────────────────────────────────────────────────────────────────────
# Full disclaimer body (paired with STATIC's "For wellness awareness only." lede)
# ─────────────────────────────────────────────────────────────────────────────

DISCLAIMER = {
    "en":"This report is generated from consumer-grade wearable data and does not constitute medical advice. It cannot diagnose, treat, or prevent any medical condition. All benchmarks are population-level guidelines — individual targets should be set with a healthcare provider. Apple Watch metrics (VO₂ max, SpO₂, sleep stages) are estimates with lower accuracy than clinical instruments.",
    "zh":"本报告基于消费级可穿戴设备数据生成，不构成医疗建议，不能用于诊断、治疗或预防任何疾病。所有基准均为人群级指导标准——个人目标应由医疗专业人员制定。Apple Watch 指标（最大摄氧量、血氧、睡眠阶段）为估算值，精度低于临床仪器。",
    "es":"Este informe se genera a partir de datos de dispositivos vestibles de consumo y no constituye consejo médico. No puede diagnosticar, tratar ni prevenir ninguna condición médica. Todos los puntos de referencia son guías a nivel poblacional — los objetivos individuales deben establecerse con un profesional sanitario. Las métricas de Apple Watch (VO₂ máx., SpO₂, fases del sueño) son estimaciones con menor precisión que los instrumentos clínicos.",
    "fr":"Ce rapport est généré à partir de données issues d'appareils portables grand public et ne constitue pas un avis médical. Il ne peut pas diagnostiquer, traiter ou prévenir une condition médicale. Tous les seuils sont des recommandations populationnelles — les objectifs individuels doivent être fixés avec un professionnel de santé. Les mesures Apple Watch (VO₂ max., SpO₂, phases de sommeil) sont des estimations moins précises que les instruments cliniques.",
    "de":"Dieser Bericht wird aus Daten von Verbraucher-Wearables generiert und stellt keine medizinische Beratung dar. Er kann keine medizinischen Zustände diagnostizieren, behandeln oder verhindern. Alle Richtwerte sind populationsbezogene Empfehlungen — individuelle Ziele sollten mit einem Arzt festgelegt werden. Apple Watch-Metriken (VO₂ max., SpO₂, Schlafphasen) sind Schätzungen mit geringerer Genauigkeit als klinische Instrumente.",
    "ja":"本レポートは消費者向けウェアラブルデバイスのデータから生成されており、医療アドバイスを構成するものではありません。いかなる医学的状態の診断、治療、予防にも使用できません。すべての基準は集団レベルのガイドラインであり、個人の目標は医療従事者と設定すべきです。Apple Watchの指標（VO₂最大値、SpO₂、睡眠ステージ）は推定値であり、臨床機器より精度が低くなります。",
    "ko":"이 보고서는 소비자용 웨어러블 기기 데이터를 기반으로 생성되었으며 의료 조언을 구성하지 않습니다. 어떤 의학적 상태도 진단, 치료, 예방할 수 없습니다. 모든 기준은 인구 수준 가이드라인이며 — 개인 목표는 의료 전문가와 설정해야 합니다. Apple Watch 지표(VO₂ 최대, SpO₂, 수면 단계)는 추정치이며 임상 기기보다 정확도가 낮습니다.",
}


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions for Python callers (report_html.py builds a multi-lang dict
# for each insight/note and embeds it as a data attribute).
# ─────────────────────────────────────────────────────────────────────────────

def _pick(d, lang):
    """Get value from dict by language, falling back to English."""
    return d.get(lang, d.get("en", ""))


def sex_name(lang, sex):
    s = (sex or "").lower()
    key = "male" if s == "male" else "female" if s == "female" else "other"
    return SEX_NAMES.get(lang, SEX_NAMES["en"])[key]


def note_for_lang(metric, lang, age=None, sex=None, age_60plus_key="steps_60plus"):
    """Resolve a benchmark note for one language, picking template + interpolating
       age/sex when appropriate, else falling back to the static note."""
    tpl_metric = metric
    # Steps switches to age-stratified template when age >= 60
    if metric == "steps" and age and age >= 60:
        tpl_metric = age_60plus_key
    tpl = NOTES_TEMPLATES.get(tpl_metric, {}).get(lang)
    if tpl is not None:
        return tpl.format(sex=sex_name(lang, sex), age=age or "")
    return _pick(NOTES.get(metric, {}), lang)


def all_notes(metric, age=None, sex=None):
    """Return {lang: rendered_note} dict for every supported language."""
    return {lang: note_for_lang(metric, lang, age=age, sex=sex) for lang in LANGS}


def all_insight(metric, variant, params):
    """Return {lang: {"head": ..., "detail": ...}} dict for every language.
       `variant` selects which detail template (e.g. "above"/"below"/"default").
       `params` is a dict of placeholders. {label} should be the EN label and
       will be auto-translated per language via STATIC."""
    spec = INSIGHT.get(metric, {})
    head_d   = spec.get("head", {})
    detail_d = spec.get("detail", {}).get(variant, {})
    out = {}
    label_en = params.get("label")
    for lang in LANGS:
        p = dict(params)
        if label_en is not None:
            p["label"] = (STATIC.get(lang, {}).get(label_en, label_en)
                          if lang != "en" else label_en)
        head   = _pick(head_d,   lang).format(**p) if head_d   else ""
        detail = _pick(detail_d, lang).format(**p) if detail_d else ""
        out[lang] = {"head": head, "detail": detail}
    return out


def disclaimer_all():
    return dict(DISCLAIMER)
