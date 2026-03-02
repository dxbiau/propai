"""
Investment models — Profiler, Stacker, and Portfolio intelligence.

These models power the new Profiler and Stacker agents with
Australian-specific investment structures, entity types, and
financial capacity scoring.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field


# ── Enums ─────────────────────────────────────────────────────────────────

class RiskTolerance(str, Enum):
    """Investor risk appetite — drives strategy selection."""
    CONSERVATIVE = "conservative"  # Capital preservation, long-term holds
    MODERATE = "moderate"          # Balanced yield + growth
    GROWTH = "growth"              # Capital growth focus, higher leverage
    AGGRESSIVE = "aggressive"      # Value-add, development, creative finance
    SPECULATIVE = "speculative"    # High-risk: off-plan, land banking


class InvestmentGoal(str, Enum):
    """Primary investment objective — determines agent behavior."""
    CASH_FLOW = "cash_flow"           # Passive income
    CAPITAL_GROWTH = "capital_growth"  # Equity appreciation
    BALANCED = "balanced"             # Both
    TAX_MINIMISATION = "tax_minimisation"  # Negative gearing, depreciation
    RETIREMENT = "retirement"         # SMSF, long-term hold
    WEALTH_CREATION = "wealth_creation"  # Portfolio building
    FIRST_HOME = "first_home"         # Owner-occupier first purchase
    SUBDIVISION = "subdivision"       # Develop and sell
    PASSIVE_INCOME = "passive_income" # Replace salary with rental income


class EntityType(str, Enum):
    """Australian investment entity structures."""
    PERSONAL = "personal"           # Individual name
    JOINT = "joint"                 # Joint tenants / tenants in common
    FAMILY_TRUST = "family_trust"   # Discretionary family trust
    UNIT_TRUST = "unit_trust"       # Fixed unit trust
    HYBRID_TRUST = "hybrid_trust"   # Hybrid discretionary/unit trust
    SMSF = "smsf"                   # Self-Managed Super Fund
    COMPANY = "company"             # Pty Ltd company
    BARE_TRUST = "bare_trust"       # Nominee/bare trust for SMSF
    PARTNERSHIP = "partnership"     # Business partnership


class ExperienceLevel(str, Enum):
    """Investor experience tier — determines coaching depth."""
    BEGINNER = "beginner"           # 0 properties, researching
    NOVICE = "novice"               # 1-2 properties owned
    INTERMEDIATE = "intermediate"   # 3-5 properties, understands LVR/yield
    ADVANCED = "advanced"           # 6-10 properties, multi-entity
    EXPERT = "expert"               # 10+ properties, development experience


class FinanceStrategy(str, Enum):
    """Deal structuring strategies for the Stacker agent."""
    STANDARD_IO = "standard_io"     # Interest-only loan
    STANDARD_PI = "standard_pi"     # Principal & interest
    BRRR = "brrr"                   # Buy, Rehab, Rent, Refinance, Repeat
    VENDOR_FINANCE = "vendor_finance"
    JOINT_VENTURE = "joint_venture"
    SMSF_LRBA = "smsf_lrba"       # SMSF Limited Recourse Borrowing
    DEPOSIT_BOND = "deposit_bond"
    EQUITY_RELEASE = "equity_release"  # Cross-collateralise existing equity
    WRAP = "wrap"                   # Installment contract
    OPTION = "option"               # Purchase lease option
    SUBDIVISION_FINANCE = "subdivision_finance"
    CONSTRUCTION = "construction"   # Construction loan


# ── Financial Capacity ────────────────────────────────────────────────────

class IncomeSource(BaseModel):
    """A single income source for borrowing power calculation."""
    source_type: str = Field(..., description="salary, rental, business, dividends, trust_distribution")
    gross_annual: float = Field(ge=0)
    is_primary: bool = False
    shading_pct: float = Field(
        default=100.0, ge=0, le=100,
        description="Bank shading — % of income banks will accept (rental ~80%, self-employed ~60-80%)"
    )

    @computed_field
    @property
    def assessable_income(self) -> float:
        """Income that banks will consider for servicing."""
        return self.gross_annual * (self.shading_pct / 100)


class ExistingLiability(BaseModel):
    """Existing debt that reduces borrowing power."""
    liability_type: str = Field(..., description="home_loan, investment_loan, car_loan, personal_loan, credit_card, hecs")
    outstanding_balance: float = Field(ge=0)
    monthly_repayment: float = Field(ge=0)
    is_investment: bool = False
    interest_rate_pct: float = Field(default=6.5, ge=0)
    remaining_term_years: Optional[int] = None


class FinancialCapacity(BaseModel):
    """Complete financial picture for borrowing power estimation."""

    # --- Income ---
    income_sources: list[IncomeSource] = Field(default_factory=list)

    # --- Existing Liabilities ---
    existing_liabilities: list[ExistingLiability] = Field(default_factory=list)

    # --- Cash Position ---
    cash_available: float = Field(default=0, ge=0, description="Liquid cash for deposits AUD")
    equity_available: float = Field(default=0, ge=0, description="Accessible equity in existing properties AUD")
    smsf_balance: float = Field(default=0, ge=0, description="SMSF balance available for property AUD")

    # --- Servicing Parameters ---
    dependents: int = Field(default=0, ge=0)
    monthly_living_expenses: float = Field(default=3_500, ge=0)
    credit_card_limits: float = Field(default=0, ge=0, description="Total credit card limits (not balance)")

    @computed_field
    @property
    def total_gross_income(self) -> float:
        return sum(s.gross_annual for s in self.income_sources)

    @computed_field
    @property
    def total_assessable_income(self) -> float:
        return sum(s.assessable_income for s in self.income_sources)

    @computed_field
    @property
    def total_existing_debt(self) -> float:
        return sum(l.outstanding_balance for l in self.existing_liabilities)

    @computed_field
    @property
    def total_monthly_commitments(self) -> float:
        return sum(l.monthly_repayment for l in self.existing_liabilities)

    @computed_field
    @property
    def total_deployable_capital(self) -> float:
        """Cash + accessible equity available for next purchase."""
        return self.cash_available + self.equity_available

    @computed_field
    @property
    def estimated_borrowing_power(self) -> float:
        """
        Simplified Australian bank borrowing power estimate.

        Formula: (Assessable Monthly Income - Commitments - Living Expenses - Buffer) × Multiplier
        Buffer rate: APRA requires banks to stress-test at +3% above rate.
        Typical multiplier: 5-6× net monthly surplus at assessment rate.

        This is an ESTIMATE — actual borrowing power depends on the specific lender.
        """
        monthly_assessable = self.total_assessable_income / 12

        # Living expenses (HEM benchmark or actual, whichever higher)
        hem_estimate = 2_500 + (self.dependents * 700)
        living = max(self.monthly_living_expenses, hem_estimate)

        # Credit card limit serviced at 3% of limit (APRA requirement)
        cc_servicing = self.credit_card_limits * 0.03

        # Monthly surplus
        surplus = monthly_assessable - self.total_monthly_commitments - living - cc_servicing

        if surplus <= 0:
            return 0.0

        # Assessment rate: current rate + 3% buffer (APRA)
        assessment_rate = 9.25  # 6.25% + 3% buffer
        monthly_rate = assessment_rate / 100 / 12

        # Borrowing power = surplus / monthly rate factor over 30 years
        # PV of annuity formula: P = PMT × [(1 - (1+r)^-n) / r]
        n = 30 * 12  # 30 year term in months
        if monthly_rate > 0:
            annuity_factor = (1 - (1 + monthly_rate) ** -n) / monthly_rate
            borrowing = surplus * annuity_factor
        else:
            borrowing = surplus * n

        return round(max(borrowing, 0), 0)


# ── Investment Profile ────────────────────────────────────────────────────

class InvestmentProfile(BaseModel):
    """
    The investor's complete profile — built by the Profiler agent.

    Captures financial capacity, goals, experience, entity structure,
    and strategy preferences. Updated continuously from user interactions.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Investor Identity ---
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    primary_goal: InvestmentGoal = InvestmentGoal.BALANCED
    secondary_goals: list[InvestmentGoal] = Field(default_factory=list)

    # --- Entity Structure ---
    preferred_entity: EntityType = EntityType.PERSONAL
    available_entities: list[EntityType] = Field(default_factory=lambda: [EntityType.PERSONAL])
    has_accountant: bool = False
    has_mortgage_broker: bool = False
    has_solicitor: bool = False

    # --- Financial Capacity ---
    financial: FinancialCapacity = Field(default_factory=FinancialCapacity)

    # --- Portfolio ---
    current_portfolio_count: int = Field(default=0, ge=0)
    current_portfolio_value: float = Field(default=0, ge=0)
    current_portfolio_debt: float = Field(default=0, ge=0)
    target_portfolio_count: int = Field(default=5, ge=0)
    target_portfolio_value: float = Field(default=2_000_000, ge=0)
    target_annual_passive_income: float = Field(default=50_000, ge=0)

    # --- Strategy Preferences ---
    preferred_strategies: list[FinanceStrategy] = Field(
        default_factory=lambda: [FinanceStrategy.STANDARD_IO]
    )
    min_acceptable_yield: float = Field(default=5.0, ge=0)
    max_acceptable_lvr: float = Field(default=80.0, ge=0, le=100)
    comfortable_with_negative_gearing: bool = True
    interested_in_development: bool = False
    interested_in_commercial: bool = False

    # --- Profiler Scoring ---
    profile_completeness_pct: float = Field(default=0, ge=0, le=100)
    investor_readiness_score: float = Field(default=0, ge=0, le=100)
    last_profiled_at: Optional[datetime] = None

    @computed_field
    @property
    def current_portfolio_equity(self) -> float:
        return max(self.current_portfolio_value - self.current_portfolio_debt, 0)

    @computed_field
    @property
    def current_portfolio_lvr(self) -> float:
        if self.current_portfolio_value == 0:
            return 0.0
        return round((self.current_portfolio_debt / self.current_portfolio_value) * 100, 1)

    @computed_field
    @property
    def max_next_purchase(self) -> float:
        """Maximum price for the next property given current capacity."""
        deposit_capacity = self.financial.total_deployable_capital
        borrowing = self.financial.estimated_borrowing_power
        # Max purchase = deposit / (1 - LVR) but capped by borrowing
        if self.max_acceptable_lvr >= 100:
            return borrowing
        deposit_ratio = 1 - (self.max_acceptable_lvr / 100)
        max_from_deposit = deposit_capacity / deposit_ratio if deposit_ratio > 0 else 0
        return min(max_from_deposit, borrowing + deposit_capacity)


# ── Deal Structure (Stacker Output) ──────────────────────────────────────

class DealStructure(BaseModel):
    """
    A structured investment scenario — output of the Stacker agent.

    Packages a property + strategy + entity + financing into
    an actionable investment plan with projected returns.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Source ---
    deal_id: Optional[UUID] = None
    property_id: Optional[UUID] = None

    # --- Structure ---
    strategy: FinanceStrategy
    entity_type: EntityType
    strategy_name: str = Field(default="", description="Human-readable strategy name")

    # --- Financing ---
    purchase_price: float = Field(ge=0)
    deposit_required: float = Field(ge=0)
    deposit_source: str = Field(default="cash", description="cash, equity_release, smsf, jv_partner")
    loan_amount: float = Field(ge=0)
    lvr_pct: float = Field(ge=0, le=100)
    interest_rate_pct: float = Field(default=6.25)
    loan_type: str = Field(default="interest_only", description="interest_only, principal_interest")
    loan_term_years: int = Field(default=30)

    # --- Costs ---
    stamp_duty: float = Field(default=0, ge=0)
    legal_costs: float = Field(default=3_000, ge=0)
    renovation_budget: float = Field(default=0, ge=0)
    other_costs: float = Field(default=0, ge=0)

    # --- Projected Returns ---
    projected_weekly_rent: float = Field(default=0, ge=0)
    projected_annual_income: float = Field(default=0, ge=0)
    projected_annual_expenses: float = Field(default=0, ge=0)
    projected_annual_cashflow: float = Field(default=0)
    projected_gross_yield_pct: float = Field(default=0)
    projected_net_yield_pct: float = Field(default=0)
    projected_5yr_capital_growth_pct: float = Field(default=0)
    projected_5yr_equity_gain: float = Field(default=0)

    # --- Tax ---
    estimated_annual_depreciation: float = Field(default=0, ge=0)
    estimated_tax_benefit: float = Field(default=0, ge=0)
    effective_after_tax_cashflow: float = Field(default=0)

    # --- Risk ---
    risk_rating: str = Field(default="moderate", description="low, moderate, high, very_high")
    risk_factors: list[str] = Field(default_factory=list)
    mitigation_strategies: list[str] = Field(default_factory=list)

    # --- SMSF Specific ---
    smsf_compliant: bool = Field(default=False)
    smsf_lrba_required: bool = Field(default=False)
    smsf_single_acquirable_asset: bool = Field(default=True)

    # --- BRRR Specific ---
    after_repair_value: float = Field(default=0, ge=0)
    forced_equity_gain: float = Field(default=0, ge=0)
    refinance_at_pct: float = Field(default=80.0)

    # --- AI Summary ---
    ai_summary: str = Field(default="")
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def total_capital_required(self) -> float:
        return self.deposit_required + self.stamp_duty + self.legal_costs + self.renovation_budget + self.other_costs

    @computed_field
    @property
    def cash_on_cash_return_pct(self) -> float:
        if self.total_capital_required == 0:
            return 0.0
        return round((self.projected_annual_cashflow / self.total_capital_required) * 100, 2)

    @computed_field
    @property
    def total_return_year1_pct(self) -> float:
        """Total return including cashflow + tax benefit + projected growth."""
        if self.total_capital_required == 0:
            return 0.0
        annual_growth = self.purchase_price * (self.projected_5yr_capital_growth_pct / 100 / 5)
        total_return = self.projected_annual_cashflow + self.estimated_tax_benefit + annual_growth
        return round((total_return / self.total_capital_required) * 100, 2)


# ── Portfolio Model ───────────────────────────────────────────────────────

class PortfolioProperty(BaseModel):
    """A property in the investor's portfolio."""
    property_id: Optional[UUID] = None
    address: str = ""
    suburb: str = ""
    state: str = ""
    property_type: str = "house"
    purchase_price: float = Field(default=0, ge=0)
    purchase_date: Optional[datetime] = None
    current_value: float = Field(default=0, ge=0)
    outstanding_loan: float = Field(default=0, ge=0)
    weekly_rent: float = Field(default=0, ge=0)
    entity: EntityType = EntityType.PERSONAL
    strategy: FinanceStrategy = FinanceStrategy.STANDARD_IO

    @computed_field
    @property
    def equity(self) -> float:
        return max(self.current_value - self.outstanding_loan, 0)

    @computed_field
    @property
    def lvr_pct(self) -> float:
        if self.current_value == 0:
            return 0.0
        return round((self.outstanding_loan / self.current_value) * 100, 1)

    @computed_field
    @property
    def gross_yield_pct(self) -> float:
        if self.current_value == 0:
            return 0.0
        return round((self.weekly_rent * 52 / self.current_value) * 100, 2)


class Portfolio(BaseModel):
    """The investor's complete portfolio — tracked by the Mentor agent."""

    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    properties: list[PortfolioProperty] = Field(default_factory=list)

    @computed_field
    @property
    def total_value(self) -> float:
        return sum(p.current_value for p in self.properties)

    @computed_field
    @property
    def total_debt(self) -> float:
        return sum(p.outstanding_loan for p in self.properties)

    @computed_field
    @property
    def total_equity(self) -> float:
        return self.total_value - self.total_debt

    @computed_field
    @property
    def portfolio_lvr_pct(self) -> float:
        if self.total_value == 0:
            return 0.0
        return round((self.total_debt / self.total_value) * 100, 1)

    @computed_field
    @property
    def total_weekly_rent(self) -> float:
        return sum(p.weekly_rent for p in self.properties)

    @computed_field
    @property
    def total_annual_income(self) -> float:
        return self.total_weekly_rent * 52

    @computed_field
    @property
    def avg_gross_yield_pct(self) -> float:
        if self.total_value == 0:
            return 0.0
        return round((self.total_annual_income / self.total_value) * 100, 2)

    @computed_field
    @property
    def property_count(self) -> int:
        return len(self.properties)


# ── QA Scoring Models ─────────────────────────────────────────────────────

class AgentPerformanceScore(BaseModel):
    """Score from the QA agent evaluating another agent's output."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # --- What was evaluated ---
    agent_name: str
    task_type: str = Field(description="e.g., property_analysis, deal_scoring, offer_generation")
    run_id: Optional[str] = None

    # --- Quality Dimensions (0-100) ---
    accuracy_score: float = Field(ge=0, le=100, description="Factual correctness")
    relevance_score: float = Field(ge=0, le=100, description="Relevance to user query")
    completeness_score: float = Field(ge=0, le=100, description="Coverage of required info")
    timeliness_score: float = Field(ge=0, le=100, description="Speed of execution")
    actionability_score: float = Field(ge=0, le=100, description="How actionable is the output")

    # --- Weighted Overall ---
    overall_score: float = Field(ge=0, le=100)

    # --- Feedback ---
    issues_found: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    skill_gap_identified: Optional[str] = None

    @classmethod
    def calculate(
        cls,
        agent_name: str,
        task_type: str,
        accuracy: float,
        relevance: float,
        completeness: float,
        timeliness: float,
        actionability: float,
        issues: list[str] | None = None,
        suggestions: list[str] | None = None,
        run_id: str | None = None,
    ) -> AgentPerformanceScore:
        """Factory method with weighted scoring."""
        overall = (
            accuracy * 0.30
            + relevance * 0.20
            + completeness * 0.20
            + timeliness * 0.10
            + actionability * 0.20
        )
        return cls(
            agent_name=agent_name,
            task_type=task_type,
            accuracy_score=accuracy,
            relevance_score=relevance,
            completeness_score=completeness,
            timeliness_score=timeliness,
            actionability_score=actionability,
            overall_score=round(overall, 1),
            issues_found=issues or [],
            improvement_suggestions=suggestions or [],
            run_id=run_id,
        )


class SkillTemplate(BaseModel):
    """
    An evolved prompt/skill template generated by the QA self-governance engine.

    When the QA agent detects poor performance, it generates improved
    skill templates that replace the underperforming prompts.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    agent_name: str
    task_type: str
    version: int = Field(default=1, ge=1)

    # --- The Skill ---
    system_prompt: str = Field(description="Improved system prompt for the agent")
    few_shot_examples: list[dict] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict, description="Tuned parameters (temperature, etc.)")

    # --- Performance ---
    avg_score_before: float = Field(ge=0, le=100)
    avg_score_after: Optional[float] = Field(None, ge=0, le=100)
    is_active: bool = True

    # --- Governance ---
    approved_by: str = Field(default="qa_auto", description="qa_auto or human_review")
    rollback_if_below: float = Field(default=60, ge=0, le=100, description="Auto-rollback threshold")
