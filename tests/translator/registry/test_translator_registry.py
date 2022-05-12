"""
Unit tests for Translator SmartAPI Registry
"""
import logging

from translator.registry import query_smart_api

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_default_empty_query():
    result = query_smart_api()
    assert len(result) > 0, "Default query failed"


def test_fake_url():
    result = query_smart_api(url="fake url")
    assert result and result.startswith("Invalid URL"), "Didn't get expected request exception?"

