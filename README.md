# Property Insights Australia — Your Digital Property Associate

> **"The Bloomberg Terminal for Australian Property."** — Investment-grade intelligence that replaces a $60k/year junior analyst.

## What Is Property Insights Australia?

Property Insights Australia (PIA) is your **Digital Property Associate** — an AI-powered platform that delivers investment-grade real estate intelligence at a fraction of the cost of a traditional buyer's agent ($12k–$30k per deal) or a junior analyst hire ($60k/year).

### Core Value Proposition
- **Save $12k–$30k per transaction** vs hiring a buyer's agent
- **Investment-Grade Analysis** — CAGR, land-to-asset ratios, infrastructure pipeline impact
- **Shadow Listings** from 40+ boutique agencies — find deals before they hit REA/Domain
- **First Look Premium** — 15-minute head start on new listings
- **Due Diligence Bot** — automated Section 32 / Contract of Sale red flag detection
- **Negotiation Shadow** — real-time WhatsApp coaching based on agent sales history

---

## The Agentic Stack

| Agent | Role | Superpower |
|-------|------|------------|
| **Scout** | Harvests listings from non-conventional sources | Finds off-market & pre-market signals |
| **Analyst** | Investment-grade financial analysis & scoring | CAGR, land-to-asset ratios, street-level pricing |
| **Closer** | Drafts persuasive, legally-safe offer documents | Turns buyers into negotiators |
| **Live Comps** | Real-time comparable sales intelligence | Exposes underquoting tactics |
| **Concierge** | Hyper-personalized WhatsApp/SMS alerts | Learns your "vibe" — no more junk |
| **Due Diligence Bot** | Section 32 & Contract of Sale analysis | Flags red flags in legal docs ($99/report) |
| **Negotiation Shadow** | Real-time WhatsApp coaching | Agent sales history-backed strategy ($500/mo) |

---

## Feature Set

| Feature | What It Does | Why It Beats Domain |
|---------|-------------|---------------------|
| Shadow Listings | Aggregates from 40+ boutique agency sites | Find houses before they hit the "big" sites |
| Tactical Offer Engine | AI-drafted persuasive offer letters | Turns a "buyer" into a "negotiator" instantly |
| Live Comps Agent | Real-time sold data (not just advertised) | Cuts through agent underquoting |
| Hyper-Personalized Concierge | WhatsApp/SMS agent that learns your preferences | No more irrelevant email alerts |
| Bargain Score™ | Proprietary distress-adjusted price metric | Instant signal on whether it's a deal or a trap |

## Pricing

| Tier | Price | What You Get |
|------|-------|-------------|
| **Explorer** | Free | Basic suburb data, 3 property views/day, public comps |
| **Investor** | $199/mo | Full agent stack, 50 analyses/mo, email alerts, ROI calculator |
| **Pro Sourcer** | $499/mo | Unlimited analyses, First Look Premium, bulk pipeline, WhatsApp alerts |
| **The Closer** | $2,500/deal | White-glove service — full pipeline, offer generation, negotiation coaching |

### Premium Add-Ons
- **Due Diligence Bot** — $99/report — automated Section 32 / Contract of Sale red flag analysis
- **Negotiation Shadow** — $500/mo — real-time WhatsApp coaching based on agent sales history
- **First Look Premium** — 15-minute head start on new listings (included in Pro Sourcer+)

---

## ROI vs Traditional Options

| | Property Insights Australia | Buyer's Agent | Junior Analyst Hire |
|---|---|---|---|
| **Annual Cost** | $2,388/yr (Investor) | $12k–$30k per deal | $60k+/yr salary |
| **Coverage** | National, 24/7, unlimited | 1 city, business hours | 1 person, limited |
| **Speed** | Instant analysis | Days–weeks | Hours–days |
| **Consistency** | Investment-grade, every time | Variable | Learning curve |
| **Scalability** | Unlimited deals | 1 at a time | Limited bandwidth |

---

## Tech Stack

- **Python 3.12+** — Core backend
- **FastAPI** — API layer
- **Playwright/ZenRows** — Bot-detection-resistant scraping
- **Claude Opus 4.6** — Reasoning engine for analysis & offer generation
- **Supabase Vector** — Vector DB for RAG
- **Twilio** — WhatsApp/SMS notifications
- **TailwindCSS** — Dashboard UI

---

## Quick Start

```bash
# 1. Clone and install
cd re2026
pip install -r requirements.txt
playwright install

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the orchestrator
python -m nexusprop.orchestrator.orchestrator

# 4. Start the API
uvicorn nexusprop.api.main:app --reload

# 5. Open the dashboard
# Navigate to http://localhost:8000 (Bloomberg Terminal UI)
# Or visit http://localhost:8000/landing.html for the landing page
```

---

## Project Structure

```
nexusprop/
├── agents/          # Scout, Analyst, Closer, Concierge, Live Comps, Due Diligence, Negotiation Shadow
├── tools/           # Scraping, ROI calc, Bargain Score, Offer Writer
├── scrapers/        # Boutique agencies, Council DAs, Public notices
├── orchestrator/    # Multi-agent pipeline orchestration
├── database/        # Vector store & data access layer
├── api/             # FastAPI endpoints
├── notifications/   # WhatsApp, SMS, Email
├── models/          # Pydantic data models (incl. subscription tiers)
├── config/          # Settings & environment
├── frontend/        # Bloomberg Terminal Dashboard + Landing Page
└── tests/           # Test suite
```

---

## Market Coverage

🇦🇺 **Australia-first** — Built for Australian terminology (Strata, Council Rates, Stamp Duty, Section 32), Australian data sources, and Australian market dynamics.

---

## www.propertyinsightsaustralia.com.au

---

## License

Proprietary — All rights reserved. Property Insights Australia Pty Ltd.
