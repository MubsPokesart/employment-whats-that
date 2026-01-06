import json
from typing import Optional
from anthropic import Anthropic

from config import Config
from src.models import ScraperConfig

class SelectorLearner:
    """Uses Claude to learn CSS selectors from career page HTML."""

    SYSTEM_PROMPT = """You are an expert web scraping engineer. Your task is to analyze HTML from a company's career page and identify the CSS selectors needed to extract job listings.

You must return a JSON object with these exact keys:
- job_container_selector: The selector for each individual job posting container
- title_selector: The selector for the job title (relative to container)
- location_selector: The selector for the job location (relative to container)
- link_selector: The selector for the apply link (relative to container)

Rules:
1. Use the most specific, stable selectors (prefer classes over tags)
2. Selectors should be relative to the job container
3. Return ONLY valid JSON, no explanations
4. If a field is not found, use an empty string

Example output:
{
    "job_container_selector": ".job-posting",
    "title_selector": "h3.title",
    "location_selector": ".location",
    "link_selector": "a.apply-btn"
}
"""

    def __init__(self):
        """Initialize Anthropic client."""
        # Note: We should probably not instantiate Anthropic here directly if we want to avoid API key checks during unit tests,
        # but the code in the plan does it. We can mock it in tests.
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY or "dummy_key")

    def learn_selectors(
        self,
        company: str,
        career_url: str,
        html_content: str
    ) -> ScraperConfig:
        """
        Use Claude to extract CSS selectors from HTML.

        Args:
            company: Company name
            career_url: URL of career page
            html_content: Raw HTML content

        Returns:
            ScraperConfig with learned selectors

        Raises:
            Exception: If API call fails or response is invalid
        """
        user_message = f"""Analyze this career page HTML from {company} and extract the CSS selectors:

```html
{html_content[:15000]}  # Limit to ~15k chars to reduce cost
```

Return only the JSON object with selectors."""

        try:
            response = self.client.messages.create(
                model=Config.ANTHROPIC_MODEL,
                max_tokens=500,
                system=self.SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )

            # Parse JSON from response
            response_text = response.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            selectors = json.loads(response_text.strip())

            return ScraperConfig(
                company=company,
                career_url=career_url,
                job_container_selector=selectors["job_container_selector"],
                title_selector=selectors["title_selector"],
                location_selector=selectors["location_selector"],
                link_selector=selectors["link_selector"],
            )

        except Exception as e:
            print(f"Error learning selectors for {company}: {e}")
            raise
