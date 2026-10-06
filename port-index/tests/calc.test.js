// Tests for calc.js. Run with: node --test "port-index/tests/*.test.js"
const test = require("node:test");
const assert = require("node:assert/strict");
const C = require("../calc.js");

const lane = (o = {}) => ({ early: 10, late: 3, base: 10000, surge: 1, demand: 4, hold: 460, penalty: 8000, ...o });

test("booking weeks run earliest first, then late sailings", () => {
  const w = C.bookingWeeks(lane({ early: 3, late: 2 }));
  assert.deepEqual(w.map(x => [x.e, x.late]), [[2, 0], [1, 0], [0, 0], [0, 1], [0, 2]]);
});

test("an empty week costs the base rate and a full week costs base × (1 + surge)", () => {
  assert.equal(C.bookingRate(lane(), 0), 10000);
  assert.equal(C.bookingRate(lane(), 1), 20000);
});

test("equilibrium: every week the crowd uses costs about the same, and unused weeks cost more", () => {
  const eq = C.bookingEquilibrium(lane());
  assert.ok(Math.abs(eq.share.reduce((a, b) => a + b) - 1) < 1e-9);
  const used = eq.paid.filter((c, i) => eq.share[i] > 0.02);
  assert.ok(Math.max(...used) - Math.min(...used) < 0.01 * eq.avg, "used weeks within 1% of each other");
  eq.paid.forEach((c, i) => { if (eq.share[i] < 0.001) assert.ok(c >= Math.min(...used) - 1); });
});

test("rates climb toward the deadline", () => {
  const eq = C.bookingEquilibrium(lane());
  for (let i = 1; i < 10; i++) assert.ok(eq.rates[i] >= eq.rates[i - 1] - 1);
});

test("coordination never costs the lane more than the equilibrium", () => {
  for (const demand of [2, 4, 7]) {
    const a = C.bookingAnarchy(lane({ demand }));
    assert.ok(a.saving >= 0 && a.ratio >= 1, `demand ${demand}`);
  }
});

test("a heavy rush with a small penalty pushes some of the coordinated plan past the deadline", () => {
  const a = C.bookingAnarchy(lane({ demand: 7 }));
  const late = a.opt.share.slice(10).reduce((x, y) => x + y);
  assert.ok(late > 0.05);
});

test("cheap-to-hold cargo sails early; expensive-to-hold cargo sails last", () => {
  const eq = C.bookingEquilibrium(lane());
  assert.equal(C.bookingBest(eq, 150, 8000).best, 0);
  assert.equal(C.bookingBest(eq, 3000, 8000).best, 9);
});

test("best response skips weeks that are closed, and returns -1 when none are open", () => {
  const eq = C.bookingEquilibrium(lane());
  const open = eq.weeks.map((w, i) => i >= 5);
  assert.ok(C.bookingBest(eq, 150, 8000, open).best >= 5);
  assert.equal(C.bookingBest(eq, 150, 8000, eq.weeks.map(() => false)).best, -1);
});

test("duties: forced-labor 301 is skipped for Section 232 goods, and MPF is clamped", () => {
  const T = { fees: { mpf_rate: 0.3464, mpf_min: 33.58, mpf_max: 651.5, hmf_rate: 0.125 }, countries: { vn: { forced_labor_301: 10 } } };
  const o = C.dutyCalc(T, "vn", 1000000, "ocean", { mfn: 5, cn301: 25, s232: 50 });
  assert.equal(o.cn301, 0);
  assert.equal(o.fl301, 0);
  assert.equal(o.fees, 651.5 + 1250);
});
