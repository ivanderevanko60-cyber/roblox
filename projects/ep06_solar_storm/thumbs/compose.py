"""EP06 thumbnails. One scene, one light: the real Sun (NASA/SDO) on the left throws a stream of plasma across
the frame; the Earth on the right catches it, its night side lit by an aurora. The headline is set in the
same heat as the Sun — white-hot core, orange glow — so the type reads as part of the picture."""
import pathlib, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "ep04_earth_age" / "thumbs"))
import design as D

HERE = pathlib.Path(__file__).resolve().parent
META = HERE.parent / "meta"
W, H = D.W, D.H
HOT = np.array([1.0, 0.55, 0.16], np.float32)
FONT = D.FONT


def stars(seed=5, n=380):
    rng = np.random.default_rng(seed)
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.choice([0.6, 0.8, 1.0, 1.4])
        d.ellipse((x - r, y - r, x + r, y + r), fill=int(rng.uniform(60, 220)))
    return np.asarray(L.filter(ImageFilter.GaussianBlur(0.6)), np.float32)[..., None] / 255 * np.array([0.8, 0.85, 1.0])


def sun_layer(plate, flip, scale, dx, dy):
    """The SDO frame as light: black sky stays black, so it simply adds onto space."""
    im = Image.open(HERE / "plates" / plate).convert("RGB")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), 0); canvas.paste(im, (dx, dy))
    a = D.f32(canvas)
    return np.clip((a - 0.02) * 1.08, 0, 1)


def stream(a, pts, width, seed=2):
    """A glowing plasma ribbon along a polyline: wide soft halo, bright thin core, sparks along the way."""
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    n = len(pts)
    for k in range(n - 1):
        w = int(width * (1 - k / n) + 3)
        d.line([pts[k], pts[k + 1]], fill=255, width=w, joint="curve")
    halo = np.asarray(L.filter(ImageFilter.GaussianBlur(38)), np.float32)[..., None] / 255
    mid = np.asarray(L.filter(ImageFilter.GaussianBlur(12)), np.float32)[..., None] / 255
    core = np.asarray(L.filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255
    a = a + halo * HOT * 0.9 + mid * HOT * 0.7 + core * np.array([1.0, 0.85, 0.6]) * 0.35
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return D.embers(a, 160, (min(xs), min(ys) - 40, max(xs), max(ys) + 40), color=(1.0, 0.6, 0.2), seed=seed)


def cloud(a, poly, seed=4, gain=0.5):
    """The CME: a wide, faint, textured haze fanning out from the eruption (no hard edges)."""
    L = Image.new("L", (W, H), 0); ImageDraw.Draw(L).polygon(poly, fill=255)
    m = np.asarray(L.filter(ImageFilter.GaussianBlur(70)), np.float32) / 255
    rng = np.random.default_rng(seed)
    n = Image.fromarray((rng.random((H // 16, W // 16)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    n = np.asarray(n.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    return a + (m * (0.55 + 0.9 * n))[..., None] * HOT * gain


def earth_layer(size):
    im = Image.open(HERE / "hero" / "earth_full.png").convert("RGBA")
    im = im.crop(im.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
    return im.resize((size, int(im.height * size / im.width)), Image.LANCZOS)


def hot_text(a, lines, size, x, y, align="left", spacing=0.98):
    """Headline in the Sun's own light: orange bloom, then a white-yellow core."""
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    sizes = size if isinstance(size, list) else [size] * len(lines)
    yy = y
    for ln, sz in zip(lines, sizes):
        f = ImageFont.truetype(FONT, sz)
        w = d.textlength(ln, font=f)
        xx = x - w if align == "right" else x - w / 2 if align == "center" else x
        d.text((xx, yy), ln, font=f, fill=255); yy += int(sz * spacing)
    m = np.asarray(L, np.float32)[..., None] / 255
    shadow = np.asarray(L.filter(ImageFilter.GaussianBlur(16)), np.float32)[..., None] / 255
    a = a * (1 - shadow * 0.75)                                            # dark bed so the type cuts out
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(30)), np.float32)[..., None] / 255 * HOT * 0.85
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(7)), np.float32)[..., None] / 255 * HOT * 0.6
    ramp = np.linspace(1.0, 0.0, H)[:, None, None]                         # hotter at the top of each letter
    core = np.array([1.0, 0.98, 0.9]) * 0.4 + np.array([1.0, 0.8, 0.3]) * 0.6
    return a * (1 - m) + m * core * (0.92 + 0.08 * ramp)


def scene(name, plate, flip, scale, sdx, sdy, earth_size, ex, ey, fan, text, tsize, tx, ty, align="left"):
    a = stars() * 0.8
    a = np.maximum(a, sun_layer(plate, flip, scale, sdx, sdy))
    a = cloud(a, fan)
    xs = [p[0] for p in fan]; ys = [p[1] for p in fan]
    a = D.embers(a, 45, (min(xs) + 120, min(ys), max(xs), max(ys)), color=(1.0, 0.6, 0.2), seed=2)
    e = earth_layer(earth_size)
    e = D.rim(e, -1, 0, (255, 150, 60), width=6)                            # sunward edge catches the plasma
    a = a + D.glow_from(e, ex, ey, (1.0, 0.45, 0.15), 30, 0.35)
    a = D.paste(a, e, ex, ey)
    a = hot_text(a, text, tsize, tx, ty, align)
    a = D.finish(a, shadows=(0.03, 0.01, 0.0), highs=(1.0, 0.7, 0.4), amount=0.25, vignette=0.45, grain=0.025)
    D.pil(a).save(META / name, quality=94)
    print("saved", name)


def poles(a, xs, base, top, sparks=()):
    """Telegraph poles and sagging wires as black silhouettes against the aurora; sparks at the insulators."""
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    heads = []
    for x, s in xs:                                   # s: perspective scale
        h = (base - top) * s
        d.rectangle((x - 5 * s, base - h, x + 5 * s, base), fill=255)
        for k in range(2):
            y = base - h + (14 + 26 * k) * s
            d.rectangle((x - 46 * s, y, x + 46 * s, y + 6 * s), fill=255)
            heads.append([(x - 40 * s, y), (x + 40 * s, y)])
    for k in range(len(heads) - 2):
        for j in range(2):
            (x0, y0), (x1, y1) = heads[k][j], heads[k + 2][j]
            pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + 30 * np.sin(np.pi * t) * abs(x1 - x0) / 400) for t in np.linspace(0, 1, 30)]
            d.line(pts, fill=255, width=3)
    m = np.asarray(L.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
    a = a * (1 - m) + m * 0.01
    for (x, y) in sparks:
        S = Image.new("L", (W, H), 0); ImageDraw.Draw(S).ellipse((x - 6, y - 6, x + 6, y + 6), fill=255)
        for r, g in ((90, 3.0), (26, 2.4), (5, 1.6)):
            a = a + np.asarray(S.filter(ImageFilter.GaussianBlur(r)), np.float32)[..., None] / 255 * np.array([1.0, 0.8, 0.5]) * g
        a = D.embers(a, 40, (x - 90, y - 40, x + 90, y + 120), color=(1.0, 0.7, 0.3), seed=x)
    return a


def sky(name, plate, text, tsize, tx, ty, align, pole_xs, base, top, sparks, redden=0.0):
    a = D.f32(Image.open(HERE / "plates" / plate).convert("RGB").resize((W, H), Image.LANCZOS))
    lum = a.mean(axis=2, keepdims=True)
    a = np.clip(lum + (a - lum) * 1.9, 0, 1)                                # the aurora's own colour, saturated
    if redden:                                                              # the upper sky towards blood red
        yy = np.linspace(1, 0, H)[:, None, None] ** 1.3
        a = a * (1 + yy * redden * np.array([1.6, -0.35, -0.2]))
    a = np.clip(a * 1.35, 0, 1) ** 1.1
    a = poles(a, pole_xs, base, top, sparks)
    a = hot_text(a, text, tsize, tx, ty, align)
    a = D.finish(a, shadows=(0.0, 0.03, 0.02), highs=(1.0, 0.7, 0.4), amount=0.25, vignette=0.5, grain=0.03)
    D.pil(a).save(META / name, quality=94)
    print("saved", name)


if __name__ == "__main__":
    # A: the miss — plasma flies past, headline on the empty right
    scene("thumb_A_missed.jpg", "sun_limb.png", False, 0.78, -250, -70, 250, 990, 430,
          [(640, 330), (1280, 150), (1280, 420)], ["MISSED US", "BY 1 WEEK"], [118, 118], 1245, 30, "right")
    # B: 1859 — the sky on fire over the telegraph line
    sky("thumb_B_skyfire.jpg", "aur_redgreen.png", ["THE SKY", "CAUGHT FIRE"], [124, 124], 60, 36, "left",
        [(880, 1.25), (1120, 1.0), (1255, 0.82)], 720, 330, [(880 - 58, 720 - 390 * 1.25 + 17), (1120 + 40, 720 - 390 + 40)], redden=0.35)
    # C: the Sun, close — the Earth tiny in front of it
    scene("thumb_C_tried.jpg", "sun_erupt.png", False, 0.9, -120, 160, 150, 1060, 70,
          [(560, 420), (1280, 60), (1280, 330)], ["IT ALREADY", "HAPPENED"], [112, 112], 40, 36, "left")
