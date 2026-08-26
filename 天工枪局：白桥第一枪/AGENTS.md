# 《天工枪局：白桥第一枪》 — 网文写作工具集（Codex）

## Skill 路由表

Codex 中优先通过 `$skill-name` 或 `/skills` 调用；自然语言也可触发对应 skill。

| 命令/意图 | Skill | 说明 |
|------|-------|------|
| `$story-long-write`、写长篇 | story-long-write | 长篇网文写作（逐章推进） |
| `$story-short-write`、写短篇 | story-short-write | 短篇网文写作（情绪驱动） |
| `$story-long-analyze`、长篇拆文 | story-long-analyze | 长篇小说深度拆解 |
| `$story-short-analyze`、短篇拆文 | story-short-analyze | 短篇小说拆文分析 |
| `$story-long-scan`、长篇扫榜 | story-long-scan | 长篇小说榜单与市场趋势 |
| `$story-short-scan`、短篇扫榜 | story-short-scan | 短篇小说榜单与情绪风口 |
| `$story-deslop`、去 AI 味 | story-deslop | 去除 AI 写作痕迹 |
| `$story-cover`、封面 | story-cover | 生成封面图 |
| `$story-review`、审查 | story-review | 多视角对抗式审查 |
| `$story-import`、导入 | story-import | 逆向导入已有小说到项目结构 |
| `$story`、网文 | story | 工具箱路由与模糊意图自动分发 |
| `$story-setup`、准备写书 | story-setup | 环境部署与升级 |
| `$browser-cdp` | browser-cdp | 浏览器 CDP 工具；本机当前默认禁用 |

## 文件结构

本目录本身就是书目根目录，使用现有的根级结构，不再嵌套同名书目目录。

- `正文/` — 长篇小说正文章节
- `设定/` — 世界、时代、游戏与 IP 设定
- `人物档案/` — 角色总表与人物档案
- `大纲/` — 后续由写作流程建立的卷纲、篇章总纲与章节细纲
- `追踪/` — 后续由导入/迁移流程建立的结构化写作状态
- `分镜/`、`提示词/`、`视觉资产/`、`AI生产/` — 漫剧生产资产
- `拆文库/`、`对标/` — 拆文与对标分析资产（按需创建）

## 现有工程兼容规则

- `README.md` 的“正史优先级”以及 `设定/IP圣经/00_专名词典与原创边界.md` 是项目权威；通用 story skill 与其冲突时，以项目权威为准。
- 小说续写或重写前先读取 `skills/tiangong-novel-production/SKILL.md`；审读前先读取 `skills/tiangong-human-first-novel-review/SKILL.md`。
- 当前正式正文只承认第一章。完成白桥民间赛第一部篇章总纲、章节细纲以及既有小说的追踪迁移前，不得创作第二章。
- 这是既有自定义长篇：首次接入通用写作流水线应先使用 `$story-import` 的迁移/导入路径建立 `追踪/_tracking-state.json`，不得把它当空白新书直接续写。
- 漫剧、分镜、视觉和 ComfyUI 视频任务继续遵守上层 QingCS 的 MiniMax H3 规则，并优先读取相应 `tiangong-*` 项目 Skill。

## Codex 项目约定

- Codex custom agents 部署在 `.codex/agents/*.toml`，需要新开 Codex 会话后才会稳定可用。
- Codex hooks 部署在 `.codex/hooks.json` 和 `.codex/hooks/`；项目 `.codex/` 层需要被信任，非 managed hooks 还需要在 `/hooks` 中 review/trust 后才会运行。
- 写正文前必须先有对应大纲：长篇 `大纲/细纲_第N章*.md`，短篇 `小节大纲.md`。Codex hooks 会做机械守卫，但 skill 流程本身也必须遵守。
- Compact 后优先读取 `追踪/上下文.md` 恢复当前写作状态。

## 协作规则

Agent 间的协调关系由 `.codex/agents/*.toml` 的职责边界描述定义，不需要独立协调规则文件。

## Compact 后恢复上下文

写作中的关键上下文：

1. 当前写作项目名称和进度
2. 最近讨论的角色设定变更
3. 未完成的伏笔列表
4. 当前章节的情绪/节奏目标

如果存在 `追踪/上下文.md`，compact 后首先读取该文件恢复上下文。
