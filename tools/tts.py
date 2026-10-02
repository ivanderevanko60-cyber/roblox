"""OpenRouter text-to-speech.

samples: python tools/tts.py samples <out_dir>            -> one file per candidate voice
line:    python tools/tts.py say <model> <voice> <out.mp3> <text>
"""
import glob, os, pathlib, shutil, subprocess, sys, requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = next(l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text().splitlines() if l.startswith("OPENROUTER_API_KEY="))
URL = "https://openrouter.ai/api/v1/audio/speech"
_ff = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe"))
FF = shutil.which("ffmpeg") or _ff[0]

# label -> (model, voice, notes)
CANDIDATES = {
    "minimax_hd": ("minimax/speech-2.8-hd", "English_expressive_narrator", "premium, $0.67/episode"),
    "mai_harper": ("microsoft/mai-voice-2", "en-US-Harper:MAI-Voice-2", "$0.15/episode"),
    "grok_leo": ("x-ai/grok-voice-tts-1.0", "leo", "$0.10/episode"),
    "grok_rex": ("x-ai/grok-voice-tts-1.0", "rex", "$0.10/episode"),
    "gemini_orus": ("google/gemini-3.1-flash-tts-preview", "Orus", "steerable by prompt"),
    "aura_atlas": ("deepgram/aura-2", "aura-2-atlas-en", "$0.20/episode"),
    "voxtral_paul": ("mistralai/voxtral-mini-tts-2603", "en_paul_neutral", "$0.11/episode"),
}

SAMPLE = ("Right now, your head is older than your feet. Not by much. "
          "Over an entire lifetime, the difference adds up to less than a tenth of a millionth of a second. "
          "But it's real. It has been measured.")


def speak(model, voice, out, text, instruction=None):
    if pathlib.Path(out).exists() and os.environ.get("TTS_FORCE") != "1":
        return pathlib.Path(out)   # never pay twice for the same file
    pcm = model.startswith("google/")
    body = {"model": model, "voice": voice, "input": (f"[{instruction}] " if instruction and pcm else "") + text,
            "response_format": "pcm" if pcm else "mp3"}
    r = requests.post(URL, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, json=body, timeout=300)
    if r.status_code != 200 or r.headers.get("content-type", "").startswith("application/json"):
        raise RuntimeError(f"{model}: {r.status_code} {r.text[:200]}")
    out = pathlib.Path(out)
    if pcm:
        raw = out.with_suffix(".pcm")
        raw.write_bytes(r.content)
        subprocess.run([FF, "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw), str(out)], check=True)
        raw.unlink()
    else:
        out.write_bytes(r.content)
    return out


def samples(out_dir):
    d = pathlib.Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    ok = []
    for label, (model, voice, note) in CANDIDATES.items():
        try:
            target = d / f"{label}.mp3"
            cached = target.exists()
            p = speak(model, voice, target, SAMPLE, instruction="calm documentary narration")
            print(f"{'CACHED' if cached else 'OK':6} {label:14} {note}")
            ok.append((label, p))
        except Exception as e:
            print(f"FAIL {label:14} {e}")
    if ok:  # one file, 1 s gaps, normalised; mp3s differ in sample rate so mix through a filter graph
        args, fc, labels = [], [], []
        for i, (_, p) in enumerate(ok):
            args += ["-i", str(p)]
            fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur=1[a{i}]")
            labels.append(f"[a{i}]")
        fc.append("".join(labels) + f"concat=n={len(ok)}:v=0:a=1,loudnorm=I=-16[out]")
        subprocess.run([FF, "-y", "-loglevel", "error", *args, "-filter_complex", ";".join(fc),
                        "-map", "[out]", "-ar", "48000", str(d / "all_voices.mp3")], check=True)
        print("order:", ", ".join(l for l, _ in ok))


if __name__ == "__main__":
    if sys.argv[1] == "samples":
        samples(sys.argv[2])
    else:
        speak(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
