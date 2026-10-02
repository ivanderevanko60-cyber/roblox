"""Pexels video search / download helper.

search:   python tools/pexels.py search "<query>" [n] [preview_dir] -> prints candidates, saves preview frames
download: python tools/pexels.py get <video_id> <out.mp4>  -> downloads the best <=1920px file
"""
import os, sys, json, pathlib, requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = next(l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text().splitlines() if l.startswith("PEXELS_API_KEY="))
H = {"Authorization": KEY}
API = "https://api.pexels.com/videos"


def best_file(video, min_w=1920):
    """Smallest landscape mp4 that is at least 1080p wide (4K is fine), else the largest available."""
    files = [f for f in video["video_files"] if f.get("width") and f["file_type"] == "video/mp4" and f["width"] >= f["height"]]
    big = [f for f in files if f["width"] >= min_w]
    return min(big, key=lambda f: f["width"]) if big else max(files, key=lambda f: f["width"])


def search(query, n=6, prev=None, tag=None):
    r = requests.get(f"{API}/search", headers=H, params={"query": query, "per_page": n, "orientation": "landscape", "size": "large"}, timeout=30)
    r.raise_for_status()
    prev = pathlib.Path(prev) if prev else ROOT / "test" / "previews"
    prev.mkdir(parents=True, exist_ok=True)
    for k, v in enumerate(r.json()["videos"]):
        f = best_file(v)
        pic = v["video_pictures"][len(v["video_pictures"]) // 2]["picture"]
        name = f"{tag}{k}_{v['id']}" if tag else str(v["id"])
        (prev / f"{name}.jpg").write_bytes(requests.get(pic, timeout=30).content)
        row = json.dumps({"tag": tag, "q": query, "id": v["id"], "dur": v["duration"], "w": f["width"], "by": v["user"]["name"], "url": v["url"]})
        print(row)
        if tag:
            with open(prev / "index.jsonl", "a", encoding="utf8") as fh:
                fh.write(row + "\n")


def get(vid, out):
    r = requests.get(f"{API}/videos/{vid}", headers=H, timeout=30)
    r.raise_for_status()
    f = best_file(r.json())
    with requests.get(f["link"], stream=True, timeout=120) as s, open(out, "wb") as fh:
        for chunk in s.iter_content(1 << 20):
            fh.write(chunk)
    print(vid, f["width"], f"{os.path.getsize(out) / 1e6:.1f} MB")


def photos(query, n=6, prev=None, tag=None):
    """Still photos (for thumbnails): saves preview jpgs and prints the originals' URLs."""
    r = requests.get("https://api.pexels.com/v1/search", headers=H,
                     params={"query": query, "per_page": n, "orientation": "landscape", "size": "large"}, timeout=30)
    r.raise_for_status()
    prev = pathlib.Path(prev) if prev else ROOT / "research" / "photos"
    prev.mkdir(parents=True, exist_ok=True)
    for k, p in enumerate(r.json()["photos"]):
        name = f"{tag}{k}_{p['id']}" if tag else str(p["id"])
        (prev / f"{name}.jpg").write_bytes(requests.get(p["src"]["large"], timeout=30).content)
        print(json.dumps({"tag": tag, "id": p["id"], "w": p["width"], "h": p["height"],
                          "by": p["photographer"], "orig": p["src"]["original"]}))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6, sys.argv[4] if len(sys.argv) > 4 else None,
               sys.argv[5] if len(sys.argv) > 5 else None)
    elif cmd == "photos":
        photos(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6,
               sys.argv[4] if len(sys.argv) > 4 else None, sys.argv[5] if len(sys.argv) > 5 else None)
    elif cmd == "get":
        get(sys.argv[2], sys.argv[3])
