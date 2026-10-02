"""Draft voiceover from a script's **VO:** lines (edge-tts, placeholder only).

python tools/draft_vo.py <script.md> <out_dir> [voice]
Writes vo_###.mp3 per line and lines.json with text + duration.
"""
import asyncio, json, pathlib, re, subprocess, sys, shutil, glob, os
import edge_tts

script, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
voice = sys.argv[3] if len(sys.argv) > 3 else "en-US-ChristopherNeural"
out.mkdir(parents=True, exist_ok=True)
FFPROBE = shutil.which("ffprobe") or glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffprobe.exe"))[0]

lines, section = [], None
for raw in script.read_text(encoding="utf8").splitlines():
    if raw.startswith("## "):
        section = raw[3:].strip()
    m = re.match(r"\*\*VO(?:\(\w+\))?:\*\*\s*(.+)", raw)
    if m:
        lines.append({"section": section, "text": m.group(1).strip()})


async def synth(i, text):
    path = out / f"vo_{i:03d}.mp3"
    if not path.exists():
        await edge_tts.Communicate(text, voice, rate="-6%").save(str(path))
    return path


async def main():
    for i, ln in enumerate(lines):
        p = await synth(i, ln["text"])
        dur = float(subprocess.check_output([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))
        ln.update(file=p.name, dur=round(dur, 3))
    (out / "lines.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False), encoding="utf8")
    total = sum(l["dur"] for l in lines)
    print(f"{len(lines)} lines, {total / 60:.1f} min of speech")


asyncio.run(main())
