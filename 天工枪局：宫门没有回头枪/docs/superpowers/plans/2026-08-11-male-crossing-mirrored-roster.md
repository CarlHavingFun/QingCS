# 男性肉身穿越与同名女队重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将新作统一改为周野男性肉身独自穿越、四名同名女性本地队友、谢晚失踪和唯一男性终端检测通过的正式正史。

**Architecture:** 先修改 IP 词典、世界规则和人物家族事实，再更新人物档案与视觉资产命名，最后重写第一章后半、六项生产 Skill 和验收文件。旧目录只作历史源，不改正文。

**Tech Stack:** Markdown、GitHub Git Data API、现有 PNG blob 复用。

## Global Constraints

- 周野是男性肉身，只有他一人穿越。
- 现代陈默、林溪、赵雨、顾遥均为男性并留在现代。
- 大曜陈默、林溪、赵雨、顾遥均为女性本地职业选手。
- 谢晚是大曜原第五人，在 `7:5` 异常时失踪。
- 周野是故事开局唯一通过最高级检测的男性玩家。
- 通过检测只获得试训与赛照申请资格，不自动获得谢晚席位。
- 禁止后宫化、男性天然更强、女队等待拯救和低俗性别福利。
- 历史源目录不得被新设定批量改写。

---

### Task 1: 锁定正史专名和制度

**Files:**
- Create: `设定/游戏背景/05_唯一男性选手与天衡检测.md`
- Modify: `README.md`
- Modify: `00_书名与IP定位.md`
- Modify: `00_迁移状态.md`
- Modify: `设定/IP圣经/00_专名词典与原创边界.md`
- Modify: `设定/IP圣经/01_长期衍生与赛季框架.md`
- Modify: `设定/时代背景/03_穿越国运与回归机制.md`
- Modify: `设定/游戏背景/01_天工枪局与万国枪赛.md`
- Modify: `设定/游戏背景/03_比赛制度与现实后果.md`
- Modify: `设定/游戏背景/04_漫剧三层表现与观察者系统.md`
- Modify: `设定/目录说明.md`

**Interfaces:**
- Consumes: approved name map and crossing rules.
- Produces: canonical public names, fifth-seat mystery and male terminal rules for every later file.

- [ ] **Step 1:** Replace the old body-swap premise with male physical crossing and the mirrored roster.
- [ ] **Step 2:** Register all canonical names and explicit same-name/different-person boundaries.
- [ ] **Step 3:** Add the four-stage terminal test and the distinction between short-term pass, full license and roster selection.
- [ ] **Step 4:** Verify public canon contains no statement that Zhou Ye occupies Xie Wan's body.

### Task 2: Rebuild people, families and asset names

**Files:**
- Rename and rewrite: `人物档案/01_周野与谢晚.md`
- Rename and rewrite: `人物档案/02_陈默.md`
- Rename and rewrite: `人物档案/03_林溪.md`
- Rename and rewrite: `人物档案/04_赵雨.md`
- Rename and rewrite: `人物档案/05_顾遥.md`
- Rename and rewrite: `人物档案/06_祁元.md`
- Modify: `人物档案/00_角色总表.md`
- Modify: `设定/人物家族背景/00_核心人物与家族总表.md`
- Modify: `设定/人物家族背景/01_玄旗队家族债与成长线.md`
- Modify: `设定/人物家族背景/02_皇室朝廷商会江湖人物.md`
- Modify: `设定/人物家族背景/03_旧外观新身份迁移索引_内部.md`
- Rename PNG files under `视觉资产/人物外观母版/`
- Modify: `视觉资产/README.md`
- Modify: `提示词/天工枪局视觉提示词总表.md`

**Interfaces:**
- Consumes: canonical rules from Task 1.
- Produces: reusable character facts and correctly named visual references.

- [ ] **Step 1:** Preserve the established family debts and tactical functions while replacing names.
- [ ] **Step 2:** Give modern and大曜 same-name characters separate histories, habits and speech.
- [ ] **Step 3:** Define consent, living-space, medical and data boundaries around the only male player.
- [ ] **Step 4:** Rename reused PNG blobs without changing image bytes.
- [ ] **Step 5:** Verify old public names remain only in the internal migration index.

### Task 3: Rewrite Chapter 1 around the new reveal

**Files:**
- Rename and rewrite: `正文/第01章_输掉决赛后，我成了玄旗队唯一男选手.md`
- Modify: `正文/目录说明.md`
- Modify: root `README.md`

**Interfaces:**
- Consumes: canonical names, terminal rules and character reactions.
- Produces: the only current public chapter and the launch point for Chapter 2.

- [ ] **Step 1:** Preserve the Major final, half-beat failure, factual review, `7:5` anomaly and medal evidence.
- [ ] **Step 2:** Replace modern teammate names with Chen Mo, Lin Xi, Zhao Yu and Gu Yao.
- [ ] **Step 3:** Have Zhou Ye arrive in his own male body while Xie Wan disappears.
- [ ] **Step 4:** Reveal the four female same-name players through natural dialogue and observable habits.
- [ ] **Step 5:** Run only the short-term terminal test and end with a three-day full-review countdown.
- [ ] **Step 6:** Verify the chapter contains no body-swap remnants or automatic starter declaration.

### Task 4: Update production Skills and acceptance gates

**Files:**
- Modify: `skills/tiangong-novel-production/SKILL.md`
- Modify: `skills/tiangong-human-first-novel-review/SKILL.md`
- Modify: `skills/tiangong-cinematic-director/SKILL.md`
- Modify: `skills/tiangong-cinematic-storyboard/SKILL.md`
- Modify: `skills/tiangong-ancient-character-visual/SKILL.md`
- Modify: `skills/tiangong-match-visual/SKILL.md`
- Modify: `分镜/目录说明.md`
- Modify: `审核/00_迁移验收基准.md`

**Interfaces:**
- Consumes: completed canon and chapter.
- Produces: future-proof generation, review and visual constraints.

- [ ] **Step 1:** Add mirrored-roster and only-male checks to novel production and review.
- [ ] **Step 2:** Add male-body, female-team, consent and space-boundary fields to director/storyboard output.
- [ ] **Step 3:** Separate Zhou Ye male visual DNA from the seven reused female appearance masters.
- [ ] **Step 4:** Add negative checks for harem framing, body-swap remnants and automatic roster inheritance.
- [ ] **Step 5:** Verify every Skill references the renamed canonical files.

### Task 5: Repository-wide verification and commit

**Files:**
- Create: `审核/2026-08-11_男性肉身穿越与同名女队重构说明.md`

**Interfaces:**
- Consumes: all previous tasks.
- Produces: auditable completion evidence.

- [ ] **Step 1:** Verify expected new and renamed files exist.
- [ ] **Step 2:** Verify deleted old paths no longer appear in the new directory.
- [ ] **Step 3:** Scan public new-canon text for old names and body-swap phrases.
- [ ] **Step 4:** Verify the first chapter has one male crossing, four female same-name teammates and one missing fifth player.
- [ ] **Step 5:** Create a fast-forward Git commit on `agent/ch01-half-beat-rewrite`.
