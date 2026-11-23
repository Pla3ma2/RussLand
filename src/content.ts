import type { Alphabet, Carte, Index, Level, ReadingStage } from "./types";
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

export async function getAllLevels(): Promise<Level[]> {
  const idx = await getIndex();
  return Promise.all(idx.levels.map((l) => getLevel(l.id)));
}
