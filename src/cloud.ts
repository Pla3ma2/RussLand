/**
 * Вход по логину (без пароля) и сохранение прогресса на сервере.
 * Один логин = один прогресс: войди под тем же логином на другом телефоне — и продолжишь с того же места.
 */
import { SUPABASE_KEY, SUPABASE_URL } from "./cloud-config";
import { onSave, progress, replaceProgress, type Progress } from "./state";
import { esc } from "./ui";

const LOGIN_KEY = "russland-login";
export const cloudEnabled = () => !!SUPABASE_URL && !!SUPABASE_KEY;
/* Логин запоминается на устройстве (localStorage + cookie на 10 лет как запасной вариант),
   поэтому входить нужно только один раз — дальше приложение открывается сразу. */
const cookieLogin = () => decodeURIComponent(document.cookie.match(/(?:^|; )russland_login=([^;]*)/)?.[1] ?? "");
export const currentLogin = () => localStorage.getItem(LOGIN_KEY) || cookieLogin();
function rememberLogin(login: string) {
  localStorage.setItem(LOGIN_KEY, login);
  document.cookie = `russland_login=${encodeURIComponent(login)}; max-age=${60 * 60 * 24 * 3650}; path=/; SameSite=Lax`;
  void navigator.storage?.persist?.(); // просим браузер не чистить данные сайта
}
function forgetLogin() {
  localStorage.removeItem(LOGIN_KEY);
  document.cookie = "russland_login=; max-age=0; path=/";
}
const norm = (s: string) => s.trim().toLowerCase().replace(/\s+/g, "-").slice(0, 32);

function api(path: string, init: RequestInit = {}) {
  return fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Content-Type": "application/json", ...(init.headers ?? {}) },
  });
}

async function pull(login: string): Promise<Progress | null> {
  const r = await api(`progress?login=eq.${encodeURIComponent(login)}&select=data`);
  if (!r.ok) throw new Error(`serveur ${r.status}`);
  const rows = (await r.json()) as { data: Progress }[];
  return rows[0]?.data ?? null;
}

async function push(login: string, data: Progress) {
  const r = await api("progress", {
    method: "POST",
    headers: { Prefer: "resolution=merge-duplicates" },
    body: JSON.stringify({ login, data, updated_at: new Date().toISOString() }),
  });
  if (!r.ok) throw new Error(`serveur ${r.status}`);
}

let timer: ReturnType<typeof setTimeout> | undefined;
let pending = false;
function schedulePush() {
  const login = currentLogin();
  if (!login) return;
  pending = true;
  clearTimeout(timer);
  timer = setTimeout(async () => {
    try {
      await push(login, progress());
      pending = false;
    } catch {
      setTimeout(schedulePush, 10000); // нет сети — попробуем позже
    }
  }, 1500);
}
// при закрытии страницы — отправить, что не успели
addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden" && pending && currentLogin()) {
    clearTimeout(timer);
    void push(currentLogin(), progress()).then(() => (pending = false), () => {});
  }
});

/** Перед запуском: если нужен вход — показываем экран логина; затем подтягиваем прогресс с сервера. */
export async function startCloud(app: HTMLElement): Promise<void> {
  if (!cloudEnabled()) return;
  onSave(schedulePush);
  const login = currentLogin();
  if (!login) return loginScreen(app);
  rememberLogin(login); // восстановить, если браузер почистил одно из хранилищ
  try {
    const remote = await pull(login);
    if (remote) replaceProgress(remote);
    else await push(login, progress());
  } catch {
    /* нет сети — работаем с тем, что есть, отправим позже */
  }
}

function loginScreen(app: HTMLElement): Promise<void> {
  return new Promise((resolve) => {
    app.innerHTML = `
      <div class="login">
        <div class="login-logo">Я</div>
        <h1>Russ<b>Land</b></h1>
        <p>Choisis un <b>pseudo</b>. Ta progression sera sauvegardée avec ce pseudo : tu pourras la retrouver sur n'importe quel téléphone.</p>
        <form id="lf">
          <input id="lg" class="field" placeholder="ton pseudo (ex. : julie-lyon)" autocomplete="username" autocapitalize="off" maxlength="32" required>
          <button class="primary" type="submit">Commencer</button>
        </form>
        <p class="hint" id="lmsg">Déjà un compte ? Entre le même pseudo.<br>Pas de mot de passe : choisis un pseudo que personne d'autre n'utilisera.</p>
      </div>`;
    const input = app.querySelector<HTMLInputElement>("#lg")!;
    const msg = app.querySelector<HTMLElement>("#lmsg")!;
    input.focus();
    app.querySelector<HTMLFormElement>("#lf")!.onsubmit = async (e) => {
      e.preventDefault();
      const login = norm(input.value);
      if (login.length < 3) return void (msg.textContent = "Au moins 3 lettres, s'il te plaît.");
      msg.textContent = "Connexion…";
      try {
        const remote = await pull(login);
        if (remote) {
          replaceProgress(remote);
        } else {
          await push(login, progress()); // nouveau compte : on garde ce qui a déjà été fait sur ce téléphone
        }
        rememberLogin(login);
        resolve();
      } catch {
        msg.innerHTML = `Impossible de joindre le serveur. Vérifie ta connexion Internet et réessaie.`;
      }
    };
  });
}

export function logout() {
  if (!confirm(`Se déconnecter de « ${esc(currentLogin())} » ?`)) return;
  forgetLogin();
  localStorage.removeItem("russland-progress-v1");
  location.reload();
}
