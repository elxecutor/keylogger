"""
Test configuration and utilities for the encrypted keylogger project.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add src directory to Python path for testing
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# Also add the tests directory itself
TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))

# Test configuration
TEST_PASSWORD = "test_password_123"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="keylogger_test_")

@pytest.fixture
def temp_data_dir():
    """Provide a temporary directory for test data."""
    return TEST_DATA_DIR

@pytest.fixture
def test_password():
    """Provide a test password for encryption tests."""
    return TEST_PASSWORD

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up test files after each test."""
    yield
    # Cleanup logic can be added here if needed

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", 
        "platform_specific: marks tests that are platform-specific"
    )
