/* Cypr 2026 — offline shell. Build injects the cache version and asset list. */
"use strict";

// Updated by cypr2026/_src/build.py on every build.
const CACHE_VERSION = "cypr-2026-template";
const PRECACHE_URLS = [];

const OSM_HOSTS = new Set(["tile.openstreetmap.org", "a.tile.openstreetmap.org", "b.tile.openstreetmap.org", "c.tile.openstreetmap.org"]);

function isMapTile(url) {
  if (OSM_HOSTS.has(url.hostname)) return true;
  return url.hostname.endsWith(".openstreetmap.org") && url.pathname.includes("/tiles/");
}

async function withGpxType(response, url) {
  if (!response || !new URL(url, self.location).pathname.endsWith('.gpx')) return response;
  const headers = new Headers(response.headers);
  headers.set('Content-Type', 'application/gpx+xml');
  return new Response(await response.blob(), {status:response.status, statusText:response.statusText, headers});
}

async function savePlan(cache) {
  await cache.addAll(PRECACHE_URLS);
  for (const url of PRECACHE_URLS.filter(url => url.endsWith('.gpx'))) {
    await cache.put(url, await withGpxType(await cache.match(url), url));
  }
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(savePlan)
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

self.addEventListener("message", (event) => {
  if (!event.data || !["OFFLINE_STATUS", "SAVE_PLAN"].includes(event.data.type) || !event.ports[0]) return;
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_VERSION);
    if (event.data.type === "SAVE_PLAN") {
      try { await savePlan(cache); } catch (error) { /* Report actual completeness below. */ }
    }
    const present = await Promise.all(PRECACHE_URLS.map((url) => cache.match(url)));
    event.ports[0].postMessage({
      version: CACHE_VERSION,
      ready: present.every(Boolean),
      saved: present.filter(Boolean).length,
      total: PRECACHE_URLS.length
    });
  })());
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
  if (request.mode === "navigate" && !/\.(gpx|pdf)$/.test(url.pathname)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put("./index.html", copy));
          }
          return response;
        })
        .catch(() => caches.open(CACHE_VERSION).then(async (cache) => await cache.match(request, {ignoreSearch:true}) || cache.match("./index.html", {ignoreSearch:true})))
    );
    return;
  }

  event.respondWith(
    caches.open(CACHE_VERSION).then((cache) => cache.match(request, { ignoreSearch: true }))
      .then((cached) => {
        if (cached) return withGpxType(cached, url.href);
        return fetch(request).then(response => withGpxType(response, url.href)).then((response) => {
          if (!response || response.status !== 200 || !['basic','default'].includes(response.type)) return response;
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
          return response;
        }).catch(async (error) => {
          if (url.pathname.includes('/assets/photos/') && /-\d+\.(avif|webp|jpe?g)$/.test(url.pathname)) {
            const small = new URL(url);
            small.pathname = small.pathname.replace(/-\d+\.(avif|webp|jpe?g)$/, '-480.$1');
            const fallback = await caches.open(CACHE_VERSION).then(cache => cache.match(small.href));
            if (fallback) return fallback;
          }
          throw error;
        });
      })
  );
});
