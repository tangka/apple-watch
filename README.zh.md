[English](README.md) | **中文**

# Apple Health 健康报告

> **Codex / Claude Code skill** —— 装一次,之后在任何地方让 AI 帮你分析 Apple Health 导出数据。

把 Apple Watch / iPhone 的健康导出,变成一份**自包含、有循证依据的交互式 HTML 报告**,全程由一个 agent skill 编排完成。

| | |
|---|---|
| **输入** | Apple Health 导出 ZIP(Apple 按手机语言命名,文件名随意,解析器自动识别里面的 XML) |
| **输出** | 一个自包含的 `health_report.html`——无 CDN、无联网、无追踪 |
| **语言** | 英 · 中 · 西 · 法 · 德 · 日 · 韩(按系统自动检测) |
| **主题** | 浅色 / 深色(按 `prefers-color-scheme` 自动) |
| **基准** | AHA / WHO / AASM / ACSM / ESC——按导出里的年龄、性别自动取参考区间 |
| **隐私** | 全程本地处理,数据不出本机 |

---

## 特性

- **20+ 指标**:步数、运动分钟、距离、静息心率、步行心率、HRV(SDNN)、最大摄氧量、睡眠时长 + 阶段(深睡 / REM / 核心 / 清醒)、血氧、呼吸率、体重、各类运动频次。
- **综合健康分**:6 指标加权仪表盘(步数 20% · 睡眠 20% · 静息心率/HRV/VO₂/运动 各 15%)+ 等级评分。
- **每个指标一句点评**:简短「这意味着什么」+ 状态区间。
- **按年龄性别调整阈值**:VO₂max、HRV、深睡目标、步行心率、步数(60+)自动选对应的 ACSM / Shaffer / Tanaka / Paluch 参考带。
- **完整引用链**:每条基准都链到原始文献。
- **固定免责声明**:每份报告都带「非医疗建议」页脚(读者语言)。

---

## 快速开始

### 1. 拿到你的数据

iPhone →「**健康**」App → 点右上角头像 →「**导出所有健康数据**」。把生成的 ZIP 存到能找到的地方(文件名随系统语言不同,`export.zip` / `导出.zip` 都行)。

### 2. 跑流程

```bash
git clone <repo> apple-health
cd apple-health
python3 health_parser.py --zip ~/Downloads/<你的导出>.zip
python3 report_html.py --data ./latest_parsed
open ./latest_parsed/health_report.html
```

解析约每 GB XML 用 1 分钟,生成报告 <1 秒。

### 3.(可选)装成 skill

**Codex / Agents**:克隆到用户级 skills 目录,重启 agent。skill 用自然语言触发,**不创建 slash 命令**:

```bash
git clone <repo> ~/.agents/skills/apple-health
```

```
用 apple-health 分析 ~/Downloads/导出.zip
use apple-health --report
use apple-health q: 我睡得最好的是哪个月?
```

**Claude Code**:克隆到 skills 目录 + 链接 slash 命令:

```bash
git clone <repo> ~/.claude/skills/apple-health
mkdir -p ~/.claude/commands
ln -sf ~/.claude/skills/apple-health/.claude/commands/apple-health.md ~/.claude/commands/apple-health.md
```

重启 Claude Code,任意目录下:

```
/apple-health ~/Downloads/<你的导出>.zip
/apple-health --report        # 只重新生成 HTML
/apple-health q: 我睡得最好的是哪个月?
```

提到「分析 Apple Health」时也会自然语言自动触发(靠 `SKILL.md` 的 description)。

---

## 隐私

这个 skill **不把数据发往任何地方**。唯一的联网是首次生成报告时下载一次 `vendor/chart.min.js`(~200 kB),之后可完全离线运行。Apple Health 导出含极其私密的数据(每一次心率、每一次运动定位、买表以来的每一晚睡眠),`.gitignore` 已排除 `latest_raw/` 和 `latest_parsed/`,防止误提交。

## 非医疗建议

本报告可视化的是消费级可穿戴设备的数据,**不能诊断、治疗或预防任何疾病**。所有阈值都是来自同行评审文献的人群级指南,个人目标应与医疗专业人员一起设定。Apple Watch 的指标(VO₂max、血氧、睡眠阶段)是估算值,精度低于临床仪器。

## License

[MIT](LICENSE)

---

## 📣 关于作者 & 支持

这套工具来自我运营的两个公众号,欢迎关注 👇

- **Codexx** —— Codex 铁粉中文社区
- **ClaudeDevs** —— Claude 中文社区

<img src="promo/codexx-qrcode.jpg" width="160" alt="Codexx 公众号"> &nbsp;&nbsp; <img src="promo/claudedevs-qrcode.jpg" width="160" alt="ClaudeDevs 公众号">

如果这些工具帮到你,欢迎请我喝杯咖啡 ☕

<img src="promo/wx_qr.png" width="200" alt="微信"> &nbsp;&nbsp; <img src="promo/ali_qr.png" width="200" alt="支付宝">
