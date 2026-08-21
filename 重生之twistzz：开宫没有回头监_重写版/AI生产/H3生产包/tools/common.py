from __future__ import annotations

ALLOWED_RATIOS = {"adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"}
H3_FIELD_NAMES = (
    "SCENE",
    "ACTION",
    "CAMERA",
    "BLOCKING",
    "PERFORMANCE",
    "AUDIO",
    "TRANSITION",
    "CONTINUITY",
    "NEGATIVE",
)
STANDARD_FIELD_NAMES = (
    "景别/地点",
    "画面动作",
    "台词或音效",
    "CS信息",
    "关系/笑点",
    "空间锚点",
)


class H3ValidationError(ValueError):
    """Raised when a storyboard or H3 job violates a hard production rule."""
