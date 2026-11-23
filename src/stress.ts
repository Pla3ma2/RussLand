const VOWELS = /[аеёиоуыэюяАЕЁИОУЫЭЮЯ]/g;

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/** Нужно ли показывать ударение: не в односложных словах и не в словах с «ё». */
export function needsMark(word: string): boolean {
  return (word.match(VOWELS)?.length ?? 0) > 1 && !/[ёЁ]/.test(word);
}

/**
 * Слово с видимым ударением: ударная гласная выделена и получает знак «´» (рисуется CSS, чтобы не зависеть от шрифта).
 * offset — сдвиг, если рисуем только кусок слова (основу или окончание).
 */
export function renderStressed(part: string, stress: number | null | undefined, fullWord: string, offset = 0): string {
  const show = stress != null && needsMark(fullWord);
  let html = "";
  for (let i = 0; i < part.length; i++) {
    const ch = esc(part[i]);
    if (show && i + offset === stress) {
      html += `<span class="stressed">${ch}́</span>`;
    } else {
      html += ch;
    }
  }
  return html;
}
