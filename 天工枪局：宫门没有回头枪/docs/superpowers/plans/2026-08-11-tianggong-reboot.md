# 《天工枪局：宫门没有回头枪》仓库迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 QingCS 根目录建立独立的新 IP 小说生产库，迁移第一章与外观资产，重写世界、游戏、人物家族和全部生产 Skill，同时保留旧目录为历史源。

**Architecture:** 采用“旧源只读、新库独立、根级导航”的双目录结构。新库以 `设定` 为正史输入，以 `人物档案`、`正文`、`skills` 和 `视觉资产` 为生产输出；旧名字只允许进入内部迁移索引，不得进入公开新作文件。

**Tech Stack:** Git/GitHub trees and blobs、UTF-8 Markdown、PNG Git blobs、QingCS 自定义 Skill Markdown。

## Global Constraints

- 正式书名固定为《天工枪局：宫门没有回头枪》。
- 穿越前游戏称 CS；穿越后游戏称《天工枪局》；顶级赛事称万国天工枪赛。
- 大曜朝、承曜二十七年、宣昭帝祁元熙及所有势力均为原创架空。
- 旧版只保留第一章的结构、节拍与文风；第 2—44 章不得复制。
- 人物只复用外观母版；旧姓名、外号、称号、身份、家族、关系和皇帝线不得继承。
- 身份母版继续严格空手；持械只出现在比赛化身或剧情动作资产。
- 每场比赛必须同时能改变局内账、队务账或现实权益中的至少一项。
- 观察者和太监解说面向观众，不得向选手泄露敌方信息。
- 旧目录原样保留为历史源；本次只删除 `.DS_Store`。

---

### Task 1: 根目录导航与新库骨架

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Delete: `重生之twistzz：开宫没有回头监_重写版/.DS_Store`
- Create: `天工枪局：宫门没有回头枪/README.md`
- Create: `天工枪局：宫门没有回头枪/00_书名与IP定位.md`
- Create: `天工枪局：宫门没有回头枪/00_迁移状态.md`

**Interfaces:**
- Consumes: 旧目录路径与新 IP 设计规格。
- Produces: 根级入口、新库权威入口、历史源与新正史的边界。

- [ ] **Step 1:** 写根级 README，列出新作和历史源，并声明默认从新作进入。
- [ ] **Step 2:** 写 `.gitignore` 忽略全仓 `.DS_Store`，并从树中删除已跟踪文件。
- [ ] **Step 3:** 写新库 README、书名定位与迁移状态，明确只有第一章进入新库。
- [ ] **Step 4:** 检查新公开入口没有旧版人物称号、旧皇帝或旧国名。
- [ ] **Step 5:** 将本任务与后续文件一起纳入一次原子迁移提交。

### Task 2: 时代、三权与穿越国运正史

**Files:**
- Create: `天工枪局：宫门没有回头枪/设定/时代背景/01_大曜朝与清制异世界.md`
- Create: `天工枪局：宫门没有回头枪/设定/时代背景/02_朝廷商会江湖三权格局.md`
- Create: `天工枪局：宫门没有回头枪/设定/时代背景/03_穿越国运与回归机制.md`

**Interfaces:**
- Consumes: 大曜朝、承曜二十七年、祁元熙、天工枢网、国运簿和归途残片。
- Produces: 所有正文、人物和游戏设定共同引用的时代事实。

- [ ] **Step 1:** 写架空王朝、技术水平、礼制视觉与非历史清朝边界。
- [ ] **Step 2:** 写天工院、军机火器署、四海票盟、百兵会和火器营的权力/资源/限制。
- [ ] **Step 3:** 写一次性穿越、身体原主责任、国运簿、天工枢网和归途残片。
- [ ] **Step 4:** 逐条确认电脑、皇帝和国运均不能自动改比分、发资格或替人物决定。

### Task 3: 原创游戏与现实后果闭环

**Files:**
- Create: `天工枪局：宫门没有回头枪/设定/游戏背景/01_天工枪局与万国枪赛.md`
- Create: `天工枪局：宫门没有回头枪/设定/游戏背景/02_地图枪械经济阵营统一规则.md`
- Create: `天工枪局：宫门没有回头枪/设定/游戏背景/03_比赛制度与现实后果.md`
- Create: `天工枪局：宫门没有回头枪/设定/游戏背景/04_漫剧三层表现与观察者系统.md`

**Interfaces:**
- Consumes: 时代正史和作者指定的材料、UI、地图、道具、阵营语言。
- Produces: 可直接支撑小说比赛、分镜、视觉提示和长期赛季的游戏规则。

- [ ] **Step 1:** 定义《天工枪局》五人制、万国赛、现代经验优势但非外挂。
- [ ] **Step 2:** 统一地图权、枪械材料、兵筹经济、火药配额、旗色阵营和道具系统。
- [ ] **Step 3:** 建立局内账、队务账、现实账及地图/回合输赢的具体后果表。
- [ ] **Step 4:** 写现实赛台、游戏战场、观察者层及专业太监解说权限。
- [ ] **Step 5:** 验证主角可在内心使用 CS/AK 类比，而公共专名保持原创。

### Task 4: 人物、家族与 IP 圣经

**Files:**
- Create: `天工枪局：宫门没有回头枪/设定/人物家族背景/00_核心人物与家族总表.md`
- Create: `天工枪局：宫门没有回头枪/设定/人物家族背景/01_玄旗队家族债与成长线.md`
- Create: `天工枪局：宫门没有回头枪/设定/人物家族背景/02_皇室朝廷商会江湖人物.md`
- Create: `天工枪局：宫门没有回头枪/设定/人物家族背景/03_旧外观新身份迁移索引_内部.md`
- Create: `天工枪局：宫门没有回头枪/设定/IP圣经/00_专名词典与原创边界.md`
- Create: `天工枪局：宫门没有回头枪/设定/IP圣经/01_长期衍生与赛季框架.md`

**Interfaces:**
- Consumes: 新世界资源和旧外观 blob 索引。
- Produces: 新姓名、家族资源/旧债、赛场职责、政治成长、衍生边界。

- [ ] **Step 1:** 为周烬/谢照夜、裴镇霜、闻青砚、霍长缨、陆停云、纪衡秋、唐照野和祁元熙写家族债。
- [ ] **Step 2:** 把朝廷、商会、江湖、外邦和公共传播配角分组，写明不能越权事项。
- [ ] **Step 3:** 在唯一内部文件记录旧外观标签到新身份的映射，公开文件不得出现旧称号。
- [ ] **Step 4:** 建立专名词典、禁用词和第一部以后可扩展的赛季/地域/媒介框架。

### Task 5: 可生产人物档案与视觉资产迁移

**Files:**
- Create: `天工枪局：宫门没有回头枪/人物档案/00_角色总表.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/01_周烬与谢照夜.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/02_裴镇霜.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/03_闻青砚.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/04_霍长缨.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/05_陆停云.md`
- Create: `天工枪局：宫门没有回头枪/人物档案/06_祁元熙.md`
- Create: `天工枪局：宫门没有回头枪/视觉资产/README.md`
- Copy seven approved character PNG blobs into `视觉资产/人物外观母版/` under new names.
- Copy four scene PNG blobs into `视觉资产/场景历史参考/` with internal-reference naming.

**Interfaces:**
- Consumes: 人物家族正史和已批准旧外观 blobs。
- Produces: 正文、分镜和视觉 Skills 可直接调用的人物事实卡与外观参考。

- [ ] **Step 1:** 写角色总表及六份核心档案，分离现代身份、身体身份和外观锚点。
- [ ] **Step 2:** 复制七张人物外观母版，不复制旧文件名。
- [ ] **Step 3:** 复制四张场景图并明确“构图/材质参考，旧文字非正史”。
- [ ] **Step 4:** 检查标准身份图继续空手，比赛持械资产另行生产。

### Task 6: 第一章重接新世界

**Files:**
- Create: `天工枪局：宫门没有回头枪/正文/目录说明.md`
- Create: `天工枪局：宫门没有回头枪/正文/第01章_输掉决赛后，我成了玄旗队首发.md`

**Interfaces:**
- Consumes: 旧第一章节拍、新人物、新游戏、新机构和新专名。
- Produces: 新 IP 唯一正式正文和后续第二章接口。

- [ ] **Step 1:** 保留现代 Major 决赛、半拍失误、团队复盘和回放异常。
- [ ] **Step 2:** 将现代队友改为关峤、沈砚、程野、薄川，主角为周烬。
- [ ] **Step 3:** 穿越后使用谢照夜、裴镇霜、闻青砚、霍长缨、陆停云和大曜玄旗队。
- [ ] **Step 4:** 通过门禁、名册、奖牌、日期和设备建立真实性，旁人只按失忆/伤情处理。
- [ ] **Step 5:** 自然加入“这不就是 CS 里的 AK 吗”的主角内心类比。
- [ ] **Step 6:** 结尾锁定承天门东掖查档和寻找回路，不提前倾倒全部世界观。
- [ ] **Step 7:** 确认新正文目录只有第一章。

### Task 7: Skills、提示词、分镜与审核入口

**Files:**
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-novel-production/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-human-first-novel-review/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-cinematic-director/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-cinematic-storyboard/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-ancient-character-visual/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/skills/tiangong-match-visual/SKILL.md`
- Create: `天工枪局：宫门没有回头枪/提示词/天工枪局视觉提示词总表.md`
- Create: `天工枪局：宫门没有回头枪/分镜/目录说明.md`
- Create: `天工枪局：宫门没有回头枪/审核/00_迁移验收基准.md`

**Interfaces:**
- Consumes: 新正史、人物档案、正文与视觉母版。
- Produces: 后续章节、盲读、导演书、分镜、人物图和比赛图的六条独立生产工作流。

- [ ] **Step 1:** 复制旧六类能力边界，重命名为 `tiangong-*` 并移除旧专名依赖。
- [ ] **Step 2:** 为每个 Skill 写权威输入优先级、工作流、失败诊断和验收清单。
- [ ] **Step 3:** 写新视觉提示词总表，覆盖身份母版、战斗化身、地图、枪械、UI 和太监解说。
- [ ] **Step 4:** 写分镜入口和迁移验收基准。

### Task 8: 最终验证与提交

**Files:**
- Verify all files created or copied in Tasks 1—7.

**Interfaces:**
- Consumes: 完整迁移树。
- Produces: 可审计的 Git 提交和后续写作起点。

- [ ] **Step 1:** 比较迁移前后树，确认旧目录除 `.DS_Store` 外未被修改。
- [ ] **Step 2:** 列出新目录文件，确认只有一章正文和六项 Skill。
- [ ] **Step 3:** 搜索新公开文件中的旧称号、旧皇帝、`TBD`、`TODO` 和占位符；唯一允许旧称号的位置是内部迁移索引。
- [ ] **Step 4:** 抽查书名、时代、游戏、家族、第一章和 Skill 内容。
- [ ] **Step 5:** 创建单一实现提交并以非强制 fast-forward 更新 `agent/ch01-half-beat-rewrite`。