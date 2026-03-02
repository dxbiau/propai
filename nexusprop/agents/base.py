"""
Base Agent — abstract base class for all Property Insights Australia agents.

Provides shared infrastructure: logging, LLM access, error handling,
and a standard interface for the Orchestrator.

LLM backend priority:
  1. Ollama (free, local) — default
  2. Anthropic (paid) — if API key is set and Ollama unavailable
  3. No-AI fallback — returns a structured "no LLM available" message
"""

from __future__ import annotations

import abc
import json
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
    Abstract base class for all Property Insights Australia agents.

    Subclasses implement `execute()` with their specific logic.
    The base class handles LLM client management, logging, and error wrapping.
    """

    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self.logger = structlog.get_logger(self.name)
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http(self) -> httpx.AsyncClient:
        """Lazy-initialized async HTTP client for Ollama / fallback."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=120.0)
        return self._http_client

    async def _ask_ollama(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> tuple[str, int]:
        """Call Ollama's local chat API (100 % free)."""
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

    async def _ask_anthropic(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> tuple[str, int]:
        """Fallback: call Anthropic (paid, requires API key)."""
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": self.settings.anthropic_model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        if system:
            kwargs["system"] = system

        response = await client.messages.create(**kwargs)
        text = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return text, tokens

    async def ask_llm(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> tuple[str, int]:
        """
        Send a prompt to the best available LLM and return (response_text, tokens_used).

        Priority: Ollama (free) → Anthropic (paid) → no-AI fallback.
        """
        # 1. Try Ollama first (free)
        if self.settings.use_ollama:
            try:
                self.logger.info("llm_request_ollama", model=self.settings.ollama_model, prompt_len=len(prompt))
                text, tokens = await self._ask_ollama(prompt, system, max_tokens, temperature)
                self.logger.info("llm_response_ollama", tokens=tokens, response_len=len(text))
                return text, tokens
            except Exception as e:
                self.logger.warning("ollama_unavailable", error=str(e))

        # 2. Try Anthropic if API key set
        if self.settings.anthropic_api_key:
            try:
                self.logger.info("llm_request_anthropic", model=self.settings.anthropic_model, prompt_len=len(prompt))
                text, tokens = await self._ask_anthropic(prompt, system, max_tokens, temperature)
                self.logger.info("llm_response_anthropic", tokens=tokens, response_len=len(text))
                return text, tokens
            except Exception as e:
                self.logger.warning("anthropic_unavailable", error=str(e))

        # 3. No-AI fallback
        self.logger.warning("no_llm_available", agent=self.name)
        return (
            '{"error": "No LLM available. Install Ollama (free) or set ANTHROPIC_API_KEY."}',
            0,
        )

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
