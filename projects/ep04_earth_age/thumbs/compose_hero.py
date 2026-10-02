"""Final EP04 thumbnails from the Blender hero renders: one idea, one light, text in the empty third."""
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from design import W, H, YELLOW, HERE, META, f32, pil, radial, paste, text_layer, finish

HERO = HERE / "hero"


def starfield(seed=2):
    a = radial(W * 0.3, H * 0.5, W * 0.9, (0.02, 0.03, 0.06), (0.003, 0.004, 0.008))
    rng = random.Random(seed)
    layer = Image.new("L", (W, H), 0); d = ImageDraw.Draw(layer)
    for _ in range(420):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([0.6, 0.8, 1, 1.4])
        d.ellipse((x - r, y - r, x + r, y + r), fill=rng.randint(70, 230))
    return a + np.asarray(layer.filter(ImageFilter.GaussianBlur(0.6)), np.float32)[..., None] / 255 * 0.9


def planet_layer(height, cx, cy):
    p = Image.open(HERO / "rings_full.png").convert("RGBA")
    p = p.crop(p.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
    p = p.resize((round(p.width * height / p.height), height), Image.LANCZOS)
    return p, cx - p.width / 2, cy - p.height / 2


def rings(text_lines, sizes, colors, name):
    a = starfield()
    p, x, y = planet_layer(690, W * 0.33, H * 0.5)
    # warm light spilling from the open core, cool atmosphere halo
    a += radial(x + p.width * 0.52, y + p.height * 0.42, 420, (0.55, 0.22, 0.05), (0, 0, 0), 1.8) * 0.8
    halo = Image.new("L", (W, H), 0); halo.paste(p.split()[3], (int(x), int(y)))
    a += np.asarray(halo.filter(ImageFilter.GaussianBlur(40)), np.float32)[..., None] / 255 * np.array([0.10, 0.25, 0.55], np.float32) * 0.9
    a = paste(a, p, x, y)
    t = text_layer(text_lines, sizes, 0, 0, colors, spacing=1.0, glow=(255, 150, 60))
    t = t.crop(t.getbbox())
    a = paste(a, t, W - t.width - 58, (H - t.height) / 2)
    META.joinpath(name).parent.mkdir(exist_ok=True)
    pil(finish(a, amount=0.2, vignette=0.4, grain=0.025)).save(META / name, quality=94)
    print("saved", name)


def hourglass(text_lines, sizes, colors, name):
    a = f32(Image.open(HERO / "hourglass_full.png").resize((W, H), Image.LANCZOS))
    t = text_layer(text_lines, sizes, 0, 0, colors, spacing=1.0, glow=(255, 150, 60))
    t = t.crop(t.getbbox())
    a = paste(a, t, 70, (H - t.height) / 2)
    pil(finish(a, amount=0.2, vignette=0.35, grain=0.025)).save(META / name, quality=94)
    print("saved", name)


if __name__ == "__main__":
    rings(["COUNT", "THE", "RINGS"], [150, 110, 150], [(255, 255, 255), (255, 255, 255), YELLOW], "thumb_P_rings.jpg")
    rings(["HOW", "OLD?"], [190, 190], [(255, 255, 255), YELLOW], "thumb_Q_rings_howold.jpg")
    hourglass(["4.54", "BILLION", "YEARS"], [210, 120, 120], [YELLOW, (255, 255, 255), (255, 255, 255)], "thumb_R_hourglass.jpg")
