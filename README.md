# Skiftschema

Skiftschema för 5-skiftet, publicerat via GitHub Pages.

## Filer

- `index.html`, `skiftlag2.ics` – sidan för skiftlag 2 och dess kalenderfil. Det är de här filerna som visas på webben.
- `build/skiftlag2.py` – bygger de två filerna ovan.
- `build/alla-lag.py` – bygger appen med alla fem lagen till `build/ut/`. Den är inte utlagd.

## Uppdatera schemat

Rotationen och tiderna står överst i respektive skript. Ändra där och kör sedan:

    python3 build/skiftlag2.py

Skripten behöver bara Python 3, inga extra paket.

## Varifrån datan kommer

Avläst från utdelade schemablad till och med 27 december 2026. Därefter uträknat på
femveckorscykeln. Stäm av mot nya blad när de kommer.
