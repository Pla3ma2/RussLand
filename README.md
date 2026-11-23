# RussLand

Приложение для изучения русского языка франкоязычными. Веб-приложение (PWA) для iOS и Android, позже — APK через Capacitor.

> Сейчас здесь **технический прототип**: одна сцена «В кафе», чтобы проверить самое рискованное.

## Что проверяет прототип

1. **Écoute** — диалог с видимым ударением, озвучка Silero TTS, нажатие на слово озвучивает его.
2. **Construis** — пазл «Я хочу ___»: окончание меняется на глазах (вода → воду) и подсвечивается цветом падежа.
3. **Comprends** — короткое объяснение от персонажа на французском.
4. **Parle** — запись голоса и сравнение с носителем + офлайн-распознавание речи (Vosk), если включить.

## Как устроено

```
content/*.source.json      ← уроки, которые пишем руками
tools/build_content.py     ← ударения (silero-stress), формы слов (pymorphy3), озвучка (Silero TTS)
public/content/*.json      ← готовые уроки для приложения
src/                       ← само приложение (Vite + TypeScript, без фреймворков)
.github/workflows/         ← сборка: контент → озвучка → модель Vosk → сайт на GitHub Pages
```

Озвучка и модель Vosk создаются автоматически в GitHub Actions — на компьютере ничего ставить не нужно.

## Локальный запуск (по желанию)

```bash
npm install
pip install -r tools/requirements.txt
python tools/build_content.py   # без озвучки: приложение говорит голосом браузера
npm run dev
```

## Лицензии использованных проектов

- Озвучка: [Silero Models](https://github.com/snakers4/silero-models) — CC BY-NC 4.0 (некоммерческое использование)
- Ударения: [silero-stress](https://github.com/snakers4/silero-stress) — MIT
- Морфология: [pymorphy3](https://github.com/no-plagiarism/pymorphy3) — MIT
- Распознавание речи: [Vosk](https://alphacephei.com/vosk/) и [vosk-browser](https://github.com/ccoreilly/vosk-browser) — Apache 2.0
