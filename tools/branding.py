"""Channel art for YouTube: avatar (800x800) and banner (2048x1152, safe area 1235x338).

python tools/branding.py <out_dir> [--photo path] [--name "THE LAST DIGIT"] [--tag "..."]
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANTON = str(ROOT / "assets/fonts/Anton-Regular.ttf.ttf")
INTER = str(ROOT / "assets/fonts/Inter.ttf")
GOLD = (255, 210, 74)
INK = (8, 9, 12)

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--photo", default=None, help="background photo for the banner")
ap.add_argument("--name", default="THE LAST DIGIT")
ap.add_argument("--tag", default="THE EXPERIMENTS THAT CHANGED WHAT WE MEASURE")
a = ap.parse_args()
out = pathlib.Path(a.out)
out.mkdir(parents=True, exist_ok=True)


def avatar(path, mode):
    S = 800
    img = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(img)
    d.ellipse([18, 18, S - 18, S - 18], outline=GOLD, width=12)
    if mode == "dots":                      # "…1" — the last digit that still means something
        f = ImageFont.truetype(ANTON, 300)
        dots = ImageFont.truetype(ANTON, 300)
        total = d.textlength("...", font=dots) + d.textlength("1", font=f) + 24
        x = (S - total) / 2
        d.text((x, S / 2 + 40), "...", font=dots, fill=(235, 235, 235), anchor="ls")
        x += d.textlength("...", font=dots) + 24
        d.text((x, S / 2 + 40), "1", font=f, fill=GOLD, anchor="ls")
    else:                                    # monogram
        f = ImageFont.truetype(ANTON, 330)
        d.text((S / 2, S / 2 + 12), "LD", font=f, fill=(240, 240, 240), anchor="mm")
        d.rectangle([S / 2 - 90, S / 2 + 150, S / 2 + 90, S / 2 + 162], fill=GOLD)
    img.save(path, quality=95)
    print("saved", path)


def banner(path, photo):
    W, H = 2048, 1152
    SAFE_W, SAFE_H = 1235, 338            # what phones and TVs actually show
    if photo:
        img = Image.open(photo).convert("RGB")
        w, h = img.size
        nh = int(w * H / W)
        y0 = max(0, int((h - nh) * 0.45))
        img = img.crop((0, y0, w, y0 + nh)).resize((W, H), Image.LANCZOS)
        img = ImageEnhance.Brightness(img).enhance(0.42)
        img = ImageEnhance.Color(img).enhance(0.9)
        img = img.filter(ImageFilter.GaussianBlur(1.2))
    else:
        img = Image.new("RGB", (W, H), INK)
    # keep the centre dark so the title always reads
    scrim = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(scrim)
    for x in range(W):
        t = abs(x - W / 2) / (W / 2)
        ds.line([(x, 0), (x, H)], fill=int(200 * max(0.0, 1 - t / 0.75)))
    img = Image.composite(Image.new("RGB", (W, H), INK), img, scrim)

    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(ANTON, 132)
    sub = ImageFont.truetype(INTER, 34)
    cx, cy = W / 2, H / 2
    # title with letter spacing
    track = 10
    total = sum(d.textlength(c, font=f) for c in a.name) + track * (len(a.name) - 1)
    x = cx - total / 2
    for ch in a.name:
        d.text((x, cy - 24), ch, font=f, fill=(245, 245, 245), anchor="ls")
        x += d.textlength(ch, font=f) + track
    d.rectangle([cx - 120, cy + 4, cx + 120, cy + 12], fill=GOLD)
    st = 6
    stotal = sum(d.textlength(c, font=sub) for c in a.tag) + st * (len(a.tag) - 1)
    x = cx - stotal / 2
    for ch in a.tag:
        d.text((x, cy + 84), ch, font=sub, fill=(205, 200, 190), anchor="ls")
        x += d.textlength(ch, font=sub) + st
    img.save(path, quality=95)
    print("saved", path, f"(safe area {SAFE_W}x{SAFE_H} centred)")


avatar(out / "avatar_dots.jpg", "dots")
avatar(out / "avatar_monogram.jpg", "mono")
banner(out / "banner.jpg", a.photo)
