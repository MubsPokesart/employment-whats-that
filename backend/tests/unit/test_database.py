import pytest
from unittest.mock import Mock, patch, MagicMock
from src.database.firestore_client import FirestoreClient
from src.models import JobPosting, UserProfile, UserFilters, ScraperConfig

@pytest.fixture
def mock_firestore_client_module():
    """Mock firebase_admin and firestore modules."""
    with patch('src.database.firestore_client.firebase_admin') as mock_admin, \
         patch('src.database.firestore_client.firestore') as mock_firestore, \
         patch('src.database.firestore_client.credentials') as mock_creds:
        
        # Setup mocks
        mock_admin._apps = {}
        mock_db = Mock()
        mock_firestore.client.return_value = mock_db
        
        yield {
            'admin': mock_admin,
            'firestore': mock_firestore,
            'db': mock_db,
            'creds': mock_creds
        }

@pytest.fixture
def mock_firestore_db(mock_firestore_client_module):
    """Return the mocked db instance."""
    return mock_firestore_client_module['db']

def test_get_seen_jobs_empty(mock_firestore_db):
    """Test fetching seen jobs when none exist."""
    mock_firestore_db.collection.return_value.select.return_value.stream.return_value = []

    client = FirestoreClient()
    # No need to set client.db manually as it's set by the mocked firestore.client()
    
    seen = client.get_seen_jobs()
    assert seen == set()

def test_add_seen_jobs(mock_firestore_db):
    """Test adding jobs to seen collection."""
    client = FirestoreClient()
    
    job_ids = ["hash1", "hash2", "hash3"]
    client.add_seen_jobs(job_ids)

    # Verify batch operations were called
    assert mock_firestore_db.batch.called

def test_get_scraper_config(mock_firestore_db):
    """Test fetching scraper config for a company."""
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "company": "Anthropic",
        "career_url": "https://anthropic.com/careers",
        "job_container_selector": ".job",
        "title_selector": "h3",
        "location_selector": ".location",
        "link_selector": "a",
        "is_learned": True,
    }

    mock_firestore_db.collection.return_value.document.return_value.get.return_value = mock_doc

    client = FirestoreClient()
    
    config = client.get_scraper_config("Anthropic")
    assert config is not None
    assert config.company == "Anthropic"
    assert config.is_learned is True

def test_save_scraper_config(mock_firestore_db):
    """Test saving learned scraper config."""
    client = FirestoreClient()
    
    config = ScraperConfig(
        company="OpenAI",
        career_url="https://openai.com/careers",
        job_container_selector=".posting",
        title_selector=".title",
        location_selector=".loc",
        link_selector="a.btn",
    )

    client.save_scraper_config(config)

    # Verify set was called with correct data
    mock_firestore_db.collection.return_value.document.return_value.set.assert_called_once()
