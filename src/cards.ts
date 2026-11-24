/** «Mes cartes»: свои карточки и слова в закладках. Хранятся на устройстве. */
import { progress, save, type MyCard } from "./state";
import { lookupWord, wordKey } from "./content";

export const myCards = () => progress().cards;

export function findCard(ru: string): MyCard | undefined {
  const k = wordKey(ru);
  return progress().cards.find((c) => wordKey(c.ru) === k);
}

export const isSaved = (ru: string) => !!findCard(ru);

export function addCard(c: Omit<MyCard, "id" | "added">): MyCard {
  const ex = findCard(c.ru);
  if (ex) return ex;
  const card: MyCard = { ...c, id: Math.random().toString(36).slice(2, 10), added: new Date().toISOString() };
  save((p) => p.cards.unshift(card));
  return card;
}

export function removeCard(id: string) {
  save((p) => (p.cards = p.cards.filter((c) => c.id !== id)));
}

/** ★: добавить / убрать. Если слово есть в базе — перевод, ударение и озвучка берутся оттуда. */
export async function toggleBookmark(ru: string, fr = "", s?: number | null, a?: string): Promise<boolean> {
  const ex = findCard(ru);
  if (ex) {
    removeCard(ex.id);
    return false;
  }
  const w = await lookupWord(ru);
  addCard({
    ru: w?.ru ?? ru,
    fr: w?.fr ?? fr,
    s: w ? w.s : s ?? null,
    a: w?.a ?? a,
    src: "bookmark",
  });
  return true;
}

export const STAR = (on: boolean) => `<button class="star ${on ? "on" : ""}" type="button" aria-label="Mes cartes">${on ? "★" : "☆"}</button>`;
