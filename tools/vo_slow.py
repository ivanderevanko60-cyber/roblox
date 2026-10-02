"""Slow the paid narration to documentary pace (Voxtral ignores its speed parameter).

python tools/vo_slow.py <vo_dir> <out_dir> [tempo]
Reads lines.json from vo_dir, writes the slowed files and a new lines.json with the real durations.
"""
import json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import tighten

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
tempo = sys.argv[3] if len(sys.argv) > 3 else "0.80"
out.mkdir(parents=True, exist_ok=True)
AF = f"rubberband=tempo={tempo}:pitchq=quality,highpass=f=70,acompressor=threshold=0.15:ratio=3:attack=8:release=180"

lines = json.loads((src / "lines.json").read_text(encoding="utf8"))
for ln in lines:
    p = out / ln["file"]
    if not p.exists():
        slow = p.with_suffix(".slow.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src / ln["file"]), "-af", AF, str(slow)], check=True)
        tighten.save(tighten.tighten(tighten.load(str(slow))), str(p))   # the model's long mid-sentence pauses, cut down
        slow.unlink()
    ln["dur"] = round(float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])), 3)
(out / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf8")
print(f"{len(lines)} lines, {sum(l['dur'] for l in lines) / 60:.1f} min")
