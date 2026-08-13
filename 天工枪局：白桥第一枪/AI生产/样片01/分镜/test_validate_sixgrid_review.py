import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_sixgrid_review import parse_storyboard, validate_review


PRODUCTION_BOARDS = {
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

PRODUCTION_MIRRORED_FIELDS = (
    "SCENE", "ANCHOR_REFS", "ADVISORY_DURATION", "CAMERA_SIZE",
    "CAMERA_MOVE", "ACTION_START", "ACTION_END", "DIALOGUE",
    "DIALOGUE_TIMING", "SOUND", "CONTINUITY_IN", "CONTINUITY_OUT",
    "POST_TEXT", "KEYFRAME_MOMENT",
)


def build_production_documents(include_qa=True):
    storyboard_lines = []
    review_lines = [
        "SOURCE_STORYBOARD_SHA256: ignored-in-unit-test",
        "BOARD_LAYOUT: PORTRAIT_2X3",
        "SHOT_FRAME_RATIO: 9:16",
    ]

    for board_id, shot_ids in PRODUCTION_BOARDS.items():
        review_lines.extend((f"## {board_id}", f"BOARD_ID: {board_id}"))
        for cell_number, shot_id in enumerate(shot_ids, start=1):
            values = {
                "SCENE": f"scene {shot_id}",
                "ANCHOR_REFS": f"anchor {shot_id}",
                "ADVISORY_DURATION": f"{cell_number}.0s",
                "CAMERA_SIZE": f"size {shot_id}",
                "CAMERA_MOVE": f"move {shot_id}",
                "ACTION_START": f"start {shot_id}",
                "ACTION_END": f"end {shot_id}",
                "DIALOGUE": f"dialogue {shot_id}",
                "DIALOGUE_TIMING": f"timing {shot_id}",
                "SOUND": f"sound {shot_id}",
                "CONTINUITY_IN": f"in {shot_id}",
                "CONTINUITY_OUT": f"out {shot_id}",
                "POST_TEXT": f"post {shot_id}",
                "KEYFRAME_MOMENT": f"moment {shot_id}",
            }
            storyboard_lines.extend((f"### 分镜 {shot_id}", f"SHOT_ID: {shot_id}"))
            storyboard_lines.extend(
                f"{field}: {values[field]}" for field in PRODUCTION_MIRRORED_FIELDS
            )

            cell_id = f"{board_id}-C{cell_number:02d}"
            review_lines.extend(
                (
                    f"### 格 {cell_number:02d}",
                    f"CELL_ID: {cell_id}",
                    "CELL_TYPE: SHOT",
                    f"SHOT_ID: {shot_id}",
                )
            )
            review_lines.extend(
                f"{field}: {values[field]}" for field in PRODUCTION_MIRRORED_FIELDS
            )
            review_lines.append("IMAGE_STATUS: NOT_GENERATED")

    if include_qa:
        review_lines.extend(
            (
                "### 格 06",
                "CELL_ID: SB-04-C06",
                "CELL_TYPE: QA_ONLY",
                "GENERATE_IMAGE: NO",
                "IMAGE_STATUS: NOT_APPLICABLE",
            )
        )

    return "\n".join(storyboard_lines) + "\n", "\n".join(review_lines) + "\n"


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

    def test_storyboard_shot_id_starts_a_block_without_a_heading(self):
        shots = parse_storyboard(
            "SHOT_ID: S01_SH01\nSCENE: first\n"
            "SHOT_ID: S01_SH02\nSCENE: second\n"
        )
        self.assertEqual(("S01_SH01", "S01_SH02"), tuple(shots))
        self.assertEqual("second", shots["S01_SH02"]["SCENE"])

    def test_rejects_rewritten_dialogue(self):
        altered = self.review.replace("A1 两个。一个贴三箱，后面还有。", "A1 有两个人！")
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("DIALOGUE must exactly match" in item for item in errors))

    def test_rejects_a_duplicate_review_field(self):
        original = "DIALOGUE: CHEN_MO（off_screen_radio）：“A1 两个。一个贴三箱，后面还有。”"
        altered = self.review.replace(
            original,
            "DIALOGUE: CHEN_MO（off_screen_radio）：“A1 有两个人！”\n" + original,
            1,
        )
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("repeats DIALOGUE" in item for item in errors))

    def test_rejects_reordered_shots(self):
        altered = self.review.replace("SHOT_ID: S01_SH01", "SHOT_ID: S01_SH02", 1)
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("shot order" in item for item in errors))

    def test_rejects_source_sha_mismatch_by_default(self):
        errors = validate_review(
            self.storyboard,
            self.review,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
        )
        self.assertTrue(
            any("SOURCE_STORYBOARD_SHA256 must match" in item for item in errors)
        )

    def test_rejects_invalid_review_format_headers(self):
        cases = (
            ("BOARD_LAYOUT: PORTRAIT_2X3", "BOARD_LAYOUT: LANDSCAPE_3X2", "BOARD_LAYOUT"),
            ("SHOT_FRAME_RATIO: 9:16", "SHOT_FRAME_RATIO: 16:9", "SHOT_FRAME_RATIO"),
        )
        for original, replacement, error_field in cases:
            with self.subTest(field=error_field):
                errors = validate_review(
                    self.storyboard,
                    self.review.replace(original, replacement),
                    expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
                    check_sha=False,
                )
                self.assertTrue(any(error_field in item for item in errors))

    def test_rejects_generated_shot_image_status(self):
        altered = self.review.replace(
            "IMAGE_STATUS: NOT_GENERATED", "IMAGE_STATUS: GENERATED", 1
        )
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("IMAGE_STATUS must be 'NOT_GENERATED'" in item for item in errors))

    def test_rejects_a_cell_id_that_does_not_match_its_position(self):
        altered = self.review.replace("CELL_ID: SB-T01-C01", "CELL_ID: SB-T01-C02", 1)
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("CELL_ID must be 'SB-T01-C01'" in item for item in errors))

    def test_production_layout_requires_the_qa_only_cell(self):
        storyboard, review = build_production_documents(include_qa=False)
        errors = validate_review(storyboard, review, check_sha=False)
        self.assertTrue(any("24 cells" in item for item in errors))
        self.assertTrue(any("QA_ONLY" in item for item in errors))

    def test_production_qa_cell_is_fixed_and_never_generated(self):
        storyboard, review = build_production_documents()
        cases = (
            ("CELL_ID: SB-04-C06", "CELL_ID: SB-04-C05", "SB-04-C06"),
            ("GENERATE_IMAGE: NO", "GENERATE_IMAGE: YES", "GENERATE_IMAGE must be 'NO'"),
            (
                "IMAGE_STATUS: NOT_APPLICABLE",
                "IMAGE_STATUS: NOT_GENERATED",
                "IMAGE_STATUS must be 'NOT_APPLICABLE'",
            ),
        )
        for original, replacement, expected_error in cases:
            with self.subTest(replacement=replacement):
                errors = validate_review(
                    storyboard,
                    review.replace(original, replacement, 1),
                    check_sha=False,
                )
                self.assertTrue(any(expected_error in item for item in errors))

    def test_rejects_reordered_board_sections(self):
        storyboard, review = build_production_documents()
        first_start = review.index("## SB-01")
        second_start = review.index("## SB-02")
        third_start = review.index("## SB-03")
        altered = (
            review[:first_start]
            + review[second_start:third_start]
            + review[first_start:second_start]
            + review[third_start:]
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("board order" in item for item in errors))

    def test_production_layout_requires_exactly_23_shot_cards(self):
        storyboard, review = build_production_documents()
        fifth_cell_start = review.rindex("### 格 05")
        qa_cell_start = review.rindex("### 格 06")
        duplicate = review[fifth_cell_start:qa_cell_start]
        duplicate = duplicate.replace("### 格 05", "### 格 07", 1)
        duplicate = duplicate.replace("CELL_ID: SB-04-C05", "CELL_ID: SB-04-C07", 1)
        errors = validate_review(storyboard, review + duplicate, check_sha=False)
        self.assertTrue(any("23 SHOT cards" in item for item in errors))

    def test_production_layout_requires_23_unique_shot_ids(self):
        storyboard, review = build_production_documents()
        altered = review.replace("SHOT_ID: S07_SH01", "SHOT_ID: S05_SH01", 1)
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("23 unique SHOT_ID" in item for item in errors))

    def test_production_layout_rejects_an_unmapped_source_shot(self):
        storyboard, review = build_production_documents()
        altered = storyboard + "### 分镜 extra\nSHOT_ID: S99_SH99\n"
        errors = validate_review(altered, review, check_sha=False)
        self.assertTrue(any("source storyboard must contain exactly 23 shots" in item for item in errors))

    def test_cli_reports_a_valid_source_locked_production_review(self):
        storyboard, review = build_production_documents()
        digest = hashlib.sha256(storyboard.encode("utf-8")).hexdigest()
        review = review.replace("ignored-in-unit-test", digest, 1)
        result = self.run_cli(storyboard, review)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "PASS: 4 boards / 24 cells / 23 source-locked shots / "
            "1 QA-only cell; frame ratio 9:16; image production stopped.\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    def test_cli_returns_nonzero_and_reports_validation_errors(self):
        storyboard, review = build_production_documents()
        digest = hashlib.sha256(storyboard.encode("utf-8")).hexdigest()
        review = review.replace("ignored-in-unit-test", digest, 1)
        review = review.replace("BOARD_LAYOUT: PORTRAIT_2X3", "BOARD_LAYOUT: LANDSCAPE_3X2")
        result = self.run_cli(storyboard, review)
        self.assertEqual(1, result.returncode)
        self.assertIn("ERROR: BOARD_LAYOUT", result.stderr)

    def run_cli(self, storyboard, review):
        script = Path(__file__).with_name("validate_sixgrid_review.py")
        with tempfile.TemporaryDirectory() as temp_dir:
            storyboard_path = Path(temp_dir, "storyboard.md")
            review_path = Path(temp_dir, "review.md")
            storyboard_path.write_text(storyboard, encoding="utf-8")
            review_path.write_text(review, encoding="utf-8")
            return subprocess.run(
                (
                    sys.executable,
                    str(script),
                    "--storyboard",
                    str(storyboard_path),
                    "--review",
                    str(review_path),
                ),
                check=False,
                capture_output=True,
                text=True,
            )


if __name__ == "__main__":
    unittest.main()
