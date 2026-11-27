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
const SILENT = "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQxAADB8AhSmxhIIEVCSiJrDCQBTcu3UrAIwUdkRgQbFAZC1CQEwTJ9mjRvBA4UOLD8nKVOWfh+UlK3z/177OXrfOdKl7pyn3Xf//WreyTRUoAWgBgkOAGbZHBgG1OF6zM82DWbZaUmMBptgQhGjsyYqc9ae9XFz280948NMBWInljyzsNRFLPWdnZGWrddDsjK1unuSrVN9jJsK8KuQtQCtMBjCEtImISdNKJOopIpBFpNSMbIHCSRpRR5iakjTiyzLhchUUBwCgyKiweBv/7UsQbg8isVNoMPMjAAAA0gAAABEVFGmgqK////9bP/6XCykxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq";
let shared: HTMLAudioElement | null = null;
function player(): HTMLAudioElement {
  if (!shared) shared = new Audio();
  return shared;
}
function unlock() {
  const a = player();
  if (a.src) return;
  a.src = SILENT;
  a.play().catch(() => {});
}
document.addEventListener("pointerdown", unlock, { once: true, capture: true });

function playUrl(url: string, text: string, rate: number): Promise<void> {
  return new Promise((resolve) => {
    const a = player();
    a.onended = a.onerror = null;
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
