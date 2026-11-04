/* Cypr 2026 — offline shell. Build injects the cache version and asset list. */
"use strict";

// Updated by cypr2026/_src/build.py on every build.
const CACHE_VERSION = "cypr-2026-1.0.0-5fc2f18ce4";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./styles.min.css?v=5fc2f18ce4",
  "./app.min.js?v=5fc2f18ce4",
  "./manifest.json?v=5fc2f18ce4",
  "./data/Cypr_2026_zrodlo_prawdy.json",
  "./assets/fonts/inter-400-ext.woff2",
  "./assets/fonts/inter-400.woff2",
  "./assets/fonts/inter-500-ext.woff2",
  "./assets/fonts/inter-500.woff2",
  "./assets/fonts/inter-600-ext.woff2",
  "./assets/fonts/inter-600.woff2",
  "./assets/fonts/newsreader-500-ext.woff2",
  "./assets/fonts/newsreader-500.woff2",
  "./assets/fonts/newsreader-600-ext.woff2",
  "./assets/fonts/newsreader-600.woff2",
  "./assets/icons/favicon.svg",
  "./assets/icons/icon-180.png",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./assets/vendor/leaflet/leaflet.css",
  "./assets/vendor/leaflet/leaflet.js",
  "./assets/photos/hero/hero-480.avif",
  "./assets/photos/hero/hero-480.webp",
  "./assets/photos/hero/hero-800.avif",
  "./assets/photos/hero/hero-800.webp",
  "./assets/photos/hero/hero-800.jpg",
  "./assets/photos/day-01/day-01-480.avif",
  "./assets/photos/day-01/day-01-480.webp",
  "./assets/photos/day-01/day-01-800.avif",
  "./assets/photos/day-01/day-01-800.webp",
  "./assets/photos/day-01/day-01-800.jpg",
  "./assets/photos/day-02/day-02-480.avif",
  "./assets/photos/day-02/day-02-480.webp",
  "./assets/photos/day-02/day-02-800.avif",
  "./assets/photos/day-02/day-02-800.webp",
  "./assets/photos/day-02/day-02-800.jpg",
  "./assets/photos/day-03/day-03-480.avif",
  "./assets/photos/day-03/day-03-480.webp",
  "./assets/photos/day-03/day-03-800.avif",
  "./assets/photos/day-03/day-03-800.webp",
  "./assets/photos/day-03/day-03-800.jpg",
  "./assets/photos/day-04/day-04-480.avif",
  "./assets/photos/day-04/day-04-480.webp",
  "./assets/photos/day-04/day-04-800.avif",
  "./assets/photos/day-04/day-04-800.webp",
  "./assets/photos/day-04/day-04-800.jpg",
  "./assets/photos/day-05/day-05-480.avif",
  "./assets/photos/day-05/day-05-480.webp",
  "./assets/photos/day-05/day-05-800.avif",
  "./assets/photos/day-05/day-05-800.webp",
  "./assets/photos/day-05/day-05-800.jpg",
  "./assets/photos/day-06/day-06-480.avif",
  "./assets/photos/day-06/day-06-480.webp",
  "./assets/photos/day-06/day-06-800.avif",
  "./assets/photos/day-06/day-06-800.webp",
  "./assets/photos/day-06/day-06-800.jpg",
  "./assets/photos/day-07/day-07-480.avif",
  "./assets/photos/day-07/day-07-480.webp",
  "./assets/photos/day-07/day-07-800.avif",
  "./assets/photos/day-07/day-07-800.webp",
  "./assets/photos/day-07/day-07-800.jpg",
  "./cal/cypr2026-2026-11-07.ics",
  "./cal/cypr2026-2026-11-08.ics",
  "./cal/cypr2026-2026-11-09.ics",
  "./cal/cypr2026-2026-11-10.ics",
  "./cal/cypr2026-2026-11-11.ics",
  "./cal/cypr2026-2026-11-12.ics",
  "./cal/cypr2026-2026-11-13.ics",
  "./cal/cypr2026-caly-wyjazd.ics",
  "./cypr2026-print.pdf",
];

const OSM_HOSTS = new Set(["tile.openstreetmap.org", "a.tile.openstreetmap.org", "b.tile.openstreetmap.org", "c.tile.openstreetmap.org"]);

function isMapTile(url) {
  if (OSM_HOSTS.has(url.hostname)) return true;
  return url.hostname.endsWith(".openstreetmap.org") && url.pathname.includes("/tiles/");
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key.startsWith("cypr-2026-") && !key.startsWith("cypr-2026-v1-") && key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // Map tiles are deliberately network-only. They are not cached and must
  // never be presented as an offline navigation aid.
  if (isMapTile(url)) return;

  // Do not intercept third-party requests (except the map tiles handled
  // above). The page has no trackers or external fonts.
  if (url.origin !== self.location.origin) return;

  // HTML is network-first so a fresh deploy is visible immediately; the
  // cached document remains the offline fallback.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put("./index.html", copy));
          }
          return response;
        })
        .catch(() => caches.match("./index.html", { ignoreSearch: true }).then((cached) => cached || caches.match("./")))
    );
    return;
  }

  event.respondWith(
    caches.match(request, { ignoreSearch: true })
      .then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (!response || response.status !== 200 || response.type !== "basic") return response;
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
          return response;
        });
      })
  );
});
