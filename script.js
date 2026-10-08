/*
 * Logiken för skiftschemat (index.html).
 * Gjord av J. Stork.
 *
 * Skriptet ritar upp hela schemat i webbläsaren, så att man kan byta lag
 * utan att ladda om sidan.
 *
 * Schemadatan ligger i data.js, som skapas av build/bygg.py och måste
 * laddas före den här filen. Därifrån kommer:
 *
 *   WEEKS      varje vecka i perioden: [måndagens datum, veckonummer]
 *   TYPES      veckotyperna i cykeln, pass måndag till söndag ("" = ledig)
 *   ORDER      ordningen på veckotyperna
 *   OFFSET     var i cykeln varje lag står första veckan (0 = A, 1 = B, ...)
 *   PASS       passkod -> [namn, tider som "05:55–14:00", ...]. Tiderna styr "Nästa pass".
 *   RED        datum -> helgdagens namn
 *   CONFIRMED  sista bekräftade dagen, veckor efter den är preliminära ("" = allt bekräftat)
 *   CAL        adress till kalenderfilen, där {n} byts mot lagnumret ("" = ingen kalender)
 */

// Laget som visas för den som inte har valt något än.
// null betyder att sidan ber besökaren välja, så att ingen läser fel lags schema.
const STANDARDLAG = null;

const LAG = Object.keys(OFFSET).map(Number).sort((a, b) => a - b);

const DAG = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"];
const DAG_LANG = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"];
const MAN = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
             "augusti", "september", "oktober", "november", "december"];

// ---------------------------------------------------------------------------
// Hjälpfunktioner
// ---------------------------------------------------------------------------

function pad(n) {
  return String(n).padStart(2, "0");
}

// Tidpunkten just nu. Med ?nu=2026-12-30T02:00 i adressen kan man prova
// hur sidan ser ut vid en annan tidpunkt.
function nu() {
  const test = new URLSearchParams(location.search).get("nu");
  const moment = test ? new Date(test) : new Date();
  return isNaN(moment) ? new Date() : moment;
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

// Veckodagens nummer med måndag som 0.
function weekday(d) {
  return (d.getDay() + 6) % 7;
}

// Passen måndag till söndag för ett lag, vecka nummer weekIndex i WEEKS.
function shifts(lag, weekIndex) {
  return TYPES[ORDER[(OFFSET[lag] + weekIndex) % ORDER.length]];
}

// Datum i kort form, till exempel "24 dec".
function shortDate(d) {
  return d.getDate() + " " + MAN[d.getMonth()].slice(0, 3);
}

// Datum i lång form, till exempel "fredag 9 oktober".
function longDate(d) {
  return DAG_LANG[weekday(d)] + " " + d.getDate() + " " + MAN[d.getMonth()];
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// Klockslag, till exempel "06:00".
function clock(d) {
  return pad(d.getHours()) + ":" + pad(d.getMinutes());
}

// Antal kalenderdagar från a till b.
function daysBetween(a, b) {
  const start = new Date(a.getFullYear(), a.getMonth(), a.getDate());
  const end = new Date(b.getFullYear(), b.getMonth(), b.getDate());
  return Math.round((end - start) / 86400000);
}

// En vecka är preliminär om den börjar efter den sista bekräftade dagen.
function isPreliminary(weekIndex) {
  return CONFIRMED !== "" && WEEKS[weekIndex][0] > CONFIRMED;
}

// Vad som gäller en dag, i ord: "natt 21:55–06:00" eller "ledig".
function describe(pass) {
  return pass ? PASS[pass][0].toLowerCase() + " " + PASS[pass][1] : "ledig";
}

// ---------------------------------------------------------------------------
// Alla pass för ett lag, med start- och sluttid
// ---------------------------------------------------------------------------

// Klockslagen i en tidsangivelse: "21:55–06:00" blir [[21, 55], [6, 0]].
function parseTimes(text) {
  return text.split("–").map(part => part.split(":").map(Number));
}

// Varje pass som { code, day, start, end }. Tiderna läses ur passets
// tidsangivelse. Ett pass som slutar före det börjar slutar dagen efter (nattpassen).
function allShifts(lag) {
  const list = [];
  WEEKS.forEach((week, weekIndex) => {
    shifts(lag, weekIndex).forEach((code, i) => {
      if (!code) return;
      const [from, to] = parseTimes(PASS[code][1]);
      const day = dayOf(week[0], i);
      const start = new Date(day.getFullYear(), day.getMonth(), day.getDate(), from[0], from[1]);
      const nextDay = to[0] * 60 + to[1] <= from[0] * 60 + from[1] ? 1 : 0;
      const end = new Date(day.getFullYear(), day.getMonth(), day.getDate() + nextDay, to[0], to[1]);
      list.push({ code: code, day: day, start: start, end: end });
    });
  });
  return list;
}

// Passet som pågår just nu, eller annars nästa pass. null när schemat är slut.
function currentShift(lag, now) {
  return allShifts(lag).find(shift => shift.end > now) || null;
}

// ---------------------------------------------------------------------------
// Överst: i dag och nästa pass
// ---------------------------------------------------------------------------

function nextHtml(lag, now) {
  const shift = currentShift(lag, now);
  const working = Boolean(shift) && shift.start <= now;
  // Översta raden: dagens datum och vad som gäller i dag enligt schemat.
  // Jobbar man nu står passet redan i kortet. Då visas bara ett senare pass
  // samma dag, till exempel kvällens helgpass när man är på väg hem från nattens.
  const todays = allShifts(lag).find(other => iso(other.day) === iso(now));
  let status = todays ? PASS[todays.code][0] : "Ledig";
  if (working) {
    status = todays && todays.start > now ? PASS[todays.code][0] + " " + clock(todays.start) : "";
  }
  const date = '<p class="date"><span>I dag <span>' + longDate(now) + '</span></span>' +
               (status ? '<b>' + status + '</b>' : '') + '</p>';
  if (!shift) {
    return date + '<p class="label">Schemat är slut</p>' +
           '<p class="fine">Det finns inga fler pass i den här perioden.</p>';
  }

  const leave = leaveHtml(lag, now, shift);
  const name = PASS[shift.code][0];
  const times = PASS[shift.code][1];
  const chip = '<span class="chip big p-' + shift.code + '" aria-hidden="true">' + shift.code + '</span>';

  if (working) {
    return date + '<div class="row">' + chip + '<div><p class="label">Du jobbar nu</p>' +
           '<p class="main">' + name + '</p>' +
           '<p class="detail">Slutar ' + clock(shift.end) + '</p></div></div>' + leave;
  }

  const days = daysBetween(now, shift.start);
  const when = days === 0 ? "i dag" : days === 1 ? "i morgon" : "om " + days + " dagar";

  // Börjar passet i dag står datumet redan överst. Då är passets namn huvudsaken.
  const main = days === 0 ? name : capitalize(longDate(shift.start));
  const detail = days === 0 ? times + ' · i dag' : name + ' ' + times + ' · ' + when;

  return date + '<div class="row">' + chip + '<div><p class="label">Nästa pass</p>' +
         '<p class="main">' + main + '</p>' +
         '<p class="detail">' + detail + '</p></div></div>' + leave;
}

// ---------------------------------------------------------------------------
// Överst: nästa ledighet
// ---------------------------------------------------------------------------

// Minsta antal lediga dygn i följd som räknas som en ledighet.
// En enstaka ledig dag mitt i veckan räknas inte.
const LEDIGHET_MINST = 2;

// Alla ledigheter för ett lag som { start, end, weekIndex }, i tidsordning.
// En ledighet som går ända till periodens sista dag tas inte med, eftersom
// ingen vet hur länge den fortsätter.
function leaves(lag) {
  const list = [];
  let run = null;
  WEEKS.forEach((week, weekIndex) => {
    shifts(lag, weekIndex).forEach((code, i) => {
      const day = dayOf(week[0], i);
      if (code) {
        if (run && run.days >= LEDIGHET_MINST) list.push(run);
        run = null;
      } else if (run) {
        run.end = day;
        run.days++;
      } else {
        run = { start: day, end: day, days: 1, weekIndex: weekIndex };
      }
    });
  });
  return list;
}

// Två datum som en period: "19–25 oktober" eller "30 okt – 2 nov".
function period(start, end) {
  if (start.getMonth() === end.getMonth()) {
    return start.getDate() + "–" + end.getDate() + " " + MAN[end.getMonth()];
  }
  return shortDate(start) + " – " + shortDate(end);
}

// Raden längst ner i kortet: när man blir ledig nästa gång och hur många
// pass som är kvar dit. Är man redan ledig står det hur länge.
function leaveHtml(lag, now, shift) {
  const today = iso(now);
  const working = shift.start <= now;
  // Ledigheter som inte är slut. Den som slutar i dag är i praktiken över.
  const coming = leaves(lag).filter(leave => iso(leave.end) > today);
  const leave = coming[0];
  if (!leave) return "";

  const note = isPreliminary(leave.weekIndex) ? ' · preliminärt' : '';

  // Pass som inte har börjat än. Passet man jobbar på räknas inte.
  const left = allShifts(lag).filter(other =>
    other.start > now && iso(other.day) < iso(leave.start)).length;

  // Redan ledig, eller inga pass kvar före ledigheten (kvällen innan den börjar).
  if (iso(leave.start) <= today || left === 0) {
    const lead = working ? "Ledig efter passet" : "Ledig";
    return '<p class="leave"><span class="label">' + lead + '</span> ' +
           '<b>till och med ' + longDate(leave.end) + '</b>' + note + '</p>';
  }

  const remaining = left + ' pass kvar' + (working ? ' efter det här' : '');
  return '<p class="leave"><span class="label">Nästa ledighet</span> ' +
         '<b>' + period(leave.start, leave.end) + '</b> · ' + remaining + note + '</p>';
}

// ---------------------------------------------------------------------------
// Veckoremsorna: den här veckan och nästa
// ---------------------------------------------------------------------------

// En veckoremsa: sju rutor med veckodag, datum och pass.
function strip(lag, weekIndex, heading, today) {
  const week = shifts(lag, weekIndex);
  let cells = "";
  for (let i = 0; i < 7; i++) {
    const pass = week[i];
    const day = dayOf(WEEKS[weekIndex][0], i);
    const isToday = iso(day) === today;
    cells += '<li' + (isToday ? ' class="today" aria-current="date"' : '') +
             ' aria-label="' + capitalize(longDate(day)) + ': ' + describe(pass) + '">' +
             '<span class="wd">' + DAG[i] + '</span>' +
             '<span class="dt">' + day.getDate() + '</span>' +
             '<span class="chip p-' + (pass || "off") + '">' + (pass || "–") + '</span></li>';
  }
  return '<h2>' + heading + ' <span>v. ' + WEEKS[weekIndex][1] + '</span></h2>' +
         '<ul class="strip">' + cells + '</ul>';
}

function weeksHtml(lag, today) {
  const current = WEEKS.findIndex(week =>
    week[0] <= today && today <= iso(dayOf(week[0], 6)));

  if (current >= 0) {
    const hasNext = Boolean(WEEKS[current + 1]);
    return strip(lag, current, "Den här veckan", today) +
           (hasNext ? strip(lag, current + 1, "Nästa vecka", today) : "");
  }
  if (today < WEEKS[0][0]) {
    // Schemat har inte börjat än.
    return strip(lag, 0, "Första veckan", today) + strip(lag, 1, "Veckan efter", today);
  }
  return "";
}

// ---------------------------------------------------------------------------
// Månaderna
// ---------------------------------------------------------------------------

// En ruta i kalendern: datum överst, passkod under.
function cellHtml(day, pass, today) {
  const date = iso(day);
  const classes = ["d", "p-" + (pass || "off")];
  let label = capitalize(longDate(day)) + ": " + describe(pass);
  if (RED[date]) {
    classes.push("red");
    label += ", " + RED[date];
  }
  if (date < today) classes.push("past");
  if (date === today) classes.push("today");
  return '<td class="' + classes.join(" ") + '" aria-label="' + label + '"' +
         (date === today ? ' aria-current="date"' : '') + '>' +
         '<span class="num">' + day.getDate() + '</span>' +
         '<span class="code">' + (pass || "–") + '</span></td>';
}

// En månad som rubrik, tabell och lista över röda dagar.
// Veckor som går över ett månadsskifte finns med i båda månaderna,
// med tomma rutor för dagarna som hör till den andra månaden.
function monthHtml(lag, year, month, today, state) {
  let rows = "";
  let notes = "";
  let allPreliminary = true;

  WEEKS.forEach((entry, weekIndex) => {
    const monday = entry[0];
    const days = [0, 1, 2, 3, 4, 5, 6].map(i => dayOf(monday, i));
    if (!days.some(day => day.getFullYear() === year && day.getMonth() === month)) return;

    const preliminary = isPreliminary(weekIndex);
    if (!preliminary) allPreliminary = false;

    // Gränsen mellan bekräftat och uträknat visas en gång, före första preliminära veckan.
    if (preliminary && !state.boundaryShown) {
      state.boundaryShown = true;
      rows += '<tr class="boundary"><td colspan="8">Härifrån är schemat uträknat, inte bekräftat</td></tr>';
    }

    const week = shifts(lag, weekIndex);
    rows += '<tr><th class="wk" scope="row" aria-label="Vecka ' + entry[1] + '">' + entry[1] + '</th>';
    days.forEach((day, i) => {
      if (day.getFullYear() !== year || day.getMonth() !== month) {
        rows += '<td class="empty"></td>';
        return;
      }
      if (RED[iso(day)]) {
        notes += '<li><b>' + shortDate(day) + '</b> ' + RED[iso(day)] + ' – ' + describe(week[i]) + '</li>';
      }
      rows += cellHtml(day, week[i], today);
    });
    rows += "</tr>";
  });

  const name = MAN[month] + " " + year;
  return '<section class="month">' +
         '<h2>' + MAN[month] + ' <span>' + year + '</span>' +
         (allPreliminary ? ' <em class="tag">Preliminärt</em>' : '') + '</h2>' +
         '<table class="grid"><caption>' + capitalize(name) + ', lag ' + lag + '</caption>' +
         '<thead><tr><th class="wk" scope="col" aria-label="Vecka">v</th>' +
         DAG.map((short, i) => '<th scope="col" aria-label="' + DAG_LANG[i] + '">' + short + '</th>').join("") +
         '</tr></thead><tbody>' + rows + '</tbody></table>' +
         (notes ? '<ul class="notes">' + notes + '</ul>' : '') +
         '</section>';
}

// Alla månader i perioden. Månader som har passerat hamnar bakom "Visa tidigare månader".
function monthsHtml(lag, today) {
  const first = dayOf(WEEKS[0][0], 0);
  const last = dayOf(WEEKS[WEEKS.length - 1][0], 6);
  const state = { boundaryShown: false };
  let earlier = "";
  let upcoming = "";

  let year = first.getFullYear();
  let month = first.getMonth();
  while (year < last.getFullYear() || (year === last.getFullYear() && month <= last.getMonth())) {
    const html = monthHtml(lag, year, month, today, state);
    const lastDayOfMonth = iso(new Date(year, month + 1, 0));
    if (lastDayOfMonth < today) earlier += html; else upcoming += html;
    month++;
    if (month > 11) { month = 0; year++; }
  }

  return (earlier ? '<details class="earlier"><summary>Visa tidigare månader</summary>' + earlier + '</details>' : '') +
         upcoming;
}

// Hela lediga veckor som inte har passerat. Preliminära veckor får en asterisk,
// och då visas också förklaringen under listan.
function freeWeeksHtml(lag, today) {
  let html = "";
  let anyPreliminary = false;
  WEEKS.forEach((entry, weekIndex) => {
    const isFree = shifts(lag, weekIndex).every(pass => !pass);
    if (!isFree || iso(dayOf(entry[0], 6)) < today) return;
    const preliminary = isPreliminary(weekIndex);
    if (preliminary) anyPreliminary = true;
    html += '<li><b>v' + entry[1] + '</b> ' + shortDate(dayOf(entry[0], 0)) + ' – ' +
            shortDate(dayOf(entry[0], 6)) + (preliminary ? ' *' : '') + '</li>';
  });
  document.getElementById("freenote").hidden = !anyPreliminary;
  return html || "<li>Inga hela lediga veckor kvar i perioden</li>";
}

// ---------------------------------------------------------------------------
// Rita upp sidan
// ---------------------------------------------------------------------------

let valtLag = null;      // laget som visas, null innan man har valt
let ritatFor = "";       // vad som senast ritades, se signature()

// Beskriver det som påverkar hur sidan ser ut: lag, datum och aktuellt pass.
// När den ändras behöver sidan ritas om.
function signature(lag, now) {
  if (!lag) return "inget";
  const shift = currentShift(lag, now);
  const state = shift ? shift.start.getTime() + (shift.start <= now ? "p" : "v") : "slut";
  return lag + "|" + iso(now) + "|" + state;
}

function render() {
  const lag = valtLag;
  const now = nu();
  const today = iso(now);
  ritatFor = signature(lag, now);

  document.querySelectorAll(".seg button").forEach(button => {
    button.setAttribute("aria-pressed", String(Number(button.dataset.lag) === lag));
  });
  document.getElementById("schema").hidden = !lag;
  document.getElementById("valj").hidden = Boolean(lag);

  if (!lag) {
    document.getElementById("rubrik").textContent = "Välj ditt lag";
    document.title = "Skiftschema";
    return;
  }

  document.getElementById("rubrik").textContent = "Lag " + lag;
  document.title = "Lag " + lag + " – skiftschema";

  document.getElementById("next").innerHTML = nextHtml(lag, now);
  const weeks = weeksHtml(lag, today);
  document.getElementById("weeks").innerHTML = weeks;
  document.getElementById("weeks").hidden = !weeks;
  document.getElementById("months").innerHTML = monthsHtml(lag, today);
  document.getElementById("free").innerHTML = freeWeeksHtml(lag, today);
  document.getElementById("freeh").textContent = "Hela veckor lediga för lag " + lag;

  // Kalenderdelen finns bara på den utlagda sidan.
  const subscribe = document.getElementById("cal-sub");
  const file = document.getElementById("cal-file");
  if (subscribe && file && CAL) {
    const address = new URL(CAL.replace("{n}", lag), location.href);
    file.href = address.href;
    // webcal:// får kalenderappen att prenumerera i stället för att bara läsa in filen en gång.
    subscribe.href = "webcal://" + address.host + address.pathname;
    subscribe.textContent = "Prenumerera på lag " + lag;
  }
}

// Ritar om sidan om datumet eller passet har ändrats sedan sist. En app på
// hemskärmen kan ligga öppen över natten, och då ska "i dag" följa med.
function refresh() {
  if (signature(valtLag, nu()) !== ritatFor) render();
}

// ---------------------------------------------------------------------------
// Välja lag
// ---------------------------------------------------------------------------

function isLag(n) {
  return LAG.includes(n);
}

// Byter lag och kommer ihåg valet till nästa gång.
function pick(lag) {
  valtLag = lag;
  render();
  // Lagring kan vara avstängd, till exempel i privat läge. Då struntar vi i det.
  try { localStorage.setItem("skiftlag", String(lag)); } catch (e) {}
}

// Vilket lag som visas först: det man själv valde senast, annars adressen
// (#lag3), annars STANDARDLAG. Det egna valet går före adressen, så att en
// app på hemskärmen inte fastnar på laget som stod i länken man fick.
function startLag() {
  let saved = 0;
  try { saved = Number(localStorage.getItem("skiftlag")) || 0; } catch (e) {}
  if (isLag(saved)) return saved;

  const fromHash = /^#lag(\d+)$/.exec(location.hash || "");
  if (fromHash && isLag(Number(fromHash[1]))) return Number(fromHash[1]);

  return STANDARDLAG;
}

document.querySelectorAll(".seg button").forEach(button => {
  button.addEventListener("click", () => pick(Number(button.dataset.lag)));
});

valtLag = startLag();
render();

// Håll sidan aktuell: när appen tas fram igen och en gång i minuten.
document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
window.addEventListener("pageshow", refresh);
setInterval(refresh, 60000);

// Offline-stöd. Finns bara på den utlagda sidan, där sw.js ligger bredvid.
if (CAL && "serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
