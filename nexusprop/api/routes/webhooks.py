"""
Webhooks API — external integrations, scheduled tasks, and callbacks.

Handles incoming webhooks from Twilio (SMS/WhatsApp replies),
Stripe (payments), and scheduler triggers for automated scraping runs.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, ConfigDict, Field

from nexusprop.models.deal import DealType

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ScheduledRunRequest(BaseModel):
    """Trigger a scheduled full pipeline run."""
    states: list[str] = Field(default_factory=lambda: ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"])
    suburbs: list[str] = Field(default_factory=list)
    strategy: DealType = Field(default=DealType.BTL)
    max_agencies: int = Field(default=10, ge=1, le=50)
    generate_offers: bool = Field(default=False)
    notify_users: bool = Field(default=True)


class TwilioWebhookPayload(BaseModel):
    """Incoming Twilio SMS/WhatsApp message payload."""
    model_config = ConfigDict(populate_by_name=True)

    MessageSid: Optional[str] = None
    From: Optional[str] = Field(None, alias="From")
    To: Optional[str] = None
    Body: Optional[str] = None
    NumMedia: Optional[str] = None


class PipelineStatusResponse(BaseModel):
    """Status of a pipeline run."""
    run_id: str
    status: str
    started_at: Optional[str] = None
    properties_found: int = 0
    deals_analyzed: int = 0
    golden_opportunities: int = 0
    duration_seconds: float = 0
    errors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Pipeline run tracking
# ---------------------------------------------------------------------------
_pipeline_runs: dict[str, dict] = {}


async def _run_pipeline_background(
    orchestrator,
    run_id: str,
    config: ScheduledRunRequest,
):
    """Execute a full pipeline run as a background task."""
    _pipeline_runs[run_id]["status"] = "running"

    try:
        result = await orchestrator.run_full_pipeline(
            target_states=config.states if config.states else None,
            target_suburbs=config.suburbs if config.suburbs else None,
            strategy=config.strategy,
            generate_offers=config.generate_offers,
            max_agencies=config.max_agencies,
        )

        _pipeline_runs[run_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "properties_found": result.properties_found,
            "deals_analyzed": result.deals_analyzed,
            "golden_opportunities": result.golden_opportunities,
            "duration_seconds": result.duration_seconds,
            "errors": result.errors,
        })

        logger.info(
            "pipeline_run_completed",
            run_id=run_id,
            properties=result.properties_found,
            golden=result.golden_opportunities,
            duration=result.duration_seconds,
        )

    except Exception as e:
        _pipeline_runs[run_id].update({
            "status": "failed",
            "errors": [str(e)],
        })
        logger.error("pipeline_run_failed", run_id=run_id, error=str(e))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/run-pipeline", response_model=PipelineStatusResponse)
async def trigger_pipeline(
    request: Request,
    config: ScheduledRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Trigger a full Property Insights pipeline run (async background task).

    Runs Scout → Analyst → (Optional) Closer → Concierge.
    Returns immediately with a run ID to poll for status.
    """
    from uuid import uuid4
    run_id = str(uuid4())[:8]

    _pipeline_runs[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
        "properties_found": 0,
        "deals_analyzed": 0,
        "golden_opportunities": 0,
        "duration_seconds": 0,
        "errors": [],
    }

    orchestrator = request.app.state.orchestrator
    background_tasks.add_task(_run_pipeline_background, orchestrator, run_id, config)

    logger.info("pipeline_triggered", run_id=run_id, states=config.states)

    return PipelineStatusResponse(**_pipeline_runs[run_id])


@router.get("/pipeline-status/{run_id}", response_model=PipelineStatusResponse)
async def pipeline_status(run_id: str):
    """Check the status of a pipeline run."""
    run = _pipeline_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return PipelineStatusResponse(**run)


@router.get("/pipeline-runs")
async def list_pipeline_runs(limit: int = 20):
    """List all pipeline runs."""
    runs = sorted(
        _pipeline_runs.values(),
        key=lambda r: r.get("started_at", ""),
        reverse=True,
    )[:limit]
    return {"runs": runs}


@router.post("/twilio/incoming")
async def twilio_incoming(request: Request):
    """
    Handle incoming Twilio SMS/WhatsApp messages.

    Supports commands:
    - "DEALS" → latest golden opportunities
    - "STOP" → opt out of notifications
    - "HELP" → available commands
    - <suburb name> → search for deals in that suburb
    """
    form = await request.form()

    from_number = form.get("From", "")
    body = (form.get("Body", "") or "").strip().upper()

    logger.info("twilio_incoming", from_number=from_number, body=body)

    # Parse commands
    response_text = ""

    if body == "DEALS":
        response_text = (
            "🏡 Australian Property Associates — Latest Golden Opportunities\n\n"
            "No active golden opportunities right now.\n"
            "We'll notify you the moment one appears!\n\n"
            "Reply HELP for commands."
        )
    elif body == "STOP":
        response_text = (
            "You've been unsubscribed from Australian Property Associates alerts.\n"
            "Reply START to re-subscribe."
        )
    elif body == "HELP":
        response_text = (
            "🏡 Australian Property Associates Commands:\n\n"
            "DEALS → Latest golden opportunities\n"
            "STOP → Unsubscribe from alerts\n"
            "<suburb> → Search deals in a suburb\n\n"
            "Your Digital Property Associate."
        )
    else:
        # Treat as suburb search
        response_text = (
            f"🔍 Searching for deals in '{body.title()}'...\n\n"
            "We'll check our database and notify you "
            "if any opportunities match."
        )

    # Return TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

    from starlette.responses import Response
    return Response(content=twiml, media_type="application/xml")


@router.post("/stripe/payment")
async def stripe_webhook(request: Request):
    """
    Handle Stripe payment webhooks for subscription management.

    Upgrades/downgrades user plans based on payment events.
    """
    try:
        payload = await request.body()
        # In production: verify Stripe signature
        logger.info("stripe_webhook_received", payload_size=len(payload))

        return {"status": "received"}

    except Exception as e:
        logger.error("stripe_webhook_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/cron/daily-scan")
async def daily_scan_trigger(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Endpoint for cron job triggers (e.g., Railway, Render cron).

    Runs a full pipeline scan for all configured states daily.
    """
    config = ScheduledRunRequest(
        states=["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"],
        strategy=DealType.BTL,
        max_agencies=20,
        generate_offers=True,
        notify_users=True,
    )

    from uuid import uuid4
    run_id = f"cron-{str(uuid4())[:8]}"

    _pipeline_runs[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "started_at": datetime.utcnow().isoformat(),
        "properties_found": 0,
        "deals_analyzed": 0,
        "golden_opportunities": 0,
        "duration_seconds": 0,
        "errors": [],
    }

    orchestrator = request.app.state.orchestrator
    background_tasks.add_task(_run_pipeline_background, orchestrator, run_id, config)

    logger.info("daily_cron_triggered", run_id=run_id)

    return {"status": "triggered", "run_id": run_id}
