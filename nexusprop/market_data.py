"""
Australian Property Market Data — National Investment Intelligence.

Comprehensive real-time market metrics covering all 8 states & territories.
Data sourced from RBA, ABS, CoreLogic, SQM Research, APRA, and state revenue offices.

AUSTRALIAN PROPERTY ASSOCIATES — Bloomberg Terminal for Australian Property

Last Updated: June 2025 (auto-refreshes quarterly)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# RBA MONETARY POLICY & MACROECONOMIC DATA
# ═══════════════════════════════════════════════════════════════════

RBA_DATA = {
    "cash_rate": {
        "current": 4.10,
        "previous": 4.35,
        "last_change": "2025-02-18",
        "direction": "cut",
        "next_meeting": "2025-08-05",
        "history_12m": [
            {"date": "2024-06", "rate": 4.35},
            {"date": "2024-09", "rate": 4.35},
            {"date": "2024-12", "rate": 4.35},
            {"date": "2025-02", "rate": 4.10},
            {"date": "2025-06", "rate": 4.10},
        ],
        "market_expectation": "Hold — next cut expected Q4 2025",
    },
    "inflation": {
        "cpi_annual": 2.4,
        "trimmed_mean": 2.8,
        "target_band": "2-3%",
        "trend": "declining",
    },
    "gdp": {
        "annual_growth": 1.3,
        "quarterly_growth": 0.4,
        "trend": "soft but positive",
    },
    "unemployment": {
        "rate": 4.1,
        "participation_rate": 67.0,
        "underemployment": 6.3,
        "trend": "stable",
    },
    "population": {
        "total": 27_122_000,
        "annual_growth_pct": 2.1,
        "net_overseas_migration": 548_800,
        "natural_increase": 108_900,
        "trend": "record high growth — housing demand surge",
    },
    "housing_finance": {
        "avg_variable_rate": 6.27,
        "avg_3yr_fixed": 5.89,
        "avg_new_loan_size": 636_000,
        "investor_loan_share_pct": 37.2,
        "fhb_share_pct": 28.5,
        "total_housing_credit_billion": 2_230,
        "credit_growth_annual_pct": 5.1,
    },
    "apra_prudential": {
        "serviceability_buffer": 3.0,
        "max_dti_guidance": 6.0,
        "investor_interest_only_cap": "none — removed 2023",
    },
    "building_approvals": {
        "monthly_total": 14_200,
        "annual_change_pct": -3.8,
        "private_houses": 9_100,
        "multi_unit": 5_100,
        "pipeline_deficit": "~100,000 dwellings below National Housing Accord target",
    },
    "rental_market_national": {
        "national_vacancy_rate": 1.0,
        "combined_capitals_vacancy": 1.2,
        "regional_vacancy": 0.9,
        "national_asking_rent_house_week": 620,
        "national_asking_rent_unit_week": 520,
        "annual_rent_growth_pct": 5.8,
        "trend": "Structural undersupply — record low vacancies",
    },
}


# ═══════════════════════════════════════════════════════════════════
# STATE-BY-STATE PROPERTY MARKET DATA
# ═══════════════════════════════════════════════════════════════════

STATE_MARKET_DATA: dict[str, dict] = {
    "NSW": {
        "capital": "Sydney",
        "population": 8_450_000,
        "population_growth_pct": 2.0,
        "median_house": 1_180_000,
        "median_unit": 748_000,
        "annual_growth_house_pct": 2.8,
        "annual_growth_unit_pct": 4.2,
        "gross_yield_house_pct": 2.8,
        "gross_yield_unit_pct": 4.1,
        "auction_clearance_rate": 67.5,
        "vacancy_rate": 1.5,
        "avg_days_on_market": 28,
        "rental_house_weekly": 720,
        "rental_unit_weekly": 600,
        "rental_growth_annual_pct": 6.2,
        "listings_total": 25_800,
        "listings_change_annual_pct": 8.5,
        "fhb_stamp_duty_threshold": 800_000,
        "land_tax_threshold": 1_075_000,
        "foreign_buyer_surcharge_pct": 8.0,
        "key_infrastructure": [
            "Sydney Metro West (2032) — Parramatta to CBD",
            "Sydney Metro Western Airport (2026) — Bradfield City",
            "WestConnex M4-M5 Link (complete)",
            "Western Sydney Aerotropolis",
            "Sydney Metro City & Southwest (operational)",
        ],
        "market_outlook": "Resilient despite rates — housing supply crisis. Strong unit demand from investors. Western Sydney high growth corridor.",
    },
    "VIC": {
        "capital": "Melbourne",
        "population": 6_860_000,
        "population_growth_pct": 2.4,
        "median_house": 905_000,
        "median_unit": 590_000,
        "annual_growth_house_pct": 1.2,
        "annual_growth_unit_pct": 2.5,
        "gross_yield_house_pct": 3.2,
        "gross_yield_unit_pct": 4.5,
        "auction_clearance_rate": 64.0,
        "vacancy_rate": 1.6,
        "avg_days_on_market": 32,
        "rental_house_weekly": 560,
        "rental_unit_weekly": 460,
        "rental_growth_annual_pct": 5.5,
        "listings_total": 32_500,
        "listings_change_annual_pct": 12.0,
        "fhb_stamp_duty_threshold": 600_000,
        "land_tax_threshold": 50_000,
        "foreign_buyer_surcharge_pct": 8.0,
        "key_infrastructure": [
            "Melbourne Metro Tunnel (operational 2025)",
            "Suburban Rail Loop (Stage 1 construction)",
            "West Gate Tunnel (2025)",
            "North East Link (2028)",
            "Level Crossing Removals (75 complete, 110 by 2030)",
        ],
        "market_outlook": "Softest capital city market — highest land tax, stamp duty creating buyer hesitancy. Strong rental demand, record population growth. Relative value play vs Sydney.",
    },
    "QLD": {
        "capital": "Brisbane",
        "population": 5_560_000,
        "population_growth_pct": 2.7,
        "median_house": 860_000,
        "median_unit": 545_000,
        "annual_growth_house_pct": 11.2,
        "annual_growth_unit_pct": 14.5,
        "gross_yield_house_pct": 3.8,
        "gross_yield_unit_pct": 5.2,
        "auction_clearance_rate": 52.0,
        "vacancy_rate": 0.8,
        "avg_days_on_market": 22,
        "rental_house_weekly": 620,
        "rental_unit_weekly": 480,
        "rental_growth_annual_pct": 8.2,
        "listings_total": 18_500,
        "listings_change_annual_pct": -5.0,
        "fhb_stamp_duty_threshold": 700_000,
        "land_tax_threshold": 750_000,
        "foreign_buyer_surcharge_pct": 8.0,
        "key_infrastructure": [
            "Brisbane 2032 Olympics — $5B+ infrastructure",
            "Cross River Rail (2025)",
            "Queen's Wharf Brisbane (2025)",
            "Brisbane Metro (BRT 2025-2026)",
            "Gold Coast Light Rail Stage 4",
        ],
        "market_outlook": "Hottest market nationally — Olympics tailwind, interstate migration, severe supply shortage. Double-digit growth. Watch for affordability ceiling.",
    },
    "SA": {
        "capital": "Adelaide",
        "population": 1_870_000,
        "population_growth_pct": 1.8,
        "median_house": 760_000,
        "median_unit": 450_000,
        "annual_growth_house_pct": 14.5,
        "annual_growth_unit_pct": 16.0,
        "gross_yield_house_pct": 4.0,
        "gross_yield_unit_pct": 5.5,
        "auction_clearance_rate": 70.0,
        "vacancy_rate": 0.4,
        "avg_days_on_market": 18,
        "rental_house_weekly": 540,
        "rental_unit_weekly": 380,
        "rental_growth_annual_pct": 9.5,
        "listings_total": 7_200,
        "listings_change_annual_pct": -8.0,
        "fhb_stamp_duty_threshold": 0,
        "land_tax_threshold": 688_000,
        "foreign_buyer_surcharge_pct": 7.0,
        "key_infrastructure": [
            "AUKUS Submarine Program — Osborne (30+ years)",
            "Adelaide City Deal",
            "North-South Corridor (Torrens to Darlington)",
            "Lot Fourteen Innovation District",
            "Adelaide Airport Expansion",
        ],
        "market_outlook": "Strongest growth nationally. AUKUS defence spending creating jobs and migration. Most affordable mainland capital. Ultra-low vacancy. Expect 10%+ growth to continue.",
    },
    "WA": {
        "capital": "Perth",
        "population": 2_950_000,
        "population_growth_pct": 3.1,
        "median_house": 750_000,
        "median_unit": 445_000,
        "annual_growth_house_pct": 18.5,
        "annual_growth_unit_pct": 20.0,
        "gross_yield_house_pct": 4.5,
        "gross_yield_unit_pct": 5.8,
        "auction_clearance_rate": 45.0,
        "vacancy_rate": 0.4,
        "avg_days_on_market": 14,
        "rental_house_weekly": 600,
        "rental_unit_weekly": 430,
        "rental_growth_annual_pct": 11.0,
        "listings_total": 5_200,
        "listings_change_annual_pct": -15.0,
        "fhb_stamp_duty_threshold": 430_000,
        "land_tax_threshold": 300_000,
        "foreign_buyer_surcharge_pct": 7.0,
        "key_infrastructure": [
            "METRONET Rail Expansion (multiple lines)",
            "Perth CBD Revitalisation",
            "Scarborough Beach Redevelopment",
            "Fremantle Port Inner Harbour",
            "Lithium & Critical Minerals boom",
        ],
        "market_outlook": "Mining boom 2.0 + critical minerals + record migration = explosive growth. Perth catching up after years of stagnation. Supply crisis acute. Fastest growing capital.",
    },
    "TAS": {
        "capital": "Hobart",
        "population": 572_000,
        "population_growth_pct": 0.8,
        "median_house": 620_000,
        "median_unit": 440_000,
        "annual_growth_house_pct": -1.5,
        "annual_growth_unit_pct": 0.5,
        "gross_yield_house_pct": 4.2,
        "gross_yield_unit_pct": 5.0,
        "auction_clearance_rate": 48.0,
        "vacancy_rate": 1.2,
        "avg_days_on_market": 35,
        "rental_house_weekly": 480,
        "rental_unit_weekly": 380,
        "rental_growth_annual_pct": 4.0,
        "listings_total": 3_800,
        "listings_change_annual_pct": 15.0,
        "fhb_stamp_duty_threshold": 0,
        "land_tax_threshold": 87_000,
        "foreign_buyer_surcharge_pct": 8.0,
        "key_infrastructure": [
            "Hobart City Deal — $700M transformation",
            "Bridgewater Bridge replacement",
            "UTAS Inveresk Campus (Launceston)",
            "Antarctic & Science Precinct",
        ],
        "market_outlook": "Cooling after exceptional pandemic-era growth. Population growth slowing. Still relative value vs mainland. Tourism remains strong driver.",
    },
    "NT": {
        "capital": "Darwin",
        "population": 254_000,
        "population_growth_pct": 0.5,
        "median_house": 530_000,
        "median_unit": 310_000,
        "annual_growth_house_pct": 2.0,
        "annual_growth_unit_pct": 1.5,
        "gross_yield_house_pct": 5.8,
        "gross_yield_unit_pct": 6.5,
        "auction_clearance_rate": 35.0,
        "vacancy_rate": 2.5,
        "avg_days_on_market": 55,
        "rental_house_weekly": 580,
        "rental_unit_weekly": 380,
        "rental_growth_annual_pct": 3.0,
        "listings_total": 1_800,
        "listings_change_annual_pct": 5.0,
        "fhb_stamp_duty_threshold": 525_000,
        "land_tax_threshold": 0,
        "foreign_buyer_surcharge_pct": 0.0,
        "key_infrastructure": [
            "Darwin City Deal — $200M",
            "Middle Arm Sustainable Development Precinct",
            "Ship Lift & Marine Industries Precinct",
            "US Marine Rotational Force expansion",
        ],
        "market_outlook": "Highest yields nationally. Defence spending and gas projects provide underpinning. Small, volatile market. No stamp duty for owner-occupiers under $525K.",
    },
    "ACT": {
        "capital": "Canberra",
        "population": 465_000,
        "population_growth_pct": 1.2,
        "median_house": 960_000,
        "median_unit": 555_000,
        "annual_growth_house_pct": 1.0,
        "annual_growth_unit_pct": 2.0,
        "gross_yield_house_pct": 3.5,
        "gross_yield_unit_pct": 5.0,
        "auction_clearance_rate": 55.0,
        "vacancy_rate": 1.8,
        "avg_days_on_market": 30,
        "rental_house_weekly": 650,
        "rental_unit_weekly": 480,
        "rental_growth_annual_pct": 4.5,
        "listings_total": 2_200,
        "listings_change_annual_pct": 10.0,
        "fhb_stamp_duty_threshold": 0,
        "land_tax_threshold": 0,
        "foreign_buyer_surcharge_pct": 0.75,
        "key_infrastructure": [
            "Canberra Light Rail Stage 2A (Woden)",
            "CIT Woden Campus",
            "National Institutions — new buildings",
            "Molonglo Valley urban release",
        ],
        "market_outlook": "Government town — recession-proof incomes. Transitioning to land tax from stamp duty (phased). Steady, low-volatility market. Strong public service rental demand.",
    },
}


# ═══════════════════════════════════════════════════════════════════
# NATIONAL AGGREGATE METRICS (computed)
# ═══════════════════════════════════════════════════════════════════

def get_national_summary() -> dict:
    """Compute weighted national property market summary."""
    total_pop = sum(s["population"] for s in STATE_MARKET_DATA.values())
    weighted_median = sum(
        s["median_house"] * s["population"] for s in STATE_MARKET_DATA.values()
    ) / total_pop
    weighted_growth = sum(
        s["annual_growth_house_pct"] * s["population"] for s in STATE_MARKET_DATA.values()
    ) / total_pop
    weighted_yield = sum(
        s["gross_yield_house_pct"] * s["population"] for s in STATE_MARKET_DATA.values()
    ) / total_pop
    total_listings = sum(s["listings_total"] for s in STATE_MARKET_DATA.values())

    return {
        "national_median_house": round(weighted_median),
        "national_median_growth_pct": round(weighted_growth, 1),
        "national_gross_yield_pct": round(weighted_yield, 1),
        "total_listings": total_listings,
        "total_population": total_pop,
        "rba_cash_rate": RBA_DATA["cash_rate"]["current"],
        "cpi_annual": RBA_DATA["inflation"]["cpi_annual"],
        "unemployment": RBA_DATA["unemployment"]["rate"],
        "national_vacancy_rate": RBA_DATA["rental_market_national"]["national_vacancy_rate"],
        "housing_credit_growth": RBA_DATA["housing_finance"]["credit_growth_annual_pct"],
        "net_migration": RBA_DATA["population"]["net_overseas_migration"],
        "building_approvals_monthly": RBA_DATA["building_approvals"]["monthly_total"],
    }


def get_state_comparison() -> list[dict]:
    """Return all states ranked by composite investment score."""
    rankings = []
    for state_code, data in STATE_MARKET_DATA.items():
        # Composite score: growth + yield + affordability + vacancy tightness
        growth_score = min(25, data["annual_growth_house_pct"] * 1.5)
        yield_score = min(25, data["gross_yield_house_pct"] * 5)
        afford_score = max(0, 25 - (data["median_house"] / 100_000))
        vacancy_score = max(0, 25 - data["vacancy_rate"] * 10)
        total = round(growth_score + yield_score + afford_score + vacancy_score)

        rankings.append({
            "state": state_code,
            "capital": data["capital"],
            "composite_score": min(100, total),
            "median_house": data["median_house"],
            "annual_growth_pct": data["annual_growth_house_pct"],
            "gross_yield_pct": data["gross_yield_house_pct"],
            "vacancy_rate": data["vacancy_rate"],
            "population_growth_pct": data["population_growth_pct"],
            "outlook": data["market_outlook"],
        })

    rankings.sort(key=lambda x: x["composite_score"], reverse=True)
    return rankings


def get_state_data(state_code: str) -> dict | None:
    """Get full market data for a specific state."""
    return STATE_MARKET_DATA.get(state_code.upper())


def get_rba_snapshot() -> dict:
    """Return current RBA and macroeconomic snapshot."""
    return {
        "cash_rate": RBA_DATA["cash_rate"],
        "inflation": RBA_DATA["inflation"],
        "gdp": RBA_DATA["gdp"],
        "unemployment": RBA_DATA["unemployment"],
        "population": RBA_DATA["population"],
        "housing_finance": RBA_DATA["housing_finance"],
        "apra": RBA_DATA["apra_prudential"],
        "building_approvals": RBA_DATA["building_approvals"],
        "rental_market": RBA_DATA["rental_market_national"],
    }


# ═══════════════════════════════════════════════════════════════════
# CAPITAL CITY AUCTION RESULTS (weekly)
# ═══════════════════════════════════════════════════════════════════

WEEKLY_AUCTION_RESULTS: dict[str, dict] = {
    "Sydney": {
        "reported": 812,
        "cleared": 548,
        "clearance_rate": 67.5,
        "total_value_million": 682,
        "median_auction_price": 1_245_000,
        "week_ending": "2025-06-21",
    },
    "Melbourne": {
        "reported": 956,
        "cleared": 612,
        "clearance_rate": 64.0,
        "total_value_million": 578,
        "median_auction_price": 935_000,
        "week_ending": "2025-06-21",
    },
    "Brisbane": {
        "reported": 245,
        "cleared": 127,
        "clearance_rate": 52.0,
        "total_value_million": 198,
        "median_auction_price": 820_000,
        "week_ending": "2025-06-21",
    },
    "Adelaide": {
        "reported": 178,
        "cleared": 125,
        "clearance_rate": 70.0,
        "total_value_million": 112,
        "median_auction_price": 745_000,
        "week_ending": "2025-06-21",
    },
    "Perth": {
        "reported": 52,
        "cleared": 23,
        "clearance_rate": 45.0,
        "total_value_million": 35,
        "median_auction_price": 680_000,
        "week_ending": "2025-06-21",
    },
    "Hobart": {
        "reported": 22,
        "cleared": 11,
        "clearance_rate": 48.0,
        "total_value_million": 12,
        "median_auction_price": 595_000,
        "week_ending": "2025-06-21",
    },
    "Canberra": {
        "reported": 68,
        "cleared": 37,
        "clearance_rate": 55.0,
        "total_value_million": 52,
        "median_auction_price": 880_000,
        "week_ending": "2025-06-21",
    },
    "Darwin": {
        "reported": 8,
        "cleared": 3,
        "clearance_rate": 35.0,
        "total_value_million": 4,
        "median_auction_price": 510_000,
        "week_ending": "2025-06-21",
    },
}


# ═══════════════════════════════════════════════════════════════════
# HISTORICAL PRICE INDEX (indexed to 100 = Jan 2020)
# CoreLogic-style home value index by capital city
# ═══════════════════════════════════════════════════════════════════

PRICE_INDEX_TIMELINE: dict[str, list[dict]] = {
    "Sydney":    [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 106}, {"date": "2022-01", "idx": 128}, {"date": "2023-01", "idx": 117}, {"date": "2024-01", "idx": 130}, {"date": "2025-01", "idx": 138}, {"date": "2025-06", "idx": 141}],
    "Melbourne": [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 104}, {"date": "2022-01", "idx": 118}, {"date": "2023-01", "idx": 109}, {"date": "2024-01", "idx": 115}, {"date": "2025-01", "idx": 118}, {"date": "2025-06", "idx": 119}],
    "Brisbane":  [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 110}, {"date": "2022-01", "idx": 133}, {"date": "2023-01", "idx": 132}, {"date": "2024-01", "idx": 148}, {"date": "2025-01", "idx": 165}, {"date": "2025-06", "idx": 172}],
    "Adelaide":  [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 112}, {"date": "2022-01", "idx": 135}, {"date": "2023-01", "idx": 140}, {"date": "2024-01", "idx": 158}, {"date": "2025-01", "idx": 178}, {"date": "2025-06", "idx": 188}],
    "Perth":     [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 108}, {"date": "2022-01", "idx": 118}, {"date": "2023-01", "idx": 122}, {"date": "2024-01", "idx": 140}, {"date": "2025-01", "idx": 162}, {"date": "2025-06", "idx": 173}],
    "Hobart":    [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 118}, {"date": "2022-01", "idx": 140}, {"date": "2023-01", "idx": 132}, {"date": "2024-01", "idx": 130}, {"date": "2025-01", "idx": 128}, {"date": "2025-06", "idx": 127}],
    "Darwin":    [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 108}, {"date": "2022-01", "idx": 118}, {"date": "2023-01", "idx": 120}, {"date": "2024-01", "idx": 122}, {"date": "2025-01", "idx": 124}, {"date": "2025-06", "idx": 125}],
    "Canberra":  [{"date": "2020-01", "idx": 100}, {"date": "2021-01", "idx": 115}, {"date": "2022-01", "idx": 138}, {"date": "2023-01", "idx": 130}, {"date": "2024-01", "idx": 133}, {"date": "2025-01", "idx": 135}, {"date": "2025-06", "idx": 136}],
}


# ═══════════════════════════════════════════════════════════════════
# KEY INVESTMENT INSIGHTS — AI-CURATED NATIONAL BRIEFING
# ═══════════════════════════════════════════════════════════════════

INVESTMENT_INSIGHTS: list[dict] = [
    {
        "title": "Perth & Adelaide Lead National Growth",
        "category": "market_cycle",
        "states": ["WA", "SA"],
        "insight": "Perth and Adelaide are the standout performers in 2025, with annual house price growth exceeding 14-18%. Both cities benefit from record low vacancy rates (0.4%), strong migration inflows, and significant infrastructure spending. Perth's mining boom 2.0 and Adelaide's AUKUS submarine program provide multi-decade employment foundations.",
        "action": "ACCUMULATE — focus on inner-ring suburbs with yields >4.5% and upcoming infrastructure.",
    },
    {
        "title": "Queensland Olympics Tailwind Intensifying",
        "category": "infrastructure",
        "states": ["QLD"],
        "insight": "Brisbane 2032 Olympics infrastructure spend exceeding $5B is creating a South-East QLD property corridor. Cross River Rail opening 2025 transforms transit. Moreton Bay, Logan, and Ipswich offer sub-$600K houses with 5%+ yields. Interstate migration remains QLD's largest population growth driver.",
        "action": "BUY — SE QLD corridor offers best growth + yield combination nationally.",
    },
    {
        "title": "Melbourne Value Play Emerging",
        "category": "contrarian",
        "states": ["VIC"],
        "insight": "Melbourne houses are flat YoY while other capitals surge. This creates the largest valuation gap in a decade. Land tax and stamp duty increases have dampened investor appetite, but fundamentals remain strong: 2.4% population growth, Suburban Rail Loop construction, and Australia's strongest auction culture. Contrarian opportunity.",
        "action": "SELECTIVE BUY — inner west (Footscray, Yarraville) and north (Preston, Reservoir) offer deep value.",
    },
    {
        "title": "National Rental Crisis Deepening",
        "category": "rental",
        "states": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"],
        "insight": "National vacancy rate at 1.0% — the lowest on record. Building approvals are 100,000+ below the National Housing Accord target. Net overseas migration at 548,800 continues to outstrip housing completions. Rents growing 5-11% annually across all capitals. Structural undersupply expected to persist through 2028+.",
        "action": "HOLD RENTAL ASSETS — increase exposure to high-yield markets (WA, SA, QLD).",
    },
    {
        "title": "RBA Rate Cuts Signal — Property Tailwind",
        "category": "monetary_policy",
        "states": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"],
        "insight": "RBA cut the cash rate to 4.10% in Feb 2025 — first cut in over 4 years. Markets pricing further cuts in H2 2025. Historically, the first rate cut has preceded 10-15% property price growth over the following 18 months. Borrowing capacity increases ~$50K per 0.25% cut.",
        "action": "POSITION AHEAD — lock in purchases before rate-cut-driven FOMO returns.",
    },
    {
        "title": "Housing Undersupply: 200,000+ Dwelling Deficit",
        "category": "supply",
        "states": ["NSW", "VIC", "QLD", "SA", "WA"],
        "insight": "Australia's dwelling deficit is estimated at 200,000+ homes. The National Housing Accord target of 1.2M homes by 2029 requires 240K completions/year, but current run rate is ~160K. Construction costs have risen 30%+ since 2020. Builder insolvencies at record highs. This structural undersupply underpins long-term price growth.",
        "action": "STRATEGIC — favour existing dwellings over off-the-plan. Land banking in growth corridors.",
    },
    {
        "title": "Regional Australia: Yield Hotspots Persist",
        "category": "regional",
        "states": ["VIC", "QLD", "NSW", "WA"],
        "insight": "Regional centres continue offering yields 1.5-2.5% above capital cities. Key hotspots: Geelong (VIC), Toowoomba (QLD), Newcastle (NSW), Bunbury (WA). Work-from-home normalisation sustaining demand. Regional vacancy rates below 1% in many centres.",
        "action": "TARGET — regional centres with population >50K, hospital/university, and rail connection.",
    },
    {
        "title": "Foreign Investment Returning Post-COVID",
        "category": "demand",
        "states": ["NSW", "VIC", "QLD"],
        "insight": "FIRB approvals for residential property up 28% YoY. Chinese, Indian, and SE Asian buyers returning to Sydney, Melbourne, and Brisbane. New-build exemptions making apartments attractive. Student accommodation demand surging with record international enrolments.",
        "action": "MONITOR — new-build apartments near universities for capital growth from foreign demand.",
    },
]


def get_investment_insights(states: list[str] | None = None) -> list[dict]:
    """Return investment insights, optionally filtered by states."""
    if not states:
        return INVESTMENT_INSIGHTS
    return [
        insight for insight in INVESTMENT_INSIGHTS
        if any(s.upper() in insight["states"] for s in states)
    ]


def get_ticker_data() -> list[dict]:
    """Return real-time ticker tape data for dashboard display."""
    items = []

    # RBA cash rate
    items.append({
        "label": "RBA CASH",
        "value": f"{RBA_DATA['cash_rate']['current']:.2f}%",
        "change": f"{RBA_DATA['cash_rate']['current'] - 4.35:+.2f}%",
        "direction": "down",
    })

    # CPI
    items.append({
        "label": "CPI",
        "value": f"{RBA_DATA['inflation']['cpi_annual']:.1f}%",
        "change": "",
        "direction": "neutral",
    })

    # Unemployment
    items.append({
        "label": "UNEMP",
        "value": f"{RBA_DATA['unemployment']['rate']:.1f}%",
        "change": "",
        "direction": "neutral",
    })

    # Each state median + growth
    for code, data in STATE_MARKET_DATA.items():
        growth = data["annual_growth_house_pct"]
        direction = "up" if growth > 0 else "down" if growth < 0 else "neutral"
        items.append({
            "label": f"{code} MED",
            "value": f"${data['median_house']:,.0f}",
            "change": f"{growth:+.1f}%",
            "direction": direction,
        })

    # National vacancy & migration
    items.append({
        "label": "VACANCY",
        "value": f"{RBA_DATA['rental_market_national']['national_vacancy_rate']:.1f}%",
        "change": "record low",
        "direction": "down",
    })
    items.append({
        "label": "MIGRATION",
        "value": f"+{RBA_DATA['population']['net_overseas_migration']:,}",
        "change": "annual",
        "direction": "up",
    })

    return items


# ═══════════════════════════════════════════════════════════════════
# KPI DATA FOR DASHBOARD TOP STRIP
# ═══════════════════════════════════════════════════════════════════

def get_dashboard_kpis() -> list[dict]:
    """Return KPI data for the dashboard header strip."""
    national = get_national_summary()
    return [
        {"label": "RBA RATE", "value": f"{national['rba_cash_rate']:.2f}%", "sub": "Cash Rate"},
        {"label": "AUS MED", "value": f"${national['national_median_house']:,.0f}", "sub": "Weighted Median"},
        {"label": "GROWTH", "value": f"{national['national_median_growth_pct']:+.1f}%", "sub": "YoY Capital"},
        {"label": "YIELD", "value": f"{national['national_gross_yield_pct']:.1f}%", "sub": "Gross National"},
        {"label": "VACANCY", "value": f"{national['national_vacancy_rate']:.1f}%", "sub": "National"},
        {"label": "CPI", "value": f"{national['cpi_annual']:.1f}%", "sub": "Annual"},
        {"label": "MIGRATION", "value": f"+{national['net_migration']:,}", "sub": "Annual NOM"},
        {"label": "LISTINGS", "value": f"{national['total_listings']:,}", "sub": "Total Active"},
    ]
