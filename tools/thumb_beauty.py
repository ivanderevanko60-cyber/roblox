"""Cinematic thumbnail: one beautiful photo, restrained type, room to breathe.

python tools/thumb_beauty.py <photo> <out.jpg> "Head line" [options]
  --sub TEXT          small line under the headline
  --font anton|bebas|playfair|inter
  --size N            headline size in px (default: auto)
  --pos bl|bc|tl|tc   corner for the text block (default bl)
  --crop 0..1         vertical centre of the 16:9 crop (0 = top, default 0.5)
  --scrim 0..1        strength of the dark gradient behind the text (default 0.72)
  --accent WORD       one word in the accent colour
  --accent-color HEX  default #FFD24A (warm) — use #E5342A for red
  --rule              thin accent rule above the headline
  --track N           extra letter spacing in px
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = {
    "anton": ROOT / "assets/fonts/Anton-Regular.ttf.ttf",
    "bebas": ROOT / "assets/fonts/BebasNeue-Regular.ttf.ttf",
    "playfair": ROOT / "assets/fonts/PlayfairDisplay.ttf",
    "inter": ROOT / "assets/fonts/Inter.ttf",
}

ap = argparse.ArgumentParser()
ap.add_argument("photo"); ap.add_argument("out"); ap.add_argument("headline")
ap.add_argument("--sub", default=None)
ap.add_argument("--font", default="anton", choices=list(FONTS))
ap.add_argument("--size", type=int, default=0)
ap.add_argument("--pos", default="bl", choices=["bl", "bc", "tl", "tc"])
ap.add_argument("--crop", type=float, default=0.5)
ap.add_argument("--scrim", type=float, default=0.72)
ap.add_argument("--accent", default=None)
ap.add_argument("--accent-color", default="#FFD24A")
ap.add_argument("--rule", action="store_true")
ap.add_argument("--track", type=int, default=0)
a = ap.parse_args()

accent = tuple(int(a.accent_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

# --- photo: 16:9 crop around the chosen band, gentle cinematic grade ------------------------------
img = Image.open(a.photo).convert("RGB")
w, h = img.size
if w / h > 16 / 9:
    nw = int(h * 16 / 9)
    x0 = int((w - nw) * 0.5)
    img = img.crop((x0, 0, x0 + nw, h))
else:
    nh = int(w * 9 / 16)
    y0 = int((h - nh) * min(max(a.crop, 0), 1))
    img = img.crop((0, y0, w, y0 + nh))
img = img.resize((W, H), Image.LANCZOS)
img = ImageEnhance.Color(img).enhance(1.12)
img = ImageEnhance.Contrast(img).enhance(1.10)
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=3))

# vignette keeps the eye in the middle
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.30, -H * 0.42, W * 1.30, H * 1.42], fill=255)
img = Image.composite(img, ImageEnhance.Brightness(img).enhance(0.62), vig.filter(ImageFilter.GaussianBlur(140)))

top = a.pos in ("tl", "tc")
scrim = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(scrim)
for y in range(H):
    t = (1 - y / H) if top else (y / H)
    d.line([(0, y), (W, y)], fill=int(255 * a.scrim * max(0.0, (t - 0.42) / 0.58) ** 1.5))
img = Image.composite(Image.new("RGB", (W, H)), img, scrim)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl = ImageDraw.Draw(layer)
lines = a.headline.split("|")
size = a.size or (96 if max(len(l) for l in lines) <= 18 else 74)
font = ImageFont.truetype(str(FONTS[a.font]), size)
subfont = ImageFont.truetype(str(FONTS["inter"]), int(size * 0.30))


def draw_tracked(draw, xy, text, fnt, fill, track):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=fnt) + track
    return x


def width_tracked(draw, text, fnt, track):
    return sum(draw.textlength(c, font=fnt) for c in text) + track * max(0, len(text) - 1)


block_h = len(lines) * size * 1.14 + (int(size * 0.62) if a.sub else 0)
margin = 64
y = margin + size if top else H - margin - block_h + size
for line in lines:
    words = line.split(" ")
    total = sum(width_tracked(dl, w, font, a.track) for w in words) + (len(words) - 1) * (dl.textlength(" ", font=font) + a.track)
    x = margin if a.pos in ("bl", "tl") else (W - total) / 2
    if a.rule and line is lines[0]:
        ry = y - size * 1.02
        dl.rectangle([x, ry, x + 86, ry + 6], fill=(*accent, 255))
    for wi, word in enumerate(words):
        colour = (*accent, 255) if a.accent and word.strip(".,?!").lower() == a.accent.lower() else (255, 255, 255, 255)
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_tracked(ImageDraw.Draw(shadow), (x, y), word, font, (0, 0, 0, 235), a.track)
        layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)))
        draw_tracked(ImageDraw.Draw(layer), (x, y), word, font, colour, a.track)
        x = x + width_tracked(dl, word, font, a.track) + dl.textlength(" ", font=font) + a.track
    y += size * 1.14

if a.sub:
    sx = margin if a.pos in ("bl", "tl") else (W - width_tracked(dl, a.sub, subfont, 3)) / 2
    sy = y - size * 0.35
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_tracked(ImageDraw.Draw(shadow), (sx, sy), a.sub, subfont, (0, 0, 0, 230), 3)
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    draw_tracked(ImageDraw.Draw(layer), (sx, sy), a.sub, subfont, (232, 228, 220, 255), 3)

img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
img.save(a.out, quality=93)
print("saved", a.out)
