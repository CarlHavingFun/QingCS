# 第一章竖屏六宫格分镜审核稿 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将第一章已经锁定的 23 个真实节奏镜头整理成四张竖屏 2×3 六宫格文字审核板，完整展示原台词、镜头动作、声音、时长和连续性，并在用户审核前保持零生图。

**Architecture:** `第01章_样片逐镜头分镜_重制版.md` 继续作为镜头事实源，新建六宫格审核稿只做无损映射，不改写镜头事实。独立 Python 校验器对四张板的格位、23 个镜头顺序、逐字段镜像、9:16 声明和唯一 QA 空格进行机械验证；目录说明记录新的审核入口和生产停点。

**Tech Stack:** Markdown、Python 3 标准库、`unittest`、Git；不调用万兴剧厂、LibTV API、GPT Image、ComfyUI 或 MiniMax H3。

## Global Constraints

- 视觉方向固定为电影级 3D 国漫写实；上海与白桥属于同一作品的统一材质体系。
- 审核板为竖版 2×3 六宫格；每个剧情关键帧的生产画幅固定为 9:16。
- 第一章保留现有 23 个镜头，不增加第 24 镜，不为凑满六格压缩或扩写剧情。
- 四张板依次为 6、6、6、5 个剧情镜头；`SB-04-C06` 只做台词、声音和连续性检查，禁止生图。
- 所有可听台词必须逐字复制源分镜中的 `DIALOGUE` 和 `DIALOGUE_TIMING`；不得润色、缩写或补写金句。
- 每格必须显示真实 `ADVISORY_DURATION`，不得按宫格平均时长。
- 精确比分、姓名、日期、报名表文字和 UI 只保留在 `POST_TEXT`，不进入图片。
- 本计划只生产可审核文字分镜，不生成场景图、人物图、关键帧或视频。
- 保护工作区已有改动；只提交本计划列出的文件。

---

### Task 1: 建立六宫格审核稿校验器

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/分镜/validate_sixgrid_review.py`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/分镜/test_validate_sixgrid_review.py`

**Interfaces:**
- Consumes: 原始逐镜分镜 Markdown 与新六宫格审核稿 Markdown。
- Produces: `parse_storyboard(text: str) -> dict[str, dict[str, str]]`、`parse_review(text: str) -> tuple[dict[str, str], list[dict[str, str]]]`、`validate_review(storyboard_text: str, review_text: str, expected_boards: dict[str, tuple[str, ...]] = EXPECTED_BOARDS) -> list[str]`；CLI 退出码 0 表示审核稿是 23 镜的无损六宫格映射。

- [ ] **Step 1: 写出单元测试，先验证测试会失败**

测试使用缩小的两板映射，避免依赖尚未创建的正式审核稿：

```python
import unittest

from validate_sixgrid_review import validate_review


class SixGridReviewValidationTests(unittest.TestCase):
    def setUp(self):
        self.storyboard = """\
### 分镜 01
SHOT_ID: S01_SH01
SCENE: B1 — 上海舞台
ANCHOR_REFS: B1, A1
ADVISORY_DURATION: 4.8s
CAMERA_SIZE: 中景
CAMERA_MOVE: 缓慢推进
ACTION_START: 报点开始
ACTION_END: 第二脚步进入声场
DIALOGUE: CHEN_MO（off_screen_radio）：“A1 两个。一个贴三箱，后面还有。”
DIALOGUE_TIMING: CHEN_MO|off_screen_radio|0.4-3.9s|before=0.4|after=0.6
SOUND: 场馆低频与报点
CONTINUITY_IN: 黑场进入
CONTINUITY_OUT: 保留 A1 轴线
POST_TEXT: 比分后期合成
KEYFRAME_MOMENT: 准星仍在烟边
### 分镜 02
SHOT_ID: S01_SH02
SCENE: B1 — 上海舞台
ANCHOR_REFS: B1, A1
ADVISORY_DURATION: 3.6s
CAMERA_SIZE: 屏幕近景
CAMERA_MOVE: 静态跟焦
ACTION_START: 两组脚步出现
ACTION_END: 准星偏离
DIALOGUE: 无台词／刻意沉默
DIALOGUE_TIMING: 无台词／刻意沉默：全镜保留脚步声。
SOUND: 两组脚步
CONTINUITY_IN: 承接报点
CONTINUITY_OUT: 准星偏离烟边
POST_TEXT: 无
KEYFRAME_MOMENT: 准星刚离开烟边
"""
        self.review = """\
SOURCE_STORYBOARD_SHA256: ignored-in-unit-test
BOARD_LAYOUT: PORTRAIT_2X3
SHOT_FRAME_RATIO: 9:16
## SB-T01
BOARD_ID: SB-T01
### 格 01
CELL_ID: SB-T01-C01
CELL_TYPE: SHOT
SHOT_ID: S01_SH01
SCENE: B1 — 上海舞台
ANCHOR_REFS: B1, A1
ADVISORY_DURATION: 4.8s
CAMERA_SIZE: 中景
CAMERA_MOVE: 缓慢推进
ACTION_START: 报点开始
ACTION_END: 第二脚步进入声场
DIALOGUE: CHEN_MO（off_screen_radio）：“A1 两个。一个贴三箱，后面还有。”
DIALOGUE_TIMING: CHEN_MO|off_screen_radio|0.4-3.9s|before=0.4|after=0.6
SOUND: 场馆低频与报点
CONTINUITY_IN: 黑场进入
CONTINUITY_OUT: 保留 A1 轴线
POST_TEXT: 比分后期合成
KEYFRAME_MOMENT: 准星仍在烟边
IMAGE_STATUS: NOT_GENERATED
### 格 02
CELL_ID: SB-T01-C02
CELL_TYPE: SHOT
SHOT_ID: S01_SH02
SCENE: B1 — 上海舞台
ANCHOR_REFS: B1, A1
ADVISORY_DURATION: 3.6s
CAMERA_SIZE: 屏幕近景
CAMERA_MOVE: 静态跟焦
ACTION_START: 两组脚步出现
ACTION_END: 准星偏离
DIALOGUE: 无台词／刻意沉默
DIALOGUE_TIMING: 无台词／刻意沉默：全镜保留脚步声。
SOUND: 两组脚步
CONTINUITY_IN: 承接报点
CONTINUITY_OUT: 准星偏离烟边
POST_TEXT: 无
KEYFRAME_MOMENT: 准星刚离开烟边
IMAGE_STATUS: NOT_GENERATED
"""

    def test_accepts_exact_mirrored_shots(self):
        errors = validate_review(
            self.storyboard,
            self.review,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertEqual([], errors)

    def test_rejects_rewritten_dialogue(self):
        altered = self.review.replace("A1 两个。一个贴三箱，后面还有。", "A1 有两个人！")
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("DIALOGUE must exactly match" in item for item in errors))

    def test_rejects_reordered_shots(self):
        altered = self.review.replace("SHOT_ID: S01_SH01", "SHOT_ID: S01_SH02", 1)
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("shot order" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
cd '天工枪局：白桥第一枪/AI生产/样片01/分镜'
python3 -m unittest -v test_validate_sixgrid_review.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'validate_sixgrid_review'`.

- [ ] **Step 2: 实现最小解析器和验证器**

验证器中的正式映射必须写死为：

```python
EXPECTED_BOARDS = {
    "SB-01": (
        "S01_SH01", "S01_SH02", "S01_SH03", "S01_SH04",
        "S02_SH01", "S02_SH02A",
    ),
    "SB-02": (
        "S02_SH02B", "S03_SH01", "S03_SH02", "S03_SH03",
        "S03_SH04A", "S03_SH04B",
    ),
    "SB-03": (
        "S03_SH04C", "S04_SH01", "S04_SH02", "S04_SH03A",
        "S04_SH03B", "S04_SH04",
    ),
    "SB-04": (
        "S05_SH01", "S05_SH02", "S06_SH01A", "S06_SH01B",
        "S07_SH01",
    ),
}

MIRRORED_FIELDS = (
    "SCENE", "ANCHOR_REFS", "ADVISORY_DURATION", "CAMERA_SIZE",
    "CAMERA_MOVE", "ACTION_START", "ACTION_END", "DIALOGUE",
    "DIALOGUE_TIMING", "SOUND", "CONTINUITY_IN", "CONTINUITY_OUT",
    "POST_TEXT", "KEYFRAME_MOMENT",
)
```

实现要求：

- `parse_storyboard` 以 `### 分镜` 和 `SHOT_ID:` 划分镜头。
- `parse_review` 读取头部字段、`## SB-xx` 板号和 `### 格 xx` 卡片。
- 每个 `SHOT` 卡必须按 `MIRRORED_FIELDS` 与源分镜逐字相等。
- 正式文件必须存在 4 张板、24 个格位、23 个唯一 `SHOT` 卡和 1 个 `QA_ONLY` 卡。
- `SB-04-C06` 必须是唯一 `QA_ONLY` 卡，且包含 `GENERATE_IMAGE: NO` 与 `IMAGE_STATUS: NOT_APPLICABLE`。
- 所有 `SHOT` 卡必须包含 `IMAGE_STATUS: NOT_GENERATED`。
- 头部必须包含 `BOARD_LAYOUT: PORTRAIT_2X3`、`SHOT_FRAME_RATIO: 9:16`，并以 SHA-256 锁定源分镜。
- CLI 参数固定为 `--storyboard PATH --review PATH`。

- [ ] **Step 3: 运行单元测试确认通过**

Run:

```bash
cd '天工枪局：白桥第一枪/AI生产/样片01/分镜'
python3 -m unittest -v test_validate_sixgrid_review.py
```

Expected: 3 tests，全部 `ok`。

- [ ] **Step 4: Commit**

```bash
git add -- \
  '天工枪局：白桥第一枪/AI生产/样片01/分镜/validate_sixgrid_review.py' \
  '天工枪局：白桥第一枪/AI生产/样片01/分镜/test_validate_sixgrid_review.py'
git commit -m 'test: validate chapter 1 six-grid review boards'
```

### Task 2: 编写四张竖屏六宫格分镜审核稿

**Files:**
- Create: `天工枪局：白桥第一枪/分镜/第01章_竖屏六宫格分镜审核稿.md`

**Interfaces:**
- Consumes: `分镜/第01章_样片逐镜头分镜_重制版.md` 的 23 个镜头及 `dialogue-lock-v2.json`。
- Produces: `SB-01` 至 `SB-04` 四张文字审核板；下一阶段仅在用户确认后读取其中的 `KEYFRAME_MOMENT` 和冻结场景锚点生成画面。

- [ ] **Step 1: 建立文件头和四张 2×3 布局索引**

文件头必须写入：

```text
SOURCE_STORYBOARD: 分镜/第01章_样片逐镜头分镜_重制版.md
SOURCE_STORYBOARD_SHA256: 05912307332ed224bf4270373f33d0415fce814a9768a62162f416bf0e489490
BOARD_LAYOUT: PORTRAIT_2X3
SHOT_FRAME_RATIO: 9:16
VISUAL_STYLE: 电影级 3D 国漫写实
IMAGE_PRODUCTION: STOPPED_PENDING_REVIEW
```

每张板先放一张两列三行的 Markdown 索引表，格位顺序严格按从左到右、从上到下排列。`SB-04-C06` 标为“审核栏／不生图”。

- [ ] **Step 2: 写 SB-01 与 SB-02**

`SB-01` 使用镜头 1–6：Major 决胜局 → 拆包失败 → 亚军结果 → 进入复盘 → 周野承认漏报的第一句。

`SB-02` 使用镜头 7–12：周野讲清准星离位因果 → 旧报点异常 → 声卡断开但声音继续 → 手机证据失败 → 暗红木框 → 钟声后开始下坠。

每个格位完整复制以下字段：

```text
CELL_ID
CELL_TYPE
SHOT_ID
SCENE
ANCHOR_REFS
ADVISORY_DURATION
CAMERA_SIZE
CAMERA_MOVE
ACTION_START
ACTION_END
DIALOGUE
DIALOGUE_TIMING
SOUND
CONTINUITY_IN
CONTINUITY_OUT
POST_TEXT
KEYFRAME_MOMENT
IMAGE_STATUS
```

`DIALOGUE` 必须在格内直接可见；无台词镜头原样写“无台词／刻意沉默”，不能省略台词字段。

- [ ] **Step 3: 写 SB-03 与 SB-04**

`SB-03` 使用镜头 13–18：奖牌滑落与黑场 → 白桥设备间醒来 → 苏禾安全核验 → 监控断帧 → 临时客籍程序 → 周野提出离线试机。

`SB-04` 使用镜头 19–23：第一轮投掷和补枪失败 → 唐夏点破“两条线” → 第二轮重新分级报点 → 先补近点再转右廊 → 报名表落笔与“第一枪，从白桥开始”。

`SB-04-C06` 写成：

```text
CELL_ID: SB-04-C06
CELL_TYPE: QA_ONLY
GENERATE_IMAGE: NO
IMAGE_STATUS: NOT_APPLICABLE
QA_DIALOGUE_LOCK: 给不给闪？／给。／你又想看两条线。／对。／右廊可能一个，距离不确定。近点先打，我补近点。右边出声再转。／收到。／右廊到门，半秒！／第五个人填谁？／也好。／第一枪，从白桥开始。
QA_SOUND_LOCK: 第一轮无胜利音乐；第二轮近点击杀完成并留反应空隙后才报右廊；结尾只保留夜雨、纸张与笔尖声。
QA_CONTINUITY_LOCK: 第一轮与第二轮复用同一乙仓轴线；第二轮严格先补近点再转右廊；报名桌仅在结尾使用。
```

- [ ] **Step 4: 运行正式六宫格校验**

Run:

```bash
python3 '天工枪局：白桥第一枪/AI生产/样片01/分镜/validate_sixgrid_review.py' \
  --storyboard '天工枪局：白桥第一枪/分镜/第01章_样片逐镜头分镜_重制版.md' \
  --review '天工枪局：白桥第一枪/分镜/第01章_竖屏六宫格分镜审核稿.md'
```

Expected:

```text
PASS: 4 boards / 24 cells / 23 source-locked shots / 1 QA-only cell; frame ratio 9:16; image production stopped.
```

- [ ] **Step 5: Commit**

```bash
git add -- '天工枪局：白桥第一枪/分镜/第01章_竖屏六宫格分镜审核稿.md'
git commit -m 'docs: add chapter 1 vertical six-grid review boards'
```

### Task 3: 发布审核入口并执行生产停点验收

**Files:**
- Modify: `天工枪局：白桥第一枪/分镜/目录说明.md`

**Interfaces:**
- Consumes: 已通过机械校验的四张六宫格审核板。
- Produces: 明确的人工审核入口；在用户确认四张板之前，GPT Image 场景图和剧情关键帧均不得进入生成队列。

- [ ] **Step 1: 更新分镜读取顺序**

将生产入口调整为：

```text
正文 → 台词锁 → 场景先行设计 → 锚点清单 → 重制版逐镜分镜 → 竖屏六宫格分镜审核稿 → 用户审核 → 场景图 → 冻结场景锚点 → 剧情关键帧
```

在目录说明中加入设计文件 `docs/superpowers/specs/2026-08-13-ch01-scene-first-vertical-storyboard-design.md` 和审核稿 `分镜/第01章_竖屏六宫格分镜审核稿.md`，并明确旧关键帧提示词当前不具备 9:16 生产资格。

- [ ] **Step 2: 运行原事实源与新审核稿双重验证**

Run:

```bash
python3 '天工枪局：白桥第一枪/AI生产/样片01/声音/validate_storyboard_v2.py' \
  --source '天工枪局：白桥第一枪/正文/第01章_输掉Major后，我从民间赛重新开始.md' \
  --dialogue '天工枪局：白桥第一枪/AI生产/样片01/声音/dialogue-lock-v2.json' \
  --storyboard '天工枪局：白桥第一枪/分镜/第01章_样片逐镜头分镜_重制版.md'

python3 '天工枪局：白桥第一枪/AI生产/样片01/分镜/validate_sixgrid_review.py' \
  --storyboard '天工枪局：白桥第一枪/分镜/第01章_样片逐镜头分镜_重制版.md' \
  --review '天工枪局：白桥第一枪/分镜/第01章_竖屏六宫格分镜审核稿.md'

git diff --check
```

Expected: 原分镜报告 23 个 actual shots、建议总时长 119.9 秒；六宫格报告 4 boards／24 cells／23 shots／1 QA-only；`git diff --check` 无输出。

- [ ] **Step 3: 人工抽检五个因果点**

逐项确认：

1. `S01_SH02 → S01_SH03`：准星先离开，赵雨后倒下。
2. `S03_SH04A → B → C`：暗红木框完成后才有钟声，钟声停留后才下坠，奖牌最后滑落。
3. `S04_SH03A/B → S04_SH04`：临时客籍表一直留在 B3 设备间维修台，没有提前切到 B5。
4. `S05_SH01 → S06_SH01A/B`：两轮复用同一乙仓轴线，第二轮先补近点再转右廊。
5. `S07_SH01`：韩平台词与周野内心声逐字来自正文，报名表精确文字仍留在 `POST_TEXT`。

- [ ] **Step 4: Commit**

```bash
git add -- '天工枪局：白桥第一枪/分镜/目录说明.md'
git commit -m 'docs: publish chapter 1 six-grid review entry'
```

- [ ] **Step 5: 停止并交用户审核**

只交付六宫格审核稿、校验结果和镜头总时长；明确场景图、关键帧与视频仍为零新增。用户确认四张板后，下一阶段才读取 `gpt-image` skill 编写并执行上海／白桥场景设定板提示词。
