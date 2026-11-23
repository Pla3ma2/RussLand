/** Проигрывание озвучки. Если mp3 нет (сборка без озвучки) — голос браузера. */
let current: HTMLAudioElement | null = null;
let useFiles = true;

export function setUseFiles(v: boolean) {
  useFiles = v;
}

function speakFallback(text: string, rate = 1): Promise<void> {
  return new Promise((resolve) => {
    if (!("speechSynthesis" in window)) return resolve();
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "ru-RU";
    u.rate = rate;
    u.onend = () => resolve();
    u.onerror = () => resolve();
    speechSynthesis.speak(u);
  });
}

export function stop() {
  current?.pause();
  current = null;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
}

export function play(file: string, text: string, rate = 1): Promise<void> {
  stop();
  if (!useFiles) return speakFallback(text, rate);
  return new Promise((resolve) => {
    const a = new Audio(`./audio/${file}`);
    a.playbackRate = rate;
    current = a;
    a.onended = () => resolve();
    a.onerror = () => speakFallback(text, rate).then(resolve);
    a.play().catch(() => speakFallback(text, rate).then(resolve));
  });
}

export function playBlob(blob: Blob): Promise<void> {
  stop();
  return new Promise((resolve) => {
    const url = URL.createObjectURL(blob);
    const a = new Audio(url);
    current = a;
    a.onended = () => {
      URL.revokeObjectURL(url);
      resolve();
    };
    a.play().catch(() => resolve());
  });
}
