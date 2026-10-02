"""Assemble an episode rough cut from a VO line list + edl.py.

python tools/build_episode.py <project_dir> [vo_dir]

project_dir must contain edl.py (EDL, SECTIONS, SOURCES) and footage/clips/*.mp4.
Output: <project_dir>/cut/rough_cut.mp4
"""
import glob, hashlib, importlib.util, json, os, pathlib, random, shutil, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ = pathlib.Path(sys.argv[1]).resolve()
VO = PROJ / (sys.argv[2] if len(sys.argv) > 2 else "vo_draft")
CUT = PROJ / "cut"
SEG = CUT / "segments"
OVL = CUT / "overlays"
for d in (CUT, SEG, OVL):
    d.mkdir(parents=True, exist_ok=True)

_ff_dir = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin"))
FF = shutil.which("ffmpeg") or os.path.join(_ff_dir[0], "ffmpeg.exe")
FP = shutil.which("ffprobe") or os.path.join(_ff_dir[0], "ffprobe.exe")

W, H, FPS = 1920, 1080, 30
GAP, LEAD, SECTION_CARD, TAIL = 0.45, 0.8, 2.6, 2.0
BAR = 60  # subtle 2:1 letterbox
GRADE = (
    "eq=contrast=1.08:saturation=0.9:gamma=0.97,"
    "colorbalance=rs=-0.03:bs=0.05:rh=0.05:gh=0.01:bh=-0.04,"
    "curves=master='0/0.02 0.25/0.21 0.75/0.79 1/0.97',"
    "vignette=angle=PI/5,noise=alls=5:allf=t"
)

spec = importlib.util.spec_from_file_location("edl", PROJ / "edl.py")
edl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edl)
lines = json.loads((VO / "lines.json").read_text(encoding="utf8"))


def run(args):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


_dur = {}
def probe(p):
    if p not in _dur:
        _dur[p] = float(subprocess.check_output([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))
    return _dur[p]


def source_path(name):
    if name in edl.SOURCES:
        return PROJ / edl.SOURCES[name]
    return PROJ / "footage" / "clips" / f"{name}.mp4"


def render_segment(shot, dur, idx):
    """Render one graded, gently moving shot of exactly `dur` seconds. Cached by content."""
    rev = shot.endswith("!r")
    shot = shot[:-2] if rev else shot
    name, _, start = shot.partition("@")
    stamp = int(source_path(name).stat().st_mtime) if name != "black" else 0
    key = hashlib.md5(f"{name}|{start}|{rev}|{dur:.3f}|{idx % 2}|{stamp}|v2".encode()).hexdigest()[:12]
    out = SEG / f"{name}_{key}.mp4"
    if out.exists():
        return out
    if name == "black":
        run(["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)])
        return out
    src = source_path(name)
    if src.suffix.lower() in (".jpg", ".jpeg", ".png"):      # archive photo -> slow Ken Burns move
        frames = int(round(dur * FPS))
        z = f"1.0+0.10*on/{frames}" if idx % 2 == 0 else f"1.10-0.10*on/{frames}"
        vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},{GRADE},setsar=1,format=yuv420p")
        run(["-loop", "1", "-t", f"{dur:.3f}", "-i", str(src), "-vf", vf, "-frames:v", str(frames),
             "-c:v", "libx264", "-crf", "17", "-preset", "fast", str(out)])
        return out
    length = probe(src)
    slow = 1.0
    if length < dur:
        ss, slow = 0.0, dur / length * 1.001
    else:
        ss = float(start) if start else max(0.0, (length - dur) / 2)
        ss = min(ss, length - dur)
    take = dur / slow
    frames = int(round(dur * FPS))
    z = f"1.0+0.06*on/{frames}" if idx % 2 == 0 else f"1.06-0.06*on/{frames}"
    vf = []
    if rev:
        vf.append("reverse")
    if slow > 1:
        vf.append(f"setpts=PTS*{slow:.4f}")
    vf += [
        f"fps={FPS}",
        f"scale={int(W * 1.5)}:{int(H * 1.5)}:force_original_aspect_ratio=increase,crop={int(W * 1.5)}:{int(H * 1.5)}",
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}",
        GRADE, "setsar=1", "format=yuv420p",
    ]
    run(["-ss", f"{ss:.3f}", "-t", f"{take:.3f}", "-i", str(src), "-an", "-vf", ",".join(vf),
         "-frames:v", str(frames), "-c:v", "libx264", "-crf", "17", "-preset", "fast", str(out)])
    return out


def overlay_png(kind, text, i):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    serif = "C:/Windows/Fonts/georgia.ttf"
    italic = "C:/Windows/Fonts/georgiai.ttf"
    if kind in ("title", "section"):
        size = 58 if kind == "title" else 46
        f = ImageFont.truetype(serif, size)
        txt = " ".join(text) if kind == "title" else text
        pos, anchor = (W / 2, H / 2), "mm"
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))    # soft dark band so the card reads over footage
        ImageDraw.Draw(band).rectangle((0, H / 2 - 110, W, H / 2 + 110), fill=(0, 0, 0, 150))
        img = Image.alpha_composite(img, band.filter(ImageFilter.GaussianBlur(60)))
    elif kind == "lower":
        f = ImageFont.truetype(italic, 38)
        txt, pos, anchor = text, (110, H - BAR - 110), "ls"
    elif kind == "big":
        f = ImageFont.truetype("C:/Windows/Fonts/cambria.ttc", 120, index=0)
        txt, pos, anchor = text, (W / 2, H / 2), "mm"
    else:  # small
        f = ImageFont.truetype("C:/Windows/Fonts/cambriai.ttf", 40)
        txt, pos, anchor = text, (W / 2, H - BAR - 120), "mm"
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text(pos, txt, font=f, fill=(0, 0, 0, 255), anchor=anchor, stroke_width=12, stroke_fill=(0, 0, 0, 255))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    d.text(pos, txt, font=f, fill=(242, 236, 224, 255), anchor=anchor)
    if kind in ("title", "section"):
        d.line([(W / 2 - 50, H / 2 + 55), (W / 2 + 50, H / 2 + 55)], fill=(200, 60, 45, 255), width=3)
    if kind == "lower":
        d.line([(110, H - BAR - 90), (190, H - BAR - 90)], fill=(200, 60, 45, 255), width=3)
    p = OVL / f"ov_{i:03d}.png"
    img.save(p)
    return p


def split_span(span, n, seed, lo=2.0, hi=8.0):
    """Uneven shot lengths inside one narration line: documentary rhythm, not a metronome."""
    if n == 1:
        return [span]
    rng = random.Random(seed)
    w = [rng.uniform(0.7, 1.4) for _ in range(n)]
    durs = [span * x / sum(w) for x in w]
    for _ in range(6):                     # clamp, then give the slack back to the free shots
        fixed = [min(max(d, lo), hi) for d in durs]
        slack = span - sum(fixed)
        free = [k for k, d in enumerate(durs) if lo < fixed[k] < hi]
        if abs(slack) < 0.01 or not free:
            durs = fixed
            break
        for k in free:
            fixed[k] += slack / len(free)
        durs = fixed
    scale = span / sum(durs)
    return [d * scale for d in durs]


def music_bed(path, total):
    """Placeholder ambient score (replace with licensed music for the real cut)."""
    sr = 48000
    n = int(total * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(11)
    out = np.zeros(n)
    chords = [(110.0, 164.81, 220.0, 261.63), (87.31, 130.81, 174.61, 220.0), (98.0, 146.83, 196.0, 246.94), (82.41, 123.47, 164.81, 207.65)]
    seg = 16.0
    for k in range(int(total // seg) + 1):
        a, b = k * seg, (k + 1) * seg + 4
        m = (t >= a) & (t < b)
        env = np.clip(np.minimum((t[m] - a) / 4, (b - t[m]) / 4), 0, 1)
        for hz in chords[k % len(chords)]:
            for det in (-0.5, 0.0, 0.6):
                out[m] += np.sin(2 * np.pi * (hz + det) * t[m] + rng.uniform(0, 6.28)) * env
    out *= 0.02
    out = np.tanh(out * np.minimum(1, np.minimum(t / 3, (total - t) / 3)))
    stereo = np.stack([out, np.roll(out, 300)], axis=1) * 0.6
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())



def sfx_track(path, total, booms, whooshes, tick_spans):
    """Synthesised sound design: sub booms on section cards, airy whooshes on cuts, a ticking motif."""
    sr = 48000
    n = int(total * sr) + sr
    out = np.zeros(n)
    rng = np.random.default_rng(5)

    def at(sec):
        return int(sec * sr)

    for b in booms:                       # low hit: 55 Hz -> 28 Hz sweep with a short noise transient
        i = at(b)
        t = np.arange(int(2.6 * sr)) / sr
        env = np.exp(-t * 1.6)
        body = np.sin(2 * np.pi * (55 - 10 * t) * t) * env
        click = rng.normal(0, 1, len(t)) * np.exp(-t * 60) * 0.25
        seg = (body * 0.9 + click) * 0.55
        out[i:i + len(seg)] += seg[:max(0, min(len(seg), n - i))]

    for w in whooshes:                    # noise swell that lands on the cut
        i = max(0, at(w - 0.6))
        t = np.arange(int(0.9 * sr)) / sr
        noise = rng.normal(0, 1, len(t))
        k = np.ones(40) / 40               # crude low-pass so it reads as air, not hiss
        noise = np.convolve(noise, k, mode="same")
        env = (t / t[-1]) ** 2 * np.exp(-np.maximum(0, t - 0.6) * 14)
        seg = noise * env * 0.22
        out[i:i + len(seg)] += seg[:max(0, min(len(seg), n - i))]

    for a, b in tick_spans:               # clock motif, one tick per second, fading in and out
        for k, tick in enumerate(np.arange(a, b, 1.0)):
            i = at(tick)
            t = np.arange(int(0.16 * sr)) / sr
            body = (np.sin(2 * np.pi * 2100 * t) + 0.6 * np.sin(2 * np.pi * 3300 * t)) * np.exp(-t * 80)
            body += rng.normal(0, 1, len(t)) * np.exp(-t * 300) * 0.4
            fade = min(1.0, (tick - a) / 1.5, (b - tick) / 1.5)
            seg = body * 0.12 * fade * (1.0 if k % 2 == 0 else 0.85)
            out[i:i + len(seg)] += seg[:max(0, min(len(seg), n - i))]

    out = np.tanh(out * 1.2)[:int(total * sr)]
    stereo = np.stack([out, np.roll(out, 120)], axis=1) * 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())


def q(seconds):
    """Snap to whole frames: otherwise 100+ shots accumulate drift and titles/voice slide off."""
    return round(seconds * FPS) / FPS


def main():
    # Plan: what to show, in order. Real timings come later, from the rendered segments,
    # because encoders round frame counts and 100+ shots would otherwise drift apart.
    timeline, plan = [], []
    for i, ln in enumerate(lines):
        on_footage = getattr(edl, "CARDS_ON_FOOTAGE", False)   # no black: picture from frame one, titles over footage
        if i == 0 and not on_footage:
            plan.append({"kind": "lead", "idx": len(timeline)})
            timeline.append(("black", LEAD))
        if i in edl.SECTIONS:
            if on_footage:
                plan.append({"kind": "card_over", "idx": len(timeline), "title": edl.SECTIONS[i]})
            else:
                plan.append({"kind": "card", "idx": len(timeline), "title": edl.SECTIONS[i]})
                timeline.append(("black", SECTION_CARD))
        shots, ov = edl.EDL[i]
        span = q(ln["dur"] + getattr(edl, "GAP", GAP))   # an EDL may tighten the breath between lines
        if i == len(lines) - 1:
            span = q(span + TAIL + 2.5)
        lo = 1.1 if i in getattr(edl, "FAST_LINES", ()) else 2.0   # punchy cutting where the EDL asks for it
        durs = [q(d) for d in split_span(span, len(shots), i, lo=lo)]
        durs[-1] = q(span - sum(durs[:-1]))
        plan.append({"kind": "line", "line": i, "idx": len(timeline), "n": len(shots), "ov": ov,
                     "black_tail": shots[-1] == "black"})
        for s, d in zip(shots, durs):
            timeline.append((s, d))
    print(f"planned {len(timeline)} shots")
    # no repeated footage: every source may be used once (except MULTI_USE, which must differ by in-point)
    seen = {}
    for s, _ in timeline:
        base = s[:-2] if s.endswith("!r") else s
        name = base.partition("@")[0]
        key = base if name in getattr(edl, "MULTI_USE", {"black"}) else name
        if name != "black" and key in seen:
            sys.exit(f"repeated shot: {s}")
        seen[key] = True
    missing = sorted({s.partition("@")[0] for s, _ in timeline if s != "black" and not source_path(s.partition("@")[0].replace("!r", "")).exists()})
    prerender = os.environ.get("PRERENDER")
    if missing and not prerender:
        sys.exit(f"missing sources: {missing}")

    segs = []
    for k, (s, d) in enumerate(timeline):
        if prerender and s.partition("@")[0] in missing:
            continue
        segs.append(render_segment(s, d, k))
        if k % 20 == 0:
            print(f"  segment {k}/{len(timeline)}", flush=True)
    if prerender:
        print(f"prerendered {len(segs)} segments; waiting on {missing}")
        return
    lst = CUT / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf8")
    raw = CUT / "video_raw.mp4"
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)])

    # Actual segment lengths -> exact cut times for titles, voice and sound design.
    seg_dur = [probe(p) for p in segs]
    starts, acc = [], 0.0
    for d in seg_dur:
        starts.append(acc)
        acc += d
    total = probe(raw)
    overlays, vo_at, booms, whooshes, tick_spans = [], [], [], [], []
    for item in plan:
        k = item["idx"]
        if item["kind"] == "card":
            a = starts[k]
            overlays.append(("section", item["title"], a + 0.3, a + seg_dur[k] - 0.3))
            booms.append(a + 0.25)
            whooshes.append(a)
        elif item["kind"] == "card_over":
            a = starts[k]
            overlays.append(("section", item["title"], a + 0.15, a + 2.6))
            whooshes.append(a)
        elif item["kind"] == "line":
            i, n = item["line"], item["n"]
            t0, span = starts[k], sum(seg_dur[k:k + n])
            vo_at.append((VO / lines[i]["file"], t0))
            if item["ov"]:
                kind, text = item["ov"]
                if kind == "title" and item["black_tail"]:
                    a = starts[k + n - 1]          # title sits on the trailing black shot
                    overlays.append((kind, text, a + 0.3, t0 + span - 0.2))
                else:
                    overlays.append((kind, text, t0 + 0.4, t0 + span - 0.3))
            for j in range(n):
                if seg_dur[k + j] >= 3.0 and starts[k + j] > LEAD + 1:
                    whooshes.append(starts[k + j])
            if i in getattr(edl, "TICKS", ()):
                tick_spans.append((t0 + 0.5, t0 + span - 0.5))
            if i in getattr(edl, "BOOMS", ()):
                booms.append(t0 + 0.2)
    print(f"cut is {total / 60:.2f} min")

    # timing manifest: subtitles/chapters are generated from this, so they can never drift
    (CUT / "timeline.json").write_text(json.dumps({
        "total": total,
        "lines": [{"i": k, "start": round(at, 3), "dur": lines[k]["dur"], "text": lines[k]["text"],
                   "section": lines[k].get("section")} for k, (_, at) in enumerate(vo_at)],
        "sections": [{"title": t, "start": round(a, 3)} for kind, t, a, _ in overlays if kind == "section"],
    }, indent=1, ensure_ascii=False), encoding="utf8")

    music = CUT / "music.wav"
    music_bed(music, total)
    sfx = CUT / "sfx.wav"
    sfx_track(sfx, total, booms, whooshes, tick_spans)

    # Pass 1: burn letterbox + overlay cards onto the cut (video only).
    vinputs = ["-i", str(raw)]
    fc = [f"[0:v]drawbox=y=0:w=iw:h={BAR}:color=black:t=fill,drawbox=y=ih-{BAR}:w=iw:h={BAR}:color=black:t=fill[b0]"]
    prev = "[b0]"
    for j, (kind, text, a, b) in enumerate(overlays):
        vinputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.3f}", "-i", str(overlay_png(kind, text, j))]
        idx = j + 1
        fc.append(f"[{idx}:v]format=rgba,fade=in:st={a:.3f}:d=0.6:alpha=1,fade=out:st={b - 0.6:.3f}:d=0.6:alpha=1[o{j}]")
        fc.append(f"{prev}[o{j}]overlay=enable='between(t,{a:.3f},{b:.3f})'[b{j + 1}]")
        prev = f"[b{j + 1}]"
    fc.append(f"{prev}trim=duration={total:.3f},format=yuv420p[vout]")
    vscript = CUT / "filter_video.txt"
    vscript.write_text(";\n".join(fc), encoding="utf8")
    titled = CUT / "video_titled.mp4"
    run([*vinputs, "-/filter_complex", str(vscript), "-map", "[vout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(titled)])
    print("video done")

    # Pass 2: narration bus (ducks the music) + music + sound design -> one audio file.
    ainputs = ["-i", str(music), "-i", str(sfx)]
    amix, labels = [], []
    for k, (f, at) in enumerate(vo_at):
        ainputs += ["-i", str(f)]
        ms = int(at * 1000)
        amix.append(f"[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{k}]")
        labels.append(f"[v{k}]")
    amix.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,"
                "loudnorm=I=-16:TP=-2:LRA=9,asplit=2[vo][key]")
    amix.append("[0:a]volume=0.30[musraw]")
    amix.append("[musraw][key]sidechaincompress=threshold=0.02:ratio=8:attack=8:release=450:makeup=1[mus]")
    amix.append("[1:a]volume=0.55[sfxb]")
    amix.append("[vo][mus][sfxb]amix=inputs=3:normalize=0:duration=first,"
                "alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    ascript = CUT / "filter_audio.txt"
    ascript.write_text(";\n".join(amix), encoding="utf8")
    mixed = CUT / "audio_mix.m4a"
    run([*ainputs, "-/filter_complex", str(ascript), "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:a", "aac", "-b:a", "192k", str(mixed)])
    print("audio done")

    out = CUT / "rough_cut.mp4"
    run(["-i", str(titled), "-i", str(mixed), "-map", "0:v", "-map", "1:a", "-c", "copy",
         "-shortest", "-movflags", "+faststart", str(out)])
    print("saved", out)
    for tmp in (raw, titled):   # ~5 GB of intermediates per episode; rough_cut.mp4 holds the same picture
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
