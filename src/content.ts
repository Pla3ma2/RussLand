import type { Alphabet, Carte, Index, Level, RawWord, ReadText, ReadingStage, Word } from "./types";
import { setUseFiles } from "./audio";

const cache = new Map<string, Promise<unknown>>();

function get<T>(path: string): Promise<T> {
  if (!cache.has(path)) {
    const p = fetch(`./content/${path}`).then((r) => {
      if (!r.ok) throw new Error(`${path}: ${r.status}`);
      return r.json();
    });
    p.catch(() => cache.delete(path));
    cache.set(path, p);
  }
  return cache.get(path) as Promise<T>;
}

export async function getIndex(): Promise<Index> {
  const idx = await get<Index>("index.json");
  setUseFiles(idx.hasAudio);
  return idx;
}
export const getLevel = (id: string) => get<Level>(`levels/${id}.json`);
export const getAlphabet = () => get<Alphabet>("alphabet.json");
export const getReading = () => get<{ stages: ReadingStage[] }>("reading.json");
export const getCarte = () => get<Carte>("carte.json");
export const getTexts = () => get<{ texts: ReadText[] }>("texts.json");

export async function getAllLevels(): Promise<Level[]> {
  const idx = await getIndex();
  return Promise.all(idx.levels.map((l) => getLevel(l.id)));
}

let wordsP: Promise<Word[]> | null = null;
/** База 5000 слов (по частотности). */
export function getWords(): Promise<Word[]> {
  if (!wordsP) {
    wordsP = get<RawWord[]>("words.json").then((raw) => raw.map(([ru, s, fr, g, a], i) => ({ i, ru, s, fr, g, a })));
    wordsP.catch(() => (wordsP = null));
  }
  return wordsP;
}

export const wordKey = (s: string) => s.trim().toLowerCase().replace(/ё/g, "е").replace(/[+\u0301]/g, "");

let lookupP: Promise<Map<string, Word>> | null = null;
/** Ищет слово в базе (без учёта регистра и ё/е). */
export async function lookupWord(ru: string): Promise<Word | undefined> {
  if (!lookupP) lookupP = getWords().then((ws) => new Map(ws.map((w) => [wordKey(w.ru), w])));
  return (await lookupP).get(wordKey(ru));
}
