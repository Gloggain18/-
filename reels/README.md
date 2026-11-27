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

---

# Крутящиеся «стеклянные» логотипы (`logo_spin.py`)

Каждый логотип превращается в прозрачное стекло с белым светящимся ободком,
делает полный оборот на месте над туманным ночным лесом, затем плавно сменяется следующим.
Видео зацикливается (Reels сам крутит его по кругу).

```bash
python make_demo_logos.py                     # демо-эмблемы (заглушки) в logos/
python logo_spin.py --logos logos --bg forest --out spin.mp4 --per 3
python logo_spin.py --logos logos --bg black  --out spin_black.mp4
python logo_spin.py --logos logos --bg forest.jpg --out spin_photo.mp4   # своё фото фона
```

Чтобы использовать свои логотипы — положите PNG (с прозрачностью или тёмный логотип на белом фоне)
в папку `logos/`, порядок задаётся именем файла: `01_...png`, `02_...png`.
Используя логотипы чужих брендов, учитывайте их правила о товарных знаках.
