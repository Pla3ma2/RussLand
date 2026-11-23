type Handler = (root: HTMLElement, ...params: string[]) => void | Promise<void>;

const routes: { re: RegExp; h: Handler }[] = [];
let root: HTMLElement;

export function route(pattern: string, h: Handler) {
  const re = new RegExp(`^${pattern.replace(/:[a-z]+/g, "([^/]+)")}$`);
  routes.push({ re, h });
}

export function navigate(path: string) {
  if (location.hash.slice(2) === path) resolve();
  else location.hash = `#/${path}`;
}

async function resolve() {
  const path = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  for (const r of routes) {
    const m = path.match(r.re);
    if (m) {
      window.scrollTo({ top: 0 });
      try {
        await r.h(root, ...m.slice(1));
      } catch (e) {
        root.innerHTML = `<p class="error">Oups, une erreur : ${String(e)}</p>`;
      }
      return;
    }
  }
  navigate("");
}

export function startRouter(el: HTMLElement) {
  root = el;
  window.addEventListener("hashchange", resolve);
  resolve();
}
