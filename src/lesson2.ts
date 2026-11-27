/**
 * Урок новой схемы. Фразы вводятся маленькими блоками и проходят «лестницу»:
 * услышать → повторить с текстом → узнать на слух → понять → связать пары →
 * дополнить → собрать → сказать самому (с подсказкой). Урок делится на части.
 */
import type { LevelV2, Line, PhraseV2, StepV2 } from "./types";
import { getIndex, getLevel } from "./content";
import { renderStressed } from "./stress";
import { play, playBlob, stop } from "./audio";
import { $, $$, ABC_BTN, bindAbc, bindTokens, confetti, esc, shuffle, sleep, speakBox, tokensHtml, voskToggle } from "./ui";
import { Recorder, normalize, recognize, toWav } from "./speech";
import { markActiveToday, progress, save } from "./state";
import { addItems } from "./srs";
import { navigate } from "./router";
import { frameBox } from "./level";

type Ex =
  | { k: "scene" }
  | { k: "intro"; p: string }
  | { k: "repeat"; p: string }
  | { k: "pickRu"; p: string }
  | { k: "pickFr"; p: string }
  | { k: "match"; ps: string[] }
  | { k: "gap"; p: string }
  | { k: "order"; p: string }
  | { k: "puzzle"; ps: string[] }
  | { k: "combo"; p: string }
  | { k: "speak"; p: string; hint: boolean }
  | { k: "insight"; i: number; examples: boolean }
  | { k: "explore" }
  | { k: "pick"; t: number }
  | { k: "roleplay" };

let lv: LevelV2;
let app: HTMLElement;

const P = (id: string): PhraseV2 => lv.phrases[id];
const partsDone = () => progress().levels[lv.id]?.parts ?? 0;

/* ======================= экран урока: список частей ======================= */

export async function renderLessonHome(root: HTMLElement, id: string) {
  app = root;
  lv = (await getLevel(id)) as unknown as LevelV2;
  await getIndex();
  const done = partsDone();
  app.innerHTML = `
    <div class="flow">
      <header class="flow-head"><button class="close" aria-label="Fermer">✕</button>
        <div class="flow-title">${lv.emoji} ${esc(lv.titleFr)}</div>${ABC_BTN}</header>
      <main class="card-stack">
        <section class="card">
          <div class="task-kicker">Leçon ${lv.order} · ${esc(lv.titleRu)}</div>
          <p class="scene">${esc(lv.sceneFr)}</p>
          <p class="hint">Trois petites parties de 4–5 minutes. Ta progression est enregistrée après chaque partie.</p>
        </section>
        <div class="stage-list">
          ${lv.parts.map((p, i) => {
            const isDone = i < done;
            const open = i <= done;
            return `<button class="stage ${isDone ? "done" : ""} ${open ? "" : "locked"}" data-i="${i}" ${open ? "" : "disabled"}>
              <span class="stage-n">${isDone ? "✓" : i + 1}</span>
              <span class="stage-body"><b>${esc(p.titleFr)}</b><small class="muted">Partie ${i + 1} sur ${lv.parts.length}</small></span>
              <span class="stage-go">${open ? (isDone ? "↺" : "▶") : "🔒"}</span></button>`;
          }).join("")}
        </div>
      </main>
    </div>`;
  $(".close", app).onclick = () => navigate("");
  bindAbc(app);
  $$<HTMLButtonElement>(".stage:not(.locked)", app).forEach((b) => (b.onclick = () => navigate(`level/${lv.id}/${b.dataset.i}`)));
}

/* ======================= генерация упражнений ======================= */

function buildPart(steps: StepV2[]): Ex[] {
  const out: Ex[] = [];
  let exploreShown = false;
  for (const st of steps) {
    switch (st.type) {
      case "scene":
        out.push({ k: "scene" });
        break;
      case "block": {
        const ps = st.phrases;
        const rv = st.review ?? [];
        // 1) знакомство + повтор вслух с текстом
        for (const p of ps) out.push({ k: "intro", p }, { k: "repeat", p });
        // 2) узнавание на слух и понимание, вперемешку
        const rec: Ex[] = [];
        ps.forEach((p, i) => rec.push(i % 2 ? { k: "pickFr", p } : { k: "pickRu", p }));
        ps.forEach((p, i) => rec.push(i % 2 ? { k: "pickRu", p } : { k: "pickFr", p }));
        out.push(...rec);
        // 3) пары
        const pool = [...ps, ...rv];
        if (pool.length >= 3) out.push({ k: "match", ps: shuffle(pool).slice(0, 4) });
        // 4) дополнить и собрать — новые фразы, между ними повтор старых
        const prod: Ex[] = [];
        for (const p of ps) if (P(p).gap) prod.push({ k: "gap", p });
        for (const r of rv) prod.push(P(r).orders ? { k: "order", p: r } : P(r).gap ? { k: "gap", p: r } : { k: "pickFr", p: r });
        for (const p of ps) if (P(p).orders) prod.push({ k: "order", p });
        out.push(...interleave(prod));
        // 5) сказать самому — только в конце блока, с подсказкой
        for (const p of ps) out.push({ k: "speak", p, hint: true });
        break;
      }
      case "warmup": {
        st.phrases.forEach((p, i) => out.push(i % 2 ? { k: "pickRu", p } : { k: "pickFr", p }));
        if (st.phrases.length >= 3) out.push({ k: "match", ps: shuffle(st.phrases).slice(0, 4) });
        for (const p of shuffle(st.phrases).slice(0, 2)) out.push({ k: "speak", p, hint: true });
        break;
      }
      case "explore":
        out.push({ k: "explore" });
        lv.tasks.forEach((_, t) => out.push({ k: "pick", t }));
        exploreShown = true;
        break;
      case "insight":
        out.push({ k: "insight", i: st.index, examples: exploreShown });
        break;
      case "final": {
        const ids = Object.keys(lv.phrases);
        const prod: Ex[] = ids.map((p) =>
          P(p).orders ? { k: "order", p } : P(p).gap ? { k: "gap", p } : { k: "pickRu", p });
        out.push(...shuffle(prod));
        out.push(...shuffle(ids).map((p): Ex => ({ k: "speak", p, hint: true })));
        break;
      }
      case "combine": {
        // пазл: новые фразы из уже знакомых кусочков
        out.push({ k: "puzzle", ps: st.phrases });
        for (const p of st.phrases) out.push({ k: "combo", p });
        for (const p of shuffle(st.phrases)) out.push({ k: "speak", p, hint: true });
        break;
      }
      case "roleplay":
        out.push({ k: "roleplay" });
        break;
    }
  }
  return out;
}

/** Перемешивает, стараясь не ставить подряд упражнения с одной фразой. */
function interleave(list: Ex[]): Ex[] {
  const a = shuffle(list);
  for (let i = 1; i < a.length; i++) {
    const pi = (a[i - 1] as { p?: string }).p;
    if (pi && (a[i] as { p?: string }).p === pi) {
      const j = a.findIndex((x, k) => k > i && (x as { p?: string }).p !== pi);
      if (j > 0) [a[i], a[j]] = [a[j], a[i]];
    }
  }
  return a;
}


/** «Собери фразу». В пазле: новая фраза + лишние слова, и подпись, откуда кусочки. */
function orderTask(p: PhraseV2, ctx: Ctx, combo: boolean) {
    const words = p.tokens.filter((t) => t.w);

    const isName = (t: string) => lv.glossary[t.toLowerCase()]?.includes("prénom");
    const shown = (t: string) => (isName(t) ? t : t.toLowerCase());
    const extra = combo ? p.combo?.extra ?? [] : [];
    const pool = shuffle([...words, ...extra.map((x) => ({ t: x.t, s: x.s, a: x.a, w: true }))].map((t, i) => ({ id: i, t })));
    let answer: typeof pool = [];
    ctx.body.innerHTML = `
      ${combo ? `<div class="task-kicker">🧩 Nouvelle phrase</div><p class="hint center puzzle-hint">Tu connais déjà tous ces mots. Attention : il y a des morceaux en trop !</p>` : `<div class="task-kicker">Remets les mots dans l'ordre</div>`}
      <p class="fr big-fr center">« ${esc(p.fr)} »</p>
      <div class="answer-row"></div>
      <div class="tiles pool"></div>
      <div class="row"><button class="link small reset" type="button">Recommencer</button></div>`;
    const render = () => {
      $(".answer-row", ctx.body).innerHTML = answer.length
        ? answer.map((x, i) => `<button class="tile small" data-a="${i}"><span class="tw">${renderStressed(shown(x.t.t), x.t.s, x.t.t)}</span></button>`).join("")
        : `<span class="placeholder">Touche les mots dans le bon ordre</span>`;
      $(".pool", ctx.body).innerHTML = pool.filter((x) => !answer.includes(x))
        .map((x) => `<button class="tile small" data-p="${x.id}"><span class="tw">${renderStressed(shown(x.t.t), x.t.s, x.t.t)}</span></button>`).join("");
      $$<HTMLButtonElement>("[data-p]", ctx.body).forEach((b) => {
        b.onclick = () => {
          const x = pool.find((y) => y.id === Number(b.dataset.p))!;
          answer.push(x);
          if (x.t.a) play(x.t.a, x.t.t);
          render();
          if (answer.length === words.length) check();
        };
      });
      $$<HTMLButtonElement>("[data-a]", ctx.body).forEach((b) => {
        b.onclick = () => {
          answer.splice(Number(b.dataset.a), 1);
          render();
        };
      });
    };
    const check = async () => {
      const said = normalize(answer.map((x) => x.t.t).join(" "));
      const ok = (p.orders ?? []).some((o) => normalize(o) === said);
      const row = $(".answer-row", ctx.body);
      row.classList.add(ok ? "good" : "bad");
      row.innerHTML = `<div class="ru">${ok ? tokensHtml(p.tokens) : esc(answer.map((x) => shown(x.t.t)).join(" "))}</div>`;
      if (ok) bindTokens(row, p.tokens, { glossary: lv.glossary });
      $(".pool", ctx.body).innerHTML = "";
      $(".reset", ctx.body).remove();
      ctx.result(ok, `« ${ruHtml(p)} »`);
      await play(p.audio, p.ru);
    };
    $(".reset", ctx.body).onclick = () => {
      answer = [];
      render();
    };
    render();
}

/* ======================= прохождение части ======================= */

export async function renderPart(root: HTMLElement, id: string, partStr: string) {
  app = root;
  lv = (await getLevel(id)) as unknown as LevelV2;
  await getIndex();
  const partIdx = Number(partStr);
  const part = lv.parts[partIdx];
  if (!part || partIdx > partsDone()) return navigate(`level/${id}`);
  const queue = buildPart(part.steps);
  const retried = new WeakSet<Ex>();
  let k = 0;

  const frame = () => {
    app.innerHTML = `
      <div class="flow">
        <header class="flow-head"><button class="close" aria-label="Fermer">✕</button>
          <div class="flow-title">${lv.emoji} ${esc(lv.titleFr)} · ${partIdx + 1}/${lv.parts.length}</div>${ABC_BTN}</header>
        <div class="progress single"><div class="pstep now"><span style="--p:${(k / queue.length) * 100}%"></span></div></div>
        <main class="card-stack"><section class="card ex-card" id="ex"></section></main>
        <footer class="flow-foot">
          <div class="fb hidden"></div>
          <button id="next" class="primary" disabled>Continuer</button>
        </footer>
      </div>`;
    $(".close", app).onclick = () => {
      stop();
      navigate(`level/${lv.id}`);
    };
    bindAbc(app);
    $("#next", app).onclick = () => {
      stop();
      k++;
      if (k >= queue.length) return finishPart(partIdx);
      show();
    };
  };

  const show = () => {
    window.scrollTo({ top: 0 });
    frame();
    const ex = queue[k];
    const body = $("#ex", app);
    body.dataset.k = ex.k;
    if ("p" in ex) body.dataset.p = ex.p;
    if ("t" in ex) body.dataset.t = String(ex.t);
    const next = $<HTMLButtonElement>("#next", app);
    const fb = $(".fb", app);
    const ctx: Ctx = {
      body,
      ready(label = "Continuer") {
        next.disabled = false;
        next.textContent = label;
      },
      result(ok, correctHtml) {
        fb.classList.remove("hidden");
        fb.className = `fb ${ok ? "good" : "bad"}`;
        fb.innerHTML = ok
          ? `<b>${pickPraise()}</b>`
          : `<b>Pas tout à fait.</b>${correctHtml ? `<div>Bonne réponse : ${correctHtml}</div>` : ""}<small>Cette question reviendra un peu plus tard.</small>`;
        next.disabled = false;
        next.textContent = "Continuer";
        if (!ok && !retried.has(ex)) {
          retried.add(ex);
          const copy = { ...ex } as Ex;
          retried.add(copy);
          queue.splice(Math.min(queue.length, k + 3), 0, copy);
        }
      },
    };
    RENDER[ex.k](ex as never, ctx);
  };

  frame();
  show();
}

interface Ctx {
  body: HTMLElement;
  ready(label?: string): void;
  result(ok: boolean, correctHtml?: string): void;
}

const PRAISE = ["Bravo !", "Parfait !", "Très bien !", "Super !", "Exactement !"];
const pickPraise = () => PRAISE[Math.floor(Math.random() * PRAISE.length)];

const ruHtml = (p: Line) => p.tokens.map((t) => (t.w ? renderStressed(t.t, t.s, t.t) : esc(t.t))).join("");

function otherPhrases(p: string, n: number, filter: (x: PhraseV2) => boolean = () => true): PhraseV2[] {
  const me = P(p);
  return shuffle(Object.values(lv.phrases).filter((x) => x.id !== p && x.ru !== me.ru && x.fr !== me.fr && filter(x))).slice(0, n);
}

function audioBtn(p: Line, big = true) {
  return `<button class="mic small-mic ${big ? "" : "tiny"}" type="button" data-play aria-label="Écouter">🔊</button>
          <button class="link small" type="button" data-slow>🐢 plus lentement</button>`;
}

function bindAudio(root: HTMLElement, p: Line) {
  $("[data-play]", root).onclick = () => play(p.audio, p.ru);
  $("[data-slow]", root).onclick = () => play(p.audio, p.ru, 0.7);
}

/* ======================= виды упражнений ======================= */

const RENDER: { [K in Ex["k"]]: (ex: Extract<Ex, { k: K }>, ctx: Ctx) => void } = {
  scene(_ex, ctx) {
    ctx.body.innerHTML = `
      <div class="task-kicker">La scène</div>
      <p class="scene">${esc(lv.sceneFr)}</p>
      <p class="hint">Écoute d'abord la scène en entier, sans chercher à tout retenir. On va apprendre chaque phrase pas à pas.</p>
      <button id="play-all" class="secondary">▶ Écouter la scène</button>
      <div class="dialogue">${lv.dialogue.map((l, i) => bubble(l, i)).join("")}</div>`;
    lv.dialogue.forEach((l, i) => bindBubble($(`[data-line="${i}"]`, ctx.body), l));
    let playing = false;
    $("#play-all", ctx.body).onclick = async () => {
      if (playing) return;
      playing = true;
      for (let i = 0; i < lv.dialogue.length; i++) {
        const row = $(`[data-line="${i}"]`, ctx.body);
        if (!row) break;
        row.classList.add("speaking");
        await play(lv.dialogue[i].audio, lv.dialogue[i].ru);
        row.classList.remove("speaking");
        await sleep(300);
      }
      playing = false;
    };
    ctx.ready("Commencer");
  },

  intro(ex, ctx) {
    const p = P(ex.p);
    ctx.body.innerHTML = `
      <div class="task-kicker">Nouvelle phrase</div>
      <div class="dialogue">${bubble(p, 0)}</div>
      ${p.noteFr ? `<p class="note-tip">💡 ${esc(p.noteFr)}</p>` : ""}
      <p class="hint">Touche chaque mot pour l'entendre et voir comment il se lit.</p>`;
    bindBubble($("[data-line]", ctx.body), p);
    play(p.audio, p.ru);
    ctx.ready();
  },

  repeat(ex, ctx) {
    const p = P(ex.p);
    ctx.body.innerHTML = `
      <div class="task-kicker">Écoute et répète</div>
      <p class="hint">Écoute, puis répète à voix haute en lisant. Imite la mélodie !</p>
      <div class="center">
        <div class="ru big-ru">${tokensHtml(p.tokens)}</div>
        <div class="fr">${esc(p.fr)}</div>
        <div class="row"><button class="secondary" data-play>▶ Modèle</button><button class="secondary" data-slow>🐢 Lent</button></div>
        <button class="mic" type="button"><span class="mic-ico">🎙️</span><span class="mic-txt">Appuie et répète</span></button>
        <div class="heard"></div>
        <div class="row"><button class="secondary mine hidden" type="button">▶ Ma voix</button></div>
        <button class="link small skip" type="button">Je ne peux pas parler maintenant</button>
      </div>`;
    bindTokens($(".big-ru", ctx.body), p.tokens, { glossary: lv.glossary });
    bindAudio(ctx.body, p);
    play(p.audio, p.ru);
    recorder(ctx.body, p, () => ctx.ready());
    $(".skip", ctx.body).onclick = () => ctx.ready();
  },

  pickRu(ex, ctx) {
    const p = P(ex.p);
    const opts = shuffle([p, ...otherPhrases(ex.p, 2)]);
    ctx.body.innerHTML = `
      <div class="task-kicker">Qu'as-tu entendu ?</div>
      <div class="center">${audioBtn(p)}</div>
      <div class="col">${opts.map((o) => `<button class="tile wide ru-choice" data-id="${o.id}"><span class="tw">${ruHtml(o)}</span></button>`).join("")}</div>`;
    bindAudio(ctx.body, p);
    play(p.audio, p.ru);
    choice(ctx, (id) => id === p.id, `« ${ruHtml(p)} »`);
  },

  pickFr(ex, ctx) {
    const p = P(ex.p);
    const opts = shuffle([p, ...otherPhrases(ex.p, 2)]);
    ctx.body.innerHTML = `
      <div class="task-kicker">Que veut dire cette phrase ?</div>
      <div class="center">
        <div class="ru big-ru">${tokensHtml(p.tokens)}</div>
        ${audioBtn(p, false)}
      </div>
      <div class="col">${opts.map((o) => `<button class="tile wide" data-id="${o.id}">${esc(o.fr)}</button>`).join("")}</div>`;
    bindTokens($(".big-ru", ctx.body), p.tokens, { glossary: lv.glossary, translit: true });
    bindAudio(ctx.body, p);
    play(p.audio, p.ru);
    choice(ctx, (id) => id === p.id, `« ${esc(p.fr)} »`);
  },

  match(ex, ctx) {
    const ps = ex.ps.map(P);
    const left = shuffle(ps);
    const right = shuffle(ps);
    ctx.body.innerHTML = `
      <div class="task-kicker">Associe les paires</div>
      <p class="hint">Touche une phrase russe (tu l'entends), puis sa traduction.</p>
      <div class="match">
        <div class="mcol">${left.map((p) => `<button class="tile mtile" data-l="${p.id}"><span class="tw">${ruHtml(p)}</span></button>`).join("")}</div>
        <div class="mcol">${right.map((p) => `<button class="tile mtile fr-tile" data-r="${p.id}">${esc(p.fr)}</button>`).join("")}</div>
      </div>`;
    let selL: string | null = null;
    let selR: string | null = null;
    let matched = 0;
    const check = () => {
      if (!selL || !selR) return;
      const l = $(`[data-l="${selL}"]`, ctx.body);
      const r = $(`[data-r="${selR}"]`, ctx.body);
      if (selL === selR) {
        [l, r].forEach((b) => {
          b.classList.remove("picked");
          b.classList.add("right");
          (b as HTMLButtonElement).disabled = true;
        });
        matched++;
        if (matched === ps.length) ctx.result(true);
      } else {
        [l, r].forEach((b) => {
          b.classList.remove("picked", "shake");
          void b.offsetWidth;
          b.classList.add("shake");
        });
      }
      selL = selR = null;
    };
    $$<HTMLButtonElement>("[data-l]", ctx.body).forEach((b) => {
      b.onclick = () => {
        $$("[data-l]", ctx.body).forEach((x) => x.classList.remove("picked"));
        b.classList.add("picked");
        selL = b.dataset.l!;
        const p = P(selL);
        play(p.audio, p.ru);
        check();
      };
    });
    $$<HTMLButtonElement>("[data-r]", ctx.body).forEach((b) => {
      b.onclick = () => {
        $$("[data-r]", ctx.body).forEach((x) => x.classList.remove("picked"));
        b.classList.add("picked");
        selR = b.dataset.r!;
        check();
      };
    });
  },

  gap(ex, ctx) {
    const p = P(ex.p);
    const g = p.gap!;
    const right = p.tokens[g.index];
    const opts = shuffle([{ t: right.t, a: right.a!, s: right.s ?? null, ok: true }, ...g.distractors.map((d) => ({ ...d, ok: false }))]);
    const cap = (t: string) => (g.index === 0 ? t[0].toUpperCase() + t.slice(1) : t);
    ctx.body.innerHTML = `
      <div class="task-kicker">Complète la phrase</div>
      <p class="fr big-fr center">« ${esc(p.fr)} »</p>
      <div class="frame"><span class="frame-ru">${p.tokens.map((t, i) =>
        i === g.index ? `<span class="slot">…</span>` : t.w ? renderStressed(t.t, t.s, t.t) : esc(t.t)).join("")}</span></div>
      <div class="tiles">${opts.map((o, i) => `<button class="tile" data-o="${i}"><span class="tw">${renderStressed(cap(o.t), o.s, o.t)}</span></button>`).join("")}</div>`;
    let answered = false;
    $$<HTMLButtonElement>("[data-o]", ctx.body).forEach((b) => {
      b.onclick = async () => {
        if (answered) return;
        answered = true;
        const o = opts[Number(b.dataset.o)];
        const slot = $(".slot", ctx.body);
        slot.className = "slot filled";
        slot.innerHTML = renderStressed(cap(right.t), right.s, right.t);
        b.classList.add(o.ok ? "right" : "wrong");
        if (!o.ok) $$<HTMLButtonElement>("[data-o]", ctx.body).find((x) => opts[Number(x.dataset.o)].ok)?.classList.add("right");
        ctx.result(o.ok, `« ${ruHtml(p)} »${!o.ok && g.whyFr ? `<small>${esc(g.whyFr)}</small>` : ""}`);
        await play(p.audio, p.ru);
      };
    });
  },

  order(ex, ctx) {
    orderTask(P(ex.p), ctx, false);
  },

  puzzle(ex, ctx) {
    const from = [...new Set(ex.ps.flatMap((id) => P(id).combo?.from ?? []))];
    ctx.body.innerHTML = `
      <div class="task-kicker">🧩 Le puzzle</div>
      <h2>Tu peux déjà dire beaucoup plus !</h2>
      <p>Avec les mots que tu connais, on peut construire des phrases toutes neuves. C'est comme un puzzle : tu prends un morceau d'une phrase, un morceau d'une autre… et tu obtiens une phrase à toi.</p>
      <p class="hint">Les morceaux viennent de : ${from.map((t) => `<b>${esc(t)}</b>`).join(", ")}.</p>`;
    ctx.ready("C'est parti");
  },

  combo(ex, ctx) {
    orderTask(P(ex.p), ctx, true);
  },
  speak(ex, ctx) {
    const p = P(ex.p);
    const words = p.tokens.filter((t) => t.w);
    ctx.body.innerHTML = `
      <div class="task-kicker">À toi de le dire</div>
      ${ex.hint ? `<div class="hint-box"><button class="link small" id="hint" type="button">💡 Un indice</button><div id="hint-out"></div></div>` : ""}
      <div id="sp"></div>
      <div class="selfcheck hidden">
        <p class="hint center">Tu l'as bien dit ?</p>
        <div class="row"><button class="secondary" id="no" type="button">✗ Pas encore</button><button class="secondary" id="yes" type="button">✓ Oui</button></div>
      </div>
      <div id="vosk" class="vosk"></div>`;
    voskToggle($("#vosk", ctx.body));
    let hintLevel = 0;
    $("#hint", ctx.body)?.addEventListener("click", () => {
      hintLevel++;
      const out = $("#hint-out", ctx.body);
      if (hintLevel === 1) {
        out.innerHTML = `<div class="tiles">${shuffle(words).map((t) => `<span class="tile small ghost"><span class="tw">${renderStressed(t.t.toLowerCase(), t.s, t.t)}</span></span>`).join("")}</div>`;
      } else {
        out.innerHTML = `<div class="first-letters">${words.map((t) => `${esc(t.t[0])}${"_".repeat(Math.max(1, t.t.length - 1))}`).join(" ")}</div>`;
        $("#hint", ctx.body).remove();
      }
    });
    speakBox($("#sp", ctx.body), p, lv.grammar, {
      glossary: lv.glossary,
      onDone: (r) => {
        $("#hint", ctx.body)?.remove();
        if (r.recognized !== undefined) {
          ctx.result(!!r.ok, r.ok ? undefined : `« ${ruHtml(p)} »`);
          return;
        }
        $(".selfcheck", ctx.body).classList.remove("hidden");
        $("#yes", ctx.body).onclick = () => {
          $(".selfcheck", ctx.body).remove();
          ctx.result(true);
        };
        $("#no", ctx.body).onclick = () => {
          $(".selfcheck", ctx.body).remove();
          ctx.result(false);
        };
      },
    });
  },

  insight(ex, ctx) {
    const ins = lv.insights[ex.i];
    const by = lv.speakers[ins.by];
    const examples = ex.examples
      ? `<div class="examples">${lv.explore.words.map((w) => `<div class="ex">${esc(w.phrase)} <small class="muted">${esc(w.phraseFr)}</small></div>`).join("")}</div>`
      : "";
    ctx.body.innerHTML = `
      <div class="bubble-row left">
        <div class="avatar" style="background:${by.color}">${by.nameFr[0]}</div>
        <div class="bubble big">
          <div class="who">${esc(by.nameFr)} t'explique</div>
          ${ins.fr.map((x) => `<p>${esc(x)}</p>`).join("")}
        </div>
      </div>${examples}`;
    ctx.ready("J'ai compris");
  },

  explore(_ex, ctx) {
    const ex = lv.explore;
    ctx.body.innerHTML = `
      <div class="task-kicker">Construis la phrase</div>
      <p class="hint">${esc(ex.hintFr || "Mets chaque mot dans la phrase et écoute.")}</p>
      <div class="frame"><div class="frame-host"></div><div class="fr frame-fr">${esc(ex.frameFr)}</div></div>
      <div class="tiles explore-tiles">${ex.words.map((w, i) => `<button class="tile" data-w="${i}">
        <span class="tile-ru">${renderStressed(w.tile, w.tileStress, w.tile)}</span><span class="tile-fr">${esc(w.fr)}</span></button>`).join("")}</div>`;
    const box = frameBox($(".frame-host", ctx.body), ex);
    const seen = new Set<number>();
    let busy = false;
    $$<HTMLButtonElement>(".explore-tiles .tile", ctx.body).forEach((b) => {
      b.onclick = async () => {
        if (busy) return;
        busy = true;
        const i = Number(b.dataset.w);
        const w = ex.words[i];
        $$(".explore-tiles .tile", ctx.body).forEach((t) => t.classList.remove("picked"));
        b.classList.add("picked", "seen");
        await box.put(w, false);
        $(".frame-fr", ctx.body).textContent = w.phraseFr;
        await play(w.audioPhrase, w.phrase);
        seen.add(i);
        busy = false;
        if (seen.size === ex.words.length) ctx.ready();
      };
    });
  },

  pick(ex, ctx) {
    const task = lv.tasks[ex.t];
    const exp = lv.explore;
    ctx.body.innerHTML = `
      <div class="task-kicker">Défi</div>
      <h2>${esc(task.fr)}</h2>
      <div class="frame"><div class="frame-host"></div></div>
      <div class="tiles">${shuffle(exp.words.map((w, i) => ({ w, i }))).map(({ w, i }) =>
        `<button class="tile" data-w="${i}"><span class="tile-ru">${renderStressed(w.tile, w.tileStress, w.tile)}</span></button>`).join("")}</div>
      <div class="feedback"></div>`;
    const box = frameBox($(".frame-host", ctx.body), exp, false);
    let solved = false;
    let mistakes = 0;
    $$<HTMLButtonElement>(".tile", ctx.body).forEach((b) => {
      b.onclick = async () => {
        if (solved) return;
        const w = exp.words[Number(b.dataset.w)];
        if (w.tile !== task.answer) {
          mistakes++;
          b.classList.remove("shake");
          void b.offsetWidth;
          b.classList.add("shake", "wrong");
          // объясняем, почему не подходит
          $(".feedback", ctx.body).innerHTML = `« ${esc(w.tile)} » = ${esc(w.fr)}. Essaie encore !`;
          play(w.audioTile, w.tile);
          return;
        }
        solved = true;
        b.classList.add("right");
        $(".feedback", ctx.body).textContent = "";
        await box.put(w, false);
        ctx.result(mistakes === 0, `« ${esc(w.phrase)} »`);
        await play(w.audioPhrase, w.phrase);
      };
    });
  },

  roleplay(_ex, ctx) {
    const me = lv.speakers[lv.learner].nameFr;
    ctx.body.innerHTML = `
      <div class="task-kicker">Joue la scène</div>
      <p class="hint">Cette fois, c'est toi ${esc(me)} ! Quand c'est ton tour, dis ta réplique, puis écoute la bonne version.</p>
      <div class="dialogue roleplay"></div>
      <div id="rp-turn"></div>`;
    const log = $(".roleplay", ctx.body);
    const turn = $("#rp-turn", ctx.body);
    let i = 0;
    const advance = async () => {
      while (i < lv.dialogue.length && lv.dialogue[i].speaker !== lv.learner) {
        log.insertAdjacentHTML("beforeend", bubble(lv.dialogue[i], i, "appear"));
        bindBubble(log.lastElementChild as HTMLElement, lv.dialogue[i]);
        (log.lastElementChild as HTMLElement).scrollIntoView({ behavior: "smooth", block: "center" });
        await play(lv.dialogue[i].audio, lv.dialogue[i].ru);
        await sleep(250);
        i++;
      }
      if (i >= lv.dialogue.length) {
        turn.innerHTML = "";
        ctx.ready("Terminer");
        return;
      }
      const line = lv.dialogue[i];
      turn.innerHTML = `<div class="your-turn"><div class="task-kicker">À toi</div><div id="rp-speak"></div>
        <div class="row"><button class="secondary hidden" id="rp-next" type="button">Continuer la scène →</button></div></div>`;
      turn.scrollIntoView({ behavior: "smooth", block: "center" });
      speakBox($("#rp-speak", turn), line, lv.grammar, {
        glossary: lv.glossary,
        onDone: () => $("#rp-next", turn).classList.remove("hidden"),
      });
      $("#rp-next", turn).onclick = () => {
        stop();
        log.insertAdjacentHTML("beforeend", bubble(line, i, "appear"));
        bindBubble(log.lastElementChild as HTMLElement, line);
        turn.innerHTML = "";
        i++;
        advance();
      };
    };
    advance();
  },
};

/* ======================= общие кусочки ======================= */

function choice(ctx: Ctx, isRight: (id: string) => boolean, correctHtml: string) {
  let answered = false;
  $$<HTMLButtonElement>("[data-id]", ctx.body).forEach((b) => {
    b.onclick = () => {
      if (answered) return;
      answered = true;
      const ok = isRight(b.dataset.id!);
      b.classList.add(ok ? "right" : "wrong");
      if (!ok) $$<HTMLButtonElement>("[data-id]", ctx.body).find((x) => isRight(x.dataset.id!))?.classList.add("right");
      ctx.result(ok, correctHtml);
    };
  });
}

function bubble(line: Line, i: number, extra = ""): string {
  const sp = lv.speakers[line.speaker];
  const side = line.speaker === lv.learner ? "right" : "left";
  return `
    <div class="bubble-row ${side} ${extra}" data-line="${i}">
      <div class="avatar" style="background:${sp.color}">${sp.nameFr[0]}</div>
      <div class="bubble">
        <div class="who">${esc(sp.nameFr)}</div>
        <div class="ru">${tokensHtml(line.tokens)}</div>
        <div class="fr">${esc(line.fr)}</div>
        <div class="bubble-actions">
          <button class="icon play" aria-label="Écouter">▶</button>
          <button class="icon slow" aria-label="Lentement">🐢</button>
        </div>
      </div>
    </div>`;
}

function bindBubble(row: HTMLElement, line: Line) {
  bindTokens(row, line.tokens, { glossary: lv.glossary });
  $(".play", row).onclick = () => play(line.audio, line.ru);
  $(".slow", row).onclick = () => play(line.audio, line.ru, 0.7);
}

/** Запись для «Écoute et répète»: моя запись vs модель + распознавание, если включено. */
function recorder(root: HTMLElement, p: Line, onRecorded: () => void) {
  const rec = new Recorder();
  const mic = $<HTMLButtonElement>(".mic", root);
  const txt = $(".mic-txt", root);
  let wav: Blob | null = null;
  $(".mine", root).onclick = () => wav && playBlob(wav);
  mic.onclick = async () => {
    if (!rec.active) {
      stop();
      try {
        await rec.start();
      } catch {
        $(".heard", root).textContent = "Micro indisponible : autorise le micro dans ton navigateur.";
        onRecorded();
        return;
      }
      mic.classList.add("recording");
      txt.textContent = "Je t'écoute… touche pour finir";
      return;
    }
    mic.classList.remove("recording");
    txt.textContent = "Encore une fois";
    const { samples, sampleRate } = await rec.stop();
    wav = toWav(samples, sampleRate);
    $(".mine", root).classList.remove("hidden");
    const heard = $(".heard", root);
    if (progress().settings.vosk) {
      heard.textContent = "Analyse…";
      try {
        const text = await recognize(samples, sampleRate, lv.grammar);
        const ok = normalize(text) === normalize(p.ru);
        heard.innerHTML = ok ? "✅ Bien prononcé !" : `J'ai entendu : <b>${esc(text || "…")}</b>. Écoute le modèle et réessaie.`;
        heard.className = `heard ${ok ? "ok" : "ko"}`;
      } catch {
        heard.textContent = "Compare ta voix au modèle 👂";
      }
    } else {
      heard.textContent = "Compare ta voix au modèle 👂";
    }
    onRecorded();
    await playBlob(wav);
    await sleep(200);
    await play(p.audio, p.ru);
  };
}

/* ======================= конец части / урока ======================= */

async function finishPart(partIdx: number) {
  markActiveToday();
  const last = partIdx === lv.parts.length - 1;
  save((pr) => {
    const cur = pr.levels[lv.id] ?? { done: false };
    cur.parts = Math.max(cur.parts ?? 0, partIdx + 1);
    if (last) {
      cur.done = true;
      cur.doneAt = new Date().toISOString();
    }
    pr.levels[lv.id] = cur;
  });
  if (last) addItems(lv as never);
  const idx = await getIndex();
  const nextLevel = idx.levels.find((l) => l.order === lv.order + 1);
  const learned = new Set<string>();
  for (const st of lv.parts[partIdx].steps) {
    if (st.type === "block") st.phrases.forEach((p) => learned.add(p));
  }
  app.innerHTML = `
    <div class="flow"><main class="card-stack done">
      <section class="card center celebrate">
        <div class="trophy">${last ? "🎉" : "✅"}</div>
        <h2>${last ? "Leçon terminée !" : `Partie ${partIdx + 1} terminée !`}</h2>
        ${last
          ? `<p>Maintenant tu sais :</p><ul class="cando">${lv.cando.map((c) => `<li>✔ ${esc(c)}</li>`).join("")}</ul>
             <p class="muted">Les phrases de cette leçon reviendront dans tes révisions, au bon moment.</p>`
          : `<p>Nouvelles phrases :</p><div class="learned">${[...learned].map((id) => `<button class="learned-item" data-p="${id}">▶ ${ruHtml(P(id))} <small class="muted">${esc(P(id).fr)}</small></button>`).join("")}</div>`}
        <div class="col">
          ${last
            ? nextLevel ? `<button id="go-next" class="primary">Leçon suivante : ${esc(nextLevel.titleFr)}</button>` : ""
            : `<button id="go-part" class="primary">Partie suivante : ${esc(lv.parts[partIdx + 1].titleFr)}</button>`}
          <button id="go-home" class="secondary">Plus tard</button>
        </div>
      </section></main></div>`;
  confetti($(".celebrate", app));
  $$<HTMLButtonElement>(".learned-item", app).forEach((b) => (b.onclick = () => play(P(b.dataset.p!).audio, P(b.dataset.p!).ru)));
  $("#go-home", app).onclick = () => navigate(last ? "" : `level/${lv.id}`);
  document.getElementById("go-part")?.addEventListener("click", () => navigate(`level/${lv.id}/${partIdx + 1}`));
  document.getElementById("go-next")?.addEventListener("click", () => navigate(`level/${nextLevel!.id}`));
}
