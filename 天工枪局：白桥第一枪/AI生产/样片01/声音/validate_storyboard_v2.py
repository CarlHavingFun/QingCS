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

KEYFRAME_REQUIRED_FIELDS = (
    "SHOT_ID",
    "REFERENCE_IMAGES",
    "ANCHOR_REFS",
    "KEYFRAME_MOMENT",
    "VISIBLE_FACT_LOCK",
    "KEYFRAME_PROMPT",
    "KEYFRAME_NEGATIVE",
    "POST_TEXT",
    "FRAME_ROLE",
    "CONTINUITY_CHECK",
)

# This suffix is deliberately literal.  Keeping it stable makes accidental
# style drift visible before a prompt reaches an image model.
KEYFRAME_STYLE_SUFFIX = (
    "16:9 横屏，1920×1080，高完成度电影级 3D 国漫，真实人体比例与可触摸材质；"
    "非廉价游戏截图、非塑料皮肤、非二维平涂、非真人照片。"
)
KEYFRAME_NEGATIVE_REQUIRED_TERMS = (
    "文字",
    "水印",
    "字幕",
    "随机 UI",
    "廉价游戏截图",
    "塑料皮肤",
    "二维平涂",
    "真人照片",
)
KEYFRAME_MULTI_MOMENT_PATTERNS = (
    ("随后", re.compile(r"随后")),
    ("然后", re.compile(r"然后")),
    ("逐渐", re.compile(r"逐渐")),
    ("开始到结束", re.compile(r"开始到结束")),
    ("先…再…", re.compile(r"先[^。；;，,！？!?]{0,40}再")),
    ("同时…随后…", re.compile(r"同时[^。！？!?]{0,80}随后")),
    ("已…并…然后…", re.compile(r"已[^。！？!?]{0,80}并[^。！？!?]{0,80}然后")),
)
_KEYFRAME_PATH_REF_RE = re.compile(
    r"^(?P<anchor>[ABC]\d+)\s*->\s*(?P<path>/.*?)\s*"
    r"\[\s*SHA-256:\s*(?P<sha>[0-9a-fA-F]{64})\s*\]$"
)
_KEYFRAME_PENDING_REF_RE = re.compile(r"^待生成\s*[：:]\s*(?P<anchor>[ABC]\d+)$")
_KEYFRAME_QUOTED_TEXT_RE = re.compile(r"[“\"]([^“”\"]{2,})[”\"]")
_KEYFRAME_VISIBLE_NAME_RE = re.compile(
    r"周野|苏禾|江宁|唐夏|许安|韩平|陈默|赵雨|林溪|顾遥|罗叔|纪秋|夏满"
)
_ACTION_STATE_SPLIT_RE = re.compile(r"[，；。！？,;!?]")

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
# Chinese text is a Unicode word in Python, so ``\b`` does not delimit an
# anchor beside characters such as ``A3身份``.  ASCII lookarounds catch both
# prose-adjacent anchor IDs and the ordinary comma-delimited form.
_ANCHOR_RE = re.compile(r"(?<![A-Za-z0-9_])[ABC]\d+(?![A-Za-z0-9_])")
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
SILENCE_FUNCTION_CODES = frozenset(
    {
        "TACTICAL_OMISSION",
        "REACTION_HOLD",
        "ANOMALY_SILENCE",
        "ACTION_ONLY",
        "RESULT_ABSENCE",
    }
)
SPEAKING_SILENCE_FUNCTION = "NOT_APPLICABLE_DIALOGUE_PRESENT"
SILENCE_FUNCTION_ALLOWLIST = SILENCE_FUNCTION_CODES | {
    SPEAKING_SILENCE_FUNCTION
}
PROVENANCE_FIELDS = (
    "PROVENANCE_SOURCE_PATH",
    "PROVENANCE_SOURCE_SHA256",
    "PROVENANCE_DIALOGUE_PATH",
    "PROVENANCE_DIALOGUE_SHA256",
    "PROVENANCE_ANCHOR_PATH",
    "PROVENANCE_ANCHOR_SHA256",
)
KEYFRAME_PROVENANCE_FIELDS = PROVENANCE_FIELDS + (
    "PROVENANCE_STORYBOARD_PATH",
    "PROVENANCE_STORYBOARD_SHA256",
)
EXPECTED_PROVENANCE_PATHS = {
    "PROVENANCE_SOURCE_PATH": "正文/第01章_输掉Major后，我从民间赛重新开始.md",
    "PROVENANCE_DIALOGUE_PATH": "AI生产/样片01/声音/dialogue-lock-v2.json",
    "PROVENANCE_ANCHOR_PATH": "分镜/第01章_样片锚点清单_重制版.md",
}
S03_CAMERA_MOVE_CANONICAL = {
    "S03_SH04A": (
        "静态贴近三箱边缘，第三声落下后等待暗红木框完成，画面仍停在休息室轴线，"
        "不提前出现钟声与下坠。"
    ),
    "S03_SH04B": (
        "从暗红木框旁的耳罩慢慢下压，等待钟声尾音完整落下并停留至少0.3s后，"
        "桌面才开始下沉，镜头随后随周野身体失去支撑向下倾。"
    ),
    "S03_SH04C": (
        "低角度贴着键盘边缘跟拍周野下坠继续，继而让奖牌从键盘边缘滑向画外，"
        "镜头不追入地面，最后停在黑暗。"
    ),
}
VISIBLE_STORYBOARD_FIELDS = frozenset(
    {
        "SCENE",
        "LAYER",
        "CAMERA_SIZE",
        "CAMERA_MOVE",
        "ACTION_START",
        "ACTION_END",
        "COMPOSITION",
        "LIGHT",
        "CONTINUITY_IN",
        "CONTINUITY_OUT",
        "KEYFRAME_MOMENT",
        "NEGATIVE",
    }
)
PAPER_TEXT_SEMANTIC_TERMS = frozenset(
    {
        "纸",
        "表",
        "表格",
        "报名",
        "姓名",
        "名字",
        "落笔",
        "写",
        "登记",
        "第五格",
        "空格",
        "落款",
        "签名",
        "字样",
        "可读",
        "显示",
    }
)
_PAPER_TEXT_SEMANTIC_RE = re.compile(
    r"纸|表(?!面|情|演|示|明|达)|表格|报名|姓名|名字|落笔|"
    r"(?<!特)写|登记|第五格|空格|落款|签名|字样|可读|显示(?!器|屏|幕)"
)
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
_SCORE_NUMBER = r"[0-9０-９零〇一二三四五六七八九十百两壹贰叁肆伍陆柒捌玖拾佰]+"
SCORE_TEXT_PATTERN = re.compile(
    rf"{_SCORE_NUMBER}\s*(?:比|[-—–:：])\s*{_SCORE_NUMBER}"
)
UI_TEXT_PATTERNS = (SCORE_TEXT_PATTERN,)

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


def _load_keyframes(path: Path) -> tuple[str | None, list[str]]:
    try:
        return path.read_text(encoding="utf-8"), []
    except (OSError, UnicodeError) as exc:
        return None, [f"cannot read keyframes {path}: {exc}"]


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


def _parse_keyframes(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse one-line ``FIELD: value`` cards from the keyframe Markdown."""

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    current: dict[str, Any] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^###\s+(?:关键帧|KEYFRAME)\b", line):
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

        if field in current:
            errors.append(
                f"keyframe line {line_number} repeats field {field} for "
                f"{current.get('SHOT_ID') or '<blank shot>'}"
            )
        current[field] = value.strip()

    if current is not None:
        records.append(current)

    if not records:
        errors.append("keyframe file contains no SHOT_ID blocks")
    return records, errors


def _parse_anchor_catalog(text: str) -> dict[str, dict[str, str | None]]:
    """Extract anchor status, absolute master path, and locked SHA values."""

    metadata: dict[str, dict[str, str | None]] = {}
    headings = list(
        re.finditer(r"^###\s+([ABC]\d+)\s+.*$", text, flags=re.MULTILINE)
    )
    for index, heading in enumerate(headings):
        anchor_id = heading.group(1)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.start() : end]
        status_match = re.search(r"^- 母版状态：([^\n]+)", block, flags=re.MULTILINE)
        path_match = re.search(r"^- 母版路径：([^\n]+)", block, flags=re.MULTILINE)
        sha_match = re.search(
            r"^- 母版 SHA-256：`?([0-9a-fA-F]{64})`?",
            block,
            flags=re.MULTILINE,
        )

        status = status_match.group(1).strip() if status_match else None
        path: str | None = None
        if path_match is not None:
            path_value = path_match.group(1).strip()
            if not path_value.startswith("待生成"):
                path = path_value.strip("`").strip()

        metadata[anchor_id] = {
            "status": status,
            "path": path,
            "sha256": sha_match.group(1).lower() if sha_match else None,
        }
    return metadata


def _anchor_metadata_near_storyboard(path: Path) -> dict[str, dict[str, str | None]] | None:
    anchor_path = path.parent / "第01章_样片锚点清单_重制版.md"
    try:
        text = anchor_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    metadata = _parse_anchor_catalog(text)
    return metadata or None


def _parse_storyboard_header(text: str) -> tuple[dict[str, str], list[str]]:
    header: dict[str, str] = {}
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^###\s+(?:分镜|关键帧|KEYFRAME)\b", line):
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


def _validate_keyframe_provenance(
    keyframe_text: str,
    keyframe_path: Path,
    storyboard_text: str,
    storyboard_path: Path,
    *,
    source_path: Path,
    dialogue_path: Path,
) -> list[str]:
    """Validate all provenance locks declared in the keyframe document.

    Keyframe provenance is resolved from the keyframe file's project root.  The
    source, dialogue, and storyboard paths must resolve to the CLI arguments;
    the anchor path must resolve to the storyboard's associated anchor lock.
    Every declared digest is then recomputed from the resolved file.
    """

    header, errors = _parse_storyboard_header(keyframe_text)
    for field in KEYFRAME_PROVENANCE_FIELDS:
        if not header.get(field, ""):
            errors.append(f"keyframe header missing {field}")

    storyboard_header, storyboard_header_errors = _parse_storyboard_header(
        storyboard_text
    )
    errors.extend(
        f"associated storyboard provenance: {error}"
        for error in storyboard_header_errors
    )

    expected_paths: dict[str, Path | None] = {
        "PROVENANCE_SOURCE_PATH": source_path.resolve(),
        "PROVENANCE_DIALOGUE_PATH": dialogue_path.resolve(),
        "PROVENANCE_STORYBOARD_PATH": storyboard_path.resolve(),
    }
    anchor_relative_path = storyboard_header.get("PROVENANCE_ANCHOR_PATH", "")
    if anchor_relative_path:
        associated_anchor_path, anchor_path_error = _safe_project_path(
            storyboard_path, anchor_relative_path
        )
        if anchor_path_error is not None or associated_anchor_path is None:
            errors.append(
                "associated storyboard PROVENANCE_ANCHOR_PATH: "
                f"{anchor_path_error}"
            )
        else:
            expected_paths["PROVENANCE_ANCHOR_PATH"] = associated_anchor_path
    else:
        errors.append(
            "associated storyboard is missing PROVENANCE_ANCHOR_PATH; "
            "cannot resolve keyframe anchor provenance"
        )

    resolved: dict[str, Path] = {}
    for path_field in (
        "PROVENANCE_SOURCE_PATH",
        "PROVENANCE_DIALOGUE_PATH",
        "PROVENANCE_ANCHOR_PATH",
        "PROVENANCE_STORYBOARD_PATH",
    ):
        declared_path = header.get(path_field, "")
        if not declared_path:
            continue
        resolved_path, path_error = _safe_project_path(keyframe_path, declared_path)
        if path_error is not None or resolved_path is None:
            errors.append(f"keyframe {path_field}: {path_error}")
            continue
        resolved[path_field] = resolved_path
        expected_path = expected_paths.get(path_field)
        if expected_path is not None and resolved_path != expected_path:
            errors.append(
                f"keyframe {path_field} resolved path must match associated file: "
                f"expected {expected_path}, got {resolved_path}"
            )
        if not resolved_path.is_file():
            errors.append(f"keyframe {path_field} does not exist: {declared_path}")

    for path_field, hash_field in (
        ("PROVENANCE_SOURCE_PATH", "PROVENANCE_SOURCE_SHA256"),
        ("PROVENANCE_DIALOGUE_PATH", "PROVENANCE_DIALOGUE_SHA256"),
        ("PROVENANCE_ANCHOR_PATH", "PROVENANCE_ANCHOR_SHA256"),
        ("PROVENANCE_STORYBOARD_PATH", "PROVENANCE_STORYBOARD_SHA256"),
    ):
        expected_hash = header.get(hash_field, "")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            errors.append(
                f"keyframe {hash_field} must be a 64-character SHA-256 hex digest"
            )
        path = resolved.get(path_field)
        if path is not None and path.is_file():
            actual_hash = _sha256(path)
            if expected_hash.lower() != actual_hash:
                errors.append(
                    f"keyframe {hash_field} does not match "
                    f"{header.get(path_field, '')}: expected {actual_hash}, "
                    f"got {expected_hash}"
                )
    return errors


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

        for field in VISIBLE_STORYBOARD_FIELDS:
            value = record.get(field)
            if not isinstance(value, str):
                continue
            for pattern in UI_TEXT_PATTERNS:
                if pattern.search(value):
                    errors.append(
                        f"{location} {shot_id}.{field} contains exact UI/paper text; "
                        "move it to POST_TEXT"
                    )
                    break
            if "周野" in value and _PAPER_TEXT_SEMANTIC_RE.search(value):
                errors.append(
                    f"{location} {shot_id}.{field} contains paper text for 周野; "
                    "move exact paper text to POST_TEXT"
                )

        canonical_camera_move = S03_CAMERA_MOVE_CANONICAL.get(shot_id)
        if canonical_camera_move is not None and record.get("CAMERA_MOVE") != canonical_camera_move:
            errors.append(
                f"{location} {shot_id}.CAMERA_MOVE must equal its canonical S03 event sentence"
            )

        dialogue_entries, dialogue_errors = _parse_dialogue_field(record.get("DIALOGUE"))
        for dialogue_error in dialogue_errors:
            errors.append(f"{location} {shot_id}: {dialogue_error}")

        silence_function = record.get("SILENCE_FUNCTION")
        if not isinstance(silence_function, str) or not silence_function.strip():
            errors.append(
                f"{location} {shot_id}.SILENCE_FUNCTION must be a non-empty string"
            )
        elif silence_function not in SILENCE_FUNCTION_ALLOWLIST:
            errors.append(
                f"{location} {shot_id}.SILENCE_FUNCTION must be an allowed ASCII code: "
                f"{', '.join(sorted(SILENCE_FUNCTION_ALLOWLIST))}"
            )
        elif record.get("DIALOGUE") == NO_DIALOGUE_VALUE:
            if silence_function not in SILENCE_FUNCTION_CODES:
                errors.append(
                    f"{location} {shot_id}: silent shot SILENCE_FUNCTION must be a "
                    "silent-function code"
                )
        elif silence_function != SPEAKING_SILENCE_FUNCTION:
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


def _parse_keyframe_reference_images(
    value: Any,
) -> tuple[list[dict[str, str]], list[str]]:
    """Parse path-plus-SHA references and explicit pending-anchor markers."""

    if not isinstance(value, str) or not value.strip():
        return [], ["REFERENCE_IMAGES must be a non-empty string"]

    entries: list[dict[str, str]] = []
    errors: list[str] = []
    seen: set[str] = set()
    parts = [part.strip() for part in re.split(r"[;；]", value) if part.strip()]
    if not parts:
        return [], ["REFERENCE_IMAGES must contain at least one reference entry"]

    for part in parts:
        path_match = _KEYFRAME_PATH_REF_RE.fullmatch(part)
        if path_match is not None:
            entry = {
                "kind": "path",
                "anchor": path_match.group("anchor"),
                "path": path_match.group("path").strip(),
                "sha256": path_match.group("sha").lower(),
            }
        else:
            pending_match = _KEYFRAME_PENDING_REF_RE.fullmatch(part)
            if pending_match is None:
                errors.append(
                    "REFERENCE_IMAGES has malformed entry; use "
                    "<ANCHOR> -> /absolute/path [SHA-256: <digest>] or 待生成：<ANCHOR>: "
                    f"{part!r}"
                )
                continue
            entry = {
                "kind": "pending",
                "anchor": pending_match.group("anchor"),
            }

        anchor_id = entry["anchor"]
        if anchor_id in seen:
            errors.append(f"REFERENCE_IMAGES repeats anchor {anchor_id}")
        seen.add(anchor_id)
        entries.append(entry)
    return entries, errors


def _prompt_score_literals(value: str) -> list[str]:
    """Return score-like literals while allowing the required 16:9 canvas tag."""

    return [
        match.group(0)
        for match in SCORE_TEXT_PATTERN.finditer(value)
        if match.group(0).replace("：", ":") != "16:9"
    ]


def _action_state_fragments(value: str) -> list[str]:
    """Return meaningful source action clauses for prompt contradiction checks."""

    return [
        fragment.strip()
        for fragment in _ACTION_STATE_SPLIT_RE.split(value)
        if len(fragment.strip()) >= 8
    ]


def _keyframe_text_literals(storyboard_records: list[dict[str, Any]]) -> set[str]:
    literals: set[str] = set()
    for record in storyboard_records:
        dialogue_entries, _ = _parse_dialogue_field(record.get("DIALOGUE"))
        literals.update(
            entry["text"] for entry in dialogue_entries if entry.get("text")
        )
        post_text = record.get("POST_TEXT")
        if isinstance(post_text, str):
            literals.update(_KEYFRAME_QUOTED_TEXT_RE.findall(post_text))
    return {literal for literal in literals if len(literal) >= 2}


def validate_keyframes(
    keyframe_text: str,
    storyboard_text: str,
    *,
    anchor_metadata: dict[str, dict[str, str | None]] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate the source-locked, one-card-per-shot keyframe prompt file."""

    keyframe_records, errors = _parse_keyframes(keyframe_text)
    storyboard_records, storyboard_parse_errors = _parse_storyboard(storyboard_text)
    errors.extend(storyboard_parse_errors)
    if errors:
        return errors, {
            "records": keyframe_records,
            "keyframe_count": len(keyframe_records),
            "blocked_count": 0,
        }

    storyboard_ids = [
        str(record.get("SHOT_ID", "")).strip()
        for record in storyboard_records
        if str(record.get("SHOT_ID", "")).strip()
    ]
    keyframe_ids = [
        str(record.get("SHOT_ID", "")).strip()
        for record in keyframe_records
        if str(record.get("SHOT_ID", "")).strip()
    ]
    if keyframe_ids != storyboard_ids:
        expected_counter = Counter(storyboard_ids)
        actual_counter = Counter(keyframe_ids)
        missing = expected_counter - actual_counter
        extra = actual_counter - expected_counter
        if missing:
            errors.append(
                "keyframe ID set is missing shot(s): "
                + ", ".join(
                    f"{shot_id} x{count}" if count > 1 else shot_id
                    for shot_id, count in missing.items()
                )
            )
        if extra:
            errors.append(
                "keyframe ID set has unexpected shot(s): "
                + ", ".join(
                    f"{shot_id} x{count}" if count > 1 else shot_id
                    for shot_id, count in extra.items()
                )
            )
        if len(keyframe_ids) == len(set(keyframe_ids)):
            errors.append("keyframe IDs must be in the same order as storyboard SHOT_IDs")

    seen_keyframe_ids: dict[str, int] = {}
    storyboard_by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(storyboard_records, start=1):
        shot_id = record.get("SHOT_ID")
        if isinstance(shot_id, str) and shot_id.strip():
            storyboard_by_id.setdefault(shot_id.strip(), record)

    exact_literals = _keyframe_text_literals(storyboard_records)
    blocked_count = 0

    for index, record in enumerate(keyframe_records, start=1):
        location = f"keyframe shot {index}"
        shot_id = record.get("SHOT_ID")
        if not isinstance(shot_id, str) or not shot_id.strip():
            errors.append(f"{location} has an empty SHOT_ID")
            continue
        shot_id = shot_id.strip()
        record["SHOT_ID"] = shot_id
        if shot_id in seen_keyframe_ids:
            errors.append(
                f"{location} duplicates SHOT_ID {shot_id} from keyframe shot "
                f"{seen_keyframe_ids[shot_id]}"
            )
        else:
            seen_keyframe_ids[shot_id] = index

        missing = [field for field in KEYFRAME_REQUIRED_FIELDS if field not in record]
        if missing:
            errors.append(
                f"{location} {shot_id} missing field(s): {', '.join(missing)}"
            )
        empty = [
            field
            for field in KEYFRAME_REQUIRED_FIELDS
            if field in record and not str(record[field]).strip()
        ]
        if empty:
            errors.append(
                f"{location} {shot_id} has empty field(s): {', '.join(empty)}"
            )

        storyboard_record = storyboard_by_id.get(shot_id)
        if storyboard_record is None:
            errors.append(f"{location} {shot_id} has no matching storyboard shot")
            continue

        storyboard_refs = _ANCHOR_RE.findall(
            str(storyboard_record.get("ANCHOR_REFS", ""))
        )
        keyframe_refs = _ANCHOR_RE.findall(str(record.get("ANCHOR_REFS", "")))
        if len(keyframe_refs) != len(set(keyframe_refs)):
            errors.append(f"{location} {shot_id}.ANCHOR_REFS repeats an anchor")
        if keyframe_refs != storyboard_refs:
            errors.append(
                f"{location} {shot_id}.ANCHOR_REFS must exactly match storyboard: "
                f"expected {', '.join(storyboard_refs)}, got {', '.join(keyframe_refs)}"
            )

        for field in ("KEYFRAME_MOMENT", "POST_TEXT"):
            expected = str(storyboard_record.get(field, ""))
            actual = str(record.get(field, ""))
            if actual != expected:
                errors.append(
                    f"{location} {shot_id}.{field} must exactly match storyboard"
                )

        expected_continuity = (
            f"IN={storyboard_record.get('CONTINUITY_IN', '')}；"
            f"OUT={storyboard_record.get('CONTINUITY_OUT', '')}"
        )
        if record.get("CONTINUITY_CHECK") != expected_continuity:
            errors.append(
                f"{location} {shot_id}.CONTINUITY_CHECK must encode storyboard "
                "CONTINUITY_IN and CONTINUITY_OUT exactly"
            )

        visible_fact_lock = str(record.get("VISIBLE_FACT_LOCK", ""))
        expected_visible_fact_lock = str(
            storyboard_record.get("KEYFRAME_MOMENT", "")
        )
        if visible_fact_lock != expected_visible_fact_lock:
            errors.append(
                f"{location} {shot_id}.VISIBLE_FACT_LOCK must exactly match "
                "storyboard KEYFRAME_MOMENT"
            )

        reference_entries, reference_errors = _parse_keyframe_reference_images(
            record.get("REFERENCE_IMAGES")
        )
        errors.extend(f"{location} {shot_id}: {error}" for error in reference_errors)
        reference_ids = [entry["anchor"] for entry in reference_entries]
        if reference_ids != storyboard_refs:
            errors.append(
                f"{location} {shot_id}.REFERENCE_IMAGES anchors must exactly match "
                "ANCHOR_REFS"
            )

        pending_ids = {
            entry["anchor"] for entry in reference_entries if entry["kind"] == "pending"
        }
        if pending_ids:
            blocked_count += 1
            frame_role = str(record.get("FRAME_ROLE", ""))
            if "BLOCKED_BY_ANCHOR" not in frame_role:
                errors.append(
                    f"{location} {shot_id} must be marked BLOCKED_BY_ANCHOR for "
                    f"pending anchor(s): {', '.join(sorted(pending_ids))}"
                )
        elif "BLOCKED_BY_ANCHOR" in str(record.get("FRAME_ROLE", "")):
            errors.append(
                f"{location} {shot_id} must not be BLOCKED_BY_ANCHOR when all "
                "anchors are available"
            )

        if anchor_metadata is None:
            errors.append(
                f"{location} {shot_id}: anchor catalog is unavailable; cannot "
                "validate REFERENCE_IMAGES status"
            )
        else:
            for entry in reference_entries:
                anchor_id = entry["anchor"]
                metadata = anchor_metadata.get(anchor_id)
                if metadata is None:
                    errors.append(
                        f"{location} {shot_id}: REFERENCE_IMAGES contains unknown "
                        f"anchor {anchor_id}"
                    )
                    continue
                status = metadata.get("status")
                if status == "可用":
                    if entry["kind"] != "path":
                        errors.append(
                            f"{location} {shot_id}: available anchor {anchor_id} "
                            "must use an absolute master path, not 待生成"
                        )
                        continue
                    expected_path = metadata.get("path")
                    expected_sha = metadata.get("sha256")
                    actual_path = entry.get("path", "")
                    actual_sha = entry.get("sha256", "")
                    if not Path(actual_path).is_absolute():
                        errors.append(
                            f"{location} {shot_id}: reference path for {anchor_id} "
                            "must be absolute"
                        )
                    if expected_path is None or actual_path != expected_path:
                        errors.append(
                            f"{location} {shot_id}: reference path for {anchor_id} "
                            "does not match anchor catalog"
                        )
                    if expected_sha is None or actual_sha != expected_sha:
                        errors.append(
                            f"{location} {shot_id}: reference SHA for {anchor_id} "
                            "does not match anchor catalog lock"
                        )
                    path = Path(actual_path)
                    if not path.is_file():
                        errors.append(
                            f"{location} {shot_id}: reference image for {anchor_id} "
                            f"does not exist: {actual_path}"
                        )
                    elif expected_sha is not None:
                        actual_file_sha = _sha256(path)
                        if actual_file_sha != expected_sha:
                            errors.append(
                                f"{location} {shot_id}: reference image SHA for "
                                f"{anchor_id} does not match anchor catalog lock"
                            )
                elif status == "待生成":
                    if entry["kind"] != "pending":
                        errors.append(
                            f"{location} {shot_id}: pending anchor {anchor_id} "
                            "must be written as 待生成：<ANCHOR>; fake paths are forbidden"
                        )
                else:
                    errors.append(
                        f"{location} {shot_id}: anchor {anchor_id} has an invalid "
                        f"母版状态: {status!r}"
                    )

        prompt = str(record.get("KEYFRAME_PROMPT", ""))
        negative = str(record.get("KEYFRAME_NEGATIVE", ""))
        lock_count = prompt.count(visible_fact_lock) if visible_fact_lock else 0
        if lock_count != 1:
            errors.append(
                f"{location} {shot_id}.KEYFRAME_PROMPT must contain "
                "VISIBLE_FACT_LOCK exactly once"
            )
        prompt_without_fact_lock = prompt
        if visible_fact_lock and lock_count == 1:
            prompt_without_fact_lock = prompt.replace(visible_fact_lock, "", 1)

        # KEYFRAME_MOMENT and CONTINUITY_CHECK are independently source-locked
        # above.  Their anchor tokens are therefore checked against their exact
        # storyboard values, while free prose in KEYFRAME_PROMPT and FRAME_ROLE
        # must only use this card's declared ANCHOR_REFS.  Removing the exact
        # VISIBLE_FACT_LOCK before scanning lets the lock carry its source facts
        # without permitting an unbound token to be added to prompt prose.
        anchor_token_checks = (
            ("KEYFRAME_PROMPT", prompt_without_fact_lock, set(keyframe_refs)),
            (
                "KEYFRAME_MOMENT",
                str(record.get("KEYFRAME_MOMENT", "")),
                set(_ANCHOR_RE.findall(expected_visible_fact_lock)),
            ),
            ("FRAME_ROLE", str(record.get("FRAME_ROLE", "")), set(keyframe_refs)),
            (
                "CONTINUITY_CHECK",
                str(record.get("CONTINUITY_CHECK", "")),
                set(_ANCHOR_RE.findall(expected_continuity)),
            ),
        )
        for field_name, value, allowed_tokens in anchor_token_checks:
            undeclared_tokens = sorted(
                set(_ANCHOR_RE.findall(value)) - allowed_tokens
            )
            if undeclared_tokens:
                errors.append(
                    f"{location} {shot_id}.{field_name} contains undeclared "
                    "anchor token(s): " + ", ".join(undeclared_tokens)
                )
        for action_field in ("ACTION_START", "ACTION_END"):
            for action_fragment in _action_state_fragments(
                str(storyboard_record.get(action_field, ""))
            ):
                if action_fragment in prompt_without_fact_lock:
                    errors.append(
                        f"{location} {shot_id}.KEYFRAME_PROMPT repeats "
                        f"{action_field} state outside VISIBLE_FACT_LOCK: "
                        f"{action_fragment!r}"
                    )
        if prompt and not prompt.endswith(KEYFRAME_STYLE_SUFFIX):
            errors.append(
                f"{location} {shot_id}.KEYFRAME_PROMPT must end with the unified "
                "16:9/3D国漫 style suffix"
            )
        for term, pattern in KEYFRAME_MULTI_MOMENT_PATTERNS:
            if pattern.search(prompt):
                errors.append(
                    f"{location} {shot_id}.KEYFRAME_PROMPT contains multi-moment "
                    f"term {term!r}; describe one static instant only"
                )

        for field_name, value in (
            ("KEYFRAME_PROMPT", prompt_without_fact_lock),
            ("KEYFRAME_NEGATIVE", negative),
        ):
            for literal in sorted(exact_literals, key=len, reverse=True):
                if literal in value:
                    errors.append(
                        f"{location} {shot_id}.{field_name} leaks exact dialogue or "
                        f"POST_TEXT literal: {literal!r}"
                    )
            for score in _prompt_score_literals(value):
                errors.append(
                    f"{location} {shot_id}.{field_name} leaks exact score/UI text: "
                    f"{score!r}; keep it in POST_TEXT"
                )
            name_match = _KEYFRAME_VISIBLE_NAME_RE.search(value)
            if name_match is not None:
                errors.append(
                    f"{location} {shot_id}.{field_name} contains visible name "
                    f"{name_match.group(0)!r}; keep exact names in POST_TEXT"
                )

        missing_negative_terms = [
            term
            for term in KEYFRAME_NEGATIVE_REQUIRED_TERMS
            if term not in negative
        ]
        if missing_negative_terms:
            errors.append(
                f"{location} {shot_id}.KEYFRAME_NEGATIVE missing unified safety term(s): "
                + ", ".join(missing_negative_terms)
            )

    stats = {
        "records": keyframe_records,
        "keyframe_count": len(keyframe_records),
        "blocked_count": blocked_count,
        "storyboard_count": len(storyboard_records),
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
    parser.add_argument(
        "--keyframes",
        type=Path,
        help="optional source-locked keyframe prompt Markdown",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_text, source_errors = _load_source(args.source)
    payload, dialogue_errors = _load_dialogue(args.dialogue)
    errors = [*source_errors, *dialogue_errors]
    storyboard_stats: dict[str, Any] | None = None
    keyframe_stats: dict[str, Any] | None = None

    if source_text is not None and not dialogue_errors:
        errors.extend(validate(source_text, payload))

    if args.storyboard is not None:
        storyboard_text, storyboard_load_errors = _load_storyboard(args.storyboard)
        errors.extend(storyboard_load_errors)
        provenance_errors: list[str] = []
        anchor_ids: set[str] | None = None
        anchor_metadata: dict[str, dict[str, str | None]] | None = None
        if storyboard_text is not None and not storyboard_load_errors:
            provenance_errors, anchor_ids = _validate_provenance(
                storyboard_text,
                args.storyboard,
                source_path=args.source,
                dialogue_path=args.dialogue,
            )
            errors.extend(provenance_errors)
            anchor_metadata = _anchor_metadata_near_storyboard(args.storyboard)
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

        if args.keyframes is not None:
            keyframe_text, keyframe_load_errors = _load_keyframes(args.keyframes)
            errors.extend(keyframe_load_errors)
            if (
                keyframe_text is not None
                and storyboard_text is not None
                and not keyframe_load_errors
                and not storyboard_load_errors
            ):
                keyframe_provenance_errors = _validate_keyframe_provenance(
                    keyframe_text,
                    args.keyframes,
                    storyboard_text,
                    args.storyboard,
                    source_path=args.source,
                    dialogue_path=args.dialogue,
                )
                errors.extend(keyframe_provenance_errors)
                keyframe_errors, keyframe_stats = validate_keyframes(
                    keyframe_text,
                    storyboard_text,
                    anchor_metadata=anchor_metadata,
                )
                errors.extend(keyframe_errors)
    elif args.keyframes is not None:
        errors.append("--keyframes requires --storyboard so shot IDs can be source-locked")

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
        if keyframe_stats is not None:
            print(
                f"PASS: keyframes {keyframe_stats['keyframe_count']}/"
                f"{keyframe_stats['storyboard_count']} shot IDs; "
                f"{keyframe_stats['blocked_count']} BLOCKED_BY_ANCHOR pending-anchor cards."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
