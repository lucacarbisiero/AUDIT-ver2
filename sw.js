/* Service Worker - Audit Energetico
   App-shell precache + runtime cache (Chart.js, datalabels, SheetJS da CDN).
   Bump CACHE quando aggiorni i file. */
const CACHE = "audit-cache-v1";
const SHELL = [
  "./",
  "./index.html",
  "./manifest.json",
  "./ateco_map.js",
  "./logo.png",
  "./icona-192.png",
  "./icona-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => Promise.allSettled(SHELL.map((u) => c.add(u)))).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // CDN (Chart.js / SheetJS): stale-while-revalidate -> offline dopo la prima volta
  if (url.hostname.includes("cdn.jsdelivr.net")) {
    e.respondWith(
      caches.open(CACHE).then(async (cache) => {
        const cached = await cache.match(req);
        const net = fetch(req).then((res) => { cache.put(req, res.clone()); return res; }).catch(() => cached);
        return cached || net;
      })
    );
    return;
  }

  // same-origin: cache-first con fallback rete
  if (url.origin === location.origin) {
    e.respondWith(
      caches.match(req).then((cached) =>
        cached || fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        }).catch(() => caches.match("./index.html"))
      )
    );
  }
});
