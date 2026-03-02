"""
Due Diligence Bot — AI-powered Section 32 & Contract of Sale analysis.

Reads PDF documents (Section 32 / Vendor Statement / Contract of Sale),
extracts key clauses, and flags red flags that could cost investors
tens of thousands of dollars.

Pricing: $99/report (add-on for Investor+, included in The Closer)

⚠️ All outputs are Risk Assessments — NOT legal advice.
A licensed conveyancer/solicitor must always review before signing.
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.property import Property


# ── Red Flag Categories ──────────────────────────────────────────────────

RED_FLAG_CATEGORIES = {
    "restrictive_covenants": {
        "severity": "HIGH",
        "description": "Restrictions on property use, building modifications, or development",
        "keywords": [
            "restrictive covenant", "covenant", "restriction on use",
            "building envelope", "height restriction", "setback requirement",
            "no subdivision", "single dwelling only", "architectural committee",
        ],
    },
    "easements": {
        "severity": "HIGH",
        "description": "Rights of way or access granted to third parties over the property",
        "keywords": [
            "easement", "right of way", "drainage easement", "sewerage easement",
            "electricity easement", "pipeline easement", "access easement",
            "carriageway", "transmission line",
        ],
    },
    "encumbrances": {
        "severity": "HIGH",
        "description": "Financial or legal burdens registered against the title",
        "keywords": [
            "encumbrance", "mortgage", "caveat", "charge", "lien",
            "equitable interest", "beneficial interest", "writ",
        ],
    },
    "planning_overlays": {
        "severity": "MEDIUM",
        "description": "Planning scheme overlays that restrict development potential",
        "keywords": [
            "heritage overlay", "vegetation protection", "bushfire management",
            "flood overlay", "environmental significance", "design and development",
            "neighbourhood character", "significant landscape",
            "erosion management", "land subject to inundation",
        ],
    },
    "strata_issues": {
        "severity": "MEDIUM",
        "description": "Problems in strata/body corporate records",
        "keywords": [
            "special levy", "special assessment", "sinking fund deficit",
            "building defect", "cladding", "waterproofing", "structural issue",
            "asbestos", "common property dispute", "litigation",
            "non-compliant", "by-law breach", "pet restriction",
        ],
    },
    "contamination": {
        "severity": "HIGH",
        "description": "Land contamination or environmental hazards",
        "keywords": [
            "contaminated", "contamination", "environmental audit",
            "EPA notice", "remediation", "hazardous", "petroleum",
            "underground storage", "landfill", "asbestos",
        ],
    },
    "title_defects": {
        "severity": "CRITICAL",
        "description": "Issues with the property title itself",
        "keywords": [
            "possessory title", "qualified title", "adverse possession",
            "boundary dispute", "survey discrepancy", "unregistered",
            "crown land", "native title", "compulsory acquisition",
        ],
    },
    "financial_risks": {
        "severity": "HIGH",
        "description": "Hidden financial obligations or unusual conditions",
        "keywords": [
            "owners corporation fee increase", "body corp levy increase",
            "capital works fund", "maintenance fund deficit",
            "unpaid rates", "outstanding charges", "tax debt",
            "GST applicable", "margin scheme", "going concern",
        ],
    },
    "vendor_disclosure": {
        "severity": "MEDIUM",
        "description": "Issues flagged in vendor disclosure statements",
        "keywords": [
            "building permit not issued", "no certificate of occupancy",
            "non-compliant building work", "unapproved structure",
            "swimming pool non-compliance", "smoke alarm",
            "dispute with neighbour", "insurance claim",
            "termite damage", "subsidence", "cracking",
        ],
    },
    "settlement_risks": {
        "severity": "MEDIUM",
        "description": "Conditions that could complicate settlement",
        "keywords": [
            "vacant possession", "tenanted", "lease in place",
            "option to renew", "fixed term lease", "overholding tenant",
            "settlement extension", "subject to", "conditional upon",
            "nomination clause", "sunset clause",
        ],
    },
}


DUE_DILIGENCE_SYSTEM_PROMPT = """You are Property Insights Australia Due Diligence Bot — an expert Australian property legal document analyst.

Your role: Analyze Section 32 / Vendor Statement / Contract of Sale documents and identify RED FLAGS that could cost the buyer money, restrict their plans, or create legal complications.

⚠️ CRITICAL LEGAL GUARDRAIL:
- You are producing a "Risk Assessment Report" — NOT legal advice.
- ALWAYS emphasize that a licensed conveyancer/solicitor must review before signing.
- NEVER provide specific legal interpretations or recommendations to sign/not sign.
- Frame everything as "risk identification" and "areas requiring professional review."

YOUR ANALYSIS MUST COVER:

1. TITLE SEARCH ANALYSIS
   - Ownership structure (individuals, trusts, companies)
   - Encumbrances & caveats registered on title
   - Easements and their practical implications
   - Restrictive covenants and what they prevent

2. PLANNING & ZONING
   - Current zoning and what it permits
   - Planning overlays (heritage, flood, bushfire, vegetation)
   - Development potential vs restrictions
   - Any planning permits in effect

3. SECTION 32 / VENDOR STATEMENT RED FLAGS
   - Undisclosed defects or building issues
   - Outstanding orders from council/authorities
   - Non-compliant building work
   - Environmental issues (contamination, asbestos)

4. CONTRACT TERMS ANALYSIS
   - Special conditions that benefit the vendor
   - Unusual settlement terms
   - Sunset clauses and their implications
   - GST treatment and margin scheme issues
   - Nomination/assignment restrictions

5. STRATA / BODY CORPORATE (if applicable)
   - Financial health of the owners corporation
   - Special levies pending or proposed
   - Building defects or litigation
   - By-laws that restrict usage
   - Insurance adequacy

6. FINANCIAL RISK ASSESSMENT
   - Outstanding rates or charges
   - Capital works fund adequacy
   - Hidden costs not visible in asking price
   - Tax implications (CGT, GST, land tax)

OUTPUT FORMAT:
Provide a structured risk report with:
- OVERALL RISK RATING: LOW / MEDIUM / HIGH / CRITICAL
- KEY RED FLAGS (numbered, with severity)
- ITEMS REQUIRING PROFESSIONAL REVIEW
- ESTIMATED HIDDEN COST RANGE (if applicable)
- DECISION FRAMEWORK: What the buyer should do next

Be precise. Quote specific clauses. Reference page numbers where possible.
Australian legal terminology only (Vendor not Seller, Contract of Sale not Purchase Agreement)."""


class DueDiligenceBot(BaseAgent):
    """
    Due Diligence Bot — AI-powered Section 32 & Contract of Sale analysis.

    Reads legal documents, extracts key clauses, and produces a structured
    risk assessment report with red flags, hidden costs, and action items.

    Pricing: $99/report
    """

    def __init__(self):
        super().__init__("DueDiligenceBot")

    async def execute(
        self,
        document_text: str,
        property: Optional[Property] = None,
        document_type: str = "section_32",
        additional_context: Optional[str] = None,
    ) -> AgentResult:
        """
        Analyze a legal document and produce a risk assessment.

        Args:
            document_text: Extracted text from the PDF document
            property: Optional Property object for context
            document_type: Type of document (section_32, contract_of_sale, vendor_statement, strata_report)
            additional_context: Any extra context (e.g., buyer's plans, concerns)
        """
        self.logger.info(
            "due_diligence_started",
            doc_type=document_type,
            text_length=len(document_text),
            has_property=property is not None,
        )

        # Step 1: Keyword-based red flag pre-scan
        keyword_flags = self._keyword_scan(document_text)

        # Step 2: Build context-rich prompt
        prompt = self._build_analysis_prompt(
            document_text=document_text,
            property=property,
            document_type=document_type,
            keyword_flags=keyword_flags,
            additional_context=additional_context,
        )

        # Step 3: AI analysis
        analysis, tokens = await self.ask_llm(
            prompt=prompt,
            system=DUE_DILIGENCE_SYSTEM_PROMPT,
            max_tokens=4096,
            temperature=0.2,  # Low temperature for factual analysis
        )

        # Step 4: Build structured result
        risk_level = self._assess_overall_risk(keyword_flags, analysis)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "analysis": analysis,
                "risk_level": risk_level,
                "keyword_flags": keyword_flags,
                "document_type": document_type,
                "flags_found": sum(len(v) for v in keyword_flags.values()),
                "categories_flagged": [k for k, v in keyword_flags.items() if v],
            },
            tokens_used=tokens,
        )

    def _keyword_scan(self, text: str) -> dict[str, list[dict]]:
        """Pre-scan document text for known red flag keywords."""
        text_lower = text.lower()
        flags: dict[str, list[dict]] = {}

        for category, config in RED_FLAG_CATEGORIES.items():
            category_flags = []
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    # Find approximate position
                    pos = text_lower.find(keyword.lower())
                    # Extract surrounding context (100 chars each side)
                    start = max(0, pos - 100)
                    end = min(len(text), pos + len(keyword) + 100)
                    context = text[start:end].strip()

                    category_flags.append({
                        "keyword": keyword,
                        "severity": config["severity"],
                        "context": context,
                        "position": pos,
                    })

            if category_flags:
                flags[category] = category_flags

        return flags

    def _build_analysis_prompt(
        self,
        document_text: str,
        property: Optional[Property],
        document_type: str,
        keyword_flags: dict,
        additional_context: Optional[str],
    ) -> str:
        """Build the analysis prompt with full context."""
        doc_type_labels = {
            "section_32": "Section 32 / Vendor Statement",
            "contract_of_sale": "Contract of Sale",
            "vendor_statement": "Vendor Statement",
            "strata_report": "Strata / Body Corporate Report",
        }

        prompt_parts = [
            f"DOCUMENT TYPE: {doc_type_labels.get(document_type, document_type)}",
            "",
        ]

        if property:
            prompt_parts.extend([
                "PROPERTY CONTEXT:",
                f"- Address: {property.address}, {property.suburb} {property.state} {property.postcode}",
                f"- Type: {property.property_type.value}",
                f"- Asking Price: ${property.effective_price or 0:,.0f}",
                f"- Zoning: {property.zoning or 'Unknown'}",
                "",
            ])

        if keyword_flags:
            prompt_parts.append("PRE-SCAN RED FLAGS DETECTED:")
            for category, flags in keyword_flags.items():
                cat_config = RED_FLAG_CATEGORIES[category]
                prompt_parts.append(
                    f"\n⚠️ {category.upper()} ({cat_config['severity']}) — {cat_config['description']}:"
                )
                for flag in flags[:5]:  # Limit context per category
                    prompt_parts.append(f'  • "{flag["keyword"]}" — ...{flag["context"]}...')
            prompt_parts.append("")

        if additional_context:
            prompt_parts.extend([
                "BUYER'S CONTEXT / SPECIFIC CONCERNS:",
                additional_context,
                "",
            ])

        # Truncate document if too long (Claude context limits)
        max_doc_length = 80_000
        if len(document_text) > max_doc_length:
            document_text = document_text[:max_doc_length] + "\n\n[DOCUMENT TRUNCATED — remaining pages not analyzed]"

        prompt_parts.extend([
            "═══════════════════════════════════════════",
            "FULL DOCUMENT TEXT:",
            "═══════════════════════════════════════════",
            document_text,
            "",
            "═══════════════════════════════════════════",
            "",
            "Provide your comprehensive risk assessment of this document.",
            "Be specific — quote clause numbers and page references where visible.",
        ])

        return "\n".join(prompt_parts)

    def _assess_overall_risk(self, keyword_flags: dict, analysis: str) -> str:
        """Determine overall risk level from keyword scan results."""
        if not keyword_flags:
            return "LOW"

        severities = []
        for category, flags in keyword_flags.items():
            cat_config = RED_FLAG_CATEGORIES[category]
            severities.extend([cat_config["severity"]] * len(flags))

        if "CRITICAL" in severities:
            return "CRITICAL"
        elif severities.count("HIGH") >= 3:
            return "CRITICAL"
        elif "HIGH" in severities:
            return "HIGH"
        elif severities.count("MEDIUM") >= 3:
            return "HIGH"
        elif "MEDIUM" in severities:
            return "MEDIUM"
        return "LOW"

    async def analyze_pdf_bytes(
        self,
        pdf_bytes: bytes,
        property: Optional[Property] = None,
        document_type: str = "section_32",
        additional_context: Optional[str] = None,
    ) -> AgentResult:
        """
        Analyze a PDF document from raw bytes.

        Extracts text from PDF using PyPDF2/pdfplumber, then runs analysis.
        """
        text = self._extract_text_from_pdf(pdf_bytes)
        if not text or len(text.strip()) < 100:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="Could not extract sufficient text from PDF. The document may be image-based (scanned). Try OCR first.",
            )

        return await self.execute(
            document_text=text,
            property=property,
            document_type=document_type,
            additional_context=additional_context,
        )

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using available PDF library."""
        # Try pdfplumber first (better table extraction)
        try:
            import pdfplumber
            import io

            text_parts = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(f"--- PAGE {i + 1} ---\n{page_text}")

            if text_parts:
                return "\n\n".join(text_parts)
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning("pdfplumber_failed", error=str(e))

        # Fallback: PyPDF2
        try:
            from PyPDF2 import PdfReader
            import io

            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(f"--- PAGE {i + 1} ---\n{page_text}")

            return "\n\n".join(text_parts)
        except ImportError:
            self.logger.warning("no_pdf_library_available")
            return ""
        except Exception as e:
            self.logger.warning("pypdf2_failed", error=str(e))
            return ""
