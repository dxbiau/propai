"""Australian Property Associates API - FastAPI Application.

The RESTful gateway to the APA Agentic Intelligence Stack.
Exposes property search, deal analysis, offer generation, and pipeline
orchestration endpoints.

Persistence: SQLite file-based DB (pia.db) - data survives restarts.
Auto-Scout: Background task discovers new properties every 15-30 min.

Run:
    uvicorn nexusprop.api.main:app --reload --port 8001
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from nexusprop.config.settings import get_settings

from nexusprop.api.routes.properties import router as properties_router
from nexusprop.api.routes.deals import router as deals_router
from nexusprop.api.routes.offers import router as offers_router
from nexusprop.api.routes.webhooks import router as webhooks_router
from nexusprop.api.routes.due_diligence import router as dd_router
from nexusprop.api.routes.negotiation import router as negotiation_router
from nexusprop.api.routes.subscriptions import router as subscriptions_router
from nexusprop.api.routes.profiler import router as profiler_router
from nexusprop.api.routes.stacker import router as stacker_router
from nexusprop.api.routes.mentor import router as mentor_router
from nexusprop.api.routes.qa import router as qa_router
from nexusprop.api.routes.photos import router as photos_router
from nexusprop.api.routes.recommendations import router as recommendations_router
from nexusprop.api.routes.chatbot import router as chatbot_router
from nexusprop.api.routes.market import router as market_router
from nexusprop.api.routes.research import router as research_router
from nexusprop.api.routes.suburb_intelligence import router as suburb_intelligence_router
from nexusprop.api.routes.investor_profiler import router as investor_profiler_router
from nexusprop.api.routes.reno_vision import router as reno_vision_router
from nexusprop.api.middleware import RequestLoggingMiddleware, RateLimitMiddleware

logger = structlog.get_logger(__name__)
settings = get_settings()

# Background task handle — cancelled on shutdown
_scout_task: asyncio.Task | None = None


# ---------------------------------------------------------------------------
# Application Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    global _scout_task

    logger.info(
        "pia_api_starting",
        env=settings.app_env.value,
        port=settings.app_port,
    )
    # Register the orchestrator as app state for shared access
    from nexusprop.orchestrator.orchestrator import Orchestrator
    app.state.orchestrator = Orchestrator()
    app.state.startup_time = datetime.utcnow()

    # ----- 1. Initialise SQLite persistence -----
    from nexusprop.db import (
        init_db,
        load_all_properties,
        load_all_deals,
        load_all_offers,
        save_properties_bulk,
        save_deals_bulk,
        db_stats,
    )

    init_db()  # creates pia.db / opens existing

    # ----- 2. Load persisted data into in-memory stores -----
    from nexusprop.api.routes.properties import _property_store
    from nexusprop.api.routes.deals import _deal_store
    from nexusprop.api.routes.offers import _offer_store

    db_props = load_all_properties()
    db_deals = load_all_deals()
    db_offers = load_all_offers()

    _property_store.update(db_props)
    _deal_store.update(db_deals)
    _offer_store.update(db_offers)

    logger.info(
        "db_data_loaded",
        properties=len(db_props),
        deals=len(db_deals),
        offers=len(db_offers),
    )

    # ----- 3. Seed ONLY if DB was empty (first run) -----
    if len(db_props) == 0:
        from nexusprop.seed_data import generate_seed_properties, generate_seed_deals

        seed_props = generate_seed_properties()
        for prop in seed_props:
            _property_store[str(prop.id)] = prop

        seed_deals = generate_seed_deals(seed_props)
        for deal in seed_deals:
            _deal_store[str(deal.id)] = deal

        # Persist seed data so next restart is instant
        save_properties_bulk(seed_props)
        save_deals_bulk(seed_deals)

        logger.info(
            "seed_data_persisted",
            properties=len(seed_props),
            deals=len(seed_deals),
        )
    else:
        logger.info("seed_skipped_db_has_data")

    # ----- 4. Start auto-scout background task -----
    from nexusprop.auto_scout import auto_scout_loop

    _scout_task = asyncio.create_task(
        auto_scout_loop(
            property_store=_property_store,
            deal_store=_deal_store,
            interval_minutes=settings.scrape_interval_minutes,
        )
    )
    logger.info(
        "auto_scout_scheduled",
        interval_minutes=settings.scrape_interval_minutes,
    )

    stats = db_stats()
    logger.info("startup_complete", **stats)

    yield

    # ----- Shutdown -----
    if _scout_task and not _scout_task.done():
        _scout_task.cancel()
        try:
            await _scout_task
        except asyncio.CancelledError:
            pass
    logger.info("pia_api_shutdown")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Australian Property Associates API",
    description=(
        "Your Digital Property Associate - Investment-Grade Real Estate Intelligence. "
        "The Bloomberg Terminal for Australian Property - All 8 States & Territories. "
        "15 AI Agents | Climate Risk Profiling | Personal Research."
    ),
    version="5.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://australianpropertyassociates.com.au"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(properties_router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(deals_router, prefix="/api/v1/deals", tags=["Deals"])
app.include_router(offers_router, prefix="/api/v1/offers", tags=["Offers"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(dd_router, prefix="/api/v1/due-diligence", tags=["Due Diligence"])
app.include_router(negotiation_router, prefix="/api/v1/negotiation", tags=["Negotiation"])
app.include_router(subscriptions_router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(profiler_router, prefix="/api/v1/profiler", tags=["Profiler"])
app.include_router(stacker_router, prefix="/api/v1/stacker", tags=["Deal Structuring"])
app.include_router(mentor_router, prefix="/api/v1/mentor", tags=["Mentor & Coaching"])
app.include_router(qa_router, prefix="/api/v1/qa", tags=["QA & Self-Governance"])
app.include_router(photos_router, prefix="/api/v1/photos", tags=["Photo Enhancement"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Competitive Edge"])
app.include_router(chatbot_router, prefix="/api/v1/chat", tags=["Chatbot & News"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(research_router, prefix="/api/v1/research", tags=["Personal Research"])
app.include_router(suburb_intelligence_router, prefix="/api/v1/suburb-intelligence", tags=["Suburb Intelligence"])
app.include_router(investor_profiler_router, prefix="/api/v1/investor-profiler", tags=["Investor Profiler"])
app.include_router(reno_vision_router, prefix="/api/v1/reno-vision", tags=["AI Reno Vision"])


# ---------------------------------------------------------------------------
# Root & Health Endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    """API root — branding and version info."""
    return {
        "name": "Australian Property Associates",
        "tagline": "Your Digital Property Associate - All of Australia",
        "version": "5.2.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Health check endpoint for load balancers and monitoring."""
    from nexusprop.db import db_stats, get_scout_history

    uptime = None
    if hasattr(request.app.state, "startup_time"):
        uptime = (datetime.utcnow() - request.app.state.startup_time).total_seconds()

    scout_history = get_scout_history(limit=5)

    return {
        "status": "healthy",
        "environment": settings.app_env.value,
        "uptime_seconds": uptime,
        "persistence": db_stats(),
        "auto_scout": {
            "active": _scout_task is not None and not _scout_task.done(),
            "interval_minutes": settings.scrape_interval_minutes,
            "recent_runs": scout_history,
        },
        "services": {
            "ollama": settings.use_ollama,
            "anthropic": bool(settings.anthropic_api_key),
            "supabase": bool(settings.supabase_url and settings.supabase_key),
            "twilio": bool(settings.twilio_account_sid),
            "sendgrid": bool(settings.sendgrid_api_key),
            "zenrows": bool(settings.zenrows_api_key),
            "sqlite": True,
        },
    }


@app.get("/api/v1/config", tags=["Config"])
async def get_config():
    """Return non-sensitive platform configuration."""
    return {
        "scoring": {
            "bargain_score_min": settings.bargain_score_min,
            "golden_opportunity_score": settings.golden_opportunity_score,
            "distress_delta_threshold": settings.distress_delta_threshold,
            "min_net_yield": settings.min_net_yield,
            "min_roi": settings.min_roi,
        },
        "market_defaults": {
            "interest_rate_pct": settings.default_interest_rate,
            "loan_lvr_pct": settings.default_loan_lvr,
            "stamp_duty_state": settings.stamp_duty_state.value,
            "council_rate_estimate_pct": settings.council_rate_estimate_pct,
        },
    }


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.app_debug else "An unexpected error occurred.",
        },
    )


# ---------------------------------------------------------------------------
# Static File Serving — Frontend
# ---------------------------------------------------------------------------
_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

app.mount("/static", StaticFiles(directory=str(_frontend_dir / "static")), name="static")


@app.get("/terminal", include_in_schema=False)
async def terminal_dashboard():
    """Serve the Bloomberg Terminal-style dashboard."""
    return FileResponse(str(_frontend_dir / "index.html"))


@app.get("/landing", include_in_schema=False)
async def landing_page():
    """Serve the marketing landing page."""
    return FileResponse(str(_frontend_dir / "landing.html"))
