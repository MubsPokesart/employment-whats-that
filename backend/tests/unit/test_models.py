import pytest
from datetime import datetime
from src.models import JobPosting, UserProfile, UserFilters, ScraperConfig

def test_job_posting_creation():
    """Test JobPosting model creation and validation."""
    job = JobPosting(
        id="abc123",
        company="Google",
        role="Software Engineer - New Grad",
        location="Mountain View, CA",
        link="https://careers.google.com/apply/123",
        source_url="https://careers.google.com",
    )

    assert job.company == "Google"
    assert job.role == "Software Engineer - New Grad"
    assert isinstance(job.discovered_at, datetime)

def test_job_posting_hash_generation():
    """Test deterministic hash generation."""
    job1 = JobPosting(
        id="hash1",
        company="Meta",
        role="SWE",
        location="NYC",
        link="http://example.com",
        source_url="http://example.com"
    )

    job2 = JobPosting(
        id="hash2",
        company="Meta",
        role="SWE",
        location="NYC",
        link="http://different.com",
        source_url="http://different.com"
    )

    # Same company/role/location should have same ID
    assert job1.generate_hash(job1.company, job1.role, job1.location) == job2.generate_hash(job2.company, job2.role, job2.location)

def test_user_filters_defaults():
    """Test UserFilters with default values."""
    filters = UserFilters()

    assert filters.companies == []
    assert filters.roles == []
    assert filters.keywords == []

def test_scraper_config_validation():
    """Test ScraperConfig CSS selector storage."""
    config = ScraperConfig(
        company="Anthropic",
        career_url="https://anthropic.com/careers",
        job_container_selector=".job-listing",
        title_selector=".job-title",
        location_selector=".job-location",
        link_selector="a.apply-link",
    )

    assert config.company == "Anthropic"
    assert config.is_learned is True
