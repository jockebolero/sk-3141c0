/*
 * Offline-stöd för skiftschemat.
 * Gjord av J. Stork.
 *
 * Sidan hämtas från nätet när det går, så att schemat är färskt.
 * Varje hämtad fil sparas också i telefonen. Utan nät, eller om nätet inte
 * svarar inom VANTA_PA_NATET, visas den sparade kopian i stället, så att
 * schemat går att läsa även vid dålig täckning.
 *
 * Byt namn på CACHE (v1, v2, ...) om gamla sparade filer ska rensas bort.
 */

const CACHE = "skiftschema-v1";

// Hur länge nätet får ta, i millisekunder, innan den sparade kopian visas.
// Vid dålig täckning svarar nätet ibland inte alls, och då ska man inte vänta.
// Den nya versionen sparas ändå när den kommer fram, till nästa gång.
const VANTA_PA_NATET = 4000;

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

  const network = fetch(request);

  // Spara en kopia av det som hämtades, till nästa gång nätet saknas.
  // waitUntil håller igång sw.js tills kopian är sparad, även om den
  // sparade kopian redan har visats. Kopian tas direkt, innan sidan hinner
  // läsa svaret, annars går den inte att ta. Ett fel från nätet ignoreras här.
  event.waitUntil(
    network
      .then(response => {
        if (!response.ok) return;
        const copy = response.clone();
        return caches.open(CACHE).then(cache => cache.put(request, copy));
      })
      .catch(() => {})
  );

  event.respondWith(
    Promise.race([network, wait(VANTA_PA_NATET)])
      .then(response => response || saved(request).then(copy => copy || network))
      .catch(() => saved(request).then(copy => copy || Response.error()))
  );
});

// Ett löfte som blir klart efter ms millisekunder, utan värde.
function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Den sparade kopian av en fil, eller undefined. Adressens ?-del och #-del spelar
// ingen roll. För själva sidan används index.html om adressen inte finns sparad.
function saved(request) {
  return caches.match(request, { ignoreSearch: true })
    .then(copy => copy || (request.mode === "navigate" ? caches.match("index.html") : undefined));
}
