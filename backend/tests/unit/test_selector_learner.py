import pytest
from unittest.mock import Mock, patch
from src.llm.selector_learner import SelectorLearner
from src.models import ScraperConfig

@pytest.fixture
def sample_career_html():
    return """
    <html>
        <body>
            <div class="careers-page">
                <article class="job-card" data-id="123">
                    <h2 class="position-title">Machine Learning Engineer - New Grad 2026</h2>
                    <span class="job-location">San Francisco, CA</span>
                    <a href="/careers/apply/ml-123" class="apply-button">Apply Now</a>
                </article>
                <article class="job-card" data-id="456">
                    <h2 class="position-title">Research Scientist</h2>
                    <span class="job-location">Remote</span>
                    <a href="/careers/apply/research-456" class="apply-button">Apply Now</a>
                </article>
            </div>
        </body>
    </html>
    """

def test_selector_learner_extracts_selectors(sample_career_html, mock_anthropic):
    """Test that LLM correctly identifies CSS selectors."""
    # Mock Anthropic response
    mock_response = Mock()
    mock_response.content = [Mock(text="""
    {
        "job_container_selector": ".job-card",
        "title_selector": ".position-title",
        "location_selector": ".job-location",
        "link_selector": ".apply-button"
    }
    """)]
    mock_anthropic.messages.create.return_value = mock_response

    learner = SelectorLearner()
    learner.client = mock_anthropic

    config = learner.learn_selectors(
        company="Anthropic",
        career_url="https://anthropic.com/careers",
        html_content=sample_career_html
    )

    assert config.job_container_selector == ".job-card"
    assert config.title_selector == ".position-title"
    assert config.location_selector == ".job-location"
    assert config.link_selector == ".apply-button"

def test_selector_learner_handles_api_errors(mock_anthropic):
    """Test graceful handling of LLM API errors."""
    mock_anthropic.messages.create.side_effect = Exception("API Rate Limit")

    learner = SelectorLearner()
    learner.client = mock_anthropic

    with pytest.raises(Exception) as exc_info:
        learner.learn_selectors("Test Co", "https://test.com", "<html></html>")

    assert "API Rate Limit" in str(exc_info.value)
