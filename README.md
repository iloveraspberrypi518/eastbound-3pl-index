# Eastbound 3PL Index

A free tool for retailers who import goods into the US East Coast. It answers two questions:

1. **Which 3PLs are near which ports?** A searchable index of third-party logistics providers, their East Coast hub locations, and the ports closest to them.
2. **What's the best way to get a container from the factory to my 3PL or showroom right now?** A route planner that weighs speed, cost and risk, and adjusts for world events, the season, and what other shippers are likely to do.

**Live site:** https://iloveraspberrypi518.github.io/eastbound-3pl-index/

> **Status:** early prototype. It covers the US East Coast only. Freight rates come from dated public indexes (Oct 2026). Transit times are typical estimates, and tariff figures are estimates to confirm with a licensed customs broker. Check facility locations with each provider before relying on them.

---

## What it does today

The site has nine tabs: **Route planner**, **Mode advisor**, **When to book**, **Tariffs & duties**, **Emissions**, **Scenario builder**, **3PL index**, **Ports**, and **About & sources**. Each tab has its own link, for example `.../port-index/#advisor`.

### Shipment journey
Pick a factory region (Shanghai, Ho Chi Minh City or Mumbai), a 3PL, and a final stop. The final stop can be a showroom or studio, with the option to skip the 3PL entirely. The planner compares every path and highlights the best route plus two alternatives:

**Factory → origin port or airport → main leg (Panama Canal, Suez Canal, Cape of Good Hope, or air) → US East Coast entry → 3PL hub → showroom/studio**

Two sliders set how much you care about speed versus cost, and how much risk you'll accept.

There are two ways to view the routes:
- **Network graph:** every possible path laid out left to right, with the top routes highlighted.
- **Map:** a world map of the ocean or air leg, plus an East Coast map of the trip from port to 3PL to showroom.

### Scenarios
- **Current events**, preset from Sept–Oct 2026 news: Red Sea/Suez still contested, Strait of Hormuz closed (higher fuel prices), Shanghai port congestion, peak-season rates, and Panama Canal drought limits.
- **Weather and seasons:** pick a ship month and the usual seasonal risks turn on. These are Lunar New Year/Tết factory closures, West Pacific typhoons, South Asia monsoon, Cape of Good Hope winter storms, Atlantic hurricanes at Southeast ports, and nor'easters.

You can switch every scenario on or off to test "what if" questions.

### Crowd effect (game theory)
Other retailers read the same news and react the same way. When most of them pile into one port or the Panama Canal, it congests. The tool works out where the crowd ends up once nobody can do better by switching routes (an equilibrium), then gives your best move in response. It also compares the "obvious" route with the smarter one once crowding is factored in.

### Mode advisor
Should a shipment fly or sail, and in what kind of container? Pick a sector, shipment weight, cargo value and deadline. The advisor compares air, ocean LCL (a shared container), 20' and 40' containers, and reefers (refrigerated containers) by **all-in cost per kg**: freight, plus the cost of inventory sitting in transit. It rules out modes that miss the deadline or the product's shelf life. It includes:
- a scale table from 100 kg to 40 t showing where ocean starts beating air
- a sector guide for apparel, food and defense materials at small, medium and large shipment sizes
- compliance reminders for each sector, such as FDA Prior Notice, ITAR/EAR, the Cargo Preference Act, and dangerous-goods rules

Rates are illustrative and editable. Current-event scenarios scale them up or down.

### When to book (booking-timing game)
When a deadline is coming (a tariff increase, Lunar New Year factory closures, or holiday stock that must be in the warehouse), every importer on the lane tries to sail before it, and rates climb as the last sailings fill up. Sailing early isn't free either, because the goods sit in a warehouse. The tab models this as a booking-timing game (a weekly version of Vickrey's bottleneck model):
- **Where the crowd books:** the equilibrium spread of bookings over the 10 sailings before the deadline and 3 after it, where nobody can save by switching weeks.
- **Your move:** your cheapest sailing given your own cargo value and the cost of missing the deadline, with booking dates. Cargo that's cheap to hold should sail ahead of the rush; expensive cargo should pay the rush premium. If rush rates cost more than the penalty, it's cheaper to wait.
- **Price of anarchy:** how much less the lane would pay per container if bookings were coordinated, and what share of cargo coordination would push past the deadline.

It uses the route planner's scenario (for transit time and rate adjustments) and the Mode advisor's 40' rate.

### Tariffs & duties
Compare the landed cost of a shipment from China, Vietnam or India. The tab stacks the base (MFN) duty, Section 301 China list duties, the July 2026 Section 301 forced-labor duties (10% or 12.5%), Section 232 metals duties, and customs fees (MPF and HMF). It then adds freight at today's published rates. Example products cover apparel, food and defense-related materials, and every rate can be edited.

### Published freight rates
The mode advisor, route planner and duty calculator use dated public benchmarks: Drewry World Container Index, Freightos FBX03, Freightos Air Index, and a published carrier rate for India. Rates for 20' containers, reefers and LCL are estimated from the 40' rate and labeled as estimates.

### Public SQL data
All rate and tariff data lives in [`port-index/data/`](port-index/data/): `rates.json`, `tariffs.json`, and a generated SQL export, [`eastbound.sql`](port-index/data/eastbound.sql). The SQL loads into SQLite, MySQL or Dolt:

```bash
sqlite3 eastbound.db < port-index/data/eastbound.sql
sqlite3 eastbound.db "SELECT lane, usd, observed, source FROM freight_rates WHERE used_in_site;"
```

### Emissions
Which route puts the least carbon in the air? Every route option is scored in kg CO₂e per tonne, door to door. The score is distance on each leg (measured along real sea lanes) × GLEC Framework default emission factors: ship 14 g, air 608 g and truck 87 g CO₂e per tonne-km. The tab shows:
- a speed-vs-emissions chart with the best trade-offs highlighted
- the CO₂ cost of the Red Sea diversion (Cape vs. Suez) on your lane
- your shipment's footprint, with an optional carbon price and a passenger-car comparison
- a full table of options, cleanest first

An **Emissions priority** slider in the route planner lets carbon steer the recommended route. The mode advisor also shows the emissions of each recommendation.

### Scenario builder
Build your own network. Drag factories, origin ports and airports, US ports and airports, 3PL hubs and showrooms onto a canvas, then connect them by dragging from one node to another. Ocean links let you choose Panama, Suez or the Cape. Every complete factory-to-showroom path is scored for days, cost, risk and CO₂e, using the route planner's scenario and priorities, and the best path is highlighted. Scenarios can be saved by name in your browser.

### 3PL index and ports
- **3PLs:** 14 providers, including DHL Supply Chain, Ryder, GXO, NFI, GEODIS, Kenco, DSV, Saddle Creek, Flexport, ShipBob, ShipMonk, Red Stag and Stord. The index shows warehouse square footage, East Coast hub cities, and nearest port. You can filter by type or by port.
- **Ports:** 2025 container volumes and year-over-year change for East Coast ports, where a verified figure exists.

Sources are listed at the bottom of the page.

### Weekly rate updates
Every Friday a GitHub Actions job ([`.github/workflows/update-rates.yml`](.github/workflows/update-rates.yml)) reads Drewry's World Container Index (Shanghai → New York and Shanghai → Los Angeles), updates `rates.json`, rebuilds the page, runs the tests and pushes the change. The other lanes (Vietnam and India ocean rates, and air) come from news articles with no stable page to read. When any of them is more than 30 days old, the job opens a GitHub issue labeled `stale-rates`. To update one by hand:

```bash
cd port-index
python3 -m pipeline.update_rates --set ocean:vn 9800 --date 2026-10-08 --source "Freightos Baltic Index FBX03" --url https://...
python3 build.py
```

---

## Next steps (planned)

The goal: a free planning tool for small businesses moving goods to and from the US East Coast. The Python stays in the data pipeline, so the site remains static and free to host. Each step is its own commit.

### Step 2: Tests for the math, and checks on every push
- Move the pure calculations (freight quotes, duties, emissions) into `port-index/calc.js`. Duties and the booking-timing game are already there, with tests in `tests/calc.test.js`. The page inlines the file, and Node's built-in test runner tests it (`node --test "port-index/tests/*.test.js"`), with no packages to install.
- Python tests that `build.py` fills every placeholder and that `eastbound.sql` loads into SQLite with the expected row counts.
- A `test.yml` workflow that runs the Python and Node tests on every push and pull request. It also fails if `index.html` wasn't rebuilt after `template.html` or the data changed.

### Step 3: Upload your orders (new "Orders plan" tab)
- Paste a CSV or pick a file. It's read in the browser and never uploaded. Columns: `sku, description, hts, origin, units, unit_cost, unit_kg, need_by, mode`, plus optional `production_days`, `unit_m3`, and `mfn_pct`/`cn301_pct`/`s232_pct` overrides. Includes a sample file and a downloadable template.
- **Landed cost per SKU:** duties come from `tariffs.json`, matched by HTS prefix. Lines from the same country, by the same mode, needed in the same month count as one shipment. Freight is the cheaper of LCL and 40' containers, or air, using the mode advisor's constants. It's split across SKUs by weight, and the MPF (minimum and maximum per entry) is split by value. Lines with no tariff match are flagged.
- **Order-by dates:** work back from the need-by date through a safety buffer, transit days (from the route planner's current scenario) and production time. Lunar New Year and Tết factory closures are added when production overlaps them (China: about 7 days before to 14 after; Vietnam: 5 before to 9 after; dates for 2026–2030). Orders whose order-by date has already passed are flagged, with a suggestion to consider air.
- Optional: kg CO₂e per unit for each SKU, once step 4 exists.

### Step 4: Life cycle assessment (Emissions tab)
A screening estimate of a product's footprint from cradle to grave. It's for planning and internal reporting, not a formal ISO 14040/14044 LCA, and not for marketing claims (FTC Green Guides). `pipeline/build_lca.py` would download the sources below, cache them in `pipeline/.cache/` and write a compact `data/lca.json`, which `validate.py` already knows how to check.

| Stage | Method | Source (all free, checked Oct 2026) |
|---|---|---|
| Materials & manufacturing | **By weight (main estimate):** kg of product × kg CO₂e per kg (e.g. Clothing 22.3, Food and drink 3.7, IT electronics 24.9, aluminium 9.1, average rigid plastics 3.4) | UK DESNZ GHG Conversion Factors 2026, "Material use" ([flat file](https://assets.publishing.service.gov.uk/media/6a6c9748862aaf18d9c62ac9/ghg-conversion-factors-2026-flat-format-revised.xlsx)) |
| | **By spend (cross-check):** factory price × kg CO₂e per 2022 $ by NAICS code. Use the factors *without* margins, because transport is counted separately | US EPA Supply Chain GHG Emission Factors v1.3 ([CSV](https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv)); convert dollars with CPI-U (2022 avg 292.655, Aug 2026 334.980) from the [BLS API](https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0) |
| Packaging | Cardboard 1.20 and plastic film 2.91 kg CO₂e per kg | DESNZ 2026 (Paper and board: board; Plastics: average plastic film) |
| Shipping to the US | The route planner's existing door-to-door figure | GLEC Framework (already used) |
| 3PL warehousing | 5.8 kWh per ft² per year × building area per pallet (editable assumption, about 10 ft²) × US grid 0.352 kg CO₂e per kWh. Electricity only | EIA CBECS 2018 table C14 (warehouse and storage); EPA Emission Factors Hub 2025, Table 6 (eGRID US average) |
| Delivery to customers | 0.128 kg CO₂e per tonne-km (shared truck) | EPA Emission Factors Hub 2025, Table 8 (medium- and heavy-duty truck, per ton-mile) |
| End of life | Product and packaging by disposal route (landfill, recycling or incineration, chosen by the user) | EPA Emission Factors Hub 2025, Table 9 (from WARM) |

Notes for the build:
- **Why weight is the main method:** EPA's spend factors describe US industries, so they badly undercount cheap imports. Apparel is 0.06 kg per $, which gives about 0.2 kg CO₂e for a $3 T-shirt, while the weight method gives about 4.5 kg, in line with published T-shirt LCAs. Show both, and explain the gap.
- Grid carbon intensity of the factory country (Our World in Data / Ember, 2025, g CO₂ per kWh): China 525, Vietnam 461, India 670, US 384. Show these as context. Don't use them to adjust the factors.
- Proposed categories, matched by HTS prefix: apparel (61, 62), home textiles (63), seafood (03), spices (09), baked goods (19), semiconductors (8541, 8542), consumer electronics (85), batteries (8506, 8507), steel (72, 73), aluminium (76), plastics (39), toys (95), glass and ceramics (69, 70), paper (48), furniture (94, by spend only) and cosmetics (33, by spend only).
- Show a stacked bar per product of where its carbon comes from. For most goods, materials and manufacturing far outweigh shipping unless the goods fly. The use phase (e.g. electricity used by electronics) is left out.
- Add the factors to `eastbound.sql` as new tables.

---

## Roadmap

### Coverage
- [ ] Gulf Coast ports (Houston, New Orleans, Mobile)
- [ ] West Coast ports (LA/Long Beach, Oakland, Seattle/Tacoma) and rail from the West Coast to inland and East Coast hubs
- [ ] More factory regions (South China/Shenzhen, Bangladesh, Indonesia, Mexico, Turkey)
- [ ] More 3PLs, including regional and specialty providers (cold chain, bulky goods, apparel)
- [ ] Verified facility addresses for every 3PL hub

### Pricing
- [x] Published freight rate benchmarks (Drewry WCI, Freightos FBX/FAX) with dates and sources
- [x] Automatic weekly rate updates (Drewry WCI; other lanes flagged for manual update when over 30 days old)
- [ ] Publish the SQL data as a DoltHub database so anyone can query it online
- [ ] 3PL rate ranges: storage per pallet, pick-and-pack, receiving
- [ ] Anonymous quote sharing, so retailers can report the rates they actually received
- [x] Tariff and duty estimates by country of origin
- [ ] Full HTS lookup and more origin countries (Bangladesh, Indonesia, Mexico, Cambodia)
- [ ] Real mode-advisor rates by lane, plus more sectors (electronics, furniture, pharma, auto parts)

### Smarter routing
- [ ] Live data feeds for news, port delays and weather, replacing manual toggles
- [ ] Separate crowd groups: cost-focused and speed-focused shippers, and big and small retailers
- [ ] Splitting a shipment across several routes or ports to spread risk
- [ ] Cost of delay: missed sell-through windows, stockouts and holding cost

### Sustainability
- [ ] Vessel- and carrier-specific emission factors (ship size, fuel type, slow steaming)
- [ ] Low-carbon fuel options (biofuel, LNG, methanol) and their cost premium
- [ ] Rail options inland, plus intermodal vs. truck comparisons
- [ ] Emissions reports retailers can download for Scope 3 reporting

### Product
- [ ] Shareable links that save a scenario
- [ ] Side-by-side comparison of 3PLs
- [ ] Accounts and saved routes for retailers
- [ ] A way for 3PLs to claim and update their own listing

---

## Repo layout

```
.
├── index.html            redirects the site root to port-index/
├── port-index/           the site: source, data, pipeline and tests (see below)
├── .github/workflows/    weekly freight rate update
├── docs/                 setup guides (VS Code dev container)
├── .devcontainer/        dev container config
├── configs/              MCP server list for the AI agents
├── .skillshare/          custom skills for the AI agents
├── opencode.json         OpenCode settings (must stay at the root)
└── CLAUDE.md             dev container tools reference
```

## Working on the site

The site lives in [`port-index/`](port-index/):

| File | What it is |
| --- | --- |
| `template.html` | The source. Edit this file. |
| `calc.js` | Shared calculations (no page code), inlined into the page and tested on their own: duties and the booking-timing game |
| `pipeline/` | Python data scripts: `update_rates.py` (freight rates), `validate.py` (data checks run by `build.py`), `xlsx.py` (reads Excel files, standard library only) |
| `tests/` | Tests. Run them with `cd port-index && python3 -m unittest discover -s tests && node --test "tests/*.test.js"` |
| `build.py` | Merges in the data and writes the finished pages and the SQL export |
| `index.html` | Generated page for GitHub Pages. Don't edit by hand. |
| `data/` | Rate and tariff data (`rates.json`, `tariffs.json`, generated `eastbound.sql`) and map outlines |

To make a change:

```bash
# 1. edit port-index/template.html
python3 port-index/build.py   # 2. rebuild
git add -A && git commit -m "Describe the change" && git push   # 3. publish
```

GitHub Pages updates the live site a minute or two after each push.

---

## Development environment

This repo runs in a dev container from [calvinw/ai-agentic-tools](https://github.com/calvinw/ai-agentic-tools). The container comes with AI coding assistants, including Claude Code, OpenCode, Copilot, Crush, Codex and Gemini. Open it in GitHub Codespaces (**Code** → **Codespaces** → **Create codespace on main**) and setup runs automatically.

- `configs/mcp-servers.conf` lists the MCP servers available to the agents. Run `install-mcps.sh` after editing it.
- `.skillshare/` holds custom skills. Run `sync-skills.sh` after editing them.
- See [`CLAUDE.md`](CLAUDE.md) for the full list of tools and scripts.
- To run it locally in VS Code instead, see [`docs/vscode-devcontainer-setup.md`](docs/vscode-devcontainer-setup.md).
