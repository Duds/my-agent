import logging
import os
import json
import pytest
from core.logging_config import setup_logging
from core.config import settings

def test_setup_logging_creates_file(tmp_path):
    # Mock settings to use a temporary log file
    log_file = tmp_path / "test.log"
    settings.log_file = str(log_file)
    settings.log_format = "text"
    
    setup_logging()
    
    logger = logging.getLogger("test_logger")
    logger.info("Test message")
    
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content

def test_setup_logging_json_format(tmp_path):
    log_file = tmp_path / "test_json.log"
    settings.log_file = str(log_file)
    settings.log_format = "json"
    
    setup_logging()
    
    logger = logging.getLogger("test_json_logger")
    logger.info("JSON message")
    
    assert log_file.exists()
    content = log_file.read_text().strip().split("\n")[-1]
    data = json.loads(content)
    
    assert data["message"] == "JSON message"
    assert data["level"] == "INFO"
    assert "timestamp" in data

def test_log_level_respected(tmp_path):
    log_file = tmp_path / "test_level.log"
    settings.log_file = str(log_file)
    settings.log_level = "ERROR"
    
    setup_logging()
    
    logger = logging.getLogger("test_level_logger")
    logger.info("Should not see this")
    logger.error("Should see this")
    
    content = log_file.read_text()
    assert "Should not see this" not in content
    assert "Should see this" in content
