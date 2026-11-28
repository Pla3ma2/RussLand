/**
 * «Mots» — 5000 самых нужных слов, как в Oxford 5000:
 * ступени → уровни по 20 слов → карточки → тест (3 ошибки = заново).
 * Плюс марафон по выученным словам и «Mes cartes» (свои карточки и закладки).
 */
import { getWords, lookupWord, wordKey } from "./content";
import { play, stop } from "./audio";
import { $, $$, ABC_BTN, bindAbc, confetti, esc, shuffle } from "./ui";
import { renderStressed } from "./stress";
import { translitHtml } from "./translit";
import { markActiveToday, progress, save } from "./state";
import { navigate } from "./router";
import { addCard, isSaved, myCards, removeCard, STAR, toggleBookmark } from "./cards";
import type { Word } from "./types";

const PER = 20;
export const STAGES = [
  { name: "Essentiel", emoji: "🌱", from: 0, to: 500, hint: "Les mots de tous les jours, sans eux rien ne marche." },
  { name: "Débutant", emoji: "🌿", from: 500, to: 1000, hint: "Pour parler de toi, de ta journée, de tes proches." },
  { name: "Élémentaire", emoji: "🌳", from: 1000, to: 2000, hint: "Pour tenir une vraie conversation." },
  { name: "Intermédiaire", emoji: "🏔️", from: 2000, to: 3500, hint: "Pour comprendre films, articles et chansons." },
  { name: "Avancé", emoji: "🚀", from: 3500, to: 5000, hint: "Pour t'exprimer avec précision." },
];

const lvlCount = (st: (typeof STAGES)[number]) => (st.to - st.from) / PER;
const firstLvl = (st: (typeof STAGES)[number]) => st.from / PER;
const stageOfLvl = (l: number) => STAGES.findIndex((s) => l >= firstLvl(s) && l < firstLvl(s) + lvlCount(s));
const doneLv = () => progress().words.levels;
const isDone = (l: number) => !!doneLv()[l];
/** Любой уровень можно начать сразу; пройденные подсвечиваются зелёным. */
const isOpen = (_l: number) => true;
const learnedIdx = () => Object.keys(doneLv()).filter((k) => doneLv()[+k]).flatMap((k) => Array.from({ length: PER }, (_, j) => +k * PER + j));

/** Слово для упражнений — из базы или из «Mes cartes». */
interface Item {
  key: string;
  ru: string;
  s: number | null;
  fr: string;
  a: string;
  g?: string;
}
const fromWord = (w: Word): Item => ({ key: `w${w.i}`, ru: w.ru, s: w.s, fr: w.fr, a: w.a, g: w.g });

const GENDER: Record<string, string> = { m: "masc.", f: "fém.", n: "neutre" };
const ruHtml = (it: { ru: string; s: number | null }) =>
  it.ru.split(" ").map((p, i, arr) => {
    const off = arr.slice(0, i).join(" ").length + (i ? 1 : 0);
    return renderStressed(p, it.s != null ? it.s - off : null, p);
  }).join(" ");
const sayIt = (it: Item) => play(it.a, it.ru);

/* ======================= главная вкладки ======================= */

export async function renderWordsHome(root: HTMLElement) {
  const page = $("#page", root);
  const learned = learnedIdx().length;
  const cards = myCards().length;
  const best = progress().words.best;
  page.innerHTML = `
    <section class="card">
      <h2>Les 5000 mots</h2>
      <p class="hint">Les mots les plus utilisés en russe, du plus utile au plus rare. Chaque niveau : 20 mots en cartes, puis un petit test.</p>
      <div class="meter"><span style="width:${(learned / 5000) * 100}%"></span></div>
      <p class="muted small-line"><b>${learned}</b> / 5000 mots appris</p>
    </section>
    <div class="duo">
      <button class="card mini-card" id="cards"><span class="mc-emoji">⭐</span><b>Mes cartes</b><small>${cards} carte${cards > 1 ? "s" : ""}</small></button>
      <button class="card mini-card" id="mara" ${learned < PER ? "data-locked" : ""}><span class="mc-emoji">🏃</span><b>Marathon</b><small>${learned < PER ? "après le 1er niveau" : `record : ${best}`}</small></button>
    </div>
    <section class="stages">
      ${STAGES.map((st, i) => {
        const n = lvlCount(st);
        const d = Array.from({ length: n }, (_, j) => firstLvl(st) + j).filter(isDone).length;
        return `<button class="card stage" data-s="${i}">
          <span class="stage-emoji">${st.emoji}</span>
          <span class="stage-body">
            <small>Mots ${st.from + 1}–${st.to}</small>
            <b>${st.name}</b>
            <span class="meter thin"><span style="width:${(d / n) * 100}%"></span></span>
            <small class="muted">${d} / ${n} niveaux</small>
          </span>
          <span class="go">›</span>
        </button>`;
      }).join("")}
    </section>`;
  $("#cards", page).onclick = () => navigate("words/cards");
  $("#mara", page).onclick = (e) => {
    const b = e.currentTarget as HTMLElement;
    if (b.hasAttribute("data-locked")) {
      b.classList.remove("shake");
      void b.offsetWidth;
      b.classList.add("shake");
      return;
    }
    navigate("words/marathon");
  };
  $$<HTMLButtonElement>(".stage", page).forEach((b) => (b.onclick = () => navigate(`words/s/${b.dataset.s}`)));
}

/* ======================= ступень: сетка уровней ======================= */

function flowFrame(root: HTMLElement, title: string, back: string, body: string, foot = "") {
  root.innerHTML = `
    <div class="flow">
      <header class="flow-head"><button class="close" aria-label="Retour">✕</button><div class="flow-title">${title}</div>${ABC_BTN}</header>
      <main class="card-stack">${body}</main>
      ${foot ? `<footer class="flow-foot">${foot}</footer>` : ""}
    </div>`;
  $(".close", root).onclick = () => {
    stop();
    navigate(back);
  };
  bindAbc(root);
}

export async function renderStage(root: HTMLElement, sStr: string) {
  const st = STAGES[+sStr];
  if (!st) return navigate("words");
  const n = lvlCount(st);
  const f = firstLvl(st);
  flowFrame(root, `${st.emoji} ${st.name}`, "words", `
    <section class="card"><p class="hint" style="margin:0">${esc(st.hint)} Commence par n'importe quel niveau : ceux que tu as réussis sont en <b class="ok-txt">vert</b>.</p></section>
    <section class="lvl-grid">
      ${Array.from({ length: n }, (_, j) => {
        const l = f + j;
        const cls = isDone(l) ? "done" : "open";
        return `<button class="lvl ${cls}" data-l="${l}"><b>${j + 1}</b><small>${isDone(l) ? "✓ appris" : `${l * PER + 1}–${l * PER + PER}`}</small></button>`;
      }).join("")}
    </section>`);
  $$<HTMLButtonElement>(".lvl", root).forEach((b) => {
    b.onclick = () => {
      if (b.classList.contains("locked")) {
        b.classList.remove("shake");
        void b.offsetWidth;
        b.classList.add("shake");
        return;
      }
      navigate(`words/l/${b.dataset.l}`);
    };
  });
  // к первому непройденному уровню
  root.querySelector(".lvl:not(.done)")?.scrollIntoView({ block: "center" });
}

/* ======================= уровень: список → карточки → тест ======================= */

export async function renderWordLevel(root: HTMLElement, lStr: string) {
  const l = +lStr;
  const ws = await getWords();
  const s = stageOfLvl(l);
  if (s < 0 || !isOpen(l)) return navigate("words");
  const words = ws.slice(l * PER, l * PER + PER);
  const num = l - firstLvl(STAGES[s]) + 1;
  flowFrame(root, `${STAGES[s].name} · niveau ${num}`, `words/s/${s}`, `
    <section class="card">
      <p class="hint" style="margin:0 0 6px">Touche un mot pour l'écouter. ☆ = l'ajouter à « Mes cartes ».</p>
      <ul class="wlist">${words.map((w) => wordRow(fromWord(w))).join("")}</ul>
    </section>`, `<div class="foot-duo"><button class="secondary" id="test">Passer le test</button><button class="primary" id="learn">Apprendre</button></div>`);
  bindRows(root, words.map(fromWord));
  $("#learn", root).onclick = () => flashcards(root, l, words.map(fromWord));
  $("#test", root).onclick = () => levelTest(root, l, ws);
}

function wordRow(it: Item, del = false): string {
  return `<li class="wrow" data-k="${esc(it.key)}">
    <button class="wplay"><span class="wru">${ruHtml(it)}</span>${it.g ? `<i class="g g-${it.g}">${GENDER[it.g]}</i>` : ""}<span class="wfr">${esc(it.fr)}</span></button>
    ${del ? `<button class="wdel" aria-label="Supprimer">✕</button>` : STAR(isSaved(it.ru))}
  </li>`;
}

function bindRows(root: HTMLElement, items: Item[], onDelete?: (it: Item) => void) {
  const byKey = new Map(items.map((it) => [it.key, it]));
  $$<HTMLLIElement>(".wrow", root).forEach((li) => {
    const it = byKey.get(li.dataset.k!)!;
    $(".wplay", li).onclick = () => {
      li.classList.add("ping");
      setTimeout(() => li.classList.remove("ping"), 400);
      sayIt(it);
    };
    const star = li.querySelector<HTMLButtonElement>(".star");
    if (star) star.onclick = () => starToggle(star, it);
    const del = li.querySelector<HTMLButtonElement>(".wdel");
    if (del && onDelete) del.onclick = () => onDelete(it);
  });
}

async function starToggle(btn: HTMLButtonElement, it: Item) {
  const on = await toggleBookmark(it.ru, it.fr, it.s, it.a);
  btn.classList.toggle("on", on);
  btn.textContent = on ? "★" : "☆";
}

/** Карточки: русское слово (со звуком) → тап → перевод. «Je savais» / «À revoir». */
function flashcards(root: HTMLElement, l: number, items: Item[]) {
  let queue = shuffle(items);
  const total = items.length;
  let known = 0;
  const s = stageOfLvl(l);
  const draw = () => {
    if (!queue.length) {
      flowFrame(root, "Cartes", `words/l/${l}`, `
        <section class="card center">
          <div class="trophy">🃏</div>
          <h2>Tu as vu les ${total} mots !</h2>
          <p>Maintenant, le test : 3 erreurs maximum.</p>
        </section>`, `<div class="foot-duo"><button class="secondary" id="again">Revoir les cartes</button><button class="primary" id="test">Passer le test</button></div>`);
      $("#again", root).onclick = () => flashcards(root, l, items);
      $("#test", root).onclick = async () => levelTest(root, l, await getWords());
      return;
    }
    const it = queue[0];
    flowFrame(root, `${STAGES[s].name} · cartes`, `words/l/${l}`, `
      <div class="progress single"><div class="pstep now"><span style="--p:${(known / total) * 100}%"></span></div></div>
      <div class="flash" id="card" role="button" tabindex="0">
        <span class="flash-top">${it.g ? `<i class="g g-${it.g}">${GENDER[it.g]}</i>` : "<i></i>"}<span class="star-slot">${STAR(isSaved(it.ru))}</span></span>
        <span class="flash-ru">${ruHtml(it)}</span>
        <span class="flash-back hidden"><span class="flash-tl">${it.ru.split(" ").map((p) => translitHtml(p, null)).join(" ")}</span><span class="flash-fr">${esc(it.fr)}</span></span>
        <span class="flash-tap">Touche pour voir la traduction</span>
      </div>
      <div class="row"><button class="icon play big-play" aria-label="Écouter">🔊</button></div>`,
      `<div class="foot-duo"><button class="secondary bad-btn" id="no">À revoir</button><button class="primary" id="yes">Je savais ✓</button></div>`);
    const card = $("#card", root);
    card.onclick = (e) => {
      if ((e.target as HTMLElement).closest(".star")) return;
      card.classList.add("flipped");
      $(".flash-back", card).classList.remove("hidden");
      $(".flash-tap", card).classList.add("hidden");
      sayIt(it);
    };
    const star = root.querySelector<HTMLButtonElement>(".star")!;
    star.onclick = (e) => {
      e.stopPropagation();
      starToggle(star, it);
    };
    $(".big-play", root).onclick = () => sayIt(it);
    $("#yes", root).onclick = () => {
      queue.shift();
      known++;
      draw();
    };
    $("#no", root).onclick = () => {
      queue.shift();
      // вернётся через пару карточек
      queue.splice(Math.min(3, queue.length), 0, it);
      draw();
    };
    sayIt(it);
  };
  draw();
}

/* ---------- вопросы ---------- */

type QType = "ru2fr" | "fr2ru" | "listen";
const frParts = (fr: string) => fr.toLowerCase().replace(/\([^)]*\)/g, "").split(/[,;/]| ou /).map((x) => x.replace(/…/g, "").trim()).filter(Boolean);

/** Неоднозначности нет: у отвлекающих вариантов не должно быть общего значения с правильным. */
function distractors(it: Item, pool: Item[], n = 3): Item[] {
  const mine = new Set(frParts(it.fr));
  const k = wordKey(it.ru);
  const out: Item[] = [];
  const seenFr = new Set<string>();
  for (const c of shuffle(pool)) {
    if (out.length >= n) break;
    if (wordKey(c.ru) === k || c.fr === it.fr) continue;
    const parts = frParts(c.fr);
    if (parts.some((p) => mine.has(p)) || seenFr.has(c.fr) || parts.some((p) => seenFr.has(p))) continue;
    parts.forEach((p) => seenFr.add(p));
    seenFr.add(c.fr);
    out.push(c);
  }
  return out;
}

interface QOpts {
  root: HTMLElement;
  head: string; // html шапки (сердца, счёт)
  back: string;
  title: string;
  pct: number;
  onAnswer: (ok: boolean) => void;
}

function askQuestion(it: Item, type: QType, pool: Item[], o: QOpts) {
  const opts = shuffle([it, ...distractors(it, pool)]);
  const showRu = type === "fr2ru";
  const prompt =
    type === "ru2fr"
      ? `<div class="task-kicker">Que veut dire ce mot ?</div><button class="q-ru" id="say">${ruHtml(it)}</button>`
      : type === "listen"
        ? `<div class="task-kicker">Écoute. Que veut dire ce mot ?</div><button class="mic small-mic" id="say" type="button">🔊</button>`
        : `<div class="task-kicker">Comment dit-on en russe ?</div><div class="q-fr">« ${esc(it.fr)} »</div>`;
  flowFrame(o.root, o.title, o.back, `
    <div class="progress single"><div class="pstep now"><span style="--p:${o.pct}%"></span></div></div>
    ${o.head}
    <section class="card center">${prompt}</section>
    <section class="tiles col-tiles">${opts.map((c, i) => `<button class="tile wide ${showRu ? "ru-opt" : ""}" data-i="${i}">${showRu ? ruHtml(c) : esc(c.fr)}</button>`).join("")}</section>
    <div id="fbslot"></div>`, `<button class="primary hidden" id="next">Continuer</button>`);
  o.root.querySelector("#say")?.addEventListener("click", () => sayIt(it));
  if (type !== "fr2ru") sayIt(it);
  let done = false;
  $$<HTMLButtonElement>(".tile[data-i]", o.root).forEach((b) => {
    b.onclick = async () => {
      if (done) return;
      done = true;
      const c = opts[+b.dataset.i!];
      const ok = c === it;
      b.classList.add(ok ? "right" : "wrong");
      if (!ok) $$<HTMLButtonElement>(".tile[data-i]", o.root).find((x) => opts[+x.dataset.i!] === it)?.classList.add("right");
      $("#fbslot", o.root).innerHTML = `<div class="fb ${ok ? "good" : "bad"}"><b>${ok ? "Bravo !" : "Pas tout à fait."}</b>
        <div><span class="fb-ru">${ruHtml(it)}</span> = ${esc(it.fr)}</div>
        ${ok ? "" : `<small>« ${showRu ? ruHtml(c) : esc(c.ru)} » = ${esc(c.fr)}</small>`}</div>`;
      const next = $("#next", o.root);
      next.classList.remove("hidden");
      next.onclick = () => {
        stop();
        o.onAnswer(ok);
      };
      if (ok) {
        await sayIt(it);
        if (!next.isConnected) return;
        o.onAnswer(ok);
      } else sayIt(it);
    };
  });
}

const hearts = (left: number) => `<div class="hearts">${"❤️".repeat(left)}${"🤍".repeat(3 - left)}</div>`;
const pickType = (i: number): QType => (["ru2fr", "fr2ru", "listen", "fr2ru", "ru2fr"] as QType[])[i % 5];

/** Тест уровня: 20 слов + до 5 слов из прошлых уровней. Ошибочные возвращаются в конец. */
function levelTest(root: HTMLElement, l: number, ws: Word[]) {
  const items = ws.slice(l * PER, l * PER + PER).map(fromWord);
  const prev = learnedIdx().filter((i) => i < l * PER);
  const review = shuffle(prev).slice(0, 5).map((i) => fromWord(ws[i]));
  // отвлекающие — из соседних слов (похожая «трудность»)
  const pool = ws.slice(Math.max(0, l * PER - 200), l * PER + 200).map(fromWord);
  let queue = shuffle([...items, ...review]);
  const total = queue.length;
  let right = 0;
  let errors = 0;
  let k = 0;
  const s = stageOfLvl(l);
  const step = () => {
    if (errors >= 3) return fail();
    if (!queue.length) return pass();
    const it = queue.shift()!;
    askQuestion(it, pickType(k++), pool, {
      root,
      head: hearts(3 - errors),
      back: `words/l/${l}`,
      title: `${STAGES[s].name} · test`,
      pct: (right / total) * 100,
      onAnswer: (ok) => {
        if (ok) right++;
        else {
          errors++;
          queue.push(it);
        }
        step();
      },
    });
  };
  const fail = () => {
    flowFrame(root, "Test", `words/l/${l}`, `
      <section class="card center">
        <div class="trophy">💪</div>
        <h2>Presque !</h2>
        <p>3 erreurs. Revois les cartes une fois de plus, puis réessaie.</p>
      </section>`, `<div class="foot-duo"><button class="secondary" id="cards">Revoir les cartes</button><button class="primary" id="retry">Réessayer</button></div>`);
    $("#cards", root).onclick = () => flashcards(root, l, items);
    $("#retry", root).onclick = () => levelTest(root, l, ws);
  };
  const pass = () => {
    markActiveToday();
    save((p) => (p.words.levels[l] = true));
    const nextL = l + 1;
    const hasNext = stageOfLvl(nextL) === s;
    flowFrame(root, "Test réussi", `words/s/${s}`, `
      <section class="card center">
        <div class="trophy">🏆</div>
        <h2>Niveau réussi !</h2>
        <p>${errors === 0 ? "Sans aucune erreur. Bravo !" : `Avec ${errors} erreur${errors > 1 ? "s" : ""}.`}</p>
        <p class="muted">${learnedIdx().length} mots appris au total.</p>
      </section>`, `<button class="primary" id="go">${hasNext ? "Niveau suivant" : "Retour"}</button>`);
    confetti(root);
    $("#go", root).onclick = () => navigate(hasNext ? `words/l/${nextL}` : `words/s/${s}`);
  };
  step();
}

/* ======================= марафон ======================= */

function marathon(root: HTMLElement, items: Item[], pool: Item[], back: string, title: string, bestKey: "best" | "cardsBest") {
  let score = 0;
  let errors = 0;
  let k = 0;
  const recent: string[] = [];
  const step = () => {
    if (errors >= 3) return over();
    let it = items[Math.floor(Math.random() * items.length)];
    for (let t = 0; t < 10 && recent.includes(it.key); t++) it = items[Math.floor(Math.random() * items.length)];
    recent.push(it.key);
    if (recent.length > Math.min(10, items.length - 1)) recent.shift();
    askQuestion(it, pickType(k++), pool, {
      root,
      head: `<div class="mara-head">${hearts(3 - errors)}<b class="score">${score}</b></div>`,
      back,
      title,
      pct: Math.min(100, (score / Math.max(10, progress().words[bestKey] ?? 0)) * 100),
      onAnswer: (ok) => {
        if (ok) score++;
        else errors++;
        step();
      },
    });
  };
  const over = () => {
    markActiveToday();
    const prevBest = progress().words[bestKey] ?? 0;
    const record = score > prevBest;
    if (record) save((p) => (p.words[bestKey] = score));
    flowFrame(root, title, back, `
      <section class="card center">
        <div class="trophy">${record ? "🥇" : "🏃"}</div>
        <h2>${score} bonne${score > 1 ? "s" : ""} réponse${score > 1 ? "s" : ""}</h2>
        <p>${record ? "Nouveau record !" : `Ton record : ${prevBest}`}</p>
      </section>`, `<div class="foot-duo"><button class="secondary" id="out">Terminer</button><button class="primary" id="again">Encore</button></div>`);
    if (record && score > 0) confetti(root);
    $("#out", root).onclick = () => navigate(back);
    $("#again", root).onclick = () => marathon(root, items, pool, back, title, bestKey);
  };
  step();
}

export async function renderMarathon(root: HTMLElement) {
  const ws = await getWords();
  const idx = learnedIdx();
  if (idx.length < PER) return navigate("words");
  const items = idx.map((i) => fromWord(ws[i]));
  const maxI = Math.max(...idx);
  const pool = ws.slice(0, Math.max(maxI + 100, 200)).map(fromWord);
  marathon(root, items, pool, "words", "🏃 Marathon", "best");
}

/* ======================= Mes cartes ======================= */

const cardItem = (c: ReturnType<typeof myCards>[number]): Item => ({ key: `c${c.id}`, ru: c.ru, s: c.s ?? null, fr: c.fr, a: c.a ?? "" });

export async function renderMyCards(root: HTMLElement) {
  const ws = await getWords();
  const cards = myCards();
  const items = cards.map(cardItem);
  const best = progress().words.cardsBest ?? 0;
  flowFrame(root, "⭐ Mes cartes", "words", `
    <section class="card">
      <h3>Ajouter un mot</h3>
      <input id="q" class="field" placeholder="Chercher : en russe ou en français" autocomplete="off">
      <ul class="sugg" id="sugg"></ul>
      <details class="own" id="own">
        <summary>Mot introuvable ? Crée ta carte</summary>
        <input id="ru" class="field" placeholder="Mot russe (ex. : дача)" autocomplete="off" lang="ru">
        <div id="found" class="hint"></div>
        <input id="fr" class="field" placeholder="Traduction en français" autocomplete="off">
        <button class="primary" id="add">Ajouter</button>
        <div id="err" class="hint bad-txt"></div>
      </details>
    </section>
    <section class="card">
      <div class="mc-head"><h3>Mes ${cards.length} carte${cards.length > 1 ? "s" : ""}</h3>${cards.length >= 4 ? `<small class="muted">record : ${best}</small>` : ""}</div>
      ${cards.length ? `<ul class="wlist">${items.map((it) => wordRow(it, true)).join("")}</ul>` : `<p class="hint">Vide pour l'instant. Ajoute des mots ici, ou touche ☆ sur un mot pendant les leçons et dans les 5000 mots.</p>`}
    </section>`,
    cards.length >= 4
      ? `<button class="primary" id="mara">🏃 Marathon (${cards.length} cartes)</button>`
      : `<button class="primary" disabled>Marathon : encore ${4 - cards.length} carte${4 - cards.length > 1 ? "s" : ""}</button>`);

  bindRows(root, items, (it) => {
    removeCard(it.key.slice(1));
    renderMyCards(root);
  });
  root.querySelector("#mara")?.addEventListener("click", () => {
    // отвлекающие: свои карточки + слова базы, если своих мало
    const pool = items.length >= 8 ? items : [...items, ...ws.slice(0, 600).map(fromWord)];
    marathon(root, items, pool, "words/cards", "🏃 Mes cartes", "cardsBest");
  });

  // поиск по базе: кириллица — по русскому слову, иначе — по переводу
  const q = $<HTMLInputElement>("#q", root);
  const sugg = $("#sugg", root);
  const search = () => {
    const v = q.value.trim().toLowerCase();
    if (v.length < 2) return void (sugg.innerHTML = "");
    const cyr = /[а-яё]/i.test(v);
    const key = wordKey(v);
    const res: Word[] = [];
    for (const w of ws) {
      if (res.length >= 6) break;
      if (cyr ? wordKey(w.ru).startsWith(key) : frParts(w.fr).some((p) => p.startsWith(v) || p.split(/\s+/).some((x) => x.replace(/^(l'|d')/, "") === v))) res.push(w);
    }
    sugg.innerHTML = res.length
      ? res.map((w) => `<li><button class="sg" data-i="${w.i}"><span class="wru">${ruHtml(w)}</span><span class="wfr">${esc(w.fr)}</span><span class="sg-add">${isSaved(w.ru) ? "✓" : "+"}</span></button></li>`).join("")
      : `<li class="hint">Pas dans les 5000 mots. Crée ta carte ci-dessous.</li>`;
    if (!res.length) ($("#own", root) as HTMLDetailsElement).open = true;
    $$<HTMLButtonElement>(".sg", sugg).forEach((b) => {
      b.onclick = () => {
        const w = ws[+b.dataset.i!];
        play(w.a, w.ru);
        if (!isSaved(w.ru)) addCard({ ru: w.ru, fr: w.fr, s: w.s, a: w.a, src: "custom" });
        renderMyCards(root);
      };
    });
  };
  q.oninput = search;

  // своя карточка: если слово есть в базе — перевод и озвучка оттуда
  const ru = $<HTMLInputElement>("#ru", root);
  const fr = $<HTMLInputElement>("#fr", root);
  const found = $("#found", root);
  let base: Word | undefined;
  let autoFr = "";
  ru.oninput = async () => {
    const v = ru.value;
    const w = await lookupWord(v);
    if (ru.value !== v) return;
    base = w;
    if (w) {
      found.innerHTML = `✓ Dans la base : <button class="link" id="hear">${ruHtml(w)} 🔊</button> — ${esc(w.fr)}`;
      $("#hear", found).onclick = () => play(w.a, w.ru);
      if (!fr.value || fr.value === autoFr) fr.value = autoFr = w.fr;
    } else {
      found.innerHTML = v.trim() ? "Pas dans la base : la voix du téléphone le lira." : "";
      if (fr.value === autoFr) fr.value = autoFr = "";
    }
  };
  $("#add", root).onclick = () => {
    const err = $("#err", root);
    const r = ru.value.trim();
    const f = fr.value.trim();
    if (!r) return void (err.textContent = "Écris le mot russe.");
    if (!/[а-яё]/i.test(r)) return void (err.textContent = "Le mot russe doit être en cyrillique (АБВ…).");
    if (!f) return void (err.textContent = "Ajoute la traduction.");
    if (isSaved(base?.ru ?? r)) return void (err.textContent = "Ce mot est déjà dans tes cartes.");
    addCard(base && wordKey(base.ru) === wordKey(r) ? { ru: base.ru, fr: f, s: base.s, a: base.a, src: "custom" } : { ru: r, fr: f, s: null, src: "custom" });
    renderMyCards(root);
  };
}
