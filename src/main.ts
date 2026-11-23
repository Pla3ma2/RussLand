import "./style.css";
import type { Lesson, Line, PuzzleWord, Token } from "./types";
import { renderStressed } from "./stress";
import { play, playBlob, setUseFiles, stop } from "./audio";
import { Recorder, loadVosk, normalize, recognize, toWav, voskAvailable } from "./speech";

const app = document.querySelector<HTMLDivElement>("#app")!;
const STEPS = ["Écoute", "Construis", "Comprends", "Parle"];

let lesson: Lesson;
let step = 0;

const $ = <T extends HTMLElement = HTMLElement>(sel: string, root: ParentNode = app) =>
  root.querySelector<T>(sel)!;
const $$ = <T extends HTMLElement = HTMLElement>(sel: string, root: ParentNode = app) =>
  [...root.querySelectorAll<T>(sel)];
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/* ---------- общие кусочки ---------- */

function tokensHtml(tokens: Token[]): string {
  return tokens
    .map((t, i) =>
      t.w
        ? `<button class="word" data-i="${i}">${renderStressed(t.t, t.s, t.t)}</button>`
        : `<span>${t.t}</span>`,
    )
    .join("");
}

function bindWords(root: HTMLElement, tokens: Token[]) {
  $$<HTMLButtonElement>(".word", root).forEach((b) => {
    b.onclick = (e) => {
      e.stopPropagation();
      const t = tokens[Number(b.dataset.i)];
      b.classList.add("ping");
      setTimeout(() => b.classList.remove("ping"), 400);
      play(t.a!, t.t);
    };
  });
}

function shell(body: string, nextLabel = "Continuer", nextEnabled = true) {
  const progress = STEPS.map(
    (s, i) => `<div class="pstep ${i < step ? "done" : i === step ? "now" : ""}"><span></span>${s}</div>`,
  ).join("");
  app.innerHTML = `
    <header>
      <div class="brand">Russ<b>Land</b> <small>prototype</small></div>
      <div class="progress">${progress}</div>
    </header>
    <main class="card-stack">${body}</main>
    <footer><button id="next" class="primary" ${nextEnabled ? "" : "disabled"}>${nextLabel}</button></footer>`;
  $("#next").onclick = () => {
    stop();
    step++;
    render();
  };
}

const enableNext = () => ($<HTMLButtonElement>("#next").disabled = false);

/* ---------- 1. Слушай ---------- */

function bubble(line: Line, i: number): string {
  const sp = lesson.speakers[line.speaker];
  const side = line.speaker === "luka" ? "right" : "left";
  return `
    <div class="bubble-row ${side}" data-line="${i}">
      <div class="avatar" style="background:${sp.color}">${sp.name[0]}</div>
      <div class="bubble">
        <div class="who">${sp.name}</div>
        <div class="ru">${tokensHtml(line.tokens)}</div>
        <div class="fr">${line.fr}</div>
        <div class="bubble-actions">
          <button class="icon play" title="Écouter">▶</button>
          <button class="icon slow" title="Lentement">🐢</button>
        </div>
      </div>
    </div>`;
}

function renderListen() {
  shell(`
    <section class="card">
      <p class="scene">${lesson.sceneFr}</p>
      <button id="play-all" class="secondary">▶ Écouter tout le dialogue</button>
      <div class="dialogue">${lesson.dialogue.map(bubble).join("")}</div>
      <p class="hint">Touche un mot pour l'entendre. L'accent tonique est marqué : ́</p>
    </section>`);
  lesson.dialogue.forEach((line, i) => {
    const row = $(`[data-line="${i}"]`);
    bindWords(row, line.tokens);
    $(".play", row).onclick = () => play(line.audio, line.ru);
    $(".slow", row).onclick = () => play(line.audio, line.ru, 0.7);
  });
  $("#play-all").onclick = async () => {
    for (let i = 0; i < lesson.dialogue.length; i++) {
      const row = $(`[data-line="${i}"]`);
      row.classList.add("speaking");
      await play(lesson.dialogue[i].audio, lesson.dialogue[i].ru);
      row.classList.remove("speaking");
      await sleep(250);
    }
  };
}

/* ---------- 2. Собери ---------- */

function slotHtml(w: PuzzleWord, morphed: boolean): string {
  const color = lesson.puzzle.caseColor;
  if (!morphed) {
    return `${renderStressed(w.stem, w.stressLemma, w.lemma)}<span class="ending">${renderStressed(
      w.endLemma, w.stressLemma, w.lemma, w.stem.length)}</span>`;
  }
  return `${renderStressed(w.stem, w.stressForm, w.form)}<span class="ending new" style="color:${color};border-color:${color}">${renderStressed(
    w.endForm, w.stressForm, w.form, w.stem.length)}</span>`;
}

function renderBuild() {
  const pz = lesson.puzzle;
  const explored = new Set<string>();
  shell(
    `
    <section class="card">
      <h2>Construis la phrase</h2>
      <p class="hint">Mets chaque mot dans la phrase et regarde bien sa fin.</p>
      <div class="frame">
        <span class="frame-ru">${tokensHtml(pz.before)}<span id="slot" class="slot">…</span>${pz.after}</span>
        <div id="frame-fr" class="fr">${pz.frameFr}</div>
        <div id="note" class="note"></div>
      </div>
      <div class="tiles" id="explore">
        ${pz.words.map((w, i) => `<button class="tile" data-w="${i}">
          <span class="tile-ru">${renderStressed(w.lemma, w.stressLemma, w.lemma)}</span>
          <span class="tile-fr">${w.fr}</span></button>`).join("")}
      </div>
    </section>
    <section class="card hidden" id="task">
      <h2>${pz.task.fr}</h2>
      <div class="frame"><span class="frame-ru">${pz.before.map((t) => t.t).join("")}<span id="slot2" class="slot">…</span>${pz.after}</span></div>
      <div class="tiles" id="task-tiles">
        ${pz.words.map((w, i) => `<button class="tile" data-w="${i}"><span class="tile-ru">${renderStressed(w.lemma, w.stressLemma, w.lemma)}</span></button>`).join("")}
      </div>
    </section>`,
    "Continuer",
    false,
  );
  bindWords($(".frame"), pz.before);
  let busy = false;

  $$<HTMLButtonElement>("#explore .tile").forEach((b) => {
    b.onclick = async () => {
      if (busy) return;
      busy = true;
      const w = pz.words[Number(b.dataset.w)];
      $$("#explore .tile").forEach((t) => t.classList.remove("picked"));
      b.classList.add("picked");
      const slot = $("#slot");
      const note = $("#note");
      note.textContent = "";
      slot.className = "slot filled";
      slot.innerHTML = slotHtml(w, false);
      play(w.audioLemma, w.lemma);
      await sleep(900);
      if (w.changed) {
        $(".ending", slot).classList.add("leaving");
        await sleep(350);
        slot.innerHTML = slotHtml(w, true);
        note.innerHTML = `<b>${w.lemma}</b> → <b style="color:${pz.caseColor}">${w.form}</b>`;
      } else {
        slot.classList.add("same");
        note.innerHTML = `<b>${w.lemma}</b> ne change pas`;
      }
      $("#frame-fr").textContent = w.phraseFr;
      await play(w.audioPhrase, `${pz.before.map((t) => t.t).join("")}${w.form}${pz.after}`);
      explored.add(w.lemma);
      busy = false;
      if (explored.size === pz.words.length) {
        $("#task").classList.remove("hidden");
        $("#task").scrollIntoView({ behavior: "smooth", block: "center" });
      }
    };
  });

  $$<HTMLButtonElement>("#task-tiles .tile").forEach((b) => {
    b.onclick = async () => {
      const w = pz.words[Number(b.dataset.w)];
      if (w.lemma !== pz.task.answer) {
        b.classList.remove("shake");
        void b.offsetWidth;
        b.classList.add("shake", "wrong");
        return;
      }
      b.classList.add("right");
      const slot = $("#slot2");
      slot.className = "slot filled";
      slot.innerHTML = slotHtml(w, true);
      await play(w.audioPhrase, w.form);
      enableNext();
      $<HTMLButtonElement>("#next").textContent = "Bravo ! Continuer";
    };
  });
}

/* ---------- 3. Пойми ---------- */

function renderInsight() {
  const pz = lesson.puzzle;
  const masha = lesson.speakers.barista;
  const examples = pz.words
    .map((w) =>
      w.changed
        ? `<div class="ex">${w.stem}<span class="ending">${w.endLemma}</span> → ${w.stem}<span class="ending new" style="color:${pz.caseColor};border-color:${pz.caseColor}">${w.endForm}</span></div>`
        : `<div class="ex">${w.lemma} → ${w.form} <small>(pareil)</small></div>`,
    )
    .join("");
  shell(`
    <section class="card insight">
      <div class="bubble-row left">
        <div class="avatar" style="background:${masha.color}">${masha.name[0]}</div>
        <div class="bubble big">
          <div class="who">${masha.name} t'explique</div>
          ${pz.insightFr.map((p) => `<p>${p}</p>`).join("")}
        </div>
      </div>
      <div class="examples">${examples}</div>
    </section>`, "J'ai compris");
}

/* ---------- 4. Скажи ---------- */

function renderSpeak() {
  const sp = lesson.speak;
  shell(
    `
    <section class="card">
      <h2>À toi de parler</h2>
      <p class="prompt">Dis en russe : <b>« ${sp.line.fr} »</b></p>
      <button id="rec" class="mic">🎙<span>Appuie et parle</span></button>
      <div id="answer" class="answer hidden">
        <div class="ru big-ru">${tokensHtml(sp.line.tokens)}</div>
        <div id="heard" class="heard"></div>
        <div class="row">
          <button id="mine" class="secondary" disabled>▶ Ma voix</button>
          <button id="model" class="secondary">▶ Le modèle</button>
        </div>
      </div>
      <button id="skip" class="link">Je ne peux pas parler maintenant</button>
      <div id="vosk" class="vosk"></div>
    </section>`,
    "Terminer",
    false,
  );
  bindWords($("#answer"), sp.line.tokens);
  const rec = new Recorder();
  let lastWav: Blob | null = null;
  let voskOn = false;

  const reveal = () => {
    $("#answer").classList.remove("hidden");
    enableNext();
  };
  $("#model").onclick = () => play(sp.line.audio, sp.line.ru);
  $("#mine").onclick = () => lastWav && playBlob(lastWav);
  $("#skip").onclick = () => {
    reveal();
    play(sp.line.audio, sp.line.ru);
  };

  const btn = $<HTMLButtonElement>("#rec");
  btn.onclick = async () => {
    if (!rec.active) {
      stop();
      try {
        await rec.start();
      } catch {
        $("#heard").textContent = "Micro indisponible. Autorise le micro ou utilise « Je ne peux pas parler ».";
        reveal();
        return;
      }
      btn.classList.add("recording");
      $("span", btn).textContent = "Je t'écoute… touche pour finir";
      return;
    }
    btn.classList.remove("recording");
    $("span", btn).textContent = "Réessayer";
    const { samples, sampleRate } = await rec.stop();
    lastWav = toWav(samples, sampleRate);
    $<HTMLButtonElement>("#mine").disabled = false;
    reveal();
    const heard = $("#heard");
    if (voskOn) {
      heard.textContent = "Analyse…";
      try {
        const text = await recognize(samples, sampleRate, sp.grammar);
        const ok = normalize(text) === normalize(sp.line.ru);
        heard.innerHTML = text
          ? `J'ai entendu : <b>${text}</b> ${ok ? "✅ Parfait !" : "— presque, écoute le modèle et réessaie."}`
          : "Je n'ai rien compris — parle un peu plus fort et réessaie.";
        heard.className = `heard ${ok ? "ok" : "ko"}`;
      } catch {
        heard.textContent = "La reconnaissance a échoué. Compare ta voix au modèle.";
      }
    } else {
      heard.textContent = "Compare ta voix au modèle 👂";
    }
    await play(sp.line.audio, sp.line.ru);
  };

  voskAvailable().then((ok) => {
    const box = $("#vosk");
    if (!ok) {
      box.innerHTML = `<small>Mode auto-évaluation : la reconnaissance vocale n'est pas installée sur ce serveur.</small>`;
      return;
    }
    box.innerHTML = `<button id="vosk-on" class="link">Activer la reconnaissance vocale hors ligne (≈45 Mo, une seule fois)</button>`;
    $("#vosk-on").onclick = async () => {
      box.innerHTML = `<small>⏳ Téléchargement du modèle…</small>`;
      try {
        await loadVosk();
        voskOn = true;
        box.innerHTML = `<small>✅ Reconnaissance vocale activée (fonctionne hors ligne).</small>`;
      } catch {
        box.innerHTML = `<small>❌ Impossible de charger le modèle sur cet appareil.</small>`;
      }
    };
  });
}

/* ---------- финал ---------- */

function renderDone() {
  app.innerHTML = `
    <main class="card-stack done">
      <section class="card center">
        <div class="trophy">🎉</div>
        <h2>Bravo !</h2>
        <p>Maintenant tu sais :</p>
        <ul class="cando">
          <li>✔ dire bonjour et merci</li>
          <li>✔ demander quelque chose au café</li>
          <li>✔ reconnaître la fin bleue <span style="color:${lesson.puzzle.caseColor}">-у</span></li>
        </ul>
        <button id="again" class="primary">Recommencer</button>
      </section>
    </main>`;
  $("#again").onclick = () => {
    step = 0;
    render();
  };
}

function render() {
  window.scrollTo({ top: 0 });
  [renderListen, renderBuild, renderInsight, renderSpeak, renderDone][step]();
}

async function boot() {
  const index: { id: string }[] = await fetch("./content/index.json").then((r) => r.json());
  lesson = await fetch(`./content/${index[0].id}.json`).then((r) => r.json());
  setUseFiles(lesson.hasAudio);
  render();
}

boot().catch((e) => {
  app.innerHTML = `<p class="error">Erreur de chargement : ${e}</p>`;
});
