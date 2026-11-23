/** Общие кусочки интерфейса: слова с подсказкой, кнопки, блок «скажи сам». */
import type { Line, Token } from "./types";
import { renderStressed } from "./stress";
import { translitHtml } from "./translit";
import { play, playBlob, stop } from "./audio";
import { Recorder, loadVosk, normalize, recognize, toWav, voskAvailable } from "./speech";
import { progress, save } from "./state";

export const $ = <T extends HTMLElement = HTMLElement>(sel: string, root: ParentNode = document) =>
  root.querySelector<T>(sel)!;
export const $$ = <T extends HTMLElement = HTMLElement>(sel: string, root: ParentNode = document) =>
  [...root.querySelectorAll<T>(sel)];
export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
export const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* ---------- слова с подсказкой (транслитерация + перевод) ---------- */

let tipEl: HTMLDivElement | null = null;
let tipTimer: ReturnType<typeof setTimeout> | undefined;

function hideTip() {
  tipEl?.classList.remove("show");
}

export function showWordTip(anchor: HTMLElement, token: Token, gloss?: string) {
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.className = "word-tip";
    document.body.appendChild(tipEl);
    window.addEventListener("scroll", hideTip, { passive: true });
  }
  tipEl.innerHTML = `<div class="tl">${translitHtml(token.t, token.s)}</div>${gloss ? `<div class="gl">${esc(gloss)}</div>` : ""}`;
  tipEl.classList.add("show");
  const r = anchor.getBoundingClientRect();
  const tw = tipEl.offsetWidth;
  const left = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
  tipEl.style.left = `${left}px`;
  tipEl.style.top = `${r.top + window.scrollY - tipEl.offsetHeight - 8}px`;
  clearTimeout(tipTimer);
  tipTimer = setTimeout(hideTip, 2600);
}

export interface TokenOpts {
  glossary?: Record<string, string>;
  translit?: boolean;
}

export function tokensHtml(tokens: Token[]): string {
  return tokens
    .map((t, i) =>
      t.w
        ? `<button class="word" data-i="${i}">${renderStressed(t.t, t.s, t.t)}</button>`
        : `<span class="punct">${esc(t.t)}</span>`,
    )
    .join("");
}

/** Делает слова внутри root нажимаемыми: озвучка + подсказка над словом. */
export function bindTokens(root: HTMLElement, tokens: Token[], opts: TokenOpts = {}) {
  $$<HTMLButtonElement>(".word", root).forEach((b) => {
    b.onclick = (e) => {
      e.stopPropagation();
      const t = tokens[Number(b.dataset.i)];
      if (!t) return;
      b.classList.add("ping");
      setTimeout(() => b.classList.remove("ping"), 450);
      if (opts.translit !== false) {
        showWordTip(b, t, opts.glossary?.[t.t.toLowerCase().replace(/ё/g, "е")]);
      }
      if (t.a) play(t.a, t.t);
    };
  });
}

/* ---------- блок «скажи сам» ---------- */

export interface SpeakResult {
  spoken: boolean;
  recognized?: string;
  ok?: boolean;
}

/**
 * Показывает задание на французском, запись голоса, правильный ответ,
 * сравнение «моя запись / модель» и (если включено) офлайн-распознавание.
 */
export function speakBox(
  container: HTMLElement,
  line: Line,
  grammar: string[],
  opts: { glossary?: Record<string, string>; onDone: (r: SpeakResult) => void; showPrompt?: boolean },
) {
  container.innerHTML = `
    <div class="speak">
      ${opts.showPrompt === false ? "" : `<p class="prompt">Dis en russe :<br><b>« ${esc(line.fr)} »</b></p>`}
      <button class="mic" type="button"><span class="mic-ico">🎙️</span><span class="mic-txt">Appuie et parle</span></button>
      <div class="answer hidden">
        <div class="ru big-ru">${tokensHtml(line.tokens)}</div>
        <div class="heard"></div>
        <div class="row">
          <button class="secondary mine" type="button" disabled>▶ Ma voix</button>
          <button class="secondary model" type="button">▶ Le modèle</button>
        </div>
      </div>
      <button class="link skip" type="button">Je ne peux pas parler maintenant</button>
    </div>`;
  const root = container;
  bindTokens($(".answer", root), line.tokens, { glossary: opts.glossary });
  const rec = new Recorder();
  let wav: Blob | null = null;
  let revealed = false;

  const reveal = (r: SpeakResult) => {
    $(".answer", root).classList.remove("hidden");
    $(".skip", root).classList.add("hidden");
    if (!revealed) {
      revealed = true;
      opts.onDone(r);
    }
  };
  $(".model", root).onclick = () => play(line.audio, line.ru);
  $(".mine", root).onclick = () => wav && playBlob(wav);
  $(".skip", root).onclick = () => {
    reveal({ spoken: false });
    play(line.audio, line.ru);
  };

  const mic = $<HTMLButtonElement>(".mic", root);
  const txt = $(".mic-txt", root);
  mic.onclick = async () => {
    if (!rec.active) {
      stop();
      try {
        await rec.start();
      } catch {
        $(".heard", root).textContent = "Micro indisponible : autorise le micro dans ton navigateur.";
        reveal({ spoken: false });
        return;
      }
      mic.classList.add("recording");
      txt.textContent = "Je t'écoute… touche pour finir";
      return;
    }
    mic.classList.remove("recording");
    txt.textContent = "Réessayer";
    const { samples, sampleRate } = await rec.stop();
    wav = toWav(samples, sampleRate);
    $<HTMLButtonElement>(".mine", root).disabled = false;
    const heard = $(".heard", root);
    $(".answer", root).classList.remove("hidden");
    let result: SpeakResult = { spoken: true };
    if (progress().settings.vosk) {
      heard.textContent = "Analyse…";
      heard.className = "heard";
      try {
        const text = await recognize(samples, sampleRate, grammar);
        const ok = normalize(text) === normalize(line.ru);
        result = { spoken: true, recognized: text, ok };
        heard.innerHTML = text && text !== "[unk]"
          ? `J'ai entendu : <b>${esc(text)}</b> ${ok ? "✅ Parfait !" : "— presque ! Écoute le modèle et réessaie."}`
          : "Je n'ai pas bien entendu. Parle un peu plus fort et réessaie.";
        heard.className = `heard ${ok ? "ok" : "ko"}`;
      } catch {
        heard.textContent = "La reconnaissance a échoué. Compare ta voix au modèle 👂";
      }
    } else {
      heard.textContent = "Compare ta voix au modèle 👂";
    }
    reveal(result);
    await play(line.audio, line.ru);
  };
}

/* ---------- переключатель распознавания речи ---------- */

export async function voskToggle(container: HTMLElement) {
  const available = await voskAvailable();
  const render = () => {
    const on = progress().settings.vosk;
    if (!available) {
      container.innerHTML = `<small class="muted">Auto-évaluation : compare ta voix au modèle.</small>`;
      return;
    }
    container.innerHTML = on
      ? `<small class="muted">✅ Reconnaissance vocale activée (hors ligne). <button class="link small off" type="button">Désactiver</button></small>`
      : `<button class="link small on" type="button">Activer la reconnaissance vocale hors ligne (≈45 Mo, une seule fois)</button>`;
    container.querySelector<HTMLButtonElement>(".on")?.addEventListener("click", async () => {
      container.innerHTML = `<small class="muted">⏳ Téléchargement du modèle… (une seule fois)</small>`;
      try {
        await loadVosk();
        save((p) => (p.settings.vosk = true));
      } catch {
        container.innerHTML = `<small class="muted">❌ Impossible de charger le modèle sur cet appareil.</small>`;
        return;
      }
      render();
    });
    container.querySelector<HTMLButtonElement>(".off")?.addEventListener("click", () => {
      save((p) => (p.settings.vosk = false));
      render();
    });
  };
  render();
  if (progress().settings.vosk && available) loadVosk().catch(() => save((p) => (p.settings.vosk = false)));
}

/* ---------- маленькие помощники ---------- */

export function confetti(container: HTMLElement) {
  const colors = ["#e07a5f", "#3d5a80", "#81b29a", "#f2cc8f", "#3a86ff"];
  for (let i = 0; i < 40; i++) {
    const s = document.createElement("span");
    s.className = "confetti";
    s.style.left = `${Math.random() * 100}%`;
    s.style.background = colors[i % colors.length];
    s.style.animationDelay = `${Math.random() * 0.4}s`;
    s.style.transform = `rotate(${Math.random() * 360}deg)`;
    container.appendChild(s);
    setTimeout(() => s.remove(), 2200);
  }
}
