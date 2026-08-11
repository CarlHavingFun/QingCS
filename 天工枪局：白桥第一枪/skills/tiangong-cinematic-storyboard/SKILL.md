---
name: tiangong-cinematic-storyboard
description: 为《天工枪局：白桥第一枪》生成连续、可拍、可生图的漫剧分镜和关键帧提示。
---

# 天工枪局分镜 Skill

## 1. 分镜目标

每个镜头只完成一个主要节拍。优先让观众看懂：

- 谁在操作；
- 谁在游戏内行动；
- 当前人数、位置和目标；
- 哪条信息改变选择；
- 比赛结果如何回到现实。

## 2. 角色 ID

```text
ZHOU_YE      周野，男性，唯一穿越者
SU_HE        苏禾，白桥 IGL
JIANG_NING   江宁，主狙
TANG_XIA     唐夏，首接触
XU_AN        许安，晚段信息
JI_QIU       纪秋，地图工程师/教练
XIA_MAN      夏满，学徒替补
```

禁止使用谢晚或同名女性现代队友 ID。

## 3. 场景 ID

```text
MODERN_MAJOR_STAGE
MODERN_REVIEW_ROOM
WHITE_BRIDGE_SERVER_ROOM
WHITE_BRIDGE_MAIN_HALL
WHITE_BRIDGE_TRAINING_ROOM
SOUTH_CITY_REGISTRATION_DESK
MAP_WHITE_BRIDGE_WAREHOUSE
MAP_SOUTH_CITY_GUILD
```

第一章不使用国家队训练院、宫城比赛殿或正式天衡检测室。

## 4. 分镜字段

```text
SHOT_ID:
DURATION:
LAYER: REALITY / GAME / OBSERVER
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
```

## 5. 十格结构建议

第一章可拆为：

1. Major 四打三；
2. 周野准星离开补枪位；
3. 五秒拆除与亚军；
4. 休息室事实复盘；
5. `7:5` 与木框转场；
6. 白桥设备间醒来；
7. 监控断帧与临时客籍；
8. 赤漆连珠铳第一次试射失败；
9. 第二轮及时报点并补枪；
10. 报名表写下周野。

每格内部可再拆 2—4 个镜头。

## 6. 战斗分镜

### 现实动作

鼠标移动、键盘输入、呼吸、报点和屏幕反馈必须有先后。

### 游戏动作

- 入口角色先获得烟闪条件；
- 补枪角色保持可见距离；
- 脚步信息有空间来源；
- 准星转移与死亡结果对应；
- 不把击杀栏当作唯一叙事。

### 对照镜头

第一轮失败：周野听见右廊，准星离开唐夏近点补枪位。

第二轮成功：周野先报告右廊不确定信息，准星留在近点，完成补枪后再转右廊。

## 7. 观察者和太监解说

- 白桥私训：无太监解说，只有输入记录和简单回放；
- 南城公开赛：地方观察者和基础解说；
- 城区以后：唱局监、评策监、掌镜监、录局监逐步进入；
- 解说不能传回选手席。

## 8. 关键帧提示规则

每张关键帧要锁定：

- 人物身份和服装层级；
- 白桥民间材质，不画国家队礼制；
- 枪械机械结构；
- 手部与武器接触；
- 镜头方向；
- 屏幕文字后期合成；
- 不生成多余人物或错误性别。

## 9. 失败诊断

- 看不懂比赛：补人数、目标和位置建立镜头；
- 人物像宣传照：加入工作动作、设备和空间阻力；
- 白桥过于豪华：增加旧设备、修补线材、租用器材和窄空间；
- 周野像救世主：把苏禾拍板、江宁资源、唐夏入口和许安信息补回；
- 游戏像古代火器战：恢复现代机匣、弹匣、瞄具和 UI。
