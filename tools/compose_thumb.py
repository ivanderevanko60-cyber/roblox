"""Compose the final thumbnail: glow + vignette + headline + grade cards."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

base_path, out_path = sys.argv[1], sys.argv[2]
W, H = 1280, 720
img = Image.open(base_path).convert("RGB").resize((W, H))

# Glow: blur the bright red areas and screen them back on
r, g, b = img.split()
mask = ImageChops.subtract(r, g).point(lambda v: 255 if v > 90 else 0)
glow_src = Image.composite(img, Image.new("RGB", (W, H)), mask)
glow = glow_src.filter(ImageFilter.GaussianBlur(40))
img = ImageChops.screen(img, glow)

# Left-side darkening so the headline reads
shade = Image.new("L", (W, H))
ImageDraw.Draw(shade).rectangle([0, 0, W, H], fill=0)
for x in range(W):
    a = int(max(0, 200 * (1 - x / (W * 0.55))))
    ImageDraw.Draw(shade).line([(x, 0), (x, H)], fill=a)
img = Image.composite(Image.new("RGB", (W, H)), img, shade)

d = ImageDraw.Draw(img)
black = "C:/Windows/Fonts/ariblk.ttf"

def grade_card(x, y, letter, color, w=150, h=190, dim=False):
    d.rounded_rectangle([x, y, x + w, y + h], 10, fill=(236, 236, 230), outline=(20, 20, 20), width=4)
    f = ImageFont.truetype(black, 120)
    d.text((x + w / 2, y + h / 2 + 6), letter, font=f, fill=color, anchor="mm")
    small = ImageFont.truetype(black, 16)
    d.text((x + w / 2, y + 22), "GRADE", font=small, fill=(40, 40, 40), anchor="mm")

# Grade cards: A = 13 points, B = 14 points
grade_card(70, 70, "A", (20, 60, 160))
d.text((145, 290), "13 pts", font=ImageFont.truetype(black, 30), fill=(200, 200, 200), anchor="mm")
grade_card(260, 70, "B", (20, 120, 50))
d.text((335, 290), "14 pts", font=ImageFont.truetype(black, 30), fill=(255, 70, 60), anchor="mm")

# Headline, two lines, with a hard shadow
head = ImageFont.truetype(black, 84)
for i, (line, col) in enumerate((("ONE POINT", (255, 255, 255)), ("TOO MANY", (255, 214, 0)))):
    y = 400 + i * 105
    d.text((66, y + 5), line, font=head, fill=(0, 0, 0))
    d.text((60, y), line, font=head, fill=col)

img.save(out_path, quality=95)
print("saved", out_path)
