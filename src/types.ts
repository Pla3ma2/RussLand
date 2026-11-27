/** Слово или знак препинания. s — индекс ударной гласной, a — аудио слова. */
export interface Token {
  t: string;
  w: boolean;
  s?: number | null;
  a?: string;
  l?: string; // начальная форма (для поиска в базе слов)
}

export interface Line {
  speaker: string;
  ru: string;
  fr: string;
  tokens: Token[];
  audio: string;
}

export interface Morph {
  from: string;
  to: string;
  stem: string;
  endFrom: string;
  endTo: string;
  stressFrom: number | null;
  stressTo: number | null;
  changed: boolean;
  audio?: string;
}

export interface ExploreWord {
  tile: string;
  tileStress: number | null;
  fr: string;
  phraseFr: string;
  phrase: string;
  morph: Morph;
  audioTile: string;
  audioPhrase: string;
}

export interface Explore {
  type: "plain" | "case" | "person";
  frameFr: string;
  color: string;
  hintFr?: string;
  before: Token[];
  after: Token[];
  verb: string | null;
  words: ExploreWord[];
}

export type Task =
  | { type: "pick"; fr: string; answer: string }
  | { type: "order"; line: Line };

export type Unlock =
  | { case: string; gender: string; from: string; to: string }
  | { verb: string; persons: string[] };

export interface ReviewItem {
  id: string;
  ru: string;
  fr: string;
  tokens: Token[];
  audio: string;
}

export interface Level {
  id: string;
  order: number;
  titleFr: string;
  titleRu: string;
  emoji: string;
  sceneFr: string;
  learner: string;
  hasAudio: boolean;
  speakers: Record<string, { name: string; nameFr: string; color: string }>;
  dialogue: Line[];
  explore: Explore;
  tasks: Task[];
  insight: { by: string; fr: string[] };
  speak: Line[];
  grammar: string[];
  cando: string[];
  glossary: Record<string, string>;
  unlocks: Unlock[];
  items: ReviewItem[];
}

export interface LevelSummary {
  version?: number;
  parts?: number;
  id: string;
  order: number;
  titleFr: string;
  titleRu: string;
  emoji: string;
  cando: string[];
}

export interface Index {
  hasAudio: boolean;
  levels: LevelSummary[];
}

export interface Letter {
  l: string;
  type: "vowel" | "consonant" | "sign";
  group: "familiar" | "deceiver" | "new" | "sign";
  exampleRu: string;
  exampleFr: string;
  tipFr: string;
  audio: string;
  exampleTokens: Token[];
  exampleAudio: string;
}

export interface Alphabet {
  groups: Record<string, { fr: string; color: string }>;
  letters: Letter[];
}

export interface Clip {
  t: string;
  audio: string;
}

export interface ReadingStage {
  id: string;
  titleFr: string;
  letters: string[];
  tipFr: string[];
  syllables: Clip[];
  words: { t: string; s: number | null; fr: string; audio: string }[];
  pairs: Clip[][];
}

export interface Carte {
  cases: { id: string; fr: string; hintFr: string; color: string }[];
  genders: { id: string; fr: string; hintFr: string }[];
  verbColor: string;
  verbs: { verb: string; fr: string; forms: Record<string, Morph> }[];
}

export interface PhraseV2 extends Line {
  id: string;
  noteFr: string;
  gap?: { index: number; whyFr?: string; distractors: { t: string; a: string; s: number | null }[] };
  orders?: string[];
  combo?: { from: string[]; extra: { t: string; a: string; s: number | null }[] };
}

export type StepV2 =
  | { type: "scene" }
  | { type: "block"; phrases: string[]; review?: string[] }
  | { type: "warmup"; phrases: string[] }
  | { type: "insight"; index: number }
  | { type: "explore" }
  | { type: "final" }
  | { type: "combine"; phrases: string[] }
  | { type: "roleplay" };

export interface LevelV2 {
  version: 2;
  id: string;
  order: number;
  titleFr: string;
  titleRu: string;
  emoji: string;
  sceneFr: string;
  learner: string;
  hasAudio?: boolean;
  speakers: Record<string, { name: string; nameFr: string; color: string }>;
  dialogue: Line[];
  phrases: Record<string, PhraseV2>;
  parts: { titleFr: string; steps: StepV2[] }[];
  insights: { by: string; fr: string[] }[];
  explore: Explore;
  tasks: { type: "pick"; fr: string; answer: string }[];
  grammar: string[];
  cando: string[];
  glossary: Record<string, string>;
  unlocks: Unlock[];
  items: ReviewItem[];
}

/** Слово из базы 5000: [слово, ударение, перевод, род, аудио]. */
export type RawWord = [string, number | null, string, string, string];
export interface Word {
  i: number; // место по частотности (0 = самое частое)
  ru: string;
  s: number | null;
  fr: string;
  g: string; // m / f / n для существительных
  a: string;
}
