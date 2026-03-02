"""
Due Diligence API — Section 32 and Contract of Sale analysis endpoints.

Accepts document text and returns AI-powered risk assessments
covering covenants, easements, planning overlays, strata issues, and more.
"""

from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class DueDiligenceRequest(BaseModel):
    """Request to analyse a legal document."""
    document_text: str = Field(..., min_length=50, max_length=200_000,
                               description="Full text of Section 32, Contract of Sale, or strata report.")
    document_type: str = Field(default="section_32",
                               description="One of: section_32, contract_of_sale, strata_report")
    additional_context: Optional[str] = Field(None, max_length=2000,
                                              description="Specific concerns or plans (e.g. 'planning to subdivide').")


class DueDiligenceResponse(BaseModel):
    """Results of the due diligence analysis."""
    risk_level: str = Field(..., description="Overall risk level: LOW, MEDIUM, HIGH, CRITICAL")
    flags_found: int = Field(..., description="Total number of red flags detected")
    categories_flagged: list[str] = Field(default_factory=list,
                                          description="List of risk categories that matched")
    analysis: str = Field(..., description="Detailed AI analysis text")
    keyword_hits: dict[str, list[str]] = Field(default_factory=dict,
                                                description="Keywords matched per category")
    document_type: str = Field(...)
    disclaimer: str = Field(default="RISK ASSESSMENT ONLY — NOT LEGAL ADVICE. "
                            "Always engage a qualified solicitor before purchasing property.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=DueDiligenceResponse)
async def analyze_document(request: DueDiligenceRequest):
    """
    Analyse a legal document (Section 32, Contract of Sale, or Strata Report)
    for red flags and risk factors.

    Pricing: $99 per report (enforcement handled at subscription middleware layer).
    """
    from nexusprop.agents.due_diligence import DueDiligenceBot

    logger.info("dd_analyze_request",
                doc_type=request.document_type,
                text_length=len(request.document_text))

    try:
        bot = DueDiligenceBot()
        result = await bot.execute(
            document_text=request.document_text,
            document_type=request.document_type,
            additional_context=request.additional_context,
        )

        # Parse the agent result into our response schema
        return DueDiligenceResponse(
            risk_level=result.get("risk_level", "MEDIUM"),
            flags_found=result.get("flags_found", 0),
            categories_flagged=result.get("categories_flagged", []),
            analysis=result.get("analysis", "Analysis unavailable."),
            keyword_hits=result.get("keyword_hits", {}),
            document_type=request.document_type,
        )

    except Exception as e:
        logger.error("dd_analyze_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Due diligence analysis failed: {e}")
