import pytest
from unittest.mock import Mock, patch
from src.notifier.expo_push import NotificationService
from src.models import JobPosting, UserProfile, UserFilters

@pytest.fixture
def sample_jobs():
    return [
        JobPosting(
            id="hash1",
            company="Anthropic",
            role="ML Engineer - New Grad",
            location="SF",
            link="https://anthropic.com/apply/1",
            source_url="https://anthropic.com/careers"
        ),
        JobPosting(
            id="hash2",
            company="OpenAI",
            role="Research Engineer",
            location="Remote",
            link="https://openai.com/apply/2",
            source_url="https://openai.com/careers"
        ),
    ]

@pytest.fixture
def sample_users():
    return [
        UserProfile(
            push_token="ExponentPushToken[abc123]",
            filters=UserFilters(
                companies=["Anthropic"],
                keywords=["new grad"]
            )
        ),
        UserProfile(
            push_token="ExponentPushToken[xyz789]",
            filters=UserFilters(
                companies=["OpenAI", "Anthropic"],
                roles=["Research"]
            )
        ),
    ]

def test_notification_filtering(sample_jobs, sample_users):
    """Test that jobs are correctly matched to user filters."""
    service = NotificationService()

    # User 1 should only get Anthropic new grad job
    matches_user1 = [
        job for job in sample_jobs
        if sample_users[0].filters.matches(job)
    ]
    assert len(matches_user1) == 1
    assert matches_user1[0].company == "Anthropic"

    # User 2 should get OpenAI research job
    # User 2 filters: companies=["OpenAI", "Anthropic"], roles=["Research"]
    # Job 1: Anthropic, ML Engineer (Research keyword check?) - Role "ML Engineer - New Grad" doesn't match "Research"
    # Job 2: OpenAI, Research Engineer - Matches Company and Role "Research"
    
    matches_user2 = [
        job for job in sample_jobs
        if sample_users[1].filters.matches(job)
    ]
    assert len(matches_user2) == 1
    assert matches_user2[0].company == "OpenAI"

@patch('src.notifier.expo_push.PushClient')
def test_notification_dispatch(mock_push_client, sample_jobs, sample_users):
    """Test notification sending logic."""
    mock_client_instance = Mock()
    mock_push_client.return_value = mock_client_instance
    mock_client_instance.publish_multiple.return_value = []

    service = NotificationService()
    service.dispatch(sample_jobs, sample_users)

    # Verify publish_multiple was called
    assert mock_client_instance.publish_multiple.called
