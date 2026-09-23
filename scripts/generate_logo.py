"""Generate Aveli's pixel-art README logo."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "aveli-logo.png"
SCALE = 6
WIDTH, HEIGHT = 160, 60
BG = "#0d1117"
RED = "#ef4d37"
RED_DARK = "#9f2e2a"
CREAM = "#f4e8d4"
MUTED = "#8b949e"

GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
}


def block(draw, x, y, color, size=2):
    draw.rectangle((x, y, x + size - 1, y + size - 1), fill=color)


def draw_mark(draw):
    # An observed page becomes indexed controls, then one selected target.
    cells = [
        (10, 11),
        (15, 8),
        (20, 11),
        (10, 16),
        (15, 16),
        (20, 16),
        (10, 21),
        (15, 24),
        (20, 21),
    ]
    for x, y in cells:
        block(draw, x, y, RED_DARK if (x, y) != (15, 16) else RED, 4)
    for x, y in ((13, 31), (17, 31), (21, 31), (17, 35)):
        block(draw, x, y, RED, 3)


def draw_wordmark(draw):
    x0, y0 = 38, 17
    for letter in "AVELI":
        for row, bits in enumerate(GLYPHS[letter]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    block(draw, x0 + col * 2, y0 + row * 2, CREAM)
        x0 += 14
    for x in range(39, 108, 4):
        block(draw, x, 36, RED if x < 67 else MUTED, 2)


image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)
draw_mark(draw)
draw_wordmark(draw)
image.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.Resampling.NEAREST).save(
    OUT, optimize=True
)
print(OUT)
