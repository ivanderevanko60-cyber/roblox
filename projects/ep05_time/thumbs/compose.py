"""EP05 thumbnails: the Earth as a clock face (Blender), text in the empty third."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "ep04_earth_age" / "thumbs"))
import numpy as np
from PIL import Image, ImageFilter
import design as D
from compose_hero import starfield

HERE = pathlib.Path(__file__).resolve().parent
META = HERE.parent / "meta"; META.mkdir(exist_ok=True)


def make(lines, sizes, colors, name, glow=(255, 150, 60)):
    W, H = D.W, D.H
    a = starfield(seed=7)
    p = Image.open(HERE / "hero" / "clock_full.png").convert("RGBA")
    p = p.crop(p.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
    h = 640; p = p.resize((round(p.width * h / p.height), h), Image.LANCZOS)
    x, y = W * 0.30 - p.width / 2, (H - p.height) / 2
    halo = Image.new("L", (W, H), 0); halo.paste(p.split()[3], (int(x), int(y)))
    a += np.asarray(halo.filter(ImageFilter.GaussianBlur(45)), np.float32)[..., None] / 255 * np.array([0.10, 0.25, 0.55], np.float32)
    a = D.paste(a, p, x, y)
    t = D.text_layer(lines, sizes, 0, 0, colors, spacing=1.0, glow=glow)
    t = t.crop(t.getbbox())
    a = D.paste(a, t, W - t.width - 56, (H - t.height) / 2)
    D.pil(D.finish(a, amount=0.2, vignette=0.4, grain=0.025)).save(META / name, quality=94)
    print("saved", name)


make(["23:59", ":60"], [150, 190], [(255, 255, 255), D.YELLOW], "thumb_A_235960.jpg")
make(["EARTH", "IS A BAD", "CLOCK"], [150, 110, 150], [(255, 255, 255), (255, 255, 255), D.YELLOW], "thumb_B_badclock.jpg")
make(["WHAT", "TIME", "IS IT?"], [150, 150, 150], [(255, 255, 255), (255, 255, 255), D.YELLOW], "thumb_C_whattime.jpg")
