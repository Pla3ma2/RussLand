import "./style.css";
import { route, startRouter, navigate } from "./router";
import { getIndex } from "./content";
import { progress, save, streak, resetProgress } from "./state";
import { dueIds } from "./srs";
import { $, $$, esc } from "./ui";
import { registerSW } from "virtual:pwa-register";

/* После каждого обновления сайта старые файлы удаляются. Если в телефоне осталась старая
   версия страницы, её куски уже не скачать — тогда просто перезагружаемся на новую версию. */
registerSW({ immediate: true });
window.addEventListener("vite:preloadError", (e) => {
  e.preventDefault();
  reloadOnce();
});
function reloadOnce() {
  const k = "russland-reloaded";
  if (sessionStorage.getItem(k)) return;
  sessionStorage.setItem(k, "1");
  location.reload();
}
setTimeout(() => sessionStorage.removeItem("russland-reloaded"), 10000);

/* Повторения из уроков, которых больше нет (уроки переделаны), убираем. */
getIndex().then((idx) => {
  const ids = new Set(idx.levels.map((l) => l.id));
  const stale = Object.keys(progress().srs).filter((k) => !ids.has(progress().srs[k].levelId));
  if (stale.length) save((p) => stale.forEach((k) => delete p.srs[k]));
}).catch(() => {});

const app = document.querySelector<HTMLDivElement>("#app")!;

type Tab = "lessons" | "reading" | "words" | "review" | "carte";

/** Каркас для пяти главных вкладок: шапка с алфавитом + нижнее меню. */
function shell(tab: Tab): HTMLElement {
  const due = dueIds().length;
  const s = streak();
  app.innerHTML = `
    <div class="shell">
      <header class="top">
        <div class="brand">Russ<b>Land</b></div>
        <div class="top-right">
          ${s > 0 ? `<span class="streak" title="Jours d'affilée">🔥 ${s}</span>` : ""}
          <button class="abc-btn" aria-label="Alphabet">АБВ</button>
        </div>
      </header>
      <main id="page" class="card-stack"></main>
      <nav class="tabbar">
        <button data-t="lessons" class="${tab === "lessons" ? "on" : ""}"><span>🗣️</span>Leçons</button>
        <button data-t="reading" class="${tab === "reading" ? "on" : ""}"><span>📖</span>Lecture</button>
        <button data-t="words" class="${tab === "words" ? "on" : ""}"><span>🃏</span>Mots</button>
        <button data-t="review" class="${tab === "review" ? "on" : ""}"><span>🔁</span>Révision${due ? `<i class="badge">${due}</i>` : ""}</button>
        <button data-t="carte" class="${tab === "carte" ? "on" : ""}"><span>🗺️</span>Carte</button>
      </nav>
    </div>`;
  $(".abc-btn", app).onclick = () => import("./alphabet").then((m) => m.openAlphabet());
  $$<HTMLButtonElement>(".tabbar button", app).forEach((b) => {
    b.onclick = () => navigate({ lessons: "", reading: "reading", words: "words", review: "review", carte: "carte" }[b.dataset.t as Tab]);
  });
  return app;
}

async function renderLessons() {
  shell("lessons");
  const page = $("#page", app);
  const idx = await getIndex();
  const done = progress().levels;
  const firstOpen = idx.levels.find((l) => !done[l.id]?.done);
  const due = dueIds().length;
  const readingStarted = Object.keys(progress().reading).length > 0;
  page.innerHTML = `
    ${Object.keys(done).length === 0 ? `
      <section class="card hero">
        <h1>Bienvenue ! 👋</h1>
        <p>Ici, tu apprends le russe pour <b>parler</b> vite : des phrases utiles, une petite histoire, et tu parles à voix haute dès la première leçon.</p>
        <p class="muted">L'alphabet te fait peur ? Commence par l'onglet <b>Lecture</b>, ou touche <b>АБВ</b> en haut à tout moment. Dans les leçons, touche un mot pour voir comment il se lit.</p>
      </section>` : ""}
    ${due > 0 ? `<button class="card review-cta" id="rev"><span>🔁</span><span><b>${due} phrase${due > 1 ? "s" : ""} à revoir</b><small>2–3 minutes pour ne rien oublier</small></span><span class="go">›</span></button>` : ""}
    ${!readingStarted ? `<button class="card review-cta reading-cta" id="read"><span>📖</span><span><b>Apprendre l'alphabet</b><small>Les lettres comme elles sonnent, puis tes premiers mots</small></span><span class="go">›</span></button>` : ""}
    <section class="path">
      ${idx.levels.map((l) => {
        const isDone = !!done[l.id]?.done;
        const isNext = firstOpen?.id === l.id;
        const locked = !isDone && !isNext;
        return `<button class="lesson ${isDone ? "done" : ""} ${isNext ? "next" : ""} ${locked ? "locked" : ""}" data-id="${l.id}">
          <span class="lesson-emoji">${isDone ? "✓" : l.emoji}</span>
          <span class="lesson-body">
            <small>Leçon ${l.order}</small>
            <b>${esc(l.titleFr)}</b>
            <span class="lesson-ru">${esc(l.titleRu)}${l.parts && !isDone && (done[l.id]?.parts ?? 0) > 0 ? ` · partie ${(done[l.id]?.parts ?? 0) + 1}/${l.parts}` : ""}</span>
          </span>
          <span class="go">${locked ? "🔒" : isNext ? "▶" : "↺"}</span>
        </button>`;
      }).join("")}
      <div class="lesson coming"><span class="lesson-emoji">✨</span><span class="lesson-body"><b>La suite arrive bientôt…</b></span></div>
    </section>
    <p class="center"><button class="link small" id="reset">Réinitialiser ma progression</button></p>
    <p class="center muted credits">Voix : Silero Models (CC BY-NC 4.0) · Reconnaissance vocale : Vosk</p>`;
  page.querySelector("#rev")?.addEventListener("click", () => navigate("review/session"));
  page.querySelector("#read")?.addEventListener("click", () => navigate("reading"));
  $$<HTMLButtonElement>(".lesson[data-id]", page).forEach((b) => {
    b.onclick = () => {
      if (b.classList.contains("locked")) {
        b.classList.remove("shake");
        void b.offsetWidth;
        b.classList.add("shake");
        return;
      }
      navigate(`level/${b.dataset.id}`);
    };
  });
  $("#reset", page).onclick = () => {
    if (confirm("Effacer toute ta progression ?")) {
      resetProgress();
      renderLessons();
    }
  };
}

route("", renderLessons);
route("level/:id", async (root, id) => {
  const idx = await getIndex();
  if (idx.levels.find((l) => l.id === id)?.version === 2) return (await import("./lesson2")).renderLessonHome(root, id);
  return (await import("./level")).renderLevel(root, id);
});
route("level/:id/:part", async (root, id, part) => (await import("./lesson2")).renderPart(root, id, part));
route("reading", async () => {
  shell("reading");
  await (await import("./reading")).renderReadingHome(app);
});
route("reading/:id", async (root, id) => (await import("./reading")).renderStage(root, id));
route("words", async () => {
  shell("words");
  await (await import("./words")).renderWordsHome(app);
});
route("words/s/:n", async (root, n) => (await import("./words")).renderStage(root, n));
route("words/l/:n", async (root, n) => (await import("./words")).renderWordLevel(root, n));
route("words/marathon", async (root) => (await import("./words")).renderMarathon(root));
route("words/cards", async (root) => (await import("./words")).renderMyCards(root));
route("review", async () => {
  shell("review");
  await (await import("./review")).renderReviewHome(app);
});
route("review/:mode", async (root, mode) => (await import("./review")).renderSession(root, mode));
route("carte", async () => {
  shell("carte");
  await (await import("./carte")).renderCarte(app);
});

startRouter(app);
