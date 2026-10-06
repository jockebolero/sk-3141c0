"""Bygger sidan för skiftlag 2.

Skriver två filer i repots rot:
    index.html      sidan som visas på webben
    skiftlag2.ics   kalenderfilen bakom knappen på sidan

Kör:
    python3 build/skiftlag2.py

Schemat ändras i avsnittet "Schemadata" här nedanför.
"""
import datetime as dt
import json
import os

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repots rot


# ---------------------------------------------------------------------------
# Schemadata
# ---------------------------------------------------------------------------

START = dt.date(2026, 8, 31)   # måndag vecka 36
END = dt.date(2027, 6, 27)     # söndag vecka 25, midsommarveckan

# Sista datum som är avläst från ett utdelat schemablad.
# Allt efter det är uträknat på cykeln.
VERIFIED = dt.date(2026, 12, 27)

# Gamla 3-skiftet, vecka 36–40. Pass måndag till söndag, tom sträng = ledig.
SEPT = {
    36: ["EM", "EM", "EM", "EM", "", "", ""],
    37: ["FM", "FM", "FM", "FM", "FM", "", ""],
    38: ["N", "N", "N", "N", "", "", ""],
    39: ["EM", "EM", "EM", "EM", "", "", ""],
    40: ["FM", "FM", "FM", "FM", "FM", "", ""],
}

# 5-skiftet: fem veckotyper som upprepas i ordningen A, B, C, D, E.
TYPES = {
    "A": ["N", "N", "", "", "FM", "HD", "HD"],
    "B": ["", "", "FM", "FM", "N", "HN", "HN"],
    "C": ["", "", "", "", "", "", ""],
    "D": ["EM", "EM", "N", "N", "", "", ""],
    "E": ["FM", "FM", "EM", "EM", "EM", "", ""],
}
ORDER = "ABCDE"

# Passkod -> (namn, tider som visas på sidan).
PASS = {
    "FM": ("Förmiddag", "05:55–14:00"),
    "EM": ("Eftermiddag", "13:55–22:00"),
    "N": ("Natt", "21:55–06:00"),
    "HD": ("Helgdag", "05:55–18:00"),
    "HN": ("Helgnatt", "17:55–06:00"),
}

# Passkod -> (hel timme då passet börjar, längd i timmar). Används i kalenderfilen.
# Man går på fem minuter före hel timme för överlämning.
TIMES = {
    "FM": (6, 8),
    "EM": (14, 8),
    "N": (22, 8),
    "HD": (6, 12),
    "HN": (18, 12),
}

# Röda dagar och aftnar som markeras på sidan.
RED = {
    dt.date(2026, 12, 24): "Julafton",
    dt.date(2026, 12, 25): "Juldagen",
    dt.date(2026, 12, 26): "Annandag jul",
    dt.date(2026, 12, 31): "Nyårsafton",
    dt.date(2027, 1, 1): "Nyårsdagen",
    dt.date(2027, 1, 6): "Trettondedag jul",
    dt.date(2027, 3, 26): "Långfredagen",
    dt.date(2027, 3, 28): "Påskdagen",
    dt.date(2027, 3, 29): "Annandag påsk",
    dt.date(2027, 5, 1): "Första maj",
    dt.date(2027, 5, 6): "Kristi himmelsfärd",
    dt.date(2027, 6, 6): "Nationaldagen",
    dt.date(2027, 6, 25): "Midsommarafton",
    dt.date(2027, 6, 26): "Midsommardagen",
}

MAN = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
       "augusti", "september", "oktober", "november", "december"]
DAG = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"]


# ---------------------------------------------------------------------------
# Veckor
# ---------------------------------------------------------------------------

def week_type(iso_year, iso_week):
    """Veckotyp (A–E) för en vecka i 5-skiftet. Vecka 41 år 2026 är typ A."""
    if iso_year == 2026:
        index = iso_week - 41
    else:
        index = (53 - 41) + iso_week   # 2026 har 53 veckor
    return ORDER[index % 5]


def build_weeks():
    """Alla veckor från START till END med veckonummer, datum och pass."""
    weeks = []
    monday = START
    while monday <= END:
        iso_year, iso_week, _ = monday.isocalendar()
        if iso_year == 2026 and iso_week in SEPT:
            shifts = SEPT[iso_week]
        else:
            shifts = TYPES[week_type(iso_year, iso_week)]
        weeks.append({
            "iso": iso_week,
            "days": [monday + dt.timedelta(days=i) for i in range(7)],
            "shifts": shifts,
        })
        monday += dt.timedelta(days=7)
    return weeks


def group_by_month(weeks):
    """Delar upp veckorna per månad. En vecka hör till torsdagens månad."""
    groups = []
    for week in weeks:
        thursday = week["days"][3]
        key = (thursday.year, thursday.month)
        if not groups or groups[-1][0] != key:
            groups.append([key, []])
        groups[-1][1].append(week)
    return groups


def short_date(day):
    """Datum i kort form, till exempel "24 dec"."""
    return f"{day.day} {MAN[day.month - 1][:3]}"


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def cell_html(day, code):
    """En ruta i kalendern: datum överst, passkod under."""
    classes = ["d", "p-" + code if code else "p-off"]
    if day in RED:
        classes.append("red")
    if day > VERIFIED:
        classes.append("calc")   # uträknad dag. Klassen har ingen egen stil ännu.
    return (f'<td class="{" ".join(classes)}" data-d="{day.isoformat()}">'
            f'<span class="num">{day.day}</span>'
            f'<span class="code">{code or "–"}</span></td>')


def months_html(weeks):
    """Rubrik, tabell och röda dagar för varje månad."""
    lines = []
    for (year, month), month_weeks in group_by_month(weeks):
        lines.append(f'<h2 class="month">{MAN[month - 1]} <span>{year}</span></h2>')
        lines.append('<table class="grid">')
        lines.append("  <thead>")
        lines.append('    <tr><th class="wk">v</th>'
                     + "".join(f"<th>{name}</th>" for name in DAG) + "</tr>")
        lines.append("  </thead>")
        lines.append("  <tbody>")

        for week in month_weeks:
            is_free = not any(week["shifts"])
            lines.append(f'    <tr class="{"wrow free" if is_free else "wrow"}">')
            lines.append(f'      <th class="wk">{week["iso"]}</th>')
            for i in range(7):
                lines.append("      " + cell_html(week["days"][i], week["shifts"][i]))
            lines.append("    </tr>")
        lines.append("  </tbody>")
        lines.append("</table>")

        # Röda dagar i månaden, med vad som gäller just den dagen.
        notes = []
        for week in month_weeks:
            for i, day in enumerate(week["days"]):
                if day not in RED:
                    continue
                code = week["shifts"][i]
                what = f"{PASS[code][0].lower()} {PASS[code][1]}" if code else "ledig"
                notes.append(f"  <li><b>{short_date(day)}</b> {RED[day]} — {what}</li>")
        if notes:
            lines += ['<ul class="notes">'] + notes + ["</ul>"]
        lines.append("")   # tom rad mellan månaderna
    return "\n".join(lines).rstrip()


def legend_html():
    """Teckenförklaringen: ett märke per passkod, sist "Ledig"."""
    items = [
        f'<li><span class="chip p-{code}">{code}</span> {name} <em>{times}</em></li>'
        for code, (name, times) in PASS.items()
    ]
    items.append('<li><span class="chip p-off">–</span> Ledig</li>')
    return "\n  ".join(items)


def free_weeks_html(weeks):
    """Listan med hela lediga veckor."""
    return "\n    ".join(
        f'<li><b>v{week["iso"]}</b> {short_date(week["days"][0])}'
        f' – {short_date(week["days"][6])}</li>'
        for week in weeks if not any(week["shifts"])
    )


def weeks_json(weeks):
    """Veckodata till skriptet på sidan, en vecka per rad."""
    rows = [
        json.dumps({"iso": week["iso"],
                    "mon": week["days"][0].isoformat(),
                    "s": week["shifts"]}, ensure_ascii=False)
        for week in weeks
    ]
    return "[\n  " + ",\n  ".join(rows) + "\n]"


def fill(template, **values):
    """Byter ut __NAMN__ i mallen mot värdet med samma namn."""
    for name, value in values.items():
        template = template.replace(f"__{name.upper()}__", value)
    return template


STYLE = """\
/* Färger i ljust läge */
:root {
  --paper: #e9edf1;
  --card: #fff;
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
}

/* Färger i mörkt läge. Följer telefonens inställning. */
@media (prefers-color-scheme: dark) {
  :root {
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
    --offink: #6b7a8a;
    --ring: #e8edf3;
  }
}

/* Grund */
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "IBM Plex Sans", -apple-system, Segoe UI, sans-serif;
  -webkit-text-size-adjust: 100%;
}
.wrap {
  max-width: 660px;
  margin: 0 auto;
  padding: calc(20px + env(safe-area-inset-top)) 14px 60px;
}

/* Sidhuvud */
header {
  padding: 2px 2px 12px;
}
h1 {
  font-family: "IBM Plex Sans Condensed", sans-serif;
  font-weight: 700;
  font-size: 1.4rem;
  line-height: 1.1;
  margin: 0 0 2px;
  letter-spacing: -.01em;
}
.sub {
  color: var(--muted);
  font-size: .82rem;
  margin: 0;
}

/* Veckoremsor: den här veckan och nästa */
.now {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px 12px 12px;
  margin-bottom: 8px;
}
.now h3 {
  font-family: "IBM Plex Sans Condensed", sans-serif;
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
  font-family: "IBM Plex Sans Condensed", sans-serif;
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
  color: var(--ink);
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
.legend li:last-child .chip {
  grid-row: auto;
}
.legend em {
  display: block;
  font-style: normal;
  font-size: .74rem;
  color: var(--muted);
  line-height: 1.2;
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

/* Små passmärken i teckenförklaringen */
.chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 22px;
  border-radius: 5px;
  font-family: "IBM Plex Sans Condensed", sans-serif;
  font-weight: 700;
  font-size: .75rem;
}
.chip.p-off {
  border: 1px dashed var(--line);
}

/* Månadsrubrik och kalenderrutnät */
h2.month {
  font-family: "IBM Plex Sans Condensed", sans-serif;
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
}
table.grid thead th {
  font-size: .68rem;
  color: var(--muted);
  font-weight: 500;
  padding-bottom: 2px;
}
th.wk {
  width: 26px;
  font-family: "IBM Plex Sans Condensed", sans-serif;
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
  font-family: "IBM Plex Sans Condensed", sans-serif;
  font-weight: 700;
  font-size: .8rem;
  line-height: 1.2;
  opacity: .92;
}

/* Tillstånd: ledig vecka, passerad dag, i dag, röd dag */
tr.free th.wk {
  color: var(--hd);
}
td.past {
  filter: grayscale(1);
  opacity: .3;
}
td.past .num {
  opacity: 1;
}
td.today {
  border-color: var(--ring);
  box-shadow: 0 0 0 1.5px var(--ring);
}
td.red .num {
  color: #c0392b;
  opacity: 1;
  font-weight: 600;
}

/* Passfärger. Ljusa pass har mörk text, mörka pass har vit text. */
.p-FM {
  background: var(--fm);
  color: #16202e;
}
.p-EM {
  background: var(--em);
  color: #16202e;
}
.p-N {
  background: var(--n);
  color: #fff;
}
.p-HD {
  background: var(--hd);
  color: #16202e;
}
.p-HN {
  background: var(--hn);
  color: #fff;
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
.free-box h3 {
  font-family: "IBM Plex Sans Condensed", sans-serif;
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
  font-family: "IBM Plex Sans Condensed", sans-serif;
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

/* Smala telefoner */
@media (max-width:380px) {
  td .code {
    font-size: .8rem;
  }
}
"""

SCRIPT = """\
// Veckodata från byggskriptet.
// iso = veckonummer, mon = måndagens datum, s = pass måndag till söndag ("" = ledig).
const WEEKS = __WEEKS__;
const DAG = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"];

// Datum som "ÅÅÅÅ-MM-DD" i telefonens lokala tid.
function iso(d) {
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return d.getFullYear() + "-" + month + "-" + day;
}

const today = iso(new Date());

// Tona ner dagar som har passerat och rama in dagens datum.
document.querySelectorAll("td.d").forEach(td => {
  if (td.dataset.d < today) td.classList.add("past");
  if (td.dataset.d === today) td.classList.add("today");
});

// Bygger en veckoremsa: sju rutor med veckodag och pass.
function strip(week, rubrik) {
  let cells = "";
  for (let i = 0; i < 7; i++) {
    const pass = week.s[i];
    cells += '<div class="hd"><span>' + DAG[i] + '</span>' +
             '<em class="p-' + (pass || "off") + '">' + (pass || "–") + '</em></div>';
  }
  return '<div class="now"><h3>' + rubrik + ' (v' + week.iso + ')</h3>' +
         '<div class="hrow">' + cells + '</div></div>';
}

// Hitta veckan som innehåller dagens datum.
const current = WEEKS.findIndex(week => {
  const sunday = new Date(week.mon + "T00:00:00");
  sunday.setDate(sunday.getDate() + 6);
  return week.mon <= today && today <= iso(sunday);
});

// Visa den här veckan och nästa överst på sidan.
const hero = document.getElementById("hero");
if (current >= 0) {
  const next = WEEKS[current + 1];
  hero.innerHTML = strip(WEEKS[current], "Den här veckan") +
                   (next ? strip(next, "Nästa vecka") : "");
} else {
  // Dagens datum ligger utanför schemat.
  hero.innerHTML = '<div class="now"><h3>Schemat gäller 31 aug 2026 – 27 juni 2027</h3></div>';
}
"""

PAGE = """\
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skiftlag 2</title>

<!-- Ikon och utseende när sidan ligger på hemskärmen -->
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skift">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">

<!-- Typsnitt -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">

<style>
__STYLE__</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Skiftlag 2</h1>
  <p class="sub">Skiftschema · september 2026 – juni 2027</p>
</header>

<!-- Fylls av skriptet längst ner: den här veckan och nästa -->
<div id="hero"></div>

<ul class="legend">
  __LEGEND__
</ul>

<a class="cal" href="https://jockebolero.github.io/sk-3141c0/skiftlag2.ics">Lägg in alla pass i din kalender</a>

<!-- En tabell per månad -->
__MONTHS__

<div class="free-box">
  <h3>Hela veckor lediga</h3>
  <ul>
    __FREE__
  </ul>
</div>

<footer>
Skiftlag 2 går 5-skift sedan 3 oktober 2026. Cykeln upprepas var femte vecka:
två nätter → två förmiddagar och en natt → ledig vecka → två kvällar och två nätter →
fem dagpass. Storhelger körs som vanligt, så schemat rullar rakt igenom jul, nyår och påsk.
<br><br>
Avläst från utdelade schemablad till och med 27 december 2026.
Därefter uträknat på cykeln — stäm av mot nya blad när de kommer.
</footer>

</div>

<script>
__SCRIPT__</script>
</body>
</html>
"""


def build_page(weeks):
    """Hela sidan som en HTML-sträng."""
    script = fill(SCRIPT, weeks=weeks_json(weeks))
    return fill(
        PAGE,
        style=STYLE,
        legend=legend_html(),
        months=months_html(weeks),
        free=free_weeks_html(weeks),
        script=script,
    )


# ---------------------------------------------------------------------------
# Kalenderfil
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


def build_events(weeks):
    """Alla pass som (kod, start, slut)."""
    events = []
    for week in weeks:
        for i, code in enumerate(week["shifts"]):
            if not code:
                continue
            hour, length = TIMES[code]
            full_hour = dt.datetime.combine(week["days"][i], dt.time(hour, 0))
            start = full_hour - dt.timedelta(minutes=5)   # överlämning
            end = full_hour + dt.timedelta(hours=length)
            events.append((code, start, end))
    return events


def build_calendar(events):
    """Kalenderfilen som text. Formatet kräver radslut av typen CRLF."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Skiftlag2//Skiftschema//SV",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Skiftlag 2",
        "X-WR-TIMEZONE:Europe/Stockholm",
    ] + TIMEZONE

    for number, (code, start, end) in enumerate(events):
        lines += [
            "BEGIN:VEVENT",
            # UID måste vara unikt och får inte ändras, annars blir det dubbletter vid ny import.
            f"UID:skiftlag2-{stamp(start)}-{number}@skiftschema",
            "DTSTAMP:20261001T090000Z",
            f"DTSTART;TZID=Europe/Stockholm:{stamp(start)}",
            f"DTEND;TZID=Europe/Stockholm:{stamp(end)}",
            f"SUMMARY:Skift: {PASS[code][0]}",
            f"DESCRIPTION:Skiftlag 2 · {code} · {start:%H:%M}–{end:%H:%M}",
            "TRANSP:OPAQUE",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


# ---------------------------------------------------------------------------
# Kör
# ---------------------------------------------------------------------------

def main():
    weeks = build_weeks()
    events = build_events(weeks)

    with open(os.path.join(ROT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_page(weeks))

    # newline="" hindrar Python från att ändra radsluten i kalenderfilen.
    with open(os.path.join(ROT, "skiftlag2.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(build_calendar(events))

    free = [week["iso"] for week in weeks if not any(week["shifts"])]
    print(f"veckor: {len(weeks)} | pass: {len(events)}")
    print(f"hela lediga veckor: {free}")


if __name__ == "__main__":
    main()
