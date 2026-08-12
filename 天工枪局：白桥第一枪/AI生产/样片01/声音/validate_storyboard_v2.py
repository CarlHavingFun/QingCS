#!/usr/bin/env python3
"""Validate a chapter-1 dialogue lock against the novel source text.

The validator intentionally checks only source-locked dialogue and its timing
hints.  Advisory shot durations are not summed or treated as a hard runtime
contract.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "shot_id",
    "speaker_id",
    "delivery",
    "text",
    "source_line",
    "start_hint_s",
    "end_hint_s",
)


STORYBOARD_REQUIRED_FIELDS = (
    "SHOT_ID",
    "SCENE",
    "LAYER",
    "TIME_CODE",
    "ADVISORY_DURATION",
    "SOURCE_EXCERPT",
    "OBJECTIVE",
    "ANCHOR_REFS",
    "CAMERA_SIZE",
    "CAMERA_MOVE",
    "ACTION_START",
    "ACTION_END",
    "COMPOSITION",
    "LIGHT",
    "EMOTION",
    "DIALOGUE",
    "DIALOGUE_TIMING",
    "SOUND",
    "CONTINUITY_IN",
    "CONTINUITY_OUT",
    "POST_TEXT",
    "KEYFRAME_MOMENT",
    "NEGATIVE",
)

_SHOT_ID_RE = re.compile(r"^(S\d+_SH\d+)([A-Z])?$")
_DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:s|秒)?\s*$")
_TIME_CODE_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*s?\s*[-–—]\s*"
    r"(\d+(?:\.\d+)?)\s*s?\s*$"
)
_TIMING_INTERVAL_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*s?\s*[-–—]\s*"
    r"(\d+(?:\.\d+)?)\s*s?"
)
_ANCHOR_RE = re.compile(r"\b[ABC]\d+\b")
_QUOTED_TEXT_RE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _load_source(path: Path) -> tuple[str | None, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, [f"cannot read source {path}: {exc}"]
    return text, []


def _load_dialogue(path: Path) -> tuple[Any, list[str]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), []
    except json.JSONDecodeError as exc:
        return None, [
            f"dialogue JSON is invalid at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ]
    except (OSError, UnicodeError) as exc:
        return None, [f"cannot read dialogue {path}: {exc}"]


def _load_storyboard(path: Path) -> tuple[str | None, list[str]]:
    try:
        return path.read_text(encoding="utf-8"), []
    except (OSError, UnicodeError) as exc:
        return None, [f"cannot read storyboard {path}: {exc}"]


def _parse_storyboard(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse one-line ``FIELD: value`` cards from the storyboard Markdown."""

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    current: dict[str, Any] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^###\s+分镜\b", line):
            if current is not None:
                records.append(current)
            current = {"__line": line_number}
            continue

        field_match = re.match(r"^([A-Z][A-Z0-9_]*):\s*(.*)$", line)
        if not field_match:
            continue

        field, value = field_match.groups()
        if field == "SHOT_ID":
            if current is None:
                current = {"__line": line_number}
            elif "SHOT_ID" in current:
                records.append(current)
                current = {"__line": line_number}
            current["SHOT_ID"] = value.strip()
            continue

        if current is None:
            continue

        if field in current and field != "SHOT_ID":
            errors.append(
                f"storyboard line {line_number} repeats field {field} for "
                f"{current.get('SHOT_ID') or '<blank shot>'}"
            )
        current[field] = value.strip()

    if current is not None:
        records.append(current)

    if not records:
        errors.append("storyboard contains no SHOT_ID blocks")
    return records, errors


def _anchor_ids_near_storyboard(path: Path) -> set[str] | None:
    """Read the sibling anchor list when the normal project layout is present."""

    anchor_path = path.parent / "第01章_样片锚点清单_重制版.md"
    try:
        text = anchor_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    ids = set(re.findall(r"^###\s+([ABC]\d+)\s+", text, flags=re.MULTILINE))
    return ids or None


def _base_shot_id(shot_id: Any) -> str | None:
    if not isinstance(shot_id, str):
        return None
    match = _SHOT_ID_RE.fullmatch(shot_id.strip())
    return match.group(1) if match else None


def _parse_duration(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    match = _DURATION_RE.fullmatch(value)
    if match is None:
        return None
    duration = float(match.group(1))
    return duration if math.isfinite(duration) and duration > 0 else None


def _parse_time_code(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, str):
        return None
    match = _TIME_CODE_RE.fullmatch(value)
    if match is None:
        return None
    start = float(match.group(1))
    end = float(match.group(2))
    if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end < start:
        return None
    return start, end


def _parse_dialogue_intervals(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, str):
        return []
    return [
        (float(start), float(end))
        for start, end in _TIMING_INTERVAL_RE.findall(value)
    ]


def _locked_lines(payload: Any) -> tuple[list[Any] | None, list[str]]:
    if not isinstance(payload, dict):
        return None, ["dialogue JSON root must be an object"]

    records = payload.get("locked_lines")
    if not isinstance(records, list):
        return None, ["dialogue JSON must contain a list field named 'locked_lines'"]
    if not records:
        return records, ["locked_lines must not be empty"]
    return records, []


def validate(source_text: str, payload: Any) -> list[str]:
    """Return all validation errors for a parsed dialogue lock."""

    records, errors = _locked_lines(payload)
    if records is None:
        return errors

    source_lines = source_text.splitlines()
    previous_by_shot: dict[str, tuple[float, float, int]] = {}

    for index, record in enumerate(records, start=1):
        location = f"locked_lines[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{location} must be an object")
            continue

        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            errors.append(f"{location} missing field(s): {', '.join(missing)}")

        shot_id = record.get("shot_id")
        if not isinstance(shot_id, str) or not shot_id.strip():
            errors.append(f"{location}.shot_id must be a non-empty string")

        for field in ("speaker_id", "delivery"):
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{location}.{field} must be a non-empty string")

        text = record.get("text")
        text_is_valid = isinstance(text, str) and bool(text.strip())
        if not text_is_valid:
            errors.append(f"{location}.text must be a non-empty string")
        elif text not in source_text:
            errors.append(f"{location}.text not found verbatim in source: {text!r}")

        source_line = record.get("source_line")
        if isinstance(source_line, bool) or not isinstance(source_line, int):
            errors.append(f"{location}.source_line must be a positive integer")
        elif source_line < 1 or source_line > len(source_lines):
            errors.append(
                f"{location}.source_line is outside source: {source_line}"
            )
        elif text_is_valid and text not in source_lines[source_line - 1]:
            errors.append(
                f"{location}.source_line {source_line} does not contain text verbatim: {text!r}"
            )

        start = record.get("start_hint_s")
        end = record.get("end_hint_s")
        start_is_valid = _is_finite_number(start)
        end_is_valid = _is_finite_number(end)
        if not start_is_valid:
            errors.append(f"{location}.start_hint_s must be a finite number")
        elif start < 0:
            errors.append(f"{location}.start_hint_s must not be negative")
        if not end_is_valid:
            errors.append(f"{location}.end_hint_s must be a finite number")
        elif end < 0:
            errors.append(f"{location}.end_hint_s must not be negative")

        if start_is_valid and end_is_valid:
            if start > end:
                errors.append(
                    f"{location} time interval is inverted: {start:g}s > {end:g}s"
                )
            if isinstance(shot_id, str) and shot_id.strip():
                previous = previous_by_shot.get(shot_id)
                if previous is not None:
                    previous_start, previous_end, previous_index = previous
                    if start < previous_start or end < previous_end:
                        errors.append(
                            f"{location} time interval reverses {shot_id} entry "
                            f"locked_lines[{previous_index}]"
                        )
                previous_by_shot[shot_id] = (float(start), float(end), index)

    return errors


def validate_storyboard(
    storyboard_text: str,
    source_text: str,
    payload: Any,
    *,
    anchor_ids: set[str] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate shot cards, continuity, and source-locked dialogue mapping."""

    records, errors = _parse_storyboard(storyboard_text)
    if errors:
        return errors, {"records": records, "locked_count": 0}

    locked_records, lock_errors = _locked_lines(payload)
    if locked_records is None:
        return lock_errors, {"records": records, "locked_count": 0}
    errors.extend(lock_errors)

    seen_ids: dict[str, int] = {}
    previous_end: float | None = None
    durations: list[float] = []
    dialogue_by_base: dict[str, list[dict[str, Any]]] = {}

    for index, record in enumerate(records, start=1):
        location = f"storyboard shot {index}"
        shot_id = record.get("SHOT_ID")
        if not isinstance(shot_id, str) or not shot_id.strip():
            errors.append(f"{location} has an empty SHOT_ID")
            continue

        shot_id = shot_id.strip()
        record["SHOT_ID"] = shot_id
        if shot_id in seen_ids:
            errors.append(
                f"{location} duplicates SHOT_ID {shot_id} from storyboard shot "
                f"{seen_ids[shot_id]}"
            )
        else:
            seen_ids[shot_id] = index

        base_id = _base_shot_id(shot_id)
        if base_id is None:
            errors.append(
                f"{location}.SHOT_ID must match S##_SH## with an optional A-Z suffix: "
                f"{shot_id!r}"
            )
        else:
            dialogue_by_base.setdefault(base_id, []).append(record)

        missing = [field for field in STORYBOARD_REQUIRED_FIELDS if field not in record]
        if missing:
            errors.append(
                f"{location} {shot_id} missing field(s): {', '.join(missing)}"
            )
        empty = [
            field
            for field in STORYBOARD_REQUIRED_FIELDS
            if field in record and not str(record[field]).strip()
        ]
        if empty:
            errors.append(
                f"{location} {shot_id} has empty field(s): {', '.join(empty)}"
            )

        duration = _parse_duration(record.get("ADVISORY_DURATION"))
        if duration is None:
            errors.append(
                f"{location} {shot_id}.ADVISORY_DURATION must be a positive duration"
            )
        else:
            durations.append(duration)

        time_code = _parse_time_code(record.get("TIME_CODE"))
        if time_code is None:
            errors.append(
                f"{location} {shot_id}.TIME_CODE must be a non-negative start-end interval"
            )
        else:
            start, end = time_code
            if previous_end is not None and not math.isclose(
                start, previous_end, rel_tol=0.0, abs_tol=0.001
            ):
                errors.append(
                    f"{location} {shot_id}.TIME_CODE is not continuous: "
                    f"starts at {start:g}s after {previous_end:g}s"
                )
            previous_end = end
            if duration is not None and not math.isclose(
                end - start, duration, rel_tol=0.0, abs_tol=0.001
            ):
                errors.append(
                    f"{location} {shot_id} duration mismatch: TIME_CODE spans "
                    f"{end - start:g}s but ADVISORY_DURATION is {duration:g}s"
                )

        source_excerpt = record.get("SOURCE_EXCERPT")
        if isinstance(source_excerpt, str) and source_excerpt.strip():
            if source_excerpt not in source_text:
                errors.append(
                    f"{location} {shot_id}.SOURCE_EXCERPT not found verbatim in source: "
                    f"{source_excerpt!r}"
                )

        refs = record.get("ANCHOR_REFS")
        ref_ids = _ANCHOR_RE.findall(refs) if isinstance(refs, str) else []
        if not ref_ids:
            errors.append(f"{location} {shot_id}.ANCHOR_REFS must contain anchor IDs")
        elif anchor_ids is not None:
            unknown = sorted(set(ref_ids) - anchor_ids)
            if unknown:
                errors.append(
                    f"{location} {shot_id}.ANCHOR_REFS contains unknown anchor(s): "
                    f"{', '.join(unknown)}"
                )

        dialogue = record.get("DIALOGUE", "")
        if isinstance(dialogue, str) and "无台词" in dialogue:
            if "刻意沉默" not in dialogue:
                errors.append(
                    f"{location} {shot_id}.DIALOGUE must explain the deliberate silence"
                )
        elif isinstance(dialogue, str):
            quoted_texts = [
                first or second
                for first, second in _QUOTED_TEXT_RE.findall(dialogue)
            ]
            for quoted_text in quoted_texts:
                if quoted_text not in source_text:
                    errors.append(
                        f"{location} {shot_id}.DIALOGUE contains non-source quoted text: "
                        f"{quoted_text!r}"
                    )

        intervals = _parse_dialogue_intervals(record.get("DIALOGUE_TIMING"))
        if isinstance(dialogue, str) and "无台词" not in dialogue and not intervals:
            errors.append(
                f"{location} {shot_id}.DIALOGUE_TIMING must contain an interval"
            )
        if duration is not None:
            for start, end in intervals:
                if start < 0 or end < start or end > duration + 0.001:
                    errors.append(
                        f"{location} {shot_id}.DIALOGUE_TIMING interval "
                        f"{start:g}-{end:g}s exceeds shot duration {duration:g}s"
                    )

    # The base ID is the lock contract. A/B/C suffixes are a continuous group,
    # so one locked line can be placed in any one of those actual shot cards.
    mapped_count = 0
    for index, locked in enumerate(locked_records, start=1):
        location = f"locked_lines[{index}]"
        if not isinstance(locked, dict):
            continue
        base_id = _base_shot_id(locked.get("shot_id"))
        if base_id is None:
            continue
        group = dialogue_by_base.get(base_id, [])
        if not group:
            errors.append(
                f"{location} shot_id {locked.get('shot_id')!r} has no storyboard shot "
                f"group (expected base ID {base_id})"
            )
            continue

        text = locked.get("text")
        speaker_id = locked.get("speaker_id")
        delivery = locked.get("delivery")
        matches = [
            record
            for record in group
            if isinstance(record.get("DIALOGUE"), str)
            and isinstance(text, str)
            and text in record["DIALOGUE"]
        ]
        if not matches:
            errors.append(
                f"{location} {base_id} dialogue is not mapped verbatim to its storyboard "
                f"group: {text!r}"
            )
            continue

        mapped_count += 1
        matching_dialogue = "\n".join(record.get("DIALOGUE", "") for record in matches)
        if isinstance(speaker_id, str) and speaker_id not in matching_dialogue:
            errors.append(
                f"{location} {base_id} maps text to a shot without speaker "
                f"{speaker_id}: {text!r}"
            )
        if isinstance(delivery, str) and delivery not in matching_dialogue:
            errors.append(
                f"{location} {base_id} maps text to a shot without delivery "
                f"{delivery}: {text!r}"
            )

    stats = {
        "records": records,
        "shot_count": len(records),
        "base_shot_count": len(dialogue_by_base),
        "duration_total": sum(durations),
        "required_field_count": len(STORYBOARD_REQUIRED_FIELDS),
        "mapped_count": mapped_count,
        "locked_count": len(locked_records),
    }
    return errors, stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a source-locked chapter-1 dialogue JSON file."
    )
    parser.add_argument("--source", required=True, type=Path, help="source Markdown")
    parser.add_argument("--dialogue", required=True, type=Path, help="dialogue lock JSON")
    parser.add_argument(
        "--storyboard",
        type=Path,
        help="optional source-locked storyboard Markdown",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_text, source_errors = _load_source(args.source)
    payload, dialogue_errors = _load_dialogue(args.dialogue)
    errors = [*source_errors, *dialogue_errors]
    storyboard_stats: dict[str, Any] | None = None

    if source_text is not None and not dialogue_errors:
        errors.extend(validate(source_text, payload))

    if args.storyboard is not None:
        storyboard_text, storyboard_load_errors = _load_storyboard(args.storyboard)
        errors.extend(storyboard_load_errors)
        if (
            storyboard_text is not None
            and source_text is not None
            and not dialogue_errors
            and not storyboard_load_errors
        ):
            storyboard_errors, storyboard_stats = validate_storyboard(
                storyboard_text,
                source_text,
                payload,
                anchor_ids=_anchor_ids_near_storyboard(args.storyboard),
            )
            errors.extend(storyboard_errors)

    if errors:
        print(f"FAIL: dialogue lock validation failed ({len(errors)} error(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    records = payload["locked_lines"]
    print(
        f"PASS: {len(records)} locked dialogue lines; "
        f"all {len(records)} source texts match verbatim."
    )
    if storyboard_stats is not None:
        print(
            f"PASS: storyboard {storyboard_stats['shot_count']} actual shots / "
            f"{storyboard_stats['base_shot_count']} base beat groups; "
            f"advisory total {storyboard_stats['duration_total']:.1f}s; "
            f"field completeness {storyboard_stats['shot_count']}/"
            f"{storyboard_stats['shot_count']} shots across "
            f"{storyboard_stats['required_field_count']} required fields; "
            f"dialogue mapping {storyboard_stats['mapped_count']}/"
            f"{storyboard_stats['locked_count']}."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
