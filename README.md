# Skiftschema

Skiftschema för 5-skiftet med alla fem skiftlagen, publicerat via GitHub Pages.
Man väljer sitt lag överst på sidan, och valet sparas i telefonen.

Skapad av J. Stork.

## Struktur

```
index.html                      Sidans innehåll
style.css                       Utseendet
script.js                       Logiken: ritar upp schemat och byter lag
data.js                         Schemadatan som script.js använder
skiftlag1.ics – skiftlag5.ics   Kalenderfilerna bakom knappen på sidan
apple-touch-icon.png            Ikon på hemskärmen
favicon.png                     Ikon i webbläsarens flik

build/
  bygg.py                       Bygger index.html, data.js och kalenderfilerna
```

`style.css` och `script.js` skrivs för hand.

`index.html`, `data.js` och kalenderfilerna skapas av `build/bygg.py` och ska inte ändras
direkt, eftersom ändringen skrivs över vid nästa bygge.

## Uppdatera schemat

Rotationen, tiderna och de röda dagarna står överst i `build/bygg.py`, under rubriken
"Schemadata". Ändra där och bygg om:

    python3 build/bygg.py

Skriptet behöver bara Python 3, inga extra paket.

## Ändra utseende eller beteende

Ändra direkt i `style.css` eller `script.js`. Det behövs inget bygge.

Vilket lag som visas för den som inte har valt något än står överst i `script.js`,
i konstanten `STANDARDLAG`.

## Länka till ett visst lag

Lägg till `#lag` och lagets nummer sist i adressen, till exempel `#lag4`.

## Varifrån datan kommer

Avläst från utdelade schemablad till och med 27 december 2026. Därefter uträknat på
femveckorscykeln. Stäm av mot nya blad när de kommer.

## Historik

Fram till oktober 2026 visade sidan bara skiftlag 2, med start i september.
Den versionen finns kvar i repots historik.
