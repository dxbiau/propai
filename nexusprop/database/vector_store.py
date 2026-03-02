"""
Vector Store — RAG infrastructure for suburb intelligence and property search.

Stores embeddings for suburb profiles, property listings, and historical
comparables to power intelligent retrieval and comparison.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

import structlog

from nexusprop.config.settings import get_settings
from nexusprop.models.suburb import SuburbProfile

logger = structlog.get_logger(__name__)


class VectorStore:
    """
    Vector database wrapper for RAG (Retrieval-Augmented Generation).

    Supports Supabase Vector (pgvector) for production and an in-memory
    store for development/testing.

    Used for:
    1. Suburb profile similarity search
    2. Property listing deduplication
    3. Historical comparable matching
    4. User preference matching
    """

    def __init__(self, use_memory: bool = False):
        self.settings = get_settings()
        self.use_memory = use_memory or not self.settings.supabase_url
        self._memory_store: dict[str, dict] = {}
        self._supabase_client = None

    async def _get_supabase(self):
        """Lazy-init Supabase client."""
        if self._supabase_client is None and not self.use_memory:
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    self.settings.supabase_url,
                    self.settings.supabase_service_key or self.settings.supabase_key,
                )
                logger.info("supabase_connected")
            except Exception as e:
                logger.warning("supabase_connection_failed", error=str(e))
                self.use_memory = True
        return self._supabase_client

    async def upsert_suburb(self, suburb: SuburbProfile) -> str:
        """Store a suburb profile with its embedding text."""
        doc_id = self._suburb_id(suburb)
        text = suburb.build_embedding_text()

        record = {
            "id": doc_id,
            "content": text,
            "metadata": {
                "suburb": suburb.suburb_name,
                "state": suburb.state,
                "postcode": suburb.postcode,
                "type": "suburb_profile",
                "median_price": suburb.growth.median_house_price,
                "yield": suburb.growth.gross_rental_yield_house,
                "growth": suburb.growth.annual_growth_pct_house,
                "vacancy": suburb.vacancy_rate_pct,
            },
        }

        if self.use_memory:
            self._memory_store[doc_id] = record
            logger.debug("suburb_stored_memory", id=doc_id)
        else:
            client = await self._get_supabase()
            if client:
                client.table("documents").upsert(record).execute()
                logger.debug("suburb_stored_supabase", id=doc_id)

        return doc_id

    async def upsert_property(self, property_data: dict) -> str:
        """Store a property listing for deduplication and search."""
        doc_id = self._property_id(property_data)

        text_parts = [
            f"Property: {property_data.get('address', '')}",
            f"Suburb: {property_data.get('suburb', '')}",
            f"Type: {property_data.get('property_type', '')}",
            f"Price: ${property_data.get('asking_price', 0):,.0f}",
            f"Beds: {property_data.get('bedrooms', '?')}",
            f"Listing: {(property_data.get('listing_text', '') or '')[:500]}",
        ]

        record = {
            "id": doc_id,
            "content": ". ".join(text_parts),
            "metadata": {
                **property_data,
                "type": "property",
            },
        }

        if self.use_memory:
            self._memory_store[doc_id] = record
        else:
            client = await self._get_supabase()
            if client:
                client.table("documents").upsert(record).execute()

        return doc_id

    async def search_similar_suburbs(
        self,
        query: str,
        limit: int = 5,
        state_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for suburbs similar to a query.

        In production, this uses pgvector similarity search.
        In memory mode, uses simple text matching.
        """
        if self.use_memory:
            return self._memory_search(query, "suburb_profile", limit, state_filter)

        client = await self._get_supabase()
        if not client:
            return []

        # RPC call to Supabase vector search function
        try:
            result = client.rpc("match_documents", {
                "query_text": query,
                "match_count": limit,
                "filter_type": "suburb_profile",
            }).execute()
            return result.data or []
        except Exception as e:
            logger.warning("vector_search_failed", error=str(e))
            return []

    async def search_properties(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search for properties matching a query."""
        if self.use_memory:
            return self._memory_search(query, "property", limit)

        client = await self._get_supabase()
        if not client:
            return []

        try:
            result = client.rpc("match_documents", {
                "query_text": query,
                "match_count": limit,
                "filter_type": "property",
            }).execute()
            return result.data or []
        except Exception as e:
            logger.warning("property_search_failed", error=str(e))
            return []

    async def check_duplicate(self, address: str) -> bool:
        """Check if a property address already exists in the store."""
        doc_id = hashlib.md5(address.lower().strip().encode()).hexdigest()

        if self.use_memory:
            return doc_id in self._memory_store

        client = await self._get_supabase()
        if client:
            result = client.table("documents").select("id").eq("id", doc_id).execute()
            return len(result.data) > 0

        return False

    def _memory_search(
        self,
        query: str,
        doc_type: str,
        limit: int,
        state_filter: Optional[str] = None,
    ) -> list[dict]:
        """Simple in-memory text search (no vector similarity)."""
        query_lower = query.lower()
        results = []

        for doc_id, record in self._memory_store.items():
            metadata = record.get("metadata", {})
            if metadata.get("type") != doc_type:
                continue
            if state_filter and metadata.get("state", "").upper() != state_filter.upper():
                continue

            content = record.get("content", "").lower()
            # Simple relevance: count query word matches
            score = sum(1 for word in query_lower.split() if word in content)
            if score > 0:
                results.append({**record, "_score": score})

        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:limit]

    @staticmethod
    def _suburb_id(suburb: SuburbProfile) -> str:
        key = f"{suburb.suburb_name}_{suburb.state}_{suburb.postcode}".lower()
        return hashlib.md5(key.encode()).hexdigest()

    @staticmethod
    def _property_id(data: dict) -> str:
        addr = data.get("address", "").lower().strip()
        return hashlib.md5(addr.encode()).hexdigest()
