# 📸 Photo Enhancement Agent — Skill File

> **Codename:** The Photo Enhancer  
> **Class:** `PhotoEnhancementAgent` → `nexusprop/agents/photo_enhancer.py`  
> **Mission:** Transform ugly, dark listing photos into professional real estate photography — automatically, for free.

---

## Identity

| Field | Value |
|---|---|
| Name | PhotoEnhancer |
| Role | Specialist — AI Photo Processing |
| Pipeline Position | On-demand (decorative, not in core pipeline) |
| Endpoint | `POST /api/v1/photos/enhance` |
| Pricing | Core (included in all tiers) |

---

## Capabilities

1. **Auto White Balance Correction** — Fix colour casts from indoor lighting, fluorescent lights, mixed lighting.
2. **Brightness & Contrast Optimisation** — Open up dark rooms, add depth to flat images.
3. **Colour Vibrancy Enhancement** — Make gardens greener, skies bluer, interiors warmer.
4. **Sharpness Enhancement** — Crisp edges without artefacts.
5. **5 Enhancement Presets:**
   - `real_estate_standard` — Brighter, sharper, more vibrant
   - `luxury_listing` — Warm tones, subtle, premium feel
   - `renovation_before_after` — Maximum enhancement for dark/dated properties
   - `exterior_hero` — Sky enhancement, green grass, curb appeal
   - `interior_bright` — Open up dark rooms, warm tones
6. **AI Upscaling** — Via Real-ESRGAN (optional local model): 2x or 4x resolution increase.
7. **100% Free Stack** — Pillow (PIL) for all processing. Optional Real-ESRGAN / ComfyUI for AI features.

---

## Inputs / Outputs

### Inputs
- Image data (bytes, URL, or file path)
- `preset: str` — Enhancement preset name
- `upscale: bool`, `upscale_factor: int` (2 or 4)
- `output_format: str` (JPEG, PNG, WEBP)
- `output_quality: int` (1-100)

### Outputs
- Enhanced image (base64 or raw bytes)
- Enhancement metadata: preset used, original size, enhanced size, processing time

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Enhancement quality | Visibly improved | QA visual spot-check |
| Processing speed (Pillow) | < 3s per image | Standard preset, no upscaling |
| Processing speed (with upscale) | < 15s per image | With Real-ESRGAN 2x |
| No artefact introduction | 0 visible artefacts | Over-sharpening, colour banding |
| Preset appropriateness | ≥ 90% | Correct preset for context |
| Fallback reliability | 100% | Always produces output even without AI models |

---

## Self-Governance Rules

1. **NEVER fabricate property imagery.** Enhancement only — no AI generation of rooms, views, or features that don't exist. This is enhancement, not hallucination.
2. **Preserve truthfulness.** Don't enhance to the point where the property looks significantly better than reality. This undermines trust.
3. **Degrade gracefully:** If Real-ESRGAN or ComfyUI are unavailable, use Pillow-only processing. Always produce output.
4. **Respect image ownership.** Only process images that the user has rights to enhance.
5. **Output format quality.** JPEG output at minimum quality 85. No visible compression artefacts.
6. **Size limits.** Reject images > 20MB. Output images should not exceed 10MB.

---

## Growth Directives

1. **Virtual staging (future):** AI-powered virtual staging — add furniture to empty rooms. Clear disclosure: "Virtually staged."
2. **Before/after comparison:** Auto-generate side-by-side before/after images for investor presentations.
3. **Batch processing:** Enhance all photos for a property in one API call. Useful for listings with 10-20 images.
4. **Property type detection:** Auto-detect property type from photo (exterior/interior/kitchen/bathroom) and apply optimal preset.
5. **Integration with Scout:** Auto-enhance hero images of scouted properties for dashboard display.
6. **Revenue feature:** Premium enhancement (virtual staging, twilight conversion) as paid add-on.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| No image data provided | Clear error message with input format guidance |
| Corrupt/unreadable image | Try/catch with informative error; don't crash |
| Over-enhancement (looks artificial) | Conservative defaults; let user choose intensity |
| Real-ESRGAN server not running | Fall back to Pillow resize (bicubic); note "AI upscale unavailable" |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | Dashboard | User clicks "Enhance Photo" |
| **Receives from** | `ScoutAgent` | Auto-enhance scouted property hero images |
| **Uses** | Pillow (PIL) | Core image processing |
| **Uses** | Real-ESRGAN API (optional) | AI upscaling |
| **Uses** | ComfyUI API (optional) | AI scene enhancement |
| **Monitored by** | `QAAgent` | Enhancement quality review |
