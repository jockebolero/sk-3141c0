/*
 * Offline-stöd för skiftschemat.
 * Gjord av J. Stork.
 *
 * Sidan hämtas alltid från nätet när det går, så att schemat är färskt.
 * Varje hämtad fil sparas också i telefonen. Utan nät visas den sparade
 * kopian i stället, så att schemat går att läsa även vid dålig täckning.
 *
 * Byt namn på CACHE (v1, v2, ...) om gamla sparade filer ska rensas bort.
 */

const CACHE = "skiftschema-v1";

// Det som behövs för att sidan ska fungera utan nät. Sparas direkt vid första besöket.
const FILES = [
  "./",
  "index.html",
  "style.css",
  "script.js",
  "data.js",
  "manifest.webmanifest",
  "favicon.png",
  "apple-touch-icon.png",
  "icon-192.png",
  "typsnitt/ibm-plex-sans-400.woff2",
  "typsnitt/ibm-plex-sans-500.woff2",
  "typsnitt/ibm-plex-sans-600.woff2",
  "typsnitt/ibm-plex-sans-condensed-600.woff2",
  "typsnitt/ibm-plex-sans-condensed-700.woff2"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  // Rensa sparade filer från äldre versioner.
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(names.filter(name => name !== CACHE).map(name => caches.delete(name))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== location.origin) return;

  event.respondWith(
    fetch(request)
      .then(response => {
        // Spara en kopia av det som hämtades, till nästa gång nätet saknas.
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put(request, copy));
        }
        return response;
      })
      .catch(() =>
        // Inget nät: använd den sparade kopian. Adressens ?-del och #-del spelar ingen roll.
        caches.match(request, { ignoreSearch: true })
          .then(saved => saved || (request.mode === "navigate" ? caches.match("index.html") : undefined))
          .then(saved => saved || Response.error())
      )
  );
});
