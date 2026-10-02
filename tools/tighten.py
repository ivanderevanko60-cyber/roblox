"""Shorten the long silences a TTS model leaves inside a sentence (and that slowing it down stretches further).

python tools/tighten.py <in.mp3> <out.mp3> [max_pause=0.15]
Any quiet stretch longer than max_pause is cut down to max_pause, by removing its middle with short fades,
so breaths at the edges stay natural. Leading/trailing silence is trimmed to 0.05 s.
"""
import subprocess, sys
import numpy as np

SR = 48000


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.float32).copy()


def save(x, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-b:a", "192k", path], input=x.astype(np.float32).tobytes(), check=True)


def tighten(x, max_pause=0.15, thresh_db=-38.0, win=0.01):
    n = int(SR * win)
    frames = len(x) // n
    rms = np.sqrt(np.mean(x[:frames * n].reshape(frames, n) ** 2, axis=1) + 1e-12)
    quiet = 20 * np.log10(rms / (np.max(rms) + 1e-12)) < thresh_db
    # runs of quiet frames
    runs, k = [], 0
    while k < frames:
        if quiet[k]:
            j = k
            while j < frames and quiet[j]:
                j += 1
            runs.append((k, j))
            k = j
        else:
            k += 1
    keep = int(max_pause / win)
    fade = int(SR * 0.008)
    out, pos = [], 0
    for a, b in runs:
        lead_or_tail = a == 0 or b == frames
        limit = 5 if lead_or_tail else keep
        if b - a <= limit:
            continue
        # keep the first and last halves of the allowed pause, drop the middle
        cut_a = (a + limit // 2) * n
        cut_b = (b - (limit - limit // 2)) * n
        seg = x[pos:cut_a].copy()
        if len(seg) > fade:
            seg[-fade:] *= np.linspace(1, 0, fade)
        out.append(seg)
        pos = cut_b
        nxt = x[pos:pos + fade].copy()
        if len(nxt) == fade:
            x = x.copy(); x[pos:pos + fade] = nxt * np.linspace(0, 1, fade)
    out.append(x[pos:])
    return np.concatenate(out)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    mp = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
    save(tighten(load(src), mp), dst)
