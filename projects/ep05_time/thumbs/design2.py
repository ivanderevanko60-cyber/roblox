"""EP05 thumbnails for "One Extra Second Broke the Internet": an LED clock showing the impossible 23:59:60,
glitching, in a red-lit server room. One light (the display), one palette (red on black), text in the same glow."""
import pathlib, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "ep04_earth_age" / "thumbs"))
import design as D

HERE = pathlib.Path(__file__).resolve().parent
META = HERE.parent / "meta"
W, H = D.W, D.H
RED = (255, 45, 30)

# seven-segment layout: a b c d e f g
SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def digit(d, x, y, w, h, t, lit, dim):
    """Draw one slanted seven-segment digit; unlit segments stay faintly visible, like a real display."""
    sk = 0.12 * w
    def P(px, py):
        return (x + px + sk * (1 - py / h), y + py)
    segs = {
        "a": [(t, 0), (w - t, 0), (w - 1.6 * t, t), (1.6 * t, t)],
        "d": [(1.6 * t, h - t), (w - 1.6 * t, h - t), (w - t, h), (t, h)],
        "g": [(t, h / 2), (1.6 * t, h / 2 - t / 2), (w - 1.6 * t, h / 2 - t / 2), (w - t, h / 2), (w - 1.6 * t, h / 2 + t / 2), (1.6 * t, h / 2 + t / 2)],
        "f": [(0, t), (t, 1.6 * t), (t, h / 2 - t), (0, h / 2 - t / 2)],
        "e": [(0, h / 2 + t / 2), (t, h / 2 + t), (t, h - 1.6 * t), (0, h - t)],
        "b": [(w, t), (w, h / 2 - t / 2), (w - t, h / 2 - t), (w - t, 1.6 * t)],
        "c": [(w, h / 2 + t / 2), (w, h - t), (w - t, h - 1.6 * t), (w - t, h / 2 + t)],
    }
    for k, poly in segs.items():
        (lit if k in SEG[d] else dim).polygon([P(*p) for p in poly], fill=255)


def display(text, dw=150, dh=270, t=26, gap=34):
    """Returns (lit mask, unlit mask) for a string like '23:59:60'."""
    width = sum(dw + gap if c.isdigit() else 60 for c in text)
    lit = Image.new("L", (width + 80, dh + 40), 0); dim = Image.new("L", lit.size, 0)
    dl, dd = ImageDraw.Draw(lit), ImageDraw.Draw(dim)
    x = 20
    for c in text:
        if c.isdigit():
            digit(c, x, 20, dw, dh, t, dl, dd); x += dw + gap
        else:
            for yy in (dh * 0.32, dh * 0.72):
                dl.ellipse((x + 10, 20 + yy - 14, x + 38, 20 + yy + 14), fill=255)
            x += 60
    return lit, dim


def glitch(a, box, seed=3, slices=9, shift=40):
    """RGB split + horizontal slice offsets inside box."""
    x0, y0, x1, y1 = box
    rng = random.Random(seed)
    out = a.copy()
    out[y0:y1, x0 + 6:x1, 0] = a[y0:y1, x0:x1 - 6, 0]            # red channel pushed right
    out[y0:y1, x0:x1 - 6, 2] = a[y0:y1, x0 + 6:x1, 2]            # blue pulled left
    for _ in range(slices):
        yy = rng.randint(y0, max(y0, y1 - 20)); hh = rng.randint(6, 26); dx = rng.randint(-shift, shift)
        out[yy:yy + hh] = np.roll(out[yy:yy + hh], dx, axis=1)
    return out


def led_text(lines, size, pitch=9, dot=0.42):
    """Render text as a red dot-matrix display: sample a type mask on a grid, draw each lit cell as a round LED."""
    from PIL import ImageFont
    f = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", size)   # wide, heavy strokes survive the dot grid
    tmp = Image.new("L", (W, H * 2), 0); d = ImageDraw.Draw(tmp)
    y = 0
    for ln in lines:
        d.text((0, y), ln, font=f, fill=255); y += int(size * 1.08)
    tmp = tmp.crop(tmp.getbbox())
    gw, gh = tmp.width // pitch + 1, tmp.height // pitch + 1
    small = np.asarray(tmp.resize((gw, gh), Image.BOX), np.float32) / 255
    lit = Image.new("L", (gw * pitch, gh * pitch), 0); dim = Image.new("L", lit.size, 0)
    dl, dd = ImageDraw.Draw(lit), ImageDraw.Draw(dim)
    r = pitch * dot
    for j in range(gh):
        for i in range(gw):
            cx, cy = i * pitch + pitch / 2, j * pitch + pitch / 2
            (dl if small[j, i] > 0.5 else dd).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    return lit, dim


def glow_layer(a, mask, x, y, col, core=0.8):
    L = Image.new("L", (W, H), 0); L.paste(mask, (x, y))
    m = np.asarray(L, np.float32)[..., None] / 255
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(26)), np.float32)[..., None] / 255 * col * 0.9
    a = a + np.asarray(L.filter(ImageFilter.GaussianBlur(5)), np.float32)[..., None] / 255 * col * 0.9
    return a * (1 - m) + m * (col * (1 - core) + core * np.array([1.0, 0.82, 0.76], np.float32))


def scene(bg_name, headline, sizes, colors, name, clock_y=0.56, text_pos="top", seed=3, led=0, margin=36):
    bg = Image.open(HERE / "plates" / bg_name).convert("RGB").resize((W, H), Image.LANCZOS)
    b = D.f32(bg.filter(ImageFilter.GaussianBlur(7)))
    lum = b.mean(axis=2, keepdims=True)
    a = lum * np.array([0.55, 0.10, 0.08], np.float32) * 0.9 + 0.01           # the room, relit red by the display
    lit, dim = display("23:59:60")
    s = 0.74 * W / lit.width
    lit = lit.resize((int(lit.width * s), int(lit.height * s)), Image.LANCZOS)
    dim = dim.resize(lit.size, Image.LANCZOS)
    x = (W - lit.width) // 2; y = int(H * clock_y - lit.height / 2)
    # the clock body: a dark glossy slab behind the digits
    body = Image.new("L", (W, H), 0)
    ImageDraw.Draw(body).rounded_rectangle((x - 40, y - 30, x + lit.width + 40, y + lit.height + 30), 28, fill=255)
    bm = np.asarray(body, np.float32)[..., None] / 255
    a = a * (1 - bm * 0.85) + bm * 0.015
    L = Image.new("L", (W, H), 0); L.paste(lit, (x, y))
    Dm = Image.new("L", (W, H), 0); Dm.paste(dim, (x, y))
    l = np.asarray(L, np.float32)[..., None] / 255
    dmm = np.asarray(Dm, np.float32)[..., None] / 255
    col = np.asarray(RED, np.float32) / 255
    a += dmm * col * 0.10
    a += np.asarray(L.filter(ImageFilter.GaussianBlur(40)), np.float32)[..., None] / 255 * col * 1.3   # bloom
    a += np.asarray(L.filter(ImageFilter.GaussianBlur(8)), np.float32)[..., None] / 255 * col * 1.1
    a = a * (1 - l) + l * (col * 0.35 + 0.65 * np.array([1.0, 0.75, 0.7], np.float32))               # hot core
    # reflection of the display on the floor below
    refl = np.flipud(a[y:y + lit.height + 30]) * 0.18
    ry = y + lit.height + 34; hh = min(H - ry, refl.shape[0])
    fade = np.linspace(1, 0, hh)[:, None, None]
    a[ry:ry + hh] += refl[:hh] * fade
    a = glitch(np.clip(a, 0, 1), (0, y + int(lit.height * 0.60), W, y + int(lit.height * 0.72)), seed=seed, slices=3, shift=22)
    if led:
        tl, td = led_text(headline, sizes[0], pitch=led)
        tx = (W - tl.width) // 2; ty = margin if text_pos == "top" else H - tl.height - margin
        dm = Image.new("L", (W, H), 0); dm.paste(td, (tx, ty))
        a += np.asarray(dm, np.float32)[..., None] / 255 * col * 0.10          # unlit LEDs, faintly visible
        a = glow_layer(a, tl, tx, ty, col)
        
    else:
        t = D.text_layer(headline, sizes, 0, 0, colors, spacing=1.0, glow=(255, 60, 40))
        t = t.crop(t.getbbox())
        ty = 40 if text_pos == "top" else H - t.height - 40
        a = D.paste(a, t, (W - t.width) // 2, ty)
    D.pil(D.finish(a, shadows=(0.03, 0.0, 0.0), amount=0.2, vignette=0.55, grain=0.03)).save(META / name, quality=94)
    print("saved", name)


if __name__ == "__main__":
    scene("servers.png", ["+1 SECOND"], [152], None, "thumb_D_plus1.jpg", clock_y=0.66, led=7, margin=70)
    scene("servers2.png", ["THIS BROKE", "THE INTERNET"], [112], None, "thumb_E_broke.jpg",
          clock_y=0.28, text_pos="bottom", seed=8, led=6, margin=62)
