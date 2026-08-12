# 第一章样片分镜重制 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按正文原话和真实表演节奏，建立可审核、可机械验证、可用于后续 GPT Image 关键帧生产的第一章样片分镜事实源。

**Architecture:** 正文是唯一剧情事实源；先生成逐字台词锁与镜头时间轴，再写锚点、逐镜分镜和关键帧提示词，最后由本地校验脚本检查原文匹配、时长下限、字段完整性与提示词单一时刻。旧稿只归档，不参与新版生产。

**Tech Stack:** Markdown、JSON、Python 3 标准库、Git；使用 `libtv-shortdrama-storyboard` 的分析、锚点和六元素镜头方法，不调用 LibTV API/CLI；本计划不调用 GPT Image、ComfyUI 或 MiniMax H3。

## Global Constraints

- 成片不设目标秒数；当前约 96 秒只是建议值，最终以真实音轨、动作和反应时间为准。
- 所有可听人声必须逐字来自 `正文/第01章_输掉Major后，我从民间赛重新开始.md`，禁止改写和模型补白。
- 每镜必须有“逐字台词”或“无台词／刻意沉默”及其叙事作用。
- 关键帧不生成字幕、比分、姓名、表格文字或随机 UI；精确文字只进入 `POST_TEXT`。
- 周野穿越前后是同一二十四岁男性身体、同一现代队服、同一右腕黑色护带。
- 旧稿与旧生成物只能归档，不删除；工作区内其他用户改动不得回滚或混入提交。
- 视觉风格为高完成度电影级 3D 国漫，不得呈现廉价游戏截图、塑料皮肤、二维平涂或直接真人照片。

---

### Task 1: 归档旧事实源并建立重制入口

**Files:**
- Move: `分镜/第01章_70秒样片导演书.md` → `分镜/历史版本/2026-08-12_重做前/第01章_70秒样片导演书.md`
- Move: `分镜/第01章_70秒样片逐镜头分镜.md` → `分镜/历史版本/2026-08-12_重做前/第01章_70秒样片逐镜头分镜.md`
- Move: `分镜/第01章_70秒样片关键帧与视频运动提示词.md` → `分镜/历史版本/2026-08-12_重做前/第01章_70秒样片关键帧与视频运动提示词.md`
- Move: `AI生产/样片01/声音/dialogue-lock.json` → `AI生产/样片01/rejected/storyboard-v1/dialogue-lock.json`
- Modify: `分镜/目录说明.md`

**Interfaces:**
- Consumes: 已批准设计 `docs/superpowers/specs/2026-08-12-ch01-storyboard-rebuild-design.md`。
- Produces: 新版文件名和读取顺序；后续任务不得读取历史版本作为事实源。

- [ ] **Step 1: 建立归档目录并移动四份旧事实源**

使用 `mkdir -p` 建立两个明确目录，再使用 `mv` 移动上述四份文件；不移动 `AI生产/样片01/视觉/keyframes/`，它们继续留作被拒绝素材证据。

- [ ] **Step 2: 重写目录说明**

新版读取顺序固定为：`正文 → 台词锁 → 锚点清单 → 重制版逐镜分镜 → 重制版关键帧提示词`。明确旧素材状态为“历史／禁止生产读取”。

- [ ] **Step 3: 验证归档边界**

Run:

```bash
test -f '分镜/历史版本/2026-08-12_重做前/第01章_70秒样片逐镜头分镜.md'
test ! -f '分镜/第01章_70秒样片逐镜头分镜.md'
test -f 'AI生产/样片01/rejected/storyboard-v1/dialogue-lock.json'
```

Expected: 三条命令全部退出码 0；旧关键帧图片仍存在且未删除。

- [ ] **Step 4: Commit**

```bash
git add -- '分镜' 'AI生产/样片01/rejected/storyboard-v1/dialogue-lock.json'
git commit -m 'docs: archive rejected chapter 1 storyboard'
```

### Task 2: 建立正文逐字台词锁与校验器

**Files:**
- Create: `AI生产/样片01/声音/dialogue-lock-v2.json`
- Create: `AI生产/样片01/声音/validate_storyboard_v2.py`

**Interfaces:**
- Consumes: 正文 Markdown 和设计中的镜头编号、说话人、表演方式、建议时长。
- Produces: `dialogue-lock-v2.json`，字段为 `shot_id`、`speaker_id`、`delivery`、`text`、`source_line`、`start_hint_s`、`end_hint_s`；校验器退出码 0 表示全部台词可逐字回查正文。

- [ ] **Step 1: 先写校验器的失败场景**

校验器必须检查：JSON 可解析、台词非空、`text` 在正文中逐字出现、同镜时间区间不倒置、非正文句触发错误。先对当前旧锁运行：

```bash
python3 'AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue 'AI生产/样片01/rejected/storyboard-v1/dialogue-lock.json'
```

Expected: FAIL，并列出旧锁中不在正文的句子。

- [ ] **Step 2: 写入新版逐字台词锁**

只收录设计中锁定的正文原句。S07_SH01 的内心声使用 `也好。` 与 `第一枪，从白桥开始。` 两个连续正文句；保留同一 `ZHOU_YE_INNER` 声线身份。

- [ ] **Step 3: 验证新版台词锁**

```bash
python3 'AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue 'AI生产/样片01/声音/dialogue-lock-v2.json'
```

Expected: PASS，输出锁定台词数量和全部原文匹配。

- [ ] **Step 4: Commit**

```bash
git add -- 'AI生产/样片01/声音/dialogue-lock-v2.json' 'AI生产/样片01/声音/validate_storyboard_v2.py'
git commit -m 'feat: lock chapter 1 dialogue to source text'
```

### Task 3: 建立新版锚点清单

**Files:**
- Create: `分镜/第01章_样片锚点清单_重制版.md`

**Interfaces:**
- Consumes: `视觉资产/人物外观母版/*.png`、场景历史参考和视觉提示词总表。
- Produces: A 类人物、B 类场景、C 类道具锚点 ID；逐镜分镜只引用 ID，不重新发明人物长相。

- [ ] **Step 1: 写人物锚点**

为现代与白桥出场人物建立稳定 ID、母版绝对路径、年龄性别、服装、面部特征、气质和必用镜头。周野额外锁定现代队服、赛事布标和右腕护带。

- [ ] **Step 2: 写场景与道具锚点**

建立上海比赛席、隔音休息室、白桥设备间、训练区、报名桌，以及亚军奖牌、声卡耳机、赤漆连珠铳、震声雷、报名表锚点。

- [ ] **Step 3: 检查锚点可解析性**

```bash
rg -n '^### [ABC][0-9]+' '分镜/第01章_样片锚点清单_重制版.md'
rg -n '母版路径|视觉描述|用途镜头|负面约束' '分镜/第01章_样片锚点清单_重制版.md'
```

Expected: 所有角色、场景和道具都有稳定 ID 与四类必要信息。

- [ ] **Step 4: Commit**

```bash
git add -- '分镜/第01章_样片锚点清单_重制版.md'
git commit -m 'docs: add chapter 1 visual anchors'
```

### Task 4: 编写真实节奏逐镜分镜

**Files:**
- Create: `分镜/第01章_样片逐镜头分镜_重制版.md`
- Modify: `AI生产/样片01/声音/validate_storyboard_v2.py`

**Interfaces:**
- Consumes: `dialogue-lock-v2.json` 和锚点 ID。
- Produces: 每镜完整字段、建议时长和连续时间码；关键帧任务直接读取 `KEYFRAME_MOMENT` 与 `ANCHOR_REFS`。

- [ ] **Step 1: 扩展校验器使缺字段先失败**

每镜必须出现：`SHOT_ID`、`ADVISORY_DURATION`、`SOURCE_EXCERPT`、`OBJECTIVE`、`ANCHOR_REFS`、`CAMERA_SIZE`、`CAMERA_MOVE`、`ACTION_START`、`ACTION_END`、`COMPOSITION`、`LIGHT`、`EMOTION`、`DIALOGUE`、`DIALOGUE_TIMING`、`SOUND`、`CONTINUITY_IN`、`CONTINUITY_OUT`、`POST_TEXT`、`KEYFRAME_MOMENT`、`NEGATIVE`。在文件尚不存在时运行必须失败。

- [ ] **Step 2: 写 S01–S03**

锁定三个关键因果：第二脚步先出现、准星先离位、赵雨后倒下；异常顺序为旧报点脱离设备 → 录像失败与 7:5 → 木框 → 钟声 → 下坠 → 奖牌滑落。

- [ ] **Step 3: 写 S04–S07**

白桥醒来保持安全距离；第一轮与第二轮训练使用相似战术轴线；第二轮必须先补近点再转右廊；结尾报名表文字进入 `POST_TEXT`，内心声使用正文原句。

- [ ] **Step 4: 运行完整分镜校验**

```bash
python3 'AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue 'AI生产/样片01/声音/dialogue-lock-v2.json' \
  --storyboard '分镜/第01章_样片逐镜头分镜_重制版.md'
```

Expected: PASS；报告镜头数、建议总时长、台词匹配数、字段完整性。建议总时长可以变化，不设置等值断言。

- [ ] **Step 5: Commit**

```bash
git add -- '分镜/第01章_样片逐镜头分镜_重制版.md' 'AI生产/样片01/声音/validate_storyboard_v2.py'
git commit -m 'docs: rebuild chapter 1 storyboard at natural pace'
```

### Task 5: 编写逐镜关键帧提示词

**Files:**
- Create: `分镜/第01章_样片关键帧提示词_重制版.md`
- Modify: `AI生产/样片01/声音/validate_storyboard_v2.py`

**Interfaces:**
- Consumes: 新版分镜的 `SHOT_ID`、`ANCHOR_REFS`、`KEYFRAME_MOMENT`、`POST_TEXT` 和连续性字段。
- Produces: 每镜一条可直接交给 GPT Image 的 `KEYFRAME_PROMPT`、`KEYFRAME_NEGATIVE`、`REFERENCE_IMAGES` 和 `POST_TEXT`。

- [ ] **Step 1: 扩展校验器检查提示词一一对应**

校验器检查每个分镜 `SHOT_ID` 恰好对应一组关键帧字段，引用锚点存在，精确台词与比分不进入 `KEYFRAME_PROMPT`，每条提示词包含统一视觉后缀和 16:9 规格。

- [ ] **Step 2: 写现代段关键帧提示词**

S01–S03 强调冷蓝玻璃、可信设备、操作手部和异常的逐层发生；任何一帧不得同时塞入多个时间阶段。

- [ ] **Step 3: 写白桥段关键帧提示词**

S04–S07 引用人物外观母版和场景／道具锚点，保持高完成度 3D 国漫材质；训练失败与成功使用同一轴线但不同动作临界帧。

- [ ] **Step 4: 运行全量校验**

```bash
python3 'AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue 'AI生产/样片01/声音/dialogue-lock-v2.json' \
  --storyboard '分镜/第01章_样片逐镜头分镜_重制版.md' \
  --keyframes '分镜/第01章_样片关键帧提示词_重制版.md'
```

Expected: PASS；镜头 ID 与关键帧 ID 一一对应，没有精确文字泄漏到生图提示词。

- [ ] **Step 5: Commit**

```bash
git add -- '分镜/第01章_样片关键帧提示词_重制版.md' 'AI生产/样片01/声音/validate_storyboard_v2.py'
git commit -m 'docs: add source-locked chapter 1 keyframe prompts'
```

### Task 6: 总体验收与生产停点

**Files:**
- Modify: `分镜/目录说明.md`
- Create: `AI生产/样片01/README_重制版.md`

**Interfaces:**
- Consumes: 所有新版事实源与校验结果。
- Produces: 后续 GPT Image、原创声线和 H3 生产唯一入口；在用户审阅关键帧提示词前保持生成停点。

- [ ] **Step 1: 更新生产入口**

写明文件读取顺序、旧稿禁用、声音 ID 尚待实际样本、关键帧尚未生成、视频尚未重制。

- [ ] **Step 2: 运行最终验证**

```bash
python3 'AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue 'AI生产/样片01/声音/dialogue-lock-v2.json' \
  --storyboard '分镜/第01章_样片逐镜头分镜_重制版.md' \
  --keyframes '分镜/第01章_样片关键帧提示词_重制版.md'
git diff --check
```

Expected: 校验器 PASS，`git diff --check` 无输出。

- [ ] **Step 3: 人工抽检四个连续性点**

逐项核对：S01 准星与倒地因果；S03 异常顺序；S05/S06 重复机位中的选择变化；S07 正文内心声。发现问题只修事实源，不生成图片补救分镜问题。

- [ ] **Step 4: Commit**

```bash
git add -- '分镜/目录说明.md' 'AI生产/样片01/README_重制版.md'
git commit -m 'docs: publish chapter 1 rebuild production entry'
```

- [ ] **Step 5: 停止并请求用户审阅**

列出新版分镜、锚点和关键帧提示词的绝对路径，明确“尚未调用生成”。得到用户确认后，下一阶段才使用 `gpt-image` 生成少量代表镜头进行视觉校样。

