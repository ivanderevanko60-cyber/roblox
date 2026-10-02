"""EP04 thumbnails as designed scenes: one light, one palette, text and objects layered in depth.

python design.py            -> ../meta/thumb_K_*.jpg ... thumb_N_*.jpg
"""
import pathlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = pathlib.Path(__file__).resolve().parent
PL = HERE / "plates"
META = HERE.parent / "meta"
FONT = str(HERE.parents[2] / "assets" / "fonts" / "Anton-Regular.ttf.ttf")
W, H = 1280, 720
YELLOW = (255, 210, 74)


# ---------- helpers ------------------------------------------------------------------------------
def f32(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32) / 255


def pil(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def cutout(name, thr=40):
    im = Image.open(PL / name).convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v > thr else int(v * 255 / thr) if v > 8 else 0)
    im.putalpha(a)
    return im.crop(a.point(lambda v: 255 if v > 128 else 0).getbbox())


def fit_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def radial(cx, cy, r, inner, outer, power=1.6):
    y, x = np.mgrid[0:H, 0:W]
    d = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1) ** power
    return np.asarray(inner, np.float32) * (1 - d[..., None]) + np.asarray(outer, np.float32) * d[..., None]


def paste(base, obj, x, y):
    """Alpha-composite an RGBA PIL object onto a float canvas."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(obj, (int(x), int(y)), obj)
    a = np.asarray(layer, np.float32) / 255
    return base * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:]


def glow_from(obj, x, y, color, blur, gain):
    layer = Image.new("L", (W, H), 0)
    layer.paste(obj.split()[3], (int(x), int(y)))
    g = np.asarray(layer.filter(ImageFilter.GaussianBlur(blur)), np.float32)[..., None] / 255
    return g * np.asarray(color, np.float32) * gain


def rim(obj, dx, dy, color, width=10):
    """Light catching one edge of an object: alpha minus alpha shifted away from the light."""
    a = obj.split()[3]
    shifted = ImageChops.offset(a, int(-dx * width), int(-dy * width))
    edge = ImageChops.subtract(a, shifted).filter(ImageFilter.GaussianBlur(2.5))
    tint = Image.new("RGBA", obj.size, color + (0,))
    tint.putalpha(edge)
    out = obj.copy()
    return Image.alpha_composite(out, tint)


def text_layer(lines, size, x, y, colors, shadow=True, spacing=1.02, glow=None):
    """lines: list of strings; colors: per-line RGB. Returns RGBA."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sizes = size if isinstance(size, list) else [size] * len(lines)
    yy = y
    for line, col, sz in zip(lines, colors, sizes):
        f = ImageFont.truetype(FONT, sz)
        d.text((x, yy), line, font=f, fill=col + (255,))
        yy += int(sz * spacing)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.85)))
        out = Image.alpha_composite(out, ImageChops.offset(sh, 6, 10))
    if glow:
        gl = Image.new("RGBA", (W, H), glow + (0,))
        gl.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.55)))
        out = Image.alpha_composite(out, gl)
    return Image.alpha_composite(out, layer)


def finish(a, shadows=(0.02, 0.07, 0.09), highs=(1.0, 0.72, 0.42), amount=0.35, vignette=0.55, grain=0.035, seed=1):
    """One grade over everything: teal shadows, warm highlights, vignette, film grain."""
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    toned = a + (np.asarray(shadows, np.float32) * (1 - lum) ** 2 + (np.asarray(highs, np.float32) - 0.7) * lum ** 2 * 0.25) * amount
    y, x = np.mgrid[0:H, 0:W]
    v = 1 - vignette * np.clip(np.hypot((x - W / 2) / (W * 0.62), (y - H / 2) / (H * 0.7)), 0, 1) ** 2.2
    toned *= v[..., None]
    rng = np.random.default_rng(seed)
    toned += rng.normal(0, grain, (H, W, 1)).astype(np.float32)
    toned = np.clip(toned, 0, 1)
    # gentle S-curve for punch
    return toned ** 0.95 * (1.08 - 0.08 * toned)


def embers(a, n, box, color=(1.0, 0.55, 0.15), seed=3):
    rng = random.Random(seed)
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.choice([1, 1, 1.5, 2, 3])
        d.ellipse((x - r, y - r, x + r, y + r), fill=rng.randint(120, 255))
    g = np.asarray(layer.filter(ImageFilter.GaussianBlur(1.2)), np.float32)[..., None] / 255
    halo = np.asarray(layer.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255
    return a + (g * 1.6 + halo * 1.2) * np.asarray(color, np.float32)


def save(a, name):
    pil(a).save(META / name, quality=94)
    print("saved", name)


rock = cutout("meteorite_cut.png")


# ---------- K: the number behind the rock ---------------------------------------------------------
def design_K():
    a = radial(W * 0.62, H * 0.62, W * 0.75, (0.20, 0.08, 0.03), (0.01, 0.012, 0.016))
    a += radial(W * 0.62, H * 1.05, W * 0.45, (0.35, 0.12, 0.02), (0, 0, 0), 2.2)          # heat pooling on the floor
    num = text_layer(["4.5"], 470, 0, 0, [(255, 236, 205)], shadow=False, glow=(255, 140, 50))
    num = num.crop(num.getbbox())
    a = paste(a, num, 56, 34)
    num_bottom = 34 + num.height
    r = fit_h(rim(rock, -1, -0.4, (255, 190, 120), 9), 420)
    rx, ry = W * 0.74 - r.width / 2, H - r.height - 30
    a += glow_from(r, rx, ry, (1.0, 0.42, 0.10), 60, 0.55)
    # contact shadow
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse((rx + 30, H - 60, rx + r.width - 30, H + 20), fill=200)
    a *= 1 - np.asarray(sh.filter(ImageFilter.GaussianBlur(24)), np.float32)[..., None] / 255 * 0.7
    a = paste(a, r, rx, ry)
    a = embers(a, 70, (W * 0.35, H * 0.25, W, H))
    words = text_layer(["BILLION YEARS"], 112, 0, 0, [YELLOW], spacing=1.0)
    words = words.crop(words.getbbox())
    words_y = num_bottom + 26
    a = paste(a, words, 60, words_y)
    save(finish(a, amount=0.4), "thumb_K_number.jpg")


# ---------- L: a meteor falling onto Earth, OLDER THAN EARTH ------------------------------------
def design_L():
    a = np.zeros((H, W, 3), np.float32) + np.array([0.006, 0.008, 0.014], np.float32)
    rng = random.Random(9)
    stars = Image.new("L", (W, H), 0); d = ImageDraw.Draw(stars)
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.point((x, y), fill=rng.randint(60, 200))
    a += np.asarray(stars, np.float32)[..., None] / 255 * 0.8
    earth = Image.open(PL / "earth_frame.png").convert("RGB")
    e = earth.resize((int(earth.width * 1.7), int(earth.height * 1.7)), Image.LANCZOS)
    e = np.asarray(e, np.float32) / 255
    ox, oy = -700, 0                                      # planet rises from the bottom-left
    sub = e[max(0, -oy):max(0, -oy) + H, max(0, -ox):max(0, -ox) + W]
    pad = np.zeros((H, W, 3), np.float32)
    pad[max(0, oy):max(0, oy) + sub.shape[0], max(0, ox):max(0, ox) + sub.shape[1]] = sub[:H - max(0, oy), :W - max(0, ox)]
    pad = np.clip((pad - 0.07) / 0.93, 0, 1)
    a = 1 - (1 - a) * (1 - pad * 0.9)                        # screen blend: the black of space stays black
    # the fire trail, coming in from the top right
    trail = Image.new("L", (W, H), 0); dt = ImageDraw.Draw(trail)
    r = fit_h(rim(rock.rotate(-18, expand=True, resample=Image.BICUBIC), 1, -1, (255, 200, 140), 8), 280)
    rx, ry = W * 0.66 - r.width / 2, H * 0.52 - r.height / 2
    cx, cy = rx + r.width / 2, ry + r.height / 2
    ex, ey = W + 150, -250
    for k in range(40):
        off = rng.uniform(-60, 60)
        dt.line((cx + off * 0.3, cy + off * 0.3, ex + off * 3, ey + off * 2), fill=rng.randint(40, 110), width=rng.randint(6, 30))
    tr = np.asarray(trail.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255
    y_, x_ = np.mgrid[0:H, 0:W]
    fade = np.clip(1 - np.hypot(x_ - cx, y_ - cy) / 900, 0, 1)[..., None]
    a += tr * fade * np.array([1.0, 0.45, 0.12], np.float32) * 2.6
    a += glow_from(r, rx, ry, (1.0, 0.5, 0.15), 50, 0.9)
    a = paste(a, r, rx, ry)
    a = embers(a, 90, (W * 0.55, 0, W, H * 0.7), seed=5)
    t = text_layer(["OLDER", "THAN", "EARTH"], [170, 128, 128], 56, 30, [YELLOW, (255, 255, 255), (255, 255, 255)], spacing=1.0)
    a = paste(a, t, 0, 0)
    save(finish(a, amount=0.3, vignette=0.45), "thumb_L_falling.jpg")


# ---------- M: typographic — Kelvin's number crossed out, the real one ---------------------------
def design_M():
    a = radial(W * 0.5, H * 0.45, W * 0.8, (0.10, 0.06, 0.04), (0.01, 0.01, 0.012))
    tex = np.asarray(Image.open(PL / "lava_frame.png").convert("L").resize((W, H)), np.float32)[..., None] / 255
    a *= 0.55 + 0.9 * tex                                   # the lava's texture as a dark backdrop
    a += tex ** 3 * np.array([0.9, 0.3, 0.05], np.float32) * 0.8
    old = text_layer(["20 MILLION"], 150, 0, 0, [(200, 196, 190)], shadow=True)
    old = old.crop(old.getbbox())
    ox, oy = (W - old.width) // 2, 70
    a = paste(a, old, ox, oy)
    strike = Image.new("L", (W, H), 0)
    ImageDraw.Draw(strike).line((ox - 30, oy + old.height * 0.62, ox + old.width + 30, oy + old.height * 0.38), fill=255, width=22)
    s = np.asarray(strike.filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
    a = a * (1 - s) + s * np.array([0.93, 0.13, 0.12], np.float32)
    new = text_layer(["4.54 BILLION"], 190, 0, 0, [YELLOW], glow=(255, 150, 40))
    new = new.crop(new.getbbox())
    a = paste(a, new, (W - new.width) // 2, 330)
    save(finish(a, amount=0.25), "thumb_M_numbers.jpg")


# ---------- N: a face lit by the rock she is holding -----------------------------------------------
def design_N():
    face = Image.open(PL / "p6605132.jpg").convert("RGB")
    s = max(W / face.width, H / face.height)
    face = face.resize((round(face.width * s), round(face.height * s)), Image.LANCZOS)
    x0 = int((face.width - W) * 0.78)
    face = face.crop((x0, 0, x0 + W, H))
    a = f32(face)
    lum = a.mean(axis=2, keepdims=True)
    a = a * 0.35 + lum * np.array([0.30, 0.34, 0.40], np.float32) * 0.55       # desaturate and cool the room
    r = fit_h(rim(rock, 0, 1, (255, 190, 120), 8), 250)
    rx, ry = W * 0.70 - r.width / 2, H - r.height - 24
    # the rock is the light source: warm light falling on the face from below
    light = radial(rx + r.width / 2, ry + r.height * 0.3, W * 0.7, (1.0, 0.55, 0.22), (0, 0, 0), 1.3)
    a = a + a * light * 1.6
    a += glow_from(r, rx, ry, (1.0, 0.48, 0.12), 70, 0.9)
    a = paste(a, r, rx, ry)
    a = embers(a, 50, (W * 0.4, H * 0.4, W * 0.95, H), seed=7)
    t = text_layer(["OLDER", "THAN", "EARTH"], [160, 120, 120], 48, 40, [YELLOW, (255, 255, 255), (255, 255, 255)], spacing=1.0)
    a = paste(a, t, 0, 0)
    save(finish(a, amount=0.25, vignette=0.5), "thumb_N_face.jpg")


if __name__ == "__main__":
    design_K(); design_L(); design_M(); design_N()
