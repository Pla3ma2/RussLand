/** Révision : фразы возвращаются по расписанию FSRS. Два вида заданий: понять на слух и сказать самому. */
import { getAllLevels } from "./content";
import { play, stop } from "./audio";
import { $, $$, ABC_BTN, bindAbc, bindTokens, confetti, esc, shuffle, sleep, speakBox, tokensHtml, voskToggle } from "./ui";
import { dueIds, findItem, grade, Rating, weakestIds } from "./srs";
import { markActiveToday, progress } from "./state";
import { navigate } from "./router";
import type { Level, ReviewItem } from "./types";

const SESSION = 10;

export async function renderReviewHome(root: HTMLElement) {
  const page = root.querySelector<HTMLElement>("#page")!;
  const total = Object.keys(progress().srs).length;
  const due = dueIds().length;
  page.innerHTML = `
    <section class="card center">
      <div class="trophy">🔁</div>
      <h2>Révisions</h2>
      ${total === 0
        ? `<p>Termine ta première leçon : ses phrases arriveront ici, et reviendront juste avant que tu les oublies.</p>
           <button class="primary" id="to-lessons">Aller aux leçons</button>`
        : `<p>${due > 0 ? `<b>${due}</b> phrase${due > 1 ? "s" : ""} à revoir aujourd'hui.` : "Rien à revoir pour l'instant 👌"}</p>
           <p class="muted">${total} phrase${total > 1 ? "s" : ""} dans ta mémoire.</p>
           <div class="col">
             ${due > 0 ? `<button class="primary" id="start">Commencer (${Math.min(due, SESSION)} phrases, ~3 min)</button>` : ""}
             <button class="${due > 0 ? "secondary" : "primary"}" id="practice">S'entraîner quand même</button>
           </div>`}
    </section>`;
  page.querySelector("#to-lessons")?.addEventListener("click", () => navigate(""));
  page.querySelector("#start")?.addEventListener("click", () => navigate("review/session"));
  page.querySelector("#practice")?.addEventListener("click", () => navigate("review/practice"));
}

export async function renderSession(root: HTMLElement, mode: string) {
  const levels = await getAllLevels();
  const ids = (mode === "practice" ? weakestIds(6) : dueIds().slice(0, SESSION));
  const items = ids.map((id) => findItem(levels, id)).filter(Boolean) as ReviewItem[];
  if (!items.length) return navigate("review");
  const allItems = levels.flatMap((l) => l.items);
  const glossary = Object.assign({}, ...levels.map((l) => l.glossary)) as Record<string, string>;
  const grammar = [...new Set(levels.flatMap((l) => l.grammar))];
  let k = 0;
  let correct = 0;

  const frame = (body: string) => {
    root.innerHTML = `
      <div class="flow">
        <header class="flow-head"><button class="close" aria-label="Fermer">✕</button>
          <div class="flow-title">🔁 Révision ${k + 1}/${items.length}</div>${ABC_BTN}</header>
        <div class="progress single"><div class="pstep now"><span style="--p:${(k / items.length) * 100}%"></span></div></div>
        <main class="card-stack">${body}</main>
        <footer class="flow-foot"><button id="next" class="primary hidden">Suivant</button></footer>
      </div>`;
    $(".close", root).onclick = () => {
      stop();
      navigate("review");
    };
    bindAbc(root);
  };

  const nextItem = () => {
    stop();
    k++;
    if (k >= items.length) return finish();
    show();
  };

  const show = () => {
    const it = items[k];
    // понимание на слух — для новых карточек и через раз; говорение — для остальных
    const listen = k % 2 === 0;
    if (listen) listenTask(it);
    else speakTask(it);
  };

  function listenTask(it: ReviewItem) {
    frame(`<section class="card center">
      <div class="task-kicker">Écoute et comprends</div>
      <button class="mic small-mic" id="again" type="button">🔊</button>
      <div class="ru big-ru hidden" id="ru">${tokensHtml(it.tokens)}</div>
      <div class="col" id="choices"></div>
      <div class="feedback"></div>
    </section>`);
    const distract = shuffle(allItems.filter((x) => x.fr !== it.fr)).slice(0, 2);
    const opts = shuffle([it, ...distract]);
    $("#choices", root).innerHTML = opts.map((o) => `<button class="tile wide" data-id="${esc(o.id)}">${esc(o.fr)}</button>`).join("");
    play(it.audio, it.ru);
    $("#again", root).onclick = () => play(it.audio, it.ru);
    let answered = false;
    $$<HTMLButtonElement>("#choices .tile", root).forEach((b) => {
      b.onclick = async () => {
        if (answered) return;
        answered = true;
        const ok = b.dataset.id === it.id;
        b.classList.add(ok ? "right" : "wrong");
        if (!ok) $$<HTMLButtonElement>("#choices .tile", root).find((x) => x.dataset.id === it.id)?.classList.add("right");
        $("#ru", root).classList.remove("hidden");
        bindTokens($("#ru", root), it.tokens, { glossary });
        $(".feedback", root).textContent = ok ? "Bravo !" : "Pas grave, elle reviendra bientôt.";
        grade(it.id, ok ? Rating.Good : Rating.Again);
        if (ok) correct++;
        await sleep(300);
        const n = $("#next", root);
        n.classList.remove("hidden");
        n.onclick = nextItem;
      };
    });
  }

  function speakTask(it: ReviewItem) {
    frame(`<section class="card">
      <div class="task-kicker">Dis-le en russe</div>
      <div id="sp"></div>
      <div class="rate hidden">
        <p class="hint center">C'était comment ?</p>
        <div class="rate-row">
          <button data-r="${Rating.Again}" class="rate-btn r1">Oublié</button>
          <button data-r="${Rating.Hard}" class="rate-btn r2">Difficile</button>
          <button data-r="${Rating.Good}" class="rate-btn r3">Bien</button>
          <button data-r="${Rating.Easy}" class="rate-btn r4">Facile</button>
        </div>
      </div>
      <div id="vosk" class="vosk"></div>
    </section>`);
    voskToggle($("#vosk", root));
    const line = { speaker: "", ru: it.ru, fr: it.fr, tokens: it.tokens, audio: it.audio };
    speakBox($("#sp", root), line, grammar, {
      glossary,
      onDone: (r) => {
        $(".rate", root).classList.remove("hidden");
        if (r.ok) $(".r3", root).classList.add("suggested");
      },
    });
    $$<HTMLButtonElement>(".rate-btn", root).forEach((b) => {
      b.onclick = () => {
        const r = Number(b.dataset.r) as Rating.Again | Rating.Hard | Rating.Good | Rating.Easy;
        grade(it.id, r);
        if (r !== Rating.Again) correct++;
        nextItem();
      };
    });
  }

  function finish() {
    markActiveToday();
    root.innerHTML = `
      <div class="flow"><main class="card-stack done">
        <section class="card center celebrate">
          <div class="trophy">✨</div>
          <h2>Révision terminée</h2>
          <p><b>${correct}</b> / ${items.length} réussies.</p>
          <p class="muted">Les phrases difficiles reviendront plus vite, les faciles plus tard.</p>
          <button id="home" class="primary">Retour</button>
        </section></main></div>`;
    confetti($(".celebrate", root));
    $("#home", root).onclick = () => navigate("review");
  }

  show();
  void (levels as Level[]);
}
