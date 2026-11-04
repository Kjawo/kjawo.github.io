/* Cypr 2026 — offline shell. Build injects the cache version and asset list. */
"use strict";

// Updated by cypr2026/_src/build.py on every build.
const CACHE_VERSION = "cypr-2026-v1-1.0.0-47c9c68d63";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./styles.css?v=47c9c68d63",
  "./app.js?v=47c9c68d63",
  "./manifest.json?v=47c9c68d63",
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
          .filter((key) => key.startsWith("cypr-2026-v1-") && key !== CACHE_VERSION)
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

  if (request.mode === "navigate") {
    event.respondWith(
      caches.match("./index.html", { ignoreSearch: true })
        .then((cached) => cached || fetch(request))
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  event.respondWith(
    caches.match(request)
      .then((cached) => {
        if (cached) return cached;
        return caches.match(request, { ignoreSearch: true }).then((searchless) => {
          if (searchless) return searchless;
          return fetch(request).then((response) => {
            if (!response || response.status !== 200 || response.type !== "basic") return response;
            const copy = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
            return response;
          });
        });
      })
  );
});
