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

PRODUCTION_QA_LOCKS = {
    "QA_DIALOGUE_LOCK": (
        "给不给闪？／给。／你又想看两条线。／对。／右廊可能一个，距离不确定。"
        "近点先打，我补近点。右边出声再转。／收到。／右廊到门，半秒！／"
        "第五个人填谁？／也好。／第一枪，从白桥开始。"
    ),
    "QA_SOUND_LOCK": (
        "第一轮无胜利音乐；第二轮近点击杀完成并留反应空隙后才报右廊；"
        "结尾环境与拟音只保留夜雨、纸张与笔尖声；对白与内心声按 QA_DIALOGUE_LOCK。"
    ),
    "QA_CONTINUITY_LOCK": (
        "第一轮与第二轮复用同一乙仓轴线；第二轮严格先补近点再转右廊；"
        "报名桌仅在结尾使用。"
    ),
}


def build_production_documents(include_qa=True):
    storyboard_lines = []
    review_lines = [
        "SOURCE_STORYBOARD: 分镜/第01章_样片逐镜头分镜_重制版.md",
        "SOURCE_STORYBOARD_SHA256: ignored-in-unit-test",
        "BOARD_LAYOUT: PORTRAIT_2X3",
        "SHOT_FRAME_RATIO: 9:16",
        "VISUAL_STYLE: 电影级 3D 国漫写实",
        "IMAGE_PRODUCTION: STOPPED_PENDING_REVIEW",
    ]

    for board_id, shot_ids in PRODUCTION_BOARDS.items():
        index_labels = list(shot_ids)
        if board_id == "SB-04":
            index_labels.append("审核栏／不生图")
        review_lines.extend(
            (
                f"## {board_id}",
                "| 左列 | 右列 |",
                "|---|---|",
            )
        )
        for row_start in range(0, 6, 2):
            left_number = row_start + 1
            right_number = row_start + 2
            review_lines.append(
                f"| {board_id}-C{left_number:02d} — {index_labels[row_start]} "
                f"| {board_id}-C{right_number:02d} — {index_labels[row_start + 1]} |"
            )
        review_lines.append(f"BOARD_ID: {board_id}")
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
        review_lines.extend(
            f"{field}: {value}" for field, value in PRODUCTION_QA_LOCKS.items()
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

    def test_rejects_mirrored_field_missing_from_review_card(self):
        altered = self.review.replace("ADVISORY_DURATION: 4.8s\n", "", 1)
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(
            any(
                "review SHOT card S01_SH01 missing ADVISORY_DURATION" in item
                for item in errors
            )
        )

    def test_rejects_mirrored_field_missing_from_source_shot(self):
        altered = self.storyboard.replace(
            "DIALOGUE: CHEN_MO（off_screen_radio）：“A1 两个。一个贴三箱，后面还有。”\n",
            "",
            1,
        )
        errors = validate_review(
            altered,
            self.review,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(
            any(
                "source storyboard shot S01_SH01 missing DIALOGUE" in item
                for item in errors
            )
        )

    def test_rejects_mirrored_field_missing_from_both_sides(self):
        timing = (
            "DIALOGUE_TIMING: "
            "CHEN_MO|off_screen_radio|0.4-3.9s|before=0.4|after=0.6\n"
        )
        storyboard = self.storyboard.replace(timing, "", 1)
        review = self.review.replace(timing, "", 1)
        errors = validate_review(
            storyboard,
            review,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(
            any(
                "source storyboard shot S01_SH01 missing DIALOGUE_TIMING" in item
                for item in errors
            )
        )
        self.assertTrue(
            any(
                "review SHOT card S01_SH01 missing DIALOGUE_TIMING" in item
                for item in errors
            )
        )

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

    def test_production_requires_exact_locked_headers(self):
        storyboard, review = build_production_documents()
        required_headers = (
            ("SOURCE_STORYBOARD", "分镜/第01章_样片逐镜头分镜_重制版.md"),
            ("BOARD_LAYOUT", "PORTRAIT_2X3"),
            ("SHOT_FRAME_RATIO", "9:16"),
            ("VISUAL_STYLE", "电影级 3D 国漫写实"),
            ("IMAGE_PRODUCTION", "STOPPED_PENDING_REVIEW"),
        )
        for field, value in required_headers:
            original = f"{field}: {value}\n"
            for mutation, replacement in (
                ("missing", ""),
                ("corrupt", f"{field}: CORRUPTED\n"),
            ):
                with self.subTest(field=field, mutation=mutation):
                    errors = validate_review(
                        storyboard,
                        review.replace(original, replacement, 1),
                        check_sha=False,
                    )
                    self.assertTrue(any(field in item for item in errors))

    def test_custom_mapping_requires_base_format_headers(self):
        for field, required_value in (
            ("BOARD_LAYOUT", "PORTRAIT_2X3"),
            ("SHOT_FRAME_RATIO", "9:16"),
        ):
            original = f"{field}: {required_value}\n"
            for mutation, replacement, actual_value in (
                ("missing", "", None),
                ("corrupt", f"{field}: CORRUPTED\n", "CORRUPTED"),
            ):
                with self.subTest(field=field, mutation=mutation):
                    errors = validate_review(
                        self.storyboard,
                        self.review.replace(original, replacement, 1),
                        expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
                        check_sha=False,
                    )
                    self.assertIn(
                        f"{field} must be {required_value!r}, got {actual_value!r}",
                        errors,
                    )

    def test_custom_mapping_still_checks_sha_when_enabled(self):
        errors = validate_review(
            self.storyboard,
            self.review,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
        )
        self.assertEqual(1, len(errors))
        self.assertTrue(
            any("SOURCE_STORYBOARD_SHA256 must match" in item for item in errors)
        )

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

    def test_production_qa_locks_are_exact(self):
        storyboard, review = build_production_documents()
        for field, value in PRODUCTION_QA_LOCKS.items():
            original = f"{field}: {value}\n"
            for mutation, replacement in (
                ("missing", ""),
                ("corrupt", f"{field}: CORRUPTED\n"),
            ):
                with self.subTest(field=field, mutation=mutation):
                    errors = validate_review(
                        storyboard,
                        review.replace(original, replacement, 1),
                        check_sha=False,
                    )
                    self.assertTrue(any(field in item for item in errors))

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

    def test_production_rejects_swapped_visible_index_cells(self):
        storyboard, review = build_production_documents()
        altered = review.replace(
            "| SB-01-C01 — S01_SH01 | SB-01-C02 — S01_SH02 |",
            "| SB-01-C02 — S01_SH02 | SB-01-C01 — S01_SH01 |",
            1,
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("visible index" in item for item in errors))

    def test_production_rejects_an_omitted_visible_index_row(self):
        storyboard, review = build_production_documents()
        altered = review.replace(
            "| SB-02-C05 — S03_SH04A | SB-02-C06 — S03_SH04B |\n",
            "",
            1,
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("visible index" in item for item in errors))

    def test_production_rejects_a_duplicated_visible_index_cell(self):
        storyboard, review = build_production_documents()
        altered = review.replace(
            "| SB-03-C01 — S03_SH04C | SB-03-C02 — S04_SH01 |",
            "| SB-03-C01 — S03_SH04C | SB-03-C01 — S03_SH04C |",
            1,
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("visible index" in item for item in errors))

    def test_production_rejects_a_falsified_sb04_index_cell(self):
        storyboard, review = build_production_documents()
        altered = review.replace(
            "| SB-04-C05 — S07_SH01 | SB-04-C06 — 审核栏／不生图 |",
            "| SB-04-C05 — S07_SH01 | SB-04-C06 — 审核栏／生图 |",
            1,
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("visible index" in item for item in errors))

    def test_rejects_a_shot_physically_under_the_wrong_board(self):
        storyboard, review = build_production_documents()
        board_start = review.index("## SB-02")
        first_cell_start = review.index("### 格 01", board_start)
        second_cell_start = review.index("### 格 02", first_cell_start)
        first_cell = review[first_cell_start:second_cell_start].replace(
            "CELL_TYPE: SHOT\n",
            "CELL_TYPE: SHOT\nBOARD_ID: SB-02\n",
            1,
        )
        altered = (
            review[:board_start]
            + first_cell
            + review[board_start:first_cell_start]
            + review[second_cell_start:]
        )
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(any("physical board section" in item for item in errors))

    def test_rejects_a_cell_before_every_board_section(self):
        first_board_start = self.review.index("## SB-T01")
        first_cell_start = self.review.index("### 格 01")
        second_cell_start = self.review.index("### 格 02")
        first_cell = self.review[first_cell_start:second_cell_start].replace(
            "CELL_TYPE: SHOT\n",
            "CELL_TYPE: SHOT\nBOARD_ID: SB-T01\n",
            1,
        )
        altered = (
            self.review[:first_board_start]
            + first_cell
            + self.review[first_board_start:first_cell_start]
            + self.review[second_cell_start:]
        )
        errors = validate_review(
            self.storyboard,
            altered,
            expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
            check_sha=False,
        )
        self.assertTrue(any("outside a board section" in item for item in errors))

    def test_rejects_missing_or_mismatched_board_declarations(self):
        cases = (
            self.review.replace("BOARD_ID: SB-T01", "BOARD_ID: SB-WRONG", 1),
            self.review.replace("BOARD_ID: SB-T01\n", "", 1),
        )
        for altered in cases:
            with self.subTest(review=altered):
                errors = validate_review(
                    self.storyboard,
                    altered,
                    expected_boards={"SB-T01": ("S01_SH01", "S01_SH02")},
                    check_sha=False,
                )
                self.assertTrue(any("board-level BOARD_ID" in item for item in errors))

    def test_qa_cell_must_be_sixth_in_the_physical_sb04_section(self):
        storyboard, review = build_production_documents()
        board_start = review.index("## SB-04")
        first_cell_start = review.index("### 格 01", board_start)
        board_header = review[board_start:first_cell_start]
        forged_cells = review[first_cell_start:].replace(
            "CELL_TYPE: SHOT\n",
            "CELL_TYPE: SHOT\nBOARD_ID: SB-04\n",
        ).replace(
            "CELL_TYPE: QA_ONLY\n",
            "CELL_TYPE: QA_ONLY\nBOARD_ID: SB-04\n",
        )
        altered = review[:board_start] + forged_cells + board_header
        errors = validate_review(storyboard, altered, check_sha=False)
        self.assertTrue(
            any(
                "QA_ONLY must belong to the SB-04 section at position 6" in item
                for item in errors
            )
        )

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

    def test_production_layout_rejects_a_duplicate_source_shot_id(self):
        storyboard, review = build_production_documents()
        second_block_start = storyboard.index("### 分镜 S01_SH02")
        duplicate_first_block = storyboard[:second_block_start]
        errors = validate_review(
            storyboard + duplicate_first_block,
            review,
            check_sha=False,
        )
        self.assertTrue(
            any("duplicate source SHOT_ID S01_SH01" in item for item in errors)
        )

    def test_production_layout_rejects_a_source_block_without_shot_id(self):
        storyboard, review = build_production_documents()
        altered = storyboard + "### 分镜 orphan\nSCENE: no identifier\n"
        errors = validate_review(altered, review, check_sha=False)
        self.assertTrue(
            any("source shot block 24 missing SHOT_ID" in item for item in errors)
        )

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
