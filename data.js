// Skapad av build/bygg.py. Ändra inte här, ändra i byggskriptet.

// Varje vecka i perioden: [måndagens datum, veckonummer].
const WEEKS = [
  ["2026-10-05", 41],
  ["2026-10-12", 42],
  ["2026-10-19", 43],
  ["2026-10-26", 44],
  ["2026-11-02", 45],
  ["2026-11-09", 46],
  ["2026-11-16", 47],
  ["2026-11-23", 48],
  ["2026-11-30", 49],
  ["2026-12-07", 50],
  ["2026-12-14", 51],
  ["2026-12-21", 52],
  ["2026-12-28", 53],
  ["2027-01-04", 1],
  ["2027-01-11", 2],
  ["2027-01-18", 3],
  ["2027-01-25", 4],
  ["2027-02-01", 5],
  ["2027-02-08", 6],
  ["2027-02-15", 7],
  ["2027-02-22", 8],
  ["2027-03-01", 9],
  ["2027-03-08", 10],
  ["2027-03-15", 11],
  ["2027-03-22", 12],
  ["2027-03-29", 13],
  ["2027-04-05", 14],
  ["2027-04-12", 15],
  ["2027-04-19", 16],
  ["2027-04-26", 17],
  ["2027-05-03", 18],
  ["2027-05-10", 19],
  ["2027-05-17", 20],
  ["2027-05-24", 21],
  ["2027-05-31", 22],
  ["2027-06-07", 23],
  ["2027-06-14", 24],
  ["2027-06-21", 25]
];

// Veckotyperna i cykeln. Pass måndag till söndag, "" = ledig.
const TYPES = {
  "A": ["N", "N", "", "", "FM", "HD", "HD"],
  "B": ["", "", "FM", "FM", "N", "HN", "HN"],
  "C": ["", "", "", "", "", "", ""],
  "D": ["EM", "EM", "N", "N", "", "", ""],
  "E": ["FM", "FM", "EM", "EM", "EM", "", ""]
};
const ORDER = "ABCDE";

// Var i cykeln varje lag står första veckan (0 = A, 1 = B, ...).
const OFFSET = {"1": 2, "2": 0, "3": 4, "4": 3, "5": 1};

// Passkod -> [namn, tider, hel timme då passet börjar, längd i timmar].
const PASS = {
  "FM": ["Förmiddag", "05:55–14:00", 6, 8],
  "EM": ["Eftermiddag", "13:55–22:00", 14, 8],
  "N": ["Natt", "21:55–06:00", 22, 8],
  "HD": ["Helgpass dag", "05:55–18:00", 6, 12],
  "HN": ["Helgpass natt", "17:55–06:00", 18, 12]
};

// Datum -> helgdagens namn.
const RED = {
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
  "2027-06-26": "Midsommardagen"
};

// Sista dagen som är bekräftad. Veckor efter den är preliminära. Tom = allt bekräftat.
const CONFIRMED = "2026-12-27";

// Adress till kalenderfilen, där {n} byts mot lagnumret. Tom i förhandsvisningen.
const CAL = "skiftlag{n}.ics";
