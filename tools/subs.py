"""Subtitles (.srt) from cut/timeline.json: splits each narration line into readable chunks.

python tools/subs.py <project_dir>
"""
import json, pathlib, re, sys

PROJ = pathlib.Path(sys.argv[1]).resolve()
tl = json.loads((PROJ / "cut" / "timeline.json").read_text(encoding="utf8"))
MAX = 84          # characters per caption (two lines of ~42)


def chunks(text):
    """Split on sentence ends first, then on commas, keeping captions under MAX."""
    parts, buf = [], ""
    for piece in re.split(r"(?<=[.!?]) ", text):
        if len(piece) > MAX and buf:      # flush first, or the order gets scrambled
            parts.append(buf)
            buf = ""
        while len(piece) > MAX:
            cut = piece.rfind(",", 0, MAX)
            cut = cut + 1 if cut > MAX * 0.4 else piece.rfind(" ", 0, MAX)
            parts.append(piece[:cut].strip())
            piece = piece[cut:].strip()
        if len(buf) + len(piece) + 1 <= MAX:
            buf = (buf + " " + piece).strip()
        else:
            if buf:
                parts.append(buf)
            buf = piece
    if buf:
        parts.append(buf)
    return parts


def ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def wrap(text):
    if len(text) <= 42:
        return text
    cut = text.rfind(" ", 0, len(text) // 2 + 8)
    return text[:cut] + "\n" + text[cut + 1:]


out, n = [], 0
for ln in tl["lines"]:
    parts = chunks(ln["text"])
    total_chars = sum(len(p) for p in parts) or 1
    t = ln["start"]
    for p in parts:
        d = ln["dur"] * len(p) / total_chars
        n += 1
        out.append(f"{n}\n{ts(t)} --> {ts(t + d - 0.05)}\n{wrap(p)}\n")
        t += d
(PROJ / "meta").mkdir(exist_ok=True)
(PROJ / "meta" / "subtitles_en.srt").write_text("\n".join(out), encoding="utf8")
print(f"{n} captions -> meta/subtitles_en.srt")
