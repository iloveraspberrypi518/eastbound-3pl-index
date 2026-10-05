# Eastbound 3PL Index

A free tool for retailers who import goods into the US East Coast. It answers two questions:

1. **Which 3PLs are near which ports?** A searchable index of third-party logistics providers, their East Coast hub locations, and the ports closest to them.
2. **What's the best way to get a container from the factory to my 3PL or showroom right now?** A route planner that weighs speed, cost and risk, and adjusts for world events, the season, and what other shippers are likely to do.

**Live site:** https://iloveraspberrypi518.github.io/personaluse/port-index/

> **Status:** early prototype. It covers the US East Coast only. Transit times are typical estimates, and costs are a relative index, not real quotes. Check facility locations with each provider before relying on them.

---

## What it does today

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
- [ ] Real cost numbers instead of the relative index, using public freight rate benchmarks (for example Freightos FBX and Drewry) with dates and sources
- [ ] 3PL rate ranges: storage per pallet, pick-and-pack, receiving
- [ ] Anonymous quote sharing, so retailers can report the rates they actually received
- [ ] Tariff and duty estimates by country of origin

### Smarter routing
- [ ] Live data feeds for news, port delays and weather, replacing manual toggles
- [ ] Separate crowd groups: cost-focused and speed-focused shippers, and big and small retailers
- [ ] Splitting a shipment across several routes or ports to spread risk
- [ ] Cost of delay: missed sell-through windows, stockouts and holding cost

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
| `build.py` | Merges in the map data and writes the finished pages |
| `index.html` | Generated page for GitHub Pages. Don't edit by hand. |
| `data/` | Map outlines (Natural Earth, via world-atlas and us-atlas) |

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
