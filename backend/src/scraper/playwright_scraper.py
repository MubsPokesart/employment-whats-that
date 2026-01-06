from typing import List
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

from config import Config
from src.models import ScraperConfig, JobPosting

class CareerPageScraper:
    """Scrapes career pages using Playwright and learned CSS selectors."""

    def __init__(self):
        self.timeout = Config.SCRAPER_TIMEOUT_MS
        self.headless = Config.SCRAPER_HEADLESS
        self.user_agent = Config.SCRAPER_USER_AGENT

    def scrape_company(self, config: ScraperConfig) -> List[JobPosting]:
        """
        Scrape a company's career page using learned selectors.

        Args:
            config: ScraperConfig with CSS selectors

        Returns:
            List of JobPosting objects

        Raises:
            TimeoutError: If page load exceeds timeout
            Exception: If scraping fails
        """
        with sync_playwright() as p:
            # Use webkit for lighter resource usage
            browser = p.webkit.launch(
                headless=self.headless,
                args=["--disable-gpu", "--single-process"]  # Lambda optimizations
            )

            try:
                page = browser.new_page(user_agent=self.user_agent)
                page.set_default_timeout(self.timeout)

                # Navigate with minimal waiting (domcontentloaded is faster than full load)
                page.goto(config.career_url, wait_until="domcontentloaded")

                jobs = self._extract_jobs_from_page(page, config)
                return jobs

            finally:
                browser.close()

    def _extract_jobs_from_page(
        self,
        page: Page,
        config: ScraperConfig
    ) -> List[JobPosting]:
        """
        Extract jobs from page using CSS selectors.

        Args:
            page: Playwright Page object
            config: ScraperConfig with selectors

        Returns:
            List of JobPosting objects
        """
        jobs = []

        # Find all job containers
        containers = page.locator(config.job_container_selector).all()

        for container in containers:
            try:
                # Extract fields using relative selectors
                title_elem = container.locator(config.title_selector).first
                location_elem = container.locator(config.location_selector).first
                link_elem = container.locator(config.link_selector).first

                title = title_elem.text_content() or ""
                location = location_elem.text_content() or ""
                link_href = link_elem.get_attribute("href") or ""

                # Normalize relative URLs
                if link_href.startswith("/"):
                    from urllib.parse import urljoin
                    link_href = urljoin(config.career_url, link_href)

                # Create JobPosting (hash auto-generated in model)
                job = JobPosting(
                    id="auto",  # Will be generated in model_post_init
                    company=config.company,
                    role=title.strip(),
                    location=location.strip(),
                    link=link_href,
                    source_url=config.career_url,
                )

                jobs.append(job)

            except Exception as e:
                print(f"Error extracting job from container: {e}")
                continue

        return jobs

    def fetch_html_for_learning(self, url: str) -> str:
        """
        Fetch raw HTML for LLM selector learning.

        Args:
            url: Career page URL

        Returns:
            Raw HTML content
        """
        with sync_playwright() as p:
            browser = p.webkit.launch(headless=True)

            try:
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                html = page.content()
                return html

            finally:
                browser.close()
