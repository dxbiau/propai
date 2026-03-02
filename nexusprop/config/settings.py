"""
Australian Property Associates — Central configuration loaded from environment.

All Australian-market-specific defaults are tuned here.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AustralianState(str, Enum):
    NSW = "NSW"
    VIC = "VIC"
    QLD = "QLD"
    SA = "SA"
    WA = "WA"
    TAS = "TAS"
    NT = "NT"
    ACT = "ACT"


# ---------------------------------------------------------------------------
# Stamp Duty Brackets by State (2025-2026 Schedule)
#
# Format: (upper_threshold_aud, marginal_rate, base_duty_aud)
#   - upper_threshold: the top of this bracket (exclusive)
#   - marginal_rate:   rate applied to the amount within this bracket
#   - base_duty:       cumulative duty already owed at the BOTTOM of this bracket
#
# ACT uses a flat-rate system (not marginal). Its brackets are handled
# separately in calculate_stamp_duty() — the rate applies to the full price.
# ---------------------------------------------------------------------------
STAMP_DUTY_BRACKETS: dict[str, list[tuple[float, float, float]]] = {
    "NSW": [
        (16_000,        0.0125,  0),
        (35_000,        0.0150,  200),
        (93_000,        0.0175,  485),
        (351_000,       0.0350,  1_500),
        (1_168_000,     0.0450,  10_530),
        (3_505_000,     0.0550,  47_295),
        (float("inf"),  0.0700,  175_830),
    ],
    "VIC": [
        (25_000,        0.014,   0),
        (130_000,       0.024,   350),
        (960_000,       0.06,    2_870),
        (float("inf"),  0.055,   52_670),  # FIX: was 0 — correct base = 2870 + (960000-130000)*0.06
    ],
    "QLD": [
        (5_000,         0.0,     0),
        (75_000,        0.015,   0),
        (540_000,       0.035,   1_050),
        (1_000_000,     0.045,   17_325),
        (float("inf"),  0.0575,  38_025),
    ],
    "SA": [
        (12_000,        0.01,    0),
        (30_000,        0.02,    120),
        (50_000,        0.03,    480),
        (100_000,       0.035,   1_080),
        (200_000,       0.04,    2_830),
        (250_000,       0.045,   6_830),
        (300_000,       0.05,    9_080),
        (500_000,       0.055,   14_080),
        (float("inf"),  0.055,   25_080),
    ],
    "WA": [
        (120_000,       0.019,   0),
        (150_000,       0.0285,  2_280),
        (360_000,       0.038,   3_135),
        (725_000,       0.0515,  11_115),
        (float("inf"),  0.0515,  29_910),
    ],
    "TAS": [
        (3_000,         0.0,     50),    # $50 flat minimum duty
        (25_000,        0.0175,  50),
        (75_000,        0.025,   435),
        (200_000,       0.035,   1_685),
        (375_000,       0.04,    6_060),
        (725_000,       0.0425,  13_060),
        (float("inf"),  0.045,   27_935),
    ],
    "NT": [
        (525_000,       0.0,     0),     # Abolished for owner-occupiers up to $525k
        (3_000_000,     0.0495,  0),
        (5_000_000,     0.0575,  0),
        (float("inf"),  0.0595,  0),
    ],
    # ACT: flat-rate system — duty = purchase_price * rate (NOT marginal)
    # Brackets here are (upper_threshold, flat_rate, unused_base)
    "ACT": [
        (260_000,       0.006,   0),
        (300_000,       0.0227,  0),
        (500_000,       0.0332,  0),
        (750_000,       0.042,   0),
        (1_000_000,     0.0497,  0),
        (1_455_000,     0.0554,  0),
        (float("inf"),  0.07,    0),
    ],
}

# States that use a flat-rate stamp duty system (rate × full purchase price)
_FLAT_RATE_STATES = {"ACT"}

# States where NT stamp duty was abolished for owner-occupiers below threshold
_NT_EXEMPTION_THRESHOLD = 525_000


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Australian Property Associates"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    app_debug: bool = True
    app_port: int = 8001
    secret_key: str = "change-me"

    # --- AI ---
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # --- Ollama (free local LLM) ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    use_ollama: bool = True  # prefer Ollama over Anthropic by default

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./pia.db"
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    # --- Scraping ---
    zenrows_api_key: str = ""
    scrape_interval_minutes: int = 30
    max_concurrent_scrapers: int = 5
    user_agent: str = "AustralianPropertyAssociates/5.1"

    # --- Notifications ---
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
    twilio_sms_from: str = ""
    sendgrid_api_key: str = ""
    from_email: str = "alerts@australianpropertyassociates.com.au"

    # --- Australian Market Defaults ---
    default_interest_rate: float = Field(default=6.25, description="Current variable rate %")
    default_loan_lvr: float = Field(default=80.0, description="Loan-to-Value Ratio %")
    stamp_duty_state: AustralianState = AustralianState.VIC
    council_rate_estimate_pct: float = Field(default=0.3, description="Council rate as % of value")

    # --- Scoring ---
    bargain_score_min: float = 65.0
    golden_opportunity_score: float = 85.0
    distress_delta_threshold: float = 15.0
    min_net_yield: float = 5.0
    min_roi: float = 12.0

    # --- Rate Limiting ---
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # ----- Validators -----

    @field_validator("app_env", mode="before")
    @classmethod
    def normalise_app_env(cls, v: object) -> object:
        """
        Accept common shorthand values for APP_ENV.

        Deployment environments often set APP_ENV=PROD or APP_ENV=DEV.
        This validator normalises them to the canonical enum values before
        Pydantic attempts the enum lookup, preventing a validation crash.
        """
        if isinstance(v, str):
            mapping = {
                "prod": "production",
                "production": "production",
                "dev": "development",
                "development": "development",
                "stage": "staging",
                "staging": "staging",
            }
            normalised = mapping.get(v.lower())
            if normalised:
                return normalised
        return v

    # ----- Computed helpers -----

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnv.PRODUCTION

    @property
    def stamp_duty_brackets(self) -> list[tuple[float, float, float]]:
        state_key = (
            self.stamp_duty_state.value
            if isinstance(self.stamp_duty_state, AustralianState)
            else str(self.stamp_duty_state)
        )
        return STAMP_DUTY_BRACKETS.get(state_key, STAMP_DUTY_BRACKETS["NSW"])

    def calculate_stamp_duty(self, purchase_price: float) -> float:
        """
        Calculate stamp duty for a purchase price in the configured state.

        Two calculation modes are supported:

        **Marginal bracket** (NSW, VIC, QLD, SA, WA, TAS, NT):
            Find the bracket that contains ``purchase_price``, then:
            ``duty = base_duty + (purchase_price - prev_threshold) * rate``

        **Flat-rate** (ACT):
            ``duty = purchase_price * rate``
            where ``rate`` is the flat rate for the bracket the price falls in.
        """
        if purchase_price <= 0:
            return 0.0

        state = (
            self.stamp_duty_state.value
            if isinstance(self.stamp_duty_state, AustralianState)
            else str(self.stamp_duty_state)
        )
        brackets = self.stamp_duty_brackets

        # ACT: flat-rate system
        if state in _FLAT_RATE_STATES:
            for threshold, rate, _ in brackets:
                if purchase_price <= threshold:
                    return round(purchase_price * rate, 2)
            # Fallback: apply highest rate
            return round(purchase_price * brackets[-1][1], 2)

        # All other states: marginal bracket system
        # Walk brackets to find which one the price falls in, then apply
        # base + excess * rate.
        prev_threshold = 0.0
        for threshold, rate, base in brackets:
            if purchase_price <= threshold:
                excess = purchase_price - prev_threshold
                return round(base + excess * rate, 2)
            prev_threshold = threshold

        # Should never reach here (last bracket is always inf), but guard anyway
        _, rate, base = brackets[-1]
        return round(base + (purchase_price - prev_threshold) * rate, 2)


@lru_cache
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
