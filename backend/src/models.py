import hashlib
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class JobPosting(BaseModel):
    """Represents a single job posting."""

    id: str  # SHA256 hash
    company: str
    role: str
    location: str
    link: Optional[str] = None
    source_url: str  # The career page URL where this was found
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def generate_hash(company: str, role: str, location: str) -> str:
        """Generate deterministic hash for job uniqueness."""
        raw = f"{company.strip().lower()}|{role.strip().lower()}|{location.strip().lower()}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def model_post_init(self, __context) -> None:
        """Auto-generate hash if id not provided."""
        if not self.id or self.id == "auto":
            self.id = self.generate_hash(self.company, self.role, self.location)

class UserFilters(BaseModel):
    """User preferences for job filtering."""

    companies: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)  # e.g., ["new grad", "entry level"]

    def matches(self, job: JobPosting) -> bool:
        """Check if job matches user filters."""
        # Empty filters = match all
        if not self.companies and not self.roles and not self.keywords:
            return True

        # Check company (case-insensitive partial match)
        if self.companies:
            company_match = any(
                comp.lower() in job.company.lower()
                for comp in self.companies
            )
            if not company_match:
                return False

        # Check role keywords
        if self.roles or self.keywords:
            search_terms = self.roles + self.keywords
            role_match = any(
                term.lower() in job.role.lower()
                for term in search_terms
            )
            if not role_match:
                return False

        return True

class UserProfile(BaseModel):
    """User profile with notification preferences."""

    push_token: str
    filters: UserFilters
    active: bool = True

class ScraperConfig(BaseModel):
    """Learned CSS selectors for a company's career page."""

    company: str
    career_url: str
    job_container_selector: str
    title_selector: str
    location_selector: str
    link_selector: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_learned: bool = True  # False if needs re-learning

    def to_dict(self) -> dict:
        """Convert to Firestore-compatible dict."""
        return {
            "company": self.company,
            "career_url": self.career_url,
            "job_container_selector": self.job_container_selector,
            "title_selector": self.title_selector,
            "location_selector": self.location_selector,
            "link_selector": self.link_selector,
            "last_updated": self.last_updated,
            "is_learned": self.is_learned,
        }
