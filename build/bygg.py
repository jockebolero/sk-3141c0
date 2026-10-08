"""Bygger skiftschemat för alla skiftlagen.

Gjord av J. Stork.

Skriver till repots rot, det som visas på webben:
    index.html                      sidans innehåll
    data.js                         schemadatan som script.js använder
    skiftlag1.ics – skiftlag5.ics   kalenderfilerna bakom knapparna på sidan

Utseendet ligger i style.css och logiken i script.js. De filerna skrivs
för hand och ändras inte av det här skriptet. Det gör inte heller sw.js
(offline-stödet), manifest.webmanifest, typsnitten eller ikonerna.

Skriptet skriver också build/ut/forhandsvisning.html: hela appen i en enda
fil, utan kalenderknappar. Den följer inte med till GitHub.

Kör:
    python3 build/bygg.py

Schemat ändras i avsnittet "Schemadata" här nedanför.
"""
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(HERE)       # repots rot, det som visas på webben
UT = os.path.join(HERE, "ut")     # förhandsvisningen, följer inte med till GitHub


# ---------------------------------------------------------------------------
# Schemadata
# ---------------------------------------------------------------------------

START = dt.date(2026, 10, 5)   # måndag vecka 41, första hela veckan i 5-skiftet
END = dt.date(2027, 6, 27)     # söndag vecka 25, midsommarveckan

# Sista dagen som är avläst från utdelade schemablad. Veckor efter den är
# uträknade på cykeln och märks som preliminära på sidan.
# Sätt till None om hela perioden är bekräftad.
CONFIRMED = dt.date(2026, 12, 27)

# Veckotyperna som upprepas i ordningen A, B, C, D, E.
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
# Namnen får inte innehålla kommatecken, eftersom de också står i kalenderfilerna.
PASS = {
    "FM": ("Förmiddag", "05:55–14:00", 6, 8),
    "EM": ("Eftermiddag", "13:55–22:00", 14, 8),
    "N": ("Natt", "21:55–06:00", 22, 8),
    "HD": ("Helgpass dag", "05:55–18:00", 6, 12),
    "HN": ("Helgpass natt", "17:55–06:00", 18, 12),
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
# Texter och inställningar
# ---------------------------------------------------------------------------

TITLE = "Skiftschema"
DESCRIPTION = "Skiftschema för alla lag."

# Raden under teckenförklaringen. Tom sträng = ingen rad.
PASS_NOTE = "Passen börjar fem minuter före hel timme för överlämning."

# Om sidan ska döljas för sökmotorer. Den är till för kollegorna, inte för Google.
NOINDEX = True

# Vem som har gjort appen. Visas i sidfoten och i sidans metadata.
# Sidfoten följer varumarke/README.md: "Gjord av J. Stork · Digitalt hantverk".
# Namnet i sidfoten länkar till webbplatsen.
CREDIT = "J. Stork"
CREDIT_URL = "https://jstork.se"
TAGLINE = "Digitalt hantverk"

# Förhandsvisningen kan inte läsa typsnittsfilerna i mappen typsnitt/,
# så den hämtar samma typsnitt från Google i stället.
PREVIEW_FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@600;700"
                 "&family=IBM+Plex+Sans:wght@400;500;600&display=swap")

DAGAR = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"]
MANADER = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
           "augusti", "september", "oktober", "november", "december"]


# ---------------------------------------------------------------------------
# Veckor
# ---------------------------------------------------------------------------

def shifts(lag, monday):
    """Passen måndag till söndag för ett lag, veckan som börjar på monday."""
    weeks_from_start = (monday - START).days // 7
    return TYPES[ORDER[(OFFSET[lag] + weeks_from_start) % len(ORDER)]]


def build_weeks():
    """Alla veckor i perioden som [måndagens datum, veckonummer]."""
    weeks = []
    monday = START
    while monday <= END:
        weeks.append([monday.isoformat(), monday.isocalendar()[1]])
        monday += dt.timedelta(days=7)
    return weeks


def long_date(day):
    """Datum i löptext, till exempel 5 oktober 2026."""
    return f"{day.day} {MANADER[day.month - 1]} {day.year}"


# ---------------------------------------------------------------------------
# Sidan
# ---------------------------------------------------------------------------

# Sidans innehåll. Samma i den färdiga appen och i förhandsvisningen.
BODY = """\
<div class="wrap">

<header class="top">
  <p class="overline">Skiftschema</p>
  <h1 id="rubrik">Välj ditt lag</h1>
  <div class="seg" role="group" aria-label="Lag">
    __BUTTONS__
  </div>
</header>

<!-- Visas tills man har valt lag -->
<p class="hint" id="valj">Välj ditt lag här ovanför, så visas schemat. Valet sparas i telefonen.</p>

<!-- Visas när man har valt lag. Innehållet fylls av script.js. -->
<main id="schema" hidden>

  <section class="card next" id="next" aria-label="I dag, nästa pass och nästa ledighet"></section>

  <section class="card" id="weeks" aria-label="Den här veckan och nästa"></section>

  <div id="months"></div>

  <section class="card">
    <h2 id="freeh">Hela veckor lediga</h2>
    <ul class="free" id="free"></ul>
    <p class="fine" id="freenote" hidden>* Preliminärt, uträknat på cykeln.</p>
  </section>

  <section class="card">
    <h2>Passen</h2>
    <ul class="legend">
      __LEGEND__
    </ul>
    __PASSNOTE__
  </section>

  <!-- Hopfälld från början. Den läser man en gång. -->
  <details class="card fold">
    <summary>Så går cykeln</summary>
    <p class="fine">Alla lagen går samma __CYCLELENGTH__ veckor, förskjutna en vecka i taget.</p>
    __CYCLE__
  </details>
__CALENDAR__
</main>

<footer>
__FOOTER__
<p class="maker">Gjord av <a href="__CREDITURL__"><b>__CREDIT__</b></a> · __TAGLINE__</p>
</footer>

</div>
"""

# Kalenderdelen. Finns bara på den utlagda sidan, eftersom kalenderfilerna
# inte följer med i förhandsvisningen. Länkarna fylls i av script.js.
CALENDAR = """
  <section class="card">
    <h2>Lägg in passen i din kalender</h2>
    <p class="fine">En prenumeration uppdateras av sig själv om schemat ändras.</p>
    <!-- script.js sätter adresserna och lägger rätt knapp först för telefonen man har -->
    <div class="calbuttons" id="cal-buttons">
      <a class="button" id="cal-apple" href="#">Apple Kalender<small>iPhone, iPad och Mac</small></a>
      <a class="button" id="cal-google" href="#">Google Kalender<small>Android, eller på datorn</small></a>
    </div>
    <details class="calhelp">
      <summary>Fungerar inte knapparna?</summary>
      <p class="fine">Kopiera adressen och lägg in den för hand.</p>
      <div class="copy">
        <input type="text" id="cal-address" readonly aria-label="Kalenderns adress">
        <button type="button" id="cal-copy">Kopiera</button>
      </div>
      <p class="fine" id="cal-copied" role="status"></p>
      <p class="fine"><b>Google Kalender:</b> öppna calendar.google.com i webbläsaren, inte i appen.
         Välj <b>+</b> vid <b>Andra kalendrar</b>, sedan <b>Från webbadress</b>, och klistra in adressen.
         Syns passen inte i appen på telefonen? Slå på <b>Synkronisera</b> för kalendern i appens inställningar.</p>
      <p class="fine"><b>Apple Kalender på Mac:</b> öppna appen Kalender, välj
         <b>Arkiv → Ny kalenderprenumeration</b> och klistra in adressen.</p>
    </details>
    <a class="textlink" id="cal-file" href="#">Ladda ner som fil i stället</a>
    <p class="fine">Har du redan lagt in filen? Ta bort de gamla passen först, annars visas de dubbelt.</p>
  </section>
"""

# Sidan: ett helt HTML-dokument som hämtar stil, data och logik från egna filer.
DOCUMENT = """\
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<meta name="author" content="__CREDIT__">
__ROBOTS__
<!-- Ikon och utseende när sidan ligger på hemskärmen -->
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skiftschema">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">

<!-- Typsnittet som används mest laddas i förväg så att texten inte hoppar -->
<link rel="preload" href="typsnitt/ibm-plex-sans-400.woff2" as="font" type="font/woff2" crossorigin>

<!-- Utseende, schemadata och logik. defer gör att skripten körs i ordning
     när hela sidan är inläst. data.js måste komma före script.js. -->
<link rel="stylesheet" href="style.css">
<script src="data.js" defer></script>
<script src="script.js" defer></script>
</head>
<body>
__BODY__</body>
</html>
"""

# Förhandsvisningen: samma app i en enda fil. Claude lägger själv till
# dokumentets ram runt innehållet, så här finns ingen <html> eller <body>.
PREVIEW = """\
<title>__TITLE__</title>
<meta name="author" content="__CREDIT__">
<link rel="stylesheet" href="__FONTS__">
<style>
__STYLE__</style>

__BODY__
<script>
__DATA__
__SCRIPT__</script>
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
        f'<li><span class="chip p-{code}">{code}</span><span>{name}<em>{times}</em></span></li>'
        for code, (name, times, _, _) in PASS.items()
    ]
    items.append('<li><span class="chip p-off">–</span><span>Ledig</span></li>')
    return "\n      ".join(items)


def cycle_html():
    """Cykeln som en liten tabell: en rad per vecka, ett märke per dag."""
    head = "".join(f'<th scope="col">{dag}</th>' for dag in DAGAR)
    rows = []
    for number, letter in enumerate(ORDER, start=1):
        cells = "".join(
            f'<td><span class="chip p-{code or "off"}">{code or "–"}</span></td>'
            for code in TYPES[letter]
        )
        rows.append(f'<tr><th scope="row">Vecka {number}</th>{cells}</tr>')
    return (
        '<table class="cycle">\n'
        f'      <thead><tr><td></td>{head}</tr></thead>\n'
        '      <tbody>\n        ' + "\n        ".join(rows) + '\n      </tbody>\n'
        '    </table>'
    )


def buttons_html():
    """Knapparna i lagväljaren, en per lag."""
    return "\n    ".join(
        f'<button type="button" data-lag="{lag}" aria-pressed="false" '
        f'aria-label="Lag {lag}"><span>Lag</span> {lag}</button>'
        for lag in sorted(OFFSET)
    )


def footer_html():
    """Texten i sidfoten: vilken period schemat gäller och hur mycket som är bekräftat."""
    period = f"<p>Schemat gäller {long_date(START)} – {long_date(END)}. Storhelger körs som vanligt.</p>"
    if CONFIRMED is None or CONFIRMED >= END:
        return period + "\n<p>Avläst från utdelade schemablad.</p>"
    return (
        period + "\n"
        f"<p>Avläst från utdelade schemablad till och med {long_date(CONFIRMED)}. "
        "Därefter uträknat på cykeln och märkt som preliminärt. "
        "Stäm av mot nya blad när de kommer.</p>"
    )


def body_html(with_calendar):
    """Sidans innehåll. Kalenderdelen finns bara på den utlagda sidan."""
    return fill(
        BODY,
        buttons=buttons_html(),
        legend=legend_html(),
        cycle=cycle_html(),
        cyclelength=str(len(ORDER)),
        calendar=CALENDAR if with_calendar else "",
        passnote=f'<p class="fine">{PASS_NOTE}</p>' if PASS_NOTE else "",
        footer=footer_html(),
        credit=CREDIT,
        crediturl=CREDIT_URL,
        tagline=TAGLINE,
    )


def data_js(weeks, calendar_address):
    """Innehållet i data.js: schemadatan som script.js använder."""
    confirmed = CONFIRMED.isoformat() if CONFIRMED and CONFIRMED < END else ""
    return "\n".join([
        "// Skapad av build/bygg.py. Ändra inte här, ändra i byggskriptet.",
        "",
        "// Varje vecka i perioden: [måndagens datum, veckonummer].",
        f"const WEEKS = {rows_to_js(weeks)};",
        "",
        "// Veckotyperna i cykeln. Pass måndag till söndag, \"\" = ledig.",
        f"const TYPES = {dict_to_js(TYPES)};",
        f"const ORDER = {to_js(ORDER)};",
        "",
        "// Var i cykeln varje lag står första veckan (0 = A, 1 = B, ...).",
        f"const OFFSET = {to_js(OFFSET)};",
        "",
        "// Passkod -> [namn, tider, hel timme då passet börjar, längd i timmar].",
        f"const PASS = {dict_to_js({code: list(values) for code, values in PASS.items()})};",
        "",
        "// Datum -> helgdagens namn.",
        f"const RED = {dict_to_js(RED)};",
        "",
        "// Sista dagen som är bekräftad. Veckor efter den är preliminära. Tom = allt bekräftat.",
        f"const CONFIRMED = {to_js(confirmed)};",
        "",
        "// Adress till kalenderfilen, där {n} byts mot lagnumret. Tom i förhandsvisningen.",
        f"const CAL = {to_js(calendar_address)};",
        "",
    ])


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

def read_source(name):
    with open(os.path.join(ROT, name), encoding="utf-8") as f:
        return f.read()


def write(folder, name, text, newline=None):
    with open(os.path.join(folder, name), "w", encoding="utf-8", newline=newline) as f:
        f.write(text)


def main():
    os.makedirs(UT, exist_ok=True)
    weeks = build_weeks()
    style = read_source("style.css")
    script = read_source("script.js")
    robots = '<meta name="robots" content="noindex">\n' if NOINDEX else ""

    for code, (name, _, _, _) in PASS.items():
        if "," in name or ";" in name:
            raise SystemExit(f"Passnamnet för {code} får inte innehålla komma eller semikolon: {name}")

    # Sidan och schemadatan. {n} i adressen byts mot lagnumret av script.js.
    write(ROT, "index.html", fill(DOCUMENT, title=TITLE, description=DESCRIPTION, credit=CREDIT,
                                  robots=robots, body=body_html(True)))
    write(ROT, "data.js", data_js(weeks, "skiftlag{n}.ics"))

    # Förhandsvisningen: allt i en fil. Den saknar kalenderdel, eftersom
    # kalenderfilerna bara finns på den utlagda sidan.
    write(UT, "forhandsvisning.html", fill(
        PREVIEW,
        title=TITLE,
        credit=CREDIT,
        fonts=PREVIEW_FONTS,
        style=style,
        body=body_html(False),
        data=data_js(weeks, ""),
        script=script,
    ))

    for lag in sorted(OFFSET):
        text, count = build_calendar(lag, weeks)
        # newline="" hindrar Python från att ändra radsluten i kalenderfilen.
        write(ROT, f"skiftlag{lag}.ics", text, newline="")
        print(f"lag {lag}: {count} pass")

    print(f"veckor: {len(weeks)}, från {weeks[0][0]} till och med vecka {weeks[-1][1]}")


if __name__ == "__main__":
    main()
