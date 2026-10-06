"""Refresh the freight rates in data/rates.json.

Drewry's World Container Index (Shanghai → New York and Shanghai → Los Angeles) is published every
Thursday on a public page, so it updates automatically. The other lanes come from news articles and a
carrier listing with no stable page to read, so they are updated by hand with --set.

    python3 -m pipeline.update_rates                  # fetch Drewry WCI and update rates.json
    python3 -m pipeline.update_rates --stale          # list rates older than 30 days (exit 1 if any)
    python3 -m pipeline.update_rates --set ocean:vn 9800 --date 2026-10-08 \\
        --source "Freightos Baltic Index FBX03" --url https://...

Run from the port-index folder, then run build.py to rebuild the page.
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path

RATES = Path(__file__).resolve().parents[1] / "data" / "rates.json"
DREWRY_URL = "https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry"
DREWRY_SOURCE = "Drewry World Container Index"
# Destination named in Drewry's commentary → (rates.json group, lane prefix)
DREWRY_LANES = {"New York": ("ocean_fcl40", "Shanghai → New York"), "Los Angeles": ("reference", "Shanghai → Los Angeles")}
MAX_AGE_DAYS = 30
# A new figure outside this band versus the last one is more likely a parsing error than a real move.
SANE_CHANGE = (0.4, 2.5)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (eastbound-3pl-index rate updater)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def page_text(raw):
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def parse_drewry(raw):
    """Return {"date": "YYYY-MM-DD", "New York": usd, "Los Angeles": usd} from the WCI page.

    Reads the weekly commentary, e.g. "Our detailed assessment for Thursday, 01 Oct 2026 ... rates from
    Shanghai to New York rose 1% to $10,428 per 40ft container". Lanes that can't be found are left out.
    """
    text = page_text(raw)
    m = re.search(r"assessment for \w+,?\s+(\d{1,2} [A-Za-z]+ \d{4})", text)
    if not m:
        raise ValueError("Couldn't find the assessment date on the Drewry page. The page layout may have changed.")
    for fmt in ("%d %b %Y", "%d %B %Y"):
        try:
            out = {"date": datetime.strptime(m.group(1), fmt).date().isoformat()}
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"Unrecognized date on the Drewry page: {m.group(1)!r}")
    for dest in DREWRY_LANES:
        # Stop at another "$", another lane, or the end of a clause, so one lane can't pick up another's price.
        lm = re.search(rf"Shanghai to {dest}(?:(?!Shanghai|; |\. |, while)[^$]){{0,80}}?\$\s?([\d,]+)\s*per 40\s?ft", text)
        if lm:
            out[dest] = int(lm.group(1).replace(",", ""))
    return out


def apply_drewry(rates, parsed):
    """Write parsed Drewry figures into rates (in place). Returns a list of human-readable changes."""
    changes = []
    for dest, (group, prefix) in DREWRY_LANES.items():
        if dest not in parsed:
            continue
        for r in rates[group]:
            if r["source"] != DREWRY_SOURCE or not r["lane"].startswith(prefix):
                continue
            if parsed["date"] <= r["date"]:
                continue
            ratio = parsed[dest] / r["usd"]
            if not SANE_CHANGE[0] <= ratio <= SANE_CHANGE[1]:
                raise ValueError(f"{r['lane']}: ${parsed[dest]:,} vs ${r['usd']:,} last time looks like a parsing error; not updating.")
            changes.append(f"{r['lane']}: ${r['usd']:,} ({r['date']}) → ${parsed[dest]:,} ({parsed['date']})")
            r.update(usd=parsed[dest], date=parsed["date"], url=DREWRY_URL)
    if changes:
        refresh_as_of(rates)
    return changes


def refresh_as_of(rates):
    rates["as_of"] = max(r["date"] for g in ("ocean_fcl40", "air") for r in rates[g])


def set_rate(rates, key, usd, when, source=None, url=None, lane=None, kind=None):
    """Manually set one rate. key is "air" or "ocean:<origin>", e.g. "ocean:vn"."""
    group, _, origin = key.partition(":")
    group = {"ocean": "ocean_fcl40", "air": "air"}.get(group)
    if not group or (group == "ocean_fcl40") != bool(origin):
        raise ValueError(f"Unknown rate {key!r}. Use 'air' or 'ocean:<origin>', e.g. 'ocean:vn'.")
    match = [r for r in rates[group] if group == "air" or r["origin"] == origin]
    if not match:
        raise ValueError(f"No {group} rate for origin {origin!r}. Origins: {', '.join(r['origin'] for r in rates[group])}")
    r = match[0]
    r.update(usd=usd, date=when)
    for k, v in (("source", source), ("url", url), ("lane", lane), ("kind", kind)):
        if v:
            r[k] = v
    refresh_as_of(rates)
    return r


def stale(rates, today, max_age=MAX_AGE_DAYS):
    """Rates the site uses that are older than max_age days, oldest first."""
    old = [r for g in ("ocean_fcl40", "air") for r in rates[g]
           if (today - date.fromisoformat(r["date"])).days > max_age]
    return sorted(old, key=lambda r: r["date"])


def dumps(data):
    """JSON with one list entry per line, matching the hand-written layout so diffs stay readable."""
    out = []
    for i, (k, v) in enumerate(data.items()):
        end = "," if i < len(data) - 1 else ""
        if isinstance(v, list):
            out.append(f"  {json.dumps(k)}: [")
            out += [f"    {json.dumps(x, ensure_ascii=False)}" + ("," if j < len(v) - 1 else "") for j, x in enumerate(v)]
            out.append("  ]" + end)
        else:
            out.append(f"  {json.dumps(k)}: " + json.dumps(v, ensure_ascii=False, indent=2).replace("\n", "\n  ") + end)
    return "{\n" + "\n".join(out) + "\n}\n"


def save(rates):
    RATES.write_text(dumps(rates))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stale", action="store_true", help="list rates older than %d days; exit 1 if any" % MAX_AGE_DAYS)
    ap.add_argument("--set", nargs=2, metavar=("RATE", "USD"), help="set a rate by hand, e.g. --set ocean:vn 9800")
    ap.add_argument("--date", help="observation date for --set (YYYY-MM-DD, default today)")
    ap.add_argument("--source"), ap.add_argument("--url"), ap.add_argument("--lane"), ap.add_argument("--kind")
    a = ap.parse_args(argv)
    rates = json.loads(RATES.read_text())

    if a.stale:
        old = stale(rates, date.today())
        for r in old:
            print(f"- {r['lane']} ({r['source']}): ${r['usd']:,} {r['unit']}, observed {r['date']}. Source: {r['url']}")
        if old:
            print(f"\nUpdate with: python3 -m pipeline.update_rates --set <ocean:cn|ocean:vn|ocean:in|air> <usd> --date YYYY-MM-DD --source ... --url ...")
        return 1 if old else 0

    if a.set:
        r = set_rate(rates, a.set[0], float(a.set[1]), a.date or date.today().isoformat(), a.source, a.url, a.lane, a.kind)
        save(rates)
        print(f"Set {r['lane']} to ${r['usd']:,} ({r['date']}). Now run: python3 build.py")
        return 0

    try:
        parsed = parse_drewry(fetch(DREWRY_URL))
    except Exception as e:  # network or layout change: keep the old rates, let --stale raise the alarm
        print(f"Drewry WCI not updated: {e}", file=sys.stderr)
        return 0
    changes = apply_drewry(rates, parsed)
    if changes:
        save(rates)
        print("Updated from Drewry WCI:\n  " + "\n  ".join(changes))
    else:
        print(f"Drewry WCI: no newer assessment than what's stored (latest on page: {parsed['date']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
