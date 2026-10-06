// Shared calculation core: pure functions only (no DOM, no page globals).
// build.py inlines this file into the page; tests/calc.test.js runs it under Node.

// Duties on a customs value V ($) from country c. L = {mfn, cn301, s232} in %, T = tariffs.json.
// Customs fees (MPF with its min/max, plus HMF on ocean cargo) apply once per entry.
function dutyCalc(T, c, V, mode, L) {
  const F = T.fees, s232 = L.s232 > 0;
  const o = {
    mfn: V * L.mfn / 100,
    cn301: c === "cn" ? V * L.cn301 / 100 : 0,
    // Section 232 goods are exempt from the forced-labor 301 duty
    fl301: s232 ? 0 : V * T.countries[c].forced_labor_301 / 100,
    s232: V * L.s232 / 100,
  };
  o.fees = Math.min(F.mpf_max, Math.max(F.mpf_min, V * F.mpf_rate / 100)) + (mode === "ocean" ? V * F.hmf_rate / 100 : 0);
  return o;
}

if (typeof module !== "undefined") module.exports = { dutyCalc };
