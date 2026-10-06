"""Bygger appen med alla fem skiftlagen.

Skriver till mappen build/ut/, som inte följer med till GitHub:
    index.html              färdig sida med kalenderknapp
    forhandsvisning.html    samma sida utan kalenderknapp
    skiftlag1.ics – skiftlag5.ics
    ikonerna för hemskärmen

Kör:
    python3 build/alla-lag.py

Appen läggs inte ut automatiskt. Schemat ändras i avsnittet "Schemadata" här nedanför.
"""
import datetime as dt
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(HERE)          # repots rot
UT = os.path.join(HERE, "ut")        # hit skrivs allt


# ---------------------------------------------------------------------------
# Schemadata
# ---------------------------------------------------------------------------

START = dt.date(2026, 10, 5)   # måndag vecka 41, första hela veckan i 5-skiftet
END = dt.date(2027, 6, 27)     # söndag vecka 25, midsommarveckan

# Fem veckotyper som upprepas i ordningen A, B, C, D, E.
# Pass måndag till söndag, tom sträng = ledig.
TYPES = {
    "A": ["N", "N", "", "", "FM", "HD", "HD"],
    "B": ["", "", "FM", "FM", "N", "HN", "HN"],
    "C": ["", "", "", "", "", "", ""],
    "D": ["EM", "EM", "N", "N", "", "", ""],
    "E": ["FM", "FM", "EM", "EM", "EM", "", ""],
}
ORDER = "ABCDE"

# Var i cykeln varje lag står första veckan (0 = A, 1 = B, ...).
# Avläst från schemabladet: vecka 41 har lag 1 typ C, lag 2 typ A, och så vidare.
OFFSET = {1: 2, 2: 0, 3: 4, 4: 3, 5: 1}

# Passkod -> (namn, tider som visas, hel timme då passet börjar, längd i timmar).
# Man går på fem minuter före hel timme för överlämning.
PASS = {
    "FM": ("Förmiddag", "05:55–14:00", 6, 8),
    "EM": ("Eftermiddag", "13:55–22:00", 14, 8),
    "N": ("Natt", "21:55–06:00", 22, 8),
    "HD": ("Helgdag", "05:55–18:00", 6, 12),
    "HN": ("Helgnatt", "17:55–06:00", 18, 12),
}

# Röda dagar och aftnar som markeras på sidan.
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
}


# ---------------------------------------------------------------------------
# Veckor
# ---------------------------------------------------------------------------

def shifts(lag, monday):
    """Passen måndag till söndag för ett lag, veckan som börjar på monday."""
    weeks_from_start = (monday - START).days // 7
    return TYPES[ORDER[(OFFSET[lag] + weeks_from_start) % 5]]


def build_weeks():
    """Alla veckor i perioden som [måndagens datum, veckonummer]."""
    weeks = []
    monday = START
    while monday <= END:
        weeks.append([monday.isoformat(), monday.isocalendar()[1]])
        monday += dt.timedelta(days=7)
    return weeks


# ---------------------------------------------------------------------------
# Sidan
# ---------------------------------------------------------------------------

# Layout: lagväljare överst, sedan veckoremsor och därefter månad för månad
# i en smal kolumn som passar en telefon.
STYLE = """\
/* Färger och typsnitt i ljust läge */
:root {
  --paper: #e9edf1;
  --card: #ffffff;
  --ink: #16202e;
  --muted: #4d5c6e;
  --line: #c9d3dd;
  --fm: #ffd166;
  --em: #e8833a;
  --n: #2e3a66;
  --hd: linear-gradient(135deg, #ffd166 0%, #ffd166 42%, #e8833a 100%);
  --hn: linear-gradient(135deg, #473d6b 0%, #141a30 100%);
  --off: #f2f5f8;
  --offink: #75828f;
  --ring: #16202e;
  --red: #b3261e;
  --on-light: #16202e;
  --on-dark: #ffffff;
  --sel: #16202e;
  --sel-ink: #ffffff;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif;
  --body: "IBM Plex Sans", -apple-system, "Segoe UI", system-ui, sans-serif;
}

/* Mörkt läge när telefonen är inställd på det */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #11161f;
    --card: #1a212c;
    --ink: #e8edf3;
    --muted: #8c9bab;
    --line: #2c3745;
    --fm: #e5b94d;
    --em: #cf6f2b;
    --n: #4a5a96;
    --hd: linear-gradient(135deg, #e5b94d 0%, #e5b94d 42%, #cf6f2b 100%);
    --hn: linear-gradient(135deg, #5a4e85 0%, #232c45 100%);
    --off: #1f2733;
    --offink: #7d8b9a;
    --ring: #e8edf3;
    --red: #ff8a80;
    --sel: #e8edf3;
    --sel-ink: #11161f;
    color-scheme: dark;
  }
}

/* Mörkt läge när det är valt uttryckligen. Samma värden som ovan. */
:root[data-theme="dark"] {
  --paper: #11161f;
  --card: #1a212c;
  --ink: #e8edf3;
  --muted: #8c9bab;
  --line: #2c3745;
  --fm: #e5b94d;
  --em: #cf6f2b;
  --n: #4a5a96;
  --hd: linear-gradient(135deg, #e5b94d 0%, #e5b94d 42%, #cf6f2b 100%);
  --hn: linear-gradient(135deg, #5a4e85 0%, #232c45 100%);
  --off: #1f2733;
  --offink: #7d8b9a;
  --ring: #e8edf3;
  --red: #ff8a80;
  --sel: #e8edf3;
  --sel-ink: #11161f;
  color-scheme: dark;
}

/* Grund */
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--body);
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
}
.wrap {
  max-width: 660px;
  margin: 0 auto;
  padding-inline: 16px;
  padding-block: 14px 60px;
}

/* Sidhuvud */
header {
  padding: 2px 2px 10px;
}
h1 {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.4rem;
  line-height: 1.1;
  margin: 0 0 2px;
}
.sub {
  color: var(--muted);
  font-size: .82rem;
  margin: 0;
}

/* Lagväljare. Ligger kvar överst när man scrollar. */
.pick {
  position: sticky;
  top: env(safe-area-inset-top, 0px);
  z-index: 5;
  background: var(--paper);
  padding: 8px 0 10px;
  margin: 0 0 6px;
}
.pick-label {
  font-size: .74rem;
  color: var(--muted);
  margin: 0 2px 5px;
  display: block;
}
.seg {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 4px;
}
.seg button {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.05rem;
  min-height: 44px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}
.seg button[aria-pressed="true"] {
  background: var(--sel);
  color: var(--sel-ink);
}
.seg button:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

/* Veckoremsor: den här veckan och nästa */
.now {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px 12px 12px;
  margin-bottom: 8px;
}
.now h2 {
  font-family: var(--display);
  font-size: .95rem;
  margin: 0 0 10px;
  font-weight: 600;
  color: var(--muted);
}
.hrow {
  display: flex;
  gap: 4px;
}
.hd {
  flex: 1;
  text-align: center;
  min-width: 0;
}
.hd span {
  display: block;
  font-size: .66rem;
  color: var(--muted);
  margin-bottom: 3px;
}
.hd em {
  display: block;
  font-style: normal;
  font-family: var(--display);
  font-weight: 700;
  font-size: .86rem;
  padding: 9px 0;
  border-radius: 6px;
}

/* Teckenförklaring */
.legend {
  list-style: none;
  padding: 0;
  margin: 14px 0 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 14px;
  font-size: .84rem;
}
.legend li {
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: 8px;
  align-items: center;
}
.legend li .chip {
  grid-row: span 2;
}
.legend li.single .chip {
  grid-row: auto;
}
.legend em {
  display: block;
  font-style: normal;
  font-size: .74rem;
  color: var(--muted);
  line-height: 1.2;
}

/* Små passmärken i teckenförklaringen */
.chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 22px;
  border-radius: 5px;
  font-family: var(--display);
  font-weight: 700;
  font-size: .75rem;
}
.chip.p-off {
  border: 1px dashed var(--line);
}

/* Knapp som lägger in passen i kalendern */
.cal {
  display: block;
  text-align: center;
  padding: 12px;
  margin: -8px 0 20px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--line);
  color: var(--ink);
  font-weight: 600;
  font-size: .9rem;
  text-decoration: none;
}
.cal:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

/* Månadsrubrik och kalenderrutnät */
h2.month {
  font-family: var(--display);
  font-weight: 600;
  font-size: 1.05rem;
  margin: 22px 0 8px;
  padding-bottom: 5px;
  border-bottom: 2px solid var(--ink);
}
h2.month span {
  color: var(--muted);
  font-weight: 500;
}
table.grid {
  width: 100%;
  border-collapse: separate;
  border-spacing: 3px;
  table-layout: fixed;
  font-variant-numeric: tabular-nums;
}
table.grid thead th {
  font-size: .68rem;
  color: var(--muted);
  font-weight: 500;
  padding-bottom: 2px;
}
th.wk {
  width: 26px;
  font-family: var(--display);
  font-size: .75rem;
  color: var(--muted);
  font-weight: 600;
}
td.d {
  border-radius: 6px;
  text-align: center;
  padding: 6px 1px 5px;
  border: 1px solid transparent;
}
td .num {
  display: block;
  font-size: .72rem;
  opacity: .9;
  line-height: 1.1;
  font-weight: 500;
}
td .code {
  display: block;
  font-family: var(--display);
  font-weight: 700;
  font-size: .8rem;
  line-height: 1.2;
}

/* Tillstånd: passerad dag, i dag, röd dag */
td.past {
  filter: grayscale(1);
  opacity: .3;
}
td.today {
  border-color: var(--ring);
  box-shadow: 0 0 0 1.5px var(--ring);
}
td.red.p-off .num {
  color: var(--red);
  opacity: 1;
  font-weight: 700;
}
td.red:not(.p-off) .num {
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 700;
}

/* Passfärger. Ljusa pass har mörk text, mörka pass har vit text. */
.p-FM {
  background: var(--fm);
  color: var(--on-light);
}
.p-EM {
  background: var(--em);
  color: var(--on-light);
}
.p-HD {
  background: var(--hd);
  color: var(--on-light);
}
.p-N {
  background: var(--n);
  color: var(--on-dark);
}
.p-HN {
  background: var(--hn);
  color: var(--on-dark);
}
.p-off {
  background: var(--off);
  color: var(--offink);
}

/* Röda dagar, listade under varje månad */
ul.notes {
  list-style: none;
  padding: 8px 10px;
  margin: 8px 0 0;
  background: var(--card);
  border-radius: 8px;
  border: 1px solid var(--line);
  font-size: .82rem;
  color: var(--muted);
}
ul.notes li {
  padding: 2px 0;
}
ul.notes b {
  color: var(--ink);
}

/* Lista med hela lediga veckor */
.free-box {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px 14px 12px;
  margin-top: 30px;
}
.free-box h2 {
  font-family: var(--display);
  margin: 0 0 8px;
  font-size: 1rem;
}
.free-box ul {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: .88rem;
  color: var(--muted);
  columns: 2;
  column-gap: 16px;
}
.free-box li {
  padding: 2px 0;
  break-inside: avoid;
}
.free-box b {
  color: var(--ink);
  font-family: var(--display);
}

/* Sidfot */
footer {
  margin-top: 26px;
  font-size: .78rem;
  color: var(--muted);
  line-height: 1.5;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
"""

# Skriptet ritar upp hela schemat i webbläsaren, så att man kan byta lag
# utan att ladda om sidan. Samma uträkning som i shifts() här ovanför.
SCRIPT = """\
// ---------------------------------------------------------------------------
// Data från byggskriptet
// ---------------------------------------------------------------------------

// Varje vecka i perioden: [måndagens datum, veckonummer].
const WEEKS = __WEEKS__;

// De fem veckotyperna i cykeln. Pass måndag till söndag, "" = ledig.
const TYPES = __TYPES__;
const ORDER = "ABCDE";

// Var i cykeln varje lag står första veckan (0 = A, 1 = B, ...).
const OFFSET = __OFFSET__;

// Passkod -> [namn, tider].
const PASS = __PASSES__;

// Datum -> helgdagens namn.
const RED = __RED__;

// Adress till kalenderfilen, där {n} byts mot lagnumret. Tom i förhandsvisningen.
const CAL = __CAL__;

const DAG = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"];
const MAN = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
             "augusti", "september", "oktober", "november", "december"];

// ---------------------------------------------------------------------------
// Hjälpfunktioner
// ---------------------------------------------------------------------------

function pad(n) {
  return String(n).padStart(2, "0");
}

// Datum som "ÅÅÅÅ-MM-DD" i telefonens lokala tid.
function iso(d) {
  return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
}

// Dag nummer i (0 = måndag) i veckan som börjar på datumet monday.
function dayOf(monday, i) {
  const [year, month, day] = monday.split("-").map(Number);
  return new Date(year, month - 1, day + i);
}

// Passen måndag till söndag för ett lag, vecka nummer weekIndex i WEEKS.
function shifts(lag, weekIndex) {
  return TYPES[ORDER[(OFFSET[lag] + weekIndex) % 5]];
}

// Datum i kort form, till exempel "24 dec".
function shortDate(d) {
  return d.getDate() + " " + MAN[d.getMonth()].slice(0, 3);
}

// ---------------------------------------------------------------------------
// Veckoremsorna överst
// ---------------------------------------------------------------------------

// En veckoremsa: sju rutor med veckodag och pass.
function strip(lag, weekIndex, rubrik) {
  const week = shifts(lag, weekIndex);
  let cells = "";
  for (let i = 0; i < 7; i++) {
    const pass = week[i];
    cells += '<div class="hd"><span>' + DAG[i] + '</span>' +
             '<em class="p-' + (pass || "off") + '">' + (pass || "–") + '</em></div>';
  }
  return '<div class="now"><h2>' + rubrik + ' (v' + WEEKS[weekIndex][1] + ')</h2>' +
         '<div class="hrow">' + cells + '</div></div>';
}

function heroHtml(lag, today) {
  const current = WEEKS.findIndex(week =>
    week[0] <= today && today <= iso(dayOf(week[0], 6)));

  if (current >= 0) {
    const hasNext = Boolean(WEEKS[current + 1]);
    return strip(lag, current, "Den här veckan") +
           (hasNext ? strip(lag, current + 1, "Nästa vecka") : "");
  }
  if (today < WEEKS[0][0]) {
    // Schemat har inte börjat än.
    return strip(lag, 0, "Första veckan") + strip(lag, 1, "Veckan efter");
  }
  // Schemat har tagit slut.
  return '<div class="now"><h2>Schemat gäller 5 okt 2026 – 27 juni 2027</h2></div>';
}

// ---------------------------------------------------------------------------
// Månaderna
// ---------------------------------------------------------------------------

// En ruta i kalendern: datum överst, passkod under.
function cellHtml(day, pass, today) {
  const date = iso(day);
  const classes = ["d", "p-" + (pass || "off")];
  if (RED[date]) classes.push("red");
  if (date < today) classes.push("past");
  if (date === today) classes.push("today");
  return '<td class="' + classes.join(" ") + '" data-d="' + date + '">' +
         '<span class="num">' + day.getDate() + '</span>' +
         '<span class="code">' + (pass || "–") + '</span></td>';
}

// Raden under en månad som säger vad som gäller en röd dag.
function redDayHtml(day, pass) {
  const what = pass ? PASS[pass][0].toLowerCase() + " " + PASS[pass][1] : "ledig";
  return '<li><b>' + shortDate(day) + '</b> ' + RED[iso(day)] + ' – ' + what + '</li>';
}

// Bygger alla månadstabeller och samlar hela lediga veckor som inte har passerat.
function monthsHtml(lag, today) {
  let html = "";
  let month = "";     // månaden som byggs just nu, som "år-månad"
  let notes = [];     // röda dagar i den månaden
  const free = [];

  function closeMonth() {
    if (!month) return;
    html += "</tbody></table>";
    if (notes.length) html += '<ul class="notes">' + notes.join("") + "</ul>";
    notes = [];
  }

  WEEKS.forEach((entry, weekIndex) => {
    const [monday, weekNumber] = entry;
    const week = shifts(lag, weekIndex);

    // En vecka hör till den månad där torsdagen ligger.
    const thursday = dayOf(monday, 3);
    const key = thursday.getFullYear() + "-" + thursday.getMonth();
    if (key !== month) {
      closeMonth();
      month = key;
      html += '<h2 class="month">' + MAN[thursday.getMonth()] +
              ' <span>' + thursday.getFullYear() + '</span></h2>' +
              '<table class="grid"><thead><tr><th class="wk">v</th>' +
              DAG.map(name => "<th>" + name + "</th>").join("") +
              '</tr></thead><tbody>';
    }

    const isFree = week.every(pass => !pass);
    if (isFree && iso(dayOf(monday, 6)) >= today) {
      free.push('<li><b>v' + weekNumber + '</b> ' + shortDate(dayOf(monday, 0)) +
                ' – ' + shortDate(dayOf(monday, 6)) + '</li>');
    }

    html += '<tr><th class="wk">' + weekNumber + '</th>';
    for (let i = 0; i < 7; i++) {
      const day = dayOf(monday, i);
      if (RED[iso(day)]) notes.push(redDayHtml(day, week[i]));
      html += cellHtml(day, week[i], today);
    }
    html += "</tr>";
  });
  closeMonth();

  return { html: html, free: free };
}

// ---------------------------------------------------------------------------
// Rita upp sidan och byta lag
// ---------------------------------------------------------------------------

function render(lag) {
  const today = iso(new Date());
  const months = monthsHtml(lag, today);

  document.getElementById("hero").innerHTML = heroHtml(lag, today);
  document.getElementById("months").innerHTML = months.html;
  document.getElementById("free").innerHTML =
    months.free.join("") || "<li>Inga hela lediga veckor kvar i perioden</li>";
  document.getElementById("freeh").textContent = "Hela veckor lediga för skiftlag " + lag;

  // Markera valt lag i väljaren.
  document.querySelectorAll(".seg button").forEach(button => {
    const selected = Number(button.dataset.lag) === lag;
    button.setAttribute("aria-pressed", String(selected));
  });

  // Kalenderknappen finns bara på den utlagda sidan.
  const cal = document.getElementById("cal");
  if (cal) {
    cal.href = CAL.replace("{n}", lag);
    cal.textContent = "Lägg in skiftlag " + lag + " i din kalender";
  }

  document.title = "Skiftlag " + lag + " – skiftschema";
}

// Byter lag och kommer ihåg valet till nästa gång.
function pick(lag) {
  render(lag);
  // Lagring kan vara avstängd, till exempel i privat läge. Då struntar vi i det.
  try { localStorage.setItem("skiftlag", String(lag)); } catch (e) {}
  try { history.replaceState(null, "", "#lag" + lag); } catch (e) {}
}

// Vilket lag som visas först: adressen (#lag3), sedan senaste valet, annars lag 1.
function startLag() {
  const fromHash = /^#lag([1-5])$/.exec(location.hash || "");
  if (fromHash) return Number(fromHash[1]);

  let saved = 0;
  try { saved = Number(localStorage.getItem("skiftlag")) || 0; } catch (e) {}
  return saved >= 1 && saved <= 5 ? saved : 1;
}

document.querySelectorAll(".seg button").forEach(button => {
  button.addEventListener("click", () => pick(Number(button.dataset.lag)));
});
render(startLag());
"""

# Det som är gemensamt för förhandsvisningen och den färdiga sidan.
CONTENT = """\
<title>Skiftschema alla lag</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
__STYLE__</style>

<div class="wrap">

<header>
  <h1>Skiftschema</h1>
  <p class="sub">5-skift · oktober 2026 – juni 2027</p>
</header>

<div class="pick">
  <span class="pick-label" id="picklabel">Välj skiftlag</span>
  <div class="seg" role="group" aria-labelledby="picklabel">
    __BUTTONS__
  </div>
</div>

<!-- Fylls av skriptet: den här veckan och nästa -->
<div id="hero"></div>

<ul class="legend">
  __LEGEND__
</ul>
__CALBUTTON__
<!-- Fylls av skriptet: en tabell per månad -->
<div id="months"></div>

<div class="free-box">
  <h2 id="freeh">Hela veckor lediga</h2>
  <ul id="free"></ul>
</div>

<footer>
Schemat börjar måndag 5 oktober 2026. Alla fem lagen går samma cykel på fem veckor,
förskjutna en vecka i taget: två nätter → två förmiddagar och en natt → ledig vecka →
två kvällar och två nätter → fem dagpass. Passen börjar fem minuter före hel timme för överlämning.
Storhelger körs som vanligt.
<br><br>
Avläst från utdelade schemablad till och med 27 december 2026.
Därefter uträknat på cykeln. Stäm av mot nya blad när de kommer.
</footer>

</div>

<script>
__SCRIPT__</script>
"""

# Den färdiga sidan är ett helt HTML-dokument runt innehållet.
DOCUMENT = """\
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

<!-- Ikon och utseende när sidan ligger på hemskärmen -->
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skift">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">

<!-- Håller innehållet undan från telefonens statusfält och hemindikator -->
<style>
:root {
  padding-top: env(safe-area-inset-top, 0px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
</head>
<body>
__CONTENT__</body>
</html>
"""


def fill(template, **values):
    """Byter ut __NAMN__ i mallen mot värdet med samma namn."""
    for name, value in values.items():
        template = template.replace(f"__{name.upper()}__", value)
    return template


def to_js(value):
    """Python-data som JavaScript, på en rad."""
    return json.dumps(value, ensure_ascii=False)


def rows_to_js(rows):
    """En lista som JavaScript, med ett element per rad."""
    return "[\n  " + ",\n  ".join(to_js(row) for row in rows) + "\n]"


def dict_to_js(mapping):
    """En uppslagstabell som JavaScript, med en nyckel per rad."""
    rows = [f"{to_js(str(key))}: {to_js(value)}" for key, value in mapping.items()]
    return "{\n  " + ",\n  ".join(rows) + "\n}"


def legend_html():
    """Teckenförklaringen: ett märke per passkod, sist "Ledig"."""
    items = [
        f'<li><span class="chip p-{code}">{code}</span>{name}<em>{times}</em></li>'
        for code, (name, times, _, _) in PASS.items()
    ]
    items.append('<li class="single"><span class="chip p-off">–</span>Ledig</li>')
    return "\n  ".join(items)


def buttons_html():
    """Knapparna 1–5 i lagväljaren."""
    return "\n    ".join(
        f'<button type="button" id="b{lag}" data-lag="{lag}" aria-pressed="false" '
        f'aria-label="Skiftlag {lag}">{lag}</button>'
        for lag in range(1, 6)
    )


def content_html(weeks, calendar_address):
    """Sidans innehåll. Utan calendar_address blir det ingen kalenderknapp."""
    script = fill(
        SCRIPT,
        weeks=rows_to_js(weeks),
        types=dict_to_js(TYPES),
        offset=to_js(OFFSET),
        passes=dict_to_js({code: [name, times] for code, (name, times, _, _) in PASS.items()}),
        red=dict_to_js(RED),
        cal=to_js(calendar_address or ""),
    )
    if calendar_address:
        cal_button = '\n<a class="cal" id="cal" href="#">Lägg in passen i din kalender</a>\n'
    else:
        cal_button = ""
    return fill(
        CONTENT,
        style=STYLE,
        buttons=buttons_html(),
        legend=legend_html(),
        calbutton=cal_button,
        script=script,
    )


# ---------------------------------------------------------------------------
# Kalenderfiler
# ---------------------------------------------------------------------------

# Tidszonen måste beskrivas i filen för att sommar- och vintertid ska bli rätt.
TIMEZONE = [
    "BEGIN:VTIMEZONE",
    "TZID:Europe/Stockholm",
    "BEGIN:DAYLIGHT",
    "TZOFFSETFROM:+0100",
    "TZOFFSETTO:+0200",
    "TZNAME:CEST",
    "DTSTART:19700329T020000",
    "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU",
    "END:DAYLIGHT",
    "BEGIN:STANDARD",
    "TZOFFSETFROM:+0200",
    "TZOFFSETTO:+0100",
    "TZNAME:CET",
    "DTSTART:19701025T030000",
    "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU",
    "END:STANDARD",
    "END:VTIMEZONE",
]


def stamp(moment):
    """Tidpunkt i kalenderformatets skrivsätt, till exempel 20261005T215500."""
    return moment.strftime("%Y%m%dT%H%M%S")


def build_calendar(lag, weeks):
    """Kalenderfilen för ett lag som (text, antal pass). Radslut av typen CRLF."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//Skiftlag{lag}//Skiftschema//SV",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Skiftlag {lag}",
        "X-WR-TIMEZONE:Europe/Stockholm",
    ] + TIMEZONE

    count = 0
    for monday_text, _ in weeks:
        monday = dt.date.fromisoformat(monday_text)
        for i, code in enumerate(shifts(lag, monday)):
            if not code:
                continue
            name, _, hour, length = PASS[code]
            full_hour = dt.datetime.combine(monday + dt.timedelta(days=i), dt.time(hour, 0))
            start = full_hour - dt.timedelta(minutes=5)   # överlämning
            end = full_hour + dt.timedelta(hours=length)
            lines += [
                "BEGIN:VEVENT",
                # UID måste vara unikt och får inte ändras, annars blir det dubbletter vid ny import.
                f"UID:lag{lag}-{stamp(start)}@skiftschema",
                "DTSTAMP:20261002T100000Z",
                f"DTSTART;TZID=Europe/Stockholm:{stamp(start)}",
                f"DTEND;TZID=Europe/Stockholm:{stamp(end)}",
                f"SUMMARY:Skift: {name}",
                f"DESCRIPTION:Skiftlag {lag} · {code} · {start:%H:%M}–{end:%H:%M}",
                "TRANSP:OPAQUE",
                "END:VEVENT",
            ]
            count += 1
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n", count


# ---------------------------------------------------------------------------
# Kör
# ---------------------------------------------------------------------------

def write(name, text, newline=None):
    with open(os.path.join(UT, name), "w", encoding="utf-8", newline=newline) as f:
        f.write(text)


def main():
    os.makedirs(UT, exist_ok=True)
    weeks = build_weeks()

    # Förhandsvisningen saknar kalenderknapp, eftersom kalenderfilerna
    # bara finns på den utlagda sidan.
    write("forhandsvisning.html", content_html(weeks, None))

    # På den färdiga sidan byts {n} i adressen mot lagnumret av skriptet.
    write("index.html", fill(DOCUMENT, content=content_html(weeks, "skiftlag{n}.ics")))

    for lag in range(1, 6):
        text, count = build_calendar(lag, weeks)
        # newline="" hindrar Python från att ändra radsluten i kalenderfilen.
        write(f"skiftlag{lag}.ics", text, newline="")
        print(f"lag {lag}: {count} pass")

    # Ikonerna för hemskärmen ligger i repots rot.
    for icon in ("apple-touch-icon.png", "favicon.png"):
        shutil.copy(os.path.join(ROT, icon), os.path.join(UT, icon))

    print(f"veckor: {len(weeks)}, från {weeks[0][0]} till och med vecka {weeks[-1][1]}")


if __name__ == "__main__":
    main()
