"""Checks on the data files. build.py runs these first and refuses to build on any error.

    python3 -m pipeline.validate      # print problems; exit 1 on errors
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
# The page groups tariff products under these sector headings; a product in any other sector wouldn't show.
SECTORS = {"Apparel", "Food", "Defense"}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Problems:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def _date(p, where, v, today):
    if not isinstance(v, str) or not ISO.match(v):
        return p.err(where, f"date {v!r} isn't YYYY-MM-DD")
    try:
        d = date.fromisoformat(v)
    except ValueError:
        return p.err(where, f"date {v!r} doesn't exist")
    if d > today + timedelta(days=1):
        p.err(where, f"date {v} is in the future")


def _num(p, where, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return p.err(where, f"{v!r} isn't a number")
    if not lo <= v <= hi:
        p.err(where, f"{v} is outside the expected range {lo}–{hi}")


def check_rates(rates, p, today):
    _date(p, "rates.as_of", rates.get("as_of"), today)
    for group in ("ocean_fcl40", "reference", "air"):
        rows = rates.get(group)
        if not isinstance(rows, list) or (group != "reference" and not rows):
            p.err(f"rates.{group}", "missing or empty")
            continue
        for i, r in enumerate(rows):
            w = f"rates.{group}[{i}] ({r.get('lane', '?')})"
            for k in ("origin", "lane", "usd", "unit", "date", "kind", "source", "url"):
                if k not in r:
                    p.err(w, f"missing {k!r}")
            if "usd" in r:
                _num(p, w + ".usd", r["usd"], 0.5, 50) if group == "air" else _num(p, w + ".usd", r["usd"], 300, 40000)
            if "date" in r:
                _date(p, w, r["date"], today)
            if not str(r.get("url", "")).startswith("https://"):
                p.err(w, "url should start with https://")
    origins = [r.get("origin") for r in rates.get("ocean_fcl40", [])]
    if len(origins) != len(set(origins)):
        p.err("rates.ocean_fcl40", "more than one rate for the same origin")
    used = rates.get("ocean_fcl40", []) + rates.get("air", [])
    dates = [r["date"] for r in used if "date" in r]
    if dates and rates.get("as_of") != max(dates):
        p.warn("rates.as_of", f"{rates.get('as_of')} should be the newest rate date ({max(dates)})")
    D = rates.get("derived", {})
    for k, (lo, hi) in {"f20_of_f40": (0.3, 1), "r40_of_f40": (1, 4), "lcl_cbm_of_f40": (0.005, 0.1)}.items():
        _num(p, f"rates.derived.{k}", D.get(k), lo, hi)


def check_tariffs(t, p, today):
    _date(p, "tariffs.as_of", t.get("as_of"), today)
    F = t.get("fees", {})
    for k, (lo, hi) in {"mpf_rate": (0, 2), "mpf_min": (0, 200), "mpf_max": (100, 2000), "hmf_rate": (0, 1)}.items():
        _num(p, f"tariffs.fees.{k}", F.get(k), lo, hi)
    if F.get("mpf_min", 0) > F.get("mpf_max", 1):
        p.err("tariffs.fees", "mpf_min is above mpf_max")
    if not t.get("countries"):
        p.err("tariffs.countries", "missing or empty")
    for c, v in t.get("countries", {}).items():
        if not v.get("name"):
            p.err(f"tariffs.countries.{c}", "missing name")
        _num(p, f"tariffs.countries.{c}.forced_labor_301", v.get("forced_labor_301"), 0, 100)
    for i, x in enumerate(t.get("products", [])):
        w = f"tariffs.products[{i}] ({x.get('name', '?')})"
        if x.get("sector") not in SECTORS:
            p.err(w, f"sector {x.get('sector')!r} must be one of {sorted(SECTORS)} or it won't appear on the page")
        if not re.match(r"^\d{4}(\.\d{2}){0,3}$", str(x.get("hts", ""))):
            p.err(w, f"HTS code {x.get('hts')!r} should look like 6109.10.00")
        for k in ("mfn", "cn301", "s232"):
            _num(p, f"{w}.{k}", x.get(k), 0, 200)
        if not x.get("name"):
            p.err(w, "missing name")


def check_cross(rates, tariffs, p):
    ocean = {r["origin"] for r in rates.get("ocean_fcl40", [])}
    countries = set(tariffs.get("countries", {}))
    if ocean != countries:
        p.err("rates/tariffs", f"ocean rate origins {sorted(ocean)} and tariff countries {sorted(countries)} should match")


TYPES = {"Contract logistics", "Forwarder + warehousing", "E-commerce fulfillment"}
SERVES = {"small", "large"}


def check_providers(P, p, today):
    _date(p, "providers.as_of", P.get("as_of"), today)
    metros = P.get("metros", {})
    for k, ll in metros.items():
        if not (isinstance(ll, list) and len(ll) == 2 and 24 <= ll[0] <= 48 and -92 <= ll[1] <= -66):
            p.err(f"providers.metros.{k}", f"{ll!r} isn't an East Coast [lat, lon]")
    names = [x.get("name") for x in P.get("providers", [])]
    if not names:
        p.err("providers.providers", "missing or empty")
    if len(names) != len(set(names)):
        p.err("providers.providers", "duplicate provider names (the route planner looks providers up by name)")
    for i, x in enumerate(P.get("providers", [])):
        w = f"providers.providers[{i}] ({x.get('name', '?')})"
        if not x.get("name"):
            p.err(w, "missing name")
        if x.get("type") not in TYPES:
            p.err(w, f"type {x.get('type')!r} should be one of {sorted(TYPES)}")
        if x.get("serves") not in SERVES:
            p.err(w, f"serves {x.get('serves')!r} should be one of {sorted(SERVES)}")
        if not x.get("metros"):
            p.err(w, "needs at least one hub metro")
        for m in x.get("metros", []):
            if m not in metros:
                p.err(w, f"metro {m!r} isn't in providers.metros, so it can't be placed on the map")
        if x.get("sqft_m") is not None:
            _num(p, w + ".sqft_m", x["sqft_m"], 0.1, 500)
        if x.get("website") and not str(x["website"]).startswith("https://"):
            p.err(w, "website should start with https://")
        if not isinstance(x.get("verified"), bool):
            p.err(w, "verified should be true or false")


def check_lca(L, p, today):
    _date(p, "lca.built", L.get("built"), today)
    for k, (lo, hi) in {"grid_us_kg_per_kwh": (0.1, 1), "delivery_kg_per_tkm": (0.02, 0.5), "kwh_per_sqft_yr": (1, 50),
                        "usd_to_2022": (0.5, 1.2)}.items():
        _num(p, f"lca.{k}", L.get(k), lo, hi)
    mats = L.get("materials", {})
    eol = L.get("end_of_life", {})
    for i, c in enumerate(L.get("categories", [])):
        w = f"lca.categories[{i}] ({c.get('name', '?')})"
        if c.get("mass_kg_per_kg") is None and c.get("spend_kg_per_usd") is None:
            p.err(w, "needs a mass-based or spend-based factor")
        if c.get("mass_kg_per_kg") is not None:
            _num(p, w + ".mass_kg_per_kg", c["mass_kg_per_kg"], 0.05, 100)
        if c.get("spend_kg_per_usd") is not None:
            _num(p, w + ".spend_kg_per_usd", c["spend_kg_per_usd"], 0.005, 5)
        if c.get("eol") not in eol:
            p.err(w, f"end-of-life material {c.get('eol')!r} isn't in lca.end_of_life")
        if not c.get("hts"):
            p.err(w, "needs at least one HTS prefix so orders can be matched to it")
    for k in ("cardboard", "plastic"):
        if k not in mats:
            p.err("lca.materials", f"missing packaging material {k!r}")
    for k, v in eol.items():
        if v.get("landfilled") is None:
            p.err(f"lca.end_of_life.{k}", "needs a landfilled factor (used when other routes don't apply)")


def load(name):
    return json.loads((DATA / name).read_text())


def run(today=None, lca=True):
    today = today or date.today()
    p = Problems()
    rates, tariffs = load("rates.json"), load("tariffs.json")
    check_rates(rates, p, today)
    check_tariffs(tariffs, p, today)
    check_cross(rates, tariffs, p)
    check_providers(load("providers.json"), p, today)
    if lca and (DATA / "lca.json").exists():
        check_lca(load("lca.json"), p, today)
    return p


def main():
    p = run()
    for w in p.warnings:
        print("warning:", w)
    for e in p.errors:
        print("ERROR:", e)
    if not p.errors:
        print("data OK")
    return 1 if p.errors else 0


if __name__ == "__main__":
    sys.exit(main())
