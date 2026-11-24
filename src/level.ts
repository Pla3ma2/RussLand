/** Урок основного режима: Écoute → Construis → Comprends → Parle → Joue la scène → Bilan. */
import type { Explore, ExploreWord, Level, Line, Task } from "./types";
import { getIndex, getLevel } from "./content";
import { renderStressed } from "./stress";
import { play, stop } from "./audio";
import { $, $$, ABC_BTN, bindAbc, bindTokens, confetti, esc, shuffle, sleep, speakBox, tokensHtml, voskToggle } from "./ui";
import { markActiveToday, progress, save } from "./state";
import { addItems } from "./srs";
import { navigate } from "./router";

const STEPS = ["Écoute", "Construis", "Comprends", "Parle", "Joue"];

let lv: Level;
let step = 0;
let app: HTMLElement;

export async function renderLevel(root: HTMLElement, id: string) {
  app = root;
  lv = await getLevel(id);
  await getIndex();
  step = 0;
  renderStep();
}

function frame(body: string, nextLabel = "Continuer", nextEnabled = true) {
  const bar = STEPS.map(
    (s, i) => `<div class="pstep ${i < step ? "done" : i === step ? "now" : ""}"><span></span>${s}</div>`,
  ).join("");
  app.innerHTML = `
    <div class="flow">
      <header class="flow-head">
        <button class="close" aria-label="Fermer">✕</button>
        <div class="flow-title">${lv.emoji} ${esc(lv.titleFr)}</div>
        ${ABC_BTN}
      </header>
      <div class="progress">${bar}</div>
      <main class="card-stack">${body}</main>
      <footer class="flow-foot"><button id="next" class="primary" ${nextEnabled ? "" : "disabled"}>${nextLabel}</button></footer>
    </div>`;
  $(".close", app).onclick = () => {
    stop();
    navigate("");
  };
  bindAbc(app);
  $("#next", app).onclick = () => {
    stop();
    step++;
    renderStep();
  };
}

const enableNext = (label?: string) => {
  const b = $<HTMLButtonElement>("#next", app);
  b.disabled = false;
  if (label) b.textContent = label;
};

function renderStep() {
  window.scrollTo({ top: 0 });
  [renderListen, renderBuild, renderInsight, renderSpeak, renderRoleplay, renderDone][step]();
}

const speakerName = (id: string) => lv.speakers[id]?.nameFr ?? id;

/* ---------- 1. Écoute ---------- */

function bubble(line: Line, i: number, extraClass = ""): string {
  const sp = lv.speakers[line.speaker];
  const side = line.speaker === lv.learner ? "right" : "left";
  return `
    <div class="bubble-row ${side} ${extraClass}" data-line="${i}">
      <div class="avatar" style="background:${sp.color}">${sp.nameFr[0]}</div>
      <div class="bubble">
        <div class="who">${esc(sp.nameFr)}</div>
        <div class="ru">${tokensHtml(line.tokens)}</div>
        <div class="fr">${esc(line.fr)}</div>
        <div class="bubble-actions">
          <button class="icon play" title="Écouter" aria-label="Écouter">▶</button>
          <button class="icon slow" title="Lentement" aria-label="Lentement">🐢</button>
        </div>
      </div>
    </div>`;
}

function bindBubble(row: HTMLElement, line: Line) {
  bindTokens(row, line.tokens, { glossary: lv.glossary });
  $(".play", row).onclick = () => play(line.audio, line.ru);
  $(".slow", row).onclick = () => play(line.audio, line.ru, 0.7);
}

function renderListen() {
  frame(`
    <section class="card">
      <p class="scene">${esc(lv.sceneFr)}</p>
      <button id="play-all" class="secondary">▶ Écouter tout le dialogue</button>
      <label class="toggle"><input type="checkbox" id="hide-fr"> Cacher la traduction</label>
      <div class="dialogue">${lv.dialogue.map((l, i) => bubble(l, i)).join("")}</div>
      <p class="hint">Touche un mot : tu l'entends et tu vois comment il se lit. L'accent tonique est en rouge.</p>
    </section>`);
  lv.dialogue.forEach((line, i) => bindBubble($(`[data-line="${i}"]`, app), line));
  $<HTMLInputElement>("#hide-fr", app).onchange = (e) =>
    $(".dialogue", app).classList.toggle("no-fr", (e.target as HTMLInputElement).checked);
  let playing = false;
  $("#play-all", app).onclick = async () => {
    if (playing) return;
    playing = true;
    for (let i = 0; i < lv.dialogue.length; i++) {
      const row = $(`[data-line="${i}"]`, app);
      if (!row) break;
      row.classList.add("speaking");
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      await play(lv.dialogue[i].audio, lv.dialogue[i].ru);
      row.classList.remove("speaking");
      await sleep(300);
    }
    playing = false;
  };
}

/* ---------- 2. Construis ---------- */

export function morphHtml(ex: Explore, w: ExploreWord, done: boolean): string {
  const m = w.morph;
  if (!done || !m.changed) {
    return `${renderStressed(m.stem, m.stressFrom, m.from)}<span class="ending">${renderStressed(m.endFrom, m.stressFrom, m.from, m.stem.length)}</span>`;
  }
  return `${renderStressed(m.stem, m.stressTo, m.to)}<span class="ending new" style="color:${ex.color};border-color:${ex.color}">${renderStressed(m.endTo, m.stressTo, m.to, m.stem.length)}</span>`;
}

/** Рамка фразы со слотом. Возвращает функцию, которая «ставит» слово в слот. */
export function frameBox(host: HTMLElement, ex: Explore, interactiveTokens = true) {
  const tokensOf = (toks: typeof ex.before) => (toks.length ? tokensHtml(toks) : "");
  const after = ex.after.map((t) => ({ ...t, t: t.w ? t.t : t.t.replace(/^\s+/, ex.type === "person" ? " " : "") }));
  if (ex.type === "person") {
    host.innerHTML = `<span class="frame-ru"><span class="slot">…</span> <span class="verb">${renderStressed(ex.verb!, null, ex.verb!)}</span>${tokensOf(after)}</span>`;
  } else {
    host.innerHTML = `<span class="frame-ru">${tokensOf(ex.before)}<span class="slot">…</span>${tokensOf(after)}</span>`;
  }
  if (interactiveTokens) {
    const ruSpan = $(".frame-ru", host);
    // before и after — разные массивы токенов, поэтому привязываем по очереди
    const words = $$<HTMLButtonElement>(".word", ruSpan);
    const all = [...(ex.type === "person" ? [] : ex.before), ...after];
    let k = 0;
    all.forEach((t) => {
      if (!t.w) return;
      const b = words[k++];
      if (!b) return;
      b.onclick = () => t.a && play(t.a, t.t);
    });
  }
  const slot = $(".slot", host);
  return {
    async put(w: ExploreWord, animate: boolean) {
      slot.className = "slot filled";
      if (ex.type === "person") {
        slot.innerHTML = renderStressed(w.tile, w.tileStress, w.tile);
        const verb = $(".verb", host);
        verb.innerHTML = morphHtml(ex, w, false);
        if (animate) {
          await sleep(700);
          $(".ending", verb).classList.add("leaving");
          await sleep(350);
        }
        verb.innerHTML = morphHtml(ex, w, true);
      } else {
        slot.innerHTML = morphHtml(ex, w, false);
        if (animate && w.morph.changed) {
          await sleep(800);
          $(".ending", slot).classList.add("leaving");
          await sleep(350);
        }
        slot.innerHTML = morphHtml(ex, w, true);
        if (!w.morph.changed && ex.type === "case") slot.classList.add("same");
      }
    },
  };
}

function noteFor(ex: Explore, w: ExploreWord): string {
  const m = w.morph;
  if (ex.type === "plain") return "";
  if (!m.changed) return `<b>${esc(m.from)}</b> ne change pas`;
  return `<b>${esc(m.from)}</b> → <b style="color:${ex.color}">${esc(m.to)}</b>`;
}

function renderBuild() {
  const ex = lv.explore;
  frame(`
    <section class="card">
      <h2>Construis la phrase</h2>
      <p class="hint">${ex.type === "plain" ? "Mets chaque mot dans la phrase et écoute." : "Mets chaque mot dans la phrase et regarde bien la fin du mot."}</p>
      <div class="frame">
        <div class="frame-host"></div>
        <div class="fr frame-fr">${esc(ex.frameFr)}</div>
        <div class="note"></div>
      </div>
      <div class="tiles explore-tiles">
        ${ex.words.map((w, i) => `<button class="tile" data-w="${i}">
          <span class="tile-ru">${renderStressed(w.tile, w.tileStress, w.tile)}</span>
          <span class="tile-fr">${esc(w.fr)}</span></button>`).join("")}
      </div>
    </section>
    <div id="tasks"></div>`, "Continuer", false);

  const box = frameBox($(".frame-host", app), ex);
  const explored = new Set<number>();
  let busy = false;
  $$<HTMLButtonElement>(".explore-tiles .tile", app).forEach((b) => {
    b.onclick = async () => {
      if (busy) return;
      busy = true;
      const idx = Number(b.dataset.w);
      const w = ex.words[idx];
      $$(".explore-tiles .tile", app).forEach((t) => t.classList.remove("picked"));
      b.classList.add("picked");
      $(".note", app).innerHTML = "";
      play(w.audioTile, w.tile);
      await box.put(w, true);
      $(".note", app).innerHTML = noteFor(ex, w);
      $(".frame-fr", app).textContent = w.phraseFr;
      await play(w.audioPhrase, w.phrase);
      explored.add(idx);
      b.classList.add("seen");
      busy = false;
      if (explored.size === ex.words.length && !$("#tasks", app).hasChildNodes()) runTasks(0);
    };
  });
}

function runTasks(i: number) {
  const host = $("#tasks", app);
  if (i >= lv.tasks.length) {
    enableNext("Bravo ! Continuer");
    return;
  }
  const card = document.createElement("section");
  card.className = "card task-card";
  host.appendChild(card);
  const task = lv.tasks[i];
  const next = () => runTasks(i + 1);
  if (task.type === "pick") pickTask(card, task, next);
  else orderTask(card, task, next);
  setTimeout(() => card.scrollIntoView({ behavior: "smooth", block: "center" }), 50);
}

function pickTask(card: HTMLElement, task: Extract<Task, { type: "pick" }>, next: () => void) {
  const ex = lv.explore;
  card.innerHTML = `
    <div class="task-kicker">Défi</div>
    <h2>${esc(task.fr)}</h2>
    <div class="frame"><div class="frame-host"></div></div>
    <div class="tiles">${shuffle(ex.words.map((w, i) => ({ w, i }))).map(({ w, i }) =>
      `<button class="tile" data-w="${i}"><span class="tile-ru">${renderStressed(w.tile, w.tileStress, w.tile)}</span></button>`).join("")}</div>`;
  const box = frameBox($(".frame-host", card), ex, false);
  let solved = false;
  $$<HTMLButtonElement>(".tile", card).forEach((b) => {
    b.onclick = async () => {
      if (solved) return;
      const w = ex.words[Number(b.dataset.w)];
      if (w.tile !== task.answer) {
        b.classList.remove("shake");
        void b.offsetWidth;
        b.classList.add("shake", "wrong");
        return;
      }
      solved = true;
      b.classList.add("right");
      await box.put(w, false);
      await play(w.audioPhrase, w.phrase);
      next();
    };
  });
}

function orderTask(card: HTMLElement, task: Extract<Task, { type: "order" }>, next: () => void) {
  const words = task.line.tokens.filter((t) => t.w);
  const target = words.map((t) => t.t.toLowerCase());
  const display = (t: string, i: number) => (i === 0 && !lv.glossary[t.toLowerCase()]?.includes("prénom") ? t.toLowerCase() : t);
  const pool = shuffle(words.map((t, i) => ({ text: display(t.t, i), key: t.t.toLowerCase(), id: i })));
  let answer: typeof pool = [];
  card.innerHTML = `
    <div class="task-kicker">Défi</div>
    <h2>Remets les mots dans l'ordre</h2>
    <p class="fr big-fr">« ${esc(task.line.fr)} »</p>
    <div class="answer-row"></div>
    <div class="tiles pool"></div>
    <div class="row"><button class="link small reset" type="button">Recommencer</button></div>`;
  const render = () => {
    $(".answer-row", card).innerHTML = answer.length
      ? answer.map((p, i) => `<button class="tile small" data-a="${i}">${esc(p.text)}</button>`).join("")
      : `<span class="placeholder">Touche les mots dans le bon ordre</span>`;
    $(".pool", card).innerHTML = pool
      .filter((p) => !answer.includes(p))
      .map((p) => `<button class="tile small" data-p="${p.id}">${esc(p.text)}</button>`)
      .join("");
    $$<HTMLButtonElement>("[data-p]", card).forEach((b) => {
      b.onclick = () => {
        const p = pool.find((x) => x.id === Number(b.dataset.p))!;
        answer.push(p);
        const tok = words[p.id];
        if (tok.a) play(tok.a, tok.t);
        render();
        if (answer.length === words.length) check();
      };
    });
    $$<HTMLButtonElement>("[data-a]", card).forEach((b) => {
      b.onclick = () => {
        answer.splice(Number(b.dataset.a), 1);
        render();
      };
    });
  };
  const check = async () => {
    const ok = answer.every((p, i) => p.key === target[i]);
    const row = $(".answer-row", card);
    if (!ok) {
      row.classList.remove("shake");
      void row.offsetWidth;
      row.classList.add("shake", "bad");
      return;
    }
    row.classList.remove("bad");
    row.classList.add("good");
    row.innerHTML = `<div class="ru">${tokensHtml(task.line.tokens)}</div>`;
    bindTokens(row, task.line.tokens, { glossary: lv.glossary });
    $(".pool", card).innerHTML = "";
    $(".reset", card).remove();
    await play(task.line.audio, task.line.ru);
    next();
  };
  $(".reset", card).onclick = () => {
    answer = [];
    $(".answer-row", card).classList.remove("bad");
    render();
  };
  render();
}

/* ---------- 3. Comprends ---------- */

function renderInsight() {
  const ex = lv.explore;
  const by = lv.speakers[lv.insight.by];
  const examples = ex.type === "plain"
    ? ex.words.map((w) => `<div class="ex">${esc(w.phrase)}</div>`).join("")
    : ex.words.map((w) => {
      const m = w.morph;
      const pre = ex.type === "person" ? `<span class="muted">${esc(w.tile)}</span> ` : "";
      const to = m.changed
        ? `${esc(m.stem)}<span class="ending new" style="color:${ex.color};border-color:${ex.color}">${esc(m.endTo)}</span>`
        : `${esc(m.to)} <small class="muted">(pareil)</small>`;
      return `<div class="ex">${ex.type === "person" ? "" : `${esc(m.stem)}<span class="ending">${esc(m.endFrom)}</span> → `}${pre}${to}</div>`;
    }).join("");
  frame(`
    <section class="card insight">
      <div class="bubble-row left">
        <div class="avatar" style="background:${by.color}">${by.nameFr[0]}</div>
        <div class="bubble big">
          <div class="who">${esc(by.nameFr)} t'explique</div>
          ${lv.insight.fr.map((p) => `<p>${esc(p)}</p>`).join("")}
        </div>
      </div>
      <div class="examples">${examples}</div>
    </section>`, "J'ai compris");
}

/* ---------- 4. Parle ---------- */

function renderSpeak() {
  frame(`
    <section class="card">
      <h2>À toi de parler</h2>
      <p class="hint">Dis la phrase à voix haute, puis compare-toi au modèle.</p>
      <div class="dots">${lv.speak.map((_, i) => `<span data-d="${i}"></span>`).join("")}</div>
      <div id="speak-host"></div>
      <div class="row"><button id="speak-next" class="secondary hidden" type="button">Phrase suivante →</button></div>
      <div id="vosk" class="vosk"></div>
    </section>`, "Continuer", false);
  voskToggle($("#vosk", app));
  let i = 0;
  const show = () => {
    $$(".dots span", app).forEach((d, k) => d.classList.toggle("on", k <= i));
    $("#speak-next", app).classList.add("hidden");
    speakBox($("#speak-host", app), lv.speak[i], lv.grammar, {
      glossary: lv.glossary,
      onDone: () => {
        if (i < lv.speak.length - 1) $("#speak-next", app).classList.remove("hidden");
        else enableNext();
      },
    });
  };
  $("#speak-next", app).onclick = () => {
    stop();
    i++;
    show();
  };
  show();
}

/* ---------- 5. Joue la scène ---------- */

function renderRoleplay() {
  const me = speakerName(lv.learner);
  frame(`
    <section class="card">
      <h2>Joue la scène</h2>
      <p class="hint">Cette fois, c'est toi ${esc(me)} ! Quand c'est ton tour, dis ta réplique, puis écoute la bonne version.</p>
      <div class="dialogue roleplay"></div>
      <div id="rp-turn"></div>
    </section>`, "Terminer", false);
  const log = $(".roleplay", app);
  const turn = $("#rp-turn", app);
  let i = 0;
  const advance = async () => {
    while (i < lv.dialogue.length && lv.dialogue[i].speaker !== lv.learner) {
      log.insertAdjacentHTML("beforeend", bubble(lv.dialogue[i], i, "appear"));
      const row = log.lastElementChild as HTMLElement;
      bindBubble(row, lv.dialogue[i]);
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      await play(lv.dialogue[i].audio, lv.dialogue[i].ru);
      await sleep(250);
      i++;
    }
    if (i >= lv.dialogue.length) {
      turn.innerHTML = "";
      enableNext();
      return;
    }
    const line = lv.dialogue[i];
    turn.innerHTML = `<div class="your-turn"><div class="task-kicker">À toi</div><div id="rp-speak"></div><div class="row"><button class="secondary hidden" id="rp-next" type="button">Continuer la scène →</button></div></div>`;
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
}

/* ---------- Bilan ---------- */

async function renderDone() {
  const idx = await getIndex();
  save((p) => (p.levels[lv.id] = { done: true, doneAt: new Date().toISOString() }));
  addItems(lv);
  markActiveToday();
  const nextLevel = idx.levels.find((l) => l.order === lv.order + 1);
  const unlockText = lv.unlocks.length
    ? `<p class="muted">🗺️ De nouvelles cases sont débloquées sur ta carte.</p>`
    : "";
  app.innerHTML = `
    <div class="flow">
      <main class="card-stack done">
        <section class="card center celebrate">
          <div class="trophy">🎉</div>
          <h2>Bravo !</h2>
          <p>Maintenant tu sais :</p>
          <ul class="cando">${lv.cando.map((c) => `<li>✔ ${esc(c)}</li>`).join("")}</ul>
          <p class="muted">Les phrases de cette leçon reviendront dans tes révisions, au bon moment.</p>
          ${unlockText}
          <div class="col">
            ${nextLevel ? `<button id="go-next" class="primary">Leçon suivante : ${esc(nextLevel.titleFr)}</button>` : ""}
            <button id="go-home" class="secondary">Retour aux leçons</button>
          </div>
        </section>
      </main>
    </div>`;
  confetti($(".celebrate", app));
  $("#go-home", app).onclick = () => navigate("");
  if (nextLevel) $("#go-next", app).onclick = () => navigate(`level/${nextLevel.id}`);
  void progress;
}
