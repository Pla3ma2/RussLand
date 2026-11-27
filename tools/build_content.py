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

# Слова, где автоматическое ударение ошибается (однозначные случаи)
STRESS_FIX = {w.replace("+", ""): w for w in [
    "уч+ишься", "уч+ится", "уч+имся", "уч+атся", "по-англ+ийски", "по-франц+узски", "по-р+усски",
]}


def accent(text: str) -> str:
    """Ставит «+» перед ударной гласной. Ручные «+» в исходнике имеют приоритет."""
    manual = {w.replace("+", "").lower(): w for w in WORD_RE.findall(text) if "+" in w}
    for w in WORD_RE.findall(text.replace("+", "")):
        if w.lower() in STRESS_FIX and w.lower() not in manual:
            manual[w.lower()] = STRESS_FIX[w.lower()]
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


def clip(acc_text: str, voice: str, folder: str = "") -> str:
    """Регистрирует фразу для озвучки; folder — подпапка (слова карточек лежат в w/, их не кладём в офлайн-кэш)."""
    cid = folder + hashlib.sha1(f"{voice}|{acc_text}".encode()).hexdigest()[:12]
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
        tokens.append({"t": plain, "s": stress, "w": True, "a": clip(m.group().lower(), WORD_VOICE),
                       "l": lemma_of(plain)})
        pos = m.end()
    if pos < len(acc):
        tokens.append({"t": acc[pos:], "w": False})
    return tokens


def lemma_of(word: str) -> str:
    w = word.lower()
    if "-" in w and w.startswith("по-"):
        return w
    return morph.parse(w)[0].normal_form


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
            form = w.get("formAcc") or conjugate(ex["verb"], pron)
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
        "type": t, "frameFr": ex["frameFr"], "color": ex.get("color", "#3d5a80"), "hintFr": ex.get("hintFr", ""),
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


def norm_words(s: str) -> str:
    return " ".join(re.sub(r"[^а-яё\- ]", " ", s.replace("+", "").lower()).split())


# Пазл: всё, что ученик уже видел в прошлых уроках (формы слов → в каком уроке впервые), и их переводы
KNOWN: dict[str, str] = {}
GLOSS_ALL: dict[str, str] = {}
nk = lambda w: w.lower().replace("ё", "е")


def forms_of(text: str) -> list[str]:
    return [nk(m.group()) for m in WORD_RE.finditer(text.replace("+", ""))]


def build_lesson_v2(src: dict) -> dict:
    """Урок новой схемы: фразы проходят «лестницу» упражнений блоками, урок делится на части."""
    lid = src["id"]
    learner = src["learner"]
    phrases = {}
    for p in src["phrases"]:
        ln = line(p["ru"], p["fr"], p["speaker"])
        words = [t for t in ln["tokens"] if t["w"]]
        out = {**ln, "id": p["id"], "noteFr": p.get("noteFr", "")}
        if "gap" in p:
            g = p["gap"]
            idx = next((i for i, t in enumerate(ln["tokens"]) if t["w"] and t["t"].lower() == g["word"].lower()), None)
            if idx is None:
                errors.append(f"{lid}/{p['id']}: слова «{g['word']}» нет во фразе")
            else:
                out["gap"] = {
                    "index": idx,
                    "whyFr": g.get("whyFr", ""),
                    "distractors": [{"t": d.replace("+", ""), "a": clip(accent(d).lower(), WORD_VOICE), "s": split_word(accent(d))[1]}
                                    for d in g["distractors"]],
                }
                full = norm_words(p["ru"])
                for d in g["distractors"]:
                    if d.lower() == g["word"].lower():
                        errors.append(f"{lid}/{p['id']}: отвлекающий вариант совпадает с ответом")
                    swapped = re.sub(rf"(?i)(?<![а-яё]){re.escape(g['word'])}(?![а-яё])", d.replace("+", ""), p["ru"].replace("+", ""))
                    if norm_words(swapped) == full:
                        errors.append(f"{lid}/{p['id']}: отвлекающий вариант даёт ту же фразу")
        if "orders" in p:
            main = norm_words(p["ru"]).replace("-", " - ")
            alts = [norm_words(o) for o in p["orders"]]
            if norm_words(p["ru"]) not in alts:
                errors.append(f"{lid}/{p['id']}: основной порядок слов не входит в orders")
            if len(words) < 3:
                errors.append(f"{lid}/{p['id']}: «собери фразу» имеет смысл от 3 слов")
            out["orders"] = alts
            del main
        phrases[p["id"]] = out

    for part in src["parts"]:
        for st in part["steps"]:
            for pid in st.get("phrases", []) + st.get("review", []):
                if pid not in phrases and not (st["type"] == "combine"):
                    errors.append(f"{lid}: шаг ссылается на неизвестную фразу «{pid}»")

    explore = build_explore(src["explore"])
    for t in src["tasks"]:
        if not any(w["tile"] == t["answer"] for w in explore["words"]):
            errors.append(f"{lid}: ответа «{t['answer']}» нет среди плиток")

    dialogue = [line(d["ru"], d["fr"], d["speaker"]) for d in src["dialogue"]]
    by = {i["by"] for i in src["insights"]}
    speakers = {s: {"name": CHARS[s]["name"], "nameFr": CHARS[s]["nameFr"], "color": CHARS[s]["color"]}
                for s in {d["speaker"] for d in src["dialogue"]} | {learner} | by | {p["speaker"] for p in src["phrases"]}}
    grammar = sorted({re.sub(r"[^а-яё ]", "", x["ru"].lower()).strip() for x in phrases.values()}
                     | {re.sub(r"[^а-яё ]", "", d["ru"].lower()).strip() for d in dialogue}) + ["[unk]"]

    glossary = {k.lower().replace("ё", "е"): v for k, v in src.get("glossary", {}).items()}
    missing = sorted({t["t"].lower() for ln in dialogue + list(phrases.values()) for t in ln["tokens"]
                      if t["w"] and t["t"].lower().replace("ё", "е") not in glossary})
    if missing:
        print(f"  ⚠ {lid}: нет перевода в glossary для: {', '.join(missing)}")

    # слова этого урока становятся «известными»
    lesson_forms = set()
    for txt in [d["ru"] for d in src["dialogue"]] + [p["ru"] for p in src["phrases"]] + [w["phrase"] for w in explore["words"]] + [w["tile"] for w in explore["words"]]:
        lesson_forms.update(forms_of(txt))
    for f in lesson_forms:
        KNOWN.setdefault(f, src["titleFr"])
    for k, v in glossary.items():
        GLOSS_ALL.setdefault(k, v)

    # Пазл: новые фразы ТОЛЬКО из уже знакомых слов (из этого и прошлых уроков)
    for i, c in enumerate(src.get("combos", [])):
        cid = f"c{i + 1}"
        unknown = [f for f in forms_of(c["ru"]) if f not in KNOWN]
        if unknown:
            errors.append(f"{lid}/пазл «{c['ru']}»: незнакомые слова {unknown}")
        if norm_words(c["ru"]) in {norm_words(x["ru"]) for x in list(src["phrases"]) + list(src["dialogue"])}:
            errors.append(f"{lid}/пазл «{c['ru']}»: такая фраза уже есть в уроке — это не новая комбинация")
        ln = line(c["ru"], c["fr"], c.get("speaker", learner))
        alts = [norm_words(o) for o in c.get("orders", [c["ru"]])]
        if norm_words(c["ru"]) not in alts:
            errors.append(f"{lid}/пазл «{c['ru']}»: основной порядок не входит в orders")
        words_c = {nk(t["t"]) for t in ln["tokens"] if t["w"]}
        for x in c.get("extra", []):
            x = x.replace("+", "")
            if nk(x) in words_c:
                errors.append(f"{lid}/пазл «{c['ru']}»: лишнее слово «{x}» есть во фразе")
            if nk(x) not in KNOWN:
                errors.append(f"{lid}/пазл «{c['ru']}»: лишнее слово «{x}» ещё не изучено")
        src_lessons = []
        for f in forms_of(c["ru"]):
            t = KNOWN.get(f)
            if t and t not in src_lessons:
                src_lessons.append(t)
        phrases[cid] = {**ln, "id": cid, "noteFr": c.get("noteFr", ""), "orders": alts,
                        "combo": {"from": src_lessons,
                                  "extra": [{"t": x.replace("+", ""), "a": clip(accent(x).lower(), WORD_VOICE), "s": split_word(accent(x))[1]}
                                            for x in c.get("extra", [])]}}
        for t in ln["tokens"]:
            if t["w"] and nk(t["t"]) not in glossary and nk(t["t"]) in GLOSS_ALL:
                glossary[nk(t["t"])] = GLOSS_ALL[nk(t["t"])]

    grammar = sorted(set(grammar[:-1]) | {re.sub(r"[^а-яё ]", "", x["ru"].lower()).strip() for x in phrases.values()}) + ["[unk]"]
    items = [{"id": f"{lid}:{p['id']}", "ru": p["ru"], "fr": p["fr"], "tokens": p["tokens"], "audio": p["audio"]}
             for p in phrases.values()]
    return {
        "version": 2, "id": lid, "order": src["order"], "titleFr": src["titleFr"], "titleRu": src["titleRu"],
        "emoji": src["emoji"], "sceneFr": src["sceneFr"], "learner": learner, "speakers": speakers,
        "dialogue": dialogue, "phrases": phrases, "parts": src["parts"], "insights": src["insights"],
        "explore": explore, "tasks": src["tasks"], "grammar": grammar, "cando": src["cando"],
        "glossary": glossary, "unlocks": src.get("unlocks", []), "items": items,
    }


# ---------- маленькие тексты для чтения (только из изученных слов) ----------

KNOWN_AT: dict[str, dict] = {}


def build_texts() -> dict:
    src = load(SRC / "texts.json")
    out = []
    for t in src["texts"]:
        tid, after = t["id"], t["after"]
        known = KNOWN_AT.get(after)
        if known is None:
            errors.append(f"тексты/{tid}: нет урока «{after}»")
            continue
        new = {nk(k): v for k, v in t.get("newWords", {}).items()}
        if len(new) > 3:
            errors.append(f"тексты/{tid}: больше 3 новых слов — текст должен быть из знакомых слов")
        voice = CHARS[t["by"]]["voice"]
        sentences = []
        for snt in t["sentences"]:
            bad = [f for f in forms_of(snt["ru"]) if f not in known and f not in new]
            if bad:
                errors.append(f"тексты/{tid}: незнакомые слова {bad} в «{snt['ru']}»")
            ln = line(snt["ru"], snt["fr"], t["by"])
            sentences.append({"ru": ln["ru"], "fr": ln["fr"], "tokens": ln["tokens"], "audio": ln["audio"]})
        gloss = {}
        for snt in sentences:
            for tok in snt["tokens"]:
                k = nk(tok["t"]) if tok["w"] else None
                if k and k not in gloss:
                    g = new.get(k) or GLOSS_ALL.get(k)
                    if g:
                        gloss[k] = g
        for q in t["questions"]:
            if len(q["options"]) < 2:
                errors.append(f"тексты/{tid}: в вопросе меньше двух вариантов")
        out.append({"id": tid, "after": after, "titleFr": t["titleFr"], "titleRu": t["titleRu"], "by": t["by"],
                    "byFr": CHARS[t["by"]]["nameFr"], "color": CHARS[t["by"]]["color"],
                    "sentences": sentences, "glossary": gloss, "newWords": sorted(new),
                    "questions": t["questions"]})
    return {"texts": out}


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


# ---------- 5000 слов ----------

def build_words() -> list:
    """[слово, ударение, перевод, род, аудио] — компактно, порядок = частотность."""
    out = []
    seen = set()
    for raw in (SRC / "words.tsv").read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        ru, fr = (x.strip() for x in raw.split("|", 1))
        key = ru.replace("+", "").lower().replace("ё", "е")
        if key in seen:
            errors.append(f"words.tsv: повтор «{ru}»")
            continue
        seen.add(key)
        acc = ru if "+" in ru else accent(ru)
        plain = acc.replace("+", "")
        stress = split_word(acc)[1] if " " not in plain else None
        g = ""
        if " " not in plain:
            parses = morph.parse(plain)
            p = parses[0]
            if p.tag.POS == "NOUN" and p.normal_form == plain.lower() and not any(x.tag.POS == "INFN" for x in parses):
                g = {"masc": "m", "femn": "f", "neut": "n"}.get(str(p.tag.gender), "")
        out.append([plain, stress, fr, g, clip(acc.lower(), WORD_VOICE, "w/")])
    return out


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
            wav_path = Path(tmp) / f"{cid.replace('/', '_')}.wav"
            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm)
            (AUDIO_DIR / f"{cid}.mp3").parent.mkdir(parents=True, exist_ok=True)
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

    levels = []
    for p in sorted((SRC / "levels").glob("*.json")):
        src = load(p)
        levels.append(build_lesson_v2(src) if src.get("version") == 2 else build_level(src))
        KNOWN_AT[src["id"]] = dict(KNOWN)
    levels.sort(key=lambda lv: lv["order"])
    alphabet = build_alphabet()
    reading = build_reading(alphabet)
    carte = build_carte()
    words = build_words()
    texts = build_texts()

    if errors:
        print("\n✗ Ошибки в контенте:")
        for e in errors:
            print("  -", e)
        return 1

    live = {f"{lv['id']}.json" for lv in levels}
    for old in (OUT / "levels").glob("*.json"):
        if old.name not in live:
            old.unlink()
    for lv in levels:
        lv["hasAudio"] = args.audio
        write(f"levels/{lv['id']}.json", lv)
    write("index.json", {
        "hasAudio": args.audio,
        "levels": [{"id": lv["id"], "order": lv["order"], "titleFr": lv["titleFr"], "titleRu": lv["titleRu"],
                    "emoji": lv["emoji"], "cando": lv["cando"], "version": lv.get("version", 1),
                    "parts": len(lv.get("parts", []))} for lv in levels],
    })
    write("alphabet.json", alphabet)
    write("reading.json", reading)
    write("carte.json", carte)
    write("words.json", words)
    write("texts.json", texts)
    print(f"Аудиофраз: {len(clips)}")
    if args.audio:
        print(f"Озвучено новых: {synthesize(args.force)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
