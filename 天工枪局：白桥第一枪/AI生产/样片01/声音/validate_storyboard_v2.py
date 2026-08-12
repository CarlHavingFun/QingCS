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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a source-locked chapter-1 dialogue JSON file."
    )
    parser.add_argument("--source", required=True, type=Path, help="source Markdown")
    parser.add_argument("--dialogue", required=True, type=Path, help="dialogue lock JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_text, source_errors = _load_source(args.source)
    payload, dialogue_errors = _load_dialogue(args.dialogue)
    errors = [*source_errors, *dialogue_errors]

    if source_text is not None and not dialogue_errors:
        errors.extend(validate(source_text, payload))

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
