"""
Pytest configuration and shared fixtures for Property Insights Australia tests.
"""

from __future__ import annotations

import os
import pytest

# Ensure test environment
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("APP_DEBUG", "true")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")


@pytest.fixture(autouse=True)
def reset_settings():
    """Clear cached settings between tests."""
    from nexusprop.config.settings import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
