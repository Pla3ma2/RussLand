/** Слово или знак препинания во фразе. s — индекс ударной гласной, a — аудио слова. */
export interface Token {
  t: string;
  w: boolean;
  s?: number | null;
  a?: string;
}

export interface Line {
  speaker: string;
  ru: string;
  fr: string;
  tokens: Token[];
  audio: string;
}

export interface PuzzleWord {
  lemma: string;
  fr: string;
  phraseFr: string;
  form: string;
  stem: string;
  endLemma: string;
  endForm: string;
  changed: boolean;
  gender: string;
  stressLemma: number | null;
  stressForm: number | null;
  audioLemma: string;
  audioPhrase: string;
}

export interface Lesson {
  id: string;
  titleFr: string;
  sceneFr: string;
  hasAudio: boolean;
  speakers: Record<string, { name: string; color: string }>;
  dialogue: Line[];
  puzzle: {
    before: Token[];
    after: string;
    frameFr: string;
    caseColor: string;
    words: PuzzleWord[];
    task: { fr: string; answer: string };
    insightFr: string[];
  };
  speak: { line: Line; grammar: string[] };
}
