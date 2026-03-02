"""
Property Insights Australia API Middleware — logging, rate limiting, and request tracking.
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from nexusprop.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every API request with timing and metadata."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        request_id = f"{int(time.time() * 1000)}"

        logger.info(
            "api_request_start",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "api_request_error",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                request_id=request_id,
            )
            raise

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "api_request_complete",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
            request_id=request_id,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory sliding window rate limiter.

    Production should use Redis-backed rate limiting.
    """

    def __init__(self, app):
        super().__init__(app)
        # client_ip -> list of timestamps
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and docs
        skip_paths = {"/", "/health", "/docs", "/redoc", "/openapi.json"}
        if request.url.path in skip_paths:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.rate_limit_period
        limit = settings.rate_limit_requests

        # Clean old entries outside the window
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if now - ts < window
        ]

        if len(self._requests[client_ip]) >= limit:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Max {limit} requests per {window}s. Try again later.",
                },
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        self._requests[client_ip].append(now)

        response = await call_next(request)
        remaining = limit - len(self._requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        return response
