"""Конвейер контента RussLand.

Источники (пишем руками):
  content/characters.json     — персонажи и их голоса
  content/levels/*.json       — уровни основного режима
  content/reading.json        — ступени режима «Чтение»
  content/alphabet.json       — алфавит: группы, звуки, подсказки
  content/carte.json          — какие падежи и глаголы есть на «Карте»

Результат (для приложения): public/content/*.json, озвучка public/audio/*.mp3

  python tools/build_content.py           # без озвучки (приложение говорит голосом браузера)
  python tools/build_content.py --audio   # с озвучкой Silero TTS (torch + ffmpeg + интернет)
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
SRC = ROOT / "content"
OUT = ROOT / "public" / "content"
AUDIO_DIR = ROOT / "public" / "audio"

WORD_RE = re.compile(r"[+А-Яа-яЁё\-]+")
VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")

accentor = load_accentor()
morph = pymorphy3.MorphAnalyzer()
clips: dict[str, tuple[str, str]] = {}  # id -> (текст с «+», голос)
errors: list[str] = []

CHARS = json.loads((SRC / "characters.json").read_text(encoding="utf-8"))
WORD_VOICE = CHARS["_wordVoice"]
PERSONS = {
    "я": {"1per", "sing"}, "ты": {"2per", "sing"}, "он": {"3per", "sing"}, "она": {"3per", "sing"},
    "мы": {"1per", "plur"}, "вы": {"2per", "plur"}, "они": {"3per", "plur"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, data) -> None:
    out = OUT / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {out.relative_to(ROOT)}")


# ---------- ударения ----------

def accent(text: str) -> str:
    """Ставит «+» перед ударной гласной. Ручные «+» в исходнике имеют приоритет."""
    manual = {w.replace("+", "").lower(): w for w in WORD_RE.findall(text) if "+" in w}
    auto = accentor(text.replace("+", ""))
    if not manual:
        return auto

    def fix(m: re.Match) -> str:
        w = m.group()
        key = w.replace("+", "").lower()
        if key not in manual:
            return w
        # берём ручное ударение, но регистр букв — как в тексте
        letters = iter(w.replace("+", ""))
        return "".join(ch if ch == "+" else next(letters) for ch in manual[key])

    return WORD_RE.sub(fix, auto)


def split_word(acc: str) -> tuple[str, int | None]:
    i = acc.find("+")
    return acc.replace("+", ""), (i if i >= 0 else None)


def clip(acc_text: str, voice: str) -> str:
    cid = hashlib.sha1(f"{voice}|{acc_text}".encode()).hexdigest()[:12]
    clips[cid] = (acc_text, voice)
    return f"{cid}.mp3"


def tokenize(text: str) -> list[dict]:
    acc = accent(text)
    tokens: list[dict] = []
    pos = 0
    for m in WORD_RE.finditer(acc):
        if m.start() > pos:
            tokens.append({"t": acc[pos:m.start()], "w": False})
        plain, stress = split_word(m.group())
        tokens.append({"t": plain, "s": stress, "w": True, "a": clip(m.group().lower(), WORD_VOICE)})
        pos = m.end()
    if pos < len(acc):
        tokens.append({"t": acc[pos:], "w": False})
    return tokens


def line(ru: str, fr: str, speaker: str) -> dict:
    return {
        "speaker": speaker, "ru": ru.replace("+", ""), "fr": fr,
        "tokens": tokenize(ru), "audio": clip(accent(ru), CHARS[speaker]["voice"]),
    }


# ---------- морфология ----------

def morph_unit(src: str, dst: str, context: str) -> dict:
    """Описание превращения слова: общая основа и меняющиеся окончания + ударения."""
    src_plain, dst_plain = src.replace("+", ""), dst.replace("+", "")
    cp = 0
    while cp < min(len(src_plain), len(dst_plain)) and src_plain[cp].lower() == dst_plain[cp].lower():
        cp += 1
    ctx_acc = accent(context)
    dst_acc = next((t for t in WORD_RE.findall(ctx_acc) if t.replace("+", "").lower() == dst_plain.lower()),
                   accent(dst))
    src_acc = src if "+" in src else accent(src_plain)
    return {
        "from": src_plain, "to": dst_plain,
        "stem": dst_plain[:cp], "endFrom": src_plain[cp:], "endTo": dst_plain[cp:],
        "stressFrom": split_word(src_acc)[1], "stressTo": split_word(dst_acc)[1],
        "changed": src_plain.lower() != dst_plain.lower(),
    }


def inflect_noun(lemma: str, case: str) -> str:
    plain = lemma.replace("+", "")
    if case == "nomn":
        return plain
    parsed = next((p for p in morph.parse(plain) if p.tag.POS == "NOUN"), morph.parse(plain)[0])
    form = parsed.inflect({case})
    if form is None:
        errors.append(f"не удалось просклонять «{plain}» в {case}")
        return plain
    word = form.word
    return word.capitalize() if plain[0].isupper() else word


def conjugate(verb: str, pron: str) -> str:
    parsed = next(p for p in morph.parse(verb) if p.tag.POS == "INFN")
    tags = set(PERSONS[pron]) | ({"pres"} if parsed.tag.aspect == "impf" else {"futr"})
    form = parsed.inflect(tags)
    if form is None:
        errors.append(f"не удалось проспрягать «{verb}» для «{pron}»")
        return verb
    return form.word


# ---------- уровни ----------

def build_explore(ex: dict) -> dict:
    t = ex["type"]
    voice = CHARS[ex["speaker"]]["voice"]
    before, _, after = ex["frame"].partition("___")
    words = []
    for w in ex["words"]:
        # phrase_src может содержать ручные «+» (имена, исключения) — accent() их уважает
        if t == "person":
            pron = w["tile"]
            form = conjugate(ex["verb"], pron)
            phrase_src = (before + pron + after).replace("{V}", form)
            phrase_src = phrase_src[0].upper() + phrase_src[1:]
            mu = morph_unit(ex["verb"], form, phrase_src)
        elif t == "case":
            form = inflect_noun(w["tile"], ex["case"])
            phrase_src = before + w.get("formAcc", form) + after
            mu = morph_unit(w["tile"], w.get("formAcc", form), phrase_src)
        else:  # plain
            phrase_src = before + w["tile"] + after
            mu = morph_unit(w["tile"], w["tile"], phrase_src)
        phrase = phrase_src.replace("+", "")
        tile_acc = w["tile"] if "+" in w["tile"] else accent(w["tile"])
        tile_plain, tile_stress = split_word(tile_acc)
        words.append({
            "tile": tile_plain, "tileStress": tile_stress, "fr": w["fr"], "phraseFr": w["phraseFr"],
            "phrase": phrase, "morph": mu,
            "audioTile": clip(tile_acc.lower(), WORD_VOICE),
            "audioPhrase": clip(accent(phrase_src), voice),
        })
    after_txt = after.replace("{V}", "")
    return {
        "type": t, "frameFr": ex["frameFr"], "color": ex.get("color", "#3d5a80"),
        "before": tokenize(before) if before.strip() else [],
        "after": tokenize(after_txt) if after_txt.strip(" ") else [],
        "verb": ex.get("verb"), "words": words,
    }


def build_level(src: dict) -> dict:
    lid = src["id"]
    speakers = {s: {"name": CHARS[s]["name"], "nameFr": CHARS[s]["nameFr"], "color": CHARS[s]["color"]}
                for s in {d["speaker"] for d in src["dialogue"]} | {src["learner"], src["insight"]["by"]}}
    dialogue = [line(d["ru"], d["fr"], d["speaker"]) for d in src["dialogue"]]
    explore = build_explore(src["explore"])
    learner_voice = src["learner"]
    tasks = []
    for t in src["tasks"]:
        if t["type"] == "pick":
            if not any(w["tile"] == t["answer"] for w in explore["words"]):
                errors.append(f"{lid}: ответа «{t['answer']}» нет среди плиток")
            tasks.append(t)
        elif t["type"] == "order":
            tasks.append({"type": "order", "line": line(t["ru"], t["fr"], learner_voice)})
    speak = [line(s["ru"], s["fr"], learner_voice) for s in src["speak"]]
    grammar_src = [s["ru"] for s in src["speak"]] + [d["ru"] for d in src["dialogue"] if d["speaker"] == src["learner"]]
    grammar = sorted({re.sub(r"[^а-яё ]", "", g.replace("+", "").lower()).strip() for g in grammar_src}) + ["[unk]"]

    # всё, что ученик говорит, попадает в повторение
    items = {}
    for ln in speak + [d for d in dialogue if d["speaker"] == src["learner"]]:
        items.setdefault(ln["ru"], {"id": f"{lid}:{hashlib.sha1(ln['ru'].encode()).hexdigest()[:8]}",
                                    "ru": ln["ru"], "fr": ln["fr"], "tokens": ln["tokens"], "audio": ln["audio"]})

    glossary = {k.lower().replace("ё", "е"): v for k, v in src.get("glossary", {}).items()}
    missing = sorted({t["t"].lower() for ln in dialogue + speak for t in ln["tokens"]
                      if t["w"] and t["t"].lower().replace("ё", "е") not in glossary})
    if missing:
        print(f"  ⚠ {lid}: нет перевода в glossary для: {', '.join(missing)}")

    return {
        "id": lid, "order": src["order"], "titleFr": src["titleFr"], "titleRu": src["titleRu"],
        "emoji": src["emoji"], "sceneFr": src["sceneFr"], "learner": src["learner"],
        "speakers": speakers, "dialogue": dialogue, "explore": explore, "tasks": tasks,
        "insight": src["insight"], "speak": speak, "grammar": grammar,
        "cando": src["cando"], "glossary": glossary, "unlocks": src.get("unlocks", []),
        "items": list(items.values()),
    }


# ---------- чтение и алфавит ----------

def build_alphabet() -> dict:
    src = load(SRC / "alphabet.json")
    letters = []
    for L in src["letters"]:
        ex_tokens = tokenize(L["exampleRu"])
        letters.append({
            **{k: v for k, v in L.items() if k != "soundText"},
            "audio": clip(L["soundText"], WORD_VOICE),
            "exampleTokens": ex_tokens,
            "exampleAudio": clip(accent(L["exampleRu"]).lower(), WORD_VOICE),
        })
    return {"groups": src["groups"], "letters": letters}


def build_reading(alphabet: dict) -> dict:
    src = load(SRC / "reading.json")
    known: set[str] = set()
    letter_map = {L["l"].lower(): L for L in alphabet["letters"]}
    stages = []
    for st in src["stages"]:
        new = [x.lower() for x in st["letters"]]
        for x in new:
            if x not in letter_map:
                errors.append(f"чтение {st['id']}: буквы «{x}» нет в алфавите")
        known |= set(new)

        def check(s: str, where: str) -> None:
            bad = {ch for ch in s.lower() if ch.isalpha() and ch not in known}
            if bad:
                errors.append(f"чтение {st['id']}: в «{s}» ({where}) ещё не изученные буквы: {''.join(sorted(bad))}")

        syllables = []
        for s in st["syllables"]:
            check(s, "слог")
            syllables.append({"t": s, "audio": clip(s, WORD_VOICE)})
        words = []
        for w in st["words"]:
            check(w["ru"], "слово")
            acc = accent(w["ru"])
            plain, stress = split_word(acc)
            words.append({"t": plain, "s": stress, "fr": w["fr"], "audio": clip(acc.lower(), WORD_VOICE)})
        stages.append({
            "id": st["id"], "titleFr": st["titleFr"], "letters": [x.upper() for x in new],
            "tipFr": st.get("tipFr", []), "syllables": syllables, "words": words,
            "pairs": [[{"t": p, "audio": clip(p, WORD_VOICE)} for p in pair] for pair in st.get("pairs", [])],
        })
        for pair in st.get("pairs", []):
            for p in pair:
                check(p, "пара")
    missing = set(letter_map) - known
    if missing:
        errors.append(f"чтение: не изучаются буквы {''.join(sorted(missing))}")
    return {"stages": stages}


def build_carte() -> dict:
    src = load(SRC / "carte.json")
    verbs = []
    for v in src["verbs"]:
        forms = {}
        for pron in ["я", "ты", "он", "мы", "вы", "они"]:
            f = conjugate(v["verb"], pron)
            forms[pron] = {**morph_unit(v["verb"], f, f), "audio": clip(accent(f).lower(), WORD_VOICE)}
        verbs.append({"verb": v["verb"], "fr": v["fr"], "forms": forms})
    return {**src, "verbs": verbs}


# ---------- озвучка ----------

def synthesize(force: bool) -> int:
    import torch  # noqa: WPS433

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    todo = {c: v for c, v in clips.items() if force or not (AUDIO_DIR / f"{c}.mp3").exists()}
    if not todo:
        return 0
    model, _ = torch.hub.load(repo_or_dir="snakers4/silero-models", model="silero_tts",
                              language="ru", speaker="v4_ru", trust_repo=True)
    sr = 48000
    done = 0
    with tempfile.TemporaryDirectory() as tmp:
        for cid, (text, voice) in todo.items():
            try:
                audio = model.apply_tts(text=text, speaker=voice, sample_rate=sr, put_accent=False, put_yo=False)
            except Exception as e:  # noqa: BLE001 — одна неудачная фраза не должна ронять сборку
                print(f"  ⚠ не озвучено «{text}»: {e}")
                continue
            pcm = (audio.clamp(-1, 1) * 32767).short().numpy().tobytes()
            wav_path = Path(tmp) / f"{cid}.wav"
            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
                            "-af", "silenceremove=start_periods=1:start_threshold=-50dB",
                            "-ac", "1", "-ar", "24000", "-b:a", "48k", str(AUDIO_DIR / f"{cid}.mp3")], check=True)
            done += 1
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    levels = [build_level(load(p)) for p in sorted((SRC / "levels").glob("*.json"))]
    levels.sort(key=lambda lv: lv["order"])
    alphabet = build_alphabet()
    reading = build_reading(alphabet)
    carte = build_carte()

    if errors:
        print("\n✗ Ошибки в контенте:")
        for e in errors:
            print("  -", e)
        return 1

    for lv in levels:
        lv["hasAudio"] = args.audio
        write(f"levels/{lv['id']}.json", lv)
    write("index.json", {
        "hasAudio": args.audio,
        "levels": [{"id": lv["id"], "order": lv["order"], "titleFr": lv["titleFr"], "titleRu": lv["titleRu"],
                    "emoji": lv["emoji"], "cando": lv["cando"]} for lv in levels],
    })
    write("alphabet.json", alphabet)
    write("reading.json", reading)
    write("carte.json", carte)
    print(f"Аудиофраз: {len(clips)}")
    if args.audio:
        print(f"Озвучено новых: {synthesize(args.force)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
