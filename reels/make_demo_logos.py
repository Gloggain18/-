"""Рисует оригинальные демо-эмблемы (заглушки) в logos/. Замените их своими PNG."""
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
S = 800

def save(name, draw_fn):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(im)); im.save(f"logos/{name}.png")

def mountain(d):
    d.polygon([(60, 620), (300, 180), (420, 380), (500, 270), (740, 620)], fill="black")
    d.text((400, 700), "TRAIL", font=ImageFont.truetype(F, 120), anchor="mm", fill="black")

def bolt(d):
    d.ellipse((80, 80, 720, 720), fill="black")
    d.ellipse((150, 150, 650, 650), fill=(0, 0, 0, 0))
    d.polygon([(450, 170), (270, 440), (390, 440), (330, 640), (540, 350), (415, 350)], fill="black")

def chevrons(d):
    for k in range(3):
        x = 120 + k * 190
        d.polygon([(x, 200), (x + 110, 200), (x + 290, 400), (x + 110, 600), (x, 600), (x + 180, 400)], fill="black")

def word(d):
    d.text((400, 400), "RUN", font=ImageFont.truetype(F, 300), anchor="mm", fill="black")
    d.rectangle((90, 560, 710, 600), fill="black")

for i, (n, f) in enumerate([("mountain", mountain), ("bolt", bolt), ("chevrons", chevrons), ("run", word)], 1):
    save(f"{i:02d}_{n}", f)
