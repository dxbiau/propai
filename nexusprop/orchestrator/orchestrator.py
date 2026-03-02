"""
Property Insights Australia Orchestrator — the conductor of the self-governing AI ecosystem.

Full pipeline: Profiler → Scout → Analyst → Stacker → Closer → Concierge → Mentor → QA

9-agent self-improving pipeline with conditional routing:
- Profiler: builds/updates investor profile (runs first for personalization)
- Scout: discovers properties from configured sources
- Analyst: financial analysis + Bargain Score™ on each property
- LiveComps: comparable sales analysis
- Stacker: deal structuring — entity, financing, tax optimization
- Closer: offer document generation (golden opportunities only)
- Concierge: match deals to users, send notifications
- Mentor: personalized coaching based on results
- QA: evaluate ALL agent outputs, self-governance loop

Every pipeline run feeds the QA agent, which scores outputs and
generates improved skill templates — making each run smarter.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional
from uuid import uuid4

import structlog

from nexusprop.agents.analyst import AnalystAgent
from nexusprop.agents.base import AgentResult
from nexusprop.agents.closer import CloserAgent
from nexusprop.agents.concierge import ConciergeAgent
from nexusprop.agents.live_comps import LiveCompsAgent
from nexusprop.agents.mentor import MentorAgent
from nexusprop.agents.profiler import ProfilerAgent
from nexusprop.agents.qa import QAAgent
from nexusprop.agents.scout import ScoutAgent
from nexusprop.agents.stacker import StackerAgent
from nexusprop.config.settings import get_settings
from nexusprop.models.deal import Deal, DealType
from nexusprop.models.investment import InvestmentProfile
from nexusprop.models.offer import OfferGenerationRequest, OfferTone, SellerMotivation
from nexusprop.models.property import Property
from nexusprop.models.suburb import SuburbProfile
from nexusprop.models.user import UserProfile

logger = structlog.get_logger(__name__)


class PipelineResult:
    """Aggregated result from a full pipeline run."""

    def __init__(self):
        self.run_id = str(uuid4())
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.agent_results: list[AgentResult] = []
        self.properties_found: int = 0
        self.deals_analyzed: int = 0
        self.golden_opportunities: int = 0
        self.notifications_sent: int = 0
        self.total_tokens: int = 0
        self.errors: list[str] = []

    @property
    def duration_seconds(self) -> float:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0

    def finalize(self):
        self.completed_at = datetime.utcnow()
        self.total_tokens = sum(r.tokens_used for r in self.agent_results)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "properties_found": self.properties_found,
            "deals_analyzed": self.deals_analyzed,
            "golden_opportunities": self.golden_opportunities,
            "notifications_sent": self.notifications_sent,
            "total_tokens": self.total_tokens,
            "errors": self.errors,
            "agents": [r.to_dict() for r in self.agent_results],
        }

    def __repr__(self) -> str:
        return (
            f"PipelineResult(run={self.run_id[:8]}, "
            f"props={self.properties_found}, deals={self.deals_analyzed}, "
            f"golden={self.golden_opportunities}, {self.duration_seconds:.1f}s)"
        )


class Orchestrator:
    """
    The Orchestrator — conducts the full Property Insights Australia 9-agent pipeline.

    Pipeline stages (conditional routing):
    1. PROFILER  → Build/update investor profile for personalization
    2. SCOUT     → Scrape & harvest properties from configured sources
    3. ANALYST   → Run financial analysis & bargain scoring on each property
    4. COMPS     → (Optional) Real-time comparable sales analysis
    5. STACKER   → Deal structuring — entity, financing, tax optimization
    6. CLOSER    → (Optional) Generate offer documents for golden opportunities
    7. CONCIERGE → Match deals to users and send notifications
    8. MENTOR    → Personalized coaching based on pipeline results
    9. QA        → Evaluate all outputs + self-governance loop

    Each stage is independently configurable and can be run in isolation.
    The QA agent runs LAST and feeds improvements back for the next run.
    """

    def __init__(self):
        self.settings = get_settings()
        # Core pipeline agents
        self.profiler = ProfilerAgent()
        self.scout = ScoutAgent()
        self.analyst = AnalystAgent()
        self.live_comps = LiveCompsAgent()
        self.stacker = StackerAgent()
        self.closer = CloserAgent()
        self.concierge = ConciergeAgent()
        self.mentor = MentorAgent()
        self.qa = QAAgent()

    async def run_full_pipeline(
        self,
        target_states: Optional[list[str]] = None,
        target_suburbs: Optional[list[str]] = None,
        users: Optional[list[UserProfile]] = None,
        strategy: DealType = DealType.BTL,
        suburb_profiles: Optional[dict[str, SuburbProfile]] = None,
        sold_data: Optional[dict[str, list[Property]]] = None,
        generate_offers: bool = False,
        max_agencies: int = 10,
        use_browser: bool = False,
        investor_profile: Optional[InvestmentProfile] = None,
        user_input: Optional[str] = None,
        enable_stacker: bool = True,
        enable_mentor: bool = True,
        enable_qa: bool = True,
    ) -> PipelineResult:
        """
        Run the complete 9-agent Property Insights pipeline.

        Args:
            target_states: Filter scraping by state
            target_suburbs: Filter for specific suburbs
            users: Users to notify about matches
            strategy: Default investment strategy
            suburb_profiles: Pre-loaded suburb data
            sold_data: Pre-loaded sold property data
            generate_offers: Auto-generate offers for golden opportunities
            max_agencies: Max agencies to scrape per run
            use_browser: Use Playwright (slower, more reliable)
            investor_profile: Pre-built investor profile
            user_input: User's description for profile building
            enable_stacker: Run deal structuring stage
            enable_mentor: Run coaching stage
            enable_qa: Run self-governance stage
        """
        result = PipelineResult()
        logger.info(
            "pipeline_started",
            run_id=result.run_id,
            states=target_states,
            suburbs=target_suburbs,
            stages="Profiler→Scout→Analyst→Stacker→Closer→Concierge→Mentor→QA",
        )

        # ── STAGE 1: PROFILER ──
        profile = investor_profile
        if user_input or not investor_profile:
            logger.info("stage_1_profiler_starting")
            profiler_result = await self.profiler.safe_execute(
                user_input=user_input,
                existing_profile=investor_profile,
                interaction_type="initial" if not investor_profile else "update",
            )
            result.agent_results.append(profiler_result)

            if profiler_result.success and profiler_result.data:
                profile_data = profiler_result.data.get("profile")
                if profile_data and isinstance(profile_data, dict):
                    try:
                        profile = InvestmentProfile(**profile_data)
                    except Exception:
                        profile = investor_profile or InvestmentProfile()
                else:
                    profile = investor_profile or InvestmentProfile()
            else:
                profile = investor_profile or InvestmentProfile()

            logger.info(
                "stage_1_profiler_complete",
                readiness=profile.investor_readiness_score if profile else 0,
            )

        # ── STAGE 2: SCOUT ──
        logger.info("stage_2_scout_starting")
        scout_result = await self.scout.safe_execute(
            target_states=target_states,
            target_suburbs=target_suburbs,
            use_browser=use_browser,
            max_agencies=max_agencies,
        )
        result.agent_results.append(scout_result)

        if not scout_result.success:
            result.errors.append(f"Scout failed: {scout_result.error}")
            if enable_qa:
                await self._run_qa(result)
            result.finalize()
            return result

        properties: list[Property] = scout_result.data.get("properties", [])
        result.properties_found = len(properties)
        logger.info("stage_2_scout_complete", properties_found=len(properties))

        if not properties:
            logger.info("no_properties_found_ending_pipeline")
            if enable_qa:
                await self._run_qa(result)
            result.finalize()
            return result

        # ── STAGE 3: ANALYST ──
        logger.info("stage_3_analyst_starting", properties=len(properties))
        analyst_result = await self.analyst.safe_execute(
            properties=properties,
            suburb_profiles=suburb_profiles,
            sold_data=sold_data,
            strategy=strategy,
        )
        result.agent_results.append(analyst_result)

        if not analyst_result.success:
            result.errors.append(f"Analyst failed: {analyst_result.error}")
            if enable_qa:
                await self._run_qa(result)
            result.finalize()
            return result

        deals: list[Deal] = analyst_result.data.get("deals", [])
        golden: list[Deal] = analyst_result.data.get("golden_opportunities", [])
        result.deals_analyzed = len(deals)
        result.golden_opportunities = len(golden)
        logger.info(
            "stage_3_analyst_complete",
            deals=len(deals),
            golden=len(golden),
        )

        # ── STAGE 4: STACKER (Deal structuring) ──
        if enable_stacker and deals and profile:
            logger.info("stage_4_stacker_starting", deals=len(deals))
            stacker_results_data = []
            for deal in deals[:5]:  # Structure top 5 deals
                try:
                    stacker_result = await self.stacker.safe_execute(
                        deal=deal,
                        profile=profile,
                        include_brrr=True,
                        include_smsf=profile.financial.smsf_balance > 200_000,
                    )
                    result.agent_results.append(stacker_result)
                    if stacker_result.success:
                        stacker_results_data.append(stacker_result.data)
                except Exception as e:
                    result.errors.append(f"Stacker failed for {deal.property.address}: {str(e)}")

            logger.info("stage_4_stacker_complete", structures=len(stacker_results_data))

        # ── STAGE 5: CLOSER (Optional — for golden opportunities) ──
        if generate_offers and golden:
            logger.info("stage_5_closer_starting", golden_count=len(golden))
            for deal in golden[:3]:  # Limit to top 3 golden opportunities
                try:
                    offer_request = OfferGenerationRequest(
                        property_id=deal.property.id,
                        property_address=deal.property.address,
                        asking_price=deal.property.effective_price or 0,
                        buyer_name="PIA User",  # Placeholder
                        buyer_budget_max=(deal.property.effective_price or 0) * 1.1,
                        seller_motivation=self._infer_motivation(deal),
                        preferred_tone=OfferTone.PROFESSIONAL,
                    )
                    closer_result = await self.closer.safe_execute(
                        request=offer_request,
                        deal=deal,
                    )
                    result.agent_results.append(closer_result)
                except Exception as e:
                    result.errors.append(f"Closer failed for {deal.property.address}: {str(e)}")

        # ── STAGE 6: CONCIERGE (Notify users) ──
        if users:
            logger.info("stage_6_concierge_starting", users=len(users), deals=len(deals))
            concierge_result = await self.concierge.safe_execute(
                deals=deals,
                users=users,
            )
            result.agent_results.append(concierge_result)

            if concierge_result.success:
                result.notifications_sent = concierge_result.data.get("total_matched", 0)

            logger.info("stage_6_concierge_complete", notifications=result.notifications_sent)

        # ── STAGE 7: MENTOR (Coaching based on results) ──
        if enable_mentor and deals:
            logger.info("stage_7_mentor_starting")
            try:
                mentor_result = await self.mentor.safe_execute(
                    topic="deal_review",
                    profile=profile,
                    deals=deals[:3],
                )
                result.agent_results.append(mentor_result)
                logger.info("stage_7_mentor_complete")
            except Exception as e:
                result.errors.append(f"Mentor failed: {str(e)}")

        # ── STAGE 8: QA (Self-governance) ──
        if enable_qa:
            await self._run_qa(result)

        result.finalize()
        logger.info(
            "pipeline_completed",
            run_id=result.run_id,
            duration=f"{result.duration_seconds:.1f}s",
            properties=result.properties_found,
            deals=result.deals_analyzed,
            golden=result.golden_opportunities,
            notifications=result.notifications_sent,
            tokens=result.total_tokens,
            stages_run=len(result.agent_results),
        )

        return result

    async def _run_qa(self, result: PipelineResult):
        """Run the QA self-governance stage."""
        logger.info("stage_qa_starting", outputs=len(result.agent_results))
        try:
            qa_result = await self.qa.evaluate_and_improve(
                agent_outputs=result.agent_results,
            )
            result.agent_results.append(qa_result)

            if qa_result.success and qa_result.data:
                qa_data = qa_result.data
                pipeline_health = qa_data.get("pipeline_health", 0)
                skills_generated = qa_data.get("skills_generated_for", [])
                logger.info(
                    "stage_qa_complete",
                    pipeline_health=pipeline_health,
                    skills_generated=skills_generated,
                )
        except Exception as e:
            result.errors.append(f"QA failed: {str(e)}")
            logger.warning("qa_stage_failed", error=str(e))

    async def analyze_single_property(
        self,
        url: str,
        strategy: DealType = DealType.BTL,
        suburb_profile: Optional[SuburbProfile] = None,
        sold_properties: Optional[list[Property]] = None,
        investor_profile: Optional[InvestmentProfile] = None,
    ) -> PipelineResult:
        """
        Analyze a single property by URL — Scout + Analyst + LiveComps + Stacker.

        Ideal for on-demand analysis of a specific listing.
        """
        result = PipelineResult()

        # Scout: Scrape the URL
        scout_result = await self.scout.scrape_single_url(url, use_ai=True)
        result.agent_results.append(scout_result)

        if not scout_result.success or not scout_result.data.get("property"):
            result.errors.append(f"Failed to scrape: {scout_result.error}")
            result.finalize()
            return result

        prop: Property = scout_result.data["property"]
        result.properties_found = 1

        # Analyst: Analyze the property
        analyst_result = await self.analyst.analyze_single(
            prop=prop,
            suburb=suburb_profile,
            sold_properties=sold_properties,
            strategy=strategy,
        )
        result.agent_results.append(analyst_result)

        deal: Optional[Deal] = None
        if analyst_result.success and analyst_result.data.get("deal"):
            deal = analyst_result.data["deal"]
            result.deals_analyzed = 1
            if deal.is_golden_opportunity:
                result.golden_opportunities = 1

        # Live Comps (if sold data available)
        if sold_properties:
            comps_result = await self.live_comps.safe_execute(
                target=prop,
                sold_properties=sold_properties,
            )
            result.agent_results.append(comps_result)

        # Stacker: Structure the deal if we have analysis
        if deal and investor_profile:
            stacker_result = await self.stacker.safe_execute(
                deal=deal,
                profile=investor_profile,
            )
            result.agent_results.append(stacker_result)

        result.finalize()
        return result

    async def generate_offer(
        self,
        deal: Deal,
        buyer_name: str,
        buyer_budget: float,
        buyer_story: Optional[str] = None,
        tone: OfferTone = OfferTone.PROFESSIONAL,
    ) -> AgentResult:
        """Generate an offer document for a specific deal."""
        request = OfferGenerationRequest(
            property_id=deal.property.id,
            property_address=deal.property.address,
            asking_price=deal.property.effective_price or 0,
            buyer_name=buyer_name,
            buyer_budget_max=buyer_budget,
            buyer_story=buyer_story,
            seller_motivation=self._infer_motivation(deal),
            preferred_tone=tone,
        )

        return await self.closer.safe_execute(request=request, deal=deal)

    def _infer_motivation(self, deal: Deal) -> SellerMotivation:
        """Infer seller motivation from property signals."""
        signals = deal.property.distress_signals
        if not signals:
            return SellerMotivation.UNKNOWN

        keywords = {s.keyword.lower() for s in signals}

        if keywords & {"deceased estate", "mortgagee", "mortgagee in possession", "divorce"}:
            return SellerMotivation.DESPERATE
        elif keywords & {"must sell", "urgent sale", "fire sale", "relocating"}:
            return SellerMotivation.MOTIVATED
        elif keywords & {"price reduced", "price slashed", "bring all offers"}:
            return SellerMotivation.MOTIVATED
        else:
            return SellerMotivation.UNKNOWN

    async def cleanup(self):
        """Clean up all agent resources."""
        await self.scout.cleanup()


# ── CLI Entry Point ──────────────────────────────────────────────────────────

async def main():
    """Run the orchestrator from the command line."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    console.print(Panel.fit(
        "[bold cyan]Property Insights Australia[/bold cyan] — Your Digital Property Associate\n"
        "[dim]Investment-Grade Real Estate Intelligence[/dim]",
        border_style="cyan",
    ))

    orchestrator = Orchestrator()

    # Demo: Run with default settings
    console.print("\n[yellow]Starting pipeline...[/yellow]\n")

    result = await orchestrator.run_full_pipeline(
        target_states=["NSW"],
        max_agencies=3,
        use_browser=False,
    )

    # Display results
    table = Table(title="Pipeline Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Run ID", result.run_id[:8])
    table.add_row("Duration", f"{result.duration_seconds:.1f}s")
    table.add_row("Properties Found", str(result.properties_found))
    table.add_row("Deals Analyzed", str(result.deals_analyzed))
    table.add_row("Golden Opportunities", str(result.golden_opportunities))
    table.add_row("Notifications", str(result.notifications_sent))
    table.add_row("Tokens Used", f"{result.total_tokens:,}")
    table.add_row("Errors", str(len(result.errors)))

    console.print(table)

    if result.errors:
        console.print("\n[red]Errors:[/red]")
        for err in result.errors:
            console.print(f"  [dim]• {err}[/dim]")

    await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
