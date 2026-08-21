# QingCS MiniMax-H3 漫剧生产包

本目录把《穿越大清打CS，我成了女队首发》现有 1—44 章十格分镜编译为本地 MiniMax-H3 可执行任务。它不建立第二套剧情事实源：章节事实仍来自 `正文/`，人物与制度来自 `人物档案/`、`设定/`，镜头事实来自 `分镜/第NN章_十格分镜.md`。

## 交付边界

- 第 1—44 章：manifest 已登记，运行时可编译为 44 份章节 JSON、共 440 个十五秒任务。
- 第 1 章：优先保留原分镜中已经写好的导演级 `SCENE/ACTION/CAMERA/...` H3 提示。
- 第 2—44 章：从“景别/地点、三拍动作、台词或音效、CS 信息、关系/笑点、空间锚点”编译成 H3 双层时间线。
- 第 45—56 章：目前只有篇章总纲，标记为 `outline_only_not_executable`；不伪造可付费执行的镜头。
- 当前分镜审核状态保持原登记：1—16 章为返修后待独立复审；17—44 章为初稿待独立复审。生成 JSON 不等于内容签发。

## 文件结构

```text
AI生产/H3生产包/
├─ assets/
│  ├─ characters.json       # 22 人稳定 ID、外形/表演锁、已验收三视图
│  └─ scenes.json           # 现实层、宫廷功能空间、比赛地图的视觉/连续性锁
├─ config/
│  └─ qingcs-h3-manifest.json  # 44 章直接生产入口
├─ schema/
│  └─ qingcs-h3-batch.schema.json
├─ tools/
│  ├─ common.py             # 常量与统一校验异常
│  ├─ storyboard.py         # 两种十格分镜格式解析
│  ├─ references.py         # 人物/场景匹配与文本锁
│  ├─ h3_jobs.py            # H3 提示、模式校验与 MMX 命令映射
│  ├─ manifest.py           # 44章 manifest 编译与便携 JSON
│  ├─ h3_pipeline.py        # 稳定兼容入口
│  ├─ compile_storyboards.py
│  └─ run_h3_batch.py
├─ tests/
├─ generated/               # 本地生成的 chNN.h3.json；默认不提交
├─ output/                  # H3 输出视频；不提交
└─ state/                   # 本地运行状态；不提交
```

## 安装与认证

官方 CLI 当前使用：

```bash
npm install -g mmx-cli
mmx auth login
mmx auth status --output json --quiet
```

H3 付费请求必须使用 Pay-as-you-go/Credit API key。密钥只保存在本机 MMX 配置；不要写入 manifest、命令历史、提交或聊天。仓库脚本在首个付费任务前只读取脱敏认证状态，并拒绝 OAuth 模式。

## 1. 免费编译 44 章 JSON

在本小说目录运行：

```bash
python AI生产/H3生产包/tools/compile_storyboards.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json
```

输出：

```text
AI生产/H3生产包/generated/index.json
AI生产/H3生产包/generated/ch01.h3.json
...
AI生产/H3生产包/generated/ch44.h3.json
```

每个章节 JSON 含 10 个任务，字段包括稳定 `job_id`、H3 模式、15 秒提示、人物参考图、场景 ID、输出路径和后期文字策略。

只编译一章：

```bash
python AI生产/H3生产包/tools/compile_storyboards.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1
```

## 2. 免费预览正式 MMX 命令

默认不提交付费任务，只打印命令：

```bash
python AI生产/H3生产包/tools/run_h3_batch.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1 --grid 9
```

这一步用于检查提示、参考图、输出路径和参数。命令固定显式指定 `--model MiniMax-H3`、`--duration 15`、`--ratio 16:9`，不使用 `--async`，便于失败时立即停止。

## 3. 明确执行一个付费任务

```bash
python AI生产/H3生产包/tools/run_h3_batch.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1 --grid 9 --execute
```

一次执行多个明确格：

```bash
python AI生产/H3生产包/tools/run_h3_batch.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1 --grid 9 --grid 10 --execute
```

明确执行整章：

```bash
python AI生产/H3生产包/tools/run_h3_batch.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json \
  --chapter 1 --all-grids --execute
```

付费安全规则：

1. `--execute` 时必须且只能选一个章节。
2. 必须选 `--grid` 或明确写 `--all-grids`。
3. 已存在的 MP4 自动跳过。
4. 任一任务失败立即停止，不自动重试，不悄悄产生第二笔费用。
5. 默认只编译/打印，不会调用生成 API。

## H3 模式策略

- `t2va`：没有可用人物参考图时使用纯文本。
- `ref2va`：命中已验收角色三视图时自动附加人物参考图。
- `i2va/fl2va/l2va`：编译器支持并校验，但章节 manifest 当前不自动制造首尾帧。
- 帧模式与多模态参考模式互斥；音频参考必须同时存在图像或视频参考。
- 一格只完成一个因果节拍：0—3 秒建立空间，3—10 秒完成核心动作，10—15 秒停在结果、台词或证据上。

## 人物与场景一致性

人物参考图只锁身份、脸型、发式和服装层级。现有三视图是白底多视角资产，提示词明确禁止复制白底排版、文字、空手站姿和多个人物分身。

现有场景设定图多为概念板或宫格图，因此不直接附加为 H3 `reference-image`；`scenes.json` 只向提示注入稳定的材质、动线、入口、轴线与连续性锁，避免模型生成宫格拼贴。

## 精确文字

比分、HUD、地图名、姓名、名册、合同、印章、门禁记录、直播标题一律后期合成。H3 只负责版面、安全区、人物动作和声音，不承担精确汉字生成。

## 修改后的正确流程

```text
正文事实
  → 人物/制度/空间权威文件
  → 十格分镜
  → 免费编译 JSON
  → 免费命令预览
  → 单格 H3 付费样片
  → 连续性与文字 QA
  → 通过后再扩大到相邻格/整章
```

不要直接批量执行 440 个任务。先从第 1 章第 9 格或第 10 格验证穿越后人物、宫廷设备房、对白和后期文字安全区。
