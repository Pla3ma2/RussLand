/** Проигрывание озвучки. Если mp3 нет (сборка без озвучки) — голос браузера. */
let current: HTMLAudioElement | null = null;
let pending: (() => void) | null = null;
let useFiles = true;

export function setUseFiles(v: boolean) {
  useFiles = v;
}

function finish() {
  const p = pending;
  pending = null;
  p?.();
}

function speakFallback(text: string, rate = 1): Promise<void> {
  return new Promise((resolve) => {
    if (!("speechSynthesis" in window)) return resolve();
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "ru-RU";
    u.rate = rate;
    pending = resolve;
    // на некоторых устройствах onend не приходит — страхуемся таймером
    const guard = setTimeout(finish, 1200 + text.length * 110);
    u.onend = u.onerror = () => {
      clearTimeout(guard);
      finish();
    };
    speechSynthesis.speak(u);
  });
}

/** Останавливает звук; ожидающие play() сразу завершаются. */
export function stop() {
  current?.pause();
  current = null;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  finish();
}

export function play(file: string, text: string, rate = 1): Promise<void> {
  stop();
  if (!useFiles || !file) return speakFallback(text, rate);
  return new Promise((resolve) => {
    const a = new Audio(`./audio/${file}`);
    a.playbackRate = rate;
    current = a;
    pending = resolve;
    const guard = setTimeout(finish, 15000);
    a.onended = () => {
      clearTimeout(guard);
      finish();
    };
    const fallback = () => {
      clearTimeout(guard);
      if (current !== a) return;
      pending = null;
      speakFallback(text, rate).then(resolve);
    };
    a.onerror = fallback;
    a.play().catch(fallback);
  });
}

export function playBlob(blob: Blob): Promise<void> {
  stop();
  return new Promise((resolve) => {
    const url = URL.createObjectURL(blob);
    const a = new Audio(url);
    current = a;
    pending = () => {
      URL.revokeObjectURL(url);
      resolve();
    };
    a.onended = finish;
    a.play().catch(finish);
  });
}
