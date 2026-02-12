"""Tests for core.config Settings."""

import pytest

from core.config import Settings


def test_settings_telegram_allowed_users_parses_string():
    """telegram_allowed_users validator parses comma-separated string into list."""
    s = Settings(telegram_allowed_users="123456, 789012 ")
    assert s.telegram_allowed_users == ["123456", "789012"]


def test_settings_get_cors_origins_list():
    """get_cors_origins_list returns list of stripped origins."""
    s = Settings(cors_origins="http://a.com, http://b.com ")
    result = s.get_cors_origins_list()
    assert result == ["http://a.com", "http://b.com"]
