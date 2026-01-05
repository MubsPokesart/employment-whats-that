import pytest
from unittest.mock import Mock
from playwright.sync_api import Page, Browser

@pytest.fixture
def mock_firestore():
    """Mock Firestore client for testing."""
    mock_db = Mock()
    return mock_db

@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    return mock_client

@pytest.fixture
def sample_job_html():
    """Sample career page HTML for testing."""
    return """
    <html>
        <body>
            <div class="job-listing">
                <h3 class="job-title">Software Engineer - New Grad</h3>
                <span class="job-location">San Francisco, CA</span>
                <a class="apply-link" href="/apply/12345">Apply</a>
            </div>
            <div class="job-listing">
                <h3 class="job-title">Product Manager</h3>
                <span class="job-location">Remote</span>
                <a class="apply-link" href="/apply/67890">Apply</a>
            </div>
        </body>
    </html>
    """
