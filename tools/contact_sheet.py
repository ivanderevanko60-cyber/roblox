"""Contact sheet: python tools/contact_sheet.py <preview_dir> <out.jpg> [cols]  (labels = file names)"""
import glob, os, sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
fs = sorted(glob.glob(os.path.join(src, "*.jpg")))
tw, th = 384, 216
sheet = Image.new("RGB", (cols * tw, ((len(fs) + cols - 1) // cols) * th))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGB"); im.thumbnail((tw, th))
    x, y = i % cols * tw, i // cols * th
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + 170, y + 18], fill="black")
    d.text((x + 4, y + 3), os.path.splitext(os.path.basename(f))[0], fill="yellow")
sheet.save(out, quality=85)
print(len(fs), "->", out)
