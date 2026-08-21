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
    compile_manifest,
    validate_manifest,
)
from tools.run_h3_batch import (  # noqa: E402
    ensure_api_key_auth,
    filter_jobs,
    require_execute_scope,
)


def standard_storyboard(chapter: int) -> str:
    lines = [
        f"# 第{chapter:02d}章 测试章节 十格分镜",
        "",
        "> **视频单元：** MiniMax H3，15秒/格；每格按0—3秒建立空间、3—10秒完成一个核心动作、10—15秒收在结果、台词或证据上。",
    ]
    for grid in range(1, 11):
        lines.extend(
            [
                "",
                f"## 第{grid}格",
                "",
                "- **景别/地点：** 中景／测试房。",
                "- **画面动作：** 0—3秒：建立空间。3—10秒：贼贼姐完成一个动作。10—15秒：停在证据上。",
                "- **台词或音效：** 贼贼姐：“收到。”／风扇声。",
                "- **CS信息：** 人数和席位不变。",
                "- **关系/笑点：** 不用印章替人按键。",
                "- **空间锚点：** 长桌、门、耳机。",
            ]
        )
    return "\n".join(lines)


class ManifestTests(unittest.TestCase):
    def test_duplicate_chapter_numbers_are_rejected(self) -> None:
        manifest = {
            "schema_version": "1.0",
            "project_id": "test",
            "project_root": "../../..",
            "defaults": {"model": "MiniMax-H3", "duration": 15, "ratio": "16:9"},
            "registries": {"characters": "assets/characters.json"},
            "chapters": [
                {"chapter": 1, "title": "A", "storyboard": "分镜/a.md"},
                {"chapter": 1, "title": "B", "storyboard": "分镜/b.md"},
            ],
        }
        with self.assertRaises(H3ValidationError):
            validate_manifest(manifest, expected_chapter_count=None)

    def test_compile_manifest_resolves_paths_and_selects_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            pack = project / "AI生产" / "H3生产包"
            config_dir = pack / "config"
            assets_dir = pack / "assets"
            storyboard_dir = project / "分镜"
            config_dir.mkdir(parents=True)
            assets_dir.mkdir(parents=True)
            storyboard_dir.mkdir(parents=True)

            (storyboard_dir / "第02章_十格分镜.md").write_text(
                standard_storyboard(2), encoding="utf-8"
            )
            (assets_dir / "characters.json").write_text(
                json.dumps(
                    {
                        "characters": [
                            {
                                "id": "CHAR_ZEIZEI",
                                "name": "贼贼姐",
                                "aliases": ["贼贼姐"],
                                "reference_image": "角色三视图/01.png",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manifest_path = config_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "project_id": "test",
                        "project_root": "../../..",
                        "defaults": {
                            "model": "MiniMax-H3",
                            "duration": 15,
                            "ratio": "16:9",
                            "style_lock": "电影级半写实国漫。",
                            "global_negative": "随机文字。",
                            "post_text_policy": "精确文字后期合成。",
                            "output_root": "AI生产/H3生产包/output",
                        },
                        "registries": {
                            "characters": "AI生产/H3生产包/assets/characters.json"
                        },
                        "chapters": [
                            {
                                "chapter": 2,
                                "title": "测试章节",
                                "storyboard": "分镜/第02章_十格分镜.md",
                                "protagonist_ref_from_grid": 1,
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = compile_manifest(
                manifest_path,
                chapter_numbers={2},
                expected_chapter_count=None,
            )

        self.assertEqual(result["project_id"], "test")
        self.assertEqual(len(result["chapters"]), 1)
        self.assertEqual(len(result["chapters"][0]["jobs"]), 10)
        self.assertEqual(result["chapters"][0]["jobs"][0]["source_storyboard"], "分镜/第02章_十格分镜.md")


class RunnerSafetyTests(unittest.TestCase):
    def test_paid_execution_requires_one_chapter_and_explicit_grid_scope(self) -> None:
        with self.assertRaises(H3ValidationError):
            require_execute_scope(execute=True, chapters=[], grids=[], all_grids=False)
        with self.assertRaises(H3ValidationError):
            require_execute_scope(execute=True, chapters=[1, 2], grids=[1], all_grids=False)
        with self.assertRaises(H3ValidationError):
            require_execute_scope(execute=True, chapters=[1], grids=[], all_grids=False)

        require_execute_scope(execute=True, chapters=[1], grids=[1], all_grids=False)
        require_execute_scope(execute=True, chapters=[1], grids=[], all_grids=True)

    def test_auth_must_be_api_key_without_exposing_key(self) -> None:
        ensure_api_key_auth({"method": "api-key", "masked_key": "sk-***"})
        with self.assertRaises(H3ValidationError):
            ensure_api_key_auth({"method": "oauth"})

    def test_filter_jobs_selects_requested_grids_in_order(self) -> None:
        chapters = [
            {
                "chapter": 1,
                "jobs": [
                    {"chapter": 1, "grid": 1, "job_id": "A"},
                    {"chapter": 1, "grid": 2, "job_id": "B"},
                ],
            },
            {
                "chapter": 2,
                "jobs": [{"chapter": 2, "grid": 1, "job_id": "C"}],
            },
        ]
        jobs = filter_jobs(chapters, chapters={1}, grids={2})
        self.assertEqual([job["job_id"] for job in jobs], ["B"])


if __name__ == "__main__":
    unittest.main()
