---
name: tiangong-cinematic-storyboard
description: Use when turning 《天工枪局》 chapters or director books into executable shot lists, ten-unit storyboards, keyframes, animatics, image/video prompts, and continuity QC.
---

# 《天工枪局》分镜、关键帧与预演

## 1. 交付物

每章固定生产：

1. `分镜/第NN章_导演书与镜头表.md`；
2. `分镜/第NN章_十格分镜.md`。

十格是默认漫剧生产结构，每格约十五秒。十五秒是剪辑/生成单元，不等于一个电影长镜头；一格可拆 1—4 个短镜头，但只能完成一个主要叙事节拍。

## 2. 输入顺序

`正式正文 → 人物与设定 → tiangong-cinematic-director 导演书 → 关键帧计划 → 十格分镜 → animatic → 视频提示 → QC`

不得绕过导演书直接堆镜头参数。

## 3. 每格必须回答

```text
BEAT:
AUDIENCE_QUESTION_BEFORE:
AUDIENCE_UPDATE:
PRIMARY_ACTION:
END_STATE:
DURATION:
```

如果一格同时承担穿越、认人、解释世界、建立枪械和推进赛务，应拆分。

## 4. 镜头字段

```text
SHOT_ID:
TIME:
STORY_FUNCTION:
LAYER: REAL_STAGE / GAME_BATTLEFIELD / OBSERVER / NON_MATCH_REALITY
SHOT_SIZE_AND_LENS:
CAMERA_ANGLE:
BLOCKING_START:
VISIBLE_STIMULUS:
PRIMARY_ACTION:
ACTION_END:
EYE_LINE:
PROP_STATE:
LIGHT:
AUDIO:
TRANSITION:
CONTINUITY:
GENERATION_RISK:
```

动作必须写到终点，例如“她后退到桌沿抵住腰并停”，不能只写“她后退”。

## 5. 比赛附加字段

```text
MAP_ID:
MAP_POSITION:
SCREEN_DIRECTION:
ROSTER_ALIVE:
TIME_LEFT:
ECONOMY:
UTILITY:
AVATAR_ID:
WEAPON_ID:
WEAPON_STATE:
BOMB_STATE:
PRIMARY_TACTICAL_ACTION:
OBSERVER_VIEW:
COMMENTATOR_ROLE:
KNOWN_INFO:
LINE_FUNCTION:
AUDIO_PRIORITY:
UI_SAFE_AREA:
REALITY_CONSEQUENCE:
```

### 层级规则

- `REAL_STAGE`：现实输入、队内语音与身体反应；
- `GAME_BATTLEFIELD`：战斗化身和游戏地理；
- `OBSERVER`：直播、沙盘、回放和太监解说；
- `NON_MATCH_REALITY`：宫门、工坊、票号、家族与赛务。

三层比赛画面逐镜切换，不在一张关键帧中混成选手可见全息世界。

## 6. 走位与轴线

每个有人物的镜头先写：

`起点 → 看到什么 → 动作 → 终点 → 看向哪里 → 道具在哪只手`

再决定相机。

- 空间首次出现先给主镜头；
- 180 度轴线和屏幕方向保持稳定；
- 有意越轴必须通过中性机位或可见移动；
- 对话先保留听者反应；
- 多人群像不能靠随机站位生成，必须锁定平面图。

## 7. 身份连续性

每章建立引用包：

```text
CHARACTER_ID:
FACE_REFERENCE:
HAIR_REFERENCE:
BODY_REFERENCE:
IDENTITY_COSTUME:
MATCH_AVATAR_COSTUME:
FIXED_PROPS:
FORBIDDEN_CHANGES:
```

- 身份母版严格空手；
- 比赛化身才允许持指定枪械；
- 周烬/谢照夜使用同一张外在脸，不能跨镜变回现代男性脸；
- 内在周烬通过操作、目光、镜子、声音和不熟悉身体的动作表达；
- 新图不得复现历史源旧胸牌、称号和队标。

## 8. 武器与动作连续性

固定：

- 枪械基础型号；
- 护木、编号片和枪带；
- 弹匣当前状态；
- 枪口方向；
- 手指是否离开扳机；
- 开火、拉栓、换弹、投掷和拾枪的动作阶段。

复杂动作拆镜：

- AWP/望山重狙开火与拉栓分开；
- 换弹拆为弹匣脱离、插入和复位；
- 投掷拆为拉环、预备、出手和落点；
- 不能一镜同时开火、转身、换弹、跳跃和说长台词。

## 9. 太监解说分镜

每句解说写：

```text
COMMENTATOR_ROLE: 唱局监 / 评策监 / 掌镜监 / 录局监
KNOWN_INFO:
FORBIDDEN_INFO:
LINE_FUNCTION: 报事实 / 解释因果 / 修正判断 / 转场 / 公众版本
OBSERVER_VIEW:
AUDIO_PRIORITY:
END_STATE:
```

- 唱局先报发生了什么；
- 评策再说为什么重要；
- 回放阶段才修正证据；
- 枪声、脚步、队内语音和拆械声优先；
- 解说席口型风险高时使用侧背影、画外音、监听灯和手部；
- 禁止尖嗓、娘化、身体笑话和谄媚表演。

## 10. 文字与 UI

生成画面只保留：

- 军令牌/竹筹/火漆/文书/沙盘的空白版式；
- A/B 或甲乙阵短标签安全区；
- 比分、兵筹、姓名、字幕、时间和击杀栏的后期区域。

精确文字全部后期合成。模型出现乱码时，不继续重抽长文字，直接清空。

## 11. 关键帧策略

### 必须先做关键帧

- 五人赛台、固定站位和群像；
- 镜中谢照夜、奖牌和门禁牌；
- 现代休息室到大曜训练院的匹配转场；
- 地图斜俯视总览、甲乙阵和轮转；
- 枪械特写与精确手部；
- 太监解说双人台和观察者控制台；
- 首尾状态差异大的动作。

### 首尾帧

转身、门开合、跌落、从现实屏幕进入游戏战场、烟雾扩散和回放叠化优先准备起始/结束关键帧，不让模型自由猜终点。

## 12. 图生视频提示

起始图已经包含静态信息时，只描述变化：

```text
ACTION:
CAMERA_MOVEMENT:
PERFORMANCE_CHANGE:
ENVIRONMENT_MOVEMENT:
AUDIO_CUE:
END_STATE:
CONTINUITY_LOCK:
NEGATIVE:
```

不要重复整张图的所有服装、建筑和武器说明。短提示优于同义形容词堆砌。

## 13. 第一章十格建议

1. 场馆、奖杯与十六比十八；
2. 四打三守包和脚步信息；
3. 准星偏开、五秒拆除与亚军；
4. 休息室事实复盘；
5. 独处回放、旧语音与 `7:5`；
6. 时间倒退、手机黑屏、木框转场；
7. 大曜训练院醒来、正常医疗与陌生手；
8. 镜子、女声、奖牌与谢照夜身份；
9. 名册、赤漆连珠铳和现代 AK 类比；
10. 三日前复核申请、东掖访问权与三天倒计时。

每格仍需从正式正文和导演书重新确认，不把本建议当不可修改的镜头模板。

## 14. 失败诊断

- **一格过载**：拆成两个节拍；
- **人物漂移**：加强外观母版与服装引用；
- **空间混乱**：补主镜头和平面图；
- **层级混乱**：重标 LAYER；
- **枪械变形**：锁型号并拆动作；
- **解说全知**：写合法信息来源；
- **文字乱码**：后期合成；
- **宫廷贴皮**：让门禁、设备、赛务和空间功能真实工作；
- **高光无后果**：增加现实切回和三本账更新。

## 15. 十格输出模板

```text
## 第N格｜00:00—00:15
- 节拍/观众更新：
- 主要层级：
- 镜头拆分：
  - N.1 时长｜功能｜层｜景别/焦段｜起点→动作→终点｜相机｜声音｜转场
- 表演变化：
- 比赛事实（如适用）：
- 连续性锚点：
- 关键帧：
- 视频提示：
- 后期文字：
- QC风险：
```

## 16. 交付检查

- 十格是否覆盖完整章节而非只挑高光；
- 每格是否只有一个主要节拍；
- 人物走位、视线、轴线和道具是否清楚；
- 三层比赛是否分开且切换有动机；
- 枪械与动作是否可生成；
- 太监解说是否专业且合法；
- 精确文字是否留后期；
- 结尾是否保留正文的具体行动和限制；
- 是否无旧称号、现实队标和历史人物影射。