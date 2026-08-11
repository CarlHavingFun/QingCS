# 《天工枪局：宫门没有回头枪》仓库迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 QingCS 根目录建立独立的新 IP 小说生产库，迁移第一章节拍与女性外观资产，重写世界、游戏、人物家族和生产 Skill，并锁定“主角男性本体穿越、唯一男性职业适格者、其他职业选手全部为成年女性”。

**Architecture:** 采用“旧源只读、新库独立、根级导航”的双目录结构。新库以 `设定` 为正史输入，以 `人物档案`、`正文`、`skills`、`提示词` 和 `视觉资产` 为生产输出；旧名字只允许进入内部迁移索引。周烬与谢照夜是两个独立人物，不存在身体替换。

**Tech Stack:** Git/GitHub trees and blobs、UTF-8 Markdown、PNG Git blobs、QingCS 自定义 Skill Markdown。

## Global Constraints

- 正式书名固定为《天工枪局：宫门没有回头枪》。
- 穿越前游戏称 CS；穿越后游戏称《天工枪局》；顶级赛事称万国天工枪赛。
- 大曜朝、承曜二十七年、宣昭帝祁元熙及所有势力均为原创架空。
- 周烬以自己的成年男性身体穿越，不进入女性身体。
- 周烬是唯一通过完整职业适格检测的男性；除他之外，所有注册职业选手均为成年女性。
- 男性适格是架空工程/制度设定，不代表现实性别能力优劣。
- 适格检测不自动授予赛籍、合同、首发、政治豁免、超能力或恋爱特权。
- 谢照夜是独立的成年女性失踪选手，是第一部长期悬疑节点。
- 旧版只保留第一章结构、节拍与文风；第 2—44 章不得复制。
- 人物只复用女性外观母版；旧姓名、外号、称号、身份、家族、关系和皇帝线不得继承。
- 周烬必须建立全新男性视觉母版，不得复用任何旧女性三视图。
- 身份母版严格空手；持械只出现在比赛化身或剧情动作资产。
- 每场比赛必须改变局内账、队务账或现实账中的至少一项。
- 观察者和太监解说面向观众，不得向选手泄露敌方信息。
- 旧目录除删除 `.DS_Store` 外保持不变。

---

### Task 1: 根目录导航与新库骨架

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Delete: `重生之twistzz：开宫没有回头监_重写版/.DS_Store`
- Create: `天工枪局：宫门没有回头枪/README.md`
- Create: `天工枪局：宫门没有回头枪/00_书名与IP定位.md`
- Create: `天工枪局：宫门没有回头枪/00_迁移状态.md`

- [ ] 写根级 README，声明新作是默认入口、旧目录是历史源。
- [ ] 写 `.gitignore` 忽略全仓 `.DS_Store`，并删除已跟踪文件。
- [ ] 写新库 README、IP 定位和迁移状态，明确新正文只有第一章。
- [ ] 检查公开入口没有旧人物称号、旧皇帝和旧国名。

### Task 2: 时代、权力、穿越和性别规则正史

**Files:**
- Create: `设定/时代背景/01_大曜朝与清制异世界.md`
- Create: `设定/时代背景/02_朝廷商会江湖三权格局.md`
- Create: `设定/时代背景/03_穿越国运与回归机制.md`
- Create: `设定/时代背景/04_唯一男性适格者与职业赛制性别规则.md`

- [ ] 写架空王朝、技术、礼制视觉和非历史清朝边界。
- [ ] 写朝廷、商会、江湖、军方的资源与互相制衡。
- [ ] 写周烬男性本体穿越、谢照夜独立失踪、国运簿、天工枢网和归途残片。
- [ ] 写唯一男性职业适格规则、检测字段、历史记录、制度争议和禁止推论。
- [ ] 明确电脑、皇帝和适格结果不能改比分、发资格或替人物决定。

### Task 3: 原创游戏与现实后果闭环

**Files:**
- Create: `设定/游戏背景/01_天工枪局与万国枪赛.md`
- Create: `设定/游戏背景/02_地图枪械经济阵营统一规则.md`
- Create: `设定/游戏背景/03_比赛制度与现实后果.md`
- Create: `设定/游戏背景/04_漫剧三层表现与观察者系统.md`

- [ ] 定义五人制、兵筹经济、现代经验优势但非外挂。
- [ ] 统一地图权、枪械材料、火药配额、旗色阵营和战术道具。
- [ ] 建立局内账、队务账、现实账及具体后果表。
- [ ] 写现实赛台、游戏战场、观察者层及专业太监解说权限。
- [ ] 验证只有主角内心/现代层可使用 CS、AK、AWP 类比。

### Task 4: 人物家族与 IP 圣经

**Files:**
- Create: `设定/人物家族背景/00_核心人物与家族总表.md`
- Create: `设定/人物家族背景/01_玄旗队家族债与成长线.md`
- Create: `设定/人物家族背景/02_皇室朝廷商会江湖人物.md`
- Create: `设定/人物家族背景/03_旧外观新身份迁移索引_内部.md`
- Create: `设定/IP圣经/00_专名词典与原创边界.md`
- Create: `设定/IP圣经/01_长期衍生与赛季框架.md`

- [ ] 为周烬、谢照夜、裴镇霜、闻青砚、霍长缨、陆停云、纪衡秋、唐照野和祁元熙写资源、限制、旧债和成长。
- [ ] 分组建立朝廷、商会、江湖、外邦和公共传播角色接口。
- [ ] 在唯一内部索引记录旧外观 blob 到新女性身份的映射。
- [ ] 建立专名词典、禁用词和多赛季/多地域/多媒介扩展框架。
- [ ] 明确其他职业选手全部为成年女性，男性可担任非选手职业。

### Task 5: 人物档案与视觉资产迁移

**Files:**
- Create: `人物档案/00_角色总表.md`
- Create: `人物档案/01_周烬.md`
- Create: `人物档案/02_谢照夜.md`
- Create: `人物档案/03_裴镇霜.md`
- Create: `人物档案/04_闻青砚.md`
- Create: `人物档案/05_霍长缨.md`
- Create: `人物档案/06_陆停云.md`
- Create: `人物档案/07_纪衡秋.md`
- Create: `人物档案/08_唐照野.md`
- Create: `人物档案/09_祁元熙.md`
- Create: `视觉资产/README.md`
- Copy: seven approved female character PNG blobs under new female names.
- Copy: four historical scene PNG blobs under internal-reference names.

- [ ] 分离周烬、谢照夜的身份、身体、记忆和外观来源。
- [ ] 写九份可生产人物事实卡和角色总表。
- [ ] 复制七张女性外观母版，不复制旧公开文件名。
- [ ] 不为周烬复制女性母版，登记其男性母版为待独立生产的首个新视觉任务。
- [ ] 复制四张场景参考并声明旧文字、牌匾和专名不构成正史。

### Task 6: 第一章重接新世界

**Files:**
- Create: `正文/目录说明.md`
- Create: `正文/第01章_输掉决赛后，我成了唯一合格的男枪手.md`

- [ ] 保留现代 Major 决赛、半拍失误、团队复盘和逐级回放异常。
- [ ] 现代主角与队友改为周烬、关峤、沈砚、程野、薄川。
- [ ] 周烬以自己的成年男性身体和现代装备穿越。
- [ ] 他出现在谢照夜封存工位；四名女性队员按安保、医务、门禁和失踪事件处理。
- [ ] 通过门禁、奖牌、日期、缺席名册和实物建立真实性。
- [ ] 连续三次检测显示“男／职业适格通过／无赛籍”，并明确通过设备不等于上场。
- [ ] 自然加入“这不就是 CS 里的 AK 吗”的内心类比。
- [ ] 结尾锁定承天门东掖查档、谢照夜失踪和寻找回路。
- [ ] 确认新正文目录只有第一章。

### Task 7: Skills、提示词、分镜与审核入口

**Files:**
- Create: `skills/tiangong-novel-production/SKILL.md`
- Create: `skills/tiangong-human-first-novel-review/SKILL.md`
- Create: `skills/tiangong-cinematic-director/SKILL.md`
- Create: `skills/tiangong-cinematic-storyboard/SKILL.md`
- Create: `skills/tiangong-ancient-character-visual/SKILL.md`
- Create: `skills/tiangong-ancient-character-visual/references/acceptance-cases.md`
- Create: `skills/tiangong-match-visual/SKILL.md`
- Create: `提示词/天工枪局视觉提示词总表.md`
- Create: `分镜/目录说明.md`
- Create: `审核/00_迁移验收基准.md`
- Create: `审核/2026-08-11_重启迁移记录.md`

- [ ] 迁移旧六类能力边界并移除旧专名依赖。
- [ ] 所有 Skill 加入男性本体、唯一男性适格、其他职业选手成年女性的硬锁。
- [ ] 写权威输入优先级、工作流、失败诊断和验收清单。
- [ ] 写视觉提示总表，覆盖周烬男性母版、女性角色母版、比赛化身、地图、枪械、UI 和太监解说。
- [ ] 写分镜入口和迁移验收基准。

### Task 8: 最终验证与提交

- [ ] 比较迁移前后树，确认旧目录除 `.DS_Store` 外未被修改。
- [ ] 确认新目录只有一章正文和六项主 Skill。
- [ ] 搜索新公开文件中的旧称号、旧皇帝、女性身体替换、`TBD`、`TODO` 和占位符。
- [ ] 检查“周烬男性本体”“谢照夜独立人物”“唯一男性适格”“其他职业选手成年女性”在正史、正文和 Skill 中一致。
- [ ] 抽查书名、时代、游戏、家族、第一章、提示词和视觉迁移。
- [ ] 创建可审计提交并以非强制 fast-forward 更新 `agent/tianggong-reboot-male-player`。
- [ ] 若 `agent/ch01-half-beat-rewrite` 仍是本分支祖先，则以非强制 fast-forward 同步；若已出现并行提交，保留功能分支并报告，不覆盖他人工作。
