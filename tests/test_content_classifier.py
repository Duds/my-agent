"""Tests for core/content_classifier.py (PBI-042)."""

import pytest

from core.content_classifier import classify


def test_classify_txt():
    r = classify("/tmp/foo.txt")
    assert r["category"] == "Documents"
    assert "Documents" in (r["suggested_destination"] or "")


def test_classify_py():
    r = classify("/home/user/script.py")
    assert r["category"] == "Code"
    assert "Code" in (r["suggested_destination"] or "")


def test_classify_unknown_ext():
    r = classify("/tmp/foo.xyz")
    assert r["category"] == "Other"
    assert r["suggested_destination"] is None


def test_classify_empty_path():
    r = classify("")
    assert r["category"] == "Unknown"
    assert r["suggested_destination"] is None
