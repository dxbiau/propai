"""
Photo Enhancement Agent — AI-powered property photo polishing.

Automatically enhances, upscales, and polishes property listing photos
using 100% free tools:

1. Pillow (PIL) — brightness, contrast, sharpness, color correction
2. OpenCV + inpainting — watermark detection and removal
3. LANCZOS upscaling — high-quality resize (Real-ESRGAN optional)
4. Real-ESRGAN via local API — AI upscaling (optional, requires model download)

Fallback: Pure Pillow processing works without any AI models installed.

The goal: Take ugly, dark, poorly-shot listing photos and make them
look like professional real estate photography — automatically.
"""

from __future__ import annotations

import asyncio
import base64
import io
import random
from pathlib import Path
from typing import Optional

import httpx
import structlog

from nexusprop.agents.base import AgentResult, BaseAgent

logger = structlog.get_logger(__name__)


# ── Rotating browser-like User-Agents for image fetching ─────────────────────

_IMAGE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# Known real estate CDN domains — used to set correct Referer header
_REALESTATE_CDN_REFERERS = {
    "domain.com.au": "https://www.domain.com.au/",
    "realestate.com.au": "https://www.realestate.com.au/",
    "homely.com.au": "https://www.homely.com.au/",
    "ratemyagent.com.au": "https://www.ratemyagent.com.au/",
    "allhomes.com.au": "https://www.allhomes.com.au/",
    "raywhite.com": "https://raywhite.com/",
    "ljhooker.com.au": "https://ljhooker.com.au/",
    "harcourts.com.au": "https://harcourts.com.au/",
}


# ── Enhancement Presets ───────────────────────────────────────────────────────

ENHANCEMENT_PRESETS = {
    "real_estate_standard": {
        "brightness": 1.15,
        "contrast": 1.20,
        "color": 1.12,
        "sharpness": 1.30,
        "auto_wb": True,
        "sky_enhance": True,
        "vignette_remove": True,
        "watermark_remove": True,
        "description": "Standard real estate photo enhancement — brighter, sharper, more vibrant",
    },
    "luxury_listing": {
        "brightness": 1.10,
        "contrast": 1.15,
        "color": 1.05,
        "sharpness": 1.20,
        "auto_wb": True,
        "sky_enhance": True,
        "warm_tone": True,
        "watermark_remove": True,
        "description": "Luxury property preset — warm tones, subtle enhancement, premium feel",
    },
    "renovation_before_after": {
        "brightness": 1.25,
        "contrast": 1.30,
        "color": 1.15,
        "sharpness": 1.40,
        "auto_wb": True,
        "watermark_remove": True,
        "description": "Maximum enhancement for dark/dated renovation properties",
    },
    "exterior_hero": {
        "brightness": 1.20,
        "contrast": 1.25,
        "color": 1.20,
        "sharpness": 1.25,
        "auto_wb": True,
        "sky_enhance": True,
        "grass_enhance": True,
        "watermark_remove": True,
        "description": "Hero shot enhancement — sky replacement, green grass, curb appeal",
    },
    "interior_bright": {
        "brightness": 1.30,
        "contrast": 1.10,
        "color": 1.08,
        "sharpness": 1.20,
        "auto_wb": True,
        "warm_tone": True,
        "watermark_remove": True,
        "description": "Interior brightening — open up dark rooms, warm tones",
    },
}


class PhotoEnhancementAgent(BaseAgent):
    """
    AI Photo Enhancement Agent — polishes property photos automatically.

    Pipeline:
    1. Fetch image with browser-like headers + correct Referer (fixes 403s)
    2. Watermark detection and removal via OpenCV inpainting
    3. Auto white-balance correction
    4. Brightness & contrast optimisation
    5. Color vibrancy enhancement
    6. Sharpness + detail enhancement
    7. LANCZOS upscaling (or Real-ESRGAN if available)

    All processing uses 100% free tools. No paid APIs required.
    """

    def __init__(self):
        super().__init__("PhotoEnhancer")
        self._esrgan_url = "http://localhost:7860"   # Real-ESRGAN / Automatic1111 API
        self._comfyui_url = "http://localhost:8188"  # ComfyUI API

    async def execute(
        self,
        image_data: bytes | None = None,
        image_url: str | None = None,
        image_path: str | None = None,
        preset: str = "real_estate_standard",
        upscale: bool = True,
        upscale_factor: int = 2,
        output_format: str = "JPEG",
        output_quality: int = 92,
        return_base64: bool = True,
    ) -> AgentResult:
        """
        Enhance a property photo.

        Args:
            image_data:    Raw image bytes (provide this OR image_url OR image_path)
            image_url:     URL to download the image from
            image_path:    Local file path to the image
            preset:        Enhancement preset name (see ENHANCEMENT_PRESETS)
            upscale:       Whether to upscale the image
            upscale_factor: Upscale multiplier (2x or 4x)
            output_format: JPEG, PNG, or WEBP
            output_quality: JPEG/WEBP quality (1-100)
            return_base64: Return base64-encoded result (vs raw bytes)
        """
        self.logger.info(
            "photo_enhancement_started",
            preset=preset,
            upscale=upscale,
            has_data=image_data is not None,
            has_url=image_url is not None,
        )

        # Step 1: Fetch image bytes
        img_bytes = await self._get_image_data(image_data, image_url, image_path)
        if not img_bytes:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="Could not load image. Check the URL is accessible or provide image_data/image_path.",
            )

        # Step 2: Watermark removal (OpenCV inpainting)
        preset_config = ENHANCEMENT_PRESETS.get(preset, ENHANCEMENT_PRESETS["real_estate_standard"])
        wm_removed = False
        if preset_config.get("watermark_remove", False):
            try:
                cleaned_bytes, wm_removed = self._remove_watermarks(img_bytes)
                if wm_removed:
                    img_bytes = cleaned_bytes
                    self.logger.info("watermark_removed")
            except Exception as e:
                self.logger.warning("watermark_removal_failed", error=str(e))

        # Step 3: Pillow enhancements
        try:
            enhanced_bytes, enhancement_log = self._enhance_with_pillow(
                img_bytes, preset, output_format, output_quality
            )
        except Exception as e:
            self.logger.error("pillow_enhancement_failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Image enhancement failed: {str(e)}",
            )

        if wm_removed:
            enhancement_log.insert(0, "Watermark detected and removed (OpenCV inpainting)")

        # Step 4: Upscaling
        upscale_used = False
        if upscale:
            try:
                upscaled = await self._ai_upscale(enhanced_bytes, upscale_factor)
                if upscaled:
                    enhanced_bytes = upscaled
                    upscale_used = True
                    enhancement_log.append(f"Upscaled {upscale_factor}x (Real-ESRGAN / LANCZOS)")
            except Exception as e:
                self.logger.warning("upscale_failed", error=str(e))
                enhancement_log.append("Upscaling skipped (error)")

        # Step 5: Build result — include BOTH field names for compatibility
        b64 = base64.b64encode(enhanced_bytes).decode("utf-8")
        result_data = {
            "enhanced": True,
            "preset": preset,
            "enhancements_applied": enhancement_log,
            "upscaled": upscale_used,
            "watermark_removed": wm_removed,
            "output_format": output_format,
            "output_size_bytes": len(enhanced_bytes),
            # Primary field name (used by API and frontend)
            "image_base64": b64,
            # Alias kept for backwards compatibility
            "enhanced_base64": b64,
            "data_uri": f"data:image/{output_format.lower()};base64,{b64}",
        }

        if not return_base64:
            del result_data["image_base64"]
            del result_data["enhanced_base64"]
            del result_data["data_uri"]
            result_data["image_bytes"] = enhanced_bytes

        self.logger.info(
            "photo_enhancement_complete",
            enhancements=len(enhancement_log),
            upscaled=upscale_used,
            watermark_removed=wm_removed,
            output_size=len(enhanced_bytes),
        )

        return AgentResult(agent_name=self.name, success=True, data=result_data)

    async def batch_enhance(
        self,
        image_urls: list[str],
        preset: str = "real_estate_standard",
        upscale: bool = False,
        max_concurrent: int = 3,
    ) -> AgentResult:
        """Enhance multiple property photos in parallel."""
        self.logger.info("batch_enhancement_started", count=len(image_urls), preset=preset)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_one(url: str, idx: int):
            async with semaphore:
                result = await self.execute(
                    image_url=url,
                    preset=preset,
                    upscale=upscale,
                    return_base64=True,
                )
                return {"index": idx, "url": url, "result": result.to_dict()}

        tasks = [process_one(url, i) for i, url in enumerate(image_urls)]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        processed, errors = [], []
        for r in batch_results:
            if isinstance(r, Exception):
                errors.append(str(r))
            else:
                processed.append(r)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "total": len(image_urls),
                "processed": len(processed),
                "errors": errors,
                "results": processed,
            },
        )

    # ── Watermark Removal ─────────────────────────────────────────────────────

    def _remove_watermarks(self, image_bytes: bytes) -> tuple[bytes, bool]:
        """
        Detect and remove watermarks / overlaid text from property photos.

        Strategy:
        1. Detect near-white or near-black semi-transparent regions in corners
           (where real estate watermarks are typically placed).
        2. Detect high-contrast text-like blobs using edge detection.
        3. Build an inpainting mask covering those regions.
        4. Apply OpenCV TELEA inpainting to fill the masked areas naturally.

        Returns (cleaned_bytes, was_watermark_found).
        """
        import cv2
        import numpy as np
        from PIL import Image

        # Convert to numpy array
        pil_img = Image.open(io.BytesIO(image_bytes))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        h, w = img.shape[:2]

        # ── Step 1: Corner region masks (most watermarks live in corners) ──
        corner_h = max(60, int(h * 0.12))
        corner_w = max(120, int(w * 0.25))
        corner_mask = np.zeros((h, w), dtype=np.uint8)
        # Bottom-left (most common for agency logos)
        corner_mask[h - corner_h:, :corner_w] = 255
        # Bottom-right
        corner_mask[h - corner_h:, w - corner_w:] = 255
        # Top-left
        corner_mask[:corner_h, :corner_w] = 255
        # Top-right
        corner_mask[:corner_h, w - corner_w:] = 255

        # ── Step 2: Detect near-white overlay text in corners ──
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Threshold for very bright pixels (white text / logos)
        _, bright_mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
        # Threshold for very dark pixels (black text on light bg)
        _, dark_mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY_INV)
        text_candidates = cv2.bitwise_or(bright_mask, dark_mask)

        # Only consider text candidates inside corner regions
        corner_text = cv2.bitwise_and(text_candidates, corner_mask)

        # ── Step 3: Edge-based text detection across the full image ──
        edges = cv2.Canny(gray, 100, 200)
        # Dilate edges to connect nearby strokes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated_edges = cv2.dilate(edges, kernel, iterations=2)
        # Find connected components of edge blobs
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(dilated_edges)
        text_blob_mask = np.zeros((h, w), dtype=np.uint8)
        for i in range(1, num_labels):
            x, y, bw, bh, area = stats[i]
            aspect = bw / max(bh, 1)
            # Typical text blob: wide, not too tall, small area
            if area < 5000 and 1.5 < aspect < 15 and bh < h * 0.08:
                text_blob_mask[y:y + bh, x:x + bw] = 255

        # Only keep text blobs that overlap with corner regions
        corner_text_blobs = cv2.bitwise_and(text_blob_mask, corner_mask)

        # ── Step 4: Combine masks ──
        combined = cv2.bitwise_or(corner_text, corner_text_blobs)

        # Dilate slightly to cover anti-aliased edges of text
        combined = cv2.dilate(combined, kernel, iterations=3)

        # Check if we actually found anything significant
        mask_coverage = combined.sum() / 255
        min_pixels = 50  # At least 50 pixels to consider it a real watermark
        if mask_coverage < min_pixels:
            return image_bytes, False

        # ── Step 5: Inpaint ──
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        inpainted = cv2.inpaint(img_bgr, combined, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        result_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)

        # Convert back to bytes
        result_pil = Image.fromarray(result_rgb)
        output = io.BytesIO()
        result_pil.save(output, format="JPEG", quality=95, optimize=True)
        return output.getvalue(), True

    # ── Pillow Enhancement ────────────────────────────────────────────────────

    def _enhance_with_pillow(
        self,
        image_bytes: bytes,
        preset: str,
        output_format: str,
        quality: int,
    ) -> tuple[bytes, list[str]]:
        """Apply Pillow-based enhancements to the image."""
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

        img = Image.open(io.BytesIO(image_bytes))
        log = []

        # Convert to RGB if needed
        if img.mode in ("RGBA", "P", "L"):
            img = img.convert("RGB")
            log.append("Converted to RGB")

        preset_config = ENHANCEMENT_PRESETS.get(preset, ENHANCEMENT_PRESETS["real_estate_standard"])

        # ── Auto White Balance ──
        if preset_config.get("auto_wb", False):
            img = self._auto_white_balance(img)
            log.append("Auto white-balance corrected")

        # ── Auto Levels (histogram stretch) ──
        img = ImageOps.autocontrast(img, cutoff=0.5)
        log.append("Auto-levels applied")

        # ── Brightness ──
        brightness_factor = preset_config.get("brightness", 1.0)
        if brightness_factor != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness_factor)
            log.append(f"Brightness: {brightness_factor:.2f}x")

        # ── Contrast ──
        contrast_factor = preset_config.get("contrast", 1.0)
        if contrast_factor != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast_factor)
            log.append(f"Contrast: {contrast_factor:.2f}x")

        # ── Color Saturation ──
        color_factor = preset_config.get("color", 1.0)
        if color_factor != 1.0:
            img = ImageEnhance.Color(img).enhance(color_factor)
            log.append(f"Color vibrancy: {color_factor:.2f}x")

        # ── Warm Tone ──
        if preset_config.get("warm_tone", False):
            img = self._apply_warm_tone(img)
            log.append("Warm tone applied")

        # ── Grass Enhancement (boost greens for exterior shots) ──
        if preset_config.get("grass_enhance", False):
            img = self._enhance_greens(img)
            log.append("Grass/green enhancement applied")

        # ── Sharpness ──
        sharpness_factor = preset_config.get("sharpness", 1.0)
        if sharpness_factor != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)
            log.append(f"Sharpness: {sharpness_factor:.2f}x")

        # ── Detail Enhancement (Unsharp Mask) ──
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=100, threshold=3))
        log.append("Detail enhancement (unsharp mask)")

        # ── Noise Reduction for dark images ──
        stat = ImageStat.Stat(img)
        avg_brightness = sum(stat.mean) / 3
        if avg_brightness < 80:
            img = img.filter(ImageFilter.SMOOTH_MORE)
            img = ImageEnhance.Sharpness(img).enhance(1.3)
            log.append("Noise reduction (dark image)")

        # ── Output ──
        output = io.BytesIO()
        save_kwargs: dict = {"format": output_format}
        if output_format.upper() == "JPEG":
            save_kwargs.update({"quality": quality, "optimize": True, "progressive": True})
        elif output_format.upper() == "WEBP":
            save_kwargs["quality"] = quality
        img.save(output, **save_kwargs)

        return output.getvalue(), log

    # ── Colour Helpers ────────────────────────────────────────────────────────

    def _auto_white_balance(self, img):
        """Grey-world white balance correction."""
        from PIL import Image, ImageStat

        stat = ImageStat.Stat(img)
        r_mean, g_mean, b_mean = stat.mean[:3]
        if r_mean == 0 or g_mean == 0 or b_mean == 0:
            return img

        overall_mean = (r_mean + g_mean + b_mean) / 3
        r_scale = max(0.7, min(1.3, overall_mean / r_mean))
        g_scale = max(0.7, min(1.3, overall_mean / g_mean))
        b_scale = max(0.7, min(1.3, overall_mean / b_mean))

        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * r_scale)))
        g = g.point(lambda x: min(255, int(x * g_scale)))
        b = b.point(lambda x: min(255, int(x * b_scale)))
        return Image.merge("RGB", (r, g, b))

    def _apply_warm_tone(self, img):
        """Subtle warm amber shift for luxury feel."""
        from PIL import Image

        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * 1.04)))
        g = g.point(lambda x: min(255, int(x * 1.01)))
        b = b.point(lambda x: min(255, int(x * 0.96)))
        return Image.merge("RGB", (r, g, b))

    def _enhance_greens(self, img):
        """Boost green channel slightly for lush lawn/garden shots."""
        from PIL import Image

        r, g, b = img.split()
        g = g.point(lambda x: min(255, int(x * 1.06)))
        return Image.merge("RGB", (r, g, b))

    # ── Image Fetching ────────────────────────────────────────────────────────

    async def _get_image_data(
        self,
        image_data: bytes | None,
        image_url: str | None,
        image_path: str | None,
    ) -> bytes | None:
        """
        Fetch image bytes from the provided source.

        For URLs, uses browser-like headers with the correct Referer for known
        real estate CDNs to avoid 403 Forbidden responses.
        """
        if image_data:
            return image_data

        if image_url:
            headers = self._build_image_headers(image_url)
            # Try up to 2 times (once with Referer, once without as fallback)
            for attempt, hdrs in enumerate([headers, {"User-Agent": random.choice(_IMAGE_USER_AGENTS)}]):
                try:
                    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                        resp = await client.get(image_url, headers=hdrs)
                        if resp.status_code == 200:
                            content_type = resp.headers.get("content-type", "")
                            if "image" in content_type or len(resp.content) > 1000:
                                return resp.content
                        self.logger.warning(
                            "image_fetch_non_200",
                            url=image_url,
                            status=resp.status_code,
                            attempt=attempt + 1,
                        )
                except Exception as e:
                    self.logger.warning("image_fetch_error", url=image_url, error=str(e), attempt=attempt + 1)
            self.logger.error("image_download_failed", url=image_url)
            return None

        if image_path:
            path = Path(image_path)
            if path.exists():
                return path.read_bytes()
            self.logger.error("image_file_not_found", path=image_path)
            return None

        return None

    @staticmethod
    def _build_image_headers(url: str) -> dict[str, str]:
        """
        Build browser-like request headers for image fetching.

        Sets a matching Referer for known Australian real estate CDN domains
        so that hotlink-protection checks pass.
        """
        ua = random.choice(_IMAGE_USER_AGENTS)
        headers = {
            "User-Agent": ua,
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "en-AU,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
        }
        # Set Referer based on the CDN domain
        try:
            from urllib.parse import urlparse
            host = urlparse(url).netloc.lower()
            for cdn_domain, referer in _REALESTATE_CDN_REFERERS.items():
                if cdn_domain in host:
                    headers["Referer"] = referer
                    break
            else:
                # Generic referer for unknown CDNs
                parsed = urlparse(url)
                headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
        except Exception:
            pass
        return headers

    # ── Upscaling ─────────────────────────────────────────────────────────────

    async def _ai_upscale(self, image_bytes: bytes, factor: int = 2) -> bytes | None:
        """
        Upscale image using Real-ESRGAN (if available) or LANCZOS fallback.

        Real-ESRGAN requires Automatic1111 / WebUI running locally on port 7860.
        Falls back to high-quality LANCZOS interpolation automatically.
        """
        # Try Real-ESRGAN via Automatic1111 API
        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            payload = {
                "resize_mode": 0,
                "upscaling_resize": factor,
                "upscaler_1": "R-ESRGAN 4x+",
                "image": b64_image,
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self._esrgan_url}/sdapi/v1/extra-single-image",
                    json=payload,
                )
            if resp.status_code == 200:
                result = resp.json()
                img_data = result.get("image", "")
                if img_data:
                    return base64.b64decode(img_data)
        except Exception:
            pass

        # Fallback: LANCZOS high-quality resize
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_bytes))
            new_size = (img.width * factor, img.height * factor)
            img = img.resize(new_size, Image.LANCZOS)
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=92, optimize=True)
            return output.getvalue()
        except Exception:
            return None

    # ── Quality Analysis ──────────────────────────────────────────────────────

    async def analyze_photo_quality(self, image_bytes: bytes) -> dict:
        """Analyse photo quality and suggest the best enhancement preset."""
        from PIL import Image, ImageStat

        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")

        stat = ImageStat.Stat(img)
        r_mean, g_mean, b_mean = stat.mean[:3]
        avg_brightness = (r_mean + g_mean + b_mean) / 3
        r_std, g_std, b_std = stat.stddev[:3]
        avg_contrast = (r_std + g_std + b_std) / 3

        issues = []
        if avg_brightness < 80:
            issues.append("too_dark")
        elif avg_brightness > 200:
            issues.append("overexposed")
        if avg_contrast < 30:
            issues.append("low_contrast")
        elif avg_contrast > 90:
            issues.append("high_contrast")

        color_diff = max(abs(r_mean - g_mean), abs(r_mean - b_mean), abs(g_mean - b_mean))
        if color_diff > 20:
            issues.append("color_cast")
        if img.width < 800 or img.height < 600:
            issues.append("low_resolution")

        if "too_dark" in issues:
            recommended_preset = "interior_bright"
        elif "low_contrast" in issues:
            recommended_preset = "renovation_before_after"
        elif img.width > img.height * 1.5:
            recommended_preset = "exterior_hero"
        else:
            recommended_preset = "real_estate_standard"

        quality_score = max(10, 100 - len(issues) * 15)

        return {
            "width": img.width,
            "height": img.height,
            "avg_brightness": round(avg_brightness, 1),
            "avg_contrast": round(avg_contrast, 1),
            "color_cast": round(color_diff, 1),
            "quality_score": quality_score,
            "issues": issues,
            "recommended_preset": recommended_preset,
            "needs_upscale": img.width < 1200,
        }

    @staticmethod
    def get_presets() -> dict:
        """Return available enhancement presets."""
        return {
            name: {
                "description": config["description"],
                "settings": {k: v for k, v in config.items() if k != "description"},
            }
            for name, config in ENHANCEMENT_PRESETS.items()
        }
