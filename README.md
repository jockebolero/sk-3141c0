# Skiftschema

Skiftschema för 5-skiftet, publicerat via GitHub Pages.

## Struktur

```
index.html              Sidan för skiftlag 2: innehållet, med en tabell per månad
style.css               Utseendet
script.js               Logiken: markerar dagens datum och visar aktuell vecka
skiftlag2.ics           Kalenderfilen bakom knappen på sidan
apple-touch-icon.png    Ikon på hemskärmen
favicon.png             Ikon i webbläsarens flik

build/
  skiftlag2.py          Bygger index.html och skiftlag2.ics
  alla-lag.py           Bygger appen med alla fem lagen till build/ut/
  alla-lag/
    style.css           Utseendet för appen med alla lagen
    script.js           Logiken för appen med alla lagen
```

Filerna i roten är det som visas på webben.

`style.css` och `script.js` skrivs för hand. `index.html` och `skiftlag2.ics` skapas av
`build/skiftlag2.py` och ska inte ändras direkt, eftersom ändringen skrivs över vid nästa bygge.

Appen med alla fem lagen är inte utlagd. Den byggs till `build/ut/`, som inte följer med till GitHub.

## Uppdatera schemat

Rotationen, tiderna och de röda dagarna står överst i respektive byggskript, under rubriken
"Schemadata". Ändra där och bygg om:

    python3 build/skiftlag2.py
    python3 build/alla-lag.py

Skripten behöver bara Python 3, inga extra paket.

## Ändra utseende eller beteende

Ändra direkt i `style.css` eller `script.js`. Det behövs inget bygge för sidan för skiftlag 2.
För appen med alla lagen kör du `python3 build/alla-lag.py` efteråt, så kopieras filerna till `build/ut/`.

## Varifrån datan kommer

Avläst från utdelade schemablad till och med 27 december 2026. Därefter uträknat på
femveckorscykeln. Stäm av mot nya blad när de kommer.
