"""Конвейер контента RussLand.

Берёт content/*.source.json (то, что пишем руками) и делает public/content/*.json:
  - ударения (silero-stress), разбивка на слова;
  - формы слов для пазла (pymorphy3) с разметкой «основа + окончание»;
  - список аудиофраз; с флагом --audio озвучивает их Silero TTS в public/audio/*.mp3.

Запуск:
  python tools/build_content.py           # без озвучки (приложение озвучит голосом браузера)
  python tools/build_content.py --audio   # с озвучкой (нужны torch, ffmpeg и интернет для первой загрузки модели)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import pymorphy3
from silero_stress import load_accentor

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "content"
OUT_DIR = ROOT / "public" / "content"
AUDIO_DIR = ROOT / "public" / "audio"

WORD_RE = re.compile(r"[+А-Яа-яЁё\-]+")

accentor = load_accentor()
morph = pymorphy3.MorphAnalyzer()

# Все фразы, которые нужно озвучить: id -> (текст с «+», голос)
clips: dict[str, tuple[str, str]] = {}


def accent(text: str) -> str:
    return accentor(text)


def clip(accented: str, voice: str) -> str:
    """Регистрирует фразу для озвучки и возвращает имя файла."""
    cid = hashlib.sha1(f"{voice}|{accented}".encode()).hexdigest()[:12]
    clips[cid] = (accented, voice)
    return f"{cid}.mp3"


def split_word(accented_word: str) -> tuple[str, int | None]:
    """'в+оду' -> ('воду', 1): слово без «+» и индекс ударной гласной."""
    idx = accented_word.find("+")
    plain = accented_word.replace("+", "")
    return plain, (idx if idx >= 0 else None)


def tokenize(text: str, word_voice: str) -> list[dict]:
    accented = accent(text)
    tokens: list[dict] = []
    pos = 0
    for m in WORD_RE.finditer(accented):
        if m.start() > pos:
            tokens.append({"t": accented[pos:m.start()], "w": False})
        plain, stress = split_word(m.group())
        tokens.append({
            "t": plain,
            "s": stress,
            "w": True,
            "a": clip(accent(plain.lower()), word_voice),
        })
        pos = m.end()
    if pos < len(accented):
        tokens.append({"t": accented[pos:], "w": False})
    return tokens


def line(text: str, fr: str, speaker: str, voices: dict, word_voice: str) -> dict:
    return {
        "speaker": speaker,
        "ru": text,
        "fr": fr,
        "tokens": tokenize(text, word_voice),
        "audio": clip(accent(text), voices[speaker]),
    }


def puzzle_word(w: dict, case: str, frame: str, voice: str, word_voice: str) -> dict:
    lemma = w["lemma"]
    parsed = morph.parse(lemma)[0]
    form = parsed.inflect({case}).word
    cp = 0
    while cp < min(len(lemma), len(form)) and lemma[cp] == form[cp]:
        cp += 1
    phrase = frame.replace("___", form)
    phrase_acc = accent(phrase)
    # ударение формы берём из целой фразы (контекст важен)
    form_acc = next(
        (t for t in WORD_RE.findall(phrase_acc) if t.replace("+", "") == form),
        accent(form),
    )
    _, stress_form = split_word(form_acc)
    _, stress_lemma = split_word(accent(lemma))
    return {
        "lemma": lemma,
        "fr": w["fr"],
        "phraseFr": w["phraseFr"],
        "form": form,
        "stem": lemma[:cp],
        "endLemma": lemma[cp:],
        "endForm": form[cp:],
        "changed": lemma != form,
        "gender": str(parsed.tag.gender),
        "stressLemma": stress_lemma,
        "stressForm": stress_form,
        "audioLemma": clip(accent(lemma), word_voice),
        "audioPhrase": clip(phrase_acc, voice),
    }


def build_lesson(src: dict) -> dict:
    voices = {k: v["voice"] for k, v in src["speakers"].items()}
    wv = src["wordVoice"]
    pz = src["puzzle"]
    before, after = pz["frame"].split("___")
    sp = src["speak"]
    return {
        "id": src["id"],
        "titleFr": src["titleFr"],
        "sceneFr": src["sceneFr"],
        "speakers": {k: {"name": v["name"], "color": v["color"]} for k, v in src["speakers"].items()},
        "dialogue": [line(d["ru"], d["fr"], d["speaker"], voices, wv) for d in src["dialogue"]],
        "puzzle": {
            "before": tokenize(before, wv) if before.strip() else [],
            "after": after,
            "frameFr": pz["frameFr"],
            "caseColor": pz["caseColor"],
            "words": [puzzle_word(w, pz["case"], pz["frame"], voices[pz["speaker"]], wv) for w in pz["words"]],
            "task": pz["task"],
            "insightFr": pz["insightFr"],
        },
        "speak": {
            "line": line(sp["ru"], sp["fr"], sp["speaker"], voices, wv),
            "grammar": sp["grammar"],
        },
    }


def synthesize(force: bool) -> int:
    import torch  # noqa: WPS433 — тяжёлые зависимости грузим только для озвучки

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    todo = {cid: v for cid, v in clips.items() if force or not (AUDIO_DIR / f"{cid}.mp3").exists()}
    if not todo:
        return 0
    model, _ = torch.hub.load(
        repo_or_dir="snakers4/silero-models", model="silero_tts",
        language="ru", speaker="v4_ru", trust_repo=True,
    )
    sr = 48000
    with tempfile.TemporaryDirectory() as tmp:
        for cid, (text, voice) in todo.items():
            audio = model.apply_tts(text=text, speaker=voice, sample_rate=sr, put_accent=False, put_yo=False)
            pcm = (audio.clamp(-1, 1) * 32767).short().numpy().tobytes()
            wav_path = Path(tmp) / f"{cid}.wav"
            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
                 "-ac", "1", "-ar", "24000", "-b:a", "48k", str(AUDIO_DIR / f"{cid}.mp3")],
                check=True,
            )
            print(f"  🔊 {cid}  [{voice}]  {text}")
    return len(todo)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", action="store_true", help="озвучить фразы Silero TTS")
    ap.add_argument("--force", action="store_true", help="переозвучить всё заново")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = []
    for src_path in sorted(SRC_DIR.glob("*.source.json")):
        lesson = build_lesson(json.loads(src_path.read_text(encoding="utf-8")))
        lesson["hasAudio"] = bool(args.audio)
        out = OUT_DIR / f"{lesson['id']}.json"
        out.write_text(json.dumps(lesson, ensure_ascii=False, indent=1), encoding="utf-8")
        index.append({"id": lesson["id"], "titleFr": lesson["titleFr"]})
        print(f"✓ {out.relative_to(ROOT)}")
    (OUT_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Аудиофраз в уроках: {len(clips)}")
    if args.audio:
        n = synthesize(args.force)
        print(f"Озвучено новых: {n}")


if __name__ == "__main__":
    sys.exit(main())
