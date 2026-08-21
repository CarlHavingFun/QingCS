from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "overlays"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"


def layer(name: str, items: list[tuple[str, tuple[int, int], int, str]]) -> None:
    image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for text, position, size, anchor in items:
        font = ImageFont.truetype(FONT, size)
        draw.text(
            position,
            text,
            font=font,
            fill=(244, 248, 255, 236),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 175),
            anchor=anchor,
        )
    image.save(OUT / name)


layer("major_state.png", [("16:18   4v3", (1850, 60), 38, "ra")])
layer("defuse_state.png", [("拆除：5 秒", (70, 60), 38, "la")])
layer("runner_up.png", [("16:19   亚军", (960, 82), 54, "ma")])
