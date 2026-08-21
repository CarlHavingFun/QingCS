from __future__ import annotations

import re
from typing import Any

from .common import H3_FIELD_NAMES, STANDARD_FIELD_NAMES, H3ValidationError


def _clean(value: str | None) -> str:
    if not value:
        return ""
    lines = [line.rstrip().rstrip("\\") for line in value.strip().splitlines()]
    return " ".join(line.strip() for line in lines if line.strip())


def _extract_bold_field(block: str, label: str) -> str:
    pattern = re.compile(
        rf"(?ms)^\s*-\s*\*\*{re.escape(label)}：\*\*\s*(.*?)"
        rf"(?=^\s*-\s*\*\*[^\n]+?：\*\*|^\s*---\s*$|\Z)"
    )
    match = pattern.search(block)
    return _clean(match.group(1)) if match else ""


def _extract_h3_fields(block: str) -> dict[str, str]:
    names = "|".join(H3_FIELD_NAMES)
    pattern = re.compile(
        rf"(?ms)^\s*\*\*({names}):\*\*\s*(.*?)"
        rf"(?=^\s*\*\*(?:{names}):\*\*|^\s*---\s*$|\Z)"
    )
    return {match.group(1): _clean(match.group(2)) for match in pattern.finditer(block)}


def _extract_timeline(action: str) -> list[dict[str, str]]:
    dash = r"[—–-]"
    patterns = (
        ("00:00-00:03", rf"0{dash}3秒：\s*(.*?)(?=3{dash}10秒：)"),
        ("00:03-00:10", rf"3{dash}10秒：\s*(.*?)(?=10{dash}15秒：)"),
        ("00:10-00:15", rf"10{dash}15秒：\s*(.*)$"),
    )
    timeline: list[dict[str, str]] = []
    for time_range, pattern in patterns:
        match = re.search(pattern, action, flags=re.S)
        if match:
            timeline.append({"range": time_range, "action": _clean(match.group(1))})
    return timeline


def parse_storyboard_text(
    text: str, source: str = "<memory>", *, strict: bool = True
) -> dict[str, Any]:
    """Parse either the chapter-1 director format or chapter-2–44 six-field format."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    chapter_match = re.search(r"(?m)^#\s*第(\d+)章\s*(.*)$", normalized)
    if not chapter_match:
        raise H3ValidationError(f"{source}: missing '# 第NN章' title")

    chapter = int(chapter_match.group(1))
    raw_title = chapter_match.group(2).strip()
    title = re.sub(r"[｜|].*$", "", raw_title).strip()
    title = title.replace("十格分镜", "").replace("｜电影级十格压缩分镜", "").strip(" 《》")

    heading_pattern = re.compile(r"(?m)^##\s*第(\d+)格(?:[｜|]\s*(.*?))?\s*$")
    matches = list(heading_pattern.finditer(normalized))
    grids: list[dict[str, Any]] = []

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        block = normalized[start:end].strip()
        grid_number = int(match.group(1))
        heading_detail = _clean(match.group(2))
        h3_fields = _extract_h3_fields(block)
        has_standard_fields = "**景别/地点：**" in block

        if has_standard_fields:
            fields = {name: _extract_bold_field(block, name) for name in STANDARD_FIELD_NAMES}
            missing = [name for name, value in fields.items() if not value]
            if strict and missing:
                raise H3ValidationError(
                    f"{source}: grid {grid_number} missing fields: {', '.join(missing)}"
                )
            timeline = _extract_timeline(fields["画面动作"])
            if strict and len(timeline) != 3:
                raise H3ValidationError(
                    f"{source}: grid {grid_number} must contain 0—3, 3—10 and 10—15 second phases"
                )
            grid = {
                "grid": grid_number,
                "title": heading_detail or f"第{grid_number}格",
                "format": "standard",
                "location": fields["景别/地点"],
                "action": fields["画面动作"],
                "dialogue_audio": fields["台词或音效"],
                "cs_facts": fields["CS信息"],
                "relationship_beat": fields["关系/笑点"],
                "spatial_anchors": fields["空间锚点"],
                "timeline": timeline,
                "h3_fields": h3_fields,
                "raw_text": block,
            }
        else:
            if strict and not h3_fields:
                raise H3ValidationError(
                    f"{source}: grid {grid_number} is neither six-field format nor embedded H3 format"
                )
            grid = {
                "grid": grid_number,
                "title": heading_detail or f"第{grid_number}格",
                "format": "director",
                "story_task": _extract_bold_field(block, "叙事任务"),
                "audience_question": _extract_bold_field(block, "观众问题"),
                "dialogue_audio": _extract_bold_field(block, "台词")
                or _extract_bold_field(block, "声音与剪辑"),
                "continuity": _extract_bold_field(block, "连续性与通过标准"),
                "h3_fields": h3_fields,
                "timeline": [],
                "raw_text": block,
            }
        grids.append(grid)

    if strict:
        numbers = [grid["grid"] for grid in grids]
        if numbers != list(range(1, 11)):
            raise H3ValidationError(
                f"{source}: expected exactly grids 1-10, got {numbers or 'none'}"
            )

    return {"chapter": chapter, "title": title, "source": source, "grids": grids}
