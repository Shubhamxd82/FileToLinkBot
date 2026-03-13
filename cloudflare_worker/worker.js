const SECRET = "YOUR_CF_SECRET_KEY";
const BACKEND = "https://your-app.koyeb.app";
addEventListener("fetch", e => e.respondWith(handle(e.request)));
async function handle(req) {
  const url = new URL(req.url);
  const p = url.pathname;
  if (p.startsWith("/stream/") || p.startsWith("/dl/") || p.startsWith("/watch/")) {
    return fetch(BACKEND + p, {headers: req.headers});
  }
  if (p === "/health") return new Response('{"ok":true}');
  return new Response("FileToLink CF Worker");
}
