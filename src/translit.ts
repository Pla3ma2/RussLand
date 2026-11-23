/**
 * Транслитерация для франкоязычных: латиницей «как читал бы француз».
 * Учитываем ударение: безударное «о» звучит как «а» (молоко → malako).
 * Возвращает HTML, где ударный слог подчёркнут.
 */
const EXCEPTIONS: Record<string, string> = {
  "здравствуйте": "zdrAstvouïtié",
  "что": "chto",
  "что-нибудь": "chtO-nibout'",
  "пожалуйста": "pajAlousta",
  "конечно": "kaniéchna",
  "сегодня": "sivOdnia",
  "его": "ievO",
  "ничего": "nitchivO",
  "солнце": "sOntsé",
  "до": "da",
  "свидания": "svidAnia",
};

const VOWELS = "аеёиоуыэюя";

function base(ch: string, prev: string, next: string, stressed: boolean): string {
  const afterVowel = !prev || VOWELS.includes(prev) || prev === "ь" || prev === "ъ";
  switch (ch) {
    case "а": return "a";
    case "б": return next ? "b" : "p";
    case "в": return next ? "v" : "f";
    case "г": return "еиёюя".includes(next) ? "gu" : next ? "g" : "k";
    case "д": return next ? "d" : "t";
    case "е": return afterVowel ? "ié" : "é";
    case "ё": return afterVowel ? "io" : "io";
    case "ж": return next ? "j" : "ch";
    case "з": return next ? "z" : "s";
    case "и": return VOWELS.includes(prev) ? "ï" : "i";
    case "й": return "ï";
    case "к": return "k";
    case "л": return "l";
    case "м": return "m";
    case "н": return "n";
    case "о": return stressed ? "o" : "a";
    case "п": return "p";
    case "р": return "r";
    case "с": return VOWELS.includes(prev) && VOWELS.includes(next) ? "ss" : "s";
    case "т": return "t";
    case "у": return "ou";
    case "ф": return "f";
    case "х": return "kh";
    case "ц": return "ts";
    case "ч": return "tch";
    case "ш": return "ch";
    case "щ": return "chtch";
    case "ъ": return "";
    case "ы": return "y";
    case "ь": return "'";
    case "э": return "è";
    case "ю": return afterVowel ? "iou" : "iou";
    case "я": return afterVowel ? "ia" : "ia";
    case "-": return "-";
    default: return ch;
  }
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

export function translitHtml(word: string, stress: number | null | undefined): string {
  const w = word.toLowerCase();
  const exc = EXCEPTIONS[w];
  if (exc) {
    // заглавная буква в исключении = ударная гласная
    return esc(exc).replace(/[AEIOUY]/, (m) => `<u>${m.toLowerCase()}</u>`);
  }
  let out = "";
  for (let i = 0; i < w.length; i++) {
    const isStressed = stress === i || (w[i] === "ё");
    const piece = base(w[i], w[i - 1] ?? "", w[i + 1] ?? "", isStressed || countVowels(w) === 1);
    out += isStressed && VOWELS.includes(w[i]) ? `<u>${esc(piece)}</u>` : esc(piece);
  }
  return out;
}

function countVowels(w: string) {
  return [...w].filter((c) => VOWELS.includes(c)).length;
}
