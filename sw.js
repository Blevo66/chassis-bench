// Offline cache: the app shell is stored on install, everything else (fonts) is cached the first time it loads.
const CACHE = 'chassis-bench-v9';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-180-v2.png', 'icon-192-v2.png', 'icon-512-v2.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // Pages (the bench, the measuring guide): try the network first so a new version shows on the next open, fall back to the cached copy offline.
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request, { cache: 'no-store' }).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request.url.split('#')[0].split('?')[0], copy)); return res; }).catch(() => caches.match(e.request, { ignoreSearch: true }).then(hit => hit || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => {
    const net = fetch(e.request).then(res => { if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return res; }).catch(() => hit);
    return hit || net;
  }));
});
