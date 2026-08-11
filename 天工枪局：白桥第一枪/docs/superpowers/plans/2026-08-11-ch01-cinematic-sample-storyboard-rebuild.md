# 第一章电影级样片分镜重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用三份可直接驱动关键帧、MiniMax H3 和声音生产的电影级文件替换第一章两份粗糙分镜，并建立唯一生产入口。

**Architecture:** 以正式第一章正文为叙事源，用导演书管理七段场景意图，用 18 个共享 `SHOT_ID` 的逐镜头分镜管理可拍动作，再用同一组 ID 的提示词文件分离 GPT Image 静态关键帧事实与 MiniMax H3 时间运动。新文件全部通过字段、数量、ID 集合与禁用词验证后，才删除旧稿并更新目录入口。

**Tech Stack:** Markdown、Git、Bash/`rg`/`sed`/`awk`/`diff` 验证、`tiangong-cinematic-director`、`tiangong-cinematic-storyboard`、`tiangong-ancient-character-visual`、`tiangong-match-visual`；提示词阶段使用 `gpt-image` 与 `h3-prompt-writing` skills。

## Global Constraints

- 当前范围只重构分镜生产文件；不在本计划中调用付费生成接口、创建 Voice ID、生成图片、提交 ComfyUI 队列或生成视频。
- 样片画幅固定 16:9；最终剪辑目标 1920×1080、24 fps、65—75 秒。
- 风格固定为电影级半写实国漫：现代段冷蓝黑灰，白桥段青砖、漆木、黄铜、黑化钢与暖灰。
- 样片覆盖十个核心节拍，并拆成恰好 18 个 `SHOT_ID`；总设计时长固定为 68.5 秒。
- 三层画面只使用 `REALITY`、`GAME`、`OBSERVER`；白桥私训不得出现太监解说或完整转播团队。
- 周野穿越前后是同一名二十四岁男性、同一身体、同一现代队服、同一右腕护带；亚军奖牌跨世界连续。
- 现代队友陈默、林溪、赵雨、顾遥只属于上海 Major 段；不得与苏禾、江宁、唐夏、许安同脸、同名或性转对应。
- 周野没有系统外挂、国家队开局、职业赛籍赠送或正式天衡检测。
- 白桥枪馆必须狭窄、旧、有维修痕迹，不能成为豪华宫廷电竞殿。
- 赤漆连珠铳保留现代机匣、导气、弹匣、枪托、瞄具和抛壳结构；禁止火绳枪、法器、蒸汽朋克和满枪黄金。
- 精确比分、姓名、报名表文字、HUD 和字幕全部后期合成；提示词只保留版式与安全区。
- 每个镜头只完成一个主要信息变化；第一轮失败与第二轮成功复用轴线和近似构图。
- 所有新增 Markdown 文件必须以换行结尾，不得包含占位标记或空字段。
- 不修改 `重生之twistzz：开宫没有回头监_重写版/` 历史源。

## File Structure

- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md` — 七段场景级意图、三层切换、声音优先级、连续性和剪辑出口。
- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md` — 18 个可执行镜头及完整导演/分镜字段，是画面与声音生产的镜头事实源。
- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md` — 与 18 个镜头一一对应的 GPT Image 静态提示、MiniMax H3 运动提示和声音提示。
- Modify: `天工枪局：白桥第一枪/分镜/目录说明.md` — 删除旧入口并声明三份新文件的读取顺序。
- Modify: `.gitignore` — 忽略视觉伴侣生成的 `.superpowers/` 本地目录。
- Delete: `天工枪局：白桥第一枪/分镜/第一章_输掉Major后我从民间赛重新开始_完整分镜.md` — 旧场景提纲。
- Delete: `天工枪局：白桥第一枪/分镜/第一章_逐镜头生产分镜.md` — 字段不完整的 42 镜头粗稿。

---

### Task 1: 建立七段电影导演书

**Files:**
- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md`
- Read: `天工枪局：白桥第一枪/正文/第01章_输掉Major后，我从民间赛重新开始.md`
- Read: `天工枪局：白桥第一枪/skills/tiangong-cinematic-director/SKILL.md`
- Read: `天工枪局：白桥第一枪/设定/游戏背景/04_漫剧三层表现与观察者系统.md`

**Interfaces:**
- Consumes: 正式正文中的事件顺序、导演 Skill 的 14 个字段、设计规格中的 68.5 秒结构。
- Produces: 七个 `SCENE_ID`：`S01_MAJOR_FINAL`、`S02_REVIEW_ROOM`、`S03_075_ANOMALY`、`S04_WHITE_BRIDGE_ARRIVAL`、`S05_TRIAL_FAILURE`、`S06_TRIAL_SUCCESS`、`S07_REGISTRATION`。

- [ ] **Step 1: 重读导演约束并固定场景表**

在文件开头写明：

```text
总设计时长：68.5 秒
画幅：16:9
最终输出：1920×1080 / 24 fps
场景数：7
镜头数：18
```

随后写入场景时长表：

```text
S01_MAJOR_FINAL             14.0s
S02_REVIEW_ROOM              7.0s
S03_075_ANOMALY             10.5s
S04_WHITE_BRIDGE_ARRIVAL    12.0s
S05_TRIAL_FAILURE            7.5s
S06_TRIAL_SUCCESS            8.5s
S07_REGISTRATION             9.0s
TOTAL                       68.5s
```

- [ ] **Step 2: 写现代 Major 与复盘场景**

为 `S01_MAJOR_FINAL` 和 `S02_REVIEW_ROOM` 完整填写：

```text
SCENE_ID:
LAYER:
LOCATION:
TIME:
CHARACTERS:
TACTICAL_FACT:
CAMERA:
MOVEMENT:
SOUND_PRIORITY:
PROP_CONTINUITY:
UI_SAFE_AREA:
REALITY_RETURN:
RESOURCE_STAKE:
NEXT_CUT:
```

硬事实包括：进攻方守包、四打三、比分 16:18、周野是赵雨的补枪位、准星向 A1 深处偏移、赵雨先倒、对手带拆弹器五秒拆除、最终 16:19；复盘不甩锅，周野主动承认听到第二脚步却没有及时报出。

- [ ] **Step 3: 写 `7:5` 转场场景**

为 `S03_075_ANOMALY` 填满 14 个字段。转场顺序固定为：断开声卡后声音仍在 → 回放时间和嘴型错位 → 比分短暂跳到 `7:5` → 手机回看只有黑屏 → A 点三箱边缘木框化 → 奖牌滑落不着地 → C4 提示音变成低沉钟响。

- [ ] **Step 4: 写白桥到达与两轮试训场景**

为 `S04_WHITE_BRIDGE_ARRIVAL`、`S05_TRIAL_FAILURE`、`S06_TRIAL_SUCCESS` 填满字段。明确四人场面调度、普通终端、断网记录、赤漆连珠铳现代机械结构、震声雷撞梁、第一次准星离开唐夏近点、第二次“右廊可能一个”与“右廊到门”分级报点。

- [ ] **Step 5: 写报名场景**

为 `S07_REGISTRATION` 填满字段。现实账必须回场：服务器欠款、南城公开赛报名锁定、七日临时客籍、四个人各自确认资源；苏禾是拍板者，周野只获得可撤销的试报名资格。

- [ ] **Step 6: 验证导演书场景数和字段**

Run:

```bash
book='天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md'
test "$(rg -c '^SCENE_ID:' "$book")" -eq 7
for field in LAYER LOCATION TIME CHARACTERS TACTICAL_FACT CAMERA MOVEMENT SOUND_PRIORITY PROP_CONTINUITY UI_SAFE_AREA REALITY_RETURN RESOURCE_STAKE NEXT_CUT; do
  test "$(rg -c "^${field}:" "$book")" -eq 7
done
rg -n 'TB[D]|TO[D]O|待填[写]|__UNRESOLVE[D]__' "$book" && exit 1 || true
```

Expected: 所有 `test` 成功；最后一条 `rg` 无输出。

- [ ] **Step 7: 提交导演书**

```bash
git add -- '天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md'
git commit -m 'docs: add chapter 1 cinematic sample director book'
```

### Task 2: 写 18 镜头完整生产分镜

**Files:**
- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md`
- Read: `天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md`
- Read: `天工枪局：白桥第一枪/skills/tiangong-cinematic-storyboard/SKILL.md`
- Read: `天工枪局：白桥第一枪/skills/tiangong-match-visual/SKILL.md`
- Read: `天工枪局：白桥第一枪/人物档案/01_周野.md`
- Read: `天工枪局：白桥第一枪/人物档案/02_苏禾.md`
- Read: `天工枪局：白桥第一枪/人物档案/03_江宁.md`
- Read: `天工枪局：白桥第一枪/人物档案/04_唐夏.md`
- Read: `天工枪局：白桥第一枪/人物档案/05_许安.md`

**Interfaces:**
- Consumes: Task 1 的七个 `SCENE_ID`、人物 ID、场景 ID、导演意图与时长预算。
- Produces: 以下 18 个稳定 `SHOT_ID`，后续提示词、关键帧、视频和音频不得改名：

```text
S01_SH01 3.5s  REALITY  场馆与周野比赛席
S01_SH02 3.5s  GAME     四打三与第二脚步
S01_SH03 3.0s  REALITY  鼠标微动与补枪断链
S01_SH04 4.0s  OBSERVER 五秒拆除、16:19、亚军
S02_SH01 3.5s  REALITY  休息室事实复盘
S02_SH02 3.5s  REALITY  周野承认漏报
S03_SH01 3.0s  REALITY  拔线后声音仍在
S03_SH02 3.5s  OBSERVER 7:5 与手机留证失败
S03_SH03 4.0s  REALITY  木框、奖牌与钟声坠落
S04_SH01 4.0s  REALITY  白桥醒来确认同一身体
S04_SH02 4.0s  REALITY  四人安全距离与身份询问
S04_SH03 4.0s  OBSERVER 天工系统 7:5 与临时客籍
S05_SH01 3.5s  GAME     赤漆连珠铳与震声雷碰梁
S05_SH02 4.0s  GAME     准星离近点、唐夏倒下
S06_SH01 4.0s  REALITY  分级报点与现实操作
S06_SH02 4.5s  GAME     近点补枪成功后转右廊
S07_SH01 4.0s  REALITY  账本、欠款与四人资源
S07_SH02 5.0s  REALITY  苏禾条件、第五格与落笔
```

- [ ] **Step 1: 建立分镜头部与字段合同**

文件开头声明 18 个 `SHOT_ID` 是后续资产命名合同；每个镜头按以下顺序填写且不得省略：

```text
SHOT_ID:
DURATION:
LAYER:
LOCATION:
CHARACTERS:
CHARACTER_POSITION:
OBJECTIVE:
TACTICAL_STATE:
WEAPON:
WEAPON_STATE:
CAMERA_SIZE:
CAMERA_ANGLE:
CAMERA_MOVE:
ACTION:
EXPRESSION:
DIALOGUE:
SOUND:
LIGHT:
CONTINUITY_IN:
CONTINUITY_OUT:
UI_SAFE_AREA:
NEGATIVE:
KEYFRAME_ROLE:
EDIT_OUT:
```

- [ ] **Step 2: 写 `S01_SH01`—`S02_SH02` 六个现代镜头**

必须让观众看到“赵雨先打—周野准星已离开—赵雨倒下—周野晚半拍补掉近点—带拆弹器的最后一人完成五秒拆除”的因果链。现代 Major 只使用虚构赛事标识，不生成现实战队、赛事或赞助 Logo。

- [ ] **Step 3: 写 `S03_SH01`—`S03_SH03` 三个异常镜头**

每镜只推进一个异常层级：声音脱离设备、证据无法记录、空间材质替换。`7:5` 和报名表文字在 `UI_SAFE_AREA` 中说明后期位置，不让关键帧模型绘制精确字形。

- [ ] **Step 4: 写 `S04_SH01`—`S04_SH03` 三个白桥到达镜头**

周野位于空间边缘；苏禾在出口与账桌之间，江宁在瞄具侧，唐夏靠训练入口，许安在门、屏幕和记录三者可见处。首次群像不得出现触碰、包围、暧昧凝视或海报式站队。

- [ ] **Step 5: 写 `S05_SH01`—`S06_SH02` 四个试训镜头**

第一轮和第二轮使用相同屏幕方向、近点入口和右廊轴线。第一轮先显示准星离位，再显示唐夏倒下；第二轮周野先说“右廊可能一个，距离不确定。近点先打，我补近点”，完成近点补枪后再说“右廊到门，半秒”，最后短点两枪。

- [ ] **Step 6: 写 `S07_SH01`—`S07_SH02` 两个报名镜头**

第一个镜头让江宁、唐夏、许安各自处理租赁、维修班次和下班时间，避免四人只等待男主；第二个镜头由苏禾说明资格可撤销，周野落笔。最后内心声压缩为“这次，从补枪位重新开始。”，不重复“第一枪，从白桥开始”的标题文字。

- [ ] **Step 7: 验证 18 镜头、字段完整性和 68.5 秒总时长**

Run:

```bash
shots='天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md'
test "$(rg -c '^SHOT_ID:' "$shots")" -eq 18
for field in DURATION LAYER LOCATION CHARACTERS CHARACTER_POSITION OBJECTIVE TACTICAL_STATE WEAPON WEAPON_STATE CAMERA_SIZE CAMERA_ANGLE CAMERA_MOVE ACTION EXPRESSION DIALOGUE SOUND LIGHT CONTINUITY_IN CONTINUITY_OUT UI_SAFE_AREA NEGATIVE KEYFRAME_ROLE EDIT_OUT; do
  test "$(rg -c "^${field}:" "$shots")" -eq 18
done
awk -F': ' '/^DURATION:/{gsub(/s/,"",$2); sum+=$2} END{exit !(sum==68.5)}' "$shots"
test "$(rg '^SHOT_ID:' "$shots" | sort -u | wc -l | tr -d ' ')" -eq 18
rg '^(LOCATION|CHARACTERS|CHARACTER_POSITION|OBJECTIVE|TACTICAL_STATE|WEAPON|WEAPON_STATE|ACTION|EXPRESSION|DIALOGUE|SOUND|LIGHT|KEYFRAME_ROLE|EDIT_OUT):' "$shots" \
  | rg 'TB[D]|TO[D]O|待填[写]|__UNRESOLVE[D]__|谢晚|女版周野|国家队训练院|正式天衡|太监解说' \
  && exit 1 || true
```

Expected: 全部检查成功，最后一条 `rg` 无输出。

- [ ] **Step 8: 提交逐镜头分镜**

```bash
git add -- '天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md'
git commit -m 'docs: add executable chapter 1 sample shots'
```

### Task 3: 写关键帧、H3 运动与声音提示词

**Files:**
- Create: `天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md`
- Read: `天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md`
- Read: `天工枪局：白桥第一枪/skills/tiangong-ancient-character-visual/SKILL.md`
- Read: `天工枪局：白桥第一枪/skills/tiangong-match-visual/SKILL.md`

**Interfaces:**
- Consumes: Task 2 的 18 个稳定 `SHOT_ID`、镜头构图、动作、连续性与声音字段。
- Produces: 每镜一个 `KEYFRAME_PROMPT`、`KEYFRAME_NEGATIVE`、`H3_MODE`、`H3_PROMPT`、`H3_AUDIO_POLICY`、`VOICE_REF`、`SFX_CUES`、`POST_TEXT`。

- [ ] **Step 1: 调用提示词 Skills 并声明静动分离规则**

实现本任务前读取 `gpt-image` 和 `h3-prompt-writing` 的 `SKILL.md`。文件开头明确：

```text
KEYFRAME_PROMPT 只描述关键帧中可见的单一时刻。
H3_PROMPT 只描述该静态事实之后的时间顺序、镜头运动和声音事件。
精确文字只写入 POST_TEXT，不进入 KEYFRAME_PROMPT 或 H3_PROMPT。
VOICE_REF 使用角色 ID，不在本阶段填写尚未创建的 MiniMax Voice ID。
```

- [ ] **Step 2: 写六个现代镜头提示词**

`S01_SH01`—`S02_SH02` 锁定同一周野脸、现代男队友身份、冷蓝比赛灯、虚构赛事标识、真实键鼠与现代 AK 结构。H3 提示按动作先后写出呼吸、鼠标微动、脚步、枪声、拆除和摘耳机，禁止无动机环绕、英雄式慢动作和嘴型乱动。

- [ ] **Step 3: 写三个异常转场提示词**

`S03_SH01`—`S03_SH03` 使用音画错位、屏幕材质变化、奖牌滑落和低沉钟声。H3 运动必须是局部渐变与垂直坠落，不允许传送门光柱、魔法粒子、仙侠能量或身体变形。

- [ ] **Step 4: 写三个白桥到达提示词**

`S04_SH01`—`S04_SH03` 引用人物外观母版，但用当前身份、服装和站位；锁定青砖、漆木、黄铜、黑化钢、旧机柜、灰布修补线材和窄空间。四人只做工作动作与警戒动作。

- [ ] **Step 5: 写四个试训提示词**

`S05_SH01`—`S06_SH02` 对赤漆连珠铳手部接触、震声雷轨迹、近点与右廊轴线、准星方向、弹匣和抛壳做硬锁。`S05_SH02` 和 `S06_SH02` 的机位参数重复书写，不使用“同上”或“参考前镜头”。

- [ ] **Step 6: 写两个报名镜头提示词**

`S07_SH01`—`S07_SH02` 锁定账本、欠款条款版式、四行已填写与第五格空白的安全区，但纸面保持可覆盖的空白或不可读占位，不生成伪汉字。“周野”由后期书写动画合成。

- [ ] **Step 7: 验证提示词数量、ID 集合和禁用内容**

Run:

```bash
shots='天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md'
prompts='天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md'
test "$(rg -c '^SHOT_ID:' "$prompts")" -eq 18
for field in KEYFRAME_PROMPT KEYFRAME_NEGATIVE H3_MODE H3_PROMPT H3_AUDIO_POLICY VOICE_REF SFX_CUES POST_TEXT; do
  test "$(rg -c "^${field}:" "$prompts")" -eq 18
done
diff \
  <(rg '^SHOT_ID:' "$shots" | sed 's/^SHOT_ID: //' | sort) \
  <(rg '^SHOT_ID:' "$prompts" | sed 's/^SHOT_ID: //' | sort)
rg '^(KEYFRAME_PROMPT|H3_PROMPT|H3_AUDIO_POLICY|VOICE_REF|SFX_CUES|POST_TEXT):' "$prompts" \
  | rg '同上|参考前镜头|TB[D]|TO[D]O|待填[写]|__UNRESOLVE[D]__|精确生成.{0,8}(比分|姓名|HUD)|魔法|仙侠|传送门光柱' \
  && exit 1 || true
```

Expected: `diff` 无输出；其他检查成功；最后一条 `rg` 无输出。

- [ ] **Step 8: 提交提示词文件**

```bash
git add -- '天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md'
git commit -m 'docs: add chapter 1 keyframe and H3 prompts'
```

### Task 4: 切换生产入口并删除粗稿

**Files:**
- Modify: `天工枪局：白桥第一枪/分镜/目录说明.md`
- Modify: `.gitignore`
- Delete: `天工枪局：白桥第一枪/分镜/第一章_输掉Major后我从民间赛重新开始_完整分镜.md`
- Delete: `天工枪局：白桥第一枪/分镜/第一章_逐镜头生产分镜.md`
- Read: `天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md`
- Read: `天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md`
- Read: `天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md`

**Interfaces:**
- Consumes: Tasks 1—3 已验证并提交的三份新文件。
- Produces: 唯一生产入口、干净工作树和不再可误读的旧稿路径。

- [ ] **Step 1: 先验证新文件存在再允许删除**

Run:

```bash
for file in \
  '天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md' \
  '天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md' \
  '天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md'; do
  test -s "$file"
done
```

Expected: 三个 `test -s` 全部成功。

- [ ] **Step 2: 更新目录说明**

把当前“正式分镜尚未迁移”的状态改为“70 秒样片分镜已迁移”。生产读取顺序固定为：导演书 → 逐镜头分镜 → 关键帧与视频运动提示词。保留十个核心节拍、层级限制、表演限制和视觉连续性，不再列出尚未存在的旧建议文件名。

- [ ] **Step 3: 忽略视觉伴侣目录**

在根 `.gitignore` 末尾增加：

```gitignore
.superpowers/
```

- [ ] **Step 4: 删除两份粗稿**

使用补丁删除：

```text
天工枪局：白桥第一枪/分镜/第一章_输掉Major后我从民间赛重新开始_完整分镜.md
天工枪局：白桥第一枪/分镜/第一章_逐镜头生产分镜.md
```

- [ ] **Step 5: 验证目录入口和删除范围**

Run:

```bash
test ! -e '天工枪局：白桥第一枪/分镜/第一章_输掉Major后我从民间赛重新开始_完整分镜.md'
test ! -e '天工枪局：白桥第一枪/分镜/第一章_逐镜头生产分镜.md'
test "$(rg -c '第01章_70秒样片' '天工枪局：白桥第一枪/分镜/目录说明.md')" -ge 3
rg -n '第一章_输掉Major后我从民间赛重新开始_完整分镜|第一章_逐镜头生产分镜|正式分镜尚未迁移' '天工枪局：白桥第一枪/分镜/目录说明.md' && exit 1 || true
git diff --check
git status --short
```

Expected: 旧路径不存在；目录至少出现三个新入口；禁用旧文本无输出；`git diff --check` 成功；状态只包含两项删除、目录说明和 `.gitignore` 修改。

- [ ] **Step 6: 提交入口切换**

```bash
git add -- \
  '.gitignore' \
  '天工枪局：白桥第一枪/分镜/目录说明.md' \
  '天工枪局：白桥第一枪/分镜/第一章_输掉Major后我从民间赛重新开始_完整分镜.md' \
  '天工枪局：白桥第一枪/分镜/第一章_逐镜头生产分镜.md'
git commit -m 'docs: replace rough chapter 1 storyboards'
```

### Task 5: 进行终局一致性验证

**Files:**
- Verify: `天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md`
- Verify: `天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md`
- Verify: `天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md`
- Verify: `天工枪局：白桥第一枪/分镜/目录说明.md`
- Verify: `.gitignore`

**Interfaces:**
- Consumes: Tasks 1—4 的所有已提交文件。
- Produces: 可交给 Voice ID、GPT Image、ComfyUI、MiniMax H3 和剪辑计划的稳定分镜合同。

- [ ] **Step 1: 运行结构验证**

Run:

```bash
director='天工枪局：白桥第一枪/分镜/第01章_70秒样片导演书.md'
shots='天工枪局：白桥第一枪/分镜/第01章_70秒样片逐镜头分镜.md'
prompts='天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md'
test "$(rg -c '^SCENE_ID:' "$director")" -eq 7
test "$(rg -c '^SHOT_ID:' "$shots")" -eq 18
test "$(rg -c '^SHOT_ID:' "$prompts")" -eq 18
diff <(rg '^SHOT_ID:' "$shots" | sed 's/^SHOT_ID: //' | sort) <(rg '^SHOT_ID:' "$prompts" | sed 's/^SHOT_ID: //' | sort)
awk -F': ' '/^DURATION:/{gsub(/s/,"",$2); sum+=$2} END{print sum; exit !(sum==68.5)}' "$shots"
```

Expected: 场景数 `7`、两个镜头数均为 `18`、`diff` 无输出、`awk` 打印 `68.5` 并成功退出。

- [ ] **Step 2: 运行正史与视觉禁用项扫描**

Run:

```bash
{
  rg '^(LOCATION|CHARACTERS|TACTICAL_FACT|CAMERA|MOVEMENT|PROP_CONTINUITY|REALITY_RETURN|RESOURCE_STAKE|NEXT_CUT):' "$director"
  rg '^(LOCATION|CHARACTERS|CHARACTER_POSITION|OBJECTIVE|TACTICAL_STATE|WEAPON|WEAPON_STATE|ACTION|EXPRESSION|DIALOGUE|SOUND|LIGHT|KEYFRAME_ROLE|EDIT_OUT):' "$shots"
  rg '^(KEYFRAME_PROMPT|H3_PROMPT|H3_AUDIO_POLICY|VOICE_REF|SFX_CUES|POST_TEXT):' "$prompts"
} | rg '谢晚|女性周野|女版周野|国家队训练院|正式天衡检测|系统外挂|火绳枪|法器|Windows 桌面|太监解说' \
  && exit 1 || true
```

Expected: 无输出。

- [ ] **Step 3: 人工逐镜检查六个高风险点**

按顺序确认：

1. `S01_SH02`—`S01_SH04` 的守包与五秒拆除因果正确；
2. `S03_SH01`—`S03_SH03` 没有魔法化穿越；
3. `S04_SH01` 明确同一男性身体、队服、护带和奖牌；
4. `S04_SH02` 四人有独立工作站位且保持安全距离；
5. `S05_SH02` 与 `S06_SH02` 轴线相同、选择不同；
6. `S07_SH01`—`S07_SH02` 由苏禾拍板，四人现实账回场，试报名可撤销。

Expected: 六项全部满足；任一失败只修改对应镜头和同 ID 提示词。

- [ ] **Step 4: 检查提交和工作树**

Run:

```bash
git diff --check origin/main..HEAD
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: `git diff --check` 成功；工作树干净；日志包含设计规格提交以及 Tasks 1—4 的四个实现提交。

- [ ] **Step 5: 仅在修复验证问题时提交终局修订**

若 Step 1—4 发现并修复问题：

```bash
git add -- '.gitignore' '天工枪局：白桥第一枪/分镜' '天工枪局：白桥第一枪/docs/superpowers/specs/2026-08-11-ch01-cinematic-sample-storyboard-rebuild-design.md'
git commit -m 'docs: finalize chapter 1 storyboard contract'
```

若没有修复，不创建空提交。

## Deferred Follow-up Plans

本计划验收后，按顺序创建并执行三份独立计划：

1. 五名角色原创 MiniMax Voice ID、试听、固定参数与声音清单；
2. 18 张 GPT Image 关键帧、ComfyUI 修复、角色/枪械/场景一致性验收；
3. 18 个 MiniMax H3 镜头、分轨声音、字幕/UI、剪辑与 1080p 完整声音样片。
