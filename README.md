# Eastbound 3PL Index

A free tool for retailers who import goods into the US East Coast. It answers two questions:

1. **Which 3PLs are near which ports?** A searchable index of third-party logistics providers, their East Coast hub locations, and the ports closest to them.
2. **What's the best way to get a container from the factory to my 3PL or showroom right now?** A route planner that weighs speed, cost and risk, and adjusts for world events, the season, and what other shippers are likely to do.

**Live site:** https://iloveraspberrypi518.github.io/eastbound-3pl-index/

> **Status:** early prototype. It covers the US East Coast only. Freight rates come from dated public indexes (Oct 2026). Transit times are typical estimates, and tariff figures are estimates to confirm with a licensed customs broker. Check facility locations with each provider before relying on them.

---

## What it does today

The site has eight tabs: **Route planner**, **Mode advisor**, **Tariffs & duties**, **Emissions**, **Scenario builder**, **3PL index**, **Ports**, and **About & sources**. Each tab has its own link, for example `.../port-index/#advisor`.

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
- [ ] Automatic weekly rate updates
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

## Working on the site

The site lives in [`port-index/`](port-index/):

| File | What it is |
| --- | --- |
| `template.html` | The source. Edit this file. |
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
