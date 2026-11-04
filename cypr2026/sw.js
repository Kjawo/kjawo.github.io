/* Cypr 2026 — offline shell. Build injects the cache version and asset list. */
"use strict";

// Updated by cypr2026/_src/build.py on every build.
const CACHE_VERSION = "cypr-2026-1.2.2-acbaa37acb";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./styles.min.css?v=acbaa37acb",
  "./app.min.js?v=acbaa37acb",
  "./manifest.json?v=acbaa37acb",
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
  "./assets/photos/hero/hero-800.jpeg",
  "./assets/photos/strip-01/strip-01-480.avif",
  "./assets/photos/strip-01/strip-01-480.webp",
  "./assets/photos/strip-02/strip-02-480.avif",
  "./assets/photos/strip-02/strip-02-480.webp",
  "./assets/photos/strip-03/strip-03-480.avif",
  "./assets/photos/strip-03/strip-03-480.webp",
  "./assets/photos/day-01-b/day-01-b-480.avif",
  "./assets/photos/day-01-b/day-01-b-480.webp",
  "./assets/photos/day-01-b/day-01-b-800.avif",
  "./assets/photos/day-01-b/day-01-b-800.webp",
  "./assets/photos/day-01-b/day-01-b-800.jpg",
  "./assets/photos/day-01/day-01-480.avif",
  "./assets/photos/day-01/day-01-480.webp",
  "./assets/photos/day-01-c/day-01-c-480.avif",
  "./assets/photos/day-01-c/day-01-c-480.webp",
  "./assets/photos/day-01-d/day-01-d-480.avif",
  "./assets/photos/day-01-d/day-01-d-480.webp",
  "./assets/photos/day-02/day-02-480.avif",
  "./assets/photos/day-02/day-02-480.webp",
  "./assets/photos/day-02/day-02-800.avif",
  "./assets/photos/day-02/day-02-800.webp",
  "./assets/photos/day-02/day-02-800.jpg",
  "./assets/photos/day-02-b/day-02-b-480.avif",
  "./assets/photos/day-02-b/day-02-b-480.webp",
  "./assets/photos/day-02-c/day-02-c-480.avif",
  "./assets/photos/day-02-c/day-02-c-480.webp",
  "./assets/photos/day-02-d/day-02-d-480.avif",
  "./assets/photos/day-02-d/day-02-d-480.webp",
  "./assets/photos/day-03/day-03-480.avif",
  "./assets/photos/day-03/day-03-480.webp",
  "./assets/photos/day-03/day-03-800.avif",
  "./assets/photos/day-03/day-03-800.webp",
  "./assets/photos/day-03/day-03-800.jpeg",
  "./assets/photos/day-03-b/day-03-b-480.avif",
  "./assets/photos/day-03-b/day-03-b-480.webp",
  "./assets/photos/day-03-c/day-03-c-480.avif",
  "./assets/photos/day-03-c/day-03-c-480.webp",
  "./assets/photos/day-03-d/day-03-d-480.avif",
  "./assets/photos/day-03-d/day-03-d-480.webp",
  "./assets/photos/day-04/day-04-480.avif",
  "./assets/photos/day-04/day-04-480.webp",
  "./assets/photos/day-04/day-04-800.avif",
  "./assets/photos/day-04/day-04-800.webp",
  "./assets/photos/day-04/day-04-800.jpg",
  "./assets/photos/day-04-b/day-04-b-480.avif",
  "./assets/photos/day-04-b/day-04-b-480.webp",
  "./assets/photos/day-04-c/day-04-c-480.avif",
  "./assets/photos/day-04-c/day-04-c-480.webp",
  "./assets/photos/day-04-d/day-04-d-480.avif",
  "./assets/photos/day-04-d/day-04-d-480.webp",
  "./assets/photos/day-05/day-05-480.avif",
  "./assets/photos/day-05/day-05-480.webp",
  "./assets/photos/day-05/day-05-800.avif",
  "./assets/photos/day-05/day-05-800.webp",
  "./assets/photos/day-05/day-05-800.jpg",
  "./assets/photos/day-05-b/day-05-b-480.avif",
  "./assets/photos/day-05-b/day-05-b-480.webp",
  "./assets/photos/day-05-c/day-05-c-480.avif",
  "./assets/photos/day-05-c/day-05-c-480.webp",
  "./assets/photos/day-05-d/day-05-d-480.avif",
  "./assets/photos/day-05-d/day-05-d-480.webp",
  "./assets/photos/day-06-b/day-06-b-480.avif",
  "./assets/photos/day-06-b/day-06-b-480.webp",
  "./assets/photos/day-06-b/day-06-b-800.avif",
  "./assets/photos/day-06-b/day-06-b-800.webp",
  "./assets/photos/day-06-b/day-06-b-800.jpg",
  "./assets/photos/day-06/day-06-480.avif",
  "./assets/photos/day-06/day-06-480.webp",
  "./assets/photos/day-06-c/day-06-c-480.avif",
  "./assets/photos/day-06-c/day-06-c-480.webp",
  "./assets/photos/day-06-d/day-06-d-480.avif",
  "./assets/photos/day-06-d/day-06-d-480.webp",
  "./assets/photos/day-07/day-07-480.avif",
  "./assets/photos/day-07/day-07-480.webp",
  "./assets/photos/day-07/day-07-800.avif",
  "./assets/photos/day-07/day-07-800.webp",
  "./assets/photos/day-07/day-07-800.jpg",
  "./assets/photos/day-07-b/day-07-b-480.avif",
  "./assets/photos/day-07-b/day-07-b-480.webp",
  "./assets/photos/day-07-c/day-07-c-480.avif",
  "./assets/photos/day-07-c/day-07-c-480.webp",
  "./assets/photos/place-baths/place-baths-480.avif",
  "./assets/photos/place-baths/place-baths-480.webp",
  "./assets/photos/place-baths/place-baths-800.avif",
  "./assets/photos/place-baths/place-baths-800.webp",
  "./assets/photos/place-baths/place-baths-800.jpg",
  "./assets/photos/place-baths-b/place-baths-b-480.avif",
  "./assets/photos/place-baths-b/place-baths-b-480.webp",
  "./assets/photos/place-baths-c/place-baths-c-480.avif",
  "./assets/photos/place-baths-c/place-baths-c-480.webp",
  "./assets/photos/place-edro/place-edro-480.avif",
  "./assets/photos/place-edro/place-edro-480.webp",
  "./assets/photos/place-edro/place-edro-800.avif",
  "./assets/photos/place-edro/place-edro-800.webp",
  "./assets/photos/place-edro/place-edro-800.jpg",
  "./assets/photos/place-edro-b/place-edro-b-480.avif",
  "./assets/photos/place-edro-b/place-edro-b-480.webp",
  "./assets/photos/place-edro-c/place-edro-c-480.avif",
  "./assets/photos/place-edro-c/place-edro-c-480.webp",
  "./assets/photos/place-faros/place-faros-480.avif",
  "./assets/photos/place-faros/place-faros-480.webp",
  "./assets/photos/place-faros/place-faros-800.avif",
  "./assets/photos/place-faros/place-faros-800.webp",
  "./assets/photos/place-faros/place-faros-800.jpg",
  "./assets/photos/place-faros-b/place-faros-b-480.avif",
  "./assets/photos/place-faros-b/place-faros-b-480.webp",
  "./assets/photos/place-faros-c/place-faros-c-480.avif",
  "./assets/photos/place-faros-c/place-faros-c-480.webp",
  "./assets/photos/place-harbour/place-harbour-480.avif",
  "./assets/photos/place-harbour/place-harbour-480.webp",
  "./assets/photos/place-harbour/place-harbour-800.avif",
  "./assets/photos/place-harbour/place-harbour-800.webp",
  "./assets/photos/place-harbour/place-harbour-800.jpg",
  "./assets/photos/place-harbour-b/place-harbour-b-480.avif",
  "./assets/photos/place-harbour-b/place-harbour-b-480.webp",
  "./assets/photos/place-harbour-c/place-harbour-c-480.avif",
  "./assets/photos/place-harbour-c/place-harbour-c-480.webp",
  "./assets/photos/place-harbour-d/place-harbour-d-480.avif",
  "./assets/photos/place-harbour-d/place-harbour-d-480.webp",
  "./assets/photos/place-omodos/place-omodos-480.avif",
  "./assets/photos/place-omodos/place-omodos-480.webp",
  "./assets/photos/place-omodos/place-omodos-800.avif",
  "./assets/photos/place-omodos/place-omodos-800.webp",
  "./assets/photos/place-omodos/place-omodos-800.jpg",
  "./assets/photos/place-omodos-b/place-omodos-b-480.avif",
  "./assets/photos/place-omodos-b/place-omodos-b-480.webp",
  "./assets/photos/place-omodos-c/place-omodos-c-480.avif",
  "./assets/photos/place-omodos-c/place-omodos-c-480.webp",
  "./assets/photos/place-omodos-d/place-omodos-d-480.avif",
  "./assets/photos/place-omodos-d/place-omodos-d-480.webp",
  "./assets/photos/place-palaipafos/place-palaipafos-480.avif",
  "./assets/photos/place-palaipafos/place-palaipafos-480.webp",
  "./assets/photos/place-palaipafos/place-palaipafos-800.avif",
  "./assets/photos/place-palaipafos/place-palaipafos-800.webp",
  "./assets/photos/place-palaipafos/place-palaipafos-800.jpg",
  "./assets/photos/place-palaipafos-b/place-palaipafos-b-480.avif",
  "./assets/photos/place-palaipafos-b/place-palaipafos-b-480.webp",
  "./assets/photos/place-palaipafos-c/place-palaipafos-c-480.avif",
  "./assets/photos/place-palaipafos-c/place-palaipafos-c-480.webp",
  "./assets/photos/place-park/place-park-480.avif",
  "./assets/photos/place-park/place-park-480.webp",
  "./assets/photos/place-park/place-park-800.avif",
  "./assets/photos/place-park/place-park-800.webp",
  "./assets/photos/place-park/place-park-800.jpg",
  "./assets/photos/place-park-b/place-park-b-480.avif",
  "./assets/photos/place-park-b/place-park-b-480.webp",
  "./assets/photos/place-park-c/place-park-c-480.avif",
  "./assets/photos/place-park-c/place-park-c-480.webp",
  "./assets/photos/place-park-d/place-park-d-480.avif",
  "./assets/photos/place-park-d/place-park-d-480.webp",
  "./assets/photos/place-petra/place-petra-480.avif",
  "./assets/photos/place-petra/place-petra-480.webp",
  "./assets/photos/place-petra/place-petra-800.avif",
  "./assets/photos/place-petra/place-petra-800.webp",
  "./assets/photos/place-petra/place-petra-800.jpg",
  "./assets/photos/place-petra-b/place-petra-b-480.avif",
  "./assets/photos/place-petra-b/place-petra-b-480.webp",
  "./assets/photos/place-petra-c/place-petra-c-480.avif",
  "./assets/photos/place-petra-c/place-petra-c-480.webp",
  "./assets/photos/place-tombs/place-tombs-480.avif",
  "./assets/photos/place-tombs/place-tombs-480.webp",
  "./assets/photos/place-tombs/place-tombs-800.avif",
  "./assets/photos/place-tombs/place-tombs-800.webp",
  "./assets/photos/place-tombs/place-tombs-800.jpg",
  "./assets/photos/place-tombs-b/place-tombs-b-480.avif",
  "./assets/photos/place-tombs-b/place-tombs-b-480.webp",
  "./assets/photos/place-tombs-c/place-tombs-c-480.avif",
  "./assets/photos/place-tombs-c/place-tombs-c-480.webp",
  "./assets/photos/place-tombs-d/place-tombs-d-480.avif",
  "./assets/photos/place-tombs-d/place-tombs-d-480.webp",
  "./assets/photos/route-aphrodite/route-aphrodite-480.avif",
  "./assets/photos/route-aphrodite/route-aphrodite-480.webp",
  "./assets/photos/route-aphrodite/route-aphrodite-800.avif",
  "./assets/photos/route-aphrodite/route-aphrodite-800.webp",
  "./assets/photos/route-aphrodite/route-aphrodite-800.jpeg",
  "./assets/photos/route-aphrodite-b/route-aphrodite-b-480.avif",
  "./assets/photos/route-aphrodite-b/route-aphrodite-b-480.webp",
  "./assets/photos/route-aphrodite-c/route-aphrodite-c-480.avif",
  "./assets/photos/route-aphrodite-c/route-aphrodite-c-480.webp",
  "./assets/photos/route-artemis/route-artemis-480.avif",
  "./assets/photos/route-artemis/route-artemis-480.webp",
  "./assets/photos/route-artemis/route-artemis-800.avif",
  "./assets/photos/route-artemis/route-artemis-800.webp",
  "./assets/photos/route-artemis/route-artemis-800.jpg",
  "./assets/photos/route-artemis-b/route-artemis-b-480.avif",
  "./assets/photos/route-artemis-b/route-artemis-b-480.webp",
  "./assets/photos/route-artemis-c/route-artemis-c-480.avif",
  "./assets/photos/route-artemis-c/route-artemis-c-480.webp",
  "./assets/photos/route-vouni/route-vouni-480.avif",
  "./assets/photos/route-vouni/route-vouni-480.webp",
  "./assets/photos/route-vouni/route-vouni-800.avif",
  "./assets/photos/route-vouni/route-vouni-800.webp",
  "./assets/photos/route-vouni/route-vouni-800.jpg",
  "./assets/photos/route-vouni-b/route-vouni-b-480.avif",
  "./assets/photos/route-vouni-b/route-vouni-b-480.webp",
  "./assets/photos/route-vouni-c/route-vouni-c-480.avif",
  "./assets/photos/route-vouni-c/route-vouni-c-480.webp",
  "./assets/photos/hero/hero-1280.avif",
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
