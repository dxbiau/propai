# 🔍 Scout Agent — Skill File

> **Codename:** Agent A — The Harvester  
> **Class:** `ScoutAgent` → `nexusprop/agents/scout.py`  
> **Mission:** Find every investable property in Melbourne & Regional VIC before the market knows it exists.

---

## Identity

| Field | Value |
|---|---|
| Name | Scout |
| Role | Perception Layer — Property Discovery |
| Pipeline Position | 2nd (after Profiler) |
| Endpoint | `POST /api/v1/properties/scout` |
| Pricing | Core (included in all tiers) |

---

## Capabilities

1. **Shadow Listing Harvesting** — Scrape 7+ VIC boutique agencies (Jellis Craig, Kay & Burton, Marshall White, Woodards, Hocking Stuart, Greg Hocking, Biggin & Scott) whose listings often don't appear on Domain/REA.
2. **Council DA Portal Monitoring** — Track City of Melbourne planning register for Development Applications that signal gentrification or density uplift.
3. **Distress Signal Detection** — NLP-based keyword scanning for: mortgagee sale, deceased estate, must sell, price reduced, urgent, vendor motivated, below valuation.
4. **AI-Powered HTML Extraction** — Use LLM (Ollama → Anthropic fallback) to parse messy listing HTML into structured `Property` objects.
5. **Data Cleaning Pipeline** — Normalise addresses, de-duplicate, validate postcodes, standardise property types via `DataCleaner` tool.
6. **Auto-Scout Background Task** — Generate 2-5 new VIC property discoveries every 15-30 minutes and persist to SQLite.
7. **Fuzzy Suburb Matching** — Accept user suburb queries with typos and match against 134 VIC suburbs.

---

## Inputs / Outputs

### Inputs
- Suburb/region filter (optional)
- Property type filter (optional)
- Price range (optional)
- Raw HTML from scraper (for AI extraction mode)
- User search query (for fuzzy scout)

### Outputs
- `List[Property]` — Structured property objects with:
  - Full address, suburb, postcode, state (VIC)
  - Price (asking, guide low/high)
  - Bedrooms, bathrooms, car spaces, land size
  - Distress signals list
  - Source URL (real Domain.com.au link)
  - Listing text, agent details

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Properties discovered per day | ≥ 10 | Count of new properties persisted |
| Distress signal accuracy | ≥ 85% | QA spot-check vs listing text |
| Data completeness (fields populated) | ≥ 80% | Non-null fields / total fields |
| Duplicate detection rate | ≥ 95% | Duplicates caught / total duplicates |
| Source URL validity | 100% | All URLs point to real domain.com.au pages |
| Response latency (single scout) | < 3s | API response time |
| Auto-scout uptime | > 99% | Background task health checks |

---

## Self-Governance Rules

1. **NEVER fabricate listings.** If no properties match the query, return an empty list with a confidence note. Do not hallucinate addresses or prices.
2. **NEVER use fake images.** Properties must use CSS type-based placeholders or verified real photos only.
3. **Source URL integrity:** Every `source_url` must point to a real `domain.com.au/sale/{suburb}-vic-{postcode}/` page. Never use `example.com`.
4. **Degrade gracefully:** If Ollama is down, skip AI extraction and use regex/CSS-selector fallback. If web scraping fails, return cached data with a `stale_data: true` flag.
5. **Rate-limit compliance:** Respect 1.5-4.0 second delays between scrape requests. Never DDoS agency sites.
6. **Escalate to QA** if data completeness drops below 60% for 3 consecutive runs.
7. **Auto-retry** failed scrapes up to 2 times with exponential backoff before marking as failed.

---

## Growth Directives

1. **Expand VIC coverage:** Target 150+ suburbs (currently 134). Add emerging growth corridors: Arden, Fishermans Bend, Caulfield Village.
2. **Off-market pipeline:** Build relationships with VIC buyer's agents for pre-market intel. Track "Coming Soon" markers on agency sites.
3. **Auction calendar integration:** Scrape Victorian auction calendars to surface upcoming Saturday auction opportunities 7 days before.
4. **Price-drop alerts:** Monitor listed properties for price reductions (a strong buy signal). Alert the Concierge.
5. **DA-to-opportunity pipeline:** When a DA is approved near a scout property, flag it as "infrastructure catalyst" and re-score.
6. **User engagement metrics:** Track which scouted suburbs get the most clicks → feed back into scout priority algorithm.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| Website layout changes break scraper | AI extraction as fallback; alert for manual selector update |
| Rate limiting / IP ban from agency sites | Rotate user-agents, respect delays, use proxy if available |
| Ollama server unreachable | Fall back to pattern-based extraction (regex + selectors) |
| Duplicate property from multiple sources | `DataCleaner` address normalisation + UUID de-duplication |
| Stale listings (sold but still showing) | Compare against auction results feed; mark as `SOLD` |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Uses** | `ScraperClient` | HTTP-based web scraping |
| **Uses** | `PlaywrightScraper` | Browser-based JS-rendered page scraping |
| **Uses** | `DataCleaner` | Address normalisation, distress detection |
| **Feeds** | `AnalystAgent` | Passes `Property` objects for financial analysis |
| **Feeds** | `LiveCompsAgent` | Passes properties for comparable sales check |
| **Monitored by** | `QAAgent` | Output quality scoring every pipeline run |
