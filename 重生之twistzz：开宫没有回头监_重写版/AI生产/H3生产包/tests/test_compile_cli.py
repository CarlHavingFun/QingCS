from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]


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


class CompileCliTests(unittest.TestCase):
    def test_cli_writes_portable_chapter_json_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            pack = project / "AI生产" / "H3生产包"
            config = pack / "config"
            assets = pack / "assets"
            storyboard = project / "分镜"
            generated = pack / "generated"
            config.mkdir(parents=True)
            assets.mkdir(parents=True)
            storyboard.mkdir(parents=True)
            (storyboard / "第02章_十格分镜.md").write_text(
                standard_storyboard(2), encoding="utf-8"
            )
            (assets / "characters.json").write_text(
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
            manifest = config / "manifest.json"
            manifest.write_text(
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
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACK_ROOT / "tools" / "compile_storyboards.py"),
                    str(manifest),
                    "--chapter",
                    "2",
                    "--generated-dir",
                    str(generated),
                    "--allow-partial-manifest",
                ],
                cwd=PACK_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            chapter_json = json.loads((generated / "ch02.h3.json").read_text(encoding="utf-8"))
            index_json = json.loads((generated / "index.json").read_text(encoding="utf-8"))

        self.assertEqual(len(chapter_json["jobs"]), 10)
        self.assertNotIn(str(project), json.dumps(chapter_json, ensure_ascii=False))
        self.assertEqual(index_json["job_count"], 10)
        self.assertEqual(index_json["chapters"][0]["chapter"], 2)


if __name__ == "__main__":
    unittest.main()
