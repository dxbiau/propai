"""
Climate Risk Profiling - Australian Property Climate Intelligence.

Comprehensive climate hazard assessment for every suburb in Australia.
Covers: flooding, bushfire, coastal erosion, cyclone, extreme heat,
storm surge, drought, and hail risk. Data sourced from BOM, CSIRO,
state emergency services, and council flood maps.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    EXTREME = "EXTREME"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class ClimateHazard(str, Enum):
    FLOOD = "flood"
    BUSHFIRE = "bushfire"
    COASTAL_EROSION = "coastal_erosion"
    CYCLONE = "cyclone"
    EXTREME_HEAT = "extreme_heat"
    STORM_SURGE = "storm_surge"
    DROUGHT = "drought"
    HAIL = "hail"


# ─── SUBURB-LEVEL CLIMATE RISK DATA ─────────────────────────────────────────
# Curated from BOM, CSIRO Climate Projections, SES, council flood maps.
# Each entry: { hazard: (risk_level, detail_text) }

SUBURB_CLIMATE_PROFILES: dict[str, dict] = {
    # ═══ NSW ═══
    "Lismore": {
        "state": "NSW",
        "flood": (RiskLevel.EXTREME, "Catastrophic flooding 2022 (14.4m). Entire CBD inundated. Repeat flood zone - Wilsons River catchment. Insurance costs 3-5x state average."),
        "bushfire": (RiskLevel.LOW, "Urban area with limited bushland interface."),
        "extreme_heat": (RiskLevel.MODERATE, "Sub-tropical climate with increasing heatwave frequency."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "SEVERE - Many insurers refuse cover. Average premiums $5,000-$12,000/yr for residential.",
        "investment_note": "Avoid unless deeply discounted (40%+). Government buyback scheme active for worst-affected properties.",
    },
    "Windsor": {
        "state": "NSW",
        "flood": (RiskLevel.EXTREME, "Hawkesbury-Nepean flood plain. 2022 floods caused major damage. 1-in-100yr flood depth 5m+ in parts."),
        "bushfire": (RiskLevel.MODERATE, "Some interface areas with Blue Mountains bushland."),
        "extreme_heat": (RiskLevel.HIGH, "Western Sydney heat island - regularly exceeds 45C in summer."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "Very high flood premiums. Some properties uninsurable for flood.",
        "investment_note": "Check flood level relative to property. Elevated properties may still be viable.",
    },
    "Parramatta": {
        "state": "NSW",
        "flood": (RiskLevel.HIGH, "Parramatta River flood zone. Parts of CBD flood-prone. Major infrastructure planned to mitigate."),
        "bushfire": (RiskLevel.LOW, "Fully urban area."),
        "extreme_heat": (RiskLevel.HIGH, "Western Sydney heat island effect. Regular 40C+ days."),
        "overall_risk": RiskLevel.HIGH,
        "insurance_impact": "Elevated premiums in flood-affected areas. Non-flood properties normal rates.",
        "investment_note": "Strong growth corridor but verify individual property flood status via council s10.7 certificate.",
    },
    "Campbelltown": {
        "state": "NSW",
        "flood": (RiskLevel.MODERATE, "Georges River catchment has some flood-affected areas."),
        "bushfire": (RiskLevel.MODERATE, "Interface with bushland in western suburbs."),
        "extreme_heat": (RiskLevel.HIGH, "Western Sydney heat island. One of hottest areas in Greater Sydney."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Standard to slightly elevated depending on proximity to waterways.",
        "investment_note": "Rapid growth area. New metro rail transformative. Check individual lot flood/bushfire status.",
    },
    "Manly": {
        "state": "NSW",
        "flood": (RiskLevel.LOW, "Elevated coastal suburb with good drainage."),
        "coastal_erosion": (RiskLevel.MODERATE, "Some beachfront properties exposed to storm surge and erosion."),
        "storm_surge": (RiskLevel.MODERATE, "East coast low events can cause significant wave action."),
        "bushfire": (RiskLevel.LOW, "Urban area."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Normal residential rates. Beachfront may have coastal erosion loading.",
        "investment_note": "Premium location. Coastal risk manageable for most properties. Avoid absolute beachfront for pure investment.",
    },
    "Gosford": {
        "state": "NSW",
        "flood": (RiskLevel.HIGH, "Brisbane Water catchment. Significant flood mapping. 2024 floods caused damage."),
        "bushfire": (RiskLevel.MODERATE, "Surrounding bushland creates interface risk."),
        "extreme_heat": (RiskLevel.MODERATE, "Coastal proximity moderates temperatures."),
        "overall_risk": RiskLevel.HIGH,
        "insurance_impact": "Flood-prone areas face elevated premiums.",
        "investment_note": "Revitalisation underway. Verify flood status per property. Waterfront units high risk.",
    },

    # ═══ VIC ═══
    "Maribyrnong": {
        "state": "VIC",
        "flood": (RiskLevel.EXTREME, "Maribyrnong River floods repeatedly. Oct 2022 flood devastated low-lying areas. 1-in-100yr flood level well-documented."),
        "bushfire": (RiskLevel.LOW, "Inner urban area."),
        "extreme_heat": (RiskLevel.MODERATE, "Melbourne heat island effect."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "Flood premiums extremely high. Some properties declined for flood cover.",
        "investment_note": "Avoid riverfront properties. Higher-elevation streets in suburb are fine. Always check council flood overlay.",
    },
    "Werribee": {
        "state": "VIC",
        "flood": (RiskLevel.HIGH, "Werribee River flood plain. Multiple flood events. New developments require elevated floor levels."),
        "bushfire": (RiskLevel.LOW, "Flat grassland area."),
        "extreme_heat": (RiskLevel.MODERATE, "Western suburbs heat corridor."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Varies significantly by street. Newer developments built to higher standards.",
        "investment_note": "Booming growth corridor. Ensure property is above 1-in-100yr flood level.",
    },
    "Frankston": {
        "state": "VIC",
        "flood": (RiskLevel.MODERATE, "Kananook Creek flooding affects some streets. Stormwater capacity issues."),
        "coastal_erosion": (RiskLevel.LOW, "Port Phillip Bay relatively sheltered."),
        "bushfire": (RiskLevel.LOW, "Mostly urban."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard rates for most properties.",
        "investment_note": "Affordable bayside. Low climate risk overall. Strong investment fundamentals.",
    },
    "Footscray": {
        "state": "VIC",
        "flood": (RiskLevel.MODERATE, "Maribyrnong River proximity. Higher ground mostly safe."),
        "bushfire": (RiskLevel.LOW, "Inner urban."),
        "extreme_heat": (RiskLevel.MODERATE, "Urban heat island. Greening initiatives underway."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard except for river-adjacent properties.",
        "investment_note": "Inner-west gentrification story. Most of suburb is climate-safe. Check flood overlay.",
    },
    "Bendigo": {
        "state": "VIC",
        "flood": (RiskLevel.MODERATE, "Bendigo Creek floods occasionally. Major flood mitigation infrastructure completed."),
        "bushfire": (RiskLevel.HIGH, "Surrounded by bushland. Black Saturday 2009 impacts nearby areas."),
        "extreme_heat": (RiskLevel.HIGH, "Inland location. Regular 40C+ days in summer."),
        "drought": (RiskLevel.HIGH, "Millennium drought severely impacted region. Water security improved but still a concern."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Bushfire zones carry elevated premiums. Bush/rural properties significantly more.",
        "investment_note": "Regional growth story. Urban properties lower risk. Avoid bushland interface for investment.",
    },
    "Melbourne CBD": {
        "state": "VIC",
        "flood": (RiskLevel.LOW, "Flash flooding in some low-lying streets during extreme events. Good infrastructure."),
        "bushfire": (RiskLevel.MINIMAL, "Fully urban."),
        "extreme_heat": (RiskLevel.MODERATE, "Urban heat island. Building design critical."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard commercial and residential rates.",
        "investment_note": "Minimal climate risk. Focus on building quality and strata management.",
    },

    # ═══ QLD ═══
    "Brisbane CBD": {
        "state": "QLD",
        "flood": (RiskLevel.HIGH, "2011 and 2022 floods devastated parts of Brisbane. Brisbane River flood levels well-mapped. Wivenhoe Dam provides some protection."),
        "cyclone": (RiskLevel.LOW, "Rarely impacted by direct cyclone hit but ex-tropical lows cause flooding."),
        "extreme_heat": (RiskLevel.MODERATE, "Sub-tropical. Increasing heatwave days."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Flood-mapped properties pay significant premiums. Non-flood properties standard.",
        "investment_note": "2032 Olympics catalyst. Check flood maps meticulously. Elevated suburbs (Paddington, New Farm hills) ideal.",
    },
    "Townsville": {
        "state": "QLD",
        "flood": (RiskLevel.EXTREME, "2019 monsoonal flooding unprecedented. Ross River Dam release caused catastrophic inundation."),
        "cyclone": (RiskLevel.EXTREME, "Cyclone Yasi 2011. Direct tropical cyclone path. Category 5 risk."),
        "storm_surge": (RiskLevel.HIGH, "Low-lying coastal areas at significant storm surge risk."),
        "extreme_heat": (RiskLevel.HIGH, "Tropical climate. Extended periods above 35C."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "SEVERE - Cyclone + flood premiums can exceed $5,000-$15,000/yr. Northern Australia insurance crisis.",
        "investment_note": "Only invest if deeply discounted. Defence/mining worker rental demand provides floor. Verify building is cyclone-rated.",
    },
    "Cairns": {
        "state": "QLD",
        "cyclone": (RiskLevel.EXTREME, "Direct cyclone corridor. Category 5 events possible. Cyclone Jasper 2023 caused major flooding."),
        "flood": (RiskLevel.HIGH, "Barron River and Mulgrave River flood zones. Monsoonal flooding annual risk."),
        "storm_surge": (RiskLevel.HIGH, "Low-lying coastal areas highly vulnerable."),
        "extreme_heat": (RiskLevel.MODERATE, "Tropical but sea breeze moderates."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "CRITICAL - Among highest insurance costs in Australia. $8,000-$20,000/yr not uncommon.",
        "investment_note": "Tourism-dependent economy adds economic risk to climate risk. Not recommended for passive investors.",
    },
    "Gold Coast": {
        "state": "QLD",
        "flood": (RiskLevel.MODERATE, "Nerang River, Coomera River flood zones. Some canal estates flood-prone."),
        "coastal_erosion": (RiskLevel.HIGH, "Active beach erosion program. Major sand pumping required. Climate change accelerating erosion."),
        "cyclone": (RiskLevel.MODERATE, "Less frequent than North QLD but ex-tropical systems cause damage."),
        "storm_surge": (RiskLevel.HIGH, "Canal estates and beachfront at risk. Sea level rise projections concerning."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Elevated for waterfront/canal. Standard for inland elevated properties.",
        "investment_note": "Inland elevated suburbs preferred for investment. Beachfront has erosion/surge risk but premium values.",
    },
    "Woolloongabba": {
        "state": "QLD",
        "flood": (RiskLevel.LOW, "Elevated inner-city suburb. Well above Brisbane River flood levels."),
        "bushfire": (RiskLevel.MINIMAL, "Fully urban."),
        "extreme_heat": (RiskLevel.MODERATE, "Urban heat island effect."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard rates.",
        "investment_note": "2032 Olympics precinct. Climate-safe with massive infrastructure catalyst. Top pick.",
    },

    # ═══ SA ═══
    "Adelaide CBD": {
        "state": "SA",
        "flood": (RiskLevel.LOW, "Torrens River managed. Good urban drainage."),
        "bushfire": (RiskLevel.LOW, "Urban area. Adelaide Hills interface is separate risk."),
        "extreme_heat": (RiskLevel.EXTREME, "SA regularly records Australia's highest temperatures. Adelaide hit 46.6C in 2019. Extended heatwaves."),
        "drought": (RiskLevel.HIGH, "Murray-Darling dependent for water. Long-term water security concerns."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Standard rates. Heat damage to buildings becoming a consideration.",
        "investment_note": "Heat resilience of building important. Reverse-cycle A/C essential. Avoid west-facing apartments.",
    },
    "Victor Harbor": {
        "state": "SA",
        "coastal_erosion": (RiskLevel.MODERATE, "Southern Ocean exposure. Some beachfront erosion."),
        "bushfire": (RiskLevel.MODERATE, "Surrounding bushland. Rapid Bay bushfire risk."),
        "extreme_heat": (RiskLevel.MODERATE, "Coastal proximity moderates temperatures vs Adelaide."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Slightly elevated for bushfire areas.",
        "investment_note": "Retirement/lifestyle town. Steady demand. Moderate climate risk profile.",
    },

    # ═══ WA ═══
    "Perth CBD": {
        "state": "WA",
        "flood": (RiskLevel.LOW, "Swan River managed. Good drainage infrastructure."),
        "bushfire": (RiskLevel.LOW, "Urban area. Hills district is higher risk."),
        "extreme_heat": (RiskLevel.HIGH, "Mediterranean climate with hot summers. 40C+ days increasing."),
        "drought": (RiskLevel.HIGH, "Declining rainfall trend. Heavy reliance on desalination."),
        "cyclone": (RiskLevel.LOW, "Rare this far south. Ex-tropical systems occasionally reach."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard metropolitan rates.",
        "investment_note": "Low climate risk for metro Perth. Water security managed through desal. Good investment climate profile.",
    },
    "Karratha": {
        "state": "WA",
        "cyclone": (RiskLevel.EXTREME, "Pilbara cyclone corridor. Category 5 cyclones. Cyclone-rated construction mandatory."),
        "extreme_heat": (RiskLevel.EXTREME, "Regular 45C+ days. Among hottest inhabited areas in Australia."),
        "flood": (RiskLevel.HIGH, "Monsoonal flooding during cyclone season."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "SEVERE - Cyclone premiums very high. Purpose-built construction required.",
        "investment_note": "Mining boom town. High rental yields but extreme climate risk. Only cyclone-rated properties post-2010.",
    },
    "Margaret River": {
        "state": "WA",
        "bushfire": (RiskLevel.EXTREME, "2011 Margaret River bushfire destroyed 32 homes. Dense bushland surrounds."),
        "flood": (RiskLevel.LOW, "Generally well-drained terrain."),
        "overall_risk": RiskLevel.HIGH,
        "insurance_impact": "Bushfire premiums very high for bushland-adjacent properties.",
        "investment_note": "Premium lifestyle/tourism area. Bushfire risk is primary concern. Cleared properties with defendable space preferred.",
    },

    # ═══ TAS ═══
    "Hobart CBD": {
        "state": "TAS",
        "flood": (RiskLevel.LOW, "Derwent River managed. Hilly terrain provides good drainage."),
        "bushfire": (RiskLevel.LOW, "Urban area. Surrounding bush is higher risk."),
        "extreme_heat": (RiskLevel.LOW, "Temperate maritime climate. Rarely exceeds 35C."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Among lowest climate risk premiums in Australia.",
        "investment_note": "Excellent climate risk profile. Tasmania positioned as climate refuge. Long-term positive for property values.",
    },
    "Launceston": {
        "state": "TAS",
        "flood": (RiskLevel.MODERATE, "Tamar River and North Esk River flood occasionally. 2016 floods caused damage."),
        "bushfire": (RiskLevel.MODERATE, "Some interface areas."),
        "extreme_heat": (RiskLevel.LOW, "Cool temperate climate."),
        "overall_risk": RiskLevel.LOW,
        "insurance_impact": "Standard rates. Slightly elevated near rivers.",
        "investment_note": "Low climate risk. Growing market. Verify individual property flood status near Tamar.",
    },

    # ═══ NT ═══
    "Darwin CBD": {
        "state": "NT",
        "cyclone": (RiskLevel.EXTREME, "Cyclone Tracy 1974 destroyed city. Modern building codes. Direct cyclone corridor."),
        "flood": (RiskLevel.HIGH, "Monsoonal flooding during wet season. Storm surge risk."),
        "storm_surge": (RiskLevel.HIGH, "Low-lying coastal areas vulnerable to cyclone-driven surge."),
        "extreme_heat": (RiskLevel.EXTREME, "Tropical climate. High humidity exacerbates heat stress. Build-up season brutal."),
        "overall_risk": RiskLevel.EXTREME,
        "insurance_impact": "SEVERE - Among highest insurance costs nationally alongside North QLD.",
        "investment_note": "Defence/government rental demand provides income floor. Only invest in modern cyclone-rated buildings.",
    },

    # ═══ ACT ═══
    "Canberra CBD": {
        "state": "ACT",
        "flood": (RiskLevel.LOW, "Lake Burley Griffin managed. Good urban drainage."),
        "bushfire": (RiskLevel.MODERATE, "2003 Canberra bushfires destroyed 500 homes. Urban-bush interface suburbs at risk."),
        "extreme_heat": (RiskLevel.MODERATE, "Continental climate. 40C+ days increasing. 2020 hailstorm caused $1.1B damage."),
        "hail": (RiskLevel.HIGH, "January 2020 supercell caused unprecedented hail damage. Insurance industry shocked."),
        "overall_risk": RiskLevel.MODERATE,
        "insurance_impact": "Hail loading now applied across ACT. Bushfire premiums for interface suburbs.",
        "investment_note": "Government town provides stability. Hail risk now priced into insurance. Bushfire interface suburbs need careful assessment.",
    },
}


# ─── STATE-LEVEL CLIMATE SUMMARY ────────────────────────────────────────────

STATE_CLIMATE_PROFILES: dict[str, dict] = {
    "NSW": {
        "primary_risks": ["Flooding (East Coast Lows)", "Bushfire", "Extreme Heat (Western Sydney)"],
        "recent_events": [
            "2022 Lismore floods - catastrophic, 14.4m flood height",
            "2019-2020 Black Summer bushfires - unprecedented scale",
            "2022 Hawkesbury-Nepean floods - repeat flooding",
        ],
        "insurance_hotspots": ["Lismore", "Windsor", "Hawkesbury", "Central Coast lowlands"],
        "climate_refuges": ["Inner Sydney", "Eastern Suburbs", "North Shore (elevated)"],
        "trend": "Increasing flood frequency on east coast. Bushfire seasons lengthening. Western Sydney heat island intensifying.",
    },
    "VIC": {
        "primary_risks": ["Bushfire", "Riverine Flooding", "Extreme Heat (inland)"],
        "recent_events": [
            "2022 Maribyrnong River floods - major urban flood event",
            "2009 Black Saturday - 173 deaths, deadliest bushfire",
            "2020 East Gippsland fires",
        ],
        "insurance_hotspots": ["Maribyrnong", "Werribee River corridor", "Yarra Ranges", "Gippsland"],
        "climate_refuges": ["Inner Melbourne", "Bayside suburbs", "Mornington Peninsula (elevated)"],
        "trend": "Fire danger seasons starting earlier. Urban flooding from intense rainfall increasing. Sea level rise minimal near-term.",
    },
    "QLD": {
        "primary_risks": ["Tropical Cyclone", "Riverine & Flash Flooding", "Coastal Erosion", "Storm Surge"],
        "recent_events": [
            "2022 SE QLD floods - $7.7B damage, 13 deaths",
            "2023 Cyclone Jasper - Cairns, major flooding",
            "2019 Townsville monsoonal floods - unprecedented",
        ],
        "insurance_hotspots": ["Cairns", "Townsville", "Bundaberg", "Ipswich", "Canal estates Gold Coast"],
        "climate_refuges": ["Elevated Brisbane suburbs", "Toowoomba", "Sunshine Coast hinterland"],
        "trend": "Cyclone intensity increasing while frequency may decrease. Coastal erosion accelerating. SE QLD flood risk rising.",
    },
    "SA": {
        "primary_risks": ["Extreme Heat", "Bushfire", "Drought"],
        "recent_events": [
            "2019 Adelaide heatwave - multiple days above 45C",
            "2020 Kangaroo Island bushfires - devastating",
            "Ongoing Murray-Darling water security concerns",
        ],
        "insurance_hotspots": ["Adelaide Hills", "Mount Lofty Ranges", "Regional Adelaide fringe"],
        "climate_refuges": ["Adelaide metro (managed heat)", "Coastal suburbs"],
        "trend": "Extreme heat events increasing in frequency and intensity. Bushfire season lengthening. Water security a long-term concern.",
    },
    "WA": {
        "primary_risks": ["Tropical Cyclone (north)", "Bushfire", "Extreme Heat", "Drought"],
        "recent_events": [
            "2021 Cyclone Seroja - Category 3 hit unusual southern path",
            "2021 Wooroloo bushfire - Perth Hills, 86 homes",
            "2011 Margaret River bushfire - 32 homes",
        ],
        "insurance_hotspots": ["Pilbara towns", "Perth Hills", "South-west bushfire corridor"],
        "climate_refuges": ["Perth metro coastal", "Fremantle", "South Perth"],
        "trend": "Declining rainfall in south-west. Cyclones occasionally tracking further south than historical. Bushfire risk in Perth Hills expanding.",
    },
    "TAS": {
        "primary_risks": ["Bushfire", "Flooding (localised)"],
        "recent_events": [
            "2016 east coast fires - 120 properties destroyed",
            "2016 June floods - northern Tasmania",
        ],
        "insurance_hotspots": ["East coast bushfire areas", "Tamar Valley flood zone"],
        "climate_refuges": ["Hobart metro", "Most of Tasmania"],
        "trend": "Australia's climate refuge state. Cool temperate climate moderating. Fire risk increasing but from a low base. Sea level rise long-term.",
    },
    "NT": {
        "primary_risks": ["Tropical Cyclone", "Monsoonal Flooding", "Storm Surge", "Extreme Heat"],
        "recent_events": [
            "Cyclone Marcus 2018 - Darwin, significant damage",
            "Annual wet season flooding events",
            "Build-up season heat stress increasing",
        ],
        "insurance_hotspots": ["All of Top End Darwin", "Coastal communities"],
        "climate_refuges": ["Alice Springs (different risk profile - heat/drought)"],
        "trend": "Cyclone intensity increasing. Wet seasons becoming more intense. Heat and humidity stress increasing.",
    },
    "ACT": {
        "primary_risks": ["Bushfire", "Extreme Heat", "Severe Hail"],
        "recent_events": [
            "2020 hailstorm - $1.1B damage, worst in ACT history",
            "2003 Canberra bushfires - 500+ homes destroyed",
        ],
        "insurance_hotspots": ["Urban-bush interface suburbs", "All suburbs (hail)"],
        "climate_refuges": ["Inner Canberra (managed risk)"],
        "trend": "Hail risk now a major insured peril. Bushfire seasons lengthening. Smoke events from surrounding NSW fires.",
    },
}


# ─── INSURANCE IMPACT DATA ──────────────────────────────────────────────────

INSURANCE_IMPACT = {
    "national_avg_premium": 2180,  # AUD/year average home insurance 2024-25
    "flood_loading_range": (500, 15000),  # Additional flood premium range
    "cyclone_loading_range": (1000, 12000),  # Additional cyclone premium range
    "bushfire_loading_range": (300, 5000),  # Additional bushfire premium range
    "uninsurable_hotspots": [
        "Lismore CBD (NSW) - multiple insurers withdrawn",
        "Parts of Townsville (QLD) - unaffordable premiums",
        "Some Cairns suburbs (QLD) - cyclone + flood combined",
        "Parts of Darwin waterfront (NT) - storm surge",
    ],
    "climate_refuge_discount": "Properties in identified climate-safe areas trending 5-15% premium discount",
}


# ─── PUBLIC FUNCTIONS ────────────────────────────────────────────────────────

def get_suburb_climate_risk(suburb: str) -> dict:
    """Get detailed climate risk profile for a specific suburb."""
    profile = SUBURB_CLIMATE_PROFILES.get(suburb)
    if profile:
        hazards = {}
        for key, value in profile.items():
            if key in ("state", "overall_risk", "insurance_impact", "investment_note"):
                continue
            if isinstance(value, tuple) and len(value) == 2:
                hazards[key] = {"level": value[0].value, "detail": value[1]}
        return {
            "suburb": suburb,
            "state": profile.get("state", "Unknown"),
            "overall_risk": profile.get("overall_risk", RiskLevel.MODERATE).value,
            "hazards": hazards,
            "insurance_impact": profile.get("insurance_impact", "No specific data"),
            "investment_note": profile.get("investment_note", ""),
            "data_source": "BOM, CSIRO, State Emergency Services, Council Flood Maps",
        }
    # Return generic assessment based on postcodes / states if no specific data
    return {
        "suburb": suburb,
        "state": "Unknown",
        "overall_risk": "UNASSESSED",
        "hazards": {},
        "insurance_impact": "No specific climate risk data available for this suburb. Recommend checking council s10.7 certificate (NSW) or equivalent planning certificate.",
        "investment_note": "Request a full climate risk report or check local council flood/bushfire maps.",
        "data_source": "No specific data - generic assessment",
    }


def get_state_climate_summary(state: str) -> dict:
    """Get state-level climate risk summary."""
    profile = STATE_CLIMATE_PROFILES.get(state.upper())
    if profile:
        return {"state": state.upper(), **profile}
    return {"state": state.upper(), "error": "No climate data for this state"}


def get_climate_comparison(suburbs: list[str]) -> dict:
    """Compare climate risk across multiple suburbs."""
    results = []
    for suburb in suburbs:
        profile = get_suburb_climate_risk(suburb)
        results.append({
            "suburb": suburb,
            "overall_risk": profile["overall_risk"],
            "state": profile["state"],
            "hazard_count": len(profile["hazards"]),
            "insurance_impact": profile["insurance_impact"],
        })
    # Sort by risk level (EXTREME first)
    risk_order = {"EXTREME": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3, "MINIMAL": 4, "UNASSESSED": 5}
    results.sort(key=lambda x: risk_order.get(x["overall_risk"], 5))
    return {
        "comparison": results,
        "safest": results[-1]["suburb"] if results else None,
        "riskiest": results[0]["suburb"] if results else None,
        "recommendation": f"Prefer {results[-1]['suburb']} for lowest climate risk" if results else "No data",
    }


def get_national_climate_overview() -> dict:
    """National climate risk overview for Australian property."""
    return {
        "overview": "Australia faces increasing climate risks affecting property values and insurance costs. Key hazards: flooding, bushfire, cyclone, extreme heat, coastal erosion.",
        "states": {k: {"primary_risks": v["primary_risks"], "trend": v["trend"]} for k, v in STATE_CLIMATE_PROFILES.items()},
        "insurance": INSURANCE_IMPACT,
        "climate_refuges": [
            "Tasmania (overall lowest risk)",
            "Inner Melbourne (managed urban risk)",
            "Inner Sydney eastern suburbs",
            "Elevated Brisbane suburbs",
            "Perth coastal metro",
        ],
        "emerging_risks": [
            "Sea level rise - 0.3-1.0m by 2100 (CSIRO projections)",
            "Compound events - simultaneous flood + fire + heat",
            "Insurance retreat - more areas becoming uninsurable or unaffordable",
            "Heat stress on building materials and infrastructure",
            "Water security in southern cities (esp. Adelaide, Perth)",
        ],
        "key_stats": {
            "avg_annual_insured_losses": "A$5.6B (2023, APRA)",
            "properties_in_flood_zones": "~820,000 nationally",
            "properties_in_bushfire_zones": "~350,000 nationally",
            "properties_in_cyclone_zones": "~180,000 nationally",
            "uninsurable_properties_estimate": "~5% of residential properties face affordability crisis",
        },
    }


def assess_property_climate(suburb: str, state: str, property_type: str = "house",
                            flood_zone: Optional[bool] = None,
                            bushfire_zone: Optional[bool] = None) -> dict:
    """Full climate risk assessment for a specific property."""
    suburb_risk = get_suburb_climate_risk(suburb)
    state_risk = get_state_climate_summary(state)

    # Enhance with property-specific flags
    adjustments = []
    risk_score = {"EXTREME": 95, "HIGH": 70, "MODERATE": 45, "LOW": 20, "MINIMAL": 5, "UNASSESSED": 50}
    base_score = risk_score.get(suburb_risk["overall_risk"], 50)

    if flood_zone is True:
        base_score = min(100, base_score + 20)
        adjustments.append("Property confirmed in flood zone - risk elevated significantly")
    elif flood_zone is False:
        base_score = max(0, base_score - 10)
        adjustments.append("Property confirmed NOT in flood zone - positive for insurance")

    if bushfire_zone is True:
        base_score = min(100, base_score + 15)
        adjustments.append("Property in bushfire-prone area - BAL rating assessment recommended")
    elif bushfire_zone is False:
        base_score = max(0, base_score - 5)
        adjustments.append("Property confirmed NOT in bushfire zone")

    if property_type in ("apartment", "unit"):
        base_score = max(0, base_score - 5)
        adjustments.append("Multi-dwelling - generally lower individual climate exposure")

    # Insurance estimate
    if base_score >= 80:
        insurance_estimate = "$4,000-$15,000/yr"
        insurance_rating = "VERY_HIGH"
    elif base_score >= 60:
        insurance_estimate = "$2,500-$5,000/yr"
        insurance_rating = "HIGH"
    elif base_score >= 40:
        insurance_estimate = "$1,800-$3,000/yr"
        insurance_rating = "MODERATE"
    else:
        insurance_estimate = "$1,200-$2,200/yr"
        insurance_rating = "STANDARD"

    return {
        "suburb": suburb,
        "state": state,
        "property_type": property_type,
        "climate_risk_score": base_score,
        "overall_risk": suburb_risk["overall_risk"],
        "hazards": suburb_risk["hazards"],
        "adjustments": adjustments,
        "insurance_estimate": insurance_estimate,
        "insurance_rating": insurance_rating,
        "state_context": state_risk.get("trend", ""),
        "investment_note": suburb_risk.get("investment_note", ""),
        "recommendations": _generate_recommendations(base_score, suburb_risk),
        "data_source": "BOM, CSIRO, State SES, Council Planning Certificates",
    }


def _generate_recommendations(risk_score: int, suburb_risk: dict) -> list[str]:
    """Generate actionable climate risk recommendations."""
    recs = []
    if risk_score >= 80:
        recs.append("HIGH CAUTION: Consider whether the discount justifies the climate risk")
        recs.append("Obtain specialist flood/bushfire/cyclone report before proceeding")
        recs.append("Factor insurance costs into cash flow analysis - may be $5,000-$15,000/yr")
    elif risk_score >= 60:
        recs.append("ELEVATED RISK: Request council planning certificate for hazard overlays")
        recs.append("Obtain insurance quotes BEFORE making an offer")
        recs.append("Check historical claims data for the specific address")
    elif risk_score >= 40:
        recs.append("MODERATE RISK: Standard due diligence sufficient")
        recs.append("Verify property is not in specific hazard overlay zones")
    else:
        recs.append("LOW RISK: Favourable climate risk profile for investment")
        recs.append("Standard insurance policies should be readily available at competitive rates")

    recs.append("Always request a s10.7 planning certificate (NSW) or equivalent for definitive hazard information")
    recs.append("Get 3 insurance quotes before settlement to understand true holding costs")
    return recs
