"""
Base Agent — abstract base class for all NexusProp agents.

Provides shared infrastructure: logging, LLM access, error handling,
and a standard interface for the Orchestrator.

LLM backend priority:
  1. OpenAI-compatible API (OPENAI_API_KEY env var) — default, uses gpt-4.1-mini
  2. Ollama (free, local) — fallback if OpenAI unavailable
  3. No-AI fallback — returns a structured "no LLM available" message
"""

from __future__ import annotations

import abc
import json
import os
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import httpx
import structlog

from nexusprop.config.settings import get_settings


class AgentResult:
    """Standardized result from any agent execution."""

    def __init__(
        self,
        agent_name: str,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        tokens_used: int = 0,
        execution_time_ms: float = 0,
    ):
        self.id = str(uuid4())
        self.agent_name = agent_name
        self.success = success
        self.data = data
        self.error = error
        self.tokens_used = tokens_used
        self.execution_time_ms = execution_time_ms
        self.timestamp = datetime.utcnow()

    def __repr__(self) -> str:
        status = "✅" if self.success else "❌"
        return f"AgentResult({status} {self.agent_name}, {self.execution_time_ms:.0f}ms)"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseAgent(abc.ABC):
    """
    Abstract base class for all NexusProp agents.

    Subclasses implement `execute()` with their specific logic.
    The base class handles LLM client management, logging, and error wrapping.
    """

    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self.logger = structlog.get_logger(self.name)
        self._http_client: Optional[httpx.AsyncClient] = None
        self._openai_client = None

    @property
    def http(self) -> httpx.AsyncClient:
        """Lazy-initialized async HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=120.0)
        return self._http_client

    def _get_openai_client(self):
        """Lazy-initialize the OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import AsyncOpenAI
                api_key = os.environ.get("OPENAI_API_KEY", "")
                if api_key:
                    self._openai_client = AsyncOpenAI()
            except ImportError:
                pass
        return self._openai_client

    async def _ask_openai(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        model: str = "gpt-4.1-mini",
    ) -> tuple[str, int]:
        """Call OpenAI-compatible API (uses OPENAI_API_KEY env var)."""
        client = self._get_openai_client()
        if not client:
            raise RuntimeError("OpenAI client not available")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return text, tokens

    async def _ask_ollama(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> tuple[str, int]:
        """Call Ollama's local chat API (100% free)."""
        url = f"{self.settings.ollama_base_url}/api/chat"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        resp = await self.http.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        text = data.get("message", {}).get("content", "")
        tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
        return text, tokens

    async def ask_llm(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        model: str = "gpt-4.1-mini",
    ) -> tuple[str, int]:
        """
        Send a prompt to the best available LLM and return (response_text, tokens_used).

        Priority: OpenAI API → Ollama (local) → no-AI fallback.
        """
        # 1. Try OpenAI first (pre-configured in sandbox)
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            try:
                self.logger.info("llm_request_openai", model=model, prompt_len=len(prompt))
                text, tokens = await self._ask_openai(prompt, system, max_tokens, temperature, model)
                self.logger.info("llm_response_openai", tokens=tokens, response_len=len(text))
                return text, tokens
            except Exception as e:
                self.logger.warning("openai_unavailable", error=str(e))

        # 2. Try Ollama (free local)
        if self.settings.use_ollama:
            try:
                self.logger.info("llm_request_ollama", model=self.settings.ollama_model, prompt_len=len(prompt))
                text, tokens = await self._ask_ollama(prompt, system, max_tokens, temperature)
                self.logger.info("llm_response_ollama", tokens=tokens, response_len=len(text))
                return text, tokens
            except Exception as e:
                self.logger.warning("ollama_unavailable", error=str(e))

        # 3. No-AI fallback
        self.logger.warning("no_llm_available", agent=self.name)
        return (
            '{"error": "No LLM available. Set OPENAI_API_KEY or install Ollama."}',
            0,
        )

    async def ask_llm_json(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.2,
        model: str = "gpt-4.1-mini",
    ) -> dict:
        """
        Ask the LLM and parse the response as JSON.
        Automatically strips markdown code fences if present.
        """
        text, tokens = await self.ask_llm(prompt, system, max_tokens, temperature, model)

        # Strip markdown code fences
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            # Remove first and last fence lines
            lines = [l for l in lines if not l.startswith("```")]
            clean = "\n".join(lines).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try to extract JSON from within the text
            import re
            match = re.search(r'\{.*\}', clean, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            self.logger.warning("llm_json_parse_failed", raw=clean[:200])
            return {"error": "Failed to parse LLM response as JSON", "raw": clean[:500]}

    @abc.abstractmethod
    async def execute(self, *args, **kwargs) -> AgentResult:
        """Execute the agent's primary task. Implemented by subclasses."""
        ...

    async def safe_execute(self, *args, **kwargs) -> AgentResult:
        """Wrapper that catches exceptions and returns a proper AgentResult."""
        start = datetime.utcnow()
        try:
            result = await self.execute(*args, **kwargs)
            result.execution_time_ms = (datetime.utcnow() - start).total_seconds() * 1000
            return result
        except Exception as e:
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            self.logger.error("agent_execution_failed", error=str(e), agent=self.name)
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                execution_time_ms=elapsed,
            )
