# Reels Generator

Генерирует вертикальные видео 1080×1920 (9:16) для Instagram Reels / TikTok / Shorts
из простого JSON-сценария. Основан на открытой библиотеке [MoviePy](https://github.com/Zulko/moviepy).

## Установка
```bash
pip install -r requirements.txt   # также нужен ffmpeg
```

## Запуск
```bash
python make_reel.py example.json my_reel.mp4
```

## Формат сценария (`example.json`)
| Поле | Описание |
|---|---|
| `color1`, `color2` | цвета анимированного градиента фона |
| `handle` | ник внизу кадра (необязательно) |
| `music` | путь к mp3/wav для фоновой музыки (необязательно) |
| `slides[].text` | текст слайда (`\n` — перенос строки) |
| `slides[].duration` | длительность в секундах |
| `slides[].size`, `slides[].color` | размер и цвет шрифта (необязательно) |

Эффекты: «pop»-появление текста, плавное исчезание, тень, прогресс-бар как в сторис.
Видео кодируется в H.264 + AAC, yuv420p, faststart — формат, который принимает Instagram.
