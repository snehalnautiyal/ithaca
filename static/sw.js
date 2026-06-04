const CACHE_NAME = 'ithaca-v1';
const PRECACHE = [
  '/',
  '/static/style.css',
  '/static/app.js',
  '/static/js/chat.js',
  '/static/js/sessions.js',
  '/static/js/markdown.js',
  '/static/js/settings.js',
  '/static/js/memory.js',
  '/static/js/documents.js',
  '/static/js/agent.js',
  '/static/js/research.js',
  '/static/js/compare.js',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // Network-first for API, cache-first for static
  if (e.request.url.includes('/api/')) return;
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
