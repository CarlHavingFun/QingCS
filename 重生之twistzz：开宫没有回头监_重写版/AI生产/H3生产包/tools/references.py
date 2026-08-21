from __future__ import annotations

from typing import Any, Mapping, Sequence


def detect_character_references(
    text: str,
    character_registry: Mapping[str, Any],
    *,
    protagonist_id: str | None = None,
    max_images: int = 9,
) -> list[dict[str, Any]]:
    """Return stable, deduplicated reference mappings in registry order."""
    characters = list(character_registry.get("characters", []))
    by_id = {item.get("id"): item for item in characters}
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(item: Mapping[str, Any] | None) -> None:
        if not item:
            return
        char_id = str(item.get("id", ""))
        reference_image = item.get("reference_image")
        if not char_id or not reference_image or char_id in seen or len(selected) >= max_images:
            return
        seen.add(char_id)
        selected.append(
            {
                "index": len(selected) + 1,
                "id": char_id,
                "name": item.get("name", char_id),
                "reference_image": reference_image,
                "appearance_lock": item.get("appearance_lock", ""),
            }
        )

    if protagonist_id:
        add(by_id.get(protagonist_id))
    for item in characters:
        aliases = [item.get("name", ""), *item.get("aliases", [])]
        if any(alias and alias in text for alias in aliases):
            add(item)
    return selected


def detect_scene_references(
    text: str,
    scene_registry: Mapping[str, Any] | None,
    *,
    max_scenes: int = 2,
) -> list[dict[str, Any]]:
    """Match stable scene IDs and textual visual locks, never collage references."""
    if not scene_registry:
        return []
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in scene_registry.get("scenes", []):
        scene_id = str(item.get("id", ""))
        aliases = [item.get("name", ""), *item.get("aliases", [])]
        if not scene_id or scene_id in seen:
            continue
        if any(alias and alias in text for alias in aliases):
            seen.add(scene_id)
            selected.append(
                {
                    "id": scene_id,
                    "name": item.get("name", scene_id),
                    "visual_lock": item.get("visual_lock", ""),
                    "continuity_lock": item.get("continuity_lock", ""),
                }
            )
            if len(selected) >= max_scenes:
                break
    return selected


def scene_lock_text(scenes: Sequence[Mapping[str, Any]]) -> str:
    if not scenes:
        return "场景锁定：使用分镜中的固定地点与空间锚点，不增造第二地点。"
    parts = []
    for item in scenes:
        lock = str(item.get("visual_lock", "")).strip()
        continuity = str(item.get("continuity_lock", "")).strip()
        detail = "；".join(value for value in (lock, continuity) if value)
        parts.append(f"{item.get('id')}（{item.get('name')}）：{detail}")
    return "场景锁定：" + " | ".join(parts)


def reference_mapping_text(references: Sequence[Mapping[str, Any]]) -> str:
    if not references:
        return "参考资产：无；本格使用文本生成。"
    lines = ["参考资产映射："]
    for index, item in enumerate(references, start=1):
        lines.append(
            f"- 参考图{index} = {item.get('id')}（{item.get('name')}），"
            "只锁定人物身份、脸型、发式和服装层级；不复制白底三视图排版。"
        )
    return "\n".join(lines)
