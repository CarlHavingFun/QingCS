from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACK_ROOT))

from tools.h3_pipeline import (  # noqa: E402
    H3ValidationError,
    build_h3_prompt,
    build_mmx_command,
    compile_storyboard,
    detect_character_references,
    detect_scene_references,
    parse_storyboard_text,
    validate_job,
)


def make_standard_storyboard() -> str:
    blocks = [
        "# 第02章 五席与五种责任 十格分镜",
        "",
        "> **视频单元：** MiniMax H3，15秒/格；每格按0—3秒建立空间、3—10秒完成一个核心动作、10—15秒收在结果、台词或证据上。",
        "",
    ]
    for grid in range(1, 11):
        blocks.extend(
            [
                f"## 第{grid}格",
                "",
                "- **景别/地点：** 中景／太和门五席登记案。",
                f"- **画面动作：** 0—3秒：建立太和门与第{grid}张职责牌。3—10秒：贼贼姐把职责牌交给大表姐。10—15秒：镜头停在签认栏和空白文字安全区。",
                "- **台词或音效：** 大表姐：“各人签自己的。”／纸牌、门风和笔尖声。",
                "- **CS信息：** 五席不变；本格只确认责任，不改变首发。",
                "- **关系/笑点：** 印章不能替谁拿枪。",
                "- **空间锚点：** 太和门、长案、职责牌、铜镇纸、签认栏。",
                "",
            ]
        )
    return "\n".join(blocks)


def make_director_storyboard() -> str:
    blocks = ["# 第01章《输掉决赛后，我成了大清女队首发》｜电影级十格压缩分镜", ""]
    for grid in range(1, 11):
        blocks.extend(
            [
                f"## 第{grid}格｜00:00—00:15｜镜头{grid}",
                "",
                "- **叙事任务：** 完成一个可读的因果动作。",
                "- **观众问题：** 这一格发生了什么？",
                "- **H3提示词：**  ",
                "  **SCENE:** A fictional palace esports room with tactile materials.  ",
                f"  **ACTION:** The subject completes action {grid} and settles.  ",
                "  **CAMERA:** Stable 50mm medium shot with a slow push.  ",
                "  **BLOCKING:** Subject frame-left, doorway frame-right.  ",
                "  **PERFORMANCE:** Restrained and natural.  ",
                "  **AUDIO:** Room tone and one short Chinese line.  ",
                "  **TRANSITION:** Hold on the evidence.  ",
                "  **CONTINUITY:** Preserve the same props and screen direction.  ",
                "  **NEGATIVE:** random text, real-person likeness, extra characters.",
                "",
                "---",
                "",
            ]
        )
    return "\n".join(blocks)


CHARACTERS = {
    "characters": [
        {
            "id": "CHAR_ZEIZEI",
            "name": "贼贼姐",
            "aliases": ["贼贼姐"],
            "reference_image": "角色三视图/大清五席/01_贼贼姐_三视图.png",
        },
        {
            "id": "CHAR_DABIAO",
            "name": "大表姐",
            "aliases": ["大表姐"],
            "reference_image": "角色三视图/大清五席/02_大表姐_三视图.png",
        },
    ]
}


SCENES = {
    "scenes": [
        {
            "id": "SCN_TAIHEMEN",
            "name": "太和门与外朝前院",
            "aliases": ["太和门", "外朝前院"],
            "visual_lock": "中轴门洞、长案、黄纸训练表、铜镇纸，现代门禁和电力设备克制嵌入。",
        }
    ]
}

DEFAULTS = {
    "model": "MiniMax-H3",
    "duration": 15,
    "ratio": "16:9",
    "style_lock": "电影级半写实国漫，真实人体比例、自然表演、可信材质与设备结构。",
    "global_negative": "Q版，纯二维平涂，照片化真人肖像，随机文字，品牌和现实队标。",
    "post_text_policy": "比分、姓名、HUD、名册和印章文字只留安全区，统一后期合成。",
}


class ParseStoryboardTests(unittest.TestCase):
    def test_standard_storyboard_extracts_ten_grids_and_three_phases(self) -> None:
        parsed = parse_storyboard_text(make_standard_storyboard(), source="chapter02.md")

        self.assertEqual(parsed["chapter"], 2)
        self.assertEqual(len(parsed["grids"]), 10)
        first = parsed["grids"][0]
        self.assertEqual(first["format"], "standard")
        self.assertEqual(first["grid"], 1)
        self.assertEqual(len(first["timeline"]), 3)
        self.assertEqual(first["timeline"][0]["range"], "00:00-00:03")
        self.assertIn("太和门", first["location"])

    def test_director_storyboard_preserves_embedded_h3_fields(self) -> None:
        parsed = parse_storyboard_text(make_director_storyboard(), source="chapter01.md")

        self.assertEqual(parsed["chapter"], 1)
        self.assertEqual(len(parsed["grids"]), 10)
        first = parsed["grids"][0]
        self.assertEqual(first["format"], "director")
        self.assertIn("fictional palace esports room", first["h3_fields"]["SCENE"])
        self.assertIn("real-person likeness", first["h3_fields"]["NEGATIVE"])

    def test_missing_grid_is_rejected_in_strict_mode(self) -> None:
        incomplete = make_standard_storyboard().replace("## 第10格", "## 删除第10格", 1)
        with self.assertRaises(H3ValidationError):
            parse_storyboard_text(incomplete, source="bad.md")


class PromptAndReferenceTests(unittest.TestCase):
    def test_standard_prompt_contains_master_and_micro_timeline(self) -> None:
        grid = parse_storyboard_text(make_standard_storyboard())["grids"][0]
        refs = [
            {"index": 1, "id": "CHAR_ZEIZEI", "name": "贼贼姐"},
            {"index": 2, "id": "CHAR_DABIAO", "name": "大表姐"},
        ]

        prompt = build_h3_prompt(grid, DEFAULTS, refs)

        self.assertIn("总段 00:00-00:15", prompt)
        self.assertIn("00:00-00:03", prompt)
        self.assertIn("00:03-00:10", prompt)
        self.assertIn("00:10-00:15", prompt)
        self.assertIn("参考图1", prompt)
        self.assertIn("不复制白底三视图排版", prompt)
        self.assertIn("后期合成", prompt)

    def test_director_prompt_keeps_existing_h3_direction(self) -> None:
        grid = parse_storyboard_text(make_director_storyboard())["grids"][0]
        prompt = build_h3_prompt(grid, DEFAULTS, [])

        self.assertIn("SCENE:", prompt)
        self.assertIn("ACTION:", prompt)
        self.assertIn("fictional palace esports room", prompt)
        self.assertIn("real-person likeness", prompt)

    def test_character_reference_detection_is_stable_and_deduplicated(self) -> None:
        refs = detect_character_references(
            "贼贼姐把牌递给大表姐，贼贼姐再收回手。",
            CHARACTERS,
            protagonist_id="CHAR_ZEIZEI",
            max_images=9,
        )

        self.assertEqual([item["id"] for item in refs], ["CHAR_ZEIZEI", "CHAR_DABIAO"])

    def test_scene_reference_detection_adds_visual_lock(self) -> None:
        scenes = detect_scene_references("太和门外的长案与门槛", SCENES)
        self.assertEqual([item["id"] for item in scenes], ["SCN_TAIHEMEN"])
        grid = parse_storyboard_text(make_standard_storyboard())["grids"][0]
        prompt = build_h3_prompt(grid, DEFAULTS, [], scenes)
        self.assertIn("SCN_TAIHEMEN", prompt)
        self.assertIn("中轴门洞", prompt)


class CompileAndCommandTests(unittest.TestCase):
    def test_compile_storyboard_produces_ten_valid_jobs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chapter02.md"
            source.write_text(make_standard_storyboard(), encoding="utf-8")
            character_path = root / "characters.json"
            character_path.write_text(json.dumps(CHARACTERS, ensure_ascii=False), encoding="utf-8")

            compiled = compile_storyboard(
                source_path=source,
                chapter_config={
                    "chapter": 2,
                    "title": "五席与五种责任",
                    "protagonist_ref_from_grid": 1,
                },
                defaults=DEFAULTS,
                character_registry=CHARACTERS,
                output_root="AI生产/H3生产包/output",
            )

        self.assertEqual(compiled["chapter"], 2)
        self.assertEqual(len(compiled["jobs"]), 10)
        first = compiled["jobs"][0]
        self.assertEqual(first["model"], "MiniMax-H3")
        self.assertEqual(first["mode"], "ref2va")
        self.assertEqual(first["duration"], 15)
        self.assertTrue(first["download"].endswith("QINGCS_CH02_G01.mp4"))
        validate_job(first)

    def test_validation_rejects_mixed_frame_and_reference_modes(self) -> None:
        job = {
            "job_id": "BAD",
            "model": "MiniMax-H3",
            "mode": "ref2va",
            "duration": 15,
            "ratio": "16:9",
            "prompt": "A valid prompt",
            "image": "start.png",
            "last_frame": None,
            "reference_images": ["character.png"],
            "reference_videos": [],
            "reference_audios": [],
            "download": "out.mp4",
        }
        with self.assertRaises(H3ValidationError):
            validate_job(job)

    def test_mmx_command_uses_official_h3_flags(self) -> None:
        job = {
            "job_id": "QINGCS_CH02_G01",
            "model": "MiniMax-H3",
            "mode": "ref2va",
            "duration": 15,
            "ratio": "16:9",
            "prompt": "One causal action beat.",
            "image": None,
            "last_frame": None,
            "reference_images": ["a.png", "b.png"],
            "reference_videos": [],
            "reference_audios": [],
            "download": "out.mp4",
        }
        command = build_mmx_command(job, mmx_executable="mmx")

        self.assertEqual(command[:4], ["mmx", "video", "generate", "--model"])
        self.assertIn("MiniMax-H3", command)
        self.assertEqual(command.count("--reference-image"), 2)
        self.assertIn("--poll-interval", command)
        self.assertIn("--timeout", command)
        self.assertIn("--non-interactive", command)
        self.assertNotIn("--async", command)


if __name__ == "__main__":
    unittest.main()
