"""Bygger skiftschemat för alla fem skiftlagen.

Gjord av J. Stork.

Skriver till repots rot, det som visas på webben:
    index.html                      sidans innehåll
    data.js                         schemadatan som script.js använder
    skiftlag1.ics – skiftlag5.ics   kalenderfilerna bakom knappen på sidan

Utseendet ligger i style.css och logiken i script.js. De filerna skrivs
för hand och ändras inte av det här skriptet.

Skriptet skriver också build/ut/forhandsvisning.html: hela appen i en enda
fil, utan kalenderknapp. Den följer inte med till GitHub.

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

# Sidans innehåll. Samma i den färdiga appen och i förhandsvisningen.
BODY = """\
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

<!-- Fylls av script.js: den här veckan och nästa -->
<div id="hero"></div>

<ul class="legend">
  __LEGEND__
</ul>
__CALBUTTON__
<!-- Fylls av script.js: en tabell per månad -->
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
<p class="maker">Gjord av <b>__CREDIT__</b> · __TAGLINE__</p>
</footer>

</div>
"""

TITLE = "Skiftschema alla lag"

# Vem som har gjort appen. Visas i sidfoten och i sidans metadata.
# När webbplatsen är uppe kan namnet i sidfoten göras till en länk i BODY.
CREDIT = "J. Stork"
TAGLINE = "Digitalt hantverk"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700"
         "&family=IBM+Plex+Sans:wght@400;500;600&display=swap")

# Sidan: ett helt HTML-dokument som hämtar stil, data och logik från egna filer.
DOCUMENT = """\
<!DOCTYPE html>
<html lang="sv" class="fristaende">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<meta name="author" content="__CREDIT__">

<!-- Ikon och utseende när sidan ligger på hemskärmen -->
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skift">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">

<!-- Typsnitt -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="__FONTS__">

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


def body_html(with_calendar_button):
    """Sidans innehåll. Kalenderknappen finns bara på den utlagda sidan."""
    if with_calendar_button:
        cal_button = '\n<a class="cal" id="cal" href="#">Lägg in passen i din kalender</a>\n'
    else:
        cal_button = ""
    return fill(BODY, buttons=buttons_html(), legend=legend_html(), calbutton=cal_button,
                credit=CREDIT, tagline=TAGLINE)


def data_js(weeks, calendar_address):
    """Innehållet i data.js: schemadatan som script.js använder."""
    passes = {code: [name, times] for code, (name, times, _, _) in PASS.items()}
    return "\n".join([
        "// Skapad av build/bygg.py. Ändra inte här, ändra i byggskriptet.",
        "",
        "// Varje vecka i perioden: [måndagens datum, veckonummer].",
        f"const WEEKS = {rows_to_js(weeks)};",
        "",
        "// De fem veckotyperna i cykeln. Pass måndag till söndag, \"\" = ledig.",
        f"const TYPES = {dict_to_js(TYPES)};",
        f"const ORDER = {to_js(ORDER)};",
        "",
        "// Var i cykeln varje lag står första veckan (0 = A, 1 = B, ...).",
        f"const OFFSET = {to_js(OFFSET)};",
        "",
        "// Passkod -> [namn, tider].",
        f"const PASS = {dict_to_js(passes)};",
        "",
        "// Datum -> helgdagens namn.",
        f"const RED = {dict_to_js(RED)};",
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

    # Sidan och schemadatan. {n} i adressen byts mot lagnumret av script.js.
    write(ROT, "index.html", fill(DOCUMENT, title=TITLE, credit=CREDIT, fonts=FONTS,
                                  body=body_html(True)))
    write(ROT, "data.js", data_js(weeks, "skiftlag{n}.ics"))

    # Förhandsvisningen: allt i en fil. Den saknar kalenderknapp, eftersom
    # kalenderfilerna bara finns på den utlagda sidan.
    write(UT, "forhandsvisning.html", fill(
        PREVIEW,
        title=TITLE,
        credit=CREDIT,
        fonts=FONTS,
        style=style,
        body=body_html(False),
        data=data_js(weeks, ""),
        script=script,
    ))

    for lag in range(1, 6):
        text, count = build_calendar(lag, weeks)
        # newline="" hindrar Python från att ändra radsluten i kalenderfilen.
        write(ROT, f"skiftlag{lag}.ics", text, newline="")
        print(f"lag {lag}: {count} pass")

    print(f"veckor: {len(weeks)}, från {weeks[0][0]} till och med vecka {weeks[-1][1]}")


if __name__ == "__main__":
    main()
