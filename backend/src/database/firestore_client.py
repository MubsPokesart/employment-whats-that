import json
from typing import List, Optional, Set
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter

from config import Config
from src.models import JobPosting, UserProfile, UserFilters, ScraperConfig

class FirestoreClient:
    """Firestore database client for job tracking and user management."""

    def __init__(self):
        """Initialize Firebase connection."""
        if not firebase_admin._apps:
            if Config.FIREBASE_CREDENTIALS_JSON:
                try:
                    cred_dict = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                except Exception as e:
                    print(f"Warning: Failed to load Firebase creds from JSON, falling back to default. Error: {e}")
                    firebase_admin.initialize_app()
            else:
                # Fallback for GCP environments (automatic auth)
                firebase_admin.initialize_app()

        self.db = firestore.client()

    def get_seen_jobs(self) -> Set[str]:
        """
        Fetch all previously seen job IDs.
        Returns a set of job hashes.
        """
        docs = self.db.collection('seen_jobs').select([]).stream()
        return {doc.id for doc in docs}

    def add_seen_jobs(self, job_ids: List[str]) -> None:
        """
        Mark jobs as seen in Firestore.
        Uses batched writes for efficiency (max 500 per batch).
        """
        if not job_ids:
            return

        # Firestore batch limit is 500 operations
        for i in range(0, len(job_ids), 500):
            chunk = job_ids[i:i+500]
            batch = self.db.batch()

            for job_id in chunk:
                ref = self.db.collection('seen_jobs').document(job_id)
                batch.set(ref, {"seen_at": firestore.SERVER_TIMESTAMP})

            batch.commit()

    def get_users(self) -> List[UserProfile]:
        """Fetch all active users with their preferences."""
        users = []
        docs = self.db.collection('users').where(
            filter=FieldFilter("active", "==", True)
        ).stream()

        for doc in docs:
            try:
                data = doc.to_dict()
                filters_data = data.get('filters', {})

                filters = UserFilters(
                    companies=filters_data.get('companies', []),
                    roles=filters_data.get('roles', []),
                    keywords=filters_data.get('keywords', [])
                )

                user = UserProfile(
                    push_token=data['push_token'],
                    filters=filters,
                    active=data.get('active', True)
                )
                users.append(user)
            except Exception as e:
                print(f"Skipping invalid user {doc.id}: {e}")

        return users

    def get_scraper_config(self, company: str) -> Optional[ScraperConfig]:
        """
        Fetch learned CSS selectors for a company.
        Returns None if company hasn't been learned yet.
        """
        doc = self.db.collection('scraper_configs').document(company).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        return ScraperConfig(**data)

    def save_scraper_config(self, config: ScraperConfig) -> None:
        """Save learned scraper configuration."""
        ref = self.db.collection('scraper_configs').document(config.company)
        ref.set(config.to_dict())

    def mark_config_needs_relearning(self, company: str) -> None:
        """Mark a scraper config as needing re-learning (e.g., after parse failure)."""
        ref = self.db.collection('scraper_configs').document(company)
        ref.update({"is_learned": False})
