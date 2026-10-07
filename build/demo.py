"""Bygger en demo av skiftschemat med ett påhittat schema.

Gjord av J. Stork.

Demon är till för att visa upp appen, till exempel på jstork.se. Den använder
samma style.css och script.js som den riktiga appen, men:

    - schemat är påhittat (andra pass, andra tider, annan rotation)
    - perioden räknas ut från dagens datum, så att demon alltid är aktuell
    - det finns ingen kalenderdel och inget offline-stöd
    - överst ligger en rad som säger att det är en demo

Skriver till build/ut/demo/, som inte följer med till GitHub.
Kopiera innehållet i den mappen till webbplatsen.

Kör:
    python3 build/demo.py
"""
import os
import shutil

import bygg

UT = os.path.join(bygg.UT, "demo")

# Vart raden överst i demon länkar. Ändra om sidan om arbetet flyttas.
BACK_URL = "../../arbeten/skiftschema/"
BACK_TEXT = "Tillbaka till J. Stork"

# Hur många veckor demon visar bakåt och framåt från den här veckan,
# och hur många veckor framåt som räknas som bekräftade.
WEEKS_BACK = 5
WEEKS_AHEAD = 34
WEEKS_CONFIRMED = 12


# ---------------------------------------------------------------------------
# Påhittat schema
# ---------------------------------------------------------------------------

TYPES = {
    "A": ["FM", "FM", "FM", "EM", "EM", "", ""],
    "B": ["EM", "EM", "", "", "N", "HN", "HN"],
    "C": ["", "", "", "", "", "", ""],
    "D": ["N", "N", "N", "", "", "HD", "HD"],
    "E": ["", "FM", "FM", "FM", "EM", "", ""],
}
ORDER = "ABCDE"
OFFSET = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}

PASS = {
    "FM": ("Förmiddag", "06:00–14:00", 6, 8),
    "EM": ("Eftermiddag", "14:00–22:00", 14, 8),
    "N": ("Natt", "22:00–06:00", 22, 8),
    "HD": ("Helgpass dag", "06:00–18:00", 6, 12),
    "HN": ("Helgpass natt", "18:00–06:00", 18, 12),
}

# Röda dagar och aftnar. Listan räcker till och med 2028.
RED = {
    "2026-12-24": "Julafton",
    "2026-12-25": "Juldagen",
    "2026-12-26": "Annandag jul",
    "2026-12-31": "Nyårsafton",
    "2027-01-01": "Nyårsdagen",
    "2027-01-06": "Trettondedag jul",
    "2027-03-26": "Långfredagen",
    "2027-03-28": "Påskdagen",
    "2027-03-29": "Annandag påsk",
    "2027-05-01": "Första maj",
    "2027-05-06": "Kristi himmelsfärd",
    "2027-06-06": "Nationaldagen",
    "2027-06-25": "Midsommarafton",
    "2027-06-26": "Midsommardagen",
    "2027-12-24": "Julafton",
    "2027-12-25": "Juldagen",
    "2027-12-26": "Annandag jul",
    "2027-12-31": "Nyårsafton",
    "2028-01-01": "Nyårsdagen",
    "2028-01-06": "Trettondedag jul",
    "2028-04-14": "Långfredagen",
    "2028-04-16": "Påskdagen",
    "2028-04-17": "Annandag påsk",
    "2028-05-01": "Första maj",
    "2028-05-25": "Kristi himmelsfärd",
    "2028-06-06": "Nationaldagen",
    "2028-06-23": "Midsommarafton",
    "2028-06-24": "Midsommardagen",
    "2028-12-24": "Julafton",
    "2028-12-25": "Juldagen",
    "2028-12-26": "Annandag jul",
    "2028-12-31": "Nyårsafton",
}


# ---------------------------------------------------------------------------
# Sidan
# ---------------------------------------------------------------------------

FOOTER = (
    "<p>Det här är en demo med ett påhittat schema. Perioden räknas ut från dagens datum.</p>\n"
    "<p>Den riktiga appen har också kalenderfiler att prenumerera på och fungerar utan nät.</p>"
)

DOCUMENT = """\
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Skiftschema – demo</title>
<meta name="description" content="Demo av ett skiftschema i mobilen, med påhittat schema.">
<meta name="author" content="__CREDIT__">
<meta name="robots" content="noindex">
<link rel="icon" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">
<link rel="preload" href="typsnitt/ibm-plex-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css">
<style>
/* Raden överst som säger att det är en demo. Finns bara i demon. */
.demo-banner {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px 14px;
  padding: 10px 16px;
  background: var(--ink);
  color: var(--paper);
  font-size: var(--t-sm);
}
.demo-banner a {
  color: inherit;
  font-weight: 600;
}
</style>
<script src="data.js" defer></script>
<script src="script.js" defer></script>
</head>
<body>
<p class="demo-banner"><span>Demo med påhittat schema</span><a href="__BACKURL__">__BACKTEXT__</a></p>
__BODY__</body>
</html>
"""

# Schemadatan i demon. Till skillnad från den riktiga appen räknas veckorna
# ut i webbläsaren, från dagens datum.
DATA = """\
// Skapad av build/demo.py. Ändra inte här, ändra i byggskriptet.
// Demo: påhittat schema där perioden räknas ut från dagens datum.

// Måndagen i veckan som innehåller datumet d.
function demoMonday(d) {
  const monday = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  monday.setDate(monday.getDate() - (monday.getDay() + 6) % 7);
  return monday;
}

// Veckonummer enligt svensk standard (ISO 8601).
function demoWeekNumber(monday) {
  const thursday = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + 3);
  const firstThursday = demoMonday(new Date(thursday.getFullYear(), 0, 4));
  firstThursday.setDate(firstThursday.getDate() + 3);
  return 1 + Math.round((thursday - firstThursday) / 604800000);
}

function demoIso(d) {
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" +
         String(d.getDate()).padStart(2, "0");
}

const DEMO_FIRST = demoMonday(new Date());
DEMO_FIRST.setDate(DEMO_FIRST.getDate() - 7 * __BACK__);

// Varje vecka i perioden: [måndagens datum, veckonummer].
const WEEKS = [];
for (let i = 0; i < __BACK__ + __AHEAD__ + 1; i++) {
  const monday = new Date(DEMO_FIRST.getFullYear(), DEMO_FIRST.getMonth(), DEMO_FIRST.getDate() + 7 * i);
  WEEKS.push([demoIso(monday), demoWeekNumber(monday)]);
}

// Veckotyperna i cykeln. Pass måndag till söndag, "" = ledig.
const TYPES = __TYPES__;
const ORDER = __ORDER__;

// Var i cykeln varje lag står första veckan. Räknas från en fast startpunkt,
// så att ett lag har samma schema oavsett vilken dag man öppnar demon.
const DEMO_WEEKS_SINCE_START = Math.round((DEMO_FIRST - new Date(2026, 0, 5)) / 604800000);
const DEMO_BASE = __OFFSET__;
const OFFSET = {};
Object.keys(DEMO_BASE).forEach(lag => {
  OFFSET[lag] = ((DEMO_BASE[lag] + DEMO_WEEKS_SINCE_START) % ORDER.length + ORDER.length) % ORDER.length;
});

// Passkod -> [namn, tider, hel timme då passet börjar, längd i timmar].
const PASS = __PASS__;

// Datum -> helgdagens namn.
const RED = __RED__;

// Sista dagen som räknas som bekräftad. Veckor efter den visas som preliminära.
const DEMO_CONFIRMED = demoMonday(new Date());
DEMO_CONFIRMED.setDate(DEMO_CONFIRMED.getDate() + 7 * __CONFIRMEDWEEKS__ + 6);
const CONFIRMED = demoIso(DEMO_CONFIRMED);

// Demon har ingen kalenderdel.
const CAL = "";
"""


def main():
    # Samma mallar och hjälpfunktioner som den riktiga appen, med demons schema.
    bygg.TYPES = TYPES
    bygg.ORDER = ORDER
    bygg.OFFSET = OFFSET
    bygg.PASS = PASS
    bygg.PASS_NOTE = ""
    bygg.footer_html = lambda: FOOTER

    os.makedirs(UT, exist_ok=True)

    page = bygg.fill(DOCUMENT, credit=bygg.CREDIT, backurl=BACK_URL, backtext=BACK_TEXT,
                     body=bygg.body_html(False))
    bygg.write(UT, "index.html", page)

    data = bygg.fill(
        DATA,
        back=str(WEEKS_BACK),
        ahead=str(WEEKS_AHEAD),
        confirmedweeks=str(WEEKS_CONFIRMED),
        types=bygg.dict_to_js(TYPES),
        order=bygg.to_js(ORDER),
        offset=bygg.to_js(OFFSET),
        **{"pass": bygg.dict_to_js({code: list(values) for code, values in PASS.items()})},
        red=bygg.dict_to_js(RED),
    )
    bygg.write(UT, "data.js", data)

    # Utseende, logik, typsnitt och ikoner är samma filer som i den riktiga appen.
    for name in ["style.css", "script.js", "favicon.png", "apple-touch-icon.png"]:
        shutil.copyfile(os.path.join(bygg.ROT, name), os.path.join(UT, name))
    shutil.copytree(os.path.join(bygg.ROT, "typsnitt"), os.path.join(UT, "typsnitt"), dirs_exist_ok=True)

    print("demo skriven till", os.path.relpath(UT, bygg.ROT))


if __name__ == "__main__":
    main()
