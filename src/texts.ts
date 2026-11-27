/** «Petites histoires»: короткие тексты-продолжения истории, только из изученных слов. */
import { getIndex, getTexts } from "./content";
import { play, stop } from "./audio";
import { $, $$, ABC_BTN, bindAbc, bindTokens, confetti, esc, shuffle, tokensHtml } from "./ui";
import { markActiveToday, progress, save } from "./state";
import { navigate } from "./router";
import type { ReadText } from "./types";

const isRead = (id: string) => !!progress().reading[`t:${id}`];
const lessonDone = (id: string) => !!progress().levels[id]?.done;

export async function renderTextList(slot: HTMLElement) {
  const [{ texts }, idx] = await Promise.all([getTexts(), getIndex()]);
  const order = (id: string) => idx.levels.find((l) => l.id === id)?.order ?? 0;
  slot.innerHTML = `
    <section class="card">
      <h2>Petites histoires</h2>
      <p class="hint">Des textes courts sur Luka et ses amis, écrits <b>seulement avec les mots que tu connais</b>. Une nouvelle histoire s'ouvre après certaines leçons.</p>
    </section>
    <div class="stage-list">
      ${texts.map((t) => {
        const open = lessonDone(t.after);
        const read = isRead(t.id);
        return `<button class="stage ${read ? "done" : ""} ${open ? "" : "locked"}" data-id="${t.id}" ${open ? "" : "disabled"}>
          <span class="stage-n" style="${open ? `background:${t.color};color:#fff` : ""}">${read ? "✓" : "📄"}</span>
          <span class="stage-body"><b>${esc(t.titleFr)}</b><span class="text-sub">${open ? esc(t.titleRu) : `après la leçon ${order(t.after)}`}</span></span>
          <span class="stage-go">${open ? "›" : "🔒"}</span></button>`;
      }).join("")}
    </div>`;
  $$<HTMLButtonElement>(".stage:not(.locked)", slot).forEach((b) => (b.onclick = () => navigate(`reading/t/${b.dataset.id}`)));
}

export async function renderText(root: HTMLElement, id: string) {
  const { texts } = await getTexts();
  const t = texts.find((x) => x.id === id);
  if (!t || !lessonDone(t.after)) return navigate("reading");
  await getIndex();
  readView(root, t);
}

function frame(root: HTMLElement, t: ReadText, body: string, foot: string) {
  root.innerHTML = `
    <div class="flow">
      <header class="flow-head"><button class="close" aria-label="Fermer">✕</button>
        <div class="flow-title">📄 ${esc(t.titleFr)}</div>${ABC_BTN}</header>
      <main class="card-stack">${body}</main>
      <footer class="flow-foot">${foot}</footer>
    </div>`;
  $(".close", root).onclick = () => {
    stop();
    navigate("reading");
  };
  bindAbc(root);
}

function readView(root: HTMLElement, t: ReadText) {
  frame(root, t, `
    <section class="card">
      <div class="text-head">
        <div class="avatar" style="background:${t.color}">${t.byFr[0]}</div>
        <div><h2 class="text-title">${esc(t.titleRu)}</h2><small class="muted">${esc(t.byFr)}</small></div>
      </div>
      <p class="hint">Lis d'abord tout seul. Touche un mot si tu as un doute, ▶ pour écouter une phrase, 👁 pour la traduction.${t.newWords.length ? ` Les mots <span class="new-w">soulignés</span> sont nouveaux.` : ""}</p>
      <button class="secondary" id="all">▶ Écouter tout le texte</button>
      <div class="read-text">
        ${t.sentences.map((s, i) => `
          <div class="snt" data-i="${i}">
            <button class="icon splay" aria-label="Écouter">▶</button>
            <div class="snt-body"><div class="ru">${tokensHtml(s.tokens)}</div><div class="fr hidden">${esc(s.fr)}</div></div>
            <button class="icon seefr" aria-label="Traduction">👁</button>
          </div>`).join("")}
      </div>
    </section>`, `<button class="primary" id="go">J'ai lu, aux questions !</button>`);
  const nw = new Set(t.newWords);
  $$<HTMLElement>(".snt", root).forEach((el) => {
    const s = t.sentences[+el.dataset.i!];
    bindTokens(el, s.tokens, { glossary: t.glossary, translit: true });
    $$<HTMLElement>(".word", el).forEach((w) => {
      const tok = s.tokens[+w.dataset.i!];
      if (tok && nw.has(tok.t.toLowerCase().replace(/ё/g, "е"))) w.classList.add("new-w");
    });
    $(".splay", el).onclick = async () => {
      $$(".snt.reading", root).forEach((x) => x.classList.remove("reading"));
      el.classList.add("reading");
      await play(s.audio, s.ru);
      el.classList.remove("reading");
    };
    $(".seefr", el).onclick = () => $(".fr", el).classList.toggle("hidden");
  });
  let playingAll = false;
  $("#all", root).onclick = async () => {
    if (playingAll) {
      playingAll = false;
      stop();
      return;
    }
    playingAll = true;
    for (const el of $$<HTMLElement>(".snt", root)) {
      if (!playingAll || !el.isConnected) break;
      el.classList.add("reading");
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      await play(t.sentences[+el.dataset.i!].audio, t.sentences[+el.dataset.i!].ru);
      el.classList.remove("reading");
    }
    playingAll = false;
  };
  $("#go", root).onclick = () => {
    stop();
    quiz(root, t, 0, 0);
  };
}

function quiz(root: HTMLElement, t: ReadText, k: number, right: number) {
  if (k >= t.questions.length) return finish(root, t, right);
  const q = t.questions[k];
  const opts = shuffle(q.options.map((o, i) => ({ o, ok: i === 0 })));
  frame(root, t, `
    <section class="card">
      <div class="task-kicker">Question ${k + 1}/${t.questions.length}</div>
      <h2>${esc(q.q)}</h2>
      <div class="tiles col-tiles">${opts.map((x, i) => `<button class="tile wide" data-i="${i}">${esc(x.o)}</button>`).join("")}</div>
      <div id="fbslot"></div>
    </section>
    <button class="link small center" id="back">↩ Relire le texte</button>`, `<button class="primary hidden" id="next">Continuer</button>`);
  $("#back", root).onclick = () => readView(root, t);
  let done = false;
  $$<HTMLButtonElement>(".tile[data-i]", root).forEach((b) => {
    b.onclick = () => {
      if (done) return;
      done = true;
      const ok = opts[+b.dataset.i!].ok;
      b.classList.add(ok ? "right" : "wrong");
      if (!ok) $$<HTMLButtonElement>(".tile[data-i]", root).find((x) => opts[+x.dataset.i!].ok)?.classList.add("right");
      $("#fbslot", root).innerHTML = `<div class="fb ${ok ? "good" : "bad"}"><b>${ok ? "Bravo !" : "Pas tout à fait."}</b></div>`;
      const next = $("#next", root);
      next.classList.remove("hidden");
      next.onclick = () => quiz(root, t, k + 1, right + (ok ? 1 : 0));
    };
  });
}

function finish(root: HTMLElement, t: ReadText, right: number) {
  markActiveToday();
  save((p) => (p.reading[`t:${t.id}`] = true));
  frame(root, t, `
    <section class="card center">
      <div class="trophy">📖</div>
      <h2>Tu as lu tout un texte en russe !</h2>
      <p>${right} bonne${right > 1 ? "s" : ""} réponse${right > 1 ? "s" : ""} sur ${t.questions.length}.</p>
    </section>`, `<button class="primary" id="out">Retour à la lecture</button>`);
  confetti(root);
  $("#out", root).onclick = () => navigate("reading");
}
