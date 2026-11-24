/** Режим «Lecture»: буквы по очереди → слоги → слова с переводом. Буквы звучат как звуки. */
import type { Alphabet, ReadingStage } from "./types";
import { getAlphabet, getReading } from "./content";
import { play, stop } from "./audio";
import { renderStressed } from "./stress";
import { $, $$, confetti, esc, shuffle, sleep } from "./ui";
import { markActiveToday, progress, save } from "./state";
import { navigate } from "./router";

let abc: Alphabet;
const letterOf = (ch: string) => abc.letters.find((L) => L.l === ch.toUpperCase());

/** Слово/слог по буквам: каждая буква — кнопка со своим звуком. */
function spelled(text: string, stress: number | null = null): string {
  return [...text]
    .map((ch, i) => {
      const mark = stress === i && /[аеиоуыэюя]/i.test(ch) && countV(text) > 1;
      return `<button class="ltr ${mark ? "stressed-l" : ""}" data-ch="${esc(ch)}">${esc(ch)}</button>`;
    })
    .join("");
}
const countV = (s: string) => [...s].filter((c) => /[аеёиоуыэюя]/i.test(c)).length;

function bindLetters(root: HTMLElement) {
  $$<HTMLButtonElement>(".ltr", root).forEach((b) => {
    b.onclick = (e) => {
      e.stopPropagation();
      const L = letterOf(b.dataset.ch!);
      $$(".ltr.lit", root).forEach((x) => x.classList.remove("lit"));
      b.classList.add("lit");
      setTimeout(() => b.classList.remove("lit"), 700);
      if (L) play(L.audio, L.l.toLowerCase());
    };
  });
}

/** Подсветка «бегущего человечка»: буквы загораются по очереди, пока звучит слово. */
async function sweep(el: HTMLElement, audio: string, text: string) {
  const letters = $$(".ltr", el);
  const p = play(audio, text);
  for (const l of letters) {
    l.classList.add("lit");
    await sleep(Math.max(90, 420 / letters.length));
  }
  await p;
  letters.forEach((l) => l.classList.remove("lit"));
}

/* ---------- список ступеней ---------- */

export async function renderReadingHome(root: HTMLElement) {
  const [r] = await Promise.all([getReading(), getAlphabet().then((a) => (abc = a))]);
  const done = progress().reading;
  let unlocked = true;
  root.querySelector("#page")!.innerHTML = `
    <section class="card">
      <h2>Apprendre à lire</h2>
      <p class="hint">Les lettres une par une, puis les syllabes, puis de vrais mots. Chaque lettre se dit comme <b>elle sonne</b> : « В » se dit « v », pas « vé ».</p>
    </section>
    <div class="stage-list">
      ${r.stages.map((st, i) => {
        const isDone = !!done[st.id];
        const open = unlocked;
        unlocked = unlocked && isDone;
        return `<button class="stage ${isDone ? "done" : ""} ${open ? "" : "locked"}" data-id="${st.id}" ${open ? "" : "disabled"}>
          <span class="stage-n">${isDone ? "✓" : i + 1}</span>
          <span class="stage-body"><b>${esc(st.titleFr)}</b><span class="stage-letters">${st.letters.join(" ")}</span></span>
          <span class="stage-go">${open ? "›" : "🔒"}</span></button>`;
      }).join("")}
    </div>`;
  $$<HTMLButtonElement>(".stage:not(.locked)", root).forEach((b) => (b.onclick = () => navigate(`reading/${b.dataset.id}`)));
}

/* ---------- одна ступень ---------- */

const PARTS = ["Lettres", "Syllabes", "Écoute", "Mots", "Quiz"];

export async function renderStage(root: HTMLElement, id: string) {
  const [r] = await Promise.all([getReading(), getAlphabet().then((a) => (abc = a))]);
  const st = r.stages.find((s) => s.id === id);
  if (!st) return navigate("reading");
  const known = new Set<string>();
  for (const s of r.stages) {
    s.letters.forEach((l) => known.add(l));
    if (s.id === id) break;
  }
  let part = 0;

  const frame = (body: string, label = "Continuer", enabled = true) => {
    root.innerHTML = `
      <div class="flow">
        <header class="flow-head"><button class="close" aria-label="Fermer">✕</button>
          <div class="flow-title">📖 ${esc(st.titleFr)}</div>
          <button class="abc-btn small" aria-label="Alphabet">АБВ</button></header>
        <div class="progress">${PARTS.map((p, i) => `<div class="pstep ${i < part ? "done" : i === part ? "now" : ""}"><span></span>${p}</div>`).join("")}</div>
        <main class="card-stack">${body}</main>
        <footer class="flow-foot"><button id="next" class="primary" ${enabled ? "" : "disabled"}>${label}</button></footer>
      </div>`;
    $(".close", root).onclick = () => {
      stop();
      navigate("reading");
    };
    $(".abc-btn", root).onclick = () => import("./alphabet").then((m) => m.openAlphabet());
    $("#next", root).onclick = () => {
      stop();
      part++;
      show();
    };
  };
  const enable = () => ($<HTMLButtonElement>("#next", root).disabled = false);

  const show = () => {
    window.scrollTo({ top: 0 });
    [lettersPart, syllablesPart, findPart, wordsPart, quizPart, donePart][part]();
  };

  /* 1. новые буквы */
  function lettersPart() {
    frame(`
      <section class="card">
        ${st!.tipFr.map((t) => `<p class="tip">${esc(t)}</p>`).join("")}
      </section>
      ${st!.letters.map((l) => {
        const L = letterOf(l)!;
        const g = abc.groups[L.group];
        return `<section class="card letter-card" data-l="${l}">
          <div class="letter-big" style="color:${g.color}">${l}<span>${l.toLowerCase()}</span></div>
          <div class="letter-info">
            <div class="abc-group" style="color:${g.color}">${esc(g.fr)}</div>
            <p>${esc(L.tipFr)}</p>
            <div class="row left"><button class="secondary snd" type="button">🔊 Écouter le son</button></div>
          </div>
        </section>`;
      }).join("")}`, "J'ai écouté toutes les lettres", false);
    const heard = new Set<string>();
    $$<HTMLElement>(".letter-card", root).forEach((c) => {
      const L = letterOf(c.dataset.l!)!;
      const go = () => {
        play(L.audio, L.l.toLowerCase());
        heard.add(L.l);
        c.classList.add("heard");
        if (heard.size === st!.letters.length) enable();
      };
      $(".snd", c).onclick = go;
      $(".letter-big", c).onclick = go;
    });
  }

  /* 2. слоги (и пары твёрдый/мягкий) */
  function syllablesPart() {
    const hasSyl = st!.syllables.length > 0;
    frame(`
      ${st!.pairs.length ? `<section class="card">
        <h2>Écoute la différence</h2>
        <div class="pairs">${st!.pairs.map((pair, pi) => `<div class="pair">${pair.map((c, ci) =>
          `<div class="read-item" data-p="${pi}-${ci}"><div class="spelled">${spelled(c.t)}</div><button class="icon play" aria-label="Écouter">▶</button></div>`).join('<span class="vs">/</span>')}</div>`).join("")}</div>
      </section>` : ""}
      ${hasSyl ? `<section class="card">
        <h2>Lis les syllabes</h2>
        <p class="hint">Essaie de lire chaque syllabe à voix haute, puis touche ▶ pour vérifier. Touche une lettre pour entendre son son.</p>
        <div class="syl-grid">${st!.syllables.map((s, i) =>
          `<div class="read-item" data-s="${i}"><div class="spelled">${spelled(s.t)}</div><button class="icon play" aria-label="Écouter">▶</button></div>`).join("")}</div>
      </section>` : ""}`);
    $$<HTMLElement>("[data-s]", root).forEach((el) => {
      const s = st!.syllables[Number(el.dataset.s)];
      bindLetters(el);
      $(".play", el).onclick = () => sweep(el, s.audio, s.t);
    });
    $$<HTMLElement>("[data-p]", root).forEach((el) => {
      const [pi, ci] = el.dataset.p!.split("-").map(Number);
      const c = st!.pairs[pi][ci];
      bindLetters(el);
      $(".play", el).onclick = () => sweep(el, c.audio, c.t);
    });
  }

  /* 3. найди букву на слух */
  function findPart() {
    const pool = [...known];
    const rounds = shuffle(st!.letters).concat(shuffle(st!.letters)).slice(0, Math.max(4, st!.letters.length));
    let k = 0;
    frame(`<section class="card center">
      <h2>Quelle lettre entends-tu ?</h2>
      <div class="dots">${rounds.map((_, i) => `<span data-d="${i}"></span>`).join("")}</div>
      <button class="mic small-mic" id="again" type="button">🔊</button>
      <div class="tiles" id="choices"></div>
      <div class="feedback"></div>
    </section>`, "Continuer", false);
    const round = () => {
      if (k >= rounds.length) {
        $(".feedback", root).textContent = "Parfait ! 👏";
        enable();
        return;
      }
      $$(".dots span", root).forEach((d, i) => d.classList.toggle("on", i < k));
      const target = rounds[k];
      const opts = shuffle([target, ...shuffle(pool.filter((l) => l !== target)).slice(0, 3)]);
      const L = letterOf(target)!;
      $("#choices", root).innerHTML = opts.map((l) => `<button class="tile letter-tile" data-l="${l}">${l}${l.toLowerCase()}</button>`).join("");
      $(".feedback", root).textContent = "";
      play(L.audio, L.l.toLowerCase());
      $("#again", root).onclick = () => play(L.audio, L.l.toLowerCase());
      let wrong = false;
      $$<HTMLButtonElement>("#choices .tile", root).forEach((b) => {
        b.onclick = async () => {
          if (b.dataset.l === target) {
            b.classList.add("right");
            $(".feedback", root).textContent = wrong ? "Voilà !" : "Bravo !";
            await sleep(600);
            k++;
            round();
          } else {
            wrong = true;
            b.classList.add("wrong", "shake");
            const W = letterOf(b.dataset.l!);
            $(".feedback", root).textContent = `Non, ça c'est « ${b.dataset.l} ». Réécoute !`;
            if (W) play(W.audio, W.l.toLowerCase());
          }
        };
      });
    };
    round();
  }

  /* 4. слова с переводом */
  function wordsPart() {
    frame(`<section class="card">
      <h2>Lis les mots</h2>
      <p class="hint">Lis d'abord tout seul, puis touche ▶. Les lettres s'allument une à une, comme si on glissait de l'une à l'autre.</p>
      <div class="word-list">${st!.words.map((w, i) => `
        <div class="read-item word-item" data-w="${i}">
          <div class="spelled big">${spelled(w.t, w.s)}</div>
          <button class="icon play" aria-label="Écouter">▶</button>
          <div class="fr">${esc(w.fr)}</div>
        </div>`).join("")}</div>
    </section>`);
    $$<HTMLElement>("[data-w]", root).forEach((el) => {
      const w = st!.words[Number(el.dataset.w)];
      bindLetters(el);
      $(".play", el).onclick = () => sweep(el, w.audio, w.t);
    });
  }

  /* 5. какое слово ты слышишь? */
  function quizPart() {
    const words = st!.words.length >= 3 ? st!.words : [...st!.words, ...st!.syllables.map((s) => ({ t: s.t, s: null, fr: "", audio: s.audio }))];
    const rounds = shuffle(words).slice(0, Math.min(4, words.length));
    let k = 0;
    frame(`<section class="card center">
      <h2>Quel mot entends-tu ?</h2>
      <div class="dots">${rounds.map((_, i) => `<span data-d="${i}"></span>`).join("")}</div>
      <button class="mic small-mic" id="again" type="button">🔊</button>
      <div class="col" id="choices"></div>
      <div class="feedback"></div>
    </section>`, "Continuer", false);
    const round = () => {
      if (k >= rounds.length) {
        $(".feedback", root).textContent = "Tu sais lire ces mots ! 🎉";
        enable();
        return;
      }
      $$(".dots span", root).forEach((d, i) => d.classList.toggle("on", i < k));
      const target = rounds[k];
      const opts = shuffle([target, ...shuffle(words.filter((w) => w.t !== target.t)).slice(0, 2)]);
      $("#choices", root).innerHTML = opts.map((w) => `<button class="tile wide ru-choice" data-t="${esc(w.t)}">${renderStressed(w.t, w.s, w.t)}</button>`).join("");
      $(".feedback", root).textContent = "";
      play(target.audio, target.t);
      $("#again", root).onclick = () => play(target.audio, target.t);
      $$<HTMLButtonElement>("#choices .tile", root).forEach((b) => {
        b.onclick = async () => {
          if (b.dataset.t === target.t) {
            b.classList.add("right");
            $(".feedback", root).textContent = target.fr ? `Oui ! « ${target.t} » = ${target.fr}` : "Oui !";
            await sleep(1100);
            k++;
            round();
          } else {
            b.classList.add("wrong", "shake");
            $(".feedback", root).textContent = "Pas tout à fait… réécoute 👂";
          }
        };
      });
    };
    round();
  }

  async function donePart() {
    save((p) => (p.reading[st!.id] = true));
    markActiveToday();
    const idx = r.stages.findIndex((s) => s.id === st!.id);
    const next: ReadingStage | undefined = r.stages[idx + 1];
    root.innerHTML = `
      <div class="flow"><main class="card-stack done">
        <section class="card center celebrate">
          <div class="trophy">📖</div>
          <h2>Étape terminée !</h2>
          <p>Tu sais maintenant lire : <b class="letters-done">${[...known].join(" ")}</b></p>
          <div class="col">
            ${next ? `<button id="go-next" class="primary">Étape suivante : ${esc(next.titleFr)}</button>` : `<p>🏆 Tu connais tout l'alphabet russe !</p>`}
            <button id="go-home" class="secondary">Retour à la lecture</button>
          </div>
        </section></main></div>`;
    confetti($(".celebrate", root));
    $("#go-home", root).onclick = () => navigate("reading");
    if (next) $("#go-next", root).onclick = () => navigate(`reading/${next.id}`);
  }

  show();
}
