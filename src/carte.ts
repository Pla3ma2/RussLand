/** «Ma carte» — скелет языка: таблица падежей и глаголов, клетки открываются по ходу уроков. */
import { getAllLevels, getCarte } from "./content";
import { play } from "./audio";
import { $$, esc } from "./ui";
import { progress } from "./state";
import type { Unlock } from "./types";

const PRON_FR: Record<string, string> = { я: "je", ты: "tu", он: "il / elle", мы: "nous", вы: "vous", они: "ils" };

export async function renderCarte(root: HTMLElement) {
  const page = root.querySelector<HTMLElement>("#page")!;
  const [carte, levels] = await Promise.all([getCarte(), getAllLevels()]);
  const done = progress().levels;
  const unlocks: Unlock[] = levels.filter((l) => done[l.id]?.done).flatMap((l) => l.unlocks);

  const caseCell = new Map<string, { from: string; to: string }>();
  const verbCell = new Set<string>();
  for (const u of unlocks) {
    if ("case" in u) caseCell.set(`${u.case}.${u.gender}`, { from: u.from, to: u.to });
    else u.persons.forEach((p) => verbCell.add(`${u.verb}.${p}`));
  }
  const opened = caseCell.size + verbCell.size;
  const totalCells = carte.cases.length * carte.genders.length + carte.verbs.length * 6;

  const cell = (caseId: string, g: string, color: string) => {
    const c = caseCell.get(`${caseId}.${g}`);
    if (!c) return `<td class="locked">?</td>`;
    let cp = 0;
    while (cp < Math.min(c.from.length, c.to.length) && c.from[cp].toLowerCase() === c.to[cp].toLowerCase()) cp++;
    const stem = c.to.slice(0, cp);
    const end = c.to.slice(cp);
    const same = c.from.toLowerCase() === c.to.toLowerCase();
    return `<td><span class="cform">${esc(stem)}<b style="color:${color}">${esc(end)}</b></span>${same && caseId !== "nomn" ? `<small class="muted">pareil</small>` : ""}</td>`;
  };

  page.innerHTML = `
    <section class="card">
      <h2>Ma carte du russe</h2>
      <p class="hint">Le squelette de la langue. Chaque leçon allume de nouvelles cases. Tu as déjà ouvert <b>${opened}</b> cases sur ${totalCells}.</p>
      <div class="meter"><span style="width:${Math.round((opened / totalCells) * 100)}%"></span></div>
    </section>
    <section class="card">
      <h3>Les mots changent de fin</h3>
      <div class="table-wrap"><table class="carte">
        <thead><tr><th></th>${carte.cases.map((c) => `<th style="color:${c.color}">${esc(c.fr)}<small>${esc(c.hintFr)}</small></th>`).join("")}</tr></thead>
        <tbody>${carte.genders.map((g) => `<tr><th>${esc(g.fr)}<small>${esc(g.hintFr)}</small></th>${carte.cases.map((c) => cell(c.id, g.id, c.color)).join("")}</tr>`).join("")}</tbody>
      </table></div>
    </section>
    <section class="card">
      <h3>Les verbes changent selon la personne</h3>
      <div class="table-wrap"><table class="carte verbs">
        <thead><tr><th></th>${carte.verbs.map((v) => `<th>${esc(v.verb)}<small>${esc(v.fr)}</small></th>`).join("")}</tr></thead>
        <tbody>${Object.keys(PRON_FR).map((p) => `<tr><th>${p}<small>${PRON_FR[p]}</small></th>${carte.verbs.map((v) => {
          const f = v.forms[p];
          if (!verbCell.has(`${v.verb}.${p}`)) return `<td class="locked">?</td>`;
          return `<td><button class="cform vplay" data-w="${esc(f.to)}" data-a="${esc(f.audio ?? "")}">${esc(f.stem)}<b style="color:${carte.verbColor}">${esc(f.endTo)}</b></button></td>`;
        }).join("")}</tr>`).join("")}</tbody>
      </table></div>
      <p class="hint">Les cases « ? » s'ouvriront dans les prochaines leçons.</p>
    </section>`;
  $$<HTMLButtonElement>(".vplay", page).forEach((b) => (b.onclick = () => play(b.dataset.a!, b.dataset.w!)));
}
