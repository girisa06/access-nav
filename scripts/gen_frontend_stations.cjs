// Generates the frontend station list from the backend's cmrl.json. Run from the repo root:
//   node scripts/gen_frontend_stations.cjs
const fs = require("fs");
const data = require("../app/data/cmrl.json");

const alias = {
  "Puratchi Thalaivar Dr. M.G. Ramachandran Central": "Chennai Central, MGR Central, Central Station",
  "Chennai International Airport": "Chennai Airport, Meenambakkam Airport",
  "Puratchi Thalaivi Dr. J. Jayalalithaa CMBT": "CMBT, Koyambedu Bus Terminus",
  "Arignar Anna Alandur": "Alandur",
  "St. Thomas Mount": "St Thomas Mount, Thomas Mount",
  "Government Estate": "Govt Estate",
};
const seen = new Set();
const rows = data.stations
  .filter(s => !/depot/i.test(s.name) && !seen.has(s.name) && seen.add(s.name))
  .map(s => ({ name: s.name, alias: alias[s.name] || "", latitude: +s.lat.toFixed(6), longitude: +s.lon.toFixed(6), type: "metro" }));

const out =
  "// CMRL metro stations (source: ungalsoththu/ChennaiGTFS, ODbL). Generated from the backend app/data/cmrl.json.\n" +
  "export const CMRL_STATIONS = " + JSON.stringify(rows, null, 1) + ";\n";
fs.writeFileSync("../frontend/src/lib/cmrlStations.js", out);
console.log(rows.length + " unique stations");
