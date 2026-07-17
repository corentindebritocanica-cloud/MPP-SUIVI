// CALIPER Pro CAM — Service Worker
// Cache-first pour le mode offline

const CACHE_NAME = 'caliper-pro-cam-v1';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.svg',
];

// Installation : mise en cache des assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Activation : nettoyage des anciens caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Fetch : cache-first, fallback réseau
self.addEventListener('fetch', event => {
  // Ne pas intercepter les requêtes caméra/gyroscope (APIs natives)
  if (event.request.url.includes('blob:') || event.request.url.includes('data:')) return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Mettre en cache les nouvelles ressources statiques
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      });
    }).catch(() => {
      // Offline fallback : retourner index.html
      return caches.match('./index.html');
    })
  );
});
