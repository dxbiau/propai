"""
Photo Enhancement API routes.

Endpoints for AI-powered property photo polishing.
All processing uses free tools (Pillow + optional Real-ESRGAN).
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from nexusprop.agents.photo_enhancer import PhotoEnhancementAgent, ENHANCEMENT_PRESETS

router = APIRouter()

_photo_agent = PhotoEnhancementAgent()


class PhotoEnhanceRequest(BaseModel):
    """Request to enhance a photo by URL."""
    image_url: str = Field(..., description="URL of the image to enhance")
    preset: str = Field(default="real_estate_standard", description="Enhancement preset")
    upscale: bool = Field(default=False, description="Whether to AI-upscale")
    upscale_factor: int = Field(default=2, ge=2, le=4, description="Upscale multiplier")


class BatchEnhanceRequest(BaseModel):
    """Batch photo enhancement request."""
    image_urls: list[str] = Field(..., description="List of image URLs")
    preset: str = Field(default="real_estate_standard")
    upscale: bool = Field(default=False)


@router.get("/presets")
async def list_presets():
    """List available photo enhancement presets."""
    return {
        "presets": PhotoEnhancementAgent.get_presets(),
        "default": "real_estate_standard",
    }


@router.post("/enhance-url")
async def enhance_from_url(request: PhotoEnhanceRequest):
    """Enhance a property photo from a URL."""
    result = await _photo_agent.safe_execute(
        image_url=request.image_url,
        preset=request.preset,
        upscale=request.upscale,
        upscale_factor=request.upscale_factor,
        return_base64=True,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result.data


@router.post("/enhance-upload")
async def enhance_uploaded(
    file: UploadFile = File(...),
    preset: str = Form(default="real_estate_standard"),
    upscale: bool = Form(default=False),
):
    """Enhance an uploaded property photo."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()
    if len(image_data) > 20 * 1024 * 1024:  # 20MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 20MB)")

    result = await _photo_agent.safe_execute(
        image_data=image_data,
        preset=preset,
        upscale=upscale,
        return_base64=True,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result.data


@router.post("/batch")
async def batch_enhance(request: BatchEnhanceRequest):
    """Enhance multiple property photos in parallel."""
    if len(request.image_urls) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 images per batch")

    result = await _photo_agent.batch_enhance(
        image_urls=request.image_urls,
        preset=request.preset,
        upscale=request.upscale,
    )

    return result.data


@router.post("/analyze")
async def analyze_photo_quality(file: UploadFile = File(...)):
    """Analyze a photo's quality and suggest enhancement preset."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()
    analysis = await _photo_agent.analyze_photo_quality(image_data)
    return analysis
