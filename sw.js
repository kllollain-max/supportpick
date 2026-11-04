/* Offline notice only. Benefit facts and personal records are never cached here. */
'use strict';
const CACHE = 'supportpick-shell-__SHELL_HASH__';
const base = self.registration.scope;
const offline = new URL('offline.html', base).href;
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([
    offline, new URL('app-icon-192.png', base).href, new URL('app-icon-512.png', base).href
  ])).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(key => key.startsWith('supportpick-shell-') && key !== CACHE)
    .map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || event.request.mode !== 'navigate' || !event.request.url.startsWith(base)) return;
  event.respondWith(fetch(event.request).catch(async () => {
    const cache = await caches.open(CACHE), response = await cache.match(offline);
    return new Response(response ? await response.text() : '인터넷 연결을 확인하고 다시 열어 주세요.', {
      status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8', 'X-Robots-Tag': 'noindex', 'Cache-Control': 'no-store' }
    });
  }));
});
