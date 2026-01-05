import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration for the scraper system."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS_JSON: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_JSON")

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = "claude-haiku-4-20250110"  # Latest Haiku for cost optimization

    # Expo
    EXPO_ACCESS_TOKEN: Optional[str] = os.getenv("EXPO_ACCESS_TOKEN")

    # Scraper settings
    SCRAPER_TIMEOUT_MS: int = 30000  # 30 seconds per company
    SCRAPER_HEADLESS: bool = True
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (compatible; CareerScraperBot/1.0)"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        required = [
            ("FIREBASE_PROJECT_ID", cls.FIREBASE_PROJECT_ID),
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
        ]
        missing = [name for name, value in required if not value]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
