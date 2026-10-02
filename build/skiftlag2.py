"""Bygger sidan för skiftlag 2: index.html och skiftlag2.ics i repots rot.

Kör: python3 build/skiftlag2.py
"""
import datetime as dt, json

START = dt.date(2026, 8, 31)
END   = dt.date(2027, 6, 27)
# Sista datum som är avläst från utdelat schemablad:
VERIFIED = dt.date(2026, 12, 27)

SEPT = {
    36: ["EM","EM","EM","EM","",  "",""],
    37: ["FM","FM","FM","FM","FM","",""],
    38: ["N", "N", "N", "N", "",  "",""],
    39: ["EM","EM","EM","EM","",  "",""],
    40: ["FM","FM","FM","FM","FM","",""],
}
TYPES = {
 "A": ["N","N","","","FM","HD","HD"],
 "B": ["","","FM","FM","N","HN","HN"],
 "C": ["","","","","","",""],
 "D": ["EM","EM","N","N","","",""],
 "E": ["FM","FM","EM","EM","EM","",""],
}
ORDER = "ABCDE"

def week_type(iy, iw):
    idx = iw - 41 if iy == 2026 else (53 - 41) + iw
    return ORDER[idx % 5]

RED = {
 dt.date(2026,12,24): "Julafton",
 dt.date(2026,12,25): "Juldagen",
 dt.date(2026,12,26): "Annandag jul",
 dt.date(2026,12,31): "Nyårsafton",
 dt.date(2027,1,1):   "Nyårsdagen",
 dt.date(2027,1,6):   "Trettondedag jul",
 dt.date(2027,3,26):  "Långfredagen",
 dt.date(2027,3,28):  "Påskdagen",
 dt.date(2027,3,29):  "Annandag påsk",
 dt.date(2027,5,1):   "Första maj",
 dt.date(2027,5,6):   "Kristi himmelsfärd",
 dt.date(2027,6,6):   "Nationaldagen",
 dt.date(2027,6,25):  "Midsommarafton",
 dt.date(2027,6,26):  "Midsommardagen",
}

PASS = {
 "FM": ("Förmiddag", "05:55–14:00"),
 "EM": ("Eftermiddag", "13:55–22:00"),
 "N":  ("Natt", "21:55–06:00"),
 "HD": ("Helgdag", "05:55–18:00"),
 "HN": ("Helgnatt", "17:55–06:00"),
}

MAN = ["januari","februari","mars","april","maj","juni","juli",
       "augusti","september","oktober","november","december"]
DAG = ["Mån","Tis","Ons","Tors","Fre","Lör","Sön"]

weeks = []
d = START
while d <= END:
    iy, iw, _ = d.isocalendar()
    shifts = SEPT[iw] if (iy == 2026 and iw in SEPT) else TYPES[week_type(iy, iw)]
    weeks.append({"iso": iw, "days": [d + dt.timedelta(days=i) for i in range(7)],
                  "shifts": shifts})
    d += dt.timedelta(days=7)

groups = []
for w in weeks:
    key = (w["days"][3].year, w["days"][3].month)
    if not groups or groups[-1][0] != key:
        groups.append([key, []])
    groups[-1][1].append(w)

def cell(day, code):
    cls = ["d", "p-" + code if code else "p-off"]
    if day in RED:
        cls.append("red")
    if day > VERIFIED:
        cls.append("calc")
    return (f'<td class="{" ".join(cls)}" data-d="{day.isoformat()}">'
            f'<span class="num">{day.day}</span>'
            f'<span class="code">{code or "–"}</span></td>')

rows = []
for (yr, mo), ws in groups:
    rows.append(f'<h2 class="month">{MAN[mo-1]} <span>{yr}</span></h2>')
    rows.append('<table class="grid"><thead><tr><th class="wk">v</th>' +
                "".join(f"<th>{x}</th>" for x in DAG) + "</tr></thead><tbody>")
    for w in ws:
        free = not any(w["shifts"])
        cells = "".join(cell(w["days"][i], w["shifts"][i]) for i in range(7))
        rows.append(f'<tr class="{"wrow free" if free else "wrow"}">'
                    f'<th class="wk">{w["iso"]}</th>{cells}</tr>')
    rows.append("</tbody></table>")
    notes = []
    for w in ws:
        for i, day in enumerate(w["days"]):
            if day in RED:
                c = w["shifts"][i]
                what = f"{PASS[c][0].lower()} {PASS[c][1]}" if c else "ledig"
                notes.append(f'<li><b>{day.day} {MAN[day.month-1][:3]}</b> {RED[day]} — {what}</li>')
    if notes:
        rows.append('<ul class="notes">' + "".join(notes) + "</ul>")

WEEKDATA = json.dumps([{"iso": w["iso"], "mon": w["days"][0].isoformat(),
                        "s": w["shifts"]} for w in weeks], ensure_ascii=False)

legend = "".join(f'<li><span class="chip p-{k}">{k}</span> {v[0]} <em>{v[1]}</em></li>'
                 for k, v in PASS.items()) + '<li><span class="chip p-off">–</span> Ledig</li>'

free_weeks = [w for w in weeks if not any(w["shifts"])]
free_list = "".join(
    f'<li><b>v{w["iso"]}</b> {w["days"][0].day} {MAN[w["days"][0].month-1][:3]}'
    f' – {w["days"][6].day} {MAN[w["days"][6].month-1][:3]}</li>' for w in free_weeks)

html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skiftlag 2</title>
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skift">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --paper:#e9edf1; --card:#fff; --ink:#16202e; --muted:#4d5c6e; --line:#c9d3dd;
  --fm:#ffd166; --em:#e8833a; --n:#2e3a66;
  --hd:linear-gradient(135deg,#ffd166 0%,#ffd166 42%,#e8833a 100%);
  --hn:linear-gradient(135deg,#473d6b 0%,#141a30 100%);
  --off:#f2f5f8; --offink:#75828f; --ring:#16202e;
}}
@media (prefers-color-scheme: dark) {{
 :root {{
  --paper:#11161f; --card:#1a212c; --ink:#e8edf3; --muted:#8c9bab; --line:#2c3745;
  --fm:#e5b94d; --em:#cf6f2b; --n:#4a5a96;
  --hd:linear-gradient(135deg,#e5b94d 0%,#e5b94d 42%,#cf6f2b 100%);
  --hn:linear-gradient(135deg,#5a4e85 0%,#232c45 100%);
  --off:#1f2733; --offink:#6b7a8a; --ring:#e8edf3;
 }}
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,Segoe UI,sans-serif;-webkit-text-size-adjust:100%}}
.wrap{{max-width:660px;margin:0 auto;
  padding:calc(20px + env(safe-area-inset-top)) 14px 60px}}
header{{padding:2px 2px 12px}}
h1{{font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:700;font-size:1.4rem;
  line-height:1.1;margin:0 0 2px;letter-spacing:-.01em}}
.sub{{color:var(--muted);font-size:.82rem;margin:0}}
.now{{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:14px 12px 12px;margin-bottom:8px}}
.now h3{{font-family:"IBM Plex Sans Condensed",sans-serif;font-size:.95rem;margin:0 0 10px;
  font-weight:600;color:var(--muted)}}
.hrow{{display:flex;gap:4px}}
.hd{{flex:1;text-align:center}}
.hd span{{display:block;font-size:.66rem;color:var(--muted);margin-bottom:3px}}
.hd em{{display:block;font-style:normal;font-family:"IBM Plex Sans Condensed",sans-serif;
  font-weight:700;font-size:.86rem;padding:9px 0;border-radius:6px}}
.legend{{list-style:none;padding:0;margin:14px 0 22px;display:grid;
  grid-template-columns:1fr 1fr;gap:10px 14px;font-size:.84rem;color:var(--ink)}}
.legend li{{display:grid;grid-template-columns:auto 1fr;column-gap:8px;align-items:center}}
.legend li .chip{{grid-row:span 2}}
.legend li:last-child .chip{{grid-row:auto}}
.legend em{{display:block;font-style:normal;font-size:.74rem;color:var(--muted);line-height:1.2}}
.cal{{display:block;text-align:center;padding:12px;margin:-8px 0 20px;border-radius:10px;
  background:var(--card);border:1px solid var(--line);color:var(--ink);
  font-weight:600;font-size:.9rem;text-decoration:none}}
.cal:focus-visible{{outline:2px solid var(--ring);outline-offset:2px}}
.chip{{display:inline-flex;align-items:center;justify-content:center;width:34px;height:22px;
  border-radius:5px;font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:700;font-size:.75rem}}
.chip.p-off{{border:1px dashed var(--line)}}
h2.month{{font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:600;font-size:1.05rem;
  margin:22px 0 8px;padding-bottom:5px;border-bottom:2px solid var(--ink)}}
h2.month span{{color:var(--muted);font-weight:500}}
table.grid{{width:100%;border-collapse:separate;border-spacing:3px;table-layout:fixed}}
table.grid thead th{{font-size:.68rem;color:var(--muted);font-weight:500;padding-bottom:2px}}
th.wk{{width:26px;font-family:"IBM Plex Sans Condensed",sans-serif;font-size:.75rem;
  color:var(--muted);font-weight:600}}
td.d{{border-radius:6px;text-align:center;padding:6px 1px 5px;border:1px solid transparent}}
td .num{{display:block;font-size:.72rem;opacity:.9;line-height:1.1;font-weight:500}}
td .code{{display:block;font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:700;
  font-size:.8rem;line-height:1.2;opacity:.92}}
tr.free th.wk{{color:var(--hd)}}
td.past{{filter:grayscale(1);opacity:.3}}
td.past .num{{opacity:1}}
td.today{{border-color:var(--ring);box-shadow:0 0 0 1.5px var(--ring)}}
td.red .num{{color:#c0392b;opacity:1;font-weight:600}}
.p-FM{{background:var(--fm);color:#16202e}} .p-EM{{background:var(--em);color:#16202e}}
.p-N{{background:var(--n);color:#fff}} .p-HD{{background:var(--hd);color:#16202e}}
.p-HN{{background:var(--hn);color:#fff}} .p-off{{background:var(--off);color:var(--offink)}}
ul.notes{{list-style:none;padding:8px 10px;margin:8px 0 0;background:var(--card);
  border-radius:8px;border:1px solid var(--line);font-size:.82rem;color:var(--muted)}}
ul.notes li{{padding:2px 0}}
ul.notes b{{color:var(--ink)}}
.free-box{{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:14px 14px 12px;margin-top:30px}}
.free-box h3{{font-family:"IBM Plex Sans Condensed",sans-serif;margin:0 0 8px;font-size:1rem}}
.free-box ul{{list-style:none;padding:0;margin:0;font-size:.88rem;color:var(--muted);
  columns:2;column-gap:16px}}
.free-box li{{padding:2px 0;break-inside:avoid}}
.free-box b{{color:var(--ink);font-family:"IBM Plex Sans Condensed",sans-serif}}
footer{{margin-top:26px;font-size:.78rem;color:var(--muted);line-height:1.5;
  border-top:1px solid var(--line);padding-top:12px}}
@media (max-width:380px){{ td .code{{font-size:.8rem}} }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Skiftlag 2</h1>
  <p class="sub">Skiftschema · september 2026 – juni 2027</p>
</header>

<div id="hero"></div>

<ul class="legend">{legend}</ul>

<a class="cal" href="https://jockebolero.github.io/sk-3141c0/skiftlag2.ics">Lägg in alla pass i din kalender</a>

{"".join(rows)}

<div class="free-box">
  <h3>Hela veckor lediga</h3>
  <ul>{free_list}</ul>
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
const WEEKS = {WEEKDATA};
const DAG = ["Mån","Tis","Ons","Tors","Fre","Lör","Sön"];
function iso(d){{return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")
  +"-"+String(d.getDate()).padStart(2,"0");}}
const today = iso(new Date());

document.querySelectorAll("td.d").forEach(td => {{
  if (td.dataset.d < today) td.classList.add("past");
  if (td.dataset.d === today) td.classList.add("today");
}});

function strip(w, rubrik) {{
  let c = "";
  for (let i = 0; i < 7; i++) {{
    const p = w.s[i];
    c += '<div class="hd"><span>' + DAG[i] + '</span><em class="p-' +
         (p || "off") + '">' + (p || "\\u2013") + '</em></div>';
  }}
  return '<div class="now"><h3>' + rubrik + ' (v' + w.iso + ')</h3>' +
         '<div class="hrow">' + c + '</div></div>';
}}

const i = WEEKS.findIndex(w => {{
  const m = new Date(w.mon + "T00:00:00");
  m.setDate(m.getDate() + 6);
  return w.mon <= today && today <= iso(m);
}});
const hero = document.getElementById("hero");
if (i >= 0) {{
  hero.innerHTML = strip(WEEKS[i], "Den här veckan") +
    (WEEKS[i+1] ? strip(WEEKS[i+1], "N\\u00e4sta vecka") : "");
}} else {{
  hero.innerHTML = '<div class="now"><h3>Schemat g\\u00e4ller 31 aug 2026 \\u2013 27 juni 2027</h3></div>';
}}
</script>
</body>
</html>
"""

import os
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repots rot
with open(os.path.join(ROT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# ---- kalenderfil ----
TIMES = {"FM": (6, 8), "EM": (14, 8), "N": (22, 8), "HD": (6, 12), "HN": (18, 12)}
ev = []
for w in weeks:
    for i, code in enumerate(w["shifts"]):
        if code:
            h, dur = TIMES[code]
            hel = dt.datetime.combine(w["days"][i], dt.time(h, 0))
            s = hel - dt.timedelta(minutes=5)   # börjar 5 min före hel timme
            ev.append((code, s, hel + dt.timedelta(hours=dur)))

g = lambda x: x.strftime("%Y%m%dT%H%M%S")
L = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Skiftlag2//Skiftschema//SV",
     "CALSCALE:GREGORIAN","METHOD:PUBLISH","X-WR-CALNAME:Skiftlag 2",
     "X-WR-TIMEZONE:Europe/Stockholm",
     "BEGIN:VTIMEZONE","TZID:Europe/Stockholm",
     "BEGIN:DAYLIGHT","TZOFFSETFROM:+0100","TZOFFSETTO:+0200","TZNAME:CEST",
     "DTSTART:19700329T020000","RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU","END:DAYLIGHT",
     "BEGIN:STANDARD","TZOFFSETFROM:+0200","TZOFFSETTO:+0100","TZNAME:CET",
     "DTSTART:19701025T030000","RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU","END:STANDARD",
     "END:VTIMEZONE"]
for n, (code, s, e) in enumerate(ev):
    L += ["BEGIN:VEVENT", f"UID:skiftlag2-{g(s)}-{n}@skiftschema",
          "DTSTAMP:20261001T090000Z",
          f"DTSTART;TZID=Europe/Stockholm:{g(s)}",
          f"DTEND;TZID=Europe/Stockholm:{g(e)}",
          f"SUMMARY:Skift: {PASS[code][0]}",
          f"DESCRIPTION:Skiftlag 2 · {code} · {s:%H:%M}–{e:%H:%M}",
          "TRANSP:OPAQUE", "END:VEVENT"]
L.append("END:VCALENDAR")
with open(os.path.join(ROT, "skiftlag2.ics"), "w", encoding="utf-8") as f:
    f.write("\r\n".join(L) + "\r\n")

print("veckor:", len(weeks), "| pass:", len(ev))
print("lediga veckor:", [w["iso"] for w in free_weeks])
for w in weeks:
    if w["iso"] in (49, 50, 51, 52) and w["days"][0].month == 12 or \
       (w["iso"] == 49 and w["days"][0].month == 11):
        print("v%s" % w["iso"], w["days"][0], w["shifts"])
