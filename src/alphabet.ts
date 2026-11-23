/** Кнопка «Алфавит»: все 33 буквы, звук, подсказка и пример — доступно с любого экрана. */
import { getAlphabet, getReading } from "./content";
import { play } from "./audio";
import { renderStressed } from "./stress";
import { $, $$, esc } from "./ui";
import { progress } from "./state";
import type { Letter } from "./types";

export async function openAlphabet() {
  const [abc, reading] = await Promise.all([getAlphabet(), getReading()]);
  const learned = new Set<string>();
  for (const st of reading.stages) if (progress().reading[st.id]) st.letters.forEach((l) => learned.add(l));

  const sheet = document.createElement("div");
  sheet.className = "sheet-backdrop";
  const cell = (L: Letter, i: number) =>
    `<button class="abc-cell ${learned.has(L.l) ? "learned" : ""}" data-i="${i}" style="--g:${abc.groups[L.group].color}">
      <span class="up">${L.l}</span><span class="lo">${L.l.toLowerCase()}</span></button>`;
  sheet.innerHTML = `
    <div class="sheet" role="dialog" aria-label="Alphabet">
      <div class="sheet-head"><b>Alphabet russe</b><button class="close" aria-label="Fermer">✕</button></div>
      <p class="hint">Touche une lettre pour entendre <b>son son</b> (et pas son nom).</p>
      <div class="abc-grid">${abc.letters.map(cell).join("")}</div>
      <div class="abc-legend">${Object.entries(abc.groups).map(([, g]) => `<span><i style="background:${g.color}"></i>${esc(g.fr)}</span>`).join("")}</div>
      <div class="abc-detail hidden"></div>
    </div>`;
  document.body.appendChild(sheet);
  requestAnimationFrame(() => sheet.classList.add("open"));
  const close = () => {
    sheet.classList.remove("open");
    setTimeout(() => sheet.remove(), 250);
  };
  sheet.onclick = (e) => e.target === sheet && close();
  $(".close", sheet).onclick = close;

  const detail = $(".abc-detail", sheet);
  $$<HTMLButtonElement>(".abc-cell", sheet).forEach((b) => {
    b.onclick = () => {
      const L = abc.letters[Number(b.dataset.i)];
      $$(".abc-cell", sheet).forEach((c) => c.classList.remove("sel"));
      b.classList.add("sel");
      play(L.audio, L.l.toLowerCase());
      const ex = L.exampleTokens.find((t) => t.w);
      detail.classList.remove("hidden");
      detail.innerHTML = `
        <div class="abc-big" style="color:${abc.groups[L.group].color}">${L.l}${L.l.toLowerCase()}</div>
        <div class="abc-info">
          <div class="abc-group">${esc(abc.groups[L.group].fr)}</div>
          <p>${esc(L.tipFr)}</p>
          <div class="row left">
            <button class="secondary snd" type="button">🔊 Le son</button>
            <button class="secondary exw" type="button">${ex ? renderStressed(ex.t, ex.s, ex.t) : esc(L.exampleRu)} <small>· ${esc(L.exampleFr)}</small></button>
          </div>
        </div>`;
      $(".snd", detail).onclick = () => play(L.audio, L.l.toLowerCase());
      $(".exw", detail).onclick = () => play(L.exampleAudio, L.exampleRu);
      detail.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
  });
}
