# Property Insights Melbourne — Team Reference Document

> **Last updated:** 20 February 2026
> **Status:** MVP Complete — Ready for iteration
> **Version:** 4.0.0

---

## TABLE OF CONTENTS

1. [What We're Building](#1-what-were-building)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [How to Run It](#4-how-to-run-it)
5. [Architecture Overview](#5-architecture-overview)
6. [The 13 AI Agents](#6-the-13-ai-agents)
7. [6 Tools](#7-6-tools)
8. [Data Models](#8-data-models)
9. [API Endpoints (14 Routers)](#9-api-endpoints-14-routers)
10. [UI / UX — Bloomberg Terminal Dashboard](#10-ui--ux--bloomberg-terminal-dashboard)
11. [Color System & Design Tokens](#11-color-system--design-tokens)
12. [Typography](#12-typography)
13. [CSS Animations](#13-css-animations)
14. [Page Layout — Component by Component](#14-page-layout--component-by-component)
15. [10 Tab Panels](#15-10-tab-panels)
16. [5 Modals](#16-5-modals)
17. [Chatbot Widget](#17-chatbot-widget)
18. [Landing Page](#18-landing-page)
19. [Location Database — 134 Suburbs, 15 Regions](#19-location-database--134-suburbs-15-regions)
20. [40 Seed Properties](#20-40-seed-properties)
21. [Subscription Tiers & Pricing](#21-subscription-tiers--pricing)
22. [10 Investor Personas](#22-10-investor-personas)
23. [LLM Strategy — 3-Tier Fallback](#23-llm-strategy--3-tier-fallback)
24. [Persistence Layer](#24-persistence-layer)
25. [Auto-Scout Background Task](#25-auto-scout-background-task)
26. [Honesty & Integrity Policies](#26-honesty--integrity-policies)
27. [100x Value Recommendations (Roadmap)](#27-100x-value-recommendations-roadmap)
28. [Persona-Driven Feature Matrix](#28-persona-driven-feature-matrix)
29. [Key Decisions & Conventions](#29-key-decisions--conventions)

---

## 1. WHAT WE'RE BUILDING

**Property Insights Melbourne (PIM)** is a Bloomberg Terminal-style SaaS platform for Melbourne and Victorian property investors. It uses 13 AI agents to scout, analyse, negotiate, coach, and close real estate deals across 134 suburbs.

**One-liner:** A Bloomberg Terminal for Australian property — 13 AI agents that find undervalued deals, crunch the numbers, write offers, and coach you through negotiation.

| Field | Value |
|-------|-------|
| **Product Name** | Property Insights Melbourne |
| **Tagline** | Your Digital Property Associate |
| **Market** | Melbourne Metro + Regional Victoria (VIC), Australia |
| **Target Users** | 10 investor personas from first-home buyers to enterprise syndicates |
| **Competitive Edge** | AI-powered deal scoring (Bargain Score™), real-time scouting, APRA-compliant borrowing power, full deal structuring — at $199/mo vs $12K–$30K for a buyer's agent |

---

## 2. TECH STACK

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13 + FastAPI |
| **Server** | Uvicorn (ASGI) on port 8001 |
| **Frontend** | Single-page HTML + Tailwind CSS (CDN) + Vanilla JavaScript |
| **Database** | SQLite with WAL mode (`pia.db`) |
| **LLM (Primary)** | Ollama running `llama3.2` locally (FREE) |
| **LLM (Fallback)** | Anthropic Claude API (paid, only if Ollama is down) |
| **LLM (Last Resort)** | Rule-based no-AI fallback — app never breaks without AI |
| **Fonts** | Inter (UI) + JetBrains Mono (data/monospace) via Google Fonts |
| **CSS Framework** | Tailwind CSS v3 via CDN + custom CSS animations |
| **Python (Path)** | `C:/Users/Azuri/AppData/Local/Programs/Python/Python313/python.exe` |

### Key Python Dependencies
`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `httpx`, `structlog`, `python-dotenv`, `anthropic`, `beautifulsoup4`, `lxml`, `selectolax`, `playwright`, `pandas`, `numpy`, `langchain`, `langchain-anthropic`, `langchain-community`, `supabase`, `twilio`, `sqlalchemy`, `rich`, `jinja2`, `pytest`, `ruff`, `mypy`

---

## 3. PROJECT STRUCTURE

```
e:\zzmaster\re2026\
├── nexusprop/                          # Main application package
│   ├── __init__.py
│   ├── agents/                         # 13 AI Agents
│   │   ├── base.py                     # BaseAgent (LLM interface, 3-tier fallback)
│   │   ├── scout.py                    # Property Hunter — scraping & discovery
│   │   ├── analyst.py                  # Financial Brain — Bargain Score & ROI
│   │   ├── closer.py                   # Offer Writer — Cialdini persuasion
│   │   ├── profiler.py                 # Investor Profiler — APRA borrowing power
│   │   ├── stacker.py                  # Deal Structurer — entity/tax/BRRR
│   │   ├── mentor.py                   # Investment Coach — adaptive education
│   │   ├── qa.py                       # QA Engine — self-governance & scoring
│   │   ├── due_diligence.py            # Document Analyst — S32 red flags
│   │   ├── negotiation_shadow.py       # Live Coaching — tactic detection
│   │   ├── live_comps.py               # Comparable Sales — underquoting detection
│   │   ├── concierge.py                # Deal Matching & Alerts
│   │   ├── chatbot.py                  # News Scraper + Market Chat (6 RSS feeds)
│   │   └── photo_enhancer.py           # Property Photo AI (5 presets)
│   │
│   ├── api/                            # FastAPI application
│   │   ├── main.py                     # App factory, startup, static files
│   │   ├── middleware.py               # Rate limiting, request logging
│   │   └── routes/                     # 14 API routers
│   │       ├── properties.py           # CRUD + Scout + Location tree
│   │       ├── deals.py                # Analysis + quick ROI
│   │       ├── offers.py               # Offer generation
│   │       ├── profiler.py             # Investor profile building
│   │       ├── stacker.py              # Deal structuring
│   │       ├── mentor.py               # Coaching + weekly brief
│   │       ├── qa.py                   # Health checks + governance
│   │       ├── due_diligence.py        # Document analysis
│   │       ├── negotiation.py          # Live negotiation coaching
│   │       ├── photos.py              # Photo enhancement + analysis
│   │       ├── chatbot.py              # Chat + trending news
│   │       ├── subscriptions.py        # Tier info + feature checks
│   │       ├── recommendations.py      # Top deal recommendations
│   │       └── webhooks.py             # Stripe webhook handler
│   │
│   ├── models/                         # Pydantic data models
│   │   ├── property.py                 # Property, DistressSignal, 16 PropertyTypes
│   │   ├── deal.py                     # Deal, CashFlowModel, BargainScore, DealType
│   │   ├── offer.py                    # OfferDocument, OfferCondition, tones
│   │   ├── investment.py               # InvestmentProfile, FinancialCapacity, DealStructure, Portfolio
│   │   ├── user.py                     # UserProfile, UserPreferences, BudgetRange
│   │   ├── subscription.py             # 4 tiers + 3 add-ons + feature gates
│   │   └── suburb.py                   # SuburbProfile (15 data points each)
│   │
│   ├── tools/                          # 6 standalone tools
│   │   ├── bargain_scorer.py           # Weighted 0-100 scoring algorithm
│   │   ├── comps_engine.py             # In-memory comparable sales matching
│   │   ├── roi_calculator.py           # Full cash-flow modelling
│   │   ├── data_cleaner.py             # Rule-based HTML→Property extraction
│   │   ├── offer_writer.py             # Template-based offer documents
│   │   └── scraper.py                  # Dual-mode web scraper (httpx + Playwright)
│   │
│   ├── frontend/                       # All frontend assets
│   │   ├── index.html                  # Bloomberg Terminal dashboard (804 lines)
│   │   ├── landing.html                # Marketing landing page (347 lines)
│   │   └── static/js/
│   │       └── nexusprop.js            # All frontend logic (1647 lines)
│   │
│   ├── config/                         # App settings (pydantic-settings)
│   ├── database/                       # DB helpers
│   ├── db.py                           # SQLite persistence (WAL mode)
│   ├── locations.py                    # 134 suburbs × 15 VIC regions
│   ├── seed_data.py                    # 40 realistic seed properties
│   ├── auto_scout.py                   # Background task (15-30 min interval)
│   ├── orchestrator/                   # Pipeline engine
│   ├── scrapers/                       # Web scraping infrastructure
│   ├── notifications/                  # Multi-channel notification system
│   ├── skills/                         # QA-evolved skill templates
│   └── tests/                          # Test suite
│
├── pia.db                              # SQLite database (auto-created)
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project metadata
├── .env.example                        # Environment variable template
├── audit.py                            # Code audit utility
├── test_api.py                         # API integration tests
├── README.md                           # Basic readme
├── SPARK_DESCRIPTION.md                # Full GitHub Spark blueprint (~2100 lines)
└── team.md                             # THIS FILE
```

---

## 4. HOW TO RUN IT

### Prerequisites
- Python 3.13+
- Ollama running locally with `llama3.2` model (optional — app works without it)

### Start the Server
```powershell
$env:PYTHONPATH = "e:\zzmaster\re2026"
python -m uvicorn nexusprop.api.main:app --port 8001 --host 127.0.0.1
```

### Access
| URL | What |
|-----|------|
| `http://127.0.0.1:8001/terminal` | **Bloomberg Terminal Dashboard** (main product) |
| `http://127.0.0.1:8001/landing` | Marketing landing page |
| `http://127.0.0.1:8001/docs` | FastAPI auto-generated Swagger docs |
| `http://127.0.0.1:8001/health` | System health check JSON |

### Environment Variables (`.env`)
```
ANTHROPIC_API_KEY=           # Optional — Ollama is default
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
USE_OLLAMA=true
APP_ENV=development
APP_PORT=8001
SECRET_KEY=change-me
```

### Clean Restart (fresh database)
```powershell
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item "e:\zzmaster\re2026\pia.db", "e:\zzmaster\re2026\pia.db-wal", "e:\zzmaster\re2026\pia.db-shm" -Force -ErrorAction SilentlyContinue
# Then start server again — seed data auto-populates
```

---

## 5. ARCHITECTURE OVERVIEW

```
┌──────────────────────────────────────────────────────────┐
│                 FRONTEND (Single Page App)                │
│  Bloomberg Terminal Dashboard — HTML + Tailwind + JS      │
│  10 Tab Panels · 5 Modals · Floating Chatbot Widget      │
├──────────────────────────────────────────────────────────┤
│                    FastAPI Backend                         │
│  14 API Routers · Rate Limiting · Request Logging         │
├───────────┬──────────┬──────────┬──────────┬─────────────┤
│  Scout    │ Analyst  │ Closer   │ Profiler │  Stacker    │
│  Agent    │ Agent    │ Agent    │ Agent    │  Agent      │
├───────────┼──────────┼──────────┼──────────┼─────────────┤
│  Mentor   │ QA       │ DueDil   │ NegShadow│ LiveComps   │
│  Agent    │ Agent    │ Agent    │ Agent    │  Agent      │
├───────────┼──────────┼──────────┴──────────┴─────────────┤
│ Concierge │ PhotoEnh │         Chatbot Agent              │
│  Agent    │ Agent    │    (RSS News Scraper + Chat)       │
├───────────┴──────────┴───────────────────────────────────┤
│              Orchestrator Pipeline Engine                  │
│  Profiler → Scout → Analyst → Comps → Stacker →          │
│  Closer → Concierge → Mentor → QA                        │
├──────────────────────────────────────────────────────────┤
│  6 Tools: BargainScorer · CompsEngine · ROICalculator     │
│           DataCleaner · OfferWriter · Scraper              │
├──────────────────────────────────────────────────────────┤
│  SQLite (WAL mode) + Auto-Scout Background Task           │
│  134 Suburbs × 15 Data Points + 40 Seed Properties       │
└──────────────────────────────────────────────────────────┘
```

**Pipeline Flow:** Each agent can work independently OR as part of the full orchestrated pipeline:
`Profiler → Scout → Analyst → LiveComps → Stacker → Closer → Concierge → Mentor → QA`

**Fail-Forward:** If any agent fails, the pipeline continues. Failed agent output is logged but doesn't block the chain. QA always runs last to score everything.

---

## 6. THE 13 AI AGENTS

Every agent extends `BaseAgent` which provides `ask_llm()` with 3-tier fallback (Ollama → Anthropic → rule-based).

### Agent Summary Table

| # | Agent | File | Purpose | Key Output |
|---|-------|------|---------|------------|
| 1 | **Scout** | `agents/scout.py` | Scrape agencies, detect shadow listings & distress | Property records with 28 distress keywords |
| 2 | **Analyst** | `agents/analyst.py` | Bargain Score (0-100), ROI, cash-flow modelling | Deal with 20+ financial metrics |
| 3 | **Closer** | `agents/closer.py` | Cialdini-based offer letters, 5 tones | Cover letter + negotiation strategy |
| 4 | **Profiler** | `agents/profiler.py` | APRA borrowing power, investor profiling | InvestmentProfile with readiness score |
| 5 | **Stacker** | `agents/stacker.py` | Entity selection, BRRR, tax optimisation | DealStructure with projections |
| 6 | **Mentor** | `agents/mentor.py` | Adaptive coaching, 7 topic types | Educational responses + weekly briefs |
| 7 | **QA** | `agents/qa.py` | Score all agents, evolve skill templates | 5-dimension scores, skill templates |
| 8 | **Due Diligence** | `agents/due_diligence.py` | S32 / contract red flag analysis | 10-category risk assessment |
| 9 | **Negotiation Shadow** | `agents/negotiation_shadow.py` | Real-time coaching, tactic detection | Counter-strategies, agent profiling |
| 10 | **Live Comps** | `agents/live_comps.py` | Comparable sales, underquoting detection | Median comps, $/sqm, underquoting flags |
| 11 | **Concierge** | `agents/concierge.py` | Deal-to-user matching, alerts | Match scores, notification payloads |
| 12 | **Photo Enhancer** | `agents/photo_enhancer.py` | 5 presets for property photos | Enhanced image + quality metrics |
| 13 | **Chatbot** | `agents/chatbot.py` | 6 RSS feeds, VIC relevance scoring | News + conversational AI responses |

### Key Agent Details

**Bargain Score Algorithm (Analyst):** Weighted 0-100 composite:
- Price Deviation (35%): How far below suburb median
- Cash Flow (25%): Based on net rental yield
- Distress Delta (20%): Distress signal intensity
- Market Timing (15%): Days on market + market growth
- DOM Bonus (5%) + Condition adjustment
- **≥85 = GOLDEN OPPORTUNITY** | ≥65 = STRONG | ≥40 = FAIR

**Profiler — APRA Borrowing Power:**
- Assessment rate: actual rate + 3% buffer (6.25% + 3% = 9.25%)
- HEM benchmark: max(actual expenses, $2,500 + $700/dependent)
- Shading: salary 100%, rental 80%, self-employed 60-80%
- Credit cards serviced at 3% of limit regardless of balance
- PV of annuity over 30 years at assessment rate

**Closer — 5 Offer Tones:** EMPATHETIC, PROFESSIONAL, FAMILY_STORY, URGENT, INVESTOR_DIRECT — each uses Cialdini's 6 Principles of Persuasion

**QA — 5-Dimension Scoring:** Accuracy (30%), Relevance (20%), Completeness (20%), Timeliness (10%), Actionability (20%). Auto-generates improved skill templates when agents underperform. Rollback if score drops below 60.

**Chatbot — 6 RSS Feeds:** Domain News, Domain Melbourne, RealEstate.com.au, CoreLogic, AFR Property, SQM Research. VIC relevance scoring (30+ keywords). 50-article cache, 30-minute TTL.

---

## 7. 6 TOOLS

| Tool | File | What It Does |
|------|------|-------------|
| **BargainScorer** | `tools/bargain_scorer.py` | Calculates weighted 0-100 Bargain Score |
| **CompsEngine** | `tools/comps_engine.py` | In-memory comparable sales matching (suburb→type→beds→price→recency) |
| **ROICalculator** | `tools/roi_calculator.py` | Full cash-flow model: gross yield, net yield, cash-on-cash, ROI, payback |
| **DataCleaner** | `tools/data_cleaner.py` | Rule-based HTML→Property extraction (regex for AU property listings) |
| **OfferWriter** | `tools/offer_writer.py` | Template-based offer documents with 5 tone variants |
| **Scraper** | `tools/scraper.py` | Dual-mode: httpx async HTTP + Playwright browser automation |

---

## 8. DATA MODELS

All models use Pydantic with computed fields. Files in `nexusprop/models/`.

### Property (`models/property.py`)
- 16 property types: HOUSE, UNIT, APARTMENT, TOWNHOUSE, VILLA, LAND, RURAL, FARM, ACREAGE, COMMERCIAL, INDUSTRIAL, RETAIL, WAREHOUSE, DUPLEX, GRANNY_FLAT, OTHER
- 7 listing statuses: ACTIVE, UNDER_OFFER, SOLD, WITHDRAWN, PRE_MARKET, OFF_MARKET, AUCTION
- 10 sources: REA, DOMAIN, BOUTIQUE_AGENCY, COUNCIL_DA, etc.
- 6 conditions: EXCELLENT → KNOCKDOWN_REBUILD
- Australian-specific fields: strata_levies_quarterly, council_rates_annual, water_rates_annual, flood_zone, bushfire_zone, heritage_listed
- Computed: distress_score (0-100), effective_price, annual_holding_costs

### Deal (`models/deal.py`)
- 10 deal types: BTL, R2SA, FLIP, BRRR, HMO, PLO, SUBDIVISION, DEVELOPMENT, LAND_BANK, OWNER_OCCUPIER
- Embedded: Property + CashFlowModel (20+ fields, 12 computed metrics) + BargainScore (5 sub-scores)
- Computed: is_golden_opportunity, price_per_sqm, land_to_asset_ratio, payback_period_months, bmv_pct

### InvestmentProfile (`models/investment.py`)
- Risk: CONSERVATIVE → SPECULATIVE (5 levels)
- Experience: BEGINNER → EXPERT (5 levels)
- Goals: 9 types (CASH_FLOW, CAPITAL_GROWTH, FIRST_HOME, RETIREMENT, etc.)
- Entities: 9 types (PERSONAL, FAMILY_TRUST, SMSF, COMPANY, etc.)
- Finance strategies: 12 types (STANDARD_IO, BRRR, SMSF_LRBA, EQUITY_RELEASE, etc.)
- FinancialCapacity: income sources with bank shading, liabilities, cash, equity, SMSF balance
- Computed: estimated_borrowing_power (APRA formula), max_next_purchase, portfolio_lvr

### DealStructure (`models/investment.py`)
- 40+ fields: strategy, entity, financing, costs, projected returns, tax benefits, risk factors
- SMSF-specific: compliant flag, LRBA required, single acquirable asset
- BRRR-specific: after_repair_value, forced_equity_gain, refinance percentage
- Computed: total_capital_required, cash_on_cash_return, total_return_year1

### Portfolio (`models/investment.py`)
- Collection of PortfolioProperty records
- Computed: total_value, total_debt, total_equity, portfolio_lvr, total_weekly_rent, avg_gross_yield

### Subscription (`models/subscription.py`)
- 4 tiers + 3 add-ons (see Section 21)
- Usage tracking: analyses_used, property_views_today, dd_reports_used
- Feature gate methods: can_analyze, can_view_property, has_shadow_listings, etc.

### SuburbProfile (`models/suburb.py`)
- 15 data points: name, postcode, median_house, median_unit, growth, house_yield, unit_yield, population, auction_clearance_rate, avg_days_on_market, vacancy_rate, walkability_score, council, gentrification_status, infrastructure_notes

---

## 9. API ENDPOINTS (14 ROUTERS)

**Base URL:** `http://127.0.0.1:8001`

### Core Infrastructure
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | App info + docs link |
| GET | `/health` | System health: uptime, DB stats, services, auto-scout history |
| GET | `/api/v1/config` | Scoring thresholds + market defaults |
| GET | `/terminal` | Bloomberg Terminal dashboard |
| GET | `/landing` | Marketing landing page |

### Properties (`/api/v1/properties`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List/filter (suburb, type, price range, distress_only, sort, pagination) |
| GET | `/{id}` | Single property |
| DELETE | `/{id}` | Dismiss/archive |
| POST | `/search` | Advanced multi-filter search |
| POST | `/scout` | Trigger Scout Agent |
| POST | `/quick-scout` | On-demand suburb scout with fuzzy matching (1-10 synthetic props) |
| GET | `/locations/tree` | Full VIC location hierarchy |
| GET | `/locations/regions` | Regions for a state |
| GET | `/locations/search` | Fuzzy suburb search |
| GET | `/locations/stats` | Location DB summary |

### Deals (`/api/v1/deals`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all deals (sort by bargain_score, roi, cash_flow, price) |
| GET | `/{id}` | Single deal |
| POST | `/bulk-analyze` | Analyse all unanalysed properties |
| GET | `/quick-roi` | Quick ROI calculation |
| POST | `/value-add` | Value-add analysis |

### Offers (`/api/v1/offers`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all offers |
| POST | `/` | Generate offer (deal_id, buyer_name, tone, story) |

### Other Routers
| Router | Key Endpoint | Description |
|--------|-------------|-------------|
| **Profiler** | POST `/api/v1/profiler/build` | Build/update investor profile from free text |
| **Stacker** | POST `/api/v1/stacker/structure` | Structure a deal (entity, strategy, projections) |
| **Mentor** | POST `/api/v1/mentor/ask` | Ask coaching question |
| **Mentor** | POST `/api/v1/mentor/brief` | Generate weekly market brief |
| **Due Diligence** | POST `/api/v1/due-diligence/analyze` | Analyse S32/contract text |
| **Negotiation** | POST `/api/v1/negotiation/coach` | Real-time coaching |
| **QA** | GET `/api/v1/qa/health` | Agent health check |
| **QA** | POST `/api/v1/qa/evaluate-and-improve` | Full governance cycle |
| **Photos** | POST `/api/v1/photos/enhance-upload` | Upload + enhance photo |
| **Photos** | POST `/api/v1/photos/analyze` | Analyse photo quality |
| **Chatbot** | POST `/api/v1/chat/` | Send chat message |
| **Chatbot** | GET `/api/v1/chat/trending` | Trending VIC property news |
| **Chatbot** | GET `/api/v1/chat/summary` | AI market intelligence brief |
| **Subscriptions** | GET `/api/v1/subscriptions/tiers` | List all tiers + pricing |
| **Recommendations** | GET `/api/v1/recommendations/` | Top deal recommendations |
| **Webhooks** | POST `/api/v1/webhooks/stripe` | Stripe payment handler |

---

## 10. UI / UX — BLOOMBERG TERMINAL DASHBOARD

The entire dashboard is a **single HTML page** (`index.html`, 804 lines) with **one JavaScript file** (`nexusprop.js`, 1647 lines). No framework. No build step. Tailwind CSS loaded via CDN.

### Design Philosophy
- **Bloomberg Terminal aesthetic** — dark background, monospace data, dense information
- **Financial dashboard feel** — ticker tape, KPI strip, real-time indicators
- **Zero stock photos** — CSS gradient placeholders with emoji icons per property type
- **Data-first** — numbers, badges, and scores dominate; prose is secondary
- **Progressive disclosure** — beginners see simple views; power users get dense data

### Page Structure (top to bottom)
1. **Top Bar** — logo badge, title, region badge, live clock (AEST), live dot, 5 action buttons
2. **Ticker Tape** — scrolling financial-style data strip (60s loop, 15+ data points)
3. **KPI Strip** — 8-column grid: Properties, Analysed, Golden, Avg Score, Avg $/m², Offers, Profile, Pipeline
4. **Tab Bar** — 10 tabs (Deals, Properties, Offers, Pipeline, Profiler, Mentor, DD Bot, Negotiation, QA Engine, Photos)
5. **Main Content** — Active tab panel (flex-1, scrollable)
6. **Status Bar Footer** — version, DB status, scout status, agent count, API status, subscription tier
7. **Floating Chatbot** — FAB button (bottom-right) + expandable chat panel

---

## 11. COLOR SYSTEM & DESIGN TOKENS

Every color in the UI is defined as a design token. No arbitrary colors.

| Token Name | Hex | Where It's Used |
|-----------|-----|----------------|
| `terminal-bg` | `#0a0e17` | Page background, input backgrounds, nested panels |
| `terminal-panel` | `#111827` | Card backgrounds, header, footer, tab bar |
| `terminal-border` | `#1f2937` | All borders, dividers, separator lines |
| `terminal-accent` | `#00d4aa` | **Primary brand color** — buttons, active tabs, links, positive highlights |
| `terminal-gold` | `#fbbf24` | Golden Opportunity badges, pulsing borders, premium labels |
| `terminal-warn` | `#f59e0b` | Warning states, Due Diligence highlights, amber badges |
| `terminal-danger` | `#ef4444` | Errors, distress signals, negative cash flow |
| `terminal-info` | `#3b82f6` | Information badges, negotiation section |
| `terminal-green` | `#10b981` | Positive values, live dot, BMV badges, status indicators |
| `terminal-red` | `#ef4444` | Negative values, health bars below 60, errors |
| `terminal-purple` | `#a855f7` | Profiler section, Mentor section accents |
| `terminal-bright` | `#ffffff` | Headers, bold numeric values, property names |
| `terminal-text` | `#e5e7eb` | Default body text |
| `terminal-dim` | `#9ca3af` | Secondary text, specs, labels |
| `terminal-muted` | `#6b7280` | Tertiary text, column headers, timestamps |

### Property Type Gradients (Inline CSS — NOT Tailwind classes)

Each property type has a unique gradient background for its placeholder card:

| Property Type | Gradient | Emoji |
|--------------|----------|-------|
| House | `linear-gradient(135deg, #1e3a5f 0%, #152238 100%)` | 🏠 |
| Apartment | `linear-gradient(135deg, #3b1f6e 0%, #251545 100%)` | 🏢 |
| Unit | `linear-gradient(135deg, #2e2b6e 0%, #1c1945 100%)` | 🏢 |
| Townhouse | `linear-gradient(135deg, #134e4a 0%, #0f302e 100%)` | 🏘 |
| Villa | `linear-gradient(135deg, #065f46 0%, #053d2e 100%)` | 🏡 |
| Land | `linear-gradient(135deg, #14532d 0%, #0a3018 100%)` | 🌳 |
| Commercial | `linear-gradient(135deg, #7c2d12 0%, #4a1a0a 100%)` | 🏗 |
| Industrial | `linear-gradient(135deg, #374151 0%, #1f2937 100%)` | 🏭 |
| Warehouse | `linear-gradient(135deg, #334155 0%, #1e293b 100%)` | 📦 |
| Retail | `linear-gradient(135deg, #78350f 0%, #451e08 100%)` | 🏪 |
| Duplex | `linear-gradient(135deg, #155e75 0%, #0e3a4a 100%)` | 🏠 |
| Farm | `linear-gradient(135deg, #3f6212 0%, #263a0b 100%)` | 🌾 |
| Rural | `linear-gradient(135deg, #14532d 0%, #0a3018 100%)` | 🌿 |
| Acreage | `linear-gradient(135deg, #065f46 0%, #053d2e 100%)` | 🌳 |

> **Important:** These are set via inline `style="background: linear-gradient(...)"` NOT via Tailwind classes. Tailwind CDN doesn't support JIT-generated gradient classes.

### Strategy Badge Colors

| Strategy | Background | Text Color |
|----------|-----------|------------|
| BTL | `#065f46` | `#6ee7b7` |
| R2SA | `#713f12` | `#fde68a` |
| FLIP | `#581c87` | `#d8b4fe` |
| BRRR | `#7c2d12` | `#fdba74` |
| HMO | `#1e3a5f` | `#93c5fd` |
| PLO | `#3f3f46` | `#d4d4d8` |
| SUBDIVISION | `#44403c` | `#e7e5e4` |
| DEVELOPMENT | `#1c1917` | `#a8a29e` |
| LAND_BANK | `#365314` | `#bef264` |

### Bargain Score Color Thresholds
| Score Range | Color Token | Meaning |
|-------------|-----------|---------|
| ≥ 85 | `terminal-gold` (#fbbf24) | **GOLDEN OPPORTUNITY** |
| ≥ 65 | `terminal-green` (#10b981) | Strong deal |
| ≥ 40 | `terminal-warn` (#f59e0b) | Fair deal |
| < 40 | `terminal-red` (#ef4444) | Weak deal |

---

## 12. TYPOGRAPHY

| Role | Font Family | Weight | Size | Notes |
|------|------------|--------|------|-------|
| Headings & labels | **Inter** | 600–800 | 14–16px | Clean sans-serif |
| Body text | **Inter** | 400 | 12–14px | |
| Monospace data | **JetBrains Mono** | 400–700 | 9–14px | All numbers, prices, scores |
| KPI numbers | **JetBrains Mono** | 700 | 16px | Large bold in KPI strip |
| Ticker tape | **JetBrains Mono** | 400 | 11px | Scrolling data |
| Metric pills | **JetBrains Mono** | 400 | 9px | Deal card badges |
| Micro-labels | Inter or JetBrains Mono | 400–600 | 8–10px | Uppercase, tracking: 0.5px+ |

**Font import:**
```
https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap
```

---

## 13. CSS ANIMATIONS

### 5 Keyframe Animations

| Animation | Duration | Used On | Effect |
|-----------|----------|---------|--------|
| **Ticker scroll** | 60s linear infinite | Ticker tape strip | Continuous right-to-left horizontal scroll |
| **Live dot blink** | 2s ease-in-out infinite | Header live indicator, chatbot | Green dot fades to 30% opacity and back |
| **Cursor blink** | 1s step-end infinite | Empty state "AWAITING DATA" | Teal block cursor toggles on/off |
| **Golden pulse** | 2s infinite | Deal cards with score ≥85 | Gold box-shadow ring expands outward and fades |
| **Fade-in** | 0.2s ease-out | Cards, toasts, modals, chat messages | Slide-up 4px + fade from 0 to 1 |

### Golden Pulse (signature visual)
```css
@keyframes goldPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.3); }
  70% { box-shadow: 0 0 0 6px rgba(251, 191, 36, 0); }
}
```
This is applied to any deal card with Bargain Score ≥ 85. It's the most recognisable visual cue on the platform — a pulsing golden glow.

### Custom Scrollbar
```css
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0e17; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }
```

---

## 14. PAGE LAYOUT — COMPONENT BY COMPONENT

### Top Bar (Header)
- **Left:** PIM logo badge (24px teal square) → "PROPERTY INSIGHTS" → "MELBOURNE + VIC" badge → clock (AEST, updates every second) → live green dot + "LIVE"
- **Right:** 5 buttons — ▶ SCOUT (teal), ROI (gray), MENTOR (purple), QA (blue), User avatar (circle with "U")

### Ticker Tape
Continuous horizontal scroll (60s loop). Data points separated by `│`:
- MEL INNER $1.28M ▲2.3%, MEL WEST $720K ▲4.5%, MEL NORTH $680K ▲3.8%, MEL SE $650K ▲4.2%
- GEELONG $690K, BENDIGO $530K, BALLARAT $490K
- RBA RATE 4.35%, MEL AUCTION CLR 68.2%, MEL VACANCY 1.1%
- SHADOW LISTINGS (count), GOLDEN OPPS (count), AUTO-SCOUT ACTIVE, DB SQLite (size), QA HEALTH

### KPI Strip
8-column grid. Each cell: right border + bottom border, centered text.

| Col | Label | Color |
|-----|-------|-------|
| 1 | PROPERTIES | White |
| 2 | ANALYSED | White |
| 3 | GOLDEN | Gold |
| 4 | AVG SCORE | Teal |
| 5 | AVG $/M² | White |
| 6 | OFFERS | White |
| 7 | PROFILE | Purple |
| 8 | PIPELINE | Green (idle) / Amber (running) / Red (error) |

### Status Bar (Footer)
- **Left:** "PIM v4.0.0" · status text · "propertyinsightsmelbourne.com.au"
- **Right:** DB status (green) · Scout status (green) · "12 AGENTS + VALUE-ADD ENGINE" · API status (green) · Subscription tier (teal)

---

## 15. 10 TAB PANELS

### Tab Bar
10 tabs, horizontal row, active tab has teal underline + teal text. Default active: **DEALS**.

| # | Tab | What It Shows |
|---|-----|---------------|
| 1 | **DEALS** | Deal cards in grid (1-3 cols), 10 filter controls, sort by 7 criteria, Golden-only toggle |
| 2 | **PROPERTIES** | Property list view (horizontal rows), suburb search, type filter, distressed-only toggle |
| 3 | **OFFERS** | Generated offer documents, full text display |
| 4 | **PIPELINE** | Execute full agent pipeline — region/suburb/strategy config + run button |
| 5 | **👤 PROFILER** | Investor profile builder — free-text input → APRA borrowing power, readiness score, follow-up questions |
| 6 | **🎓 MENTOR** | AI coaching chat — 7 topic buttons + chat interface + weekly brief |
| 7 | **DD BOT** | Due diligence — paste S32/contract text → 10-category risk assessment |
| 8 | **NEGOTIATION** | Live coaching — agent profile form + real-time chat |
| 9 | **🔬 QA ENGINE** | System health grid (per-agent scores), performance stats, self-governance cycle |
| 10 | **📸 PHOTOS** | Photo upload → 5 enhancement presets + before/after preview |

### Deal Card Anatomy (Deals Tab)
```
┌──────────────────────────────────────────┐
│  [GRADIENT BLOCK — 112px]                │  ← Property type gradient + emoji
│  🏠  HOUSE — BRUNSWICK                   │
├──────────────────────────────────────────┤
│  Brunswick, VIC              ┌── 72 ──┐  │  ← Suburb + Bargain Score
│  123 Smith St                │ BARGAIN │  │
│                              │  SCORE  │  │
│  $650,000 [BTL] [BMV 12%] 🏆 GOLDEN    │  ← Price + badges
│  3BR 2BA 1🚗  HOUSE  450m²  $520/wk    │  ← Specs line
│  ┌──────┐ ┌────────┐ ┌────────┐        │  ← Metric pills (up to 7)
│  │GY 5.2│ │NY 3.8% │ │CF $280 │        │
│  └──────┘ └────────┘ └────────┘        │
│  ⚠⚠ 2 distress signals                  │  ← Red, only if signals
│                        [OFFER][DETAILS]  │  ← Action buttons
└──────────────────────────────────────────┘
```
- **Golden cards:** Gold border + pulsing golden glow animation
- **Normal cards:** Standard gray border
- Click anywhere → opens Deal Detail modal

---

## 16. 5 MODALS

All modals: fixed overlay, `bg-black/80` backdrop, centered panel, max-h 85vh scrollable, fade-in animation.

| Modal | Trigger | Width | Key Content |
|-------|---------|-------|-------------|
| **Quick ROI** | Header ROI button | 384px | Price + rent → yields, cash flow, stamp duty |
| **Offer Generation** | "OFFER" button on deal card | 448px | Name, entity, budget, tone (5 options), story → AI offer |
| **Deal Detail** | Click any deal card | 672px | Full deep dive: gradient header, score breakdown, 3-row financial grid, renovation analysis, distress signals, AI analysis, listing text, links to Domain/REA |
| **Property Detail** | Click property in list | 672px | Property info, pricing, agent, "Verify on Real Portals" links |
| **Location Scout** | Header SCOUT button | 672px | 3 scope modes (All VIC / By Region / By Suburb), fuzzy search, market data preview, pill tag selections |

---

## 17. CHATBOT WIDGET

**FAB (Floating Action Button):** Bottom-right, 56px teal circle, 💬 emoji, red notification badge when news available.

**Chat Panel** (384px wide, opens above FAB):
1. **Header:** Live dot + "MELBOURNE MARKET AI" + refresh/clear/close buttons
2. **Trending News Strip:** Up to 4 articles with VIC relevance indicators (🟢🟡⚪), clickable titles
3. **Messages Area:** User (blue bg, right-aligned) + AI (green bg, left-aligned) + typing indicator
4. **Input Footer:** Text input + ▶ send button + 3 quick-chat buttons (📰 News, 📊 Yields, 🔮 Outlook)

**Chat Formatting:** Supports **bold**, bullet points with teal bullets, numbered lists with teal numbers, clickable links.

---

## 18. LANDING PAGE

Separate marketing page at `/landing` with the same design system.

### Special CSS
- `.gradient-text` — teal → blue → purple gradient on hero text
- `.hero-glow` — radial gradient glow from top
- `.card-glow:hover` — subtle teal glow on hover
- `.float` — 6s infinite vertical bounce animation

### Sections
1. **Fixed Nav** — blurred bg, logo, nav links, "Launch Terminal" CTA
2. **Hero** — "The Bloomberg Terminal for Australian Property" (gradient text), 2 CTAs
3. **6 Agent Cards** — Scout, Analyst, Closer, Concierge, DD Bot, Negotiation Shadow
4. **ROI Comparison** — PIM ($2,388/yr) vs Buyer's Agent ($12K-$30K) vs Junior Analyst ($60K+)
5. **4-Tier Pricing** — Explorer (Free) → Investor ($199) → Pro Sourcer ($499) → The Closer ($2,500)
6. **CTA Footer** — "Stop Overpaying for Property Intelligence"

---

## 19. LOCATION DATABASE — 134 SUBURBS, 15 REGIONS

File: `nexusprop/locations.py`

| # | Region | Key Suburbs | Median Range |
|---|--------|------------|-------------|
| 1 | Melbourne — CBD & Inner City | Melbourne CBD, Southbank, Docklands, Carlton, Parkville | $880K–$2.5M |
| 2 | Melbourne — Inner North | Fitzroy, Collingwood, Brunswick, Coburg, Preston | $950K–$1.45M |
| 3 | Melbourne — Inner East | Richmond, Hawthorn, Kew, Camberwell, Canterbury, Box Hill | $1.25M–$3.2M |
| 4 | Melbourne — Inner South | South Yarra, Prahran, St Kilda, Albert Park, Elwood | $980K–$2.2M |
| 5 | Melbourne — Inner West | Footscray, Yarraville, Williamstown, Newport, Maribyrnong | $780K–$1.35M |
| 6 | Melbourne — Western Growth | Werribee, Point Cook, Tarneit, Melton, Sunshine | $480K–$750K |
| 7 | Melbourne — Northern Growth | Craigieburn, Epping, South Morang, Doreen, Mernda | $460K–$680K |
| 8 | Melbourne — Eastern Suburbs | Doncaster, Ringwood, Croydon, Lilydale, Bayswater | $680K–$1.35M |
| 9 | Melbourne — South Eastern | Cranbourne, Pakenham, Berwick, Dandenong, Officer | $520K–$850K |
| 10 | Melbourne — Bayside & Peninsula | Brighton, Hampton, Frankston, Mornington, Sorrento | $680K–$3M |
| 11 | Geelong & Surf Coast | Geelong, Torquay, Ocean Grove, Lara, Armstrong Creek | $420K–$1.1M |
| 12 | Bendigo & Goldfields | Bendigo, Castlemaine, Kangaroo Flat, Eaglehawk | $380K–$780K |
| 13 | Ballarat & Central Highlands | Ballarat, Wendouree, Buninyong, Sebastopol | $390K–$680K |
| 14 | Gippsland | Traralgon, Morwell, Sale, Warragul, Drouin | $280K–$680K |
| 15 | Hume & North East VIC | Shepparton, Wodonga, Wangaratta, Mildura, Swan Hill | $320K–$460K |

Each suburb has 15 data points: name, postcode, median_house, median_unit, growth, house_yield, unit_yield, population, auction_clearance_rate, avg_days_on_market, vacancy_rate, walkability_score, council, gentrification_status, infrastructure_notes.

---

## 20. 40 SEED PROPERTIES

File: `nexusprop/seed_data.py` — 40 realistic Victorian properties auto-loaded on startup.

- **Types:** Houses, apartments, townhouses, units, commercial, land, rural, industrial
- **Price range:** $320K (Moe industrial) → $2.2M (Brighton house)
- **Every property has:** Full address, suburb, postcode, all specs, listing text (realistic marketing copy), source_url (real Domain.com.au / REA search links), distress signals where applicable, rates/levies
- **Distress keywords embedded naturally** in listing text (e.g., "deceased estate", "must sell", "vendor motivated")
- **Real infrastructure references:** Metro Tunnel, West Gate Tunnel, Level Crossing Removals

---

## 21. SUBSCRIPTION TIERS & PRICING

### 4 Tiers

| Tier | Price | Analyses/mo | Views/day | Key Features |
|------|-------|------------|-----------|--------------|
| **EXPLORER** | Free | 3 | 3 | Basic suburb data, public comps, email alerts |
| **INVESTOR** | $199/mo | 50 | Unlimited | Shadow listings, full ROI models, Bargain Score, offer generation |
| **PRO_SOURCER** | $499/mo | Unlimited | Unlimited | + First Look Premium, bulk pipeline, WhatsApp alerts, 5 DD reports/mo, API access |
| **THE_CLOSER** | $2,500/deal | Unlimited | Unlimited | + Everything above, unlimited DD, Negotiation Shadow, dedicated support, custom strategy |

### 3 Premium Add-Ons
| Add-On | Price | Description |
|--------|-------|-------------|
| **Due Diligence Bot** | $99/report | AI Section 32 & Contract analysis — 30+ red flag categories |
| **Negotiation Shadow** | $500/mo | Real-time WhatsApp coaching during negotiations |
| **First Look Premium** | Included in Pro+ | 15-min head start on new shadow listings |

---

## 22. 10 INVESTOR PERSONAS

The Profiler Agent identifies users into one of 10 personas on first login to adapt the entire platform experience.

| # | Persona | Who They Are | Properties | Income | Natural Tier |
|---|---------|-------------|-----------|--------|-------------|
| 1 | **First Home Dreamer** | Never bought, saved up, overwhelmed | 0 | $55K–$110K | Free |
| 2 | **Stepping Up** | Owns home, wants first IP, nervous | 1 (PPOR) | $90K–$180K | $199/mo |
| 3 | **Accidental Landlord** | Inherited/kept a property, not optimising | 1-2 | $80K–$200K | Free → $199 |
| 4 | **Equity Unlocked** | 2-3 properties, accelerating | 2-3 | $120K–$250K | $199 → $499 |
| 5 | **Portfolio Builder** | Building to 10+, financial freedom | 4-8 | $150K–$350K | $499/mo |
| 6 | **Tax Strategist** | High income, property as tax shelter | 1-5 | $200K–$500K+ | $199/mo |
| 7 | **SMSF Retiree** | Buying through super, compliance-cautious | 1-3 | $80K–$150K + super | $199/mo |
| 8 | **Developer/Flipper** | Value-add and sell, feasibility-focused | 0-3 held + flipping | $100K–$500K+ | $499 or $2,500/deal |
| 9 | **Professional Sourcer** | Buyer's agent buying for clients | 2-10+ personal | $150K–$500K+ | $2,500/deal |
| 10 | **Enterprise/Syndicate** | Fund manager, $5M–$100M+ AUM | 10-100+ | $300K–$2M+ | Custom $2K–$10K/mo |

### Persona Identification (5-Question Onboarding)
1. "How many properties do you currently own?" → Routes to broad persona bucket
2. "What brings you to Property Insights today?" → 10 answer options map to 10 personas
3. Income range → Refines within bucket
4. Urgency → Adjusts coaching aggressiveness
5. "Have you worked with a mortgage broker?" → Knowledge depth/jargon comfort

### Estimated Lifetime Value
| Persona | Annual LTV |
|---------|-----------|
| First Home Dreamer | $0 → $597 |
| Stepping Up | $2,388 |
| Accidental Landlord | $1,194 |
| Equity Unlocked | $4,188 |
| Portfolio Builder | $8,988 |
| Tax Strategist | $2,388 |
| SMSF Retiree | $2,388 |
| Developer/Flipper | $10,494 |
| Professional Sourcer | $30,000 |
| Enterprise/Syndicate | $24K–$120K |

---

## 23. LLM STRATEGY — 3-TIER FALLBACK

Every agent's `ask_llm()` method follows this cascade:

```
1. Ollama (FREE, LOCAL)
   ↓ fails?
2. Anthropic Claude (PAID API)
   ↓ fails or no key?
3. Rule-based fallback (NO AI)
   → Agent-specific logic ensures the app NEVER breaks
```

- **Ollama:** `http://localhost:11434/api/chat`, model `llama3.2`, `stream: false`
- **Anthropic:** `anthropic.AsyncAnthropic`, only if Ollama fails AND ANTHROPIC_API_KEY is set
- **No-AI:** Each agent has its own smart fallback (e.g., Analyst still calculates all financials, just no narrative text; Scout uses regex-based DataCleaner; Closer uses template offer letters)

---

## 24. PERSISTENCE LAYER

**Database:** SQLite with WAL mode (`pia.db` at project root)

| Table | Purpose |
|-------|---------|
| `properties` | JSON blob per property (UUID as PK) |
| `deals` | JSON blob per deal |
| `offers` | JSON blob per offer |
| `scout_runs` | Audit trail (timestamp, new_properties, new_deals, duration_ms, notes) |

**Functions:** `init_db()`, `save_properties_bulk()`, `save_deals_bulk()`, `save_offer()`, `save_property()`, `save_deal()`, `load_all_properties()`, `load_all_deals()`, `load_all_offers()`, `delete_property()`, `delete_deal()`, `delete_offer()`, `count_properties()`, `count_deals()`, `count_offers()`, `db_stats()`, `log_scout_run()`, `get_scout_history()`

Database is auto-created on first startup. Delete `pia.db` for a clean restart (seed data repopulates automatically).

---

## 25. AUTO-SCOUT BACKGROUND TASK

File: `nexusprop/auto_scout.py`

Runs every 15-30 minutes via `asyncio.create_task()` on server startup:
1. Picks 2-5 random suburbs from the 134-suburb database
2. Generates synthetic properties priced around suburb median (±8-22% discount)
3. Runs Analyst Agent → creates deals with Bargain Scores
4. Persists to SQLite
5. Logs to `scout_history` table

This keeps the deal pipeline flowing without user intervention.

---

## 26. HONESTY & INTEGRITY POLICIES

1. **No Fake Photos** — CSS gradient placeholders with emoji icons. Never stock photos.
2. **SIMULATED LISTING Badge** — All properties marked as simulated for demonstration
3. **"Verify on Real Portals" Links** — Every property links to Domain.com.au and REA.com.au search pages for the actual suburb
4. **Legal Disclaimers** — All offers marked "Commercial Strategy Draft — not legal advice"
5. **Accurate Market Data** — Suburb medians, infrastructure projects, rents, and growth rates verified against real Victorian market data

---

## 27. 100x VALUE RECOMMENDATIONS (ROADMAP)

These are prioritised features to transform PIM from an MVP into an addictive product:

### Priority 1 — Critical
| # | Feature | What It Does |
|---|---------|-------------|
| R1 | **WebSocket Live Deal Feed** | Real-time deal push via `/ws/deals`, desktop notifications, sound effects |
| R2 | **Gamification — Investor XP** | Points for actions, levels (Apprentice→Tycoon), achievement badges, leaderboard |

### Priority 2 — High Value
| # | Feature | What It Does |
|---|---------|-------------|
| R3 | **Interactive Suburb Heatmap** | Clickable SVG/Canvas map of VIC, colored by price/yield/growth/score |
| R4 | **Deal Watchlist + Price Tracking** | Watch button, price change alerts, "WATCHLIST" tab |
| R5 | **Daily Morning Wrap** | 7am AEST auto-brief: top golden deals, auction results, suburb of week |
| R6 | **Side-by-Side Comparison** | Compare 2-4 deals in aligned columns, winning metrics highlighted green |

### Priority 3 — Quick Wins
| # | Feature | What It Does |
|---|---------|-------------|
| R7 | **Score Explainability** | "?" icon on Bargain Score → shows point breakdown per factor |
| R8 | **Conversational Onboarding** | 5-step wizard replacing free-text profiler input |
| R9 | **Sparklines on Deal Cards** | 30-day suburb price trend + yield comparison micro-charts |
| R10 | **One-Click Follow-Up Actions** | Context-aware next-step buttons after every AI interaction |
| R11 | **Streak Counter + Session Timer** | 🔥 streak in footer, session time, confetti at 7-day streak |
| R12 | **Keyboard Shortcuts** | Bloomberg-style: D=Deals, P=Properties, S=Scout, R=ROI, M=Mentor, C=Chat |

### Priority 4 — Nice to Have
| # | Feature | What It Does |
|---|---------|-------------|
| R13 | **Theme Toggle** | Dark/Light modes + custom accent color picker |
| R14 | **PDF/CSV Export** | 1-page deal report PDF, filtered deals CSV download |
| R15 | **Social Sharing + Referral** | Share golden deals, referral program (invite 3 → 1 month free) |

### Addiction Framework (Nir Eyal Hook Model)
| Layer | Current | Target |
|-------|---------|--------|
| **Trigger** | Manual (user opens terminal) | Push notifications, daily briefing, price alerts |
| **Action** | Browse deals, click buttons | 1-click follow-ups, keyboard shortcuts, conversational onboarding |
| **Variable Reward** | New deals on scout | Real-time deal feed, streak counter, leaderboard changes |
| **Investment** | Profile building | Watchlist, badges, XP progress, exported reports |

---

## 28. PERSONA-DRIVEN FEATURE MATRIX

### How Agents Adapt Per Persona Group

| Agent | Beginners (1-3) | Growers (4-6) | Specialists (7-8) | Pros (9-10) |
|-------|-----------------|---------------|-------------------|-------------|
| **Scout** | Simple results, bargain badge | Full metrics, yield overlay | SMSF flag / dev potential | Bulk pipeline, API, custom alerts |
| **Analyst** | Plain English, 3 numbers | Full ROI, depreciation | SMSF tax / feasibility | Portfolio aggregation, stress test |
| **Closer** | Guided wizard, templates | Flexible with strategy | SMSF-compliant / DA offer | Multi-offer pipeline, white-label |
| **Profiler** | 1 question at a time | 3-5 questions | Specialist path | Multi-profile, client-brief mode |
| **Stacker** | "What you can afford" | IO vs PI, equity release | LRBA / JV + construction | Multi-deal, capital allocation |
| **Mentor** | Teacher — explains all | Peer — debates strategy | Specialist coach | Portfolio advisor, fund strategy |
| **Chatbot** | No jargon, beginner news | Analysis with depth | Planning regs, SMSF rules | Institutional intelligence |

### How UI Adapts Per Persona Group

| UI Element | Beginners (1-3) | Growers (4-6) | Specialists (7-8) | Pros (9-10) |
|-----------|-----------------|---------------|-------------------|-------------|
| **Default tab** | Suburb Explorer | Deal Pipeline | Specialist Dashboard | Portfolio Command Centre |
| **Metric density** | 3-5 KPIs | 8-12 KPIs | 10-15 KPIs | 20+ KPIs |
| **Jargon** | Plain English + tooltips | Industry terms, hover defs | Specialist terminology | Institutional language |
| **Primary CTA** | "Learn More" / "Save" | "Analyse" / "Generate Offer" | "Check Compliance" | "Add to Pipeline" / "Export" |
| **Tutorials** | Yes, progressive | Optional, dismissible | Specialist tips only | None — Pro Mode |
| **Notifications** | 1/day max | 3/day | As matches appear | Real-time stream |
| **Export** | None (in-app) | PDF summary | PDF + CSV | API + JSON + branded PDF |

---

## 29. KEY DECISIONS & CONVENTIONS

### Design Decisions
- **No framework** for frontend — vanilla HTML/JS/Tailwind for simplicity and no build step
- **No stock photos** — CSS gradient placeholders with emoji. Honest about simulated data.
- **Inline CSS gradients** — Tailwind CDN doesn't support JIT-generated gradient classes; all property type gradients are inline `style` attributes
- **Single-page dashboard** — All 10 tabs rendered at once, hidden/shown via JS
- **SQLite not Postgres** — MVP simplicity, WAL mode for concurrent reads, JSON blob storage
- **Ollama first** — Free local LLM keeps costs at $0 during development
- **Every agent has no-AI fallback** — App functions (with reduced quality) even without any LLM

### Naming Conventions
- **Files:** snake_case (Python standard)
- **Classes:** PascalCase (Pydantic models, agents)
- **Enums:** UPPER_SNAKE_CASE values
- **API routes:** kebab-case paths
- **Frontend IDs:** kebab-case (`stat-properties`, `panel-deals`, `ticker-golden`)
- **CSS classes:** Tailwind utility classes + custom `terminal-*` color tokens

### Australian Specifics to Remember
- Currency is AUD ($)
- State: VIC (Victoria)
- Timezone: AEST (`Australia/Sydney`)
- Stamp duty varies by state — marginal bracket system
- APRA regulates bank lending — assessment rate = actual + 3% buffer
- Section 32 (Vendor Statement) is VIC-specific pre-contract disclosure
- Negative gearing: investment losses offset PAYG income
- SMSF: Self-Managed Super Fund — strict ATO rules for property
- LVR: Loan-to-Value Ratio — 80% = no LMI, above requires Lenders Mortgage Insurance
- PPOR: Principal Place of Residence (your home)
- IP: Investment Property

---

*This document covers everything we've built so far. Share it with the team. When in doubt, check `SPARK_DESCRIPTION.md` for the exhaustive specification or the actual code in `nexusprop/`.*
