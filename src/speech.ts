import type { Model } from "vosk-browser";

const MODEL_URL = "./models/vosk-ru.tar.gz";

/** Запись с микрофона в «сырые» сэмплы: из них делаем и WAV для прослушивания, и вход для Vosk. */
export class Recorder {
  private ctx: AudioContext | null = null;
  private stream: MediaStream | null = null;
  private node: ScriptProcessorNode | null = null;
  private chunks: Float32Array[] = [];

  get active() {
    return this.ctx !== null;
  }

  async start() {
    this.chunks = [];
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
    });
    this.ctx = new AudioContext();
    const src = this.ctx.createMediaStreamSource(this.stream);
    this.node = this.ctx.createScriptProcessor(4096, 1, 1);
    this.node.onaudioprocess = (e) => {
      this.chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    src.connect(this.node);
    this.node.connect(this.ctx.destination);
  }

  async stop(): Promise<{ samples: Float32Array; sampleRate: number }> {
    const sampleRate = this.ctx?.sampleRate ?? 48000;
    this.node?.disconnect();
    this.stream?.getTracks().forEach((t) => t.stop());
    await this.ctx?.close();
    this.ctx = null;
    const len = this.chunks.reduce((n, c) => n + c.length, 0);
    const samples = new Float32Array(len);
    let off = 0;
    for (const c of this.chunks) {
      samples.set(c, off);
      off += c.length;
    }
    return { samples, sampleRate };
  }
}

export function toWav(samples: Float32Array, sampleRate: number): Blob {
  const buf = new ArrayBuffer(44 + samples.length * 2);
  const v = new DataView(buf);
  const str = (o: number, s: string) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
  str(0, "RIFF");
  v.setUint32(4, 36 + samples.length * 2, true);
  str(8, "WAVE");
  str(12, "fmt ");
  v.setUint32(16, 16, true);
  v.setUint16(20, 1, true);
  v.setUint16(22, 1, true);
  v.setUint32(24, sampleRate, true);
  v.setUint32(28, sampleRate * 2, true);
  v.setUint16(32, 2, true);
  v.setUint16(34, 16, true);
  str(36, "data");
  v.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([buf], { type: "audio/wav" });
}

/* ---------- Распознавание речи (Vosk, офлайн) ---------- */

let modelPromise: Promise<Model> | null = null;

export async function voskAvailable(): Promise<boolean> {
  try {
    const r = await fetch(MODEL_URL, { method: "HEAD" });
    // dev-сервер на отсутствующий файл отдаёт index.html — его не считаем моделью
    return r.ok && !(r.headers.get("content-type") ?? "").includes("text/html");
  } catch {
    return false;
  }
}

export function loadVosk(): Promise<Model> {
  if (!modelPromise) {
    modelPromise = import("vosk-browser").then((v) => v.createModel(MODEL_URL));
    modelPromise.catch(() => (modelPromise = null));
  }
  return modelPromise;
}

export async function recognize(samples: Float32Array, sampleRate: number, grammar: string[]): Promise<string> {
  const model = await loadVosk();
  const rec = new model.KaldiRecognizer(sampleRate, JSON.stringify(grammar));
  return new Promise((resolve) => {
    const parts: string[] = [];
    const done = () => {
      rec.remove();
      resolve(parts.join(" ").trim());
    };
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      done();
    };
    const hardTimeout = setTimeout(finish, 8000);
    let debounce: ReturnType<typeof setTimeout> | undefined;
    // промежуточные «result» бывают на паузах; финальный приходит после retrieveFinalResult
    rec.on("result", (m) => {
      const text = (m as { result?: { text?: string } }).result?.text;
      if (text) parts.push(text);
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        clearTimeout(hardTimeout);
        finish();
      }, 900);
    });
    const step = 4096;
    for (let i = 0; i < samples.length; i += step) {
      rec.acceptWaveformFloat(samples.subarray(i, i + step), sampleRate);
    }
    rec.retrieveFinalResult();
  });
}

export const normalize = (s: string) =>
  s.toLowerCase().replace(/ё/g, "е").replace(/[^а-я\s]/g, "").replace(/\s+/g, " ").trim();
