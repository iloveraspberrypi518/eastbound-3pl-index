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

// ---------- Booking timing: a discrete version of Vickrey's bottleneck model.
// Importers racing one deadline each pick a sailing week. A week's freight rate rises with how
// full it is; sailing early costs holding (inventory carrying + storage); sailing after the
// deadline costs a one-off penalty (higher tariff, missed season).
// P = {early, late, base, surge, demand, hold, penalty}
//   early: sailings that make the deadline (week e = 0 is the last one), late: sailings after it
//   base: uncongested $/container, surge: rate multiple added when a week is exactly full
//   demand: lane bookings in weeks of normal capacity, hold: $/container per week early
//   penalty: $/container for missing the deadline
// Weeks run earliest first: early-1 … 0 weeks early, then late sailings 1 … late.
function bookingWeeks(P) {
  const w = [];
  for (let e = P.early - 1; e >= 0; e--) w.push({ e, late: 0 });
  for (let k = 1; k <= P.late; k++) w.push({ e: 0, late: k });
  return w;
}
// Load is in multiples of a week's capacity, so a load of 1 doubles the rate when surge = 1.
const bookingRate = (P, load) => P.base * (1 + P.surge * load * load);
// What one shipper pays to sail in week w at the given rate, with their own hold and penalty.
const bookingCost = (w, rate, hold, penalty) => rate + hold * w.e + (w.late ? penalty : 0);

// Method of successive averages, as in the route planner's crowd model. With system = true it
// prices each week at its marginal cost to the whole lane instead, which gives the coordinated
// optimum. The gap between the two average costs is the price of anarchy.
function bookingEquilibrium(P, system = false, iters = 3000) {
  const W = bookingWeeks(P);
  let x = W.map(() => 1 / W.length);
  const costs = x => W.map((w, i) => {
    const L = x[i] * P.demand, c = bookingCost(w, bookingRate(P, L), P.hold, P.penalty);
    return system ? c + 2 * P.base * P.surge * L * L : c;
  });
  for (let k = 1; k <= iters; k++) {
    const c = costs(x), j = c.indexOf(Math.min(...c));
    x = x.map((v, i) => v + ((i === j ? 1 : 0) - v) / (k + 1));
  }
  const rates = x.map(v => bookingRate(P, v * P.demand));
  const paid = W.map((w, i) => bookingCost(w, rates[i], P.hold, P.penalty));
  return { weeks: W, share: x, rates, paid, avg: paid.reduce((a, c, i) => a + c * x[i], 0) };
}

// Price of anarchy for the lane: average cost per container when everyone books for themselves
// vs. when bookings are coordinated.
function bookingAnarchy(P) {
  const eq = bookingEquilibrium(P), opt = bookingEquilibrium(P, true);
  return { eq, opt, saving: eq.avg - opt.avg, ratio: eq.avg / opt.avg };
}

// One small shipper's best response to the crowd's rates. Too small to move rates themselves.
// open[i] = false rules out week i (e.g. its booking date has passed); best is -1 if none is open.
function bookingBest(eq, hold, penalty, open) {
  const cost = eq.weeks.map((w, i) => bookingCost(w, eq.rates[i], hold, penalty));
  let best = -1;
  cost.forEach((c, i) => { if ((!open || open[i]) && (best < 0 || c < cost[best])) best = i; });
  return { cost, best };
}

if (typeof module !== "undefined") module.exports = {
  dutyCalc, bookingWeeks, bookingRate, bookingCost, bookingEquilibrium, bookingAnarchy, bookingBest,
};
