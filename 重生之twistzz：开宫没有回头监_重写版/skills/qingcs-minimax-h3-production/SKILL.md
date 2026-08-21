---
name: qingcs-minimax-h3-production
description: 将《穿越大清打CS，我成了女队首发》的正文、人物、场景与十格分镜编译为可验证、可预览、可按单格付费执行的 MiniMax-H3 JSON 和官方 MMX 命令。
---

# QingCS MiniMax-H3 Production Skill

## 1. 必须先读取

按顺序读取：

1. `00_重写版状态.md`
2. `README.md`
3. `分镜/目录说明.md`
4. 当前章节正文
5. 当前章节十格分镜；第 1 章额外读取导演书
6. `人物档案/00_人物档案总表.md`
7. 当前人物个人档案与 `人物档案/23_全员外貌性格与古风发式深化.md`
8. `设定/06_大清战队宫廷电竞基地总览与宫殿索引.md`
9. `AI生产/H3生产包/assets/characters.json`
10. `AI生产/H3生产包/assets/scenes.json`
11. `AI生产/H3生产包/config/qingcs-h3-manifest.json`

同时遵守现有 Skill：

- `qingcs-human-first-novel-review`
- `qingcs-novel-production`
- `qingcs-cinematic-director`
- `qingcs-cinematic-storyboard`
- `qingcs-ancient-character-visual`
- `qingcs-mingqing-match-visual`

## 2. 生产边界

- 1—44 章已有正文和十格分镜，可编译。
- 45—56 章只有总纲，不得生成伪装成正式镜头的付费 H3 任务。
- 生成 JSON 是技术编译，不等于章节完成独立复审或最终签发。
- 不改写人数、比分、地图、席位、队籍、合同、权限、角色性别和时间线。

## 3. 提示结构

每格必须包含：

```text
输出规格
全局视觉锁定
人物参考图映射
场景视觉与连续性锁
总段 00:00—00:15
分拍 00:00—00:03 / 00:03—00:10 / 00:10—00:15
地点、空间锚点与调度
对白、声音与说话人
可核验比赛/制度事实
终态锁定
后期文字策略
负面约束
```

第 1 章已有 `SCENE/ACTION/CAMERA/BLOCKING/PERFORMANCE/AUDIO/TRANSITION/CONTINUITY/NEGATIVE` 时原样保留，不再用模板覆盖。

## 4. H3 模式

- 必须显式使用 `MiniMax-H3`。
- 时长为整数 4—15 秒；本项目默认 15 秒。
- 画幅默认 16:9。
- 无参考资产：`t2va`。
- 人物三视图参考：`ref2va`。
- 首帧：`i2va`；首尾帧：`fl2va`；仅尾帧：`l2va`。
- 帧输入与 reference image/video/audio 互斥。
- 最多 9 张参考图、3 个参考视频、3 个参考音频、12 个混合参考；音频参考必须同时有图像或视频。
- 提示不超过 7000 字符。

## 5. 角色引用

只调用 `characters.json` 中已有 `reference_image` 的验收图。三视图只锁身份、脸型、发式和服装层级；提示必须写明不复制白底、多视角排版、文字、空手站姿或额外分身。

第 1 章第 1—8 格的主角仍是现代成年男性局部/侧影，不得提前引用贼贼姐女性三视图；从第 9 格身体确认后才引用 `CHAR_ZEIZEI`。

## 6. 场景引用

场景概念板默认不作为 reference image，只调用 `scenes.json` 的文本锁。每格最多匹配两个稳定场景，避免同一 15 秒跨多个地点。

## 7. 精确文字

比分、姓名、HUD、名册、合同、印章、门禁记录、直播标题和弹幕全部后期合成。H3 画面只生成载体、版面和安全区。对白是声音例外，必须逐字保留原分镜，不扩写。

## 8. 免费编译与付费执行

免费编译：

```bash
python AI生产/H3生产包/tools/compile_storyboards.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json
```

免费命令预览：

```bash
python AI生产/H3生产包/tools/run_h3_batch.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1 --grid 9
```

付费执行必须显式 `--execute`，且只选一个章节并指定格或 `--all-grids`。执行前通过 `mmx auth status --output json --quiet` 检查脱敏认证；H3 只接受 Pay-as-you-go/Credit API key。禁止把密钥写入仓库或打印到命令中。

## 9. 失败策略

- 任务失败立即停止；不自动重试。
- 输出 MP4 已存在则跳过。
- 只重做失败格，不用下一格掩盖错误。
- 先修分镜事实，再重新编译；不得手改 generated JSON 形成第二事实源。

## 10. 完成检查

```text
[ ] 当前章节正文与分镜一致
[ ] 恰好十格，每格一个因果节拍
[ ] 三拍时间线完整
[ ] 人物参考图与出镜时间正确
[ ] 场景 ID、轴线、入口和物件连续
[ ] 比赛/制度事实可核验
[ ] 精确文字已移到后期
[ ] H3 mode、时长、画幅和参考上限通过校验
[ ] 免费命令预览无误
[ ] 只有得到明确付费范围后才执行
```
