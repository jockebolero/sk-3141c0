/*
 * Logiken för appen med alla fem skiftlagen.
 *
 * Skriptet ritar upp hela schemat i webbläsaren, så att man kan byta lag
 * utan att ladda om sidan.
 *
 * Schemadatan ligger i data.js, som skapas av build/alla-lag.py och måste
 * laddas före den här filen. Därifrån kommer:
 *
 *   WEEKS   varje vecka i perioden: [måndagens datum, veckonummer]
 *   TYPES   de fem veckotyperna i cykeln, pass måndag till söndag ("" = ledig)
 *   ORDER   ordningen på veckotyperna
 *   OFFSET  var i cykeln varje lag står första veckan (0 = A, 1 = B, ...)
 *   PASS    passkod -> [namn, tider]
 *   RED     datum -> helgdagens namn
 *   CAL     adress till kalenderfilen, där {n} byts mot lagnumret
 */

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
