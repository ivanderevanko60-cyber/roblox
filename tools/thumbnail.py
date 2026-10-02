"""YouTube thumbnail in the style top science channels actually use.

Rules taken from Veritasium / PBS Space Time / Cool Worlds / Kurzgesagt thumbnails:
  * 2-4 words, huge, top of the frame; no second line of small text, no badges
  * one bright subject, large, in the lower half
  * a red arrow or underline pointing at the subject
  * sentence-case serif (Veritasium) or heavy caps (PBS / Cool Worlds)

python tools/thumbnail.py <bg> <out> "Head line|second" [--style serif|caps]
       [--arrow x1,y1,x2,y2] [--underline WORD] [--accent WORD] [--align left|center]
Coordinates for --arrow are fractions of width/height (0..1), from tail to head.
"""
import argparse, math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
RED = (222, 46, 32)
ACCENT = (255, 205, 40)
SERIF = "C:/Windows/Fonts/georgiab.ttf"
CAPS = "C:/Windows/Fonts/ariblk.ttf"

ap = argparse.ArgumentParser()
ap.add_argument("bg"); ap.add_argument("out"); ap.add_argument("headline")
ap.add_argument("--style", default="serif", choices=["serif", "caps"])
ap.add_argument("--arrow", default=None)
ap.add_argument("--underline", default=None)
ap.add_argument("--accent", default=None)
ap.add_argument("--align", default="center", choices=["left", "center"])
ap.add_argument("--banner", default=None, choices=["top", "bottom"], help="solid black bar behind the headline")
ap.add_argument("--banner-color", default="white", choices=["white", "red", "yellow"])
ap.add_argument("--kicker", default=None, help="small red label above the headline, e.g. PHYSICS")
ap.add_argument("--paste", action="append", default=[],
                help="composite an element: file,cx,cy,scale[,circle] (cx/cy/scale are fractions of the frame)")
ap.add_argument("--split", default=None, help="second photo for a split-screen right half")
ap.add_argument("--split-label", default=None, help="two labels for the split halves: LEFT|RIGHT")
a = ap.parse_args()

img = Image.open(a.bg).convert("RGB").resize((W, H), Image.LANCZOS)
img = ImageEnhance.Color(img).enhance(1.2)
img = ImageEnhance.Contrast(img).enhance(1.15)

if a.split:                       # split screen: left photo | right photo, red divider
    right = Image.open(a.split).convert("RGB").resize((W, H), Image.LANCZOS)
    right = ImageEnhance.Color(right).enhance(1.2)
    img.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))

BAR_H = 0.30            # black banner height as a share of the frame
if a.banner:
    img = ImageEnhance.Brightness(img).enhance(1.05)

# darken only the top band, where the words go
band = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(band)
for y in range(H):
    d.line([(0, y), (W, y)], fill=int(max(0, 190 * (1 - y / (H * 0.55)))))
if a.banner:
    band = Image.new("L", (W, H), 0)   # the bar does the contrast work instead
img = Image.composite(Image.new("RGB", (W, H)), img, band)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl = ImageDraw.Draw(layer)
bar_top = 0 if a.banner == "top" else H - int(H * BAR_H)
if a.banner:
    dl.rectangle([0, bar_top, W, bar_top + int(H * BAR_H)], fill=(0, 0, 0, 255))
    rule_y = bar_top + int(H * BAR_H) if a.banner == "top" else bar_top
    dl.rectangle([0, rule_y - 6 if a.banner == "bottom" else rule_y, W, (rule_y + 6) if a.banner == "top" else rule_y + 6], fill=(*RED, 255))

lines = a.headline.split("|")
longest = max(len(l) for l in lines)
if a.style == "serif":
    size = 104 if longest <= 16 else (86 if longest <= 22 else 70)
    font = ImageFont.truetype(SERIF, size)
else:
    size = 112 if longest <= 13 else (92 if longest <= 18 else 74)
    font = ImageFont.truetype(CAPS, size)
fill = {"white": (255, 255, 255, 255), "red": (*RED, 255), "yellow": (*ACCENT, 255)}[a.banner_color]
if a.banner:
    size = int(min(size, (H * BAR_H - 40) / len(lines)))
    font = ImageFont.truetype(SERIF if a.style == "serif" else CAPS, size)

block_h = size * 1.08 * len(lines)
if a.banner:
    y = bar_top + (H * BAR_H - block_h) / 2 - size * 0.08
    if a.kicker:
        y += 30
else:
    y = 54
boxes = []
for line in lines:
    words = line.split(" ")
    widths = [dl.textlength(w + " ", font=font) for w in words]
    total = sum(widths) - dl.textlength(" ", font=font)
    x = (W - total) / 2 if a.align == "center" else 66
    for w, wid in zip(words, widths):
        clean = w.strip(".,?!")
        hot = (*RED, 255) if a.banner_color == "white" else (*ACCENT, 255)
        colour = hot if a.accent and clean.lower() == a.accent.lower() else fill
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((x, y), w, font=font, fill=(0, 0, 0, 255), anchor="la", stroke_width=13, stroke_fill=(0, 0, 0, 255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        layer.alpha_composite(shadow)
        layer.alpha_composite(shadow)
        ImageDraw.Draw(layer).text((x, y), w, font=font, fill=colour, anchor="la")
        if a.underline and clean.lower() == a.underline.lower():
            boxes.append((x, y + size * 1.02, x + wid - dl.textlength(" ", font=font)))
        x += wid
    y += size * 1.08

if a.kicker and a.banner:
    kf = ImageFont.truetype(CAPS, 34)
    kw = dl.textlength(a.kicker, font=kf)
    kx = 44
    ky = bar_top + 12
    ImageDraw.Draw(layer).rectangle([kx, ky, kx + kw + 36, ky + 48], fill=(*RED, 255))
    ImageDraw.Draw(layer).text((kx + 18, ky + 24), a.kicker, font=kf, fill=(255, 255, 255, 255), anchor="lm")

for x0, yy, x1 in boxes:       # Veritasium-style red underline under one word
    ImageDraw.Draw(layer).line([(x0, yy), (x1, yy)], fill=(*RED, 255), width=7)

if a.arrow:                    # hand-drawn-ish curved arrow pointing at the subject
    x1, y1, x2, y2 = [float(v) for v in a.arrow.split(",")]
    p0 = (x1 * W, y1 * H)
    p2 = (x2 * W, y2 * H)
    mx, my = (p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2
    dx, dy = p2[0] - p0[0], p2[1] - p0[1]
    p1 = (mx - dy * 0.28, my + dx * 0.28)          # control point bows the curve
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(pts, fill=(0, 0, 0, 255), width=22, joint="curve")
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(layer).line(pts, fill=(*RED, 255), width=11, joint="curve")
    ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    L = 46
    head = [pts[-1],
            (pts[-1][0] - L * math.cos(ang - 0.45), pts[-1][1] - L * math.sin(ang - 0.45)),
            (pts[-1][0] - L * math.cos(ang + 0.45), pts[-1][1] - L * math.sin(ang + 0.45))]
    ImageDraw.Draw(layer).polygon(head, fill=(*RED, 255))

for spec in a.paste:              # cut-out elements (clock dials, objects) pasted onto the photo
    parts = spec.split(",")
    f, cx, cy, sc = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
    circle = len(parts) > 4 and parts[4] == "circle"
    el = Image.open(f).convert("RGB")
    if circle:                     # square-crop, then mask to a disc with a white rim
        side = min(el.size)
        el = el.crop(((el.width - side) // 2, (el.height - side) // 2,
                      (el.width - side) // 2 + side, (el.height - side) // 2 + side))
    tw = int(W * sc)
    el = el.resize((tw, int(el.height * tw / el.width)), Image.LANCZOS)
    el = ImageEnhance.Contrast(ImageEnhance.Color(el).enhance(1.15)).enhance(1.15)
    piece = Image.new("RGBA", el.size, (0, 0, 0, 0))
    piece.paste(el, (0, 0))
    if circle:
        mask = Image.new("L", el.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, el.size[0] - 1, el.size[1] - 1], fill=255)
        piece.putalpha(mask)
        ring = Image.new("RGBA", el.size, (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([3, 3, el.size[0] - 4, el.size[1] - 4], outline=(255, 255, 255, 255), width=8)
        piece.alpha_composite(ring)
    px, py = int(cx * W - el.size[0] / 2), int(cy * H - el.size[1] / 2)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", el.size, (0, 0, 0, 220)), (px + 6, py + 8), piece.split()[3])
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    layer.alpha_composite(piece.convert("RGBA"), (px, py))

if a.split:
    dl2 = ImageDraw.Draw(layer)
    dl2.rectangle([W // 2 - 5, 0, W // 2 + 5, H], fill=(*RED, 255))
    if a.split_label:
        lf = ImageFont.truetype(CAPS, 44)
        for half, text in enumerate(a.split_label.split("|")):
            cx = W * 0.25 + half * W * 0.5
            tw = dl2.textlength(text, font=lf)
            y0 = H - 96
            dl2.rectangle([cx - tw / 2 - 22, y0, cx + tw / 2 + 22, y0 + 62], fill=(0, 0, 0, 225))
            dl2.text((cx, y0 + 31), text, font=lf, fill=(255, 255, 255, 255), anchor="mm")

img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
img.save(a.out, quality=92)
print("saved", a.out)
