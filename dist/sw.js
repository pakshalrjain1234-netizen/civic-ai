// Only this explicit, same-origin frontend shell is cached. Never AI or user data.
const CACHE = 'civiceye-shell-development';
const SHELL = ['/', '/index.html', '/style.css', '/additions.css', '/favicon.svg',
  '/config.js', '/vision-env.js', '/app.js', '/features.js', '/live-scan.js', '/motion-scan.js',
  '/vision-backend.js', '/local-workflow.js', '/pwa.js', '/manifest.webmanifest',
  '/icons/icon-192.png', '/icons/icon-512.png', '/icons/maskable-192.png', '/icons/maskable-512.png'];
const STATIC = new Set(SHELL);
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
  // Activate on the next navigation after existing clients close; avoid mixed versions.
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(key => key.startsWith('civiceye-shell-') && key !== CACHE)
    .map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin ||
      ['/detect', '/health'].includes(url.pathname) || url.pathname.startsWith('/api/')) return;
  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(() => caches.open(CACHE).then(cache => cache.match('/index.html'))));
    return;
  }
  if (!STATIC.has(url.pathname) || url.search) return;
  event.respondWith(caches.open(CACHE).then(async cache => (await cache.match(url.pathname)) || fetch(request)));
});
