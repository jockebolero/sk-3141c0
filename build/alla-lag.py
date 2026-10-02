"""Bygger appen med alla fem skiftlagen till build/ut/ (läggs inte ut automatiskt).

Kör: python3 build/alla-lag.py
"""
import datetime as dt, json, os

# ---------- data ----------
START = dt.date(2026, 10, 5)      # måndag v41, första hela veckan i 5-skiftet
END   = dt.date(2027, 6, 27)
V41   = dt.date(2026, 10, 5)
TYPES = {
 "A": ["N","N","","","FM","HD","HD"],
 "B": ["","","FM","FM","N","HN","HN"],
 "C": ["","","","","","",""],
 "D": ["EM","EM","N","N","","",""],
 "E": ["FM","FM","EM","EM","EM","",""],
}
ORDER = "ABCDE"
# veckotyp i v41 för varje lag, avläst från schemabladet
OFFSET = {1: 2, 2: 0, 3: 4, 4: 3, 5: 1}
PASS = {
 "FM": ("Förmiddag", "05:55–14:00", 6, 8),
 "EM": ("Eftermiddag", "13:55–22:00", 14, 8),
 "N":  ("Natt", "21:55–06:00", 22, 8),
 "HD": ("Helgdag", "05:55–18:00", 6, 12),
 "HN": ("Helgnatt", "17:55–06:00", 18, 12),
}
RED = {
 "2026-12-24":"Julafton","2026-12-25":"Juldagen","2026-12-26":"Annandag jul",
 "2026-12-31":"Nyårsafton","2027-01-01":"Nyårsdagen","2027-01-06":"Trettondedag jul",
 "2027-03-26":"Långfredagen","2027-03-28":"Påskdagen","2027-03-29":"Annandag påsk",
 "2027-05-01":"Första maj","2027-05-06":"Kristi himmelsfärd","2027-06-06":"Nationaldagen",
 "2027-06-25":"Midsommarafton","2027-06-26":"Midsommardagen",
}

def shifts(lag, mon):
    idx = (mon - V41).days // 7
    return TYPES[ORDER[(OFFSET[lag] + idx) % 5]]

weeks = []
d = START
while d <= END:
    weeks.append([d.isoformat(), d.isocalendar()[1]])
    d += dt.timedelta(days=7)

# ---------- sida ----------
STYLE = r"""
/* Layout: lagväljare överst (fast vid scroll), veckoremsor, sedan månad för månad i en smal kolumn. */
:root{
  --paper:#e9edf1; --card:#ffffff; --ink:#16202e; --muted:#4d5c6e; --line:#c9d3dd;
  --fm:#ffd166; --em:#e8833a; --n:#2e3a66;
  --hd:linear-gradient(135deg,#ffd166 0%,#ffd166 42%,#e8833a 100%);
  --hn:linear-gradient(135deg,#473d6b 0%,#141a30 100%);
  --off:#f2f5f8; --offink:#75828f; --ring:#16202e; --red:#b3261e;
  --on-light:#16202e; --on-dark:#ffffff;
  --sel:#16202e; --sel-ink:#ffffff;
  --display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;
  --body:"IBM Plex Sans",-apple-system,"Segoe UI",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#11161f; --card:#1a212c; --ink:#e8edf3; --muted:#8c9bab; --line:#2c3745;
    --fm:#e5b94d; --em:#cf6f2b; --n:#4a5a96;
    --hd:linear-gradient(135deg,#e5b94d 0%,#e5b94d 42%,#cf6f2b 100%);
    --hn:linear-gradient(135deg,#5a4e85 0%,#232c45 100%);
    --off:#1f2733; --offink:#7d8b9a; --ring:#e8edf3; --red:#ff8a80;
    --sel:#e8edf3; --sel-ink:#11161f; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#11161f; --card:#1a212c; --ink:#e8edf3; --muted:#8c9bab; --line:#2c3745;
  --fm:#e5b94d; --em:#cf6f2b; --n:#4a5a96;
  --hd:linear-gradient(135deg,#e5b94d 0%,#e5b94d 42%,#cf6f2b 100%);
  --hn:linear-gradient(135deg,#5a4e85 0%,#232c45 100%);
  --off:#1f2733; --offink:#7d8b9a; --ring:#e8edf3; --red:#ff8a80;
  --sel:#e8edf3; --sel-ink:#11161f; color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);
  font-size:16px;-webkit-text-size-adjust:100%}
.wrap{max-width:660px;margin:0 auto;padding-inline:16px;padding-block:14px 60px}
header{padding:2px 2px 10px}
h1{font-family:var(--display);font-weight:700;font-size:1.4rem;line-height:1.1;margin:0 0 2px}
.sub{color:var(--muted);font-size:.82rem;margin:0}

.pick{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--paper);
  padding:8px 0 10px;margin:0 0 6px}
.pick-label{font-size:.74rem;color:var(--muted);margin:0 2px 5px;display:block}
.seg{display:grid;grid-template-columns:repeat(5,1fr);gap:4px;background:var(--card);
  border:1px solid var(--line);border-radius:12px;padding:4px}
.seg button{font-family:var(--display);font-weight:700;font-size:1.05rem;min-height:44px;
  border:0;border-radius:8px;background:transparent;color:var(--muted);cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--sel);color:var(--sel-ink)}
.seg button:focus-visible{outline:2px solid var(--ring);outline-offset:2px}

.now{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:14px 12px 12px;margin-bottom:8px}
.now h2{font-family:var(--display);font-size:.95rem;margin:0 0 10px;font-weight:600;color:var(--muted)}
.hrow{display:flex;gap:4px}
.hd{flex:1;text-align:center;min-width:0}
.hd span{display:block;font-size:.66rem;color:var(--muted);margin-bottom:3px}
.hd em{display:block;font-style:normal;font-family:var(--display);font-weight:700;
  font-size:.86rem;padding:9px 0;border-radius:6px}

.legend{list-style:none;padding:0;margin:14px 0 22px;display:grid;
  grid-template-columns:1fr 1fr;gap:10px 14px;font-size:.84rem}
.legend li{display:grid;grid-template-columns:auto 1fr;column-gap:8px;align-items:center}
.legend li .chip{grid-row:span 2}
.legend li.single .chip{grid-row:auto}
.legend em{display:block;font-style:normal;font-size:.74rem;color:var(--muted);line-height:1.2}
.chip{display:inline-flex;align-items:center;justify-content:center;width:34px;height:22px;
  border-radius:5px;font-family:var(--display);font-weight:700;font-size:.75rem}
.chip.p-off{border:1px dashed var(--line)}
.cal{display:block;text-align:center;padding:12px;margin:-8px 0 20px;border-radius:10px;
  background:var(--card);border:1px solid var(--line);color:var(--ink);
  font-weight:600;font-size:.9rem;text-decoration:none}
.cal:focus-visible{outline:2px solid var(--ring);outline-offset:2px}

h2.month{font-family:var(--display);font-weight:600;font-size:1.05rem;
  margin:22px 0 8px;padding-bottom:5px;border-bottom:2px solid var(--ink)}
h2.month span{color:var(--muted);font-weight:500}
table.grid{width:100%;border-collapse:separate;border-spacing:3px;table-layout:fixed;
  font-variant-numeric:tabular-nums}
table.grid thead th{font-size:.68rem;color:var(--muted);font-weight:500;padding-bottom:2px}
th.wk{width:26px;font-family:var(--display);font-size:.75rem;color:var(--muted);font-weight:600}
td.d{border-radius:6px;text-align:center;padding:6px 1px 5px;border:1px solid transparent}
td .num{display:block;font-size:.72rem;opacity:.9;line-height:1.1;font-weight:500}
td .code{display:block;font-family:var(--display);font-weight:700;font-size:.8rem;line-height:1.2}
td.past{filter:grayscale(1);opacity:.3}
td.today{border-color:var(--ring);box-shadow:0 0 0 1.5px var(--ring)}
td.red.p-off .num{color:var(--red);opacity:1;font-weight:700}
td.red:not(.p-off) .num{text-decoration:underline;text-underline-offset:2px;font-weight:700}

.p-FM{background:var(--fm);color:var(--on-light)}
.p-EM{background:var(--em);color:var(--on-light)}
.p-HD{background:var(--hd);color:var(--on-light)}
.p-N{background:var(--n);color:var(--on-dark)}
.p-HN{background:var(--hn);color:var(--on-dark)}
.p-off{background:var(--off);color:var(--offink)}

ul.notes{list-style:none;padding:8px 10px;margin:8px 0 0;background:var(--card);
  border-radius:8px;border:1px solid var(--line);font-size:.82rem;color:var(--muted)}
ul.notes li{padding:2px 0}
ul.notes b{color:var(--ink)}
.free-box{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:14px 14px 12px;margin-top:30px}
.free-box h2{font-family:var(--display);margin:0 0 8px;font-size:1rem}
.free-box ul{list-style:none;padding:0;margin:0;font-size:.88rem;color:var(--muted);
  columns:2;column-gap:16px}
.free-box li{padding:2px 0;break-inside:avoid}
.free-box b{color:var(--ink);font-family:var(--display)}
footer{margin-top:26px;font-size:.78rem;color:var(--muted);line-height:1.5;
  border-top:1px solid var(--line);padding-top:12px}
"""

SCRIPT = r"""
const WEEKS=__WEEKS__, TYPES=__TYPES__, ORDER="ABCDE", OFFSET=__OFFSET__;
const PASS=__PASS__, RED=__RED__, CAL=__CAL__;
const DAG=["Mån","Tis","Ons","Tors","Fre","Lör","Sön"];
const MAN=["januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"];
const pad=n=>String(n).padStart(2,"0");
const iso=d=>d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());
function dayOf(mon,i){const [y,m,d]=mon.split("-").map(Number);return new Date(y,m-1,d+i);}
function shifts(lag,wi){return TYPES[ORDER[(OFFSET[lag]+wi)%5]];}
const kort=d=>d.getDate()+" "+MAN[d.getMonth()].slice(0,3);

function strip(lag,wi,rubrik){
  const s=shifts(lag,wi);let c="";
  for(let i=0;i<7;i++){const p=s[i];
    c+='<div class="hd"><span>'+DAG[i]+'</span><em class="p-'+(p||"off")+'">'+(p||"–")+'</em></div>';}
  return '<div class="now"><h2>'+rubrik+' (v'+WEEKS[wi][1]+')</h2><div class="hrow">'+c+'</div></div>';
}

function render(lag){
  const today=iso(new Date());
  // veckoremsor
  let cur=WEEKS.findIndex(w=>w[0]<=today&&today<=iso(dayOf(w[0],6)));
  const hero=document.getElementById("hero");
  if(cur>=0){hero.innerHTML=strip(lag,cur,"Den här veckan")+(WEEKS[cur+1]?strip(lag,cur+1,"Nästa vecka"):"");}
  else if(today<WEEKS[0][0]){hero.innerHTML=strip(lag,0,"Första veckan")+strip(lag,1,"Veckan efter");}
  else{hero.innerHTML='<div class="now"><h2>Schemat gäller 5 okt 2026 – 27 juni 2027</h2></div>';}
  // månader (veckan hör till torsdagens månad)
  let html="",key="",notes=[];const free=[];
  const closeMonth=()=>{if(!key)return;html+="</tbody></table>";
    if(notes.length)html+='<ul class="notes">'+notes.join("")+"</ul>";notes=[];};
  WEEKS.forEach((w,wi)=>{
    const thu=dayOf(w[0],3),k=thu.getFullYear()+"-"+thu.getMonth();
    if(k!==key){closeMonth();key=k;
      html+='<h2 class="month">'+MAN[thu.getMonth()]+' <span>'+thu.getFullYear()+'</span></h2>'+
        '<table class="grid"><thead><tr><th class="wk">v</th>'+DAG.map(x=>"<th>"+x+"</th>").join("")+'</tr></thead><tbody>';}
    const s=shifts(lag,wi);
    if(s.every(x=>!x)&&iso(dayOf(w[0],6))>=today)
      free.push('<li><b>v'+w[1]+'</b> '+kort(dayOf(w[0],0))+' – '+kort(dayOf(w[0],6))+'</li>');
    html+='<tr><th class="wk">'+w[1]+'</th>';
    for(let i=0;i<7;i++){const d=dayOf(w[0],i),ds=iso(d),p=s[i];
      const cls=["d","p-"+(p||"off")];
      if(RED[ds]){cls.push("red");
        notes.push('<li><b>'+kort(d)+'</b> '+RED[ds]+' – '+(p?PASS[p][0].toLowerCase()+' '+PASS[p][1]:'ledig')+'</li>');}
      if(ds<today)cls.push("past");if(ds===today)cls.push("today");
      html+='<td class="'+cls.join(" ")+'" data-d="'+ds+'"><span class="num">'+d.getDate()+
        '</span><span class="code">'+(p||"–")+'</span></td>';}
    html+="</tr>";
  });
  closeMonth();
  document.getElementById("months").innerHTML=html;
  document.getElementById("free").innerHTML=free.join("")||"<li>Inga hela lediga veckor kvar i perioden</li>";
  document.getElementById("freeh").textContent="Hela veckor lediga för skiftlag "+lag;
  document.querySelectorAll(".seg button").forEach(b=>b.setAttribute("aria-pressed",String(+b.dataset.lag===lag)));
  const cal=document.getElementById("cal");
  if(cal){cal.href=CAL.replace("{n}",lag);cal.textContent="Lägg in skiftlag "+lag+" i din kalender";}
  document.title="Skiftlag "+lag+" – skiftschema";
}

function pick(lag,spara){
  render(lag);
  if(spara){try{localStorage.setItem("skiftlag",String(lag));}catch(e){}
    try{history.replaceState(null,"","#lag"+lag);}catch(e){}}
}
function start(){
  let lag=0;const m=/^#lag([1-5])$/.exec(location.hash||"");
  if(m)lag=+m[1];
  if(!lag){try{lag=+localStorage.getItem("skiftlag")||0;}catch(e){}}
  if(!(lag>=1&&lag<=5))lag=1;
  document.querySelectorAll(".seg button").forEach(b=>b.addEventListener("click",()=>pick(+b.dataset.lag,true)));
  render(lag);
}
start();
"""

def js(o): return json.dumps(o, ensure_ascii=False)

def page(cal_href):
    legend = "".join(
        f'<li><span class="chip p-{k}">{k}</span>{v[0]}<em>{v[1]}</em></li>' for k, v in PASS.items()
    ) + '<li class="single"><span class="chip p-off">–</span>Ledig</li>'
    cal = f'<a class="cal" id="cal" href="#">Lägg in passen i din kalender</a>' if cal_href else ""
    script = (SCRIPT.replace("__WEEKS__", js(weeks)).replace("__TYPES__", js(TYPES))
              .replace("__OFFSET__", js(OFFSET))
              .replace("__PASS__", js({k: [v[0], v[1]] for k, v in PASS.items()}))
              .replace("__RED__", js(RED)).replace("__CAL__", js(cal_href or "")))
    seg = "".join(f'<button type="button" id="b{n}" data-lag="{n}" aria-pressed="false" '
                  f'aria-label="Skiftlag {n}">{n}</button>' for n in range(1, 6))
    return f"""<title>Skiftschema alla lag</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
<div class="wrap">
<header>
  <h1>Skiftschema</h1>
  <p class="sub">5-skift · oktober 2026 – juni 2027</p>
</header>
<div class="pick">
  <span class="pick-label" id="picklabel">Välj skiftlag</span>
  <div class="seg" role="group" aria-labelledby="picklabel">{seg}</div>
</div>
<div id="hero"></div>
<ul class="legend">{legend}</ul>
{cal}
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
<script>{script}</script>
"""

UT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ut")
os.makedirs(UT, exist_ok=True)
# 1) förhandsvisning (utan kalenderknapp – filerna finns först när sidan läggs ut)
open(os.path.join(UT, "forhandsvisning.html"), "w", encoding="utf-8").write(page(None))
# 2) färdig webbplats (läggs inte ut ännu)
full = f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="icon" href="favicon.png">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skift">
<meta name="theme-color" content="#e9edf1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11161f" media="(prefers-color-scheme: dark)">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>
</head><body>
{page("skiftlag{n}.ics")}
</body></html>
"""
open(os.path.join(UT, "index.html"), "w", encoding="utf-8").write(full)

# ---------- kalenderfiler ----------
g = lambda x: x.strftime("%Y%m%dT%H%M%S")
TZ = ["BEGIN:VTIMEZONE","TZID:Europe/Stockholm",
 "BEGIN:DAYLIGHT","TZOFFSETFROM:+0100","TZOFFSETTO:+0200","TZNAME:CEST",
 "DTSTART:19700329T020000","RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU","END:DAYLIGHT",
 "BEGIN:STANDARD","TZOFFSETFROM:+0200","TZOFFSETTO:+0100","TZNAME:CET",
 "DTSTART:19701025T030000","RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU","END:STANDARD","END:VTIMEZONE"]
for lag in range(1, 6):
    L = ["BEGIN:VCALENDAR","VERSION:2.0",f"PRODID:-//Skiftlag{lag}//Skiftschema//SV",
         "CALSCALE:GREGORIAN","METHOD:PUBLISH",f"X-WR-CALNAME:Skiftlag {lag}",
         "X-WR-TIMEZONE:Europe/Stockholm"] + TZ
    n = 0
    for mon_s, _ in weeks:
        mon = dt.date.fromisoformat(mon_s)
        for i, code in enumerate(shifts(lag, mon)):
            if not code: continue
            name, _, h, dur = PASS[code]
            hel = dt.datetime.combine(mon + dt.timedelta(days=i), dt.time(h, 0))
            s, e = hel - dt.timedelta(minutes=5), hel + dt.timedelta(hours=dur)
            L += ["BEGIN:VEVENT", f"UID:lag{lag}-{g(s)}@skiftschema", "DTSTAMP:20261002T100000Z",
                  f"DTSTART;TZID=Europe/Stockholm:{g(s)}", f"DTEND;TZID=Europe/Stockholm:{g(e)}",
                  f"SUMMARY:Skift: {name}", f"DESCRIPTION:Skiftlag {lag} · {code} · {s:%H:%M}–{e:%H:%M}",
                  "TRANSP:OPAQUE", "END:VEVENT"]
            n += 1
    L.append("END:VCALENDAR")
    open(os.path.join(UT, f"skiftlag{lag}.ics"), "w", encoding="utf-8", newline="").write("\r\n".join(L) + "\r\n")
    print(f"lag {lag}: {n} pass")
# ikonerna för hemskärmen ligger i repots rot
import shutil
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for ikon in ("apple-touch-icon.png", "favicon.png"):
    shutil.copy(os.path.join(ROT, ikon), os.path.join(UT, ikon))
print("veckor:", len(weeks), weeks[0], weeks[-1])
