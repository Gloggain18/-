"""Зацикленное видео: логотипы — «прозрачное стекло в белом ободке» — крутятся
на фоне ночного леса (или чёрного фона / своей картинки). Формат 1080x1920.

Запуск:
  python logo_spin.py --logos logos/ --bg forest --out spin.mp4 --per 3
  --bg: forest | black | путь_к_картинке.jpg
Логотипы: PNG с прозрачностью, либо тёмный логотип на светлом фоне (PNG/JPG).
Порядок — по имени файла (01_..., 02_...).
"""
import argparse
import glob
import os

import numpy as np
from moviepy import VideoClip
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
LOGO = 760          # размер логотипа на экране
ZOOM = 1.08
RIM = 9             # толщина белого ободка
rng = np.random.default_rng(7)


# ---------- фон: ночной туманный лес ----------
def pine(d, x, base, h, color):
    w = h * 0.42
    for k in range(5):
        top = base - h + k * h * 0.16
        bot = top + h * 0.38
        hw = w * (0.35 + k * 0.16) / 2
        d.polygon([(x, top), (x - hw, bot), (x + hw, bot)], fill=color)
    d.rectangle((x - h * 0.02, base - h * 0.1, x + h * 0.02, base), fill=color)


def forest_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    sky = (np.array([18, 38, 40]) * (1 - y) + np.array([6, 12, 12]) * y)
    img = Image.fromarray(np.repeat(sky, W, axis=1).astype(np.uint8)).convert("RGBA")
    # лунное свечение
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W * 0.55, 120, W * 0.55 + 260, 380), fill=(200, 230, 220, 120))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    layers = 6
    for i in range(layers):
        f = i / (layers - 1)                     # 0 — дальний, 1 — ближний
        col = tuple(int(c) for c in np.array([60, 88, 84]) * (1 - f) + np.array([4, 9, 8]) * f) + (255,)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        base = H * (0.52 + 0.1 * f)
        d.rectangle((0, base, W, H), fill=col)
        x = -60
        while x < W + 60:
            h = rng.uniform(260, 520) * (0.7 + f * 1.4)
            pine(d, x, base + rng.uniform(0, 40), h, col)
            x += rng.uniform(40, 110) * (0.6 + f)
        img.alpha_composite(lay)
        fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(fog).rectangle((0, base - 80, W, base + 120), fill=(150, 175, 170, int(55 * (1 - f) + 15)))
        img.alpha_composite(fog.filter(ImageFilter.GaussianBlur(60)))
    return img


def fog_strip():
    """Широкая полоса тумана, которая медленно плывёт (бесшовно)."""
    fw = W * 2
    a = np.zeros((H, fw), np.float32)
    for _ in range(40):
        cx, cy = rng.uniform(0, fw), rng.uniform(H * 0.35, H * 0.95)
        rx, ry = rng.uniform(200, 500), rng.uniform(40, 110)
        yy, xx = np.ogrid[:H, :fw]
        for dx in (-fw, 0, fw):                  # бесшовность по краям
            a += np.exp(-(((xx - cx - dx) / rx) ** 2 + ((yy - cy) / ry) ** 2)) * 0.35
    a = np.clip(a, 0, 1) * 70
    rgba = np.dstack([np.full_like(a, 190), np.full_like(a, 210), np.full_like(a, 205), a]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def load_bg(kind):
    if kind == "forest":
        return forest_bg(), fog_strip()
    if kind == "black":
        return Image.new("RGBA", (W, H), (0, 0, 0, 255)), None
    im = Image.open(kind).convert("RGBA")
    s = max(W / im.width, H / im.height) * ZOOM
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if s > 3:   # маленькое фото — делаем мягкое «боке», как размытый фон камеры
        im = im.filter(ImageFilter.GaussianBlur(10))
    im = Image.eval(im.convert("RGB"), lambda p: int(p * 0.72)).convert("RGBA")
    return im, "photo"


# ---------- логотип -> стеклянный с белым ободком ----------
def logo_mask(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or "transparency" in im.info:
        m = im.convert("RGBA").getchannel("A")
    else:                                         # тёмный логотип на светлом фоне
        m = Image.eval(im.convert("L"), lambda p: 255 - p)
    m = m.point(lambda p: 255 if p > 110 else 0)
    m = m.crop(m.getbbox())
    s = (LOGO - 2 * RIM - 20) / max(m.size)
    m = m.resize((max(1, int(m.width * s)), max(1, int(m.height * s))), Image.LANCZOS)
    pad = Image.new("L", (m.width + 60, m.height + 60), 0)
    pad.paste(m, (30, 30))
    return pad


def glass_logo(mask):
    inner = mask.filter(ImageFilter.MinFilter(RIM * 2 + 1))
    rim = ImageChops.subtract(mask, inner)
    glow = rim.filter(ImageFilter.GaussianBlur(14)).point(lambda p: int(p * 0.8))
    fill = inner.point(lambda p: int(p * 0.13))  # почти прозрачная «стеклянная» заливка
    alpha = ImageChops.lighter(ImageChops.lighter(rim, glow), fill)
    out = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out, inner


def build(logo_paths, bg_kind, per):
    bg, fog = load_bg(bg_kind)
    logos = [glass_logo(logo_mask(p)) for p in logo_paths]
    n, fade = len(logos), 0.5
    total = n * per
    cy = int(H * 0.42)

    def draw_logo(canvas, idx, t_local, a):
        img, inner = logos[idx]
        ang = 2 * np.pi * t_local / per            # ровно 1 оборот за слайд
        c = np.cos(ang)
        w = max(2, int(img.width * abs(c)))
        im = img.resize((w, img.height), Image.BILINEAR)
        if c < 0:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)   # обратная сторона
        # блик, пробегающий по стеклу
        sheen = Image.new("L", im.size, 0)
        sx = int((np.sin(ang) * 0.5 + 0.5) * w)
        ImageDraw.Draw(sheen).rectangle((sx - 30, 0, sx + 30, im.height), fill=90)
        sheen = sheen.filter(ImageFilter.GaussianBlur(25))
        inn = inner.resize((w, img.height), Image.BILINEAR)
        if c < 0:
            inn = inn.transpose(Image.FLIP_LEFT_RIGHT)
        al = ImageChops.lighter(im.getchannel("A"), ImageChops.multiply(sheen, inn))
        al = al.point(lambda p: int(p * a))
        im.putalpha(al)
        bob = int(14 * np.sin(2 * np.pi * t_local / per))   # лёгкое «парение»
        canvas.alpha_composite(im, ((W - w) // 2, cy - img.height // 2 + bob))
        # тень-эллипс на земле
        sh = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
        ew = int(img.width * (0.35 + 0.25 * abs(c)))
        ImageDraw.Draw(sh).ellipse(((W - ew) // 2, 70, (W + ew) // 2, 130), fill=(0, 0, 0, int(120 * a)))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (0, cy + img.height // 2 + 40))

    def frame(t):
        if fog == "photo":                          # медленный наплыв камеры (зациклен)
            z = 1 + (ZOOM - 1) * (0.5 - 0.5 * np.cos(2 * np.pi * t / total))
            cw, ch = int(bg.width / z), int(bg.height / z)
            l, tp = (bg.width - cw) // 2, (bg.height - ch) // 2
            canvas = bg.crop((l, tp, l + cw, tp + ch)).resize((W, H), Image.BILINEAR)
        else:
            canvas = bg.copy()
        if fog is not None and fog != "photo":                         # туман плывёт ровно на 1 ширину за цикл
            off = int((t / total) * W * 2) % (W * 2)
            strip = fog.crop((off, 0, off + W, H)) if off + W <= W * 2 else \
                Image.fromarray(np.hstack([np.array(fog)[:, off:], np.array(fog)[:, :off + W - W * 2]]), "RGBA")
            canvas.alpha_composite(strip)
        i = int(t // per) % n
        tl = t - i * per
        a_in = min(1.0, tl / fade)
        a_out = min(1.0, (per - tl) / fade)
        draw_logo(canvas, i, tl, min(a_in, a_out))
        return np.array(canvas.convert("RGB"))

    return VideoClip(frame, duration=total)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--logos", default="logos")
    ap.add_argument("--bg", default="forest")
    ap.add_argument("--out", default="logo_spin.mp4")
    ap.add_argument("--per", type=float, default=3.0, help="секунд на логотип")
    a = ap.parse_args()
    paths = sorted(p for p in glob.glob(os.path.join(a.logos, "*"))
                   if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    build(paths, a.bg, a.per).write_videofile(
        a.out, fps=FPS, codec="libx264", audio=False, logger=None,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart", "-crf", "18"])
    print("готово:", a.out)
