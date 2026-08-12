#!/usr/bin/env python3
"""Validate the chapter-1 source lock and the complete storyboard gate.

Dialogue is a closed structured multiset, while shot durations remain advisory
values that are summed for reporting and checked only for local performance
capacity and continuous timecodes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
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
    "SILENCE_FUNCTION",
    "DIALOGUE_TIMING",
    "SOUND",
    "CONTINUITY_IN",
    "CONTINUITY_OUT",
    "POST_TEXT",
    "KEYFRAME_MOMENT",
    "NEGATIVE",
)

_SHOT_ID_RE = re.compile(r"^(S\d+_SH\d+)([ABC])?$")
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
_DIALOGUE_ENTRY_RE = re.compile(
    r"(?P<speaker>[A-Z][A-Z0-9_]*)（(?P<delivery>[a-z][a-z0-9_]*)）："
    r"“(?P<text>[^“”]+)”"
)
_TIMING_ENTRY_RE = re.compile(
    r"(?P<speaker>[A-Z][A-Z0-9_]*)\|(?P<delivery>[a-z][a-z0-9_]*)\|"
    r"(?P<start>\d+(?:\.\d+)?)s?-(?P<end>\d+(?:\.\d+)?)s?\|"
    r"before=(?P<before>\d+(?:\.\d+)?)\|after=(?P<after>\d+(?:\.\d+)?)"
)
_EVENT_ENTRY_RE = re.compile(
    r"(?P<event>[a-z][a-z0-9_]*)=(?P<time>\d+(?:\.\d+)?)s?"
)

NO_DIALOGUE_VALUE = "无台词／刻意沉默"
NO_DIALOGUE_PREFIX = f"{NO_DIALOGUE_VALUE}："
SPEAKING_SILENCE_FUNCTION = "不适用（本镜有台词）"
PROVENANCE_FIELDS = (
    "PROVENANCE_SOURCE_PATH",
    "PROVENANCE_SOURCE_SHA256",
    "PROVENANCE_DIALOGUE_PATH",
    "PROVENANCE_DIALOGUE_SHA256",
    "PROVENANCE_ANCHOR_PATH",
    "PROVENANCE_ANCHOR_SHA256",
)
EXPECTED_PROVENANCE_PATHS = {
    "PROVENANCE_SOURCE_PATH": "正文/第01章_输掉Major后，我从民间赛重新开始.md",
    "PROVENANCE_DIALOGUE_PATH": "AI生产/样片01/声音/dialogue-lock-v2.json",
    "PROVENANCE_ANCHOR_PATH": "分镜/第01章_样片锚点清单_重制版.md",
}
SPEECH_RATE_BY_DELIVERY = {
    "off_screen_radio": 4.0,
    "recorded_replay": 4.0,
    "off_screen_inner_voice": 4.0,
    "on_screen": 4.0,
}
TACTICAL_TERMS = (
    "A1",
    "烟里",
    "给不给闪",
    "右廊",
    "近点",
    "半秒",
    "收到",
    "三箱",
    "补枪",
    "跳台",
    "包边",
    "脚步",
    "两条线",
    "准星",
    "开枪",
    "出声",
)
UI_TEXT_PATTERNS = (
    re.compile(r"\d+\s*[:：]\s*\d+"),
    re.compile(r"七比五|十六比十九|十六比十八"),
    re.compile(r"(?:报名表|第五格|空格).{0,20}[“\"]周野[”\"]"),
    re.compile(r"[“\"]周野[”\"].{0,20}(?:报名表|第五格|空格)"),
    re.compile(r"(?:纸|表格|报名表|第五格|空格).{0,20}(?:写|填|书写).{0,20}[“\"]?周野"),
    re.compile(r"[“\"]?周野[”\"]?.{0,20}(?:写|填|书写).{0,20}(?:纸|表格|报名表|第五格|空格)"),
)

_SPEECH_CHARACTER_RE = re.compile(
    r"[A-Za-z0-9\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
_PAUSE_WEIGHTS = {
    "，": 0.2,
    ",": 0.2,
    "、": 0.2,
    "。": 0.35,
    "！": 0.35,
    "!": 0.35,
    "？": 0.35,
    "?": 0.35,
    "…": 0.35,
    "；": 0.3,
    ";": 0.3,
    "：": 0.3,
    ":": 0.3,
}


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


def _parse_storyboard_header(text: str) -> tuple[dict[str, str], list[str]]:
    header: dict[str, str] = {}
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^###\s+分镜\b", line):
            break
        match = re.match(r"^(PROVENANCE_[A-Z0-9_]+):\s*(.*?)\s*$", line)
        if match is None:
            continue
        field, value = match.groups()
        if field in header:
            errors.append(f"storyboard header line {line_number} repeats {field}")
        header[field] = value
    return header, errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_project_path(storyboard_path: Path, relative_path: str) -> tuple[Path | None, str | None]:
    if not relative_path or Path(relative_path).is_absolute():
        return None, "provenance path must be relative to the project root"
    project_root = storyboard_path.resolve().parent.parent
    candidate = (project_root / relative_path).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError:
        return None, "provenance path escapes the project root"
    return candidate, None


def _validate_provenance(
    storyboard_text: str,
    storyboard_path: Path,
    *,
    source_path: Path | None = None,
    dialogue_path: Path | None = None,
) -> tuple[list[str], set[str] | None]:
    header, errors = _parse_storyboard_header(storyboard_text)
    for field in PROVENANCE_FIELDS:
        value = header.get(field, "")
        if not value:
            errors.append(f"storyboard header missing {field}")

    resolved: dict[str, Path] = {}
    for path_field, expected_path in EXPECTED_PROVENANCE_PATHS.items():
        actual_path = header.get(path_field, "")
        if actual_path and actual_path != expected_path:
            errors.append(
                f"{path_field} must be the project-relative path {expected_path!r}, "
                f"got {actual_path!r}"
            )
        if not actual_path:
            continue
        path, path_error = _safe_project_path(storyboard_path, actual_path)
        if path_error is not None or path is None:
            errors.append(f"{path_field}: {path_error}")
            continue
        resolved[path_field] = path
        if not path.is_file():
            errors.append(f"{path_field} does not exist: {actual_path}")

    for argument_name, path_field, argument_path in (
        ("--source", "PROVENANCE_SOURCE_PATH", source_path),
        ("--dialogue", "PROVENANCE_DIALOGUE_PATH", dialogue_path),
    ):
        declared_path = resolved.get(path_field)
        if argument_path is None or declared_path is None:
            continue
        resolved_argument = argument_path.resolve()
        if resolved_argument != declared_path:
            errors.append(
                f"{argument_name} resolved path must match {path_field}: "
                f"expected {declared_path}, got {resolved_argument}"
            )

    for path_field, hash_field in (
        ("PROVENANCE_SOURCE_PATH", "PROVENANCE_SOURCE_SHA256"),
        ("PROVENANCE_DIALOGUE_PATH", "PROVENANCE_DIALOGUE_SHA256"),
        ("PROVENANCE_ANCHOR_PATH", "PROVENANCE_ANCHOR_SHA256"),
    ):
        path = resolved.get(path_field)
        expected_hash = header.get(hash_field, "")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            errors.append(f"{hash_field} must be a 64-character SHA-256 hex digest")
        if path is not None and path.is_file():
            actual_hash = _sha256(path)
            if expected_hash.lower() != actual_hash:
                errors.append(
                    f"{hash_field} does not match {header.get(path_field, '')}: "
                    f"expected {actual_hash}, got {expected_hash}"
                )

    anchor_ids: set[str] | None = None
    anchor_path = resolved.get("PROVENANCE_ANCHOR_PATH")
    if anchor_path is not None and anchor_path.is_file():
        try:
            anchor_text = anchor_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read anchor catalog {anchor_path}: {exc}")
        else:
            anchor_ids = set(
                re.findall(r"^###\s+([ABC]\d+)\s+", anchor_text, flags=re.MULTILINE)
            )
            if not anchor_ids:
                errors.append("anchor catalog parsed successfully but contains no anchor IDs")
    else:
        errors.append("anchor catalog is unavailable; cannot validate ANCHOR_REFS")
    return errors, anchor_ids


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


def _consume_structured_entries(
    value: str,
    pattern: re.Pattern[str],
    label: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    position = 0
    while position < len(value):
        while position < len(value) and value[position] in " \t；;":
            position += 1
        if position >= len(value):
            break
        match = pattern.match(value, position)
        if match is None:
            errors.append(
                f"{label} has malformed structured entry near {value[position:position + 40]!r}"
            )
            break
        entries.append(match.groupdict())
        position = match.end()
        if position < len(value) and value[position] not in " \t；;":
            errors.append(
                f"{label} has unexpected separator near {value[position:position + 40]!r}"
            )
            break
    return entries, errors


def _parse_dialogue_field(value: Any) -> tuple[list[dict[str, str]], list[str]]:
    if not isinstance(value, str) or not value.strip():
        return [], ["DIALOGUE must be a non-empty string"]
    value = value.strip()
    if value == NO_DIALOGUE_VALUE:
        return [], []
    if value.startswith(NO_DIALOGUE_VALUE):
        return [], [
            f"no-dialogue DIALOGUE must equal {NO_DIALOGUE_VALUE!r} exactly"
        ]
    if "无台词" in value:
        return [], [f"no-dialogue DIALOGUE must start with {NO_DIALOGUE_PREFIX!r}"]
    entries, errors = _consume_structured_entries(
        value, _DIALOGUE_ENTRY_RE, "DIALOGUE"
    )
    return entries, errors


def _parse_timing_field(value: Any) -> tuple[list[dict[str, str]], list[str]]:
    if not isinstance(value, str) or not value.strip():
        return [], ["DIALOGUE_TIMING must be a non-empty string"]
    value = value.strip()
    if value.startswith(NO_DIALOGUE_PREFIX):
        remainder = value[len(NO_DIALOGUE_PREFIX):]
        if _TIMING_ENTRY_RE.search(remainder):
            return [], ["no-dialogue DIALOGUE_TIMING must not contain a speaking interval"]
        return [], []
    entries, errors = _consume_structured_entries(
        value, _TIMING_ENTRY_RE, "DIALOGUE_TIMING"
    )
    return entries, errors


def _parse_event_timing(value: Any) -> tuple[dict[str, float], list[str]]:
    if not isinstance(value, str) or not value.strip():
        return {}, ["EVENT_TIMING must be a non-empty string"]
    events: dict[str, float] = {}
    errors: list[str] = []
    position = 0
    while position < len(value):
        while position < len(value) and value[position] in " \t；;":
            position += 1
        if position >= len(value):
            break
        match = _EVENT_ENTRY_RE.match(value, position)
        if match is None:
            errors.append(
                f"EVENT_TIMING has malformed event near {value[position:position + 40]!r}"
            )
            break
        event_name = match.group("event")
        if event_name in events:
            errors.append(f"EVENT_TIMING repeats event {event_name}")
        events[event_name] = float(match.group("time"))
        position = match.end()
        if position < len(value) and value[position] not in " \t；;":
            errors.append(
                f"EVENT_TIMING has unexpected separator near {value[position:position + 40]!r}"
            )
            break
    return events, errors


def _speech_rate(text: str, delivery: str) -> float:
    if any(term in text for term in TACTICAL_TERMS):
        return 5.0
    return SPEECH_RATE_BY_DELIVERY.get(delivery, 4.0)


def _speech_character_count(text: str) -> int:
    """Count only Han characters, ASCII letters, and digits as spoken units."""

    return len(_SPEECH_CHARACTER_RE.findall(text))


def _punctuation_pause_budget(text: str) -> float:
    """Add conservative pauses without treating punctuation as spoken units."""

    return sum(_PAUSE_WEIGHTS.get(character, 0.0) for character in text)


def _minimum_speech_duration(text: str, delivery: str) -> float:
    return (
        _speech_character_count(text) / _speech_rate(text, delivery)
        + _punctuation_pause_budget(text)
    )


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
    """Validate shot cards, continuity, and a closed dialogue lock."""

    records, errors = _parse_storyboard(storyboard_text)
    if errors:
        return errors, {"records": records, "locked_count": 0}

    locked_records, lock_errors = _locked_lines(payload)
    if locked_records is None:
        return lock_errors, {"records": records, "locked_count": 0}
    errors.extend(lock_errors)
    if anchor_ids is None:
        errors.append("anchor catalog is unavailable; cannot validate ANCHOR_REFS")

    seen_ids: dict[str, int] = {}
    previous_end: float | None = None
    durations: list[float] = []
    dialogue_by_base: dict[str, list[dict[str, Any]]] = {}
    actual_dialogue: list[tuple[str, str, str, str]] = []
    timing_by_shot: dict[str, list[dict[str, Any]]] = {}
    event_by_shot: dict[str, dict[str, float]] = {}
    timecode_by_shot: dict[str, tuple[float, float]] = {}

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
                f"{location}.SHOT_ID must match S##_SH## with an optional A/B/C suffix: "
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
            timecode_by_shot[shot_id] = time_code
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

        for field, value in record.items():
            if field.startswith("__") or field.startswith("PROVENANCE_"):
                continue
            if field in {
                "POST_TEXT",
                "DIALOGUE",
                "DIALOGUE_TIMING",
                "TIME_CODE",
                "EVENT_TIMING",
            }:
                continue
            if not isinstance(value, str):
                continue
            for pattern in UI_TEXT_PATTERNS:
                if pattern.search(value):
                    errors.append(
                        f"{location} {shot_id}.{field} contains exact UI/paper text; "
                        "move it to POST_TEXT"
                    )
                    break

        dialogue_entries, dialogue_errors = _parse_dialogue_field(record.get("DIALOGUE"))
        for dialogue_error in dialogue_errors:
            errors.append(f"{location} {shot_id}: {dialogue_error}")

        silence_function = record.get("SILENCE_FUNCTION")
        if not isinstance(silence_function, str) or not silence_function.strip():
            errors.append(
                f"{location} {shot_id}.SILENCE_FUNCTION must be a non-empty string"
            )
        elif record.get("DIALOGUE") == NO_DIALOGUE_VALUE:
            if silence_function == SPEAKING_SILENCE_FUNCTION:
                errors.append(
                    f"{location} {shot_id}: silent shot SILENCE_FUNCTION must "
                    "state a non-empty narrative function"
                )
        elif dialogue_entries and silence_function != SPEAKING_SILENCE_FUNCTION:
            errors.append(
                f"{location} {shot_id}: speaking shot SILENCE_FUNCTION must equal "
                f"{SPEAKING_SILENCE_FUNCTION!r}"
            )

        timing_entries, timing_errors = _parse_timing_field(
            record.get("DIALOGUE_TIMING")
        )
        for timing_error in timing_errors:
            errors.append(f"{location} {shot_id}: {timing_error}")
        timing_by_shot[shot_id] = []

        if not dialogue_entries:
            if timing_entries:
                errors.append(
                    f"{location} {shot_id}: silent DIALOGUE cannot have speaking timing entries"
                )
        elif len(dialogue_entries) != len(timing_entries):
            errors.append(
                f"{location} {shot_id}: DIALOGUE has {len(dialogue_entries)} entries but "
                f"DIALOGUE_TIMING has {len(timing_entries)} entries"
            )

        if dialogue_entries and timing_entries:
            previous_timing: dict[str, Any] | None = None
            for entry_index, (dialogue_entry, timing_entry) in enumerate(
                zip(dialogue_entries, timing_entries), start=1
            ):
                if (
                    dialogue_entry.get("speaker") != timing_entry.get("speaker")
                    or dialogue_entry.get("delivery") != timing_entry.get("delivery")
                ):
                    errors.append(
                        f"{location} {shot_id}: DIALOGUE_TIMING entry {entry_index} "
                        "does not match DIALOGUE speaker/delivery"
                    )

                start = float(timing_entry["start"])
                end = float(timing_entry["end"])
                before = float(timing_entry["before"])
                after = float(timing_entry["after"])
                timing_entry["start_s"] = start
                timing_entry["end_s"] = end
                timing_entry["before_s"] = before
                timing_entry["after_s"] = after
                timing_by_shot[shot_id].append(timing_entry)

                if start < 0 or end <= start:
                    errors.append(
                        f"{location} {shot_id}: DIALOGUE_TIMING entry {entry_index} "
                        "must have a positive interval"
                    )
                if duration is not None and end > duration + 0.001:
                    errors.append(
                        f"{location} {shot_id}: DIALOGUE_TIMING entry {entry_index} "
                        f"ends at {end:g}s beyond shot duration {duration:g}s"
                    )
                if not 0.3 <= before <= 0.8:
                    errors.append(
                        f"{location} {shot_id}: entry {entry_index} before reaction "
                        f"must be 0.3-0.8s, got {before:g}s"
                    )
                if not 0.3 <= after <= 0.8:
                    errors.append(
                        f"{location} {shot_id}: entry {entry_index} after reaction "
                        f"must be 0.3-0.8s, got {after:g}s"
                    )

                minimum = _minimum_speech_duration(
                    dialogue_entry["text"], dialogue_entry["delivery"]
                )
                if end - start + 0.001 < minimum:
                    errors.append(
                        f"{location} {shot_id}: entry {entry_index} speech window "
                        f"{end - start:.2f}s is shorter than conservative minimum "
                        f"{minimum:.2f}s for {len(dialogue_entry['text'])} characters"
                    )

                if previous_timing is None:
                    if start + 0.001 < before:
                        errors.append(
                            f"{location} {shot_id}: first speech entry starts before "
                            "its before-reaction window ends"
                        )
                else:
                    gap = start - float(previous_timing["end_s"])
                    required_gap = max(
                        float(previous_timing["after_s"]), before
                    )
                    if gap + 0.001 < required_gap:
                        errors.append(
                            f"{location} {shot_id}: entries {entry_index - 1} and "
                            f"{entry_index} have only {gap:.2f}s reaction gap; "
                            f"need {required_gap:.2f}s"
                        )
                previous_timing = timing_entry

                if base_id is not None:
                    actual_dialogue.append(
                        (
                            base_id,
                            dialogue_entry["speaker"],
                            dialogue_entry["delivery"],
                            dialogue_entry["text"],
                        )
                    )
            if duration is not None and timing_by_shot[shot_id]:
                final_timing = timing_by_shot[shot_id][-1]
                if duration - final_timing["end_s"] + 0.001 < final_timing["after_s"]:
                    errors.append(
                        f"{location} {shot_id}: final speech entry leaves less than its "
                        "required after-reaction window"
                    )

        if "EVENT_TIMING" in record:
            events, event_errors = _parse_event_timing(record["EVENT_TIMING"])
            for event_error in event_errors:
                errors.append(f"{location} {shot_id}: {event_error}")
            if duration is not None:
                for event_name, event_time in events.items():
                    if event_time < 0 or event_time > duration + 0.001:
                        errors.append(
                            f"{location} {shot_id}: event {event_name} at {event_time:g}s "
                            f"is outside shot duration {duration:g}s"
                        )
            event_by_shot[shot_id] = events

    expected_dialogue: Counter[tuple[str, str, str, str]] = Counter()
    expected_dialogue_sequence: list[tuple[str, str, str, str]] = []
    for index, locked in enumerate(locked_records, start=1):
        if not isinstance(locked, dict):
            continue
        base_id = _base_shot_id(locked.get("shot_id"))
        if base_id is None:
            errors.append(
                f"locked_lines[{index}].shot_id must match S##_SH## with an optional A/B/C suffix"
            )
            continue
        dialogue_item = (
            base_id,
            str(locked.get("speaker_id", "")),
            str(locked.get("delivery", "")),
            str(locked.get("text", "")),
        )
        expected_dialogue[dialogue_item] += 1
        expected_dialogue_sequence.append(dialogue_item)

    actual_counter = Counter(actual_dialogue)
    missing_dialogue = expected_dialogue - actual_counter
    extra_dialogue = actual_counter - expected_dialogue
    for item, count in missing_dialogue.items():
        errors.append(f"dialogue closed set missing {count} occurrence(s): {item!r}")
    for item, count in extra_dialogue.items():
        errors.append(f"dialogue closed set has {count} unexpected occurrence(s): {item!r}")

    if actual_dialogue != expected_dialogue_sequence:
        mismatch_index = 0
        for mismatch_index, (actual, expected) in enumerate(
            zip(actual_dialogue, expected_dialogue_sequence), start=1
        ):
            if actual != expected:
                errors.append(
                    f"dialogue sequence mismatch at position {mismatch_index}: "
                    f"expected {expected!r}, got {actual!r}"
                )
                break
        else:
            errors.append(
                "dialogue sequence length mismatch: "
                f"expected {len(expected_dialogue_sequence)}, got {len(actual_dialogue)}"
            )

    def global_event(shot_id: str, event_name: str) -> float | None:
        events = event_by_shot.get(shot_id)
        time_code = timecode_by_shot.get(shot_id)
        if events is None or event_name not in events or time_code is None:
            return None
        return time_code[0] + events[event_name]

    required_events = {
        "S03_SH04A": ("wood_frame_complete",),
        "S03_SH04B": ("bell_start", "bell_tail_end", "fall_start"),
        "S03_SH04C": ("fall_continues", "medal_slide_start"),
        "S06_SH01B": ("near_kill_complete", "dialogue_start"),
    }
    for shot_id, event_names in required_events.items():
        events = event_by_shot.get(shot_id)
        if events is None:
            errors.append(f"{shot_id} requires EVENT_TIMING for causal ordering")
            continue
        for event_name in event_names:
            if event_name not in events:
                errors.append(f"{shot_id} EVENT_TIMING missing {event_name}")

    wood_frame = global_event("S03_SH04A", "wood_frame_complete")
    bell_start = global_event("S03_SH04B", "bell_start")
    bell_tail_end = global_event("S03_SH04B", "bell_tail_end")
    fall_start = global_event("S03_SH04B", "fall_start")
    fall_continues = global_event("S03_SH04C", "fall_continues")
    medal_global = global_event("S03_SH04C", "medal_slide_start")
    if (
        wood_frame is not None
        and bell_start is not None
        and wood_frame > bell_start
    ):
        errors.append("S03 event order requires wood_frame_complete <= bell_start")
    if (
        bell_start is not None
        and bell_tail_end is not None
        and bell_start > bell_tail_end
    ):
        errors.append("S03 event order requires bell_start <= bell_tail_end")
    if bell_tail_end is not None and fall_start is not None:
        if fall_start - bell_tail_end < 0.3:
            errors.append(
                "S03_SH04B requires at least 0.3s after bell_tail_end before fall_start"
            )
    if (
        fall_start is not None
        and fall_continues is not None
        and fall_start > fall_continues
    ):
        errors.append("S03 event order requires fall_start <= fall_continues")
    if (
        fall_continues is not None
        and medal_global is not None
        and fall_continues > medal_global
    ):
        errors.append("S03 event order requires fall_continues <= medal_slide_start")

    s06_events = event_by_shot.get("S06_SH01B")
    s06_timing = timing_by_shot.get("S06_SH01B", [])
    if s06_events is not None and s06_timing:
        near_kill = s06_events.get("near_kill_complete")
        dialogue_start = s06_events.get("dialogue_start")
        actual_start = s06_timing[0]["start_s"]
        if dialogue_start is not None and actual_start + 0.001 < dialogue_start:
            errors.append(
                "S06_SH01B DIALOGUE_TIMING starts before its dialogue_start event"
            )
        if (
            near_kill is not None
            and dialogue_start is not None
            and dialogue_start < near_kill + 0.3
        ):
            errors.append(
                "S06_SH01B needs at least 0.3s after near_kill_complete before the call"
            )

    stats = {
        "records": records,
        "shot_count": len(records),
        "base_shot_count": len(dialogue_by_base),
        "duration_total": sum(durations),
        "required_field_count": len(STORYBOARD_REQUIRED_FIELDS),
        "mapped_count": sum((expected_dialogue & actual_counter).values()),
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
        provenance_errors: list[str] = []
        anchor_ids: set[str] | None = None
        if storyboard_text is not None and not storyboard_load_errors:
            provenance_errors, anchor_ids = _validate_provenance(
                storyboard_text,
                args.storyboard,
                source_path=args.source,
                dialogue_path=args.dialogue,
            )
            errors.extend(provenance_errors)
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
                anchor_ids=anchor_ids,
            )
            errors.extend(storyboard_errors)

    if errors:
        failure_kind = (
            "storyboard validation" if args.storyboard is not None else "dialogue lock validation"
        )
        print(f"FAIL: {failure_kind} failed ({len(errors)} error(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    records = payload["locked_lines"]
    if storyboard_stats is None:
        print(
            f"DIALOGUE-ONLY PASS: {len(records)} locked dialogue lines; "
            f"all {len(records)} source texts match verbatim."
        )
    else:
        print(
            f"PASS: {len(records)} locked dialogue lines; "
            f"all {len(records)} source texts match verbatim."
        )
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
