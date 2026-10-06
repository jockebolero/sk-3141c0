"""Bygger sidan för skiftlag 2.

Skriver två filer i repots rot:
    index.html      sidans innehåll, med en tabell per månad
    skiftlag2.ics   kalenderfilen bakom knappen på sidan

Utseendet ligger i style.css och logiken i script.js. De filerna skrivs
för hand och ändras inte av det här skriptet.

Kör:
    python3 build/skiftlag2.py

Schemat ändras i avsnittet "Schemadata" här nedanför.
"""
import datetime as dt
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


def fill(template, **values):
    """Byter ut __NAMN__ i mallen mot värdet med samma namn."""
    for name, value in values.items():
        template = template.replace(f"__{name.upper()}__", value)
    return template


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

<!-- Utseende och logik. defer gör att skriptet körs när hela sidan är inläst. -->
<link rel="stylesheet" href="style.css">
<script src="script.js" defer></script>
</head>
<body>
<div class="wrap">

<header>
  <h1>Skiftlag 2</h1>
  <p class="sub">Skiftschema · september 2026 – juni 2027</p>
</header>

<!-- Fylls av script.js: den här veckan och nästa -->
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
</body>
</html>
"""


def build_page(weeks):
    """Hela sidan som en HTML-sträng."""
    return fill(
        PAGE,
        legend=legend_html(),
        months=months_html(weeks),
        free=free_weeks_html(weeks),
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
