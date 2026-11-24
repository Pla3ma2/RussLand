/** Прогресс ученика: хранится только на устройстве (localStorage). */
import type { Card } from "ts-fsrs";

export interface SrsEntry {
  levelId: string;
  card: Card;
}

export interface Progress {
  v: 1;
  levels: Record<string, { done: boolean; doneAt?: string; parts?: number }>;
  reading: Record<string, boolean>;
  srs: Record<string, SrsEntry>;
  settings: { vosk: boolean };
  days: string[]; // дни, когда человек занимался (для серии)
}

const KEY = "russland-progress-v1";

function empty(): Progress {
  return { v: 1, levels: {}, reading: {}, srs: {}, settings: { vosk: false }, days: [] };
}

function revive(p: Progress): Progress {
  for (const e of Object.values(p.srs)) {
    const c = e.card as unknown as Record<string, unknown>;
    c.due = new Date(c.due as string);
    if (c.last_review) c.last_review = new Date(c.last_review as string);
  }
  return p;
}

let state: Progress = (() => {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? revive({ ...empty(), ...JSON.parse(raw) }) : empty();
  } catch {
    return empty();
  }
})();

export const progress = () => state;

export function save(mutator?: (p: Progress) => void) {
  mutator?.(state);
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* хранилище недоступно — работаем в памяти */
  }
}

export function markActiveToday() {
  const today = new Date().toISOString().slice(0, 10);
  if (!state.days.includes(today)) save((p) => p.days.push(today));
}

/** Серия: сколько дней подряд (включая сегодня или вчера) были занятия. */
export function streak(): number {
  const set = new Set(state.days);
  let n = 0;
  const d = new Date();
  if (!set.has(d.toISOString().slice(0, 10))) d.setDate(d.getDate() - 1);
  while (set.has(d.toISOString().slice(0, 10))) {
    n++;
    d.setDate(d.getDate() - 1);
  }
  return n;
}

export function resetProgress() {
  state = empty();
  save();
}
