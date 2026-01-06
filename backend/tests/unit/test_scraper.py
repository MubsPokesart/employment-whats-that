import pytest
from unittest.mock import Mock, patch
from src.scraper.playwright_scraper import CareerPageScraper
from src.models import ScraperConfig, JobPosting

@pytest.fixture
def sample_config():
    return ScraperConfig(
        company="Anthropic",
        career_url="https://anthropic.com/careers",
        job_container_selector=".job-listing",
        title_selector=".job-title",
        location_selector=".job-location",
        link_selector="a.apply-link",
    )

def test_scraper_extracts_jobs(sample_config, sample_job_html):
    """Test job extraction using learned selectors."""
    scraper = CareerPageScraper()

    # We'll need to mock Playwright page
    with patch('src.scraper.playwright_scraper.sync_playwright') as mock_playwright:
        mock_page = Mock()
        mock_page.content.return_value = sample_job_html

        # Mock locator chain
        mock_containers = [Mock(), Mock()]
        mock_page.locator.return_value.all.return_value = mock_containers

        # First job
        mock_containers[0].locator.return_value.first.text_content.side_effect = [
            "Software Engineer - New Grad",
            "San Francisco, CA",
        ]
        # Link attribute
        mock_containers[0].locator.return_value.first.get_attribute.return_value = "/apply/12345"

        # Second job
        mock_containers[1].locator.return_value.first.text_content.side_effect = [
            "Product Manager",
            "Remote",
        ]
        # Link attribute
        mock_containers[1].locator.return_value.first.get_attribute.return_value = "/apply/67890"

        # Note: The scraper implementation will call locator(selector).first.text_content()
        # So we need to ensure the mocks structure supports that.
        
        # Actually, let's refine the mock structure to match the expected implementation:
        # container.locator(config.title_selector).first.text_content()
        
        # Reset side effects for clearer logic
        def get_text(selector):
            if "title" in selector: return "Software Engineer - New Grad"
            if "location" in selector: return "San Francisco, CA"
            return ""
            
        # This mocking is getting complex. Let's rely on the implementation using .first properly.
        # I'll adjust the implementation expectation or the mock.
        
        # Let's use the code from the plan as a base but ensure the mocks align.
        # Plan code:
        # title_elem = container.locator(config.title_selector).first
        # title = title_elem.text_content()
        
        # So mock_containers[0].locator().first.text_content() should return title
        
        # Setup for Job 1
        job1_title = Mock(); job1_title.text_content.return_value = "Software Engineer - New Grad"
        job1_loc = Mock(); job1_loc.text_content.return_value = "San Francisco, CA"
        job1_link = Mock(); job1_link.get_attribute.return_value = "/apply/12345"
        
        # Setup for Job 2
        job2_title = Mock(); job2_title.text_content.return_value = "Product Manager"
        job2_loc = Mock(); job2_loc.text_content.return_value = "Remote"
        job2_link = Mock(); job2_link.get_attribute.return_value = "/apply/67890"

        def locator_side_effect_1(*args, **kwargs):
             m = Mock()
             if args[0] == sample_config.title_selector: m.first = job1_title
             elif args[0] == sample_config.location_selector: m.first = job1_loc
             elif args[0] == sample_config.link_selector: m.first = job1_link
             return m

        def locator_side_effect_2(*args, **kwargs):
             m = Mock()
             if args[0] == sample_config.title_selector: m.first = job2_title
             elif args[0] == sample_config.location_selector: m.first = job2_loc
             elif args[0] == sample_config.link_selector: m.first = job2_link
             return m

        mock_containers[0].locator.side_effect = locator_side_effect_1
        mock_containers[1].locator.side_effect = locator_side_effect_2
        
        # Mock browser launch
        mock_browser = Mock()
        mock_playwright.return_value.__enter__.return_value.webkit.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        jobs = scraper._extract_jobs_from_page(mock_page, sample_config)

        assert len(jobs) == 2
        assert jobs[0].company == "Anthropic"
        assert jobs[0].role == "Software Engineer - New Grad"

def test_scraper_handles_timeouts(sample_config):
    """Test that scraper handles page load timeouts gracefully."""
    scraper = CareerPageScraper()

    with patch('src.scraper.playwright_scraper.sync_playwright') as mock_pw:
        mock_browser = Mock()
        mock_pw.return_value.__enter__.return_value.webkit.launch.return_value = mock_browser
        
        mock_page = Mock()
        mock_browser.new_page.return_value = mock_page
        
        # Simulate TimeoutError on goto
        from playwright.sync_api import TimeoutError
        mock_page.goto.side_effect = TimeoutError("Navigation timeout")

        with pytest.raises(TimeoutError):
            scraper.scrape_company(sample_config)
