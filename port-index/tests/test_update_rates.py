import json
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import update_rates as U  # noqa: E402

PAGE = """<html><script>var x="$1 per 40ft";</script><p>Our detailed assessment for Thursday, 08 Oct 2026</p>
<p>On the Transpacific trade route, rates from Shanghai to New York fell 2% to $10,219 per 40ft container,
while those from Shanghai to Los Angeles remained stable at $7,835 per 40ft container.</p></html>"""


def sample():
    return json.loads((Path(__file__).resolve().parents[1] / "data" / "rates.json").read_text())


class ParseDrewry(unittest.TestCase):
    def test_reads_date_and_lanes(self):
        self.assertEqual(U.parse_drewry(PAGE), {"date": "2026-10-08", "New York": 10219, "Los Angeles": 7835})

    def test_missing_date_is_an_error(self):
        with self.assertRaises(ValueError):
            U.parse_drewry("<p>Shanghai to New York rose to $10,000 per 40ft</p>")

    def test_lane_does_not_borrow_another_lanes_price(self):
        p = U.parse_drewry("assessment for Thursday, 08 Oct 2026. Shanghai to New York was not assessed; Genoa $3,702 per 40ft")
        self.assertNotIn("New York", p)


class ApplyDrewry(unittest.TestCase):
    def test_updates_newer_figures_and_as_of(self):
        r = sample()
        changes = U.apply_drewry(r, {"date": "2026-10-08", "New York": 10219, "Los Angeles": 7900})
        self.assertEqual(len(changes), 2)
        ny = next(x for x in r["ocean_fcl40"] if x["lane"].startswith("Shanghai → New York"))
        self.assertEqual((ny["usd"], ny["date"]), (10219, "2026-10-08"))
        self.assertEqual(r["as_of"], "2026-10-08")

    def test_ignores_same_or_older_assessment(self):
        r = sample()
        self.assertEqual(U.apply_drewry(r, {"date": r["as_of"], "New York": 1}), [])

    def test_refuses_implausible_jump(self):
        with self.assertRaises(ValueError):
            U.apply_drewry(sample(), {"date": "2026-10-08", "New York": 104})


class ManualAndStale(unittest.TestCase):
    def test_set_rate(self):
        r = sample()
        U.set_rate(r, "ocean:vn", 9800, "2026-10-08", source="Freightos Baltic Index FBX03")
        self.assertEqual(next(x for x in r["ocean_fcl40"] if x["origin"] == "vn")["usd"], 9800)
        with self.assertRaises(ValueError):
            U.set_rate(r, "ocean:xx", 1, "2026-10-08")

    def test_stale(self):
        r = sample()
        self.assertEqual(U.stale(r, date.fromisoformat(r["as_of"])), [])
        self.assertEqual(len(U.stale(r, date(2027, 1, 1))), 4)

    def test_dumps_round_trips(self):
        r = sample()
        self.assertEqual(json.loads(U.dumps(r)), r)


if __name__ == "__main__":
    unittest.main()
