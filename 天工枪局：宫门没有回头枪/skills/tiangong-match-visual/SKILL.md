---
name: tiangong-match-visual
description: Use when producing 天工枪局 tactical maps, modern firearms with Qing-industrial materials, utilities, armed match avatars, observer UI, eunuch commentator visuals, or match keyframes.
---

# 天工枪局比赛视觉生产

## 三层系统

1. `REAL_STAGE`：选手、键鼠、耳机、宫廷赛台、裁判和现实后果；
2. `GAME_BATTLEFIELD`：权契图、战斗化身、枪械、道具和交火；
3. `OBSERVER_INFO`：OB、UI、回放、太监解说和公众版本。

一次资产只选择一个主层和一个主资产类型。

## 资产类型

- `MAP`：地图总览、甲点、乙点、中路；
- `WPN`：基础枪械型号；
- `UTL`：烟雾罐、震声雷、火油瓶、破片瓷雷、震城匣、拆械匣；
- `AVT`：比赛化身和持械动作；
- `OBS`：UI、沙盘、经济、回放；
- `CAST`：太监解说和观察者台；
- `KF`：三层切换关键帧。

## 性别与身份

- 周烬：成年男性，必须引用新批准男性母版；
- 在男性母版通过前，不生成可辨识正脸的持枪海报；
- 谢照夜和其他职业选手为成年女性；
- 不能把周烬换成谢照夜外观；
- 不用“唯一男性”构图制造女性围观、崇拜和后宫感；
- 比赛群像按位置、枪线和任务站位。

## 地图流程

先填写：

```text
MAP_ID:
REAL_RIGHT:
ATTACK_SPAWN:
DEFENSE_SPAWN:
SITE_JIA:
SITE_YI:
MID:
LONG_SIGHTLINE:
CLOSE_CONTEST:
PRIMARY_ROTATION:
RISKY_FLANK:
SMOKE_CUTS:
FLASH_ENTRIES:
FIRE_DENIAL:
HEIGHT_AND_SOUND:
```

顺序：

1. 斜俯视战术总览；
2. 甲点；
3. 乙点；
4. 中路；
5. 俯视沙盘；
6. 道具空间；
7. 正式灯光。

地图必须可打，不是纯古建筑风景。

## 枪械流程

先锁现代功能轮廓：

```text
WEAPON_ID:
FUNCTION_CLASS:
BARREL:
RECEIVER:
MAGAZINE:
STOCK:
SIGHT:
ACTION_OR_BOLT:
GRIP_POINTS:
RELOAD_PATH:
EJECTION:
```

再加入乌木、黄铜、牛皮、漆器、景泰蓝和少量鎏金。装饰不能妨碍握持、散热、拆卸、换弹和抛壳。

禁止火绳枪、燧发枪、弓弩、仙侠法器、巨大龙头、满枪珠宝和蒸汽朋克管线。

## 战斗化身

比赛化身引用身份母版，并改成：

- 收紧袖口；
- 短下摆；
- 防滑鞋；
- 功能腰带；
- 弹匣和道具固定；
- 原创旗色、补服、腰牌和轻甲纹样。

母版空手，化身可持械。两类资产不能混在一张标准板中。

## 周烬比赛化身

- 成年男性；
- 不改变脸、体态和性别；
- 初期可穿无品牌现代队服进入测试图；
- 取得大曜临时训练服后再建立正式化身；
- 职业动作是跟随第一接触、急停补枪和残局处理；
- 不做单人帝王、无双战神或女性群体中心。

## 观察者与太监解说

岗位：

- 唱局监：事实、人数、时间和目标；
- 评策监：经济、道具、站位和代价；
- 掌镜监：切镜；
- 录局监：证据索引。

太监形象为成年男性专业从业者，使用收袖工作袍、耳机、麦克风和真实观察者设备。禁止尖嗓脸、娘化、猥琐、跪地谄媚、拂尘当麦克风和身体笑话。

## UI

视觉语言：

- 军令牌比分；
- 竹筹经济；
- 兵部文书装备；
- 沙盘小地图；
- 火漆回放标记。

精确文字、数字和姓名后期合成。图像生成只留 `UI_SAFE_AREA`。

## 正式任务字段

```text
ASSET_ID:
ASSET_TYPE:
PURPOSE:
LAYER:
CANON_INPUT:
CHARACTER_REFERENCE:
MAP_REFERENCE:
WEAPON_REFERENCE:
TACTICAL_FUNCTION:
COMPOSITION:
ACTION_START:
PRIMARY_ACTION:
ACTION_END:
CAMERA:
LIGHT_AND_COLOR:
OBSERVER_VIEW:
COMMENTATOR_ROLE:
UI_SAFE_AREA:
CONTINUITY:
NEGATIVE:
QC_PASS:
```

## 失败诊断

- 地图看不懂 → 回到甲/乙/中路和回防；
- 武器结构错 → 删除装饰，先锁机械；
- 周烬女性化 → 停止并重建男性母版；
- 女性角色工具化 → 重做职业站位和独立动作；
- UI 像外挂 → 移出游戏世界；
- 解说像宫廷小品 → 重写专业岗位；
- 文字乱码 → 后期合成；
- 动作坍塌 → 一帧只保留一个主动作；
- 高光无代价 → 加现实赛台或权契后果关键帧。
