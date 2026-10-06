import copy
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import validate as V  # noqa: E402


class Providers(unittest.TestCase):
    def setUp(self):
        self.P = V.load("providers.json")

    def errors(self, P):
        p = V.Problems()
        V.check_providers(P, p, date.today())
        return p.errors

    def test_published_data_is_clean(self):
        self.assertEqual(self.errors(self.P), [])

    def test_unknown_metro_is_an_error(self):
        P = copy.deepcopy(self.P)
        P["providers"][0]["metros"].append("Nowhere ZZ")
        self.assertTrue(any("Nowhere ZZ" in e for e in self.errors(P)))

    def test_duplicate_names_and_bad_serves_are_errors(self):
        P = copy.deepcopy(self.P)
        P["providers"].append(dict(P["providers"][0], serves="tiny"))
        errs = self.errors(P)
        self.assertTrue(any("duplicate" in e for e in errs))
        self.assertTrue(any("serves" in e for e in errs))


class SqlExport(unittest.TestCase):
    def test_loads_into_sqlite(self):
        import sqlite3
        db = sqlite3.connect(":memory:")
        db.executescript((V.DATA / "eastbound.sql").read_text())
        n = db.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
        self.assertEqual(n, len(V.load("providers.json")["providers"]))
        orphans = db.execute("SELECT COUNT(*) FROM provider_hubs WHERE provider NOT IN (SELECT name FROM providers)").fetchone()[0]
        self.assertEqual(orphans, 0)


if __name__ == "__main__":
    unittest.main()
