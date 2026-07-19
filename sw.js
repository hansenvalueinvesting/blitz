// Blitz service worker.
//
// The whole point of this file is to fix the "installed app never updates"
// problem: without a service worker, an installed PWA leans on the browser's
// HTTP cache for index.html and often serves a stale copy for a long time.
//
// Strategy:
//   • The app shell (the HTML document) and directory.json are fetched
//     NETWORK-FIRST — when you're online you always get the latest version,
//     and the cache is only a fallback for when you're offline.
//   • Question files and icons are STALE-WHILE-REVALIDATE — served instantly
//     from cache, then refreshed in the background. They rarely change, so
//     this keeps the feed fast and makes seen questions work offline.
//
// Because the shell is network-first, there is nothing to bump on each deploy:
// a new index.html shows up on the next launch automatically. CACHE is just
// the bucket name; bump it only if you ever need to nuke every client's cache.

const CACHE = 'blitz-v1';

self.addEventListener('install', () => {
  // Take over as soon as we're installed instead of waiting for a reload.
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    // Drop any older cache buckets so a CACHE bump wipes stale content.
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // don't touch cross-origin

  // The app shell + directory: always try the network first so edits sync.
  const isShell =
    req.mode === 'navigate' ||
    url.pathname.endsWith('/') ||
    url.pathname.endsWith('index.html') ||
    url.pathname.endsWith('directory.json');

  e.respondWith(isShell ? networkFirst(req) : staleWhileRevalidate(req));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(req, { cache: 'no-store' });
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(req, { ignoreSearch: true });
    if (cached) return cached;
    throw err;
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const network = fetch(req)
    .then(res => { if (res && res.ok) cache.put(req, res.clone()); return res; })
    .catch(() => cached);
  return cached || network;
}
