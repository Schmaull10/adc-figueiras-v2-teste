const CACHE='adc-figueiras-v2-preview-3';
const ASSETS=[
  './','./index.html','./styles.css','./app.js','./manifest.webmanifest',
  './assets/adc-figueiras-emblema.png','./assets/icon-192.png','./assets/icon-512.png','./assets/apple-touch-icon.png',
  './data/competition.json'
];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);
  if(url.pathname.endsWith('/data/competition.json')){
    event.respondWith(fetch(event.request).then(response=>{
      const copy=response.clone();caches.open(CACHE).then(cache=>cache.put('./data/competition.json',copy));return response;
    }).catch(()=>caches.match('./data/competition.json')));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
