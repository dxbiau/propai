# Property Insights Melbourne — GitHub Spark Blueprint

> **Dream it. See it. Ship it.**
> A complete specification to transform this idea into a full-stack intelligent app in a snap.

---

## THE VISION IN ONE SENTENCE

**A Bloomberg Terminal for Melbourne property investors** — 13 AI agents that scout, analyse, negotiate, coach, and close real estate deals across 134 suburbs in Victoria, Australia, powered by local LLM (Ollama) with paid API fallback, all rendered in a dark-mode financial terminal UI.

---

## APPLICATION IDENTITY

| Field | Value |
|-------|-------|
| **Name** | Property Insights Melbourne |
| **Tagline** | Your Digital Property Associate |
| **Domain** | Melbourne Metro + Regional Victoria (VIC), Australia |
| **Tech Stack** | Python 3.13 + FastAPI backend, vanilla HTML/JS/Tailwind frontend, SQLite persistence, Ollama (llama3.2) local LLM |
| **Aesthetic** | Bloomberg Terminal — dark (#0a0e17 background), monospace fonts (JetBrains Mono), teal accent (#00d4aa), gold highlights (#fbbf24) |
| **URL** | `http://localhost:8001/terminal` (dashboard), `/landing` (marketing page) |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Single Page)                 │
│  Bloomberg Terminal Dashboard — HTML + Tailwind + JS     │
│  10 Tab Panels + 5 Modals + Floating Chatbot Widget     │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│  14 API Routers + Rate Limiting + Request Logging        │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  Scout   │ Analyst  │ Closer   │ Profiler │ Stacker     │
│  Agent   │ Agent    │ Agent    │ Agent    │ Agent       │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│  Mentor  │ QA       │ DueDil   │ NegShadow│ LiveComps   │
│  Agent   │ Agent    │ Agent    │ Agent    │ Agent       │
├──────────┼──────────┼──────────┴──────────┴─────────────┤
│ Concierge│ PhotoEnh │         Chatbot Agent              │
│  Agent   │ Agent    │    (RSS News Scraper + Chat)       │
├──────────┴──────────┴───────────────────────────────────┤
│            Orchestrator Pipeline Engine                   │
│  Profiler → Scout → Analyst → Comps → Stacker →         │
│  Closer → Concierge → Mentor → QA                       │
├─────────────────────────────────────────────────────────┤
│  6 Tools: BargainScorer, CompsEngine, ROICalculator,     │
│           DataCleaner, OfferWriter, Scraper               │
├─────────────────────────────────────────────────────────┤
│  SQLite (WAL mode) + Auto-Scout Background Task          │
│  134 Suburbs × 15 Data Points + 40 Seed Properties      │
└─────────────────────────────────────────────────────────┘
```

---

## LLM STRATEGY — 3-TIER FALLBACK

Every agent extends `BaseAgent` which provides `ask_llm()`:

1. **Tier 1 — Ollama (FREE, LOCAL):** Calls `http://localhost:11434/api/chat` with model `llama3.2`, `stream: false`. Default.
2. **Tier 2 — Anthropic (PAID):** Uses `anthropic.AsyncAnthropic` with Claude. Only if Ollama fails AND API key is set.
3. **Tier 3 — No-AI Fallback:** Returns structured error JSON. Each agent has its own smart no-LLM fallback with rule-based logic so the app never breaks without AI.

---

## THE 13 AI AGENTS — COMPLETE SPECIFICATION

### Agent 1: SCOUT AGENT — The Property Hunter

**Purpose:** Scrape 100+ real estate agencies, detect shadow listings, distressed properties, and price drops across Victoria.

**System Prompt:** Extract structured property data from raw HTML. Output JSON with 20 fields: address, suburb, state, postcode, property_type, bedrooms, bathrooms, car_spaces, land_size_sqm, asking_price, price_guide_low, price_guide_high, listing_text, agent_name, agency_name, agent_phone, image_urls, distress_keywords, strata_levies_quarterly, council_rates_annual, zoning.

**Data:**
- `BOUTIQUE_AGENCIES` — 31 real estate agencies across all 8 AU states with name, URL, and CSS selector
- `COUNCIL_DA_PORTALS` — 4 council development application portals
- `DISTRESS_KEYWORDS` — 28 keywords: "must sell", "deceased estate", "mortgagee", "DA approved", "STCA", "vendor says sell", "price reduced", "below market", etc.

**Methods:**
- `execute(target_states, target_suburbs, use_browser, max_agencies)` → Batch scraping run
- `scrape_single_url(url, source, use_ai)` → Single URL scrape
- `_ai_extract(html, url, source)` → LLM-powered HTML→Property JSON extraction (temperature 0.1)
- No-LLM fallback: Rule-based `DataCleaner.clean_html_to_property()`

**KPIs:** Properties found/hour, distress detection accuracy, shadow listing discovery rate, data completeness, duplicate rate

---

### Agent 2: ANALYST AGENT — The Financial Brain

**Purpose:** Investment-grade property analysis with Bargain Score algorithm, ROI calculations, and AI-written market analysis.

**System Prompt:** Produce 8-section analysis: (1) Street-Level Price Positioning with CAGR, (2) Land-to-Asset Ratio, (3) Infrastructure Pipeline Impact, (4) Capital Growth Trajectory, (5) Cash-Flow Deep Dive with sensitivity analysis, (6) Risk Matrix, (7) Precise Entry Price Recommendation, (8) Final Verdict: DEAL / FAIR / TRAP with confidence score. Australian terminology enforced.

**Core Algorithms:**

**Bargain Score (0–100):** Weighted composite:
- Price Deviation Score (35%): How far below suburb median
- Cash Flow Score (25%): Based on net rental yield
- Distress Delta (20%): Distress signal intensity
- Market Timing Score (15%): Days on market + market growth
- DOM Bonus (5%) + Condition adjustment
- ≥85 = GOLDEN OPPORTUNITY, ≥65 = STRONG, ≥40 = FAIR

**Cash Flow Model — Differentiated Formulas:**
- `gross_rental_yield` = (annual_rent / purchase_price) × 100
- `net_yield` = (annual_rent − operating_expenses_excl_mortgage) / purchase_price × 100
- `cash_on_cash_return` = annual_net_income_after_mortgage / total_cash_invested × 100
- `roi` = (annual_net_income + purchase_price × capital_growth_rate) / total_cash_invested × 100
- `monthly_cash_flow` = annual_net_income / 12

**Offer Range Calculation:**
- Score ≥85 (Golden): 92–98% of median
- Score ≥65 (Strong): 85–95%
- Score ≥40 (Fair): 80–90%
- Below 40: 75–85%
- Additional -5% discount if distress signals detected

**Methods:**
- `execute(properties, suburb_profiles, sold_data, strategy, run_ai_analysis)` → Batch analysis
- `analyze_single(prop, suburb, sold_properties, strategy)` → Single property deep dive
- No-LLM fallback: All quantitative analysis works without AI; only narrative text is missing

---

### Agent 3: CLOSER AGENT — The Offer Writer

**Purpose:** Generate psychologically-tuned offer letters using Cialdini's 6 Principles of Persuasion.

**System Prompt:** Expert negotiation strategist. Uses: (1) Reciprocity, (2) Commitment/Consistency, (3) Social Proof, (4) Authority, (5) Liking, (6) Scarcity. 5 tone presets: EMPATHETIC, PROFESSIONAL, FAMILY_STORY, URGENT, INVESTOR_DIRECT. Australian legal terminology (Vendor, Contract of Sale, Section 32). Legal guardrail: outputs are "Commercial Strategy Draft" not legal advice.

**Output JSON:** cover_letter, negotiation_talking_points, counter_offer_strategy, recommended_offer_price, key_persuasion_hooks

**Standard AU Conditions auto-included:** Finance Approval, Building & Pest Inspection (14d), Strata Report (14d), Section 32/Contract Review (7d, not waivable)

**Methods:**
- `execute(request: OfferGenerationRequest)` → Full offer document with cover letter, conditions, negotiation strategy
- No-LLM fallback: Template-based offer with standard conditions and tone-matched cover letter

---

### Agent 4: PROFILER AGENT — The Investor Profiler

**Purpose:** Build investor profiles using APRA-level borrowing power calculations and progressive profiling through conversation.

**System Prompt:** Expert Australian property investment profiler. Extract: risk_tolerance, experience_level, primary_goal, cash_available, equity_available, annual_income, existing_debts, dependents, preferred_strategies, interested_in_development, interested_in_commercial, current_portfolio detail, target_portfolio, preferred_entities.

**APRA Borrowing Power Formula:**
- Assessment rate: actual rate + 3% buffer (e.g., 6.25% + 3% = 9.25%)
- HEM (Household Expenditure Measure) benchmark: max(actual_monthly_expenses, $3,500 + $500/dependent)
- Net Servicing Income: total_assessable_income/12 − HEM − existing_commitments − 3% of credit_card_limits
- Borrowing Power: PV of annuity over 30 years at assessment rate, capped at net servicing capacity

**Progressive Profiling:** Returns follow_up_questions based on what's missing. Experience levels: BEGINNER (0 properties), NOVICE (1-2), INTERMEDIATE (3-5), ADVANCED (6-9), EXPERT (10+).

**Methods:**
- `execute(user_input, existing_profile)` → Profile with readiness score, borrowing power, max purchase, follow-up questions
- No-LLM fallback: Regex-based income/budget extraction from free text

---

### Agent 5: STACKER AGENT — The Deal Structurer

**Purpose:** Structure deals with optimal entity selection, finance strategy, tax optimisation, BRRR analysis, and stress testing.

**System Prompt:** Expert Australian property deal structuring. Must consider: entity selection (Personal/Trust/SMSF/Company tradeoffs), finance strategy matching, depreciation schedules, negative gearing, BRRR refinance modelling, SMSF compliance (arm's length, single acquirable asset, LRBA), stress test at +2% rate rise.

**Entity Decision Tree:**
- PERSONAL: <3 properties, no asset protection needed
- FAMILY_TRUST: Asset protection + flexibility, multiple beneficiaries
- UNIT_TRUST: JV structures, specific unit allocation
- SMSF: Retirement-focused, strict compliance rules
- COMPANY: Commercial properties, 25% flat tax rate

**Finance Strategies:** STANDARD_IO, STANDARD_PI, BRRR, VENDOR_FINANCE, JOINT_VENTURE, SMSF_LRBA, DEPOSIT_BOND, EQUITY_RELEASE, WRAP, OPTION, SUBDIVISION_FINANCE, CONSTRUCTION

**BRRR Analysis:** Purchase → Renovate → Rent → Refinance at 80% of After Repair Value → Calculate forced equity and returned capital

**Methods:**
- `execute(deal, investment_profile)` → DealStructure with entity, strategy, projections, risks, tax benefits, action items
- No-LLM fallback: Rule-based entity/strategy selection + formulaic financial projections

---

### Agent 6: MENTOR AGENT — The Investment Coach

**Purpose:** Experience-adaptive property investment education with coaching, market commentary, and portfolio reviews.

**System Prompt:** Adaptive based on ExperienceLevel. BEGINNER: foundational, no jargon, step-by-step. INTERMEDIATE: strategic, assume basic knowledge. EXPERT: advanced strategies, market nuance, assume deep knowledge. Always: data-specific, Victorian market, actionable.

**7 Topic Types:**
1. `market_commentary` — Current VIC market trends, rate impacts, auction results
2. `strategy_education` — BTL, BRRR, HMO, subdivision, development strategies
3. `portfolio_review` — Portfolio health check, diversification, next acquisition
4. `suburb_deepdive` — Specific suburb analysis with growth drivers and risks
5. `deal_review` — Specific deal assessment with entry price guidance
6. `next_steps` — Personalised roadmap based on profile
7. `general_coaching` — Open-ended property investment questions

**Weekly Brief:** Generates market summary covering clearance rates, price movements, rate outlook, top opportunities.

**Methods:**
- `execute(question, topic, profile, market_data)` → Coaching response with follow-up suggestions
- `generate_brief(states, deals, profile)` → Weekly market intelligence brief
- No-LLM fallback: Topic-specific canned educational content

---

### Agent 7: QA AGENT — The Self-Governance Engine

**Purpose:** Quality assurance system that scores every agent's output, generates improvement skill templates, and auto-rolls back degraded agents.

**5-Dimension Scoring (weighted):**
- Accuracy (30%): Factual correctness of outputs
- Relevance (20%): How well output matches the request
- Completeness (20%): All required sections/fields present
- Timeliness (10%): Execution time within acceptable bounds
- Actionability (20%): Are outputs usable for decision-making?

**Skill Template System:** QA generates `SkillTemplate` objects with improved system prompts, few-shot examples, and parameters. Templates are versioned and track avg_score_before/after. Auto-rollback if score drops below threshold (default 60).

**Methods:**
- `execute(agent_outputs)` → Scores, health grid, skill gaps
- `health_check()` → System-wide agent health assessment
- `evaluate_and_improve()` → Full governance cycle: score all agents, identify gaps, generate skill templates
- No-LLM fallback: Heuristic scoring based on output completeness (field count, text length, has required sections)

---

### Agent 8: DUE DILIGENCE AGENT — The Document Analyst

**Purpose:** Analyse Section 32 vendor statements, contracts of sale, and strata reports for red flags.

**10 Red Flag Categories:** (1) Title Defects, (2) Planning Overlays, (3) Building Compliance, (4) Environmental Hazards, (5) Owner's Corporation Issues, (6) Financial Encumbrances, (7) Boundary/Easement, (8) Heritage Restrictions, (9) Disclosure Gaps, (10) Contractual Risks

**System Prompt:** Victorian property law expert. Analyse documents section-by-section. For each issue: category, severity (HIGH/MEDIUM/LOW), specific clause reference, plain-English explanation, recommended action. Must include overall risk rating (HIGH/MODERATE/LOW), deal-breaker flags, and estimated cost of identified issues.

**Methods:**
- `execute(document_text, document_type, specific_concerns)` → Risk assessment with categorised flags, severity ratings, action items
- No-LLM fallback: Keyword scanning for 10 red flag categories with pattern matching

---

### Agent 9: NEGOTIATION SHADOW — Live Coaching

**Purpose:** Real-time negotiation coaching with agent profiling and WhatsApp-style live guidance during conversations with real estate agents.

**System Prompt:** Expert negotiation coach. Build psychological profile of selling agent from their messages. Detect tactics: anchoring, false urgency, phantom offers, emotional manipulation. Provide real-time counter-strategies. Track commitment points and walk-away signals.

**Agent Sales Profile tracking:** name, agency, estimated_experience_years, detected_tactics, communication_style, pressure_level, honesty_signals, recommended_approach

**Methods:**
- `execute(buyer_message, agent_context, conversation_history, max_budget)` → Coaching response with talking points, detected tactics, emotional analysis, suggested responses
- No-LLM fallback: Tactic-detection via keyword matching + template coaching responses

---

### Agent 10: LIVE COMPS AGENT — Comparable Sales

**Purpose:** Find and analyse comparable sales to detect underquoting and establish true market value.

**CompsEngine:** In-memory comparable sales analysis. Matches by: suburb (exact > same postcode > neighbouring), property type, bedrooms (±1), price range (0.7x–1.3x), recency (within 6 months preferred).

**Underquoting Detection:** Flags when asking price is significantly below recent comparable sales median. Victorian underquoting laws reference.

**Methods:**
- `execute(property, sold_data, radius_km)` → Comparable sales with $/sqm analysis, median, underquoting flag
- `quick_check(property, all_properties)` → Fast in-memory comp check

---

### Agent 11: CONCIERGE AGENT — Deal Matching & Alerts

**Purpose:** Match deals to user preferences and manage multi-channel notifications (WhatsApp, SMS, Email, Push).

**Matching Logic:** Scores deals against UserPreferences: budget range, location match, property type match, bedroom count, yield threshold, bargain score minimum, strategy alignment. Deals above threshold get notifications.

**Spam Prevention:** Max notifications per day (configurable), quiet hours enforcement, no duplicate alerts for same property.

**Methods:**
- `execute(deals, user_preferences, notification_channel)` → Matched deals with match scores, notification payloads
- No-LLM fallback: Rule-based matching with threshold scoring

---

### Agent 12: PHOTO ENHANCER AGENT — Property Photo AI

**Purpose:** Enhance property listing photos for better presentation. 5 presets optimised for real estate.

**5 Presets:**
1. `real_estate_standard` — Balanced brightness, contrast, saturation for generic listings
2. `luxury_listing` — High contrast, warm tones, emphasised details
3. `renovation_before_after` — High clarity, revealing details for condition assessment
4. `exterior_hero` — Sky enhancement, green boost, wide-angle optimisation
5. `interior_bright` — Window pull, shadow lift, warm white balance

**Enhancement Pipeline:** Pillow (PIL) → optional Real-ESRGAN upscaling → optional ComfyUI inpainting

**Truthfulness Rule:** Enhancements must not misrepresent property condition. No object removal, no sky replacement, no virtual staging unless labelled.

**Methods:**
- `execute(image_path, preset, upscale)` → Enhanced image + quality metrics (brightness delta, contrast delta, sharpness delta)
- `analyze_quality(image_path)` → Quality score, recommended preset, individual metrics

---

### Agent 13: CHATBOT AGENT — Trending News & Market Chat

**Purpose:** Conversational AI that scrapes trending real estate news from 6 RSS feeds, scores articles for Victorian relevance, and engages users with market intelligence.

**6 RSS News Sources:**
1. Domain News — `https://www.domain.com.au/news/feed/`
2. Domain Melbourne — `https://www.domain.com.au/news/melbourne/feed/`
3. RealEstate.com.au Insights — `https://www.realestate.com.au/news/feed/`
4. CoreLogic Australia — `https://www.corelogic.com.au/news-research/feed`
5. AFR Property — `https://www.afr.com/property/rss`
6. SQM Research — `https://sqmresearch.com.au/feed`

**VIC Relevance Scoring:** 30+ keywords (melbourne, victoria, vic, geelong, bendigo, ballarat, auction, clearance rate, stamp duty, land tax, etc.) → relevance score 0.0–1.0. Articles sorted by relevance.

**News Cache:** 50 articles max, 30-minute TTL, de-duplication by normalised title.

**Conversation Memory:** Per-session, 20-message sliding window, FIFO eviction.

**No-LLM Fallback:** Smart keyword-based responses. If message contains "news/headline/latest" → format top 3 articles. If "suburb/area/region" → match to VIC locations data. If "strategy/invest/yield" → return educational strategy snippets. Otherwise → general helpful response.

**Methods:**
- `execute(user_message, session_id, include_news)` → AI response + trending articles
- `get_trending_news(limit)` → Top articles by VIC relevance
- `get_news_summary()` → AI-written market intelligence brief
- `clear_session(session_id)` → Reset conversation

---

## ORCHESTRATOR — Pipeline Engine

**Pipeline Sequence:** Profiler → Scout → Analyst → LiveComps → Stacker → Closer → Concierge → Mentor → QA

**Fail-Forward Logic:** If any agent fails, pipeline continues with remaining agents. Failed agent's output is logged but doesn't block the chain.

**QA Mandatory:** Every pipeline run ends with QA scoring all agent outputs.

---

## 6 TOOLS

### 1. BargainScorer
Calculates the 0–100 Bargain Score using the weighted formula described above. Input: asking_price, suburb_median, net_yield, distress_score, days_on_market, condition_factor, market_growth. Output: BargainScore with overall, sub-scores, is_golden, summary.

### 2. CompsEngine
In-memory comparable sales engine. Matches properties by suburb → postcode → property_type → bedrooms → price_range → recency. Outputs: median_comp_price, $/sqm, comp_count, underquoting_flag.

### 3. ROICalculator
Full cash flow modelling. Inputs: purchase_price, weekly_rent, stamp_duty_state, interest_rate, LVR, expenses. Outputs: CashFlowModel with 12+ computed financial metrics.

### 4. DataCleaner
Rule-based HTML→Property extraction without AI. Regex patterns for Australian property listings: price extraction ($X,XXX,XXX or $X.XXM), bedroom/bathroom/car pattern (e.g., "3 bed 2 bath 1 car"), address patterns, distress keyword scanning.

### 5. OfferWriter
Template-based offer document generation. 5 tone-matched cover letter templates. Standard Australian conditions (Finance, B&P, Strata, Section 32). Legal disclaimer auto-attached.

### 6. Scraper
Dual-mode web scraper: (1) httpx async HTTP client for static pages, (2) Playwright browser automation for JavaScript-rendered pages. Configurable user agent, timeout, retry logic.

---

## DATA MODELS — COMPLETE SCHEMA

### Property Model
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Auto-generated |
| address | string | min 5 chars |
| suburb | string | |
| state | string | |
| postcode | string | 4-digit AU postcode |
| latitude, longitude | float? | |
| property_type | enum | HOUSE, UNIT, APARTMENT, TOWNHOUSE, VILLA, LAND, RURAL, FARM, ACREAGE, COMMERCIAL, INDUSTRIAL, RETAIL, WAREHOUSE, DUPLEX, GRANNY_FLAT, OTHER |
| bedrooms, bathrooms, car_spaces | int? | |
| land_size_sqm, building_size_sqm | float? | |
| year_built | int? | 1800–2030 |
| condition | enum | EXCELLENT, GOOD, FAIR, RENOVATION_REQUIRED, KNOCKDOWN_REBUILD, UNKNOWN |
| asking_price, price_guide_low/high, sold_price | float? | |
| listing_status | enum | ACTIVE, UNDER_OFFER, SOLD, WITHDRAWN, PRE_MARKET, OFF_MARKET, AUCTION |
| source | enum | REA, DOMAIN, BOUTIQUE_AGENCY, COUNCIL_DA, PUBLIC_NOTICE, SOCIAL_MEDIA, COMING_SOON, OFF_MARKET, AUCTION_RESULT, MANUAL |
| source_url, listing_text, agent_name, agent_phone, agency_name | string? | |
| strata_levies_quarterly, council_rates_annual, water_rates_annual | float? | AU-specific |
| zoning | string? | |
| flood_zone, bushfire_zone, heritage_listed | bool? | |
| estimated_weekly_rent, current_weekly_rent | float? | |
| vacancy_rate_pct | float? | 0–100 |
| distress_signals | DistressSignal[] | keyword, confidence (0–1), source |
| image_urls | string[] | |
| tags | string[] | |
| **Computed:** has_distress_signals, distress_score (0–100), effective_price, annual_holding_costs | | |

### Deal Model
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | |
| property | Property | Embedded |
| suburb_median_price | float | |
| deal_type | enum | BTL, R2SA, FLIP, BRRR, HMO, PLO, SUBDIVISION, DEVELOPMENT, LAND_BANK, OWNER_OCCUPIER |
| recommended_strategies | DealType[] | |
| cash_flow | CashFlowModel | 20+ financial fields, 12 computed metrics |
| bargain_score | BargainScore | 5 sub-scores + overall + is_golden + summary |
| ai_analysis | string | LLM-written market analysis |
| comparable_sales_summary | string | |
| recommended_offer_price, offer_range_low/high | float? | |
| estimated_refurb_cost, after_repair_value | float | |
| flip_profit, brrr_equity_gain | float | |
| **Computed:** is_golden_opportunity, price_per_sqm, land_to_asset_ratio, payback_period_months, bmv_pct, uplift_value_pct, headline | | |

### Offer Document Model
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | |
| property_id, property_address | | |
| buyer_name, buyer_entity | string | |
| offer_price, deposit_amount | float | |
| settlement_days | int | 14–180, default 42 |
| seller_motivation | enum | DESPERATE, MOTIVATED, NEUTRAL, ASPIRATIONAL, UNKNOWN |
| offer_tone | enum | EMPATHETIC, PROFESSIONAL, URGENT, FAMILY_STORY, INVESTOR_DIRECT |
| conditions | OfferCondition[] | name, description, days, is_waivable |
| cover_letter | string | AI-generated |
| negotiation_talking_points | string[] | |
| counter_offer_strategy | string | |
| walk_away_price | float? | |
| legal_disclaimer | string | Hardcoded AU disclaimer |

### Investment Profile Model
| Field | Type | Notes |
|-------|------|-------|
| risk_tolerance | enum | CONSERVATIVE, MODERATE, GROWTH, AGGRESSIVE, SPECULATIVE |
| experience_level | enum | BEGINNER, NOVICE, INTERMEDIATE, ADVANCED, EXPERT |
| primary_goal | enum | CASH_FLOW, CAPITAL_GROWTH, BALANCED, TAX_MINIMISATION, RETIREMENT, WEALTH_CREATION, FIRST_HOME, SUBDIVISION, PASSIVE_INCOME |
| preferred_entity | enum | PERSONAL, JOINT, FAMILY_TRUST, UNIT_TRUST, HYBRID_TRUST, SMSF, COMPANY, BARE_TRUST, PARTNERSHIP |
| financial.income_sources | IncomeSource[] | source_type, gross_annual, shading_pct |
| financial.existing_liabilities | ExistingLiability[] | type, balance, monthly_repayment, interest_rate |
| financial.cash_available, equity_available, smsf_balance | float | |
| financial.dependents, monthly_living_expenses, credit_card_limits | | |
| current_portfolio_count/value/debt | | |
| target_portfolio_count/value, target_annual_passive_income | | |
| preferred_strategies | FinanceStrategy[] | 12 strategy types |
| **Computed:** estimated_borrowing_power (APRA formula), max_next_purchase, portfolio_equity/lvr | | |

### Deal Structure Model
| Field | Type | Notes |
|-------|------|-------|
| strategy | FinanceStrategy | STANDARD_IO, BRRR, SMSF_LRBA, etc. |
| entity_type | EntityType | |
| purchase_price, deposit, loan_amount, lvr, interest_rate | float | |
| stamp_duty, legal_costs, renovation_budget | float | |
| projected yields, cashflow, 5yr growth, depreciation, tax_benefit | float | |
| risk_rating, risk_factors, mitigation_strategies | | |
| smsf_compliant, smsf_lrba_required | bool | |
| after_repair_value, forced_equity_gain | float | BRRR |
| pros, cons, action_items | string[] | |

### Subscription Model
| Tier | Price | Analyses/mo | Views/day | Features |
|------|-------|-------------|-----------|----------|
| EXPLORER | Free | 3 | 5 | Basic scoring |
| INVESTOR | $199/mo | 50 | Unlimited | Shadow listings, First Look, WhatsApp, offers |
| PRO_SOURCER | $499/mo | Unlimited | Unlimited | + Bulk pipeline, API, multi-state |
| THE_CLOSER | $2,500/deal | Unlimited | Unlimited | + Dedicated analyst, custom strategy |
| **Add-ons:** | DD Bot $99/report | Negotiation Shadow $500/mo | First Look $49/mo | |

### Suburb Profile Model
15 data points per suburb: name, postcode, median_house, median_unit, growth, house_yield, unit_yield, population, auction_clearance_rate, avg_days_on_market, vacancy_rate, walkability_score, council, gentrification_status (emerging/established/mature/premium), infrastructure_notes.

---

## LOCATION DATABASE — 15 VIC REGIONS, 134 SUBURBS

### Region Map
| # | Region | Suburbs | Median Range |
|---|--------|---------|--------------|
| 1 | Melbourne — CBD & Inner City | Melbourne CBD, Southbank, Docklands, Carlton, North Melbourne, West Melbourne, Parkville | $880K–$2.5M |
| 2 | Melbourne — Inner North | Fitzroy, Collingwood, Abbotsford, Northcote, Thornbury, Preston, Brunswick, Coburg, Pascoe Vale | $950K–$1.45M |
| 3 | Melbourne — Inner East | Richmond, Hawthorn, Kew, Camberwell, Canterbury, Balwyn, Surrey Hills, Box Hill | $1.25M–$3.2M |
| 4 | Melbourne — Inner South | South Yarra, Prahran, St Kilda, Windsor, Albert Park, South Melbourne, Port Melbourne, Elwood | $980K–$2.2M |
| 5 | Melbourne — Inner West | Footscray, Seddon, Yarraville, Williamstown, Newport, Kingsville, Maidstone, Maribyrnong | $780K–$1.35M |
| 6 | Melbourne — Western Growth | Werribee, Hoppers Crossing, Point Cook, Tarneit, Truganina, Melton, Caroline Springs, Sunshine, St Albans | $480K–$750K |
| 7 | Melbourne — Northern Growth | Craigieburn, Broadmeadows, Epping, South Morang, Doreen, Mernda, Mill Park, Thomastown, Lalor | $460K–$680K |
| 8 | Melbourne — Eastern Suburbs | Doncaster, Ringwood, Croydon, Lilydale, Mitcham, Nunawading, Blackburn, Bayswater, Boronia | $680K–$1.35M |
| 9 | Melbourne — South Eastern | Dandenong, Noble Park, Springvale, Cranbourne, Berwick, Narre Warren, Pakenham, Officer, Clyde | $520K–$850K |
| 10 | Melbourne — Bayside & Peninsula | Brighton, Hampton, Cheltenham, Mentone, Frankston, Mornington, Sorrento, Dromana, Rosebud | $680K–$3M |
| 11 | Geelong & Surf Coast | Geelong, Newtown, Belmont, Corio, Norlane, Lara, Ocean Grove, Torquay, Armstrong Creek | $420K–$1.1M |
| 12 | Bendigo & Goldfields | Bendigo, Quarry Hill, Epsom, Kangaroo Flat, Strathdale, Golden Square, Eaglehawk, Castlemaine | $380K–$780K |
| 13 | Ballarat & Central Highlands | Ballarat, Sebastopol, Wendouree, Alfredton, Buninyong, Delacombe, Brown Hill | $390K–$680K |
| 14 | Gippsland | Traralgon, Morwell, Sale, Warragul, Drouin, Bairnsdale, Wonthaggi | $280K–$680K |
| 15 | Hume & North East VIC | Shepparton, Wodonga, Wangaratta, Benalla, Seymour, Mildura, Swan Hill | $320K–$460K |

---

## 40 SEED PROPERTIES — VALUE-ADD INTELLIGENCE

Pre-loaded with 40 realistic Victorian properties featuring:
- Diverse property types: houses, apartments, townhouses, units, commercial, land, rural
- Price range: $320K (Moe industrial) to $2.2M (Brighton house)
- Every property has: address, suburb, state (VIC), postcode, property_type, bedrooms, bathrooms, car_spaces, land_size, building_size, year_built, asking_price, estimated_weekly_rent, listing_text (realistic marketing copy with value-add intelligence), source_url (real Domain.com.au or realestate.com.au search links), distress_signals where applicable, council_rates, water_rates, strata_levies
- Distress keywords embedded naturally in listing text where applicable
- Real infrastructure references (Metro Tunnel, West Gate Tunnel, Level Crossing Removals, etc.)

---

## API — COMPLETE ENDPOINT SPECIFICATION

### Infrastructure
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | App info + docs link |
| `/health` | GET | System health: uptime, DB stats, service status, auto-scout history |
| `/api/v1/config` | GET | Scoring thresholds + market defaults |
| `/terminal` | GET | Bloomberg Terminal dashboard (main UI) |
| `/landing` | GET | Marketing landing page |

### Properties — `/api/v1/properties`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | List/filter properties (suburb, state, type, price range, bedrooms, distress_only, source, sort, pagination) |
| `/{id}` | GET | Single property |
| `/{id}` | DELETE | Dismiss/archive property |
| `/search` | POST | Advanced multi-filter search (suburbs[], postcodes[], property_types[], min_bargain_score, etc.) |
| `/scout` | POST | Trigger Scout Agent (states, suburbs, max_agencies, use_browser) |
| `/quick-scout` | POST | On-demand suburb scout with fuzzy matching (generates 1–10 synthetic properties) |
| `/locations/tree` | GET | Full VIC location hierarchy: state → region → suburbs |
| `/locations/regions` | GET | Regions for a state |
| `/locations/search` | GET | Fuzzy suburb search by name/postcode (max 20 results) |
| `/locations/stats` | GET | Location database summary + property counts |

### Deals — `/api/v1/deals`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | List all deals with sorting (bargain_score, roi, cash_flow, price) |
| `/{id}` | GET | Single deal |
| `/bulk-analyze` | POST | Trigger Analyst Agent on all unanalysed properties |
| `/quick-roi` | GET | Quick ROI calculation (price, rent, state → yields, cash flow, stamp duty) |
| `/value-add` | POST | Value-add analysis for a property |

### Offers — `/api/v1/offers`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | List all offers |
| `/` | POST | Generate offer via Closer Agent (deal_id, buyer_name, entity, budget, tone, story) |

### Profiler — `/api/v1/profiler`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/build` | POST | Build/update investor profile from free-text input |

### Stacker — `/api/v1/stacker`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/structure` | POST | Structure a deal (deal_id, profile_id) → DealStructure |

### Mentor — `/api/v1/mentor`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask mentor a question (question, topic, profile_id) |
| `/brief` | POST | Generate weekly market brief (states[]) |

### Due Diligence — `/api/v1/due-diligence`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyse document (text, document_type, concerns) → risk assessment |

### Negotiation — `/api/v1/negotiation`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/coach` | POST | Real-time coaching (buyer_message, agent_name, agency, max_budget, history) |

### QA — `/api/v1/qa`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Agent health check with per-agent scores |
| `/evaluate-and-improve` | POST | Full governance cycle → scores + skill templates |

### Photos — `/api/v1/photos`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enhance-upload` | POST | Upload + enhance photo (multipart: file, preset, upscale) |
| `/analyze` | POST | Analyse photo quality (multipart: file) |

### Chatbot — `/api/v1/chat`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | POST | Send chat message (message, session_id, include_news) → response + trending |
| `/trending` | GET | Get trending VIC property news articles (limit) |
| `/summary` | GET | AI-generated market intelligence brief |
| `/{session_id}` | DELETE | Clear chat conversation |

### Subscriptions — `/api/v1/subscriptions`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tiers` | GET | List all subscription tiers with pricing and features |
| `/check` | POST | Check feature access for a subscription |

### Recommendations — `/api/v1/recommendations`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Get top deal recommendations (limit, strategy filter) |

### Webhooks — `/api/v1/webhooks`
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stripe` | POST | Stripe payment webhook handler |

---

## FRONTEND UX — PIXEL-PERFECT SPECIFICATION

> **Reproduce this section exactly to recreate the dashboard in any no-code tool.**
> Every color hex, font weight, spacing value, animation, interaction, and state transition is documented below.

---

### 1. GLOBAL DESIGN SYSTEM

#### Color Palette (exact hex values)
| Token | Hex | Usage |
|-------|-----|-------|
| `terminal-bg` | `#0a0e17` | Page background, input backgrounds, nested panels |
| `terminal-panel` | `#111827` | Card backgrounds, header, footer, tab bar |
| `terminal-border` | `#1f2937` | All borders, dividers, separator lines |
| `terminal-accent` | `#00d4aa` | Primary action buttons, active tab underlines, links, positive highlights |
| `terminal-gold` | `#fbbf24` | Golden opportunity badges, pulsing borders, premium labels |
| `terminal-warn` | `#f59e0b` | Warning states, Due Diligence highlights, amber badges |
| `terminal-danger` | `#ef4444` | Errors, distress signals, negative cash flow, toast errors |
| `terminal-info` | `#3b82f6` | Information badges, negotiation agent profile header |
| `terminal-green` | `#10b981` | Positive values, live dot, BMV badges, scout/API status |
| `terminal-red` | `#ef4444` | Negative values, health bars below 60, error states |
| `terminal-purple` | `#a855f7` | Profiler section, mentor section accents |
| `terminal-bright` | `#ffffff` | Headers, bold numeric values, property names |
| `terminal-text` | `#e5e7eb` | Default body text |
| `terminal-dim` | `#9ca3af` | Secondary text, specs, labels |
| `terminal-muted` | `#6b7280` | Tertiary text, column headers, timestamps |

#### Typography
| Role | Font | Weight | Size |
|------|------|--------|------|
| Headings & labels | Inter | 600–800 | 14–16px |
| Body text | Inter | 400 | 12–14px |
| Monospace data | JetBrains Mono | 400–700 | 9–14px |
| KPI numbers | JetBrains Mono | 700 | 16px (base size in KPI strip) |
| Ticker tape | JetBrains Mono | 400 | 11px |
| Metric pills | JetBrains Mono | 400 | 9px |
| Micro-labels | Inter or JetBrains Mono | 400–600 | 8–10px, uppercase, letter-spacing: 0.5px+ |

Font imports:
```
https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap
```

#### Spacing & Layout Rules
- Page: `min-h-screen`, flex column, no horizontal scroll
- Main content: `padding: 12px` (p-3), `overflow-y: auto`, flex-1
- Card padding: `12px` (p-3) for deal cards, `16px` (p-4) for panel sections
- Card border-radius: `rounded` (4px default Tailwind)
- Grid gaps: `8px` (gap-2) for deal cards, `12px` (gap-3) for panel grids
- Input fields: `bg-terminal-bg`, `border border-terminal-border`, `rounded`, `px-2 py-1` or `px-3 py-1.5`, `text-xs font-mono text-terminal-text`
- All inputs use monospace font, dark background, subtle border

#### Scrollbar Styling
```css
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0e17; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }
```

---

### 2. CSS ANIMATIONS (5 keyframe animations)

#### 2a. Ticker Tape Scroll
```css
@keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
.ticker-content { display: inline-block; animation: ticker 60s linear infinite; }
```
Continuous horizontal scroll, 60-second loop, linear timing.

#### 2b. Live Dot Blink
```css
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
```
Small green circle, fades to 30% opacity and back every 2 seconds. Used in header and chatbot panel.

#### 2c. Terminal Cursor Blink
```css
.cursor-blink::after { content: '█'; animation: cursorBlink 1s step-end infinite; color: #00d4aa; }
@keyframes cursorBlink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
```
Teal block cursor that toggles on/off every 0.5s. Used in empty-state "AWAITING DATA" text.

#### 2d. Golden Opportunity Pulse
```css
.golden-pulse { animation: goldPulse 2s infinite; }
@keyframes goldPulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.3); } 70% { box-shadow: 0 0 0 6px rgba(251, 191, 36, 0); } }
```
Applied to deal cards with Bargain Score ≥ 85. Gold box-shadow ring that expands outward and fades, repeating every 2 seconds. This is the signature "golden deal" visual cue.

#### 2e. Fade-In Entry
```css
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
```
Applied to: deal cards when rendered, toast notifications, modals on open, chat messages. Quick 200ms slide-up + fade.

---

### 3. PAGE LAYOUT — TOP TO BOTTOM (exact structure)

The page is a vertical flex column (`flex flex-col min-h-screen`). All sections are `flex-shrink-0` except the main content area which is `flex-1 overflow-y-auto`.

#### 3a. TOP BAR (Header)
- **Container:** `bg-terminal-panel`, bottom border `border-terminal-border`, horizontal padding 16px, vertical padding 6px, flex row, items centered, justify space-between
- **Left cluster:**
  - **Logo badge:** 24×24px square, `bg-terminal-accent`, rounded, contains "PIM" text in `text-terminal-bg font-bold text-xs`, centered
  - **Title:** "PROPERTY INSIGHTS" — `font-semibold text-sm text-terminal-bright tracking-tight`
  - **Region badge:** "MELBOURNE + VIC" — `text-[10px] text-terminal-accent font-mono bg-terminal-accent/10 px-1.5 py-0.5 rounded`
  - **Separator:** `|` character in `text-terminal-muted text-xs`
  - **Clock:** `--:--:-- AEST` — `text-terminal-dim text-xs font-mono`, updates every 1 second with `Australia/Sydney` timezone
  - **Live dot:** 8px green circle with blink animation, margin-left 8px
  - **"LIVE" text:** `text-terminal-green text-[10px] font-mono`
- **Right cluster — 5 action buttons in a row:**
  1. **▶ SCOUT:** `bg-terminal-accent/10 hover:bg-terminal-accent/20 text-terminal-accent`, border `border-terminal-accent/30`, opens Location Scout modal
  2. **ROI:** `bg-terminal-panel hover:bg-terminal-border text-terminal-dim`, border `border-terminal-border`, opens Quick ROI modal
  3. **MENTOR:** `bg-terminal-purple/10 hover:bg-terminal-purple/20 text-terminal-purple`, border `border-terminal-purple/30`, switches to Mentor tab
  4. **QA:** `bg-terminal-info/10 hover:bg-terminal-info/20 text-terminal-info`, border `border-terminal-info/30`, switches to QA tab
  5. **User avatar:** 28×28px circle (`rounded-full`), `bg-terminal-border`, contains "U" in `text-xs font-bold text-terminal-accent`, clickable → switches to Profiler tab

All buttons: `px-3 py-1 rounded text-xs font-mono font-medium transition`

#### 3b. TICKER TAPE
- **Container:** `bg-terminal-bg`, bottom border, vertical padding 2px, `overflow: hidden`, `white-space: nowrap`
- **Content:** Single inline-block div that scrolls from right to left (60s linear infinite animation)
- **Data points** (separated by `│` characters in `text-terminal-border`):

| Label | Value Color | Example |
|-------|------------|---------|
| MEL INNER | dim→green | $1.28M ▲2.3% |
| MEL WEST | dim→green | $720K ▲4.5% |
| MEL NORTH | dim→green | $680K ▲3.8% |
| MEL SE | dim→green | $650K ▲4.2% |
| GEELONG | dim→green | $690K ▲4.2% |
| BENDIGO | dim→green | $530K ▲4.0% |
| BALLARAT | dim→green | $490K ▲4.5% |
| RBA RATE | dim→warn | 4.35% |
| MEL AUCTION CLR | dim→green | 68.2% |
| MEL VACANCY | dim→green | 1.1% ▼ |
| SHADOW LISTINGS | dim→accent | (dynamic count) |
| GOLDEN OPPS | dim→gold | (dynamic count) |
| AUTO-SCOUT | dim→green | ACTIVE or q15m/q30m |
| DB | dim→green | SQLite {size}KB |
| QA HEALTH | dim→green/warn/red | HEALTHY / FAIR / DEGRADED |

Labels in `text-terminal-dim`, values in their respective colors. All `font-mono text-[11px]`, horizontal spacing `space-x-8` between sections.

Dynamic IDs: `ticker-shadow`, `ticker-golden`, `ticker-scout`, `ticker-db`, `ticker-qa` — populated on page load from API.

#### 3c. KPI STRIP
- **Container:** CSS Grid, 8 equal columns (`grid-cols-8`), bottom border
- **Each cell:** `data-cell` class — right border + bottom border `1px solid #1f2937`, `px-2 py-1.5`, `text-center`
- Last cell has no right border

| Column | Label (9px, muted, uppercase, tracking-wider) | Value ID | Default | Value Style |
|--------|-------|----------|---------|-------------|
| 1 | PROPERTIES | `stat-properties` | 0 | `text-base font-mono font-bold text-terminal-bright` |
| 2 | ANALYSED | `stat-deals` | 0 | Same |
| 3 | GOLDEN | `stat-golden` | 0 | `text-base font-mono font-bold text-terminal-gold` (label also gold & font-semibold) |
| 4 | AVG SCORE | `stat-avg-score` | — | `text-base font-mono font-bold text-terminal-accent` |
| 5 | AVG $/M² | `stat-avg-sqm` | — | `text-base font-mono font-bold text-terminal-bright` |
| 6 | OFFERS | `stat-offers` | 0 | `text-base font-mono font-bold text-terminal-bright` |
| 7 | PROFILE | `stat-profile` | — | `text-base font-mono font-bold text-terminal-purple` |
| 8 | PIPELINE | `stat-pipeline` | IDLE | `text-base font-mono font-bold text-terminal-green` (changes to warn during run, red on error) |

#### 3d. TAB BAR
- **Container:** flex row, bottom border, `bg-terminal-panel/50`, overflow-x auto (horizontal scroll on small screens)
- **10 tab buttons**, each: `px-3 py-2 text-xs font-mono font-medium tracking-wide whitespace-nowrap`
- **Active state:** `tab-active` class → `color: #00d4aa; border-bottom: 2px solid #00d4aa;`
- **Inactive state:** `text-terminal-muted`, on hover → `hover:text-terminal-text`
- **Tab labels & their onclick targets:**

| # | Label | Tab ID | Panel ID |
|---|-------|--------|----------|
| 1 | DEALS | `tab-deals` | `panel-deals` |
| 2 | PROPERTIES | `tab-properties` | `panel-properties` |
| 3 | OFFERS | `tab-offers` | `panel-offers` |
| 4 | PIPELINE | `tab-pipeline` | `panel-pipeline` |
| 5 | 👤 PROFILER | `tab-profiler` | `panel-profiler` |
| 6 | 🎓 MENTOR | `tab-mentor` | `panel-mentor` |
| 7 | DD BOT | `tab-diligence` | `panel-diligence` |
| 8 | NEGOTIATION | `tab-negotiate` | `panel-negotiate` |
| 9 | 🔬 QA ENGINE | `tab-qa` | `panel-qa` |
| 10 | 📸 PHOTOS | `tab-photos` | `panel-photos` |

**Tab switching logic:** `switchTab(name)` iterates all 10 tab IDs, hides all panels except the target, applies `tab-active` class to the matching tab, sets `text-terminal-muted` on all others.

**Default active tab on load:** DEALS

---

### 4. TAB PANELS — DETAILED UX PER SCREEN

#### 4a. DEALS PANEL (default visible)

**Filter Bar** — flex row, flex-wrap with vertical gap, margin-bottom 12px:
1. **Region dropdown:** `<select>`, max-width 240px, default "ALL VIC REGIONS". Dynamically populated with 15 VIC region names from `/properties/locations/tree` API. On change → `filterDeals()`.
2. **Suburb search input:** `<input type="text">`, placeholder "SEARCH SUBURB...", width 144px (w-36), on input → `filterDeals()`. Matches suburb name, address, and postcode.
3. **Strategy dropdown:** Options: ALL STRATEGIES, BTL, R2SA, FLIP, BRRR, HMO, PLO, SUBDIVISION, DEVELOPMENT, LAND BANK.
4. **Sort dropdown:** Options: BARGAIN SCORE (default, desc), RETURN ON INVESTMENT (desc), CASH FLOW (desc), PRICE (asc), PRICE PER m² (asc), PAYBACK MONTHS (asc), BELOW MARKET VALUE % (desc).
5. **Golden-only checkbox:** Gold label "GOLDEN ONLY", accent-gold checkbox. Filters to `is_golden_opportunity === true`.
6. **BMV-only checkbox:** Green label "BMV ONLY", accent-green checkbox. Filters to `bmv_pct > 0`.
7. **Spacer** (flex-1)
8. **Result count badge:** `text-[10px] font-mono text-terminal-muted`, shows "{N} DEALS".
9. **Quick Scout cluster:** Text input (placeholder "SCOUT SUBURB...", w-36, Enter key triggers) + "SCOUT" button (`bg-terminal-green/10 text-terminal-green border-terminal-green/30`). On click: POST `/properties/quick-scout` with fuzzy suburb name → generates 1-10 synthetic properties, shows toast with matched suburb name, auto-fills suburb filter.
10. **BULK ANALYSE button:** `bg-terminal-accent/10 text-terminal-accent border-terminal-accent/30`. POST `/deals/bulk-analyze` → analyses all unanalysed properties.

**Empty State:** Centered vertically in grid area — "NO ACTIVE DEALS" in `font-mono text-sm`, "Run SCOUT to harvest properties, then analyse." in `text-xs`, plus "AWAITING DATA" with terminal cursor blink animation.

**Deal Card Grid:** `grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-2`

**Individual Deal Card Anatomy (top to bottom):**

```
┌─────────────────────────────────────────┐
│ ┌─────────────────────────────────────┐ │
│ │   PROPERTY TYPE GRADIENT BLOCK      │ │ ← 112px tall (h-28), full-width
│ │   🏠  (3xl emoji centered)          │ │    bg: inline CSS linear-gradient
│ │   HOUSE — BRUNSWICK (9px mono)      │ │    bottom: type label + suburb
│ └─────────────────────────────────────┘ │
│                                         │
│  Brunswick, VIC          ┌─── 72 ───┐  │ ← suburb + state (xs, bright) │ score (sm, mono, bold)
│  123 Smith St            │  BARGAIN  │  │ ← address (10px, dim)        │ "BARGAIN SCORE" (8px)
│                          │  SCORE    │  │
│                          └───────────┘  │
│  $650,000  [BTL]  [BMV 12%]  🏆 GOLDEN │ ← price (sm, mono, bold) + badges
│                                         │
│  3BR 2BA 1🚗  HOUSE  450m²  $520/wk    │ ← specs line (10px, dim, mono)
│                                         │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌────┐ │ ← metric pills (flex-wrap)
│  │GY 5.2│ │NY 3.8% │ │CF $280 │ │CoC │ │    each: bg-terminal-border,
│  └──────┘ └────────┘ └────────┘ └────┘ │    border #374151, rounded-sm
│  ┌────────┐ ┌──────┐ ┌───────────────┐ │    9px mono text
│  │ROI 8.4%│ │$4,200│ │Payback 84 mo  │ │
│  └────────┘ └──────┘ └───────────────┘ │
│                                         │
│  ⚠⚠ 2 distress signals                 │ ← red, 9px, only if signals exist
│                         [OFFER][DETAILS]│ ← 2 buttons, 9px mono
└─────────────────────────────────────────┘
```

**Card styling:**
- Container: `bg-terminal-panel rounded border p-3 animate-fade-in cursor-pointer hover:bg-terminal-border/30 transition`
- Golden cards: `border-terminal-gold golden-pulse` (gold border + pulsing glow)
- Normal cards: `border-terminal-border`
- Entire card is clickable → opens Deal Detail modal

**Property Type Gradient Placeholders** — Not stock photos. CSS gradient backgrounds with emoji icon, per type:

| Type | Gradient (inline CSS) | Emoji |
|------|----------------------|-------|
| house | `linear-gradient(135deg, #1e3a5f 0%, #152238 100%)` | 🏠 |
| apartment | `linear-gradient(135deg, #3b1f6e 0%, #251545 100%)` | 🏢 |
| unit | `linear-gradient(135deg, #2e2b6e 0%, #1c1945 100%)` | 🏢 |
| townhouse | `linear-gradient(135deg, #134e4a 0%, #0f302e 100%)` | 🏘 |
| villa | `linear-gradient(135deg, #065f46 0%, #053d2e 100%)` | 🏡 |
| land | `linear-gradient(135deg, #14532d 0%, #0a3018 100%)` | 🌳 |
| commercial | `linear-gradient(135deg, #7c2d12 0%, #4a1a0a 100%)` | 🏗 |
| industrial | `linear-gradient(135deg, #374151 0%, #1f2937 100%)` | 🏭 |
| warehouse | `linear-gradient(135deg, #334155 0%, #1e293b 100%)` | 📦 |
| retail | `linear-gradient(135deg, #78350f 0%, #451e08 100%)` | 🏪 |
| duplex | `linear-gradient(135deg, #155e75 0%, #0e3a4a 100%)` | 🏠 |
| farm | `linear-gradient(135deg, #3f6212 0%, #263a0b 100%)` | 🌾 |
| rural | `linear-gradient(135deg, #14532d 0%, #0a3018 100%)` | 🌿 |
| acreage | `linear-gradient(135deg, #065f46 0%, #053d2e 100%)` | 🌳 |

Large size (deal cards): `h-28` (112px tall), `rounded`, `border border-terminal-border/30`, centered flex-col: 3xl emoji + 9px type/suburb label below.
Small size (property list): `48×48px`, `rounded`, `flex-shrink-0`, centered emoji `text-lg`.

**Bargain Score color thresholds:**
- ≥ 85: `text-terminal-gold` (golden)
- ≥ 65: `text-terminal-green` (strong)
- ≥ 40: `text-terminal-warn` (fair)
- < 40: `text-terminal-red` (weak)

**Strategy Badge CSS classes:**
| Strategy | Class | Background | Text |
|----------|-------|-----------|------|
| BTL | `strat-btl` | `#065f46` | `#6ee7b7` |
| R2SA | `strat-r2sa` | `#713f12` | `#fde68a` |
| FLIP | `strat-flip` | `#581c87` | `#d8b4fe` |
| BRRR | `strat-brrr` | `#7c2d12` | `#fdba74` |
| HMO | `strat-hmo` | `#1e3a5f` | `#93c5fd` |
| PLO | `strat-plo` | `#3f3f46` | `#d4d4d8` |
| SUBDIVISION | `strat-subdivision` | `#44403c` | `#e7e5e4` |
| DEVELOPMENT | `strat-development` | `#1c1917` | `#a8a29e` |
| LAND_BANK | `strat-land_bank` | `#365314` | `#bef264` |

Badge style: `display: inline-flex; align-items: center; padding: 1px 6px; border-radius: 3px; font-size: 9px; font-weight: 600; letter-spacing: 0.5px;`

**BMV Badge:** `background: #10b981; color: #000; font-weight: 700; padding: 1px 5px; border-radius: 3px; font-size: 9px;` — shows "BMV {pct}%"

**Metric Pill:** `background: #1f2937; border: 1px solid #374151; border-radius: 4px; padding: 2px 6px; font-size: 9px;` — full text labels like "Gross Yield 5.2%", "Cash Flow $280/mo", "Return on Investment 8.4%"
- Cash flow pill: green text if positive, red if negative
- Up to 7 pills per card: Gross Yield, Net Yield, Cash Flow/mo, Cash-on-Cash, ROI, $/m², Payback months
- Optional Flip Profit pill in purple if applicable

**Card Buttons (bottom right):**
- OFFER: `bg-terminal-green/10 hover:bg-terminal-green/20 text-terminal-green px-2 py-0.5 rounded text-[9px] font-mono` — stops click propagation, opens Offer modal
- DETAILS: `bg-terminal-accent/10 hover:bg-terminal-accent/20 text-terminal-accent px-2 py-0.5 rounded text-[9px] font-mono` — opens Deal Detail modal

**Filter Logic (client-side JavaScript):**
1. Region filter: matches deal's suburb against the suburb list in the selected VIC region from the location tree
2. Suburb search: text `.includes()` match against suburb, address, and postcode (case-insensitive)
3. Strategy filter: exact match on `deal_type`
4. Golden only: `is_golden_opportunity === true`
5. BMV only: `bmv_pct > 0`
6. Sorting: all done client-side on the filtered array, then re-rendered

---

#### 4b. PROPERTIES PANEL

**Filter Bar:** flex row, gap 8px, margin-bottom 12px:
1. Suburb search input (w-48, placeholder "SEARCH SUBURB...")
2. Property type dropdown (15 types: HOUSE, UNIT, APARTMENT, TOWNHOUSE, VILLA, LAND, RURAL, FARM, ACREAGE, COMMERCIAL, INDUSTRIAL, RETAIL, WAREHOUSE, DUPLEX + "ALL TYPES")
3. Distressed-only toggle checkbox — red label "DISTRESSED"

**List View** — vertical stack (`space-y-1`), each property is a horizontal row:

```
┌──────────────────────────────────────────────────────────────────┐
│ [48px    ] [##]  123 Lygon Street                    3⚠  $650K  │
│ [gradient]  BED  Carlton, VIC 3053 — APARTMENT            $480/w│
│ [icon   ]        ↑ type label after suburb              420m²   │
│                                                      DOMAIN ↗   │
└──────────────────────────────────────────────────────────────────┘
```

- Container: `bg-terminal-panel rounded border border-terminal-border px-3 py-2 flex items-center justify-between hover:bg-terminal-border/30 transition cursor-pointer`
- Left: 48px gradient thumbnail (small size) + bed count center-aligned + address/suburb/type
- Right: distress badge (red "{count} ⚠"), price in `text-terminal-accent font-mono text-sm font-bold`, rent, land size, "DOMAIN ↗" link
- Clicking the row → opens Property Detail modal
- Domain link: stops propagation, opens `https://www.domain.com.au/sale/{suburb-slug}-vic-{postcode}/` in new tab

---

#### 4c. OFFERS PANEL

**Empty state:** "NO OFFERS GENERATED" centered

**Offer cards** — vertical stack (`space-y-2`):
- Container: `bg-terminal-panel rounded border border-terminal-border p-3`
- Header row: property address (left, `font-mono text-xs text-terminal-accent`) + date (right, `text-[10px] font-mono text-terminal-muted`)
- Body: full offer text in `text-xs text-terminal-text whitespace-pre-wrap leading-relaxed`
- Footer: offer amount + tone badge in `text-[10px] font-mono text-terminal-dim`

---

#### 4d. PIPELINE PANEL

**Configuration Panel:** `bg-terminal-panel rounded border border-terminal-border p-4`

Header row: "▶ LAUNCH PIPELINE" (accent, tracking-wider) + "🗺 LOCATION SCOUT" button (opens scout modal)

**4-column grid (gap 12px):**
1. **VIC REGIONS** — multi-select `<select>` with `size="4"` (visible 4 rows), 12 VIC region options. "CBD & Inner City" pre-selected.
2. **SUBURBS** — text input, placeholder "e.g. Bendigo, Epsom, Quarry Hill"
3. **STRATEGY** — dropdown: BTL, R2SA, FLIP, BRRR, HMO
4. **MAX AGENCIES** — number input, default 10, min 1, max 50

**Options column (5th in the grid):**
- AUTO-OFFERS checkbox (unchecked by default)
- STACKER checkbox (checked by default)
- QA ENGINE checkbox (checked by default)
- Each: `text-[10px] font-mono`, label color `text-terminal-dim`

**Execute button:** Full accent green: `bg-terminal-accent text-terminal-bg px-6 py-2 rounded font-mono text-xs font-bold tracking-wider hover:bg-terminal-accent/90 transition`. Label: "▶ EXECUTE PIPELINE". During run: disabled, text changes to "⏳ EXECUTING...", pipeline status in KPI strip changes to "RUNNING" (warn), then "COMPLETE" (green) or "ERROR" (red).

**Recent Runs section** below the config panel: "RECENT RUNS" label, empty state "NO PIPELINE RUNS"

---

#### 4e. PROFILER PANEL

**3-column grid (gap 12px):**

**Column 1 (1/3 width):** Input panel
- Header: "👤 INVESTOR PROFILER" (purple) + "AI-POWERED" badge (accent on accent/10 background)
- Description text: 10px muted
- Textarea: 6 rows, long placeholder text about income/goals/experience, `resize-none`
- "BUILD / UPDATE PROFILE" button: full-width, `bg-terminal-purple/20 text-terminal-purple border-terminal-purple/30`
- **Follow-up questions section** (hidden until profile built): "QUESTIONS TO STRENGTHEN YOUR PROFILE:" label, then clickable question cards that auto-fill the textarea

**Column 2-3 (2/3 width):**
- **3 metric cards** in a row (grid-cols-3):
  1. INVESTOR READINESS: huge number `/100` in `text-3xl font-mono font-bold text-terminal-accent`
  2. BORROWING POWER: `text-xl font-mono font-bold text-terminal-green`, label "APRA ESTIMATE"
  3. MAX PURCHASE: `text-xl font-mono font-bold text-terminal-bright`, label "INC. COSTS"
- **Completeness bar:** label "PROFILE COMPLETENESS" + percentage, then `health-bar` (4px tall, rounded, `bg-terminal-border` track) with `health-fill bg-terminal-accent` at dynamic width
- **Profile details panel:** Shows "NO PROFILE BUILT" initially, then after building: 2-column grid of profile attributes (risk tolerance, experience, goals, preferred states) in `text-[10px] font-mono`

**Interaction flow:** User types free text → clicks BUILD → API returns readiness score, borrowing power, max purchase → numbers animate in → follow-up questions appear → user clicks a question → it fills the textarea → user can refine

---

#### 4f. MENTOR PANEL

**4-column grid (gap 12px):**

**Column 1 (1/4 width):** Coaching topics sidebar
- 7 topic buttons in a vertical stack (`space-y-1`):
  - 📊 Market Commentary
  - 📚 Strategy Education
  - 📋 Portfolio Review
  - 📍 Suburb Deep Dive
  - 🔍 Deal Review
  - 🎯 Next Steps
  - 💬 General Coaching
- Each: `w-full text-left bg-terminal-bg hover:bg-terminal-border px-2 py-1.5 rounded text-[10px] font-mono text-terminal-text transition`
- Below a separator border: "📰 WEEKLY BRIEF" button in purple accent

**Columns 2-4 (3/4 width):** Chat interface
- Header: "MENTOR — AI PROPERTY COACH" (accent) + topic badge showing current topic
- Chat area: `flex-1 overflow-y-auto`, `min-height: 500px`
  - Welcome message centered: "🎓 YOUR PROPERTY MENTOR", "Ask anything about Australian property investment", "Coaching adapts to your experience level"
  - User messages: right-aligned, `chat-msg-user` class → `background: #1e3a5f; border: 1px solid #2563eb33;` — label "YOU" in info color
  - AI messages: left-aligned, `chat-msg-ai` class → `background: #064e3b; border: 1px solid #10b98133;` — label "🎓 MENTOR" in accent color
  - Follow-up topics: rendered as clickable buttons below AI responses
- Input: text input + "ASK" button (`bg-terminal-accent text-terminal-bg font-mono font-bold`)

**Interaction:** Click topic → pre-fills question → auto-sends → AI responds with coaching + follow-up topics

---

#### 4g. DUE DILIGENCE PANEL

Single panel: `bg-terminal-panel rounded border border-terminal-border p-4`

- Header: "⚠ DUE DILIGENCE BOT" in warn color + "$99/report" subtitle + "AI-POWERED" badge
- **Document type dropdown:** Section 32 / Vendor Statement, Contract of Sale, Strata / Body Corp Report
- **Text area:** 8 rows, placeholder "Paste Section 32 / Contract text here..."
- **Concerns input:** optional, placeholder "e.g., Planning to subdivide, worried about covenants..."
- **ANALYSE button:** full-width, `bg-terminal-warn/10 text-terminal-warn border-terminal-warn/30`, label "⚠ ANALYSE DOCUMENT — $99"
- **Result panel** (hidden until analysis): risk level badge (color-coded: LOW=green, MEDIUM=warn, HIGH=danger, CRITICAL=danger+bold), flags count, full analysis text in `whitespace-pre-wrap`

---

#### 4h. NEGOTIATION PANEL

**3-column grid (gap 12px):**

**Column 1 (1/3 width):** Agent Profile form
- Heading: "AGENT PROFILE" in info color
- 3 inputs: Agent Name, Agency, Your Max Budget (number)

**Columns 2-3 (2/3 width):** Live chat interface
- Header: "NEGOTIATION SHADOW — LIVE COACHING" (accent) + "$500/mo" (muted)
- Chat area: `min-height: 400px`
- Empty state: "SHADOW MODE READY", "Describe what's happening in your negotiation"
- Same chat styling as mentor (user = blue bg, AI = green bg, labels "YOU" and "SHADOW")
- Input + "SEND" button

---

#### 4i. QA ENGINE PANEL

**Top section — 3-column grid (gap 12px):**

**Column 1: SYSTEM HEALTH**
- Header: "🔬 SYSTEM HEALTH" in info color
- Health grid: per-agent health bars. Each agent shows name + score + 4px-tall colored bar:
  - ≥ 80: `bg-terminal-green`
  - ≥ 60: `bg-terminal-warn`
  - < 60: `bg-terminal-red`
- "REFRESH HEALTH CHECK" button in info color

**Column 2: PERFORMANCE**
- Header: "📈 PERFORMANCE" in accent
- Statistics list (populated after deals exist): Total Deals, Cash Flow Positive (count + %), Golden Opportunities, Avg Bargain Score, Avg Gross Yield
- Strategy mix breakdown below

**Column 3: SELF-GOVERNANCE**
- Header: "⚡ SELF-GOVERNANCE" in gold
- Description text about QA monitoring
- 5 dimension weights displayed: Accuracy 30%, Relevance 20%, Completeness 20%, Timeliness 10%, Actionability 20%
- "⚡ RUN GOVERNANCE CYCLE" button in gold

**Bottom section:** "🧬 EVOLVED SKILLS" — 4-column grid of evolved skill template cards (populated after governance run)

---

#### 4j. PHOTOS PANEL

**3-column grid (gap 12px):**

**Column 1 (1/3 width):** Upload & controls
- Header: "📸 PHOTO ENHANCER" in accent + "FREE" badge in green
- Description text
- File input: `accept="image/*"`, on change → shows preview in "ORIGINAL" slot
- Preset dropdown: 5 options (Real Estate Standard, Luxury Listing, Renovation Before/After, Exterior Hero Shot, Interior Bright & Airy)
- AI Upscale (2×) checkbox
- "✨ ENHANCE PHOTO" button (accent)
- "ANALYSE QUALITY" button (muted panel style, smaller)
- Quality analysis results (hidden until analysed): 5 metrics in rows

**Columns 2-3 (2/3 width):** Before/After
- Header: "BEFORE / AFTER PREVIEW"
- 2-column grid, each `min-height: 300px`:
  - ORIGINAL: shows uploaded photo or "Upload a photo" placeholder
  - ENHANCED: shows enhanced photo or "Enhanced result will appear here"
- Below: 4-column metrics grid (hidden until enhanced): brightness, contrast, sharpness, improvement percentages

---

### 5. MODALS — 5 OVERLAY DIALOGS

All modals share: `fixed inset-0 z-50`, initially `hidden`, when open: `flex items-center justify-center`, backdrop `bg-black/80`. Content panel: `bg-terminal-panel rounded border border-terminal-border p-5 animate-fade-in max-h-[85vh] overflow-y-auto`.

Close button: `&times;` in top-right, `text-terminal-muted hover:text-terminal-text text-lg`.

#### 5a. Quick ROI Modal
- Width: `max-w-sm` (384px)
- Fields: Purchase Price (number, placeholder "650000"), Weekly Rent (number, placeholder "500"), State (dropdown, VIC pre-selected)
- CALCULATE button: full-width, `bg-terminal-accent text-terminal-bg font-mono font-bold`
- Result panel (hidden until calculated):
  - Verdict badge (centered, large): "STRONG YIELD", "WEAK YIELD", etc. — green/red/warn coloring
  - 2×2 grid: Gross Yield, Net Yield (est.), Monthly Cash Flow (green if ≥0, red if <0), Stamp Duty

#### 5b. Offer Generation Modal
- Width: `max-w-md` (448px)
- Hidden input: `offer-deal-id` (set when opening from a deal card)
- Fields: Full Name, Entity (optional), Max Budget (number), Tone (dropdown: PROFESSIONAL, EMPATHETIC, URGENT, FAMILY STORY, INVESTOR DIRECT), Personal Story (textarea, 2 rows, optional)
- "▶ GENERATE OFFER" button: full-width, `bg-terminal-green text-terminal-bg font-mono font-bold`
- On success: closes modal, shows success toast, switches to Offers tab, refreshes offer list

#### 5c. Deal Detail Modal
- Width: `max-w-2xl` (672px)
- Header: "DEAL DEEP DIVE" in accent
- Content sections (stacked vertically, `space-y-3`):
  1. **Property type header placeholder:** 96px tall gradient block + 4xl emoji + type name + suburb/postcode
  2. **2-column grid:** Left = property address, suburb/state, bed/bath/car, land/building size, zoning, condition. Right = Bargain Score (3xl bold, color-coded) + summary + 4 sub-score rows (Price Deviation, Cash Flow Score, Market Timing, Below Market Value %)
  3. **Financial Analysis panel** (`bg-terminal-bg border`): 3 rows of 4-column centered metric grids:
     - Row 1: Purchase Price, Stamp Duty, Total Investment, Loan Amount
     - Row 2: Weekly Rent, Gross Yield (accent), Net Yield (green/red), Monthly Cash Flow (green/red)
     - Row 3: Cash-on-Cash Return, Return on Investment, Price per m², Payback Period
  4. **Renovation & Flip Analysis** (conditional, only if refurb/flip values > 0): 3 columns — Renovation Cost, After Repair Value, Flip Profit (green)
  5. **Distress Signals** (conditional): list of keyword + confidence percentage rows
  6. **AI Analysis** (conditional): `whitespace-pre-wrap` long-form text
  7. **Listing Description** (conditional): marketing copy in dim text
  8. **Action buttons row:** GENERATE OFFER (green), DOMAIN.COM.AU ↗ (accent), REALESTATE.COM.AU ↗ (muted)
  9. **Honesty disclaimer:** "⚠ SIMULATED LISTING — Search real portals above to verify actual availability & pricing" — `text-[8px] text-terminal-muted font-mono italic centered`

#### 5d. Property Detail Modal
- Width: `max-w-2xl` (672px)
- Header: "PROPERTY DETAIL" in accent
- Content:
  1. **Type header:** 96px gradient block + emoji + type + suburb
  2. **2-column grid:** Left = address, suburb/state, bed/bath/car, land/building size, year built, zoning, condition. Right = price (2xl accent), est. rent, current rent (green if tenanted), council rates, water rates, strata levies
  3. **Agent info** (conditional): agent name, agency, phone
  4. **Distress signals** (conditional)
  5. **Listing description** (conditional)
  6. **Verify on Real Portals** box (warn border): explanation text + 2 buttons: "🏠 SEARCH DOMAIN.COM.AU ↗" (accent) + "🔎 SEARCH REALESTATE.COM.AU ↗" (green) — both open real portal URLs in new tabs

#### 5e. Location Scout Modal
- Width: `max-w-2xl` (672px)
- Header: "LOCATION SCOUT" (accent, bold, sm) + dynamic DB stats subtitle + close button

**Scope selector — 3 toggle buttons:**
- 🌏 ALL VIC (default active: accent bg/border)
- 🗺 BY REGION
- 🏘 BY SUBURB
- Active: `bg-terminal-accent/20 text-terminal-accent border-terminal-accent/30`
- Inactive: `bg-terminal-panel text-terminal-dim border-terminal-border hover:text-terminal-text`
- Switching scope resets selections and shows/hides relevant rows

**Region picker** (shown for BY REGION and BY SUBURB scope):
- Dropdown populated with all VIC regions
- On change: shows market data preview grid

**Suburb picker** (shown for BY SUBURB scope):
- Search input with fuzzy matching (calls `/properties/locations/search?q=...`)
- Results list: each result shows suburb name, state, postcode, region, median price, growth %, yield %
- Clicking toggles selection. Selected suburbs shown as removable pill tags below (`bg-terminal-accent/10 text-terminal-accent border-terminal-accent/30 rounded px-2 py-0.5 text-[9px] font-mono` with × button)

**Market data preview grid** (for region scope): 2-3 column grid of suburb cards showing name/state/region

**Scout target summary box:** Before execute button — shows scope summary (e.g., "All VIC — 15 Regions · 134 Suburbs") with region count, suburb count, property count

**Execute button:** Full-width, `bg-terminal-accent text-terminal-bg py-2.5 rounded font-mono text-xs font-bold`

---

### 6. CHATBOT FLOATING WIDGET

#### 6a. FAB (Floating Action Button)
- Position: `fixed bottom-6 right-6 z-40`
- Size: `w-14 h-14` (56×56px)
- Shape: `rounded-full` (circle)
- Background: `bg-terminal-accent`
- Content: 💬 emoji (2xl)
- Hover: `hover:scale-110 transition-transform`
- Shadow: `shadow-lg`
- Notification badge: `absolute -top-1 -right-1`, red circle (`bg-terminal-danger`), `w-5 h-5`, "!" text. Hidden by default, shown when trending news loads while chatbot is closed.

#### 6b. Chat Panel
- Position: `fixed bottom-24 right-6 z-40` (appears above the FAB)
- Size: `w-96` (384px wide), `max-h-[520px]`
- Shape: `rounded-lg`, `shadow-2xl`
- Background: `bg-terminal-panel border border-terminal-border`
- Layout: flex column

**Panel sections (top to bottom):**

1. **Header bar** (px-4 py-3, bottom border, `bg-terminal-bg/50 rounded-t-lg`):
   - Live dot + "MELBOURNE MARKET AI" (accent, bold, tracking-wider, `text-xs font-mono`) + "Trending news & market intelligence" (9px muted)
   - Right side: 📰 (refresh news), 🗑 (clear session), × (close)

2. **Trending news strip** (px-3 py-2, bottom border, `bg-terminal-bg/30`, max-h 96px, scrollable):
   - "TRENDING" label (9px muted tracking-wider)
   - Up to 4 news article rows:
     - VIC relevance dot: 🟢 (≥70%), 🟡 (≥40%), ⚪ (<40%)
     - Truncated title (clickable → sends "Tell me about: {title}" as chat message)
     - Source name (muted, max 12 chars)

3. **Messages area** (flex-1, `overflow-y-auto`, px-3 py-3, min-h 200px, max-h 300px):
   - **Welcome message** (left-aligned AI bubble): "Hey! I'm your Melbourne property market assistant..."
   - **User messages:** right-aligned, `chat-msg-user` (`bg: #1e3a5f, border: 1px solid #2563eb33`), rounded-lg, max-w 85%
   - **AI messages:** left-aligned, `chat-msg-ai` (`bg: #064e3b, border: 1px solid #10b98133`), rounded-lg, max-w 85%
   - **Typing indicator:** AI bubble with "Analysing..." text, shown while waiting for response, removed on response
   - **Error messages:** red-tinted border, "ERROR" label in danger color
   - Each message has label ("YOU" / "MARKET AI" / "ERROR") in `text-[10px] font-mono`
   - Text formatting: **bold** → `<strong class="text-terminal-bright">`, [links](url) → accent-colored clickable, bullet points → accent "•" prefix, numbered lists → accent numbers

4. **Input footer** (px-3 py-2, top border, `bg-terminal-bg/30 rounded-b-lg`):
   - Text input: `flex-1`, `bg-terminal-bg border-terminal-border rounded px-3 py-2 text-xs font-mono`, `focus:border-terminal-accent focus:outline-none`
   - Send button: `bg-terminal-accent text-terminal-bg px-3 py-2 rounded text-xs font-mono font-bold`, label "▶"
   - Below input — left: 3 quick-chat buttons (`text-[9px] text-terminal-muted hover:text-terminal-accent font-mono`):
     - 📰 News → "What's trending in Melbourne property?"
     - 📊 Yields → "Best suburbs for yield in Melbourne?"
     - 🔮 Outlook → "Current Melbourne market outlook?"
   - Below input — right: status text (8px muted), shows "Ready", "Thinking...", or "{N} messages"

---

### 7. TOAST NOTIFICATION SYSTEM
- Container: `fixed bottom-10 right-4 z-50`, vertical stack (`space-y-1`)
- Each toast: `border rounded px-3 py-2 text-xs font-mono animate-fade-in`
- Color variants: info (blue/20 + blue/40 border + blue text), success (green), error (red), warn (amber)
- Auto-dismiss after 4 seconds
- Multiple toasts stack vertically

---

### 8. STATUS BAR FOOTER
- Container: `bg-terminal-panel`, top border, px-4 py-1, flex row justify-between
- **Left items** (10px mono muted): "PIM v4.0.0", separator, status text ("READY"), separator, "propertyinsightsmelbourne.com.au"
- **Right items** (10px mono): DB status ("● SQLite PERSISTED" green), separator, Scout status ("● AUTO-SCOUT ACTIVE" green), separator, "12 AGENTS + VALUE-ADD ENGINE", separator, API status ("● API CONNECTED" green), separator, subscription tier ("EXPLORER" accent)

Dynamic IDs: `status-text`, `db-status`, `scout-status`, `api-status`, `sub-tier`

---

### 9. PAGE INITIALIZATION SEQUENCE (on DOMContentLoaded)

1. Check API health (`/health`) → update API status, DB size, auto-scout interval/status in footer and ticker
2. Load location tree (`/properties/locations/tree`) → populate VIC region dropdowns
3. Load deals and properties in parallel (`/deals/`, `/properties/`)
4. Load offers (non-blocking)
5. Compute and set ticker shadow listing count (from properties data or `/locations/stats`)
6. Run QA health check (`/qa/health`) → populate ticker QA status + QA health grid
7. Populate QA performance/trends panel from deal statistics
8. Start AEST clock (1-second interval)
9. Load chatbot trending news (`/chat/trending?limit=5`)

---

### 10. LANDING PAGE (`/landing`) — MARKETING SITE

Separate HTML page, same design system but with marketing-focused layout.

#### Design Tokens
Same color palette as terminal, plus:
- `pia-500`: `#00d4aa` (matches terminal-accent)
- `pia-bg`: `#0a0e17`
- `pia-panel`: `#111827`
- Custom CSS: `.gradient-text` — 3-color gradient text (teal → blue → purple): `background: linear-gradient(135deg, #00d4aa 0%, #3b82f6 50%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;`
- `.hero-glow` — radial gradient from top: `radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,212,170,0.15), transparent)`
- `.card-glow:hover` — `box-shadow: 0 0 30px rgba(0,212,170,0.1);`
- `.float` animation — `translateY(0) → translateY(-6px) → translateY(0)` over 6s, infinite

#### Sections (top to bottom):

1. **Fixed Nav Bar:** `bg-pia-bg/80 backdrop-blur-xl border-b border-gray-800/50`, max-w-7xl centered, 64px height. Logo (32px square teal "PIA") + "Property Insights" + "AUSTRALIA" badge. Desktop nav: Agents, Pricing, ROI links + "Launch Terminal" teal CTA button.

2. **Hero Section:** pt-32 pb-20, centered text:
   - Badge: "POWERED BY CLAUDE OPUS 4.6 — 7 AGENTIC AI MODULES" — mono, accent, bordered rounded-full
   - H1: "The Bloomberg Terminal for Australian Property" — 5xl/7xl, extrabold, gradient-text on "Bloomberg Terminal"
   - Subtitle: "less than the cost of one buyer's agent lunch" — semibold white highlight
   - 2 CTAs: "Launch Terminal — Free" (teal solid + shadow) + "See Pricing" (bordered)
   - Fine print: "No credit card required · Explorer tier is free forever"

3. **6 Agent Cards** (3-column grid):
   - Each: `bg-pia-panel border border-gray-800 rounded-xl p-5 hover:border-pia-500/30 card-glow transition-all`
   - Agent icon (40px colored/10 bg) + name + tagline (xs uppercase mono) + description paragraph
   - Due Diligence & Negotiation Shadow cards have premium price badges in their corner

4. **ROI Comparison** (3 cards side by side):
   - PIA ($2,388/yr): highlighted with border-2 border-pia-500 + "BEST VALUE" badge + float animation + savings callout
   - Buyer's Agent ($12K-$30K/deal): gray border, disadvantage bullets
   - Junior Analyst ($60K+/yr): gray border, disadvantage bullets

5. **4-Tier Pricing Grid** (4 columns):
   - Explorer (Free), Investor ($199/mo with "POPULAR" badge + border-2 teal), Pro Sourcer ($499/mo), The Closer ($2,500/deal in amber)
   - Each card: features list with ✓/✕ markers, CTA button
   - Below: 3 add-on cards (DD Bot $99/report, Negotiation Shadow $500/mo, First Look $49/mo)

6. **CTA Section:** "Stop Overpaying for Property Intelligence" with large teal "Launch Terminal — Free Forever" button

7. **Footer:** Company name, ABN placeholder, email, legal disclaimer, copyright

---

## 100x VALUE MULTIPLIER — RECOMMENDATIONS TO MAKE IT ADDICTIVE

> The following are strategic recommendations to transform PIM from an MVP into a product investors can't stop using—organized by impact and addiction mechanics.

---

### R1. REAL-TIME DEAL FEED WITH PUSH NOTIFICATIONS 🔴 Critical

**Current:** Users must manually click SCOUT or check the terminal.
**Upgrade:** WebSocket-powered live deal feed. New golden opportunities animate into the deals grid in real-time with a brief gold flash + desktop notification. Sound effect optional (soft "ding" for golden, subtle "tick" for normal).

**Implementation:**
- WebSocket endpoint `/ws/deals` pushes new deals as they're scouted
- Deal cards slide-in from the right with a 300ms animation
- Browser `Notification.requestPermission()` + `new Notification("🏆 Golden Opportunity in Brunswick!")` when tab is hidden
- Badge count on browser tab title: `(3) PIM — Terminal`

**Addiction mechanic:** Variable reward schedule — users don't know when the next golden deal drops, so they keep the tab open like a stock ticker.

---

### R2. GAMIFICATION — INVESTOR SCORE & LEADERBOARD 🔴 Critical

**Add:**
- **Investor XP system:** Points for: completing profile (+100), first analysis (+50), making an offer (+200), scouting a suburb (+25), asking mentor (+10), running DD (+300). Levels: Apprentice → Analyst → Sourcer → Strategist → Tycoon.
- **Portfolio heatmap:** Interactive map of Victoria showing your deal locations as hot/cold circles. More deals in an area = bigger glow.
- **Achievement badges:** "First Blood" (first offer), "Golden Eye" (found 5 golden deals), "Marathon Man" (7-day login streak), "Certified Closer" (10 offers), "VIC Specialist" (analysed deals in all 15 regions).
- **Public leaderboard** (opt-in): Top investors by portfolio value, number of offers, avg bargain score.

**Addiction mechanic:** Progress bars, levels, and social proof create compulsive return behavior. Users want to "level up."

---

### R3. INTERACTIVE SUBURB HEATMAP 🟡 High-Value

**Replace or complement the region dropdown with a clickable SVG/Canvas map of Victoria.** Suburbs are colored by:
- Default: median price (green = affordable → red = premium)
- Toggle: yield (green = high yield)
- Toggle: bargain score density (gold = many deals)
- Toggle: growth rate

**Hover:** Shows suburb tooltip with median, yield, growth, deal count.
**Click:** Filters deals to that suburb instantly.

**Addiction mechanic:** Maps are inherently exploratory — users zoom, pan, and discover pockets of value they never knew existed.

---

### R4. DEAL WATCHLIST + PRICE TRACKING 🟡 High-Value

**Add a "Watch" button to every deal card.** Watched deals:
- Show in a new "WATCHLIST" tab (between DEALS and PROPERTIES)
- Track price changes over time (simple line chart)
- Alert when bargain score changes (up or down) or when status changes (e.g., goes from ACTIVE to UNDER_OFFER)
- Show "days since added to watchlist" counter

**Addiction mechanic:** Loss aversion — "Will I miss this deal if I don't check?" + price tracking creates anxiety loops.

---

### R5. DAILY MARKET BRIEFING ("THE MORNING WRAP") 🟡 High-Value

**At 7am AEST daily, auto-generate and surface a market intelligence brief:**
- Top 3 new golden opportunities
- Auction clearance results from Saturday
- Suburb of the week (highest growth, yield, or value)
- One mentor coaching tip
- One news headline

**Delivery:** Shown as a special chatbot message when the user opens the terminal, OR as an email digest, OR as a push notification.

**Addiction mechanic:** Creates a daily habit loop. Users open PIM every morning before coffee, like checking the stock market.

---

### R6. SIDE-BY-SIDE DEAL COMPARISON 🟡 High-Value

**Add a "Compare" checkbox to deal cards.** When 2–4 deals are selected, show a floating "COMPARE" button that opens a comparison modal:
- Properties displayed in columns
- Every metric aligned in rows for easy visual comparison
- Winning metric in each row highlighted in green
- Overall recommendation at the bottom

**Addiction mechanic:** Comparison reduces decision paralysis and gives users confidence to move forward with offers.

---

### R7. AI DEAL SCORE EXPLANATION ("WHY THIS SCORE?") 🟢 Quick-Win

**On every deal card and detail modal, add a "?" icon next to the Bargain Score.** Clicking it shows a micro-modal:
- "This property scored 78/100 because:"
  - "✅ Priced 12% below suburb median of $720K" (+31 pts)
  - "✅ Net yield of 4.2% exceeds cash flow threshold" (+22 pts)
  - "⚠ Only 15 days on market (below average)" (+8 pts)
  - "⬛ No distress signals detected" (+0 pts)
  - "✅ Moderate growth suburb" (+17 pts)

**Addiction mechanic:** Transparency builds trust. Users understand the system, trust it more, and use it more.

---

### R8. CONVERSATIONAL ONBOARDING WIZARD 🟢 Quick-Win

**Replace the current profiler free-text box with a guided conversation flow:**
- Step 1: "What's your primary investment goal?" (radio cards: Cash Flow, Capital Growth, Balanced, Retirement, First Property)
- Step 2: "How many properties do you own?" (0, 1-2, 3-5, 6+)
- Step 3: "What's your annual household income?" (slider: $50K–$500K+)
- Step 4: "How much cash do you have available?" (slider)
- Step 5: "Which VIC regions interest you?" (clickable map or tag selector)

**After completion:** Animate the readiness score filling up, then auto-switch to Deals tab filtered to their preferences with a toast "Found 12 deals matching your profile!"

**Addiction mechanic:** Sunk cost fallacy — after investing 2 minutes in profile setup, users feel invested and are more likely to continue using.

---

### R9. MICRO-CHARTS ON DEAL CARDS 🟢 Quick-Win

**Add tiny inline sparkline charts to deal cards:**
- 30-day suburb price trend (tiny line chart, 40px wide, next to suburb name)
- Yield vs. suburb average (tiny bar chart, shows deal yield as a vertical bar against suburb average)

**Implementation:** SVG or Canvas, no external charting library, fits in the existing card layout.

**Addiction mechanic:** Financial data visualization is inherently engaging. Small charts add density and make the terminal feel "alive."

---

### R10. ONE-CLICK "FOLLOW-UP" ACTIONS 🟢 Quick-Win

**After every AI interaction, present exactly 1–3 next actions:**
- After analysing a deal: [📝 Generate Offer] [📊 Run DD] [🔍 Compare to Comps]
- After generating an offer: [📱 Send via WhatsApp] [📧 Email to Agent] [📋 Copy to Clipboard]
- After mentor coaching: [🎯 Find deals matching this strategy] [📚 Learn more] [💬 Ask follow-up]
- After scouting: [📊 Bulk Analyse All] [⭐ Watchlist top 3] [🗺 Scout adjacent suburbs]

**Addiction mechanic:** Reduces friction to zero. Users follow a path of least resistance deeper into the product.

---

### R11. STREAK COUNTER + SESSION TIMER 🟢 Quick-Win

**In the status bar footer, add:**
- "🔥 3-day streak" — consecutive days visiting the terminal (resets if a day is missed)
- "⏱ 14m session" — how long they've been active (subtle social proof to themselves)

**After 7-day streak:** Unlock "VIC Market Insider" badge + show a subtle confetti animation.

**Addiction mechanic:** Streaks are the most powerful retention mechanic in consumer products (see Snapchat, Duolingo). Loss of a streak creates massive return motivation.

---

### R12. KEYBOARD SHORTCUTS (POWER-USER DELIGHT) 🟢 Quick-Win

**Add Bloomberg Terminal-style keyboard shortcuts:**
| Key | Action |
|-----|--------|
| `D` | Switch to Deals tab |
| `P` | Switch to Properties tab |
| `S` | Focus Scout input |
| `R` | Open ROI calculator |
| `M` | Switch to Mentor tab |
| `C` | Toggle Chatbot |
| `G` | Filter to Golden only |
| `?` | Show keyboard shortcut overlay |
| `Esc` | Close any open modal |
| `←` / `→` | Previous/Next deal in detail modal |

Show a subtle "Press ? for shortcuts" hint in the status bar on first visit.

**Addiction mechanic:** Power users become emotionally attached to products they've mastered. Keyboard shortcuts create mastery feedback loops.

---

### R13. DARK/LIGHT THEME TOGGLE + CUSTOM ACCENT COLORS 🟣 Nice-to-Have

**Add a theme picker in the top bar** (next to the user avatar). Options:
- Terminal Dark (current, default)
- Terminal Light (for daytime use)
- Custom accent color (let users pick teal, blue, purple, green, gold)

**Addiction mechanic:** Personalization creates ownership. "My terminal" vs "the terminal."

---

### R14. EXPORTABLE DEAL REPORTS (PDF/CSV) 🟣 Nice-to-Have

**Add "Export" buttons:**
- Deal Detail modal → "📄 EXPORT PDF" — generates a professional 1-page deal summary with all financials, bargain score breakdown, and market analysis. Branded with PIM logo.
- Deals tab → "📊 EXPORT CSV" — downloads all filtered deals as a spreadsheet.

**Addiction mechanic:** Export creates external artifacts that users share with business partners, accountants, and mentors — viral distribution + social proof.

---

### R15. SOCIAL SHARING + REFERRAL PROGRAM 🟣 Nice-to-Have

**Add "Share" buttons on golden deal cards:**
- "Share this golden opportunity" → generates a unique link or image snippet
- Referral program: "Invite 3 investors → get 1 month Investor tier free"
- Anonymous aggregated stats page: "PIM investors have found 1,247 golden deals this month across Victoria"

**Addiction mechanic:** Social proof + network effects. Every share brings potential new users.

---

### ADDICTION FRAMEWORK SUMMARY

| Layer | Current | Recommended |
|-------|---------|-------------|
| **Trigger** | Manual: user opens terminal | Automated: push notifications, daily briefing, price alerts |
| **Action** | Browse deals, click buttons | Minimal friction: 1-click follow-ups, keyboard shortcuts, conversational onboarding |
| **Variable Reward** | New deals on scout | Real-time deal feed (WebSocket), streak counter, leaderboard position changes |
| **Investment** | Profile building | Watchlist, achievement badges, XP progress, custom theme, exported reports |

**Priority order for maximum impact:**
1. WebSocket live deal feed + push notifications (R1)
2. Daily Morning Wrap briefing (R5)
3. Investor XP + streak counter (R2, R11)
4. Interactive suburb heatmap (R3)
5. Deal watchlist + price tracking (R4)
6. Conversational onboarding wizard (R8)
7. Everything else (R6-R15)

---

## 10 INVESTOR PERSONAS — WHO WE'RE BUILDING FOR

Every feature, agent behaviour, UI element, and coaching tone must be tailored to one of these 10 investor archetypes. The personas span the complete Australian property investment lifecycle — from someone who has never bought anything to institutional-grade portfolio operators. On first login the platform must identify which persona the user fits (via the Profiler Agent's onboarding conversation) and adapt the entire experience accordingly.

### Data Model Addition — `InvestorPersona` Enum

```python
class InvestorPersona(str, Enum):
    FIRST_HOME_DREAMER    = "first_home_dreamer"
    STEPPING_UP           = "stepping_up"
    ACCIDENTAL_LANDLORD   = "accidental_landlord"
    EQUITY_UNLOCKED       = "equity_unlocked"
    PORTFOLIO_BUILDER     = "portfolio_builder"
    TAX_STRATEGIST        = "tax_strategist"
    SMSF_RETIREE          = "smsf_retiree"
    DEVELOPER_FLIPPER     = "developer_flipper"
    PROFESSIONAL_SOURCER  = "professional_sourcer"
    ENTERPRISE_SYNDICATE  = "enterprise_syndicate"
```

---

### Persona 1: THE FIRST HOME DREAMER
**Tagline:** "I've never bought anything. Where do I even start?"

| Attribute | Detail |
|-----------|--------|
| **Age range** | 22–35 |
| **Income** | $55K–$110K salary (single or combined couple income) |
| **Savings** | $20K–$120K (some in FHSSS / First Home Super Saver Scheme) |
| **Properties owned** | 0 |
| **Debt** | HECS/HELP ($15K–$60K), possibly a car loan, credit card <$5K limit |
| **Experience level** | BEGINNER |
| **Risk tolerance** | CONSERVATIVE |
| **Primary goal** | FIRST_HOME |
| **Entity** | PERSONAL (doesn't know trusts exist) |
| **Borrowing power** | $350K–$650K (single); $500K–$950K (couple) |
| **Typical search** | 2-bed unit or townhouse in middle-ring Melbourne suburbs |
| **Psychographic** | Overwhelmed by news ("property is too expensive"), paralysed by choice, scared of making a mistake, compares renting vs buying constantly |

**What they need from PIM:**
- **Onboarding wizard** that starts with "Are you renting right now?" — meets them where they are
- **Rent vs Buy calculator** showing break-even timeline in their target suburbs
- **First Home Buyer (FHB) concession auto-detection** — VIC stamp duty exemptions (<$600K), FHOG ($10K for new builds), FHSSS balance estimator
- **Borrowing power estimator** that explains APRA buffers in plain English
- **Suburb affordability heatmap** filtered to their budget
- **Mentor Agent in "Hand-Holding" mode** — explains every metric (what IS gross yield?), no jargon, links to definitions
- **"My First Deal" guided pathway** — step-by-step from profile → suburb shortlist → property viewing checklist → offer → settlement
- **Confidence score** — "Based on your savings and income, you're 78% ready to buy in Footscray"

**Subscription tier:** EXPLORER (free) → upgrade to INVESTOR when serious
**Risk:** Churn if overwhelmed. Must keep complexity hidden behind progressive disclosure.

---

### Persona 2: THE STEPPING UP BUYER
**Tagline:** "I own my home. I want to build wealth but I'm nervous about investing."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 30–45 |
| **Income** | $90K–$180K household |
| **Savings** | $30K–$80K cash + $50K–$200K equity in PPOR |
| **Properties owned** | 1 (own home / PPOR) |
| **Debt** | Home loan $350K-$650K, maybe HECS residual |
| **Experience level** | NOVICE |
| **Risk tolerance** | MODERATE |
| **Primary goal** | WEALTH_CREATION |
| **Entity** | PERSONAL or JOINT (hasn't considered trusts yet) |
| **Borrowing power** | $450K–$800K (after existing mortgage) |
| **Typical search** | Sub-$600K investment property, regional VIC or outer-ring Melbourne |
| **Psychographic** | Reads articles about property investing, listens to podcasts, heard about negative gearing but doesn't fully understand it, worried about tenants trashing the place, partner may be sceptical |

**What they need from PIM:**
- **Equity release calculator** — "You have ~$180K accessible equity at 80% LVR. Here's what that unlocks."
- **"What if I rented my home out?" scenario** — dual-scenario modelling (keep PPOR vs convert to IP)
- **Partner convincer pack** — exportable PDF with ROI projections, risk mitigation, and market data
- **Negative gearing explainer** built into every deal analysis — "This property costs you $127/week out-of-pocket AFTER tax benefits"
- **Tenant risk scoring** on properties (vacancy rates, median days on market for rentals)
- **Insurance & landlord protection** guidance built into deal summaries
- **Mentor Agent in "Educator" mode** — explains concepts in depth, offers "why" not just "what"
- **3-property roadmap** — "Here's how your first IP leads to a second within 3 years using equity growth"

**Subscription tier:** INVESTOR ($199/mo) — sweet spot for this persona
**Risk:** Analysis paralysis. Needs social proof ("437 investors in your bracket bought this year").

---

### Persona 3: THE ACCIDENTAL LANDLORD
**Tagline:** "I inherited a property / kept my old place when I upgraded. Now what?"

| Attribute | Detail |
|-----------|--------|
| **Age range** | 35–55 |
| **Income** | $80K–$200K salary + $15K–$35K existing rental income |
| **Savings** | $10K–$50K cash (didn't plan for investing so cash is thin) |
| **Properties owned** | 1-2 (PPOR + inherited or kept IP) |
| **Debt** | Home loan + maybe small residual loan on IP (or inherited free-and-clear) |
| **Experience level** | NOVICE (owns property but doesn't think like an investor) |
| **Risk tolerance** | CONSERVATIVE to MODERATE |
| **Primary goal** | CASH_FLOW (wants the rental to "not be a headache") |
| **Entity** | PERSONAL (inherited in personal name, probably wrong structure) |
| **Borrowing power** | Highly variable — may have strong equity but never considered using it |
| **Typical search** | Not actively searching — needs PIM to show them what's possible |
| **Psychographic** | Treats their IP like a savings account not a business, under-rented, may have capital gains implications they haven't considered, didn't choose this path but curious to optimise |

**What they need from PIM:**
- **Portfolio health check** — "Your Brunswick IP is worth $850K, rented at $380/wk. Market rent is $520/wk. You're leaving $7,280/year on the table."
- **Capital gains tax scenario modelling** — "If you sell now vs hold 5 years, here's the CGT difference"
- **Entity restructuring guidance** — "Consider transferring to a family trust. Here's why (asset protection, tax splitting)"
- **Rental yield optimisation** — current rent vs market comps, renovation ROI for rent uplift
- **"You accidentally have equity" discovery** — show them their leverageable position
- **Stacker Agent** presenting "what you could buy NEXT with your existing equity" scenarios
- **Mentor Agent in "Wake Up" mode** — proactive, shows missed opportunity cost
- **Property manager comparison** tools (optional future feature)

**Subscription tier:** EXPLORER → INVESTOR once they realise they're sitting on a goldmine
**Risk:** Apathy. They didn't choose this. Must show immediate dollar value of optimising.

---

### Persona 4: THE EQUITY UNLOCKED
**Tagline:** "I have 2-3 properties and I've figured out the game. Time to accelerate."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 35–50 |
| **Income** | $120K–$250K salary + $40K–$80K rental income |
| **Savings** | $50K–$150K cash + $200K–$500K accessible equity |
| **Properties owned** | 2-3 (PPOR + 1-2 IPs) |
| **Debt** | $800K–$1.5M across properties |
| **Experience level** | INTERMEDIATE |
| **Risk tolerance** | GROWTH |
| **Primary goal** | WEALTH_CREATION transitioning to CAPITAL_GROWTH |
| **Entity** | MIX — PPOR in personal name, considering family trust for next purchase |
| **Borrowing power** | $600K–$1.2M (existing servicing capacity) |
| **Typical search** | $500K–$800K properties with strong growth fundamentals and 5%+ yield |
| **Psychographic** | Has an accountant (or should), understands LVR, reads API, knows about trust structures but hasn't pulled the trigger, wants to get to 5+ properties in 5 years, compares every deal quantitatively |

**What they need from PIM:**
- **Full agent stack** — Scout, Analyst, Stacker, all working together
- **Cross-collateralisation analysis** — "Don't cross-collateralise. Here's a standalone equity release strategy."
- **Entity strategy wizard** — trust vs company vs personal for the NEXT purchase specifically
- **Portfolio-level LVR dashboard** — total exposure, per-property LVR, refinance triggers
- **Yield vs growth scatterplot** for all 134 suburbs overlaid with their budget
- **"Deal of the Week" curated pipeline** — pre-analysed deals matching their criteria
- **Stacker Agent in full force** — BRRR modelling, IO vs P&I comparison, refinance timeline
- **Tax optimisation preview** for every deal — depreciation schedule, negative gearing offset, bracket impact
- **5-year portfolio projection** showing compound equity growth and passive income trajectory

**Subscription tier:** INVESTOR ($199/mo) → PRO_SOURCER ($499/mo) when pipeline velocity matters
**Risk:** Impatient with basics. Needs dense, data-rich UI. Will leave if the platform feels "beginner."

---

### Persona 5: THE PORTFOLIO BUILDER
**Tagline:** "I'm building to 10+ properties and financial freedom. Show me the machine."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 35–55 |
| **Income** | $150K–$350K combined (salary + rental + business) |
| **Savings** | $100K–$300K deployable + $500K–$1M+ accessible equity |
| **Properties owned** | 4-8 |
| **Debt** | $2M–$5M across portfolio |
| **Experience level** | ADVANCED |
| **Risk tolerance** | GROWTH to AGGRESSIVE |
| **Primary goal** | PASSIVE_INCOME — wants to replace salary ($100K–$200K/yr target) |
| **Entity** | Multi-entity: PPOR personal, IPs in family trust, some in company |
| **Borrowing power** | Complex — may be hitting serviceability ceiling, needs creative solutions |
| **Typical search** | High-yield regional, dual-income properties, subdivisions, commercial crossover |
| **Psychographic** | Spreadsheet warrior, has broker + accountant + solicitor, benchmarks their portfolio against indices, thinks in terms of "next purchase serviceability gap", frustrated by traditional property platforms that don't think like an investor |

**What they need from PIM:**
- **Serviceability ceiling calculator** — "You can borrow $287K more before lender X cuts you off. Here's how to structure around it."
- **Multi-entity portfolio dashboard** — trust allocations, LVR per entity, aggregated and separate views
- **Lender diversification tracker** — which lenders hold what, avoiding concentration risk
- **Dual-income property detection** — granny flat potential, dual-occ, house + studio
- **Subdivision feasibility** — basic lot size vs council overlay checks
- **BRRR pipeline tracker** — buy → reno → revalue → refinance → repeat, with timeline milestones
- **Bulk deal comparison** — compare 10+ deals side-by-side on all metrics
- **Cash-flow waterfall chart** per property and portfolio aggregate
- **Mentor Agent in "Peer" mode** — assumes knowledge, debates strategy, challenges assumptions
- **Negotiation Shadow** for active purchases — real-time coaching worth its weight

**Subscription tier:** PRO_SOURCER ($499/mo) — core audience
**Risk:** Hit serviceability wall and churn. Must provide creative structuring solutions to keep them engaged.

---

### Persona 6: THE TAX STRATEGIST
**Tagline:** "I earn big. Property is my tax shelter. Maximise my depreciation."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 35–60 |
| **Income** | $200K–$500K+ (high-income professional: surgeon, lawyer, executive, business owner) |
| **Savings** | $200K+ liquid, but tax-averse (wants capital deployed, not sitting in savings) |
| **Properties owned** | 1-5 (often underoptimised — bought on a mate's tip, not strategically) |
| **Debt** | Varies — may be under-leveraged relative to income |
| **Experience level** | NOVICE to INTERMEDIATE (high income ≠ high property knowledge) |
| **Risk tolerance** | MODERATE to GROWTH |
| **Primary goal** | TAX_MINIMISATION (negative gearing + depreciation) |
| **Entity** | COMPANY or FAMILY_TRUST (accountant-led) |
| **Borrowing power** | $1M–$3M+ (income is massive but they may not realise their capacity) |
| **Typical search** | New builds (max depreciation), established with renovation depreciation opportunity, inner-city units for set-and-forget |
| **Psychographic** | Time-poor, wants to deploy capital efficiently, decisions driven by accountant's advice, cares about after-tax returns not gross yield, may be cynical ("property people always oversell"), wants data not salesmanship |

**What they need from PIM:**
- **Tax impact calculator on EVERY deal** — "This property saves you $18,400/yr in tax via depreciation + negative gearing at your marginal rate of 47%"
- **New build vs established depreciation comparison** — Division 40 + Division 43 schedule preview
- **After-tax cash flow as the PRIMARY metric** (not pre-tax yield)
- **Marginal tax rate input** driving all calculations — deal cards show after-tax position
- **Bulk capital deployment planner** — "You have $500K. Here are 3 strategies deploying it across 2 properties optimised for tax"
- **Accountant-ready export** — CSV / PDF with depreciation schedule estimates, cash flow forecasts, entity structure
- **Stacker Agent in "Tax Mode"** — optimises for tax offset, not raw yield
- **Time-efficient UI** — fewer clicks, denser information, skip tutorials
- **Set-and-forget alerts** — "New property in your criteria with estimated $22K first-year depreciation"

**Subscription tier:** INVESTOR ($199/mo) or PRO_SOURCER ($499/mo) — price insensitive, value time
**Risk:** Won't engage with fluffy content. If they see "what is LVR?" they'll think the platform isn't for them. Needs a "Pro Mode" toggle.

---

### Persona 7: THE SMSF RETIREE
**Tagline:** "I want my super to work harder. Can I buy property through my SMSF?"

| Attribute | Detail |
|-----------|--------|
| **Age range** | 50–70 |
| **Income** | $80K–$150K salary (nearing retirement) + super contributions |
| **Super balance** | $300K–$1.5M in SMSF |
| **Properties owned** | 1-3 (PPOR, maybe 1 IP held personally) |
| **Debt** | Minimal personal debt, PPOR may be paid off |
| **Experience level** | NOVICE to INTERMEDIATE |
| **Risk tolerance** | CONSERVATIVE |
| **Primary goal** | RETIREMENT — income-producing asset inside super |
| **Entity** | SMSF (with corporate trustee), BARE_TRUST for lending (LRBA) |
| **Borrowing power** | Limited — SMSF lenders max 70% LVR, higher rates, strict rules |
| **Typical search** | $300K–$700K commercial or residential yielding 5%+ |
| **Psychographic** | Worried about running out of money in retirement, disillusioned with share market volatility, wants "real" assets, cautious about SMSF compliance, relies heavily on accountant/SMSF administrator |

**What they need from PIM:**
- **SMSF compliance checker on every deal** — "This property IS/IS NOT compliant for SMSF purchase" (single acquirable asset rule, can't be from related party, can't live in it)
- **LRBA (Limited Recourse Borrowing Arrangement) modelling** — 70% LVR, higher rates, limited lenders
- **"Can my SMSF afford this?" calculator** — contribution caps, cash reserves, rental income serviceability within the fund
- **SMSF vs Personal purchase comparison** — tax at 15% inside super vs 47% marginal rate outside
- **Pension phase income projections** — "If your SMSF buys this, in retirement it generates $32K/yr tax-free"
- **Compliance warnings** — "You CANNOT renovate this with SMSF funds. Repairs yes, improvements no."
- **Commercial property filter** — SMSF investors often prefer commercial (longer leases, higher yields, GST-free in super)
- **Mentor Agent in "Gentle Guide" mode** — patient, repeats concepts, links to ATO resources, never rushes
- **Accountant/administrator handoff report** — pre-formatted for SMSF professionals

**Subscription tier:** INVESTOR ($199/mo) — cautious spender, but the value is clear
**Risk:** Compliance fear = paralysis. Must build trust through accuracy and disclaimers. One wrong recommendation = lost forever.

---

### Persona 8: THE DEVELOPER / FLIPPER
**Tagline:** "I don't hold. I add value and sell. Show me the spread."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 30–55 |
| **Income** | Variable — $100K–$500K+ (project-based, lumpy) |
| **Savings** | $200K–$1M+ liquid (needs access to capital between projects) |
| **Properties owned** | 0-3 held long-term (actively flipping 1-3 at any time) |
| **Debt** | Project-specific: construction loans, mezzanine finance, JV structures |
| **Experience level** | ADVANCED to EXPERT |
| **Risk tolerance** | AGGRESSIVE to SPECULATIVE |
| **Primary goal** | SUBDIVISION or CAPITAL_GROWTH (via forced equity / value-add) |
| **Entity** | PROJECT-SPECIFIC SPV: unit trust per project, or company |
| **Borrowing power** | N/A traditional sense — uses construction finance, JV capital, private lending |
| **Typical search** | Knockdowns on large land, properties with subdivision STCA, dual-occ potential, unrenovated in gentrifying suburbs |
| **Psychographic** | Thinks in feasibility studies not yield, knows council planning overlays, has builder relationships, measures success in IRR not rental yield, time is money — needs fast data |

**What they need from PIM:**
- **Development feasibility calculator** — land cost + build cost + holding costs + selling costs vs GRV (Gross Realisation Value)
- **Subdivision potential detector** — lot size vs zone minimum, overlay checks (Heritage, VPO, SLO, LSIO)
- **Council zone data** — NRZ, GRZ, RGZ, MUZ, C1Z, C2Z for every property, with what's permissible
- **Renovation ROI estimator** — "Spend $80K on kitchen/bathroom/landscaping → add $150K to value"
- **Comparable SOLD prices for renovated vs unrenovated** in the same street/suburb
- **Construction timeline modelling** — permit (12-16 weeks), build (6-12 months), sell (4-8 weeks)
- **Joint venture structure templates** — JV vs unit trust vs company for each project
- **IRR calculator** (not just yield) — time-weighted return accounting for capital deployed duration
- **Bulk pipeline scanning** — needs 50+ properties analysed per batch to find 1-2 viable projects
- **"Spread" metric** prominently displayed — buy price vs estimated after-repair / after-build value

**Subscription tier:** PRO_SOURCER ($499/mo) or THE_CLOSER ($2,500/deal)
**Risk:** Will use PIM as a deal-sourcing funnel and churn between projects. Must show ongoing pipeline value.

---

### Persona 9: THE PROFESSIONAL SOURCER / BUYER'S AGENT
**Tagline:** "I find and buy properties for OTHER PEOPLE for a living."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 28–55 |
| **Income** | $150K–$500K+ (commission/fee-based: $10K–$25K per deal) |
| **Client count** | Managing 3-15 active client briefs simultaneously |
| **Properties owned** | 2-10+ personally |
| **Experience level** | EXPERT |
| **Risk tolerance** | Variable — matches client's tolerance per brief |
| **Primary goal** | N/A for self — executing CLIENT goals (all 9 InvestmentGoal types) |
| **Entity** | Company (ABN for business), clients' entities vary |
| **Typical search** | Whatever the client needs — must support 15 simultaneous search profiles |
| **Psychographic** | Speed is money, reputation is everything, needs to show clients they found the BEST deal (quantified), competes with other buyers' agents, values data as competitive advantage |

**What they need from PIM:**
- **Multi-profile workspace** — switch between client briefs instantly, each with its own filters/preferences/budget
- **Client-facing reports** — branded/white-label PDF exports showing deal analysis, comps, and recommendations
- **Bulk pipeline processing** — analyse 100+ properties against a brief in one run
- **Competitive market intelligence** — days on market trends, vendor discount averages, auction clearance rates by suburb
- **Shortlist management** — for each client: longlist → shortlist → inspected → offered → purchased funnel
- **Due Diligence Bot** on demand — Section 32 analysis for every serious candidate
- **Negotiation Shadow** for live offers — their competitive edge
- **CRM-lite features** — client notes, next actions, follow-up reminders
- **API access** for integration with their own CRM / deal pipeline tools
- **Automated morning brief per client** — "3 new listings match Sarah's brief. 1 is a Golden Opportunity."
- **White-label option** — co-brand reports with their agency logo

**Subscription tier:** PRO_SOURCER ($499/mo) minimum, most will be THE_CLOSER ($2,500/deal)
**Risk:** If pipeline quality drops, they can't justify the fee to clients. Must be consistently excellent.

---

### Persona 10: THE ENTERPRISE / SYNDICATE OPERATOR
**Tagline:** "I raise capital, syndicate deals, and operate at scale. I need institutional-grade data."

| Attribute | Detail |
|-----------|--------|
| **Age range** | 35–65 |
| **Income** | $300K–$2M+ (fund management fees, carried interest, development profits) |
| **AUM (Assets Under Management)** | $5M–$100M+ |
| **Properties owned** | 10-100+ across multiple entities and funds |
| **Debt** | $5M–$50M+ (commercial lending, private debt, fund-level leverage) |
| **Experience level** | EXPERT |
| **Risk tolerance** | Full spectrum — managed per fund/client mandate |
| **Primary goal** | All goals simultaneously across different mandates |
| **Entity** | UNIT_TRUST (per fund), COMPANY (management), PARTNERSHIP (GPs) |
| **Typical search** | Block purchases, distressed portfolios, commercial, development sites, portfolio-level optimisation |
| **Psychographic** | Data-driven, compliance-conscious (AFSL/ACL requirements), competes with REITs and institutional funds, needs audit trail, values speed of execution and information arbitrage |

**What they need from PIM:**
- **Portfolio analytics dashboard** — aggregate all holdings, entity-level breakdowns, fund-level P&L
- **Investor reporting engine** — quarterly performance reports for LP investors
- **Bulk acquisition pipeline** — source 500+ properties, filter to 20, deep-dive 5, acquire 2
- **Risk modelling** — portfolio-level stress tests (rate rise +2%, vacancy spike, market correction)
- **Market cycle indicators** — VIC lending data, auction clearance, listing volume, rent growth trends
- **Capital allocation optimiser** — "Fund A should buy 3 regionals, Fund B should focus on 1 development"
- **Compliance audit trail** — every recommendation, analysis, and score timestamped and exportable
- **API-first access** — all data available programmatically for their BI tools
- **Custom agent training** — ability to tune agent behavior for fund-specific mandates
- **Multi-user access** — team members with role-based permissions
- **Negotiation Shadow at scale** — concurrent deal coaching across multiple active negotiations

**Subscription tier:** ENTERPRISE (custom pricing — $2K–$10K/mo) — a tier above THE_CLOSER
**Risk:** Will only stay if PIM's data quality matches or exceeds CoreLogic/PropTrack. Must be defensible.

---

### PERSONA IDENTIFICATION — ONBOARDING FLOW

The Profiler Agent identifies the user's persona through a 5-question progressive onboarding:

```
Q1: "How many properties do you currently own?"
    → 0 → Likely Persona 1 (Dreamer)
    → 1 → Likely Persona 2 (Stepping Up) or 3 (Accidental)
    → 2-3 → Likely Persona 4 (Equity Unlocked)
    → 4-8 → Likely Persona 5 (Builder)
    → 9+ → Likely Persona 9 or 10

Q2: "What brings you to Property Insights today?"
    → "I want to buy my first home" → Persona 1
    → "I want to start investing in property" → Persona 2
    → "I inherited / kept a property and want to optimise" → Persona 3
    → "I want to grow my portfolio faster" → Persona 4/5
    → "I want to reduce my tax bill" → Persona 6
    → "I want to buy through my SMSF" → Persona 7
    → "I'm looking for renovation/development projects" → Persona 8
    → "I source properties for clients" → Persona 9
    → "I manage funds / syndicates" → Persona 10

Q3: [Income qualifier] "Roughly what's your household income range?"
    → Refines within persona bucket

Q4: [Urgency] "How soon are you looking to take action?"
    → Adjusts coaching aggressiveness and notification frequency

Q5: [Experience qualifier] "Have you worked with a mortgage broker?"
    → Determines knowledge depth and jargon comfort
```

### PERSONA → SUBSCRIPTION TIER MAPPING

| Persona | Natural Tier | Upgrade Trigger | Lifetime Value (Est.) |
|---------|-------------|-----------------|----------------------|
| 1. First Home Dreamer | EXPLORER (Free) | Finds dream property, needs analysis | $0 → $199×3 months |
| 2. Stepping Up | INVESTOR ($199) | Buys first IP, wants next | $199×12 = $2,388/yr |
| 3. Accidental Landlord | EXPLORER → INVESTOR | Sees missed rental income | $199×6 = $1,194/yr |
| 4. Equity Unlocked | INVESTOR → PRO_SOURCER | Pipeline velocity needed | $199×6 + $499×6 = $4,188/yr |
| 5. Portfolio Builder | PRO_SOURCER | Stays for tools, adds Nego Shadow | $499×12 + $500×6 = $8,988/yr |
| 6. Tax Strategist | INVESTOR | Stays for tax calc, bulk deploy | $199×12 = $2,388/yr |
| 7. SMSF Retiree | INVESTOR | Stays for compliance checking | $199×12 = $2,388/yr |
| 8. Developer/Flipper | PRO_SOURCER / CLOSER | Per-deal on active projects | $499×6 + $2,500×3 = $10,494/yr |
| 9. Professional Sourcer | THE_CLOSER | Per-deal with clients | $2,500×12 = $30,000/yr |
| 10. Enterprise/Syndicate | ENTERPRISE (custom) | Data quality + API | $24K–$120K/yr |

### PERSONA → AGENT BEHAVIOUR MATRIX

| Agent | Personas 1-3 (Learners) | Personas 4-6 (Growers) | Personas 7-8 (Specialists) | Personas 9-10 (Professionals) |
|-------|------------------------|------------------------|---------------------------|------------------------------|
| **Scout** | Simplified results, bargain badge only | Full metrics, yield + growth overlay | SMSF compliance flag / dev potential flag | Bulk pipeline, API-accessible, custom alerts |
| **Analyst** | Plain English summary, 3 key numbers | Full ROI model, depreciation estimate | SMSF tax calc / feasibility study | Portfolio-level aggregation, stress testing |
| **Closer** | Guided offer wizard, templates only | Flexible offer with strategy | SMSF-compliant offer / subject-to-DA offer | Multi-offer pipeline, white-label |
| **Profiler** | Hand-holding, 1 question at a time | Efficient, 3-5 questions | Specialist path (SMSF rules / reno budget) | Multi-profile, client-brief mode |
| **Stacker** | "Here's what you can afford" | IO vs PI, equity release scenarios | LRBA + SMSF structuring / JV + construction | Multi-deal structuring, capital allocation |
| **Mentor** | Teacher tone, explains everything | Peer tone, debates strategy | Specialist coach, compliance-aware | Portfolio advisor, fund-level strategy |
| **Chatbot** | Beginner market news, no jargon | Market analysis with depth | Specialist news (planning regs, SMSF rules) | Institutional-grade market intelligence |
| **Due Diligence** | "Here's what to watch for" (educational) | Full S32 analysis | SMSF-specific clause flags | Bulk S32 processing, risk matrix |
| **Negotiation Shadow** | Not available (too early) | Available as add-on | Active coaching for complex deals | Multi-concurrent deal support |

### PERSONA → UI ADAPTATION

| UI Element | Beginners (1-3) | Growers (4-6) | Specialists (7-8) | Pros (9-10) |
|-----------|-----------------|---------------|-------------------|-------------|
| **Dashboard default tab** | Suburb Explorer | Deal Pipeline | Specialist Dashboard | Portfolio Command Centre |
| **Metric density** | Low: 3-5 KPIs | Medium: 8-12 KPIs | Medium-High: 10-15 KPIs | Maximum: 20+ KPIs |
| **Jargon level** | Plain English, tooltips everywhere | Industry terms, definitions on hover | Specialist terminology | Institutional language |
| **Default sort** | Price (low to high) | Bargain Score | Specialist metric (SMSF yield / dev spread) | Custom multi-sort |
| **CTA primary** | "Learn More" / "Save" | "Analyse" / "Generate Offer" | "Check Compliance" / "Run Feasibility" | "Add to Pipeline" / "Export" |
| **Tutorial popups** | Yes, progressive | Optional, dismissible | Specialist tips only | None — Pro Mode |
| **Notification frequency** | 1/day max | 3/day | As matches appear | Real-time stream |
| **Export format** | None (save in-app) | PDF summary | PDF + CSV | API + JSON + branded PDF |

---

## PERSISTENCE — SQLite + WAL Mode

### Tables
| Table | Purpose |
|-------|---------|
| `properties` | JSON blob per property (id as PK) |
| `deals` | JSON blob per deal |
| `offers` | JSON blob per offer |
| `scout_runs` | Scout run log (timestamp, new_properties, new_deals, duration_ms, notes) |

### Functions
- `init_db()` — Creates tables if not exist, enables WAL mode
- `save_properties_bulk(list)`, `save_deals_bulk(list)`, `save_offer(offer)` — Persist
- `save_property(prop)`, `save_deal(deal)` — Single upsert
- `load_all_properties()`, `load_all_deals()`, `load_all_offers()` — Load all as dict
- `delete_property(id)`, `delete_deal(id)`, `delete_offer(id)` — Remove record
- `count_properties()`, `count_deals()`, `count_offers()` — Row counts
- `db_stats()` — Row counts, DB size, path
- `log_scout_run()`, `get_scout_history(limit)` — Scout audit trail

---

## AUTO-SCOUT — Background Task

Runs every 15–30 minutes via `asyncio.create_task()` on server startup:
1. Picks 2–5 random VIC suburbs from the 134-suburb database
2. Generates synthetic properties priced around suburb median (±8–22% discount for value-add)
3. Runs Analyst Agent to create deals with Bargain Scores
4. Persists to SQLite
5. Logs run to scout_runs

---

## STAMP DUTY CALCULATOR — All 8 AU States

Marginal bracket system for each state. VIC example:
- $0–$25K: 1.4%
- $25K–$130K: 2.4% + $350 base
- $130K–$960K: 6.0% + $2,870 base
- $960K+: 5.5% of excess above $960K

Full bracket tables for NSW, VIC, QLD, SA, WA, TAS, NT, ACT.

---

## MARKETING LANDING PAGE

### Sections
1. **Hero:** "The Bloomberg Terminal for Australian Property" — gradient text, CTA to launch terminal
2. **6 Agent Cards:** Scout, Analyst, Closer, Concierge, Due Diligence, Negotiation Shadow
3. **ROI Comparison:** PIA ($2,388/yr) vs Buyer's Agent ($12K–$30K/deal) vs Junior Analyst ($60K+/yr)
4. **4-Tier Pricing:** Explorer (Free) → Investor ($199/mo) → Pro Sourcer ($499/mo) → The Closer ($2,500/deal) + 3 premium add-ons
5. **CTA:** "Stop Overpaying for Property Intelligence"
6. **Footer:** Company info, ABN, disclaimer

---

## HONESTY & INTEGRITY POLICIES

1. **No Fake Photos:** Property cards show CSS gradient placeholders with type-specific emoji icons (🏠 house, 🏢 apartment, etc.) — never stock photos
2. **SIMULATED LISTING Badge:** All properties are marked as simulated data for demonstration
3. **"Verify on Real Portals" Links:** Every property includes clickable links to Domain.com.au and Realestate.com.au search pages for the actual suburb
4. **Legal Disclaimers:** All offers marked "Commercial Strategy Draft — not legal advice"; subscription terms and data disclaimers on landing page
5. **Accurate Data:** All suburb medians, infrastructure projects, rents, and growth rates verified against real market data for Victoria

---

## CONFIGURATION & DEPENDENCIES

### Python Dependencies
fastapi, uvicorn, pydantic, pydantic-settings, httpx, structlog, python-dotenv, anthropic, beautifulsoup4, lxml, selectolax, playwright, pandas, numpy, langchain, langchain-anthropic, langchain-community, supabase, pgvector, twilio, sqlalchemy, alembic, asyncpg, apscheduler, celery, rich, jinja2, pytest, pytest-asyncio, pytest-cov, black, ruff, mypy

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=           # Optional — Ollama is default
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
USE_OLLAMA=true
APP_ENV=development
APP_PORT=8001
SECRET_KEY=change-me
```

### Start Command
```bash
PYTHONPATH=. python -m uvicorn nexusprop.api.main:app --port 8001 --host 127.0.0.1
```

---

## GROWTH TRAJECTORY

The application is designed to grow via:
1. **QA Self-Governance:** QA Agent continuously scores and improves other agents through skill templates
2. **Auto-Scout:** Background task constantly discovers new properties
3. **Chatbot News:** Real-time market intelligence keeps users engaged
4. **Progressive Profiling:** Each interaction builds a richer investor profile
5. **Pipeline Orchestration:** Full-chain automation from scouting to closing
6. **Subscription Monetisation:** Free tier → $199/mo → $499/mo → $2,500/deal + premium add-ons

---

*This is a complete, production-ready specification for rebuilding Property Insights Melbourne from scratch. Every model, endpoint, agent, UI element, and business rule is documented above.*
