---
name: tiangong-cinematic-storyboard
description: 为《天工枪局：白桥第一枪》生成连续、可拍、可生图的 70 秒漫剧分镜，固定 8 段、16 镜和穿越后优先结构。
---

# 天工枪局分镜 Skill

## 1. 结构硬锁

```text
8 段场景
16 个镜头
70 秒
穿越前 8 秒
穿越后 62 秒
```

正式 `SHOT_ID` 为 `S01_SH01` 至 `S08_SH02`。不新增另一套版本化 ID。

## 2. 分镜目标

每个镜头只完成一个主要节拍，并让观众看懂：

- 谁在操作；
- 当前现实或游戏层；
- 哪条信息改变选择；
- 准星和动作如何产生结果；
- 比赛结果如何回到现实代价。

## 3. 角色 ID

```text
ZHOU_YE      周野，男性，唯一穿越者
SU_HE        苏禾，白桥 IGL 与经营者
JIANG_NING   江宁，主狙与瞄具维修
TANG_XIA     唐夏，首接触与火器维修
XU_AN        许安，晚段信息与记录
```

## 4. 场景 ID

```text
MODERN_MAJOR_EVIDENCE
MODERN_ANOMALY_ROOM
WHITE_BRIDGE_SERVER_ROOM
WHITE_BRIDGE_MAIN_HALL
WHITE_BRIDGE_REGISTRATION_DESK
WHITE_BRIDGE_TRAINING_ROOM
MAP_WHITE_BRIDGE_WAREHOUSE
WHITE_BRIDGE_RAIN_EXTERIOR
```

第一章不使用国家队训练院、宫城比赛殿或正式天衡检测室。

## 5. 分镜字段

```text
SHOT_ID:
TIME_RANGE:
DURATION:
LAYER:
LOCATION:
CHARACTERS:
CHARACTER_POSITION:
OBJECTIVE:
TACTICAL_STATE:
CAMERA_SIZE:
CAMERA_ANGLE:
CAMERA_MOVE:
ACTION:
DIALOGUE:
SOUND:
LIGHT:
CONTINUITY_IN:
CONTINUITY_OUT:
POST_TEXT:
NEGATIVE:
```

## 6. 16 镜分配

```text
S01 2 镜：准星离位；拆包与奖牌
S02 1 镜：7:5、断电仍响、木框与坠落
S03 3 镜：奖牌落地；四人分工；确认男性身体
S04 2 镜：异常记录；枪馆完整显现
S05 2 镜：欠款与第五格；七日客籍和断网试训
S06 2 镜：错误投掷；准星离位和失败
S07 2 镜：分级报点；近点补枪后转右廊
S08 2 镜：七日担保与落笔；雨夜白桥
```

## 7. 战斗分镜

- 投掷物有拿出、动作、碰撞、爆开和作用；
- 入口角色先获得条件；
- 补枪角色保持可见距离；
- 脚步有明确空间来源；
- 准星转移必须早于死亡结果；
- 同构失败/成功镜头不得翻转左右关系；
- 观察者信息只验证，不替代战术叙事。

## 8. 关键帧规则

每张关键帧锁定：

- 人物正式三视图；
- 场景正式效果图；
- 服装层级；
- 手部与设备/枪械接触；
- 镜头方向和人物左右；
- 后期文字安全区；
- 不出现额外人物、错误性别和历史角色。

## 9. H3 连续性

一个片段 4—15 秒。多参考镜头必须使用连续时间轴：

```text
初始状态
→ 准备动作
→ 核心动作
→ 收束与锁定末状态
```

上一镜末状态必须等于下一镜初始状态，包括人物位置、视线、双手、道具归属、枪械状态和摄影机轴线。

## 10. 失败诊断

- 现代段过长：继续压缩，只留因果证据；
- 白桥过于豪华：增加旧设备、修补线材、窄空间和账本；
- 人物像宣传照：加入工作动作、距离和空间阻力；
- 周野像救世主：补回苏禾拍板、江宁资源、唐夏入口、许安记录；
- 战斗看不懂：先补条件和准星，再给死亡结果；
- 文件越来越多：直接替换正式文件，不新建带后缀版本。
