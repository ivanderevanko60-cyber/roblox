"""Build the 30s visual test: graded stock shots + crossfades + captions + generated ambient score."""
import glob, os, pathlib, shutil, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "test"
TMP = T / "tmp"
TMP.mkdir(exist_ok=True)
FF = shutil.which("ffmpeg") or glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe"))[0]
W, H, FPS, XF = 1920, 1080, 30, 0.6

# (clip, start, duration, push direction)
SHOTS = [
    ("01_5838621.mp4", 1.0, 4.5, "in"),
    ("02_30284377.mp4", 5.0, 4.0, "out"),
    ("03_34720127.mp4", 3.0, 3.5, "in"),
    ("04_8626681.mp4", 6.0, 3.5, "in"),
    ("05_7612023.mp4", 10.0, 4.0, "out"),
    ("06_3250277.mp4", 0.5, 4.0, "in"),
    ("07_31631562.mp4", 1.0, 4.0, "in"),
    ("08_29456564.mp4", 0.5, 5.5, "out"),
]
END_CARD = 3.5

starts, t = [], 0.0
for _, _, d, _ in SHOTS:
    starts.append(t)
    t += d - XF
END_START = t
TOTAL = END_START + END_CARD

CAPTIONS = [  # (text, start, end, style)
    ("Every night, New York feeds eight million people.", 0.8, 3.6, "cap"),
    ("Behind every window, a kitchen.", 4.3, 7.0, "cap"),
    ("And somewhere, someone is keeping score.", 10.6, 15.8, "cap"),
    ("Thirteen points: an A.", starts[5] + 0.4, starts[6] - 0.2, "cap"),
    ("Fourteen: a B.", starts[6] + 0.4, starts[7] - 0.2, "cap"),
    ("One point decides what the whole city sees.", starts[7] + 0.5, END_START + 0.2, "cap"),
    ("THE LAST GOOD NUMBER", END_START + 0.6, TOTAL - 0.4, "title"),
]

GRADE = (
    "eq=contrast=1.10:saturation=0.88:gamma=0.96,"
    "colorbalance=rs=-0.04:gs=0.00:bs=0.07:rh=0.07:gh=0.02:bh=-0.05,"
    "curves=master='0/0.02 0.25/0.20 0.75/0.80 1/0.97',"
    "vignette=angle=PI/4.5,"
    "noise=alls=7:allf=t"
)
BAR = int((H - W / 2.39) / 2)


def run(args):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def render_shot(i, clip, ss, dur, direction):
    frames = int(dur * FPS)
    z = f"1.0+0.07*on/{frames}" if direction == "in" else f"1.07-0.07*on/{frames}"
    vf = (
        f"fps={FPS},scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
        f"{GRADE},setsar=1,format=yuv420p"
    )
    out = TMP / f"shot{i}.mp4"
    if out.exists():
        return out
    run(["-ss", str(ss), "-t", str(dur), "-i", str(T / "clips" / clip), "-an", "-vf", vf,
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(out)])
    return out


def caption_png(i, text, style):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if style == "title":
        f = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 64)
        spaced = "  ".join(text)
        d.text((W / 2, H / 2), spaced, font=f, fill=(235, 228, 215, 255), anchor="mm")
        d.line([(W / 2 - 60, H / 2 + 70), (W / 2 + 60, H / 2 + 70)], fill=(200, 60, 45, 255), width=3)
    else:
        f = ImageFont.truetype("C:/Windows/Fonts/georgiai.ttf", 50)
        y = H - BAR - 90
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((W / 2, y + 2), text, font=f, fill=(0, 0, 0, 255), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0, 255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, shadow)
        img = Image.alpha_composite(img, shadow)
        ImageDraw.Draw(img).text((W / 2, y), text, font=f, fill=(245, 240, 230, 255), anchor="mm")
    p = TMP / f"cap{i}.png"
    img.save(p)
    return p


def score(path):
    sr = 48000
    n = int(TOTAL * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(7)
    out = np.zeros(n)
    # A-minor pad: detuned sines with slow swells
    for hz in (110.0, 164.81, 220.0, 261.63, 329.63):
        for det in (-0.6, 0.0, 0.7):
            ph = rng.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * (hz + det) * t + ph) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + ph))
    out *= 0.035
    # Chord shift to F major under "Fourteen"
    shift = (t > starts[6]) & (t < END_START)
    out[shift] += 0.05 * np.sin(2 * np.pi * 87.31 * t[shift]) * np.minimum(1, (t[shift] - starts[6]) * 2)
    # Rain bed: smoothed noise
    rain = rng.normal(0, 1, n)
    rain = np.convolve(rain, np.ones(8) / 8, mode="same") * 0.05
    out += rain * np.clip(1 - t / (END_START + 1), 0, 1)
    # Low heartbeat pulse
    for beat in np.arange(starts[2], END_START, 1.2):
        k = (t >= beat) & (t < beat + 0.5)
        tt = t[k] - beat
        out[k] += 0.35 * np.sin(2 * np.pi * (55 - 30 * tt) * tt) * np.exp(-tt * 9)
    # Impacts on the grade reveals and end card
    for hit in (starts[5], starts[6], END_START):
        k = (t >= hit) & (t < hit + 2.5)
        tt = t[k] - hit
        out[k] += 0.6 * np.sin(2 * np.pi * (48 - 12 * tt) * tt) * np.exp(-tt * 2.2)
    fade = np.minimum(1, np.minimum(t / 1.5, (TOTAL - t) / 2.0))
    out = np.tanh(out * fade * 1.4) * 0.8
    stereo = np.stack([out, np.roll(out, 240)], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())


def main():
    shots = [render_shot(i, *s) for i, s in enumerate(SHOTS)]
    print("shots done")
    audio = TMP / "score.wav"
    score(audio)

    inputs, fc = [], []
    for s in shots:
        inputs += ["-i", str(s)]
    inputs += ["-f", "lavfi", "-t", str(END_CARD), "-i", f"color=c=black:s={W}x{H}:r={FPS}"]
    caps = [caption_png(i, c[0], c[3]) for i, c in enumerate(CAPTIONS)]
    for p in caps:
        inputs += ["-loop", "1", "-t", str(TOTAL), "-framerate", str(FPS), "-i", str(p)]
    inputs += ["-i", str(audio)]

    n = len(shots)
    for k in range(n + 1):
        fc.append(f"[{k}:v]settb=AVTB,fps={FPS},format=yuv420p,setsar=1[v{k}]")
    prev, durs = "[v0]", [s[2] for s in SHOTS] + [END_CARD]
    acc = durs[0]
    for k in range(1, n + 1):
        off = acc - XF * k
        lbl = f"[x{k}]"
        fc.append(f"{prev}[v{k}]xfade=transition=fade:duration={XF}:offset={off:.3f}{lbl}")
        prev, acc = lbl, acc + durs[k]
    # Letterbox bars
    fc.append(f"{prev}drawbox=y=0:w=iw:h={BAR}:color=black:t=fill,drawbox=y=ih-{BAR}:w=iw:h={BAR}:color=black:t=fill[base]")
    prev = "[base]"
    for i, (_, a, b, _) in enumerate(CAPTIONS):
        src = n + 1 + i
        fc.append(f"[{src}:v]format=rgba,fade=in:st={a}:d=0.5:alpha=1,fade=out:st={b - 0.5}:d=0.5:alpha=1[c{i}]")
        fc.append(f"{prev}[c{i}]overlay=enable='between(t,{a},{b})':shortest=0[o{i}]")
        prev = f"[o{i}]"
    fc.append(f"{prev}trim=duration={TOTAL:.3f},format=yuv420p[vout]")

    out = T / "test_30s.mp4"
    run([*inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n + 1 + len(CAPTIONS)}:a",
         "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    print("saved", out, f"{TOTAL:.1f}s")


if __name__ == "__main__":
    main()
