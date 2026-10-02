"""Composite thumbnails: cut an object out of a photo (rembg) and stage it over a background with glow + text.

python tools/thumb_comp.py <background> <object_photo> <out.jpg> "LINE|LINE" --accent WORD
       [--obj-x 0.72 --obj-y 0.55 --obj-h 0.75] [--glow #ff7a1a] [--pos tl|bl] [--size 120] [--bg-dim 0.55]
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from rembg import remove

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = str(ROOT / "assets" / "fonts" / "Anton-Regular.ttf.ttf")
W, H = 1280, 720

ap = argparse.ArgumentParser()
ap.add_argument("bg"); ap.add_argument("obj"); ap.add_argument("out"); ap.add_argument("headline")
ap.add_argument("--accent", default=None); ap.add_argument("--accent-color", default="#FFD24A")
ap.add_argument("--obj-x", type=float, default=0.72); ap.add_argument("--obj-y", type=float, default=0.55)
ap.add_argument("--obj-h", type=float, default=0.75); ap.add_argument("--glow", default="#ff7a1a")
ap.add_argument("--pos", default="tl"); ap.add_argument("--size", type=int, default=120)
ap.add_argument("--bg-dim", type=float, default=0.6); ap.add_argument("--bg-x", type=float, default=0.5)
ap.add_argument("--flip-bg", action="store_true")
a = ap.parse_args()


def cover(img, w, h, cx=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = int((img.width - w) * cx); y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


bg = cover(Image.open(a.bg).convert("RGB"), W, H, a.bg_x)
if a.flip_bg:
    bg = bg.transpose(Image.FLIP_LEFT_RIGHT)
bg = ImageEnhance.Brightness(bg).enhance(a.bg_dim)
canvas = bg.convert("RGBA")

# object cut-out, scaled to a share of the frame height
cut = remove(Image.open(a.obj).convert("RGB"))
cut = cut.crop(cut.getbbox())
oh = int(H * a.obj_h); ow = int(cut.width * oh / cut.height)
cut = cut.resize((ow, oh), Image.LANCZOS)
cut = ImageEnhance.Contrast(cut).enhance(1.12)
ox = int(W * a.obj_x - ow / 2); oy = int(H * a.obj_y - oh / 2)

# glow behind the object: its own silhouette, blurred and tinted
alpha = cut.split()[3]
glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
tint = Image.new("RGBA", cut.size, a.glow); tint.putalpha(alpha)
glow.paste(tint, (ox, oy), tint)
glow = glow.filter(ImageFilter.GaussianBlur(38))
canvas = Image.alpha_composite(canvas, glow)
canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(90)))
# soft contact shadow
canvas.paste(cut, (ox, oy), cut)

# left-side scrim so the text always reads
scrim = Image.new("L", (W, H), 0); d = ImageDraw.Draw(scrim)
for x in range(W):
    d.line([(x, 0), (x, H)], fill=int(200 * max(0, 1 - x / (W * 0.62)) ** 1.6))
canvas = Image.alpha_composite(canvas, Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [scrim]))

# headline
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype(FONT, a.size)
lines = a.headline.split("|")
lh = int(a.size * 1.08)
y = 44 if a.pos == "tl" else H - 44 - lh * len(lines)
for line in lines:
    x = 52
    for k, word in enumerate(line.split(" ")):
        col = a.accent_color if a.accent and word.strip("?!.,").upper() in {w.upper() for w in a.accent.split()} else "#FFFFFF"
        draw.text((x + 4, y + 5), word, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), word, font=font, fill=col)
        x += draw.textlength(word + " ", font=font)
    y += lh
canvas.convert("RGB").save(a.out, quality=93)
print("saved", a.out)
