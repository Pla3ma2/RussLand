/** Интервальное повторение (FSRS) для фраз, которые ученик уже говорил в уроках. */
import { createEmptyCard, fsrs, generatorParameters, Rating, type Grade } from "ts-fsrs";
import { progress, save } from "./state";
import type { Level, ReviewItem } from "./types";

const scheduler = fsrs(generatorParameters({ enable_fuzz: true, request_retention: 0.9 }));

export { Rating };

export function addItems(level: Level) {
  save((p) => {
    for (const it of level.items) {
      if (!p.srs[it.id]) p.srs[it.id] = { levelId: level.id, card: createEmptyCard(new Date()) };
    }
  });
}

export function dueIds(now = new Date()): string[] {
  return Object.entries(progress().srs)
    .filter(([, e]) => e.card.due <= now)
    .sort((a, b) => +a[1].card.due - +b[1].card.due)
    .map(([id]) => id);
}

/** Если ничего не «созрело», даём потренировать самые слабые фразы. */
export function weakestIds(n: number): string[] {
  return Object.entries(progress().srs)
    .sort((a, b) => a[1].card.stability - b[1].card.stability)
    .slice(0, n)
    .map(([id]) => id);
}

export function grade(id: string, rating: Grade) {
  save((p) => {
    const e = p.srs[id];
    if (!e) return;
    e.card = scheduler.next(e.card, new Date(), rating).card;
  });
}

export function findItem(levels: Level[], id: string): ReviewItem | undefined {
  for (const lv of levels) {
    const it = lv.items.find((i) => i.id === id);
    if (it) return it;
  }
  return undefined;
}
