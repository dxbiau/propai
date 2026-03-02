"""
Personal Research Agent - Property Link Research & Climate Intelligence.

Allows users to:
  1. Paste a property URL (Domain, REA, any link) and import/analyse it
  2. Get all nearby properties in the same region
  3. Get real-time market data and climate risk profiling
  4. Keep properties private or add to public database

Part of Australian Property Associates (APA) intelligence stack.
"""

from __future__ import annotations

import re
import time
from typing import Any, Optional
from uuid import uuid4

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.climate_risk import (
    assess_property_climate,
    get_suburb_climate_risk,
    get_state_climate_summary,
    get_climate_comparison,
)
from nexusprop.locations import AUSTRALIAN_REGIONS
from nexusprop.market_data import get_state_data


# URL patterns for property portals
URL_PATTERNS = {
    "domain": re.compile(r"domain\.com\.au/.+?/(.+?)-(\w+)-(\d{4})-", re.IGNORECASE),
    "realestate": re.compile(r"realestate\.com\.au/.+?/(.+?)-(.+?)-(\d+)", re.IGNORECASE),
    "generic": re.compile(r"https?://[^\s]+", re.IGNORECASE),
}

# State lookup by postcode range
POSTCODE_STATE_MAP = [
    (1000, 2599, "NSW"), (2619, 2899, "NSW"), (2921, 2999, "NSW"),
    (2600, 2618, "ACT"), (2900, 2920, "ACT"),
    (3000, 3999, "VIC"),
    (4000, 4999, "QLD"),
    (5000, 5799, "SA"),
    (6000, 6797, "WA"),
    (7000, 7799, "TAS"),
    (800, 899, "NT"), (900, 999, "NT"),
]


def postcode_to_state(postcode: str) -> str:
    """Resolve Australian state from postcode."""
    try:
        pc = int(postcode)
    except (ValueError, TypeError):
        return "NSW"
    for low, high, state in POSTCODE_STATE_MAP:
        if low <= pc <= high:
            return state
    return "NSW"


def extract_property_info_from_url(url: str) -> dict:
    """Extract suburb, state, type hints from a property portal URL."""
    info = {"url": url, "source": "unknown", "suburb_hint": None, "state_hint": None}

    if "domain.com.au" in url.lower():
        info["source"] = "domain.com.au"
        # Domain URLs: /property-type/suburb-state-postcode/address
        parts = url.lower().replace("-", " ").split("/")
        for part in parts:
            # Look for state abbreviations
            for st in ("nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"):
                if f" {st} " in f" {part} ":
                    info["state_hint"] = st.upper()
        # Try to extract suburb from URL path
        match = re.search(r"/([a-z\-]+)-(?:nsw|vic|qld|sa|wa|tas|nt|act)-(\d{4})", url.lower())
        if match:
            info["suburb_hint"] = match.group(1).replace("-", " ").title()
            info["state_hint"] = postcode_to_state(match.group(2))

    elif "realestate.com.au" in url.lower():
        info["source"] = "realestate.com.au"
        match = re.search(r"/([a-z\+\-]+)\+(?:nsw|vic|qld|sa|wa|tas|nt|act)\+(\d{4})", url.lower())
        if match:
            info["suburb_hint"] = match.group(1).replace("+", " ").replace("-", " ").title()
            info["state_hint"] = postcode_to_state(match.group(2))

    elif "allhomes.com.au" in url.lower():
        info["source"] = "allhomes.com.au"

    return info


def find_nearby_suburbs(suburb: str, state: str, radius: int = 5) -> list[dict]:
    """Find suburbs in the same region/area as the target suburb."""
    nearby = []
    target_region = None

    # Find which region this suburb belongs to
    state_regions = AUSTRALIAN_REGIONS.get(state, {})
    for region_name, suburbs in state_regions.items():
        for sub in suburbs:
            if sub["name"].lower() == suburb.lower():
                target_region = region_name
                break
        if target_region:
            break

    if target_region and target_region in state_regions:
        for sub in state_regions[target_region]:
            if sub["name"].lower() != suburb.lower():
                nearby.append({
                    "suburb": sub["name"],
                    "postcode": sub["postcode"],
                    "state": state,
                    "region": target_region,
                    "median": sub.get("median", 0),
                    "growth": sub.get("growth", 0),
                })

    # Also check adjacent regions (first 3 suburbs from each)
    region_keys = list(state_regions.keys())
    if target_region and target_region in region_keys:
        idx = region_keys.index(target_region)
        for adj_idx in [idx - 1, idx + 1]:
            if 0 <= adj_idx < len(region_keys):
                adj_region = region_keys[adj_idx]
                for sub in state_regions[adj_region][:3]:
                    nearby.append({
                        "suburb": sub["name"],
                        "postcode": sub["postcode"],
                        "state": state,
                        "region": adj_region,
                        "median": sub.get("median", 0),
                        "growth": sub.get("growth", 0),
                    })

    return nearby[:radius * 3]  # Cap results


class PersonalResearchAgent(BaseAgent):
    """
    Personal Research Agent - paste a link, get everything.

    Capabilities:
    - Parse property URLs from Domain, REA, AllHomes
    - Extract suburb/state/type from URL structure
    - Pull nearby properties from the same region
    - Full climate risk profiling (flood, bushfire, cyclone, heat)
    - Market data overlay (median prices, growth, yields)
    - AI-enriched investment analysis
    """

    def __init__(self):
        super().__init__("PersonalResearchAgent")

    async def execute(self, request: dict) -> AgentResult:
        """
        Main entry point for personal research.

        request keys:
            - url: str (property URL to research)
            - suburb: str (optional, if known)
            - state: str (optional, if known)
            - postcode: str (optional)
            - private: bool (keep research private, default False)
            - include_climate: bool (include climate risk, default True)
            - include_nearby: bool (include nearby properties, default True)
        """
        start = time.time()
        try:
            url = request.get("url", "")
            suburb = request.get("suburb")
            state = request.get("state")
            postcode = request.get("postcode")
            private = request.get("private", False)
            include_climate = request.get("include_climate", True)
            include_nearby = request.get("include_nearby", True)

            # Step 1: Extract info from URL
            url_info = extract_property_info_from_url(url) if url else {}
            suburb = suburb or url_info.get("suburb_hint") or "Unknown"
            state = state or url_info.get("state_hint") or "NSW"

            self.logger.info("personal_research_start",
                             suburb=suburb, state=state, url=url[:80] if url else "none",
                             private=private)

            result = {
                "research_id": str(uuid4()),
                "url": url,
                "url_analysis": url_info,
                "suburb": suburb,
                "state": state,
                "postcode": postcode or "",
                "private": private,
                "property_data": None,
                "climate_risk": None,
                "nearby_properties": None,
                "market_data": None,
                "ai_analysis": None,
            }

            # Step 2: Climate risk profiling
            if include_climate:
                result["climate_risk"] = assess_property_climate(
                    suburb=suburb,
                    state=state,
                    property_type=request.get("property_type", "house"),
                    flood_zone=request.get("flood_zone"),
                    bushfire_zone=request.get("bushfire_zone"),
                )

            # Step 3: Nearby suburbs
            if include_nearby:
                nearby = find_nearby_suburbs(suburb, state)
                result["nearby_properties"] = nearby

                # Climate comparison of nearby suburbs
                if include_climate and nearby:
                    nearby_names = [suburb] + [n["suburb"] for n in nearby[:5]]
                    result["climate_comparison"] = get_climate_comparison(nearby_names)

            # Step 4: Market data overlay
            market = get_state_data(state)
            if market:
                result["market_data"] = {
                    "state_median_house": market.get("median_house"),
                    "state_median_unit": market.get("median_unit"),
                    "annual_growth": market.get("annual_growth_house_pct"),
                    "gross_yield": market.get("gross_yield_house_pct"),
                    "vacancy_rate": market.get("vacancy_rate"),
                    "auction_clearance": market.get("auction_clearance_rate"),
                    "rental_house_weekly": market.get("rental_house_weekly"),
                    "days_on_market": market.get("avg_days_on_market"),
                }

            # Step 5: AI-enriched analysis (try LLM)
            try:
                ai_prompt = self._build_research_prompt(result)
                system = (
                    "You are an expert Australian property research analyst for "
                    "Australian Property Associates (APA). Provide concise, "
                    "actionable investment intelligence. Include climate risk "
                    "assessment in your analysis. Use factual data."
                )
                text, tokens = await self._ask_llm(ai_prompt, system)
                result["ai_analysis"] = text
            except Exception:
                result["ai_analysis"] = self._fallback_analysis(result)

            elapsed = (time.time() - start) * 1000
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=result,
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            self.logger.error("personal_research_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                execution_time_ms=elapsed,
            )

    async def _ask_llm(self, prompt: str, system: str) -> tuple[str, int]:
        """Try Ollama first, then Anthropic, then raise."""
        try:
            return await self._ask_ollama(prompt, system=system)
        except Exception:
            try:
                return await self._ask_anthropic(prompt, system=system)
            except Exception:
                raise

    def _build_research_prompt(self, data: dict) -> str:
        """Build a comprehensive research prompt for the LLM."""
        parts = [
            f"Analyse this property research for {data['suburb']}, {data['state']}.",
            f"URL: {data.get('url', 'N/A')}",
        ]
        if data.get("climate_risk"):
            cr = data["climate_risk"]
            parts.append(f"Climate Risk Score: {cr.get('climate_risk_score', 'N/A')}/100")
            parts.append(f"Overall Risk: {cr.get('overall_risk', 'N/A')}")
            if cr.get("hazards"):
                for hazard, info in cr["hazards"].items():
                    parts.append(f"  {hazard}: {info['level']} - {info['detail'][:100]}")
        if data.get("market_data"):
            md = data["market_data"]
            parts.append(f"State Median House: ${md.get('state_median_house', 0):,.0f}")
            parts.append(f"Gross Yield: {md.get('gross_yield', 0)}%")
            parts.append(f"Vacancy Rate: {md.get('vacancy_rate', 0)}%")
        if data.get("nearby_properties"):
            parts.append(f"Nearby suburbs found: {len(data['nearby_properties'])}")

        parts.append("\nProvide: 1) Investment verdict, 2) Climate risk summary, "
                      "3) Key opportunities, 4) Red flags, 5) Recommended next steps.")
        return "\n".join(parts)

    def _fallback_analysis(self, data: dict) -> str:
        """Generate analysis without LLM."""
        suburb = data["suburb"]
        state = data["state"]
        cr = data.get("climate_risk", {})
        risk = cr.get("overall_risk", "UNASSESSED")

        lines = [
            f"=== PERSONAL RESEARCH REPORT: {suburb}, {state} ===\n",
            f"CLIMATE RISK: {risk}",
        ]

        if cr.get("climate_risk_score"):
            score = cr["climate_risk_score"]
            if score >= 70:
                lines.append(f"WARNING: High climate risk score ({score}/100). "
                             "Factor elevated insurance costs into cash flow.")
            elif score >= 40:
                lines.append(f"Climate risk is moderate ({score}/100). "
                             "Standard due diligence sufficient.")
            else:
                lines.append(f"Favourable climate risk profile ({score}/100). "
                             "Low insurance impact expected.")

        md = data.get("market_data", {})
        if md:
            lines.append(f"\nMARKET DATA ({state}):")
            lines.append(f"  Median House: ${md.get('state_median_house', 0):,.0f}")
            lines.append(f"  Gross Yield: {md.get('gross_yield', 0):.1f}%")
            lines.append(f"  Days on Market: {md.get('days_on_market', 'N/A')}")
            lines.append(f"  Vacancy Rate: {md.get('vacancy_rate', 0):.1f}%")

        nearby = data.get("nearby_properties", [])
        if nearby:
            lines.append(f"\nNEARBY SUBURBS ({len(nearby)} found):")
            for n in nearby[:5]:
                lines.append(f"  {n['suburb']} ({n['postcode']}) - "
                             f"Median ${n.get('median', 0):,.0f}, "
                             f"Growth {n.get('growth', 0):.1f}%")

        lines.append(f"\nRECOMMENDATION: {'Proceed with caution - verify climate risk' if risk in ('EXTREME', 'HIGH') else 'Standard research profile - proceed with due diligence'}")
        return "\n".join(lines)
