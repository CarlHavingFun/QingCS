---
name: tiangong-minimax-visual-production
description: 使用 MiniMax 为《天工枪局：白桥第一枪》生产人物、场景、关键帧和 H3 视频，强制执行正式资产引用、穿越后视觉优先与无中间版本文件规则。
---

# 天工枪局 MiniMax 视觉生产 Skill

## 1. 使用范围

用于：

- 人物三视图和身份关键帧；
- 白桥设备间、枪馆、货栈、登记桌和雨夜外景；
- 第一章关键帧；
- MiniMax-H3 视频片段；
- 视觉一致性检查。

通用命令先读取：

- `../minimax-multimodal-toolkit/SKILL.md`
- `../minimax-h3-video/SKILL.md`

## 2. 正式资产唯一入口

人物：

```text
视觉资产/人物三视图/00_周野.jpg
视觉资产/人物三视图/01_苏禾.jpg
视觉资产/人物三视图/02_江宁.jpg
视觉资产/人物三视图/03_唐夏.jpg
视觉资产/人物三视图/04_许安.jpg
```

场景：

```text
视觉资产/场景效果图/01_白桥设备间.jpg
视觉资产/场景效果图/02_白桥枪馆主厅.jpg
视觉资产/场景效果图/03_第一次试训失败.jpg
视觉资产/场景效果图/04_第二次试训成功.jpg
视觉资产/场景效果图/05_临时客籍登记桌.jpg
视觉资产/场景效果图/06_雨夜白桥.jpg
```

禁止引用旧母版、历史场景、废稿、rejected、raw、qa 抽帧或 Git 历史图片作为正式输入。

## 3. 生产顺序

```text
正式人物三视图
→ 正式场景效果图
→ 单镜头合成关键帧
→ 关键帧验收
→ H3 视频
→ 后期文字与声音
```

每次只处理一个 `CURRENT_ASSET`。未通过前不生成下一项。

## 4. 第一章节奏硬锁

```text
穿越前：8 秒
穿越后：62 秒
总时长：70 秒
```

现代段只允许：

- “你跟着补”；
- 第二脚步；
- 准星离位；
- 拆包和亚军奖牌；
- 7:5、木框化和坠落。

不得恢复完整比赛、独立团队复盘、长颁奖或现代队友群像资产。

## 5. 人物一致性

### 周野

- 二十四岁中国男性；
- 自己的身体；
- 短黑发、男性骨相；
- 现代深色队服；
- 右腕黑色护带；
- 亚军奖牌跨界；
- 不使用现实职业选手完整肖像。

### 白桥四人

- 苏禾：经营者、IGL、权限与账本；
- 江宁：主狙、瞄具维修与装备资源；
- 唐夏：首接触、入口条件与补枪；
- 许安：记录、置信度和晚段信息；
- 四人必须独立，不得同脸、同身高、同发型或同表情；
- 不生成围住周野、暧昧接触或后宫海报。

## 6. 白桥空间硬锁

必须包含：

- 南城窄长店面；
- 青砖、深漆木、黑化钢、黄铜走线槽；
- 旧普通终端；
- 修补线材和磨损桌面；
- 机柜风扇、桥板雨声与货船；
- 小额经营压力。

禁止：

- 豪华宫廷电竞殿；
- 国家队训练院；
- 仙侠法器；
- 蒸汽朋克管线；
- 赛博霓虹基地；
- 无使用痕迹的样板间。

## 7. 图片命令

```bash
mmx image generate \
  --prompt "$(cat prompt.txt)" \
  --aspect-ratio 16:9 \
  --n 1 \
  --out-dir ./output \
  --out-prefix "$CURRENT_ASSET" \
  --non-interactive \
  --quiet
```

角色引用示例：

```bash
mmx image generate \
  --prompt "$(cat prompt.txt)" \
  --subject-ref type=character,image="视觉资产/人物三视图/00_周野.jpg" \
  --aspect-ratio 16:9 \
  --out-dir ./output \
  --out-prefix "$CURRENT_ASSET" \
  --non-interactive \
  --quiet
```

## 8. H3 命令

已通过首帧后：

```bash
mmx video generate \
  --model MiniMax-H3 \
  --prompt "$(cat video-prompt.txt)" \
  --image "$KEYFRAME" \
  --duration "$DURATION" \
  --ratio 16:9 \
  --download "$OUTPUT_MP4" \
  --poll-interval 10 \
  --timeout 1800 \
  --non-interactive
```

规则：

- H3 使用 Pay-as-you-go/Credit API key；
- 先运行 `mmx auth status --output json --quiet`，只查看掩码状态；
- 命令中不出现字面 API key；
- 首帧模式和参考模式不可混用；
- 已返回 task ID 后绝不因等待、轮询或下载中断而重提任务；
- 下载失败只重试同一结果下载，不重新生成。

## 9. 文件规则

- 正式文件名不追加 `v2`、`重构版`、`重点版` 或 `最终版`；
- 修改时直接替换正式路径，版本追溯交给 Git；
- 不在正史目录保留 `raw/`、`rejected/`、`qa/`、抽帧、临时语音种子和测试视频；
- MiniMax 密钥、`~/.mmx`、`.env` 和凭证文件禁止提交。

## 10. 验收

生成后按 `审核/验收基准.md` 检查。任何以下错误都不得进入正式目录：

- 周野性别或脸型漂移；
- 四名队友身份混淆；
- 白桥过于豪华；
- 现代队友在大曜出现；
- 枪械变成火绳枪或法器；
- 第一遍与第二遍机位和因果不对应；
- 图片承担错误可读文字；
- 穿越前超过 8 秒。
