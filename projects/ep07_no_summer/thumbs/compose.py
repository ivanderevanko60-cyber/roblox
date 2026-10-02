"""EP07 thumbnails. The idea in every frame is a contradiction you can see at feed size: summer under snow.
One light per scene; falling snow is part of the same scene (sharp flakes near, soft flakes far), and the
headline is lit like the scene — ice-blue glow on the cold plates, the volcano's orange on the hot one."""
import pathlib, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "ep04_earth_age" / "thumbs"))
import design as D

HERE = pathlib.Path(__file__).resolve().parent
META = HERE.parent / "meta"
W, H = D.W, D.H
ICE = np.array([0.55, 0.8, 1.0], np.float32)
HOT = np.array([1.0, 0.55, 0.16], np.float32)


def plate(name, cool=0.0, sat=1.0, gain=1.0):
    a = D.f32(Image.open(HERE / "plates" / name).convert("RGB").resize((W, H), Image.LANCZOS))
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * sat
    if cool:                                                               # a cold cast over the whole frame
        a = a * (1 - cool) + cool * lum * np.array([0.78, 0.92, 1.12])
    return np.clip(a * gain, 0, 1)


def snow(a, n, seed=1, box=(0, 0, W, H)):
    """Three depths of flakes: big soft ones near the lens, mid, and small sharp ones far away."""
    rng = np.random.default_rng(seed)
    for count, rmin, rmax, blur, gain in ((n // 8, 7, 14, 6, 0.55), (n // 3, 3, 6, 1.6, 0.8), (n, 1, 2.4, 0.5, 0.9)):
        L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
        for _ in range(count):
            x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3]); r = rng.uniform(rmin, rmax)
            d.ellipse((x - r, y - r, x + r, y + r), fill=int(rng.uniform(150, 255)))
        m = np.asarray(L.filter(ImageFilter.GaussianBlur(blur)), np.float32)[..., None] / 255 * gain
        a = a * (1 - m) + m * np.array([0.95, 0.97, 1.0])
    return a


def glow_text(a, lines, size, x, y, glow, core, align="left", spacing=0.98, bed=0.7):
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    sizes = size if isinstance(size, list) else [size] * len(lines)
    yy = y
    for ln, sz in zip(lines, sizes):
        f = ImageFont.truetype(D.FONT, sz)
        w = d.textlength(ln, font=f)
        xx = x - w if align == "right" else x - w / 2 if align == "center" else x
        d.text((xx, yy), ln, font=f, fill=255); yy += int(sz * spacing)
    m = np.asarray(L, np.float32)[..., None] / 255
    shadow = np.asarray(L.filter(ImageFilter.GaussianBlur(18)), np.float32)[..., None] / 255
    a = a * (1 - shadow * bed)
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(28)), np.float32)[..., None] / 255 * glow * 0.8
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255 * glow * 0.5
    return a * (1 - m) + m * np.asarray(core, np.float32)


def out(a, name, **grade):
    a = D.finish(a, **grade)
    D.pil(a).save(META / name, quality=94)
    print("saved", name)


def thumb_A():
    """Snow on June leaves. Headline on the darker left, ice light."""
    a = plate("snow_leaves.png", cool=0.35, sat=1.15, gain=0.95)
    a = a * (1 - 0.55 * np.linspace(1, 0, W)[None, :, None] ** 1.5)       # darken the left for the type
    a = snow(a, 420, seed=3)
    a = glow_text(a, ["SNOW", "IN JUNE"], [190, 150], 50, 70, ICE, (0.96, 0.99, 1.0))
    out(a, "thumb_A_snowjune.jpg", shadows=(0.0, 0.03, 0.07), highs=(0.85, 0.92, 1.0), amount=0.3, vignette=0.45, grain=0.025)


def thumb_B():
    """The eruption, and snow falling over it — the cause and the effect in one frame."""
    a = plate("eruption.png", sat=1.2, gain=1.0)
    a = snow(a, 300, seed=5, box=(0, 0, W, H))
    a = glow_text(a, ["IT CANCELLED", "SUMMER"], [118, 150], W - 50, 40, HOT, (1.0, 0.95, 0.85), align="right")
    out(a, "thumb_B_cancelled.jpg", shadows=(0.03, 0.02, 0.05), highs=(1.0, 0.75, 0.5), amount=0.25, vignette=0.5, grain=0.025)


def thumb_C():
    """Apple blossom in a snowstorm; the year as one big cold number."""
    a = plate("snow_blossom.png", cool=0.3, sat=1.1, gain=0.9)
    a = a * (1 - 0.45 * np.linspace(0, 1, W)[None, :, None] ** 2)
    a = snow(a, 380, seed=8)
    a = glow_text(a, ["1816"], [300], W - 40, 40, ICE, (0.97, 0.99, 1.0), align="right")
    a = glow_text(a, ["NO SUMMER"], [110], W - 46, 360, ICE, (0.97, 0.99, 1.0), align="right", bed=0.5)
    out(a, "thumb_C_1816.jpg", shadows=(0.0, 0.03, 0.07), highs=(0.9, 0.93, 1.0), amount=0.3, vignette=0.45, grain=0.025)


if __name__ == "__main__":
    thumb_A(); thumb_B(); thumb_C()
