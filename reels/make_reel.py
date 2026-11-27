"""Генератор вертикальных видео для Instagram Reels (1080x1920).

Использует MoviePy (https://github.com/Zulko/moviepy) + Pillow + NumPy.
Запуск:  python make_reel.py script.json out.mp4
"""
import json
import sys

import numpy as np
from moviepy import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def wrap(text, font, max_w, draw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = f"{cur} {word}".strip()
            if draw.textlength(test, font=font) <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def render_text(text, size, color):
    """Рисует текст с тенью в RGBA-картинку (один раз на слайд)."""
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = wrap(text, font, W - 160, tmp)
    lh = int(size * 1.25)
    img = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = (W - d.textlength(line, font=font)) / 2
        y = 20 + i * lh
        d.text((x + 6, y + 6), line, font=font, fill=(0, 0, 0, 110))
        d.text((x, y), line, font=font, fill=color)
    return img


def build(cfg):
    slides = cfg["slides"]
    c1, c2 = hex_rgb(cfg.get("color1", "#ff3d7f")), hex_rgb(cfg.get("color2", "#3d5afe"))
    accent = cfg.get("accent", "#ffffff")
    for s in slides:
        s["img"] = render_text(s["text"], s.get("size", 92), s.get("color", accent))
    starts = np.cumsum([0] + [s["duration"] for s in slides])
    total = float(starts[-1])

    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]

    def frame(t):
        # Анимированный диагональный градиент
        k = 0.5 + 0.5 * np.sin(2 * np.pi * (xx * 0.6 + yy * 0.8) - t * 1.5)
        bg = (c1 * k[..., None] + c2 * (1 - k[..., None])).astype(np.uint8)
        canvas = Image.fromarray(bg).convert("RGBA")

        i = int(np.searchsorted(starts, t, side="right") - 1)
        i = min(i, len(slides) - 1)
        local, dur = t - starts[i], slides[i]["duration"]
        appear = min(local / 0.35, 1.0)
        vanish = min((dur - local) / 0.25, 1.0)
        a = max(0.0, min(appear, vanish))
        ease = 1 - (1 - appear) ** 3            # ease-out «pop»
        scale = 0.8 + 0.2 * ease
        img = slides[i]["img"]
        sw, sh = int(img.width * scale), int(img.height * scale)
        im = img.resize((sw, sh), Image.BILINEAR)
        alpha = im.getchannel("A").point(lambda p: int(p * a))
        im.putalpha(alpha)
        y = (H - sh) // 2 + int((1 - ease) * 120)
        canvas.alpha_composite(im, ((W - sw) // 2, y))

        # Прогресс-бар сверху (как сторис)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        d.rounded_rectangle((60, 80, W - 60, 92), 6, fill=(255, 255, 255, 70))
        d.rounded_rectangle((60, 80, 60 + int((W - 120) * t / total), 92), 6, fill=(255, 255, 255, 230))
        if cfg.get("handle"):
            f = ImageFont.truetype(FONT, 44)
            d.text(((W - d.textlength(cfg["handle"], font=f)) / 2, H - 200), cfg["handle"],
                   font=f, fill=(255, 255, 255, 200))
        canvas.alpha_composite(overlay)
        return np.array(canvas.convert("RGB"))

    clip = VideoClip(frame, duration=total)
    if cfg.get("music"):
        audio = AudioFileClip(cfg["music"]).subclipped(0, total)
        clip = clip.with_audio(audio)
    return clip


if __name__ == "__main__":
    cfg_path, out = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "reel.mp4")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    build(cfg).write_videofile(out, fps=FPS, codec="libx264", audio_codec="aac",
                               ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
