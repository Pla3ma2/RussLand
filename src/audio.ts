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
  playSeq++;
  current?.pause();
  current = null;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  finish();
}

/* Файлы скачиваем через fetch: так ответ целиком (200) попадает в офлайн-кэш, а не кусками. */
const blobs = new Map<string, Promise<string>>();
function fileUrl(file: string): Promise<string> {
  let p = blobs.get(file);
  if (!p) {
    p = fetch(`./audio/${file}`).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.blob();
    }).then((b) => URL.createObjectURL(b));
    p.catch(() => blobs.delete(file));
    blobs.set(file, p);
  }
  return p;
}

let playSeq = 0;
export function play(file: string, text: string, rate = 1): Promise<void> {
  stop();
  if (!useFiles || !file) return speakFallback(text, rate);
  const seq = ++playSeq;
  return fileUrl(file).then(
    (url) => (seq === playSeq ? playUrl(url, text, rate) : undefined),
    () => (seq === playSeq ? speakFallback(text, rate) : undefined),
  );
}

/* Один общий плеер: на iPhone звук разрешён элементу, который уже играл после касания экрана. */
/** Настоящая тишина: WAV из нулей (0,05 с), собранный прямо в коде. */
function silentWav(): string {
  const n = 1200, buf = new ArrayBuffer(44 + n * 2), v = new DataView(buf);
  const str = (o: number, t: string) => [...t].forEach((c, k) => v.setUint8(o + k, c.charCodeAt(0)));
  str(0, "RIFF"); v.setUint32(4, 36 + n * 2, true); str(8, "WAVE"); str(12, "fmt ");
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, 24000, true); v.setUint32(28, 48000, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  str(36, "data"); v.setUint32(40, n * 2, true);
  return URL.createObjectURL(new Blob([buf], { type: "audio/wav" }));
}
let shared: HTMLAudioElement | null = null;
function player(): HTMLAudioElement {
  if (!shared) shared = new Audio();
  return shared;
}
function unlock() {
  const a = player();
  if (a.src) return;
  const url = silentWav();
  a.muted = true; // даже если что-то пойдёт не так — ничего не будет слышно
  a.src = url;
  const done = () => {
    if (a.src === url) a.pause(); // не трогаем, если уже играет настоящий звук
    a.muted = false;
  };
  a.play().then(done, done);
}
document.addEventListener("pointerdown", unlock, { once: true, capture: true });

function playUrl(url: string, text: string, rate: number): Promise<void> {
  return new Promise((resolve) => {
    const a = player();
    a.onended = a.onerror = null;
    a.muted = false;
    a.src = url;
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
    const a = player();
    a.onended = a.onerror = null;
    a.muted = false;
    a.src = url;
    a.playbackRate = 1;
    current = a;
    pending = () => {
      URL.revokeObjectURL(url);
      resolve();
    };
    a.onended = finish;
    a.play().catch(finish);
  });
}
