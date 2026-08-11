# First Chapter Human Dialogue Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 清理第一章穿越后半段的 AI 总结腔和公文腔，并把穿越前赛事统一为上海举办的中国 Major 总决赛。

**Architecture:** 不改变剧情和事件顺序，只重写对白与旁白表达；通过生产 Skill 与审核 Skill 增加“人话硬锁”，防止后续章节复发。中国 Major 只改现代段的举办地和索引，不改变国际赛事性质。

**Tech Stack:** Markdown 小说、设定与 Skill 文档，GitHub contents API。

## Global Constraints

- 不改变白桥民间赛、七日临时客籍、两轮试训、`7:5` 和第一章结尾。
- 不新增剧情或新角色。
- 不把专业角色写成随意或低智，只去掉不自然的公文串句和作者总结。
- 上海中国 Major 是国际 Major，不是中国国内联赛。
- 历史源目录不修改。

---

### Task 1: 清理第一章对白与旁白

**Files:**
- Modify: `正文/第01章_输掉Major后，我从民间赛重新开始.md`

- [ ] **Step 1:** 将“手机、奖牌和衣服分开拍照。人没同意，不碰身”改为现场自然口语。
- [ ] **Step 2:** 删除“每一句都像写进账里”“她只报了名字，没有说我们以后会是什么关系”等作者总结。
- [ ] **Step 3:** 清理“没被激将”“没有突然相信我的全部故事”“三个人都没有说欢迎”等解释性旁白，以动作或下一句对白替代。
- [ ] **Step 4:** 将韩平、苏禾涉及客籍和担保的对白改成可以口头说出的短句，保留制度信息。
- [ ] **Step 5:** 把“她们不是等我来救的一支队伍”等总结压缩成周野更自然的第一人称判断。
- [ ] **Step 6:** 全章现代段将北港赛事地名统一为上海举办的中国 Major。

### Task 2: 固化语言规则

**Files:**
- Modify: `skills/tiangong-novel-production/SKILL.md`
- Modify: `skills/tiangong-human-first-novel-review/SKILL.md`

- [ ] **Step 1:** 生产 Skill 增加“人话硬锁”：禁止标签式总结、解释对白真实含义、连续公文名词串。
- [ ] **Step 2:** 审核 Skill 增加专项扫描，要求指出并替换“像写进账里”类型句式。

### Task 3: 同步中国 Major 索引

**Files:**
- Modify: `人物档案/01_周野.md`
- Modify: `正文/目录说明.md`
- Modify: `分镜/目录说明.md`
- Modify: `提示词/天工枪局视觉提示词总表.md`
- Modify: `审核/00_迁移验收基准.md`

- [ ] **Step 1:** 统一现代赛事为上海举办的中国 Major 总决赛。
- [ ] **Step 2:** 保留“Major”作为职业履历与第一章标题核心，不改白桥后续结构。
- [ ] **Step 3:** 审核基准增加“活跃正史不得把北港 Major 当举办地”的检查项。

### Task 4: 验证并提交

**Files:**
- Verify all modified active-new-canon files.

- [ ] **Step 1:** 搜索第一章，确认不再存在“每一句都像写进账里”“人没同意，不碰身”“没被激将”“三个人都没有说欢迎”。
- [ ] **Step 2:** 搜索活跃正史现代段，确认当前赛事称为上海/中国 Major；历史源可保留旧文本。
- [ ] **Step 3:** 抽查穿越后事件顺序未变化：设备间→客籍→试训一→试训二→报名。
- [ ] **Step 4:** 检查分支 HEAD 和提交差异。
