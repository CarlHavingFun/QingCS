# 明清化比赛战场、武器与太监解说实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `agent/ch01-half-beat-rewrite` 分支建立可直接用于小说、漫剧分镜和图像生产的明清化比赛战场、枪械、战斗化身与太监解说体系。

**Architecture:** 以三个互不混淆的层级组织比赛：现实赛台层、游戏战场层、观察者信息层。核心设定与提示词分别存放，人物身份母版和持械比赛化身严格分流；电影分镜技能只消费经过视觉 Skill 固化的连续性锚点。

**Tech Stack:** Markdown 设定文档、Markdown Skill 文件、GitHub Git Data API、UTF-8。

## Global Constraints

- 采用“战术骨架保留、视觉重新设计”，不做古风贴皮，也不改变 CS 基础玩法。
- 正文与比赛语音继续使用 AK、AWP、M4、烟、闪等通用短名；原创式样名只用于视觉资产和设定。
- 太监解说是专业直播岗位，不使用尖嗓、娘化、身体羞辱或低俗笑话。
- 标准人物定妆照始终空手无武器；比赛化身与剧情动作资产另立任务。
- 现实战队标志、赞助商、真人肖像复刻、随机文字和伪汉字全部禁止。
- 精确 UI 与比分文字以后期合成为主。

---

### Task 1: 固化核心设定与索引

**Files:**
- Create: `设定/09_明清化游戏战场与枪械视觉设定.md`
- Create: `设定/10_太监解说与观察者信息层设定.md`
- Create: `设定/11_明清比赛视觉资产清单.md`
- Modify: `设定/目录说明.md`

**Interfaces:**
- Consumes: 已有世界观、电竞叙事规范和宫廷电竞空间规则。
- Produces: 地图、武器、三层画面、太监解说和资产 ID 的唯一权威入口。

- [ ] **Step 1: 写入三层画面与地图/枪械硬规则**

把现实赛台、游戏战场、观察者信息层的职责写清，并锁定八张首批地图和十四种常用武器/道具式样。

- [ ] **Step 2: 写入太监解说机构、岗位和权限**

明确唱局太监、评策太监、掌镜太监与洛遥音的分工；加入直播延时、隐藏信息、队内语音和回放证据边界。

- [ ] **Step 3: 建立资产登记表**

为地图、武器、道具、战斗化身、观察者 UI、太监解说台和比赛关键帧分配稳定 assetId、文件名、用途、依赖和 QC 条件。

- [ ] **Step 4: 更新设定目录索引**

把 09、10、11 和提示词总表登记为穿越后比赛视觉的权威入口，并声明与旧场景资产清单的关系。

- [ ] **Step 5: 验证核心词与路径**

Run:

```bash
grep -R "现实赛台层\|游戏战场层\|观察者信息层" 设定/09_明清化游戏战场与枪械视觉设定.md
grep -R "唱局太监\|评策太监\|掌镜太监" 设定/10_太监解说与观察者信息层设定.md
```

Expected: 三层画面与三个解说岗位均至少出现一次，且目录中引用路径完全一致。

### Task 2: 建立可直接调用的提示词与角色绑定

**Files:**
- Create: `提示词/明清化比赛地图与武器提示词总表.md`
- Create: `人物档案/24_比赛化身与武器绑定总表.md`
- Modify: `人物档案/目录说明.md`

**Interfaces:**
- Consumes: 09 的视觉规则、人物身份母版和现有职业分工。
- Produces: 地图/枪械/道具设定板提示词、比赛化身提示词模板和上场人物武器连续性。

- [ ] **Step 1: 写统一正向与负面提示块**

锁定材质、色板、功能结构、画幅、文字安全区，以及火绳枪、法器、赛博霓虹、现实 LOGO 等禁止项。

- [ ] **Step 2: 写首批地图提示词**

每张地图必须显式包含 A/B 点、中路、长短道、烟闪空间、回防路线和战斗地理可读性。

- [ ] **Step 3: 写常用枪械与道具提示词**

每件武器写功能轮廓、明清材料、设定板视角、第一人称识别和专属负面约束。

- [ ] **Step 4: 写比赛化身与武器绑定总表**

至少覆盖大清开局五席、霍昭宁和已登记外邦上场角色；教练、队务和官员明确不自动获得游戏战斗化身。

- [ ] **Step 5: 更新人物目录并验证空手分流**

Run:

```bash
grep -R "标准定妆.*空手\|比赛化身.*持械" 人物档案/24_比赛化身与武器绑定总表.md 人物档案/目录说明.md
```

Expected: 身份母版与比赛化身的边界明确，目录能找到新总表。

### Task 3: 建立比赛视觉 Skill 与电影分镜路由

**Files:**
- Create: `skills/qingcs-mingqing-match-visual/SKILL.md`
- Modify: `skills/qingcs-ancient-character-visual/SKILL.md`
- Modify: `skills/qingcs-cinematic-director/SKILL.md`
- Modify: `skills/qingcs-cinematic-storyboard/SKILL.md`

**Interfaces:**
- Consumes: 09、10、11、提示词总表与比赛化身绑定表。
- Produces: 从角色母版到比赛化身、地图/武器关键帧、三层比赛镜头和太监解说音轨的固定生产流程。

- [ ] **Step 1: 创建比赛视觉 Skill**

规定输入、资产分类、地图工作流、武器工作流、比赛化身工作流、观察者层工作流、提示词字段、连续性和失败诊断。

- [ ] **Step 2: 更新古风人物 Skill 路由**

保留空手硬锁，并明确检测到持械、游戏战场或比赛动作需求时转交 `qingcs-mingqing-match-visual`。

- [ ] **Step 3: 更新导演 Skill**

加入现实赛台→游戏战场→观察者信息→现实反应的镜头语法、太监解说 J-cut/L-cut 用法和 UI 后期合成规则。

- [ ] **Step 4: 更新分镜 Skill**

在连续性圣经和 H3 字段中加入 `LAYER / MAP / WEAPON / AVATAR / OBSERVER / EUNUCH_CAST / UI_SAFE_AREA`。

- [ ] **Step 5: 验证 Skill 路由**

Run:

```bash
grep -R "qingcs-mingqing-match-visual" skills/qingcs-ancient-character-visual/SKILL.md skills/qingcs-cinematic-director/SKILL.md skills/qingcs-cinematic-storyboard/SKILL.md
grep -R "EUNUCH_CAST\|太监解说" skills/qingcs-cinematic-*/SKILL.md skills/qingcs-mingqing-match-visual/SKILL.md
```

Expected: 三个消费 Skill 均引用比赛视觉 Skill，导演和分镜均包含太监解说字段。

### Task 4: 全局一致性验证与提交

**Files:**
- Verify: all files from Tasks 1-3

**Interfaces:**
- Consumes: 全部新增和修改文件。
- Produces: 一个无占位符、无断链、可回溯的 Git 提交。

- [ ] **Step 1: 扫描占位符与冲突词**

Run:

```bash
! grep -R -nE "T[B]D|T[O]DO|待[补]|以后再[写]" \
  设定/09_明清化游戏战场与枪械视觉设定.md \
  设定/10_太监解说与观察者信息层设定.md \
  设定/11_明清比赛视觉资产清单.md \
  提示词/明清化比赛地图与武器提示词总表.md \
  人物档案/24_比赛化身与武器绑定总表.md \
  skills/qingcs-mingqing-match-visual/SKILL.md
```

Expected: no matches.

- [ ] **Step 2: 验证必需规则同时存在**

Run:

```bash
grep -R "战术骨架保留、视觉重新设计" 设定/09_明清化游戏战场与枪械视觉设定.md
grep -R "不.*尖嗓\|不得.*尖嗓" 设定/10_太监解说与观察者信息层设定.md
grep -R "火绳枪\|仙侠法器" 提示词/明清化比赛地图与武器提示词总表.md
grep -R "精确.*后期合成" skills/qingcs-mingqing-match-visual/SKILL.md skills/qingcs-cinematic-storyboard/SKILL.md
```

Expected: all commands return at least one match.

- [ ] **Step 3: 检查路径清单**

逐项确认计划中的 11 个目标路径都已进入新树对象，修改文件使用最新 blob，未删除旧资产。

- [ ] **Step 4: 创建单一实现提交并快进分支**

Commit message:

```text
feat: add Ming-Qing match visuals and eunuch commentary
```

Expected: `agent/ch01-half-beat-rewrite` 从计划提交快进到实现提交，无强制更新。
