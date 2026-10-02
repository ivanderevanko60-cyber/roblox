"""Full voiceover for a script's **VO:** lines via OpenRouter TTS (cached: never pays twice).

python tools/vo.py <script.md> <out_dir> [model] [voice] [speed] [--only 0-5]
Writes vo_###.mp3 per line + lines.json (text, file, duration) for build_episode.py.
A line may pick its own delivery: **VO(excited):** uses en_paul_excited instead of the default voice.
Files are named by a hash of voice + text, so editing a line or its mood re-records only that line.
"""
import glob, hashlib, json, os, pathlib, re, subprocess, shutil, sys
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = next(l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text().splitlines() if l.startswith("OPENROUTER_API_KEY="))
URL = "https://openrouter.ai/api/v1/audio/speech"
FP = shutil.which("ffprobe") or glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffprobe.exe"))[0]

argv = sys.argv[1:]
only = None
if "--only" in argv:
    k = argv.index("--only"); a, b = map(int, argv[k + 1].split("-")); only = range(a, b + 1); del argv[k:k + 2]
script, out = pathlib.Path(argv[0]), pathlib.Path(argv[1])
model = argv[2] if len(argv) > 2 else "mistralai/voxtral-mini-tts-2603"
voice = argv[3] if len(argv) > 3 else "en_paul_neutral"
speed = float(argv[4]) if len(argv) > 4 else 0.92
out.mkdir(parents=True, exist_ok=True)

lines, section = [], None
for raw in script.read_text(encoding="utf8").splitlines():
    if raw.startswith("## "):
        section = raw[3:].strip()
    m = re.match(r"\*\*VO(?:\((\w+)\))?:\*\*\s*(.+)", raw)
    if m:
        v = voice.rsplit("_", 1)[0] + "_" + m.group(1) if m.group(1) else voice
        lines.append({"section": section, "text": m.group(2).strip(), "voice": v})

spent = 0
if only:
    lines = [ln for i, ln in enumerate(lines) if i in only]
for i, ln in enumerate(lines):
    h = hashlib.sha1((ln["voice"] + "|" + ln["text"]).encode()).hexdigest()[:8]
    p = out / f"vo_{i:03d}_{h}.mp3"
    if not p.exists():
        body = {"model": model, "voice": ln["voice"], "input": ln["text"], "response_format": "mp3", "speed": speed}
        r = requests.post(URL, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, json=body, timeout=300)
        if r.status_code != 200 or r.headers.get("content-type", "").startswith("application/json"):
            sys.exit(f"line {i}: {r.status_code} {r.text[:200]}")
        p.write_bytes(r.content)
        spent += len(ln["text"])
    dur = float(subprocess.check_output([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))
    ln.update(file=p.name, dur=round(dur, 3))

(out / "lines.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False), encoding="utf8")
(out / "meta.json").write_text(json.dumps({"model": model, "voice": voice, "speed": speed}, indent=1), encoding="utf8")
total = sum(l["dur"] for l in lines)
print(f"{len(lines)} lines, {total / 60:.1f} min speech, {spent} new chars (~${spent / 1e6 * 16:.3f})")
