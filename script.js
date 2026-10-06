/*
 * Logiken för sidan Skiftlag 2 (index.html).
 *
 * Skriptet gör två saker:
 *   1. Tonar ner dagar som har passerat och ramar in dagens datum.
 *   2. Visar den här veckan och nästa överst på sidan.
 *
 * Schemat står i tabellerna i index.html. Skriptet läser passen därifrån,
 * så det finns ingen schemadata i den här filen.
 */

const DAG = ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"];

// Tecknet som står i en ruta när man är ledig.
const LEDIG = "–";

// Datum som "ÅÅÅÅ-MM-DD" i telefonens lokala tid.
function iso(d) {
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return d.getFullYear() + "-" + month + "-" + day;
}

// Tonar ner dagar som har passerat och ramar in dagens datum.
// Varje ruta har sitt datum i attributet data-d.
function markDays(today) {
  document.querySelectorAll("td.d").forEach(cell => {
    if (cell.dataset.d < today) cell.classList.add("past");
    if (cell.dataset.d === today) cell.classList.add("today");
  });
}

// Läser en vecka från en tabellrad: veckonummer och de sju passen.
function readWeek(row) {
  const codes = row.querySelectorAll("td.d .code");
  return {
    number: row.querySelector("th.wk").textContent,
    passes: Array.from(codes, code => code.textContent),
  };
}

// Bygger en veckoremsa: sju rutor med veckodag och pass.
function strip(week, rubrik) {
  let cells = "";
  for (let i = 0; i < 7; i++) {
    const pass = week.passes[i];
    const color = pass === LEDIG ? "off" : pass;
    cells += '<div class="hd"><span>' + DAG[i] + '</span>' +
             '<em class="p-' + color + '">' + pass + '</em></div>';
  }
  return '<div class="now"><h3>' + rubrik + ' (v' + week.number + ')</h3>' +
         '<div class="hrow">' + cells + '</div></div>';
}

// Visar den här veckan och nästa överst på sidan.
function showCurrentWeeks() {
  const hero = document.getElementById("hero");

  // Alla veckor på sidan i ordning. Varje vecka är en tabellrad.
  const rows = Array.from(document.querySelectorAll("tr.wrow"));
  const todayCell = document.querySelector("td.today");
  const current = todayCell ? rows.indexOf(todayCell.parentElement) : -1;

  if (current < 0) {
    // Dagens datum ligger utanför schemat.
    hero.innerHTML = '<div class="now"><h3>Schemat gäller 31 aug 2026 – 27 juni 2027</h3></div>';
    return;
  }

  const next = rows[current + 1];
  hero.innerHTML = strip(readWeek(rows[current]), "Den här veckan") +
                   (next ? strip(readWeek(next), "Nästa vecka") : "");
}

markDays(iso(new Date()));
showCurrentWeeks();
