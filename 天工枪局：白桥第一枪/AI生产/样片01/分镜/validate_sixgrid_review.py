#!/usr/bin/env python3
"""Validate source-locked chapter-1 six-grid storyboard review boards."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


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

PRODUCTION_HEADERS = (
    ("SOURCE_STORYBOARD", "分镜/第01章_样片逐镜头分镜_重制版.md"),
    ("VISUAL_STYLE", "电影级 3D 国漫写实"),
    ("IMAGE_PRODUCTION", "STOPPED_PENDING_REVIEW"),
)

PRODUCTION_QA_LOCKS = (
    (
        "QA_DIALOGUE_LOCK",
        "给不给闪？／给。／你又想看两条线。／对。／右廊可能一个，距离不确定。"
        "近点先打，我补近点。右边出声再转。／收到。／右廊到门，半秒！／"
        "第五个人填谁？／也好。／第一枪，从白桥开始。",
    ),
    (
        "QA_SOUND_LOCK",
        "第一轮无胜利音乐；第二轮近点击杀完成并留反应空隙后才报右廊；"
        "结尾环境与拟音只保留夜雨、纸张与笔尖声；对白与内心声按 QA_DIALOGUE_LOCK。",
    ),
    (
        "QA_CONTINUITY_LOCK",
        "第一轮与第二轮复用同一乙仓轴线；第二轮严格先补近点再转右廊；"
        "报名桌仅在结尾使用。",
    ),
)

_PRODUCTION_HEADER_FIELDS = frozenset(
    {
        "SOURCE_STORYBOARD_SHA256",
        "BOARD_LAYOUT",
        "SHOT_FRAME_RATIO",
        *(field for field, _ in PRODUCTION_HEADERS),
    }
)
_PRODUCTION_BOARD_FIELDS = frozenset({"BOARD_ID"})
_PRODUCTION_SHOT_FIELDS = frozenset(
    {"CELL_ID", "CELL_TYPE", "SHOT_ID", "IMAGE_STATUS", *MIRRORED_FIELDS}
)
_PRODUCTION_QA_FIELDS = frozenset(
    {
        "CELL_ID",
        "CELL_TYPE",
        "GENERATE_IMAGE",
        "IMAGE_STATUS",
        *(field for field, _ in PRODUCTION_QA_LOCKS),
    }
)

_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s*(.*?)\s*$")
_STORYBOARD_HEADING_RE = re.compile(r"^###\s+分镜(?:\s|$)")
_BOARD_HEADING_RE = re.compile(r"^##\s+(SB-[A-Za-z0-9-]+)\s*$", re.MULTILINE)
_CELL_HEADING_RE = re.compile(r"^###\s+格(?:\s+(\d+))?\s*$")
_SECTION_BOARD_ID = "__SECTION_BOARD_ID"
_SECTION_CELL_POSITION = "__SECTION_CELL_POSITION"
_SECTION_CELL_HEADING_NUMBER = "__SECTION_CELL_HEADING_NUMBER"


def _parse_storyboard_internal(
    text: str,
) -> tuple[dict[str, dict[str, str]], list[str], int, int]:
    """Parse shots while retaining source block and ID declaration counts."""

    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    declaration_count = 0
    errors: list[str] = []

    def store_current() -> None:
        if current is not None:
            blocks.append(dict(current))

    for line_number, line in enumerate(text.splitlines(), start=1):
        if _STORYBOARD_HEADING_RE.match(line):
            store_current()
            current = {}
            continue

        match = _FIELD_RE.match(line)
        if match is None:
            continue
        field, value = match.groups()
        if field == "SHOT_ID":
            declaration_count += 1
            if current is not None and current.get("SHOT_ID"):
                store_current()
                current = {}
            elif current is None:
                current = {}
        if current is not None:
            if field != "SHOT_ID" and field in current:
                errors.append(
                    f"source line {line_number} shot block {len(blocks) + 1} "
                    f"repeats {field}"
                )
            current[field] = value

    store_current()
    shots: dict[str, dict[str, str]] = {}
    for block_number, block in enumerate(blocks, start=1):
        shot_id = block.get("SHOT_ID", "")
        if not shot_id:
            errors.append(f"source shot block {block_number} missing SHOT_ID")
            continue
        if shot_id in shots:
            errors.append(
                f"duplicate source SHOT_ID {shot_id} at shot block {block_number}"
            )
        shots[shot_id] = block

    return shots, errors, len(blocks), declaration_count


def parse_storyboard(text: str) -> dict[str, dict[str, str]]:
    """Parse storyboard shot blocks keyed by ``SHOT_ID``."""

    shots, _, _, _ = _parse_storyboard_internal(text)
    return shots


def _parse_review_internal(
    text: str,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse review data with non-overridable physical section metadata."""

    header: dict[str, str] = {}
    cells: list[dict[str, str]] = []
    board_id = ""
    board_cell_position = 0
    current: dict[str, str] | None = None

    for line in text.splitlines():
        board_match = _BOARD_HEADING_RE.match(line)
        if board_match is not None:
            if current is not None:
                cells.append(current)
                current = None
            board_id = board_match.group(1)
            board_cell_position = 0
            continue

        cell_match = _CELL_HEADING_RE.match(line)
        if cell_match is not None:
            if current is not None:
                cells.append(current)
            if board_id:
                board_cell_position += 1
            current = {
                _SECTION_BOARD_ID: board_id,
                _SECTION_CELL_POSITION: str(board_cell_position),
                _SECTION_CELL_HEADING_NUMBER: cell_match.group(1) or "",
            }
            continue

        field_match = _FIELD_RE.match(line)
        if field_match is None:
            continue
        field, value = field_match.groups()
        if current is None:
            if not board_id:
                header[field] = value
        else:
            current[field] = value

    if current is not None:
        cells.append(current)
    return header, cells


def parse_review(text: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse review headers and cells, exposing physical board membership."""

    header, internal_cells = _parse_review_internal(text)
    cells: list[dict[str, str]] = []
    for internal_cell in internal_cells:
        cell = {
            field: value
            for field, value in internal_cell.items()
            if not field.startswith("__")
        }
        cell["BOARD_ID"] = internal_cell[_SECTION_BOARD_ID]
        cells.append(cell)
    return header, cells


def _duplicate_review_field_errors(text: str) -> list[str]:
    """Report repeated fields within one header, board, or cell scope."""

    errors: list[str] = []
    seen: set[str] = set()
    scope = "header"
    for line_number, line in enumerate(text.splitlines(), start=1):
        board_match = _BOARD_HEADING_RE.match(line)
        if board_match is not None:
            seen = set()
            scope = board_match.group(1)
            continue
        if _CELL_HEADING_RE.match(line):
            seen = set()
            scope = line.strip()
            continue
        field_match = _FIELD_RE.match(line)
        if field_match is None:
            continue
        field = field_match.group(1)
        if field in seen:
            errors.append(f"review line {line_number} {scope} repeats {field}")
        seen.add(field)
    return errors


def _board_declaration_errors(text: str) -> list[str]:
    """Require each board heading to have one matching board-level ID."""

    sections: list[tuple[str, str | None]] = []
    current_section_index: int | None = None
    inside_cell = False
    for line in text.splitlines():
        board_match = _BOARD_HEADING_RE.match(line)
        if board_match is not None:
            sections.append((board_match.group(1), None))
            current_section_index = len(sections) - 1
            inside_cell = False
            continue
        if _CELL_HEADING_RE.match(line):
            inside_cell = True
            continue
        field_match = _FIELD_RE.match(line)
        if (
            field_match is not None
            and current_section_index is not None
            and not inside_cell
            and field_match.group(1) == "BOARD_ID"
        ):
            section_id, _ = sections[current_section_index]
            sections[current_section_index] = (section_id, field_match.group(2))

    errors: list[str] = []
    for section_id, declared_id in sections:
        if declared_id != section_id:
            errors.append(
                f"{section_id} board-level BOARD_ID must be {section_id!r}, "
                f"got {declared_id!r}"
            )
    return errors


def _expected_production_index_lines(
    board_id: str,
    shot_ids: tuple[str, ...],
) -> tuple[str, ...]:
    """Build the exact visible 2×3 index required above one production board."""

    labels = list(shot_ids)
    if board_id == "SB-04":
        labels.append("审核栏／不生图")

    lines = ["| 左列 | 右列 |", "|---|---|"]
    for row_start in range(0, 6, 2):
        left_number = row_start + 1
        right_number = row_start + 2
        lines.append(
            f"| {board_id}-C{left_number:02d} — {labels[row_start]} "
            f"| {board_id}-C{right_number:02d} — {labels[row_start + 1]} |"
        )
    return tuple(lines)


def _production_index_errors(text: str) -> list[str]:
    """Validate each board's visible Markdown index before its BOARD_ID line."""

    headings = list(_BOARD_HEADING_RE.finditer(text))
    indexes: dict[str, tuple[str, ...]] = {}
    for position, heading in enumerate(headings):
        section_end = (
            headings[position + 1].start()
            if position + 1 < len(headings)
            else len(text)
        )
        section_body = text[heading.end():section_end]
        declaration = re.search(
            r"^BOARD_ID:\s*.*$",
            section_body,
            flags=re.MULTILINE,
        )
        index_text = (
            section_body[:declaration.start()]
            if declaration is not None
            else section_body
        )
        indexes[heading.group(1)] = tuple(
            line.strip() for line in index_text.splitlines() if line.strip()
        )

    errors: list[str] = []
    for board_id, shot_ids in EXPECTED_BOARDS.items():
        expected_lines = _expected_production_index_lines(board_id, shot_ids)
        actual_lines = indexes.get(board_id, ())
        if actual_lines != expected_lines:
            errors.append(
                f"{board_id} visible index must be exactly {expected_lines!r}, "
                f"got {actual_lines!r}"
            )
    return errors


def _production_schema_errors(text: str) -> list[str]:
    """Reject fields outside the exact production schema in every scope."""

    errors: list[str] = []
    scope = "header"
    board_id = ""
    cell_fields: list[tuple[int, str, str]] | None = None

    def validate_cell() -> None:
        if cell_fields is None:
            return
        values = {field: value for _, field, value in cell_fields}
        cell_type = values.get("CELL_TYPE", "")
        cell_id = values.get("CELL_ID", "<unknown cell>")
        if cell_type == "SHOT":
            allowed_fields = _PRODUCTION_SHOT_FIELDS
            scope_name = "SHOT"
        elif cell_type == "QA_ONLY":
            allowed_fields = _PRODUCTION_QA_FIELDS
            scope_name = "QA_ONLY"
        else:
            allowed_fields = _PRODUCTION_SHOT_FIELDS | _PRODUCTION_QA_FIELDS
            scope_name = "cell"
        for line_number, field, _ in cell_fields:
            if field not in allowed_fields:
                errors.append(
                    f"production {scope_name} cell {cell_id} field {field} "
                    f"is not allowed at review line {line_number}"
                )

    for line_number, line in enumerate(text.splitlines(), start=1):
        board_match = _BOARD_HEADING_RE.match(line)
        if board_match is not None:
            validate_cell()
            cell_fields = None
            scope = "board"
            board_id = board_match.group(1)
            continue

        if _CELL_HEADING_RE.match(line):
            validate_cell()
            cell_fields = []
            scope = "cell"
            continue

        field_match = _FIELD_RE.match(line)
        if field_match is None:
            continue
        field, value = field_match.groups()
        if scope == "header":
            if field not in _PRODUCTION_HEADER_FIELDS:
                errors.append(
                    f"production header field {field} is not allowed "
                    f"at review line {line_number}"
                )
        elif scope == "board":
            if field not in _PRODUCTION_BOARD_FIELDS:
                errors.append(
                    f"production board {board_id} field {field} is not allowed "
                    f"at review line {line_number}"
                )
        else:
            assert cell_fields is not None
            cell_fields.append((line_number, field, value))

    validate_cell()
    return errors


def validate_review(
    storyboard_text: str,
    review_text: str,
    expected_boards: dict[str, tuple[str, ...]] = EXPECTED_BOARDS,
    check_sha: bool = True,
) -> list[str]:
    """Return every violation found in a six-grid review document."""

    errors = _duplicate_review_field_errors(review_text)
    errors.extend(_board_declaration_errors(review_text))
    (
        source_shots,
        source_parse_errors,
        source_block_count,
        source_declaration_count,
    ) = _parse_storyboard_internal(storyboard_text)
    errors.extend(source_parse_errors)
    header, cells = _parse_review_internal(review_text)
    is_production = expected_boards == EXPECTED_BOARDS
    boards_to_validate = EXPECTED_BOARDS if is_production else expected_boards

    for field, required_value in (
        ("BOARD_LAYOUT", "PORTRAIT_2X3"),
        ("SHOT_FRAME_RATIO", "9:16"),
    ):
        actual_value = header.get(field)
        if actual_value != required_value:
            errors.append(
                f"{field} must be {required_value!r}, got {actual_value!r}"
            )

    if check_sha:
        expected_sha = hashlib.sha256(storyboard_text.encode("utf-8")).hexdigest()
        actual_sha = header.get("SOURCE_STORYBOARD_SHA256")
        if actual_sha != expected_sha:
            errors.append(
                "SOURCE_STORYBOARD_SHA256 must match the source storyboard: "
                f"expected {expected_sha}, got {actual_sha!r}"
            )

    board_order = tuple(
        match.group(1)
        for line in review_text.splitlines()
        if (match := _BOARD_HEADING_RE.match(line)) is not None
    )
    required_board_order = tuple(boards_to_validate)
    if board_order != required_board_order:
        errors.append(
            f"board order must be {required_board_order!r}, got {board_order!r}"
        )

    cells_by_board: dict[str, list[dict[str, str]]] = {}
    for cell in cells:
        physical_board_id = cell[_SECTION_BOARD_ID]
        if not physical_board_id:
            errors.append(
                f"{cell.get('CELL_ID', '<unknown cell>')} appears outside a board section"
            )
        else:
            required_heading_number = f"{int(cell[_SECTION_CELL_POSITION]):02d}"
            actual_heading_number = cell[_SECTION_CELL_HEADING_NUMBER]
            if actual_heading_number != required_heading_number:
                errors.append(
                    f"{physical_board_id} cell heading number must be "
                    f"{required_heading_number!r}, got {actual_heading_number!r}"
                )
        if "BOARD_ID" in cell:
            errors.append(
                f"{cell.get('CELL_ID', '<unknown cell>')} cell BOARD_ID cannot change "
                f"its physical board section {physical_board_id!r}"
            )
        cells_by_board.setdefault(physical_board_id, []).append(cell)

    if is_production:
        errors.extend(_production_schema_errors(review_text))
        for field, required_value in PRODUCTION_HEADERS:
            actual_value = header.get(field)
            if actual_value != required_value:
                errors.append(
                    f"{field} must be {required_value!r}, got {actual_value!r}"
                )
        errors.extend(_production_index_errors(review_text))
        if source_block_count != 23:
            errors.append(
                "source storyboard must contain exactly 23 shots (shot blocks), "
                f"got {source_block_count}"
            )
        if source_declaration_count != 23:
            errors.append(
                "source storyboard must contain exactly 23 SHOT_ID declarations, "
                f"got {source_declaration_count}"
            )
        if len(cells) != 24:
            errors.append(
                f"production review must contain exactly 24 cells, got {len(cells)}"
            )
        all_shot_cells = [cell for cell in cells if cell.get("CELL_TYPE") == "SHOT"]
        if len(all_shot_cells) != 23:
            errors.append(
                "production review must contain exactly 23 SHOT cards, "
                f"got {len(all_shot_cells)}"
            )
        unique_shot_ids = {cell.get("SHOT_ID", "") for cell in all_shot_cells}
        if len(unique_shot_ids) != 23:
            errors.append(
                "production review must contain exactly 23 unique SHOT_ID values, "
                f"got {len(unique_shot_ids)}"
            )
        qa_cells = [cell for cell in cells if cell.get("CELL_TYPE") == "QA_ONLY"]
        if len(qa_cells) != 1:
            errors.append(
                "production review must contain exactly one QA_ONLY cell, "
                f"got {len(qa_cells)}"
            )
        else:
            qa_cell = qa_cells[0]
            if (
                qa_cell[_SECTION_BOARD_ID] != "SB-04"
                or qa_cell[_SECTION_CELL_POSITION] != "6"
            ):
                errors.append(
                    "QA_ONLY must belong to the SB-04 section at position 6, "
                    f"got section {qa_cell[_SECTION_BOARD_ID]!r} position "
                    f"{qa_cell[_SECTION_CELL_POSITION]}"
                )
            qa_required_fields = (
                ("CELL_ID", "SB-04-C06"),
                ("GENERATE_IMAGE", "NO"),
                ("IMAGE_STATUS", "NOT_APPLICABLE"),
            ) + PRODUCTION_QA_LOCKS
            for field, required_value in qa_required_fields:
                actual_value = qa_cell.get(field)
                if actual_value != required_value:
                    errors.append(
                        f"QA_ONLY {field} must be {required_value!r}, "
                        f"got {actual_value!r}"
                    )

    for board_id, expected_shots in boards_to_validate.items():
        board_cells = cells_by_board.get(board_id, [])
        for position, cell in enumerate(board_cells, start=1):
            required_cell_id = f"{board_id}-C{position:02d}"
            if cell.get("CELL_ID") != required_cell_id:
                errors.append(
                    f"{board_id} cell {position} CELL_ID must be "
                    f"{required_cell_id!r}, got {cell.get('CELL_ID')!r}"
                )
        shot_cells = [
            cell for cell in board_cells if cell.get("CELL_TYPE") == "SHOT"
        ]
        actual_shots = tuple(cell.get("SHOT_ID", "") for cell in shot_cells)
        if actual_shots != expected_shots:
            errors.append(
                f"{board_id} shot order must be {expected_shots!r}, "
                f"got {actual_shots!r}"
            )

        for cell in shot_cells:
            shot_id = cell.get("SHOT_ID", "")
            if cell.get("IMAGE_STATUS") != "NOT_GENERATED":
                errors.append(
                    f"{board_id} {shot_id} IMAGE_STATUS must be "
                    f"'NOT_GENERATED', got {cell.get('IMAGE_STATUS')!r}"
                )
            source = source_shots.get(shot_id)
            if source is None:
                errors.append(f"{board_id} references unknown source shot {shot_id!r}")
                continue
            for field in MIRRORED_FIELDS:
                source_has_field = field in source
                review_has_field = field in cell
                if not source_has_field:
                    errors.append(
                        f"source storyboard shot {shot_id} missing {field}"
                    )
                if not review_has_field:
                    errors.append(f"review SHOT card {shot_id} missing {field}")
                if (
                    source_has_field
                    and review_has_field
                    and cell[field] != source[field]
                ):
                    errors.append(
                        f"{board_id} {shot_id} {field} must exactly match source: "
                        f"expected {source[field]!r}, got {cell[field]!r}"
                    )

    return errors


def build_parser() -> argparse.ArgumentParser:
    """Build the fixed two-path command-line interface."""

    parser = argparse.ArgumentParser(
        description="Validate a source-locked chapter-1 six-grid review."
    )
    parser.add_argument("--storyboard", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the validator without modifying either input document."""

    args = build_parser().parse_args(argv)
    try:
        storyboard_text = args.storyboard.read_text(encoding="utf-8")
        review_text = args.review.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read input: {exc}", file=sys.stderr)
        return 1

    errors = validate_review(storyboard_text, review_text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "PASS: 4 boards / 24 cells / 23 source-locked shots / "
        "1 QA-only cell; frame ratio 9:16; image production stopped."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
