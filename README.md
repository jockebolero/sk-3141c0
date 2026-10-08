# Skiftschema

Skiftschema för 5-skiftet med alla fem skiftlagen, publicerat via GitHub Pages.
Man väljer sitt lag överst på sidan, och valet sparas i telefonen.

Gjord av J. Stork.

## Struktur

```
index.html                      Sidans innehåll
style.css                       Utseendet
script.js                       Logiken: ritar upp schemat och byter lag
data.js                         Schemadatan som script.js använder
skiftlag1.ics – skiftlag5.ics   Kalenderfilerna bakom knapparna på sidan
sw.js                           Offline-stödet: sparar sidan i telefonen
manifest.webmanifest            Namn, färger och ikoner för hemskärmen
typsnitt/                       IBM Plex Sans i fem snitt, med licens
favicon.png, apple-touch-icon.png, icon-*.png   Ikoner

build/
  bygg.py                       Bygger index.html, data.js och kalenderfilerna
  ikoner.py                     Ritar ikonerna (behövs bara om ikonen ändras)
  demo.py                       Bygger en demo med påhittat schema, till jstork.se
```

`style.css`, `script.js`, `sw.js` och `manifest.webmanifest` skrivs för hand.

`index.html`, `data.js` och kalenderfilerna skapas av `build/bygg.py` och ska inte ändras
direkt, eftersom ändringen skrivs över vid nästa bygge.

## Uppdatera schemat

Rotationen, tiderna och de röda dagarna står överst i `build/bygg.py`, under rubriken
"Schemadata". Ändra där och bygg om:

    python3 build/bygg.py

Skriptet behöver bara Python 3, inga extra paket.

När nya schemablad har kommit: flytta fram `CONFIRMED` till sista dagen som är avläst
från bladen. Veckor efter den dagen märks som preliminära på sidan.

## Ändra utseende eller beteende

Ändra direkt i `style.css` eller `script.js`. Det behövs inget bygge.

Utseendet bygger på fem textstorlekar och två hörnradier, som står som variabler överst
i `style.css`. Använd dem i stället för nya värden.

## Vilket lag som visas

1. Laget man själv valde senast på sidan.
2. Annars laget i adressen, till exempel `#lag4`.
3. Annars inget: sidan ber besökaren välja.

Det egna valet går före adressen. Annars fastnar en app på hemskärmen på laget som stod
i länken man fick. Vill man ha ett förvalt lag i stället för frågan sätter man
`STANDARDLAG` överst i `script.js`.

## Hålla sidan aktuell

Sidan ritas om när datumet eller passet ändras, även om den ligger öppen över natten
som app på hemskärmen.

## Prova en annan tidpunkt

Lägg till `?nu=` och en tidpunkt i adressen för att se hur sidan ser ut då:

    index.html?nu=2026-12-30T02:00#lag2

## Utan nät

`sw.js` sparar sidan i telefonen vid första besöket. Sidan hämtas från nätet när det går
och från den sparade kopian annars. Svarar nätet inte inom fyra sekunder (`VANTA_PA_NATET`)
visas den sparade kopian direkt, och den nya versionen sparas till nästa gång. Byt namn på `CACHE` överst i `sw.js` om gamla sparade
filer ska rensas bort.

## Kalendern

Sidan erbjuder en prenumeration (uppdateras av sig själv) och en fil att ladda ner.

Prenumerationen har två knappar. Apple Kalender (iPhone, Mac) får en `webcal://`-länk.
Google Kalender (Android) förstår inte sådana länkar, så den knappen går till
`calendar.google.com/calendar/r?cid=` med kalenderns adress. På Android hamnar
Google-knappen först. Under knapparna finns adressen med en kopieringsknapp och hur man
lägger in den för hand, om knapparna inte fungerar.
Varje pass har ett fast id i kalenderfilen. Ändra inte hur id:t byggs upp i `bygg.py`,
då blir det dubbletter hos dem som redan har lagt in passen.

## Demo

`build/demo.py` bygger en kopia av appen med ett påhittat schema, för att visa upp den
utan att visa arbetsplatsens schema:

    python3 build/demo.py

Demon hamnar i `build/ut/demo/` och använder samma `style.css` och `script.js` som den
riktiga appen. Perioden räknas ut från dagens datum, så demon blir aldrig gammal.
På jstork.se ligger den i `demo/skiftschema/`. Bygg om och kopiera dit när appen har ändrats.

## Sökmotorer

Sidan är till för kollegorna och ber sökmotorer att inte visa den (`NOINDEX` i `bygg.py`).

## Varifrån datan kommer

Avläst från utdelade schemablad till och med 27 december 2026. Därefter uträknat på
femveckorscykeln. Stäm av mot nya blad när de kommer.

## Historik

Fram till oktober 2026 visade sidan bara skiftlag 2, med start i september.
Den versionen finns kvar i repots historik.
