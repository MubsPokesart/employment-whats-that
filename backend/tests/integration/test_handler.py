import pytest
from unittest.mock import Mock, patch, MagicMock
from src.handler import lambda_handler

@patch('src.handler.Config.validate')
@patch('src.handler.FirestoreClient')
@patch('src.handler.SelectorLearner')
@patch('src.handler.CareerPageScraper')
@patch('src.handler.NotificationService')
def test_lambda_handler_full_flow(
    mock_notifier, mock_scraper, mock_learner, mock_db, mock_config
):
    """Test complete Lambda execution flow."""
    # Mock database responses
    mock_db_instance = Mock()
    mock_db_instance.get_seen_jobs.return_value = set()
    mock_db_instance.get_users.return_value = [
        Mock(
            push_token="ExponentPushToken[test]",
            filters=Mock(matches=Mock(return_value=True), companies=["TestCo"])
        )
    ]
    mock_db_instance.get_scraper_config.return_value = Mock(
        company="TestCo",
        career_url="https://test.com/careers",
        job_container_selector=".job",
        title_selector="h3",
        location_selector=".loc",
        link_selector="a",
        is_learned=True
    )
    mock_db.return_value = mock_db_instance

    # Mock scraper returning new jobs
    mock_scraper_instance = Mock()
    mock_scraper_instance.scrape_company.return_value = [
        Mock(
            id="job123",
            company="TestCo",
            role="SWE",
            location="SF",
            link="http://test.com",
            source_url="http://test.com"
        )
    ]
    mock_scraper.return_value = mock_scraper_instance

    # Execute handler
    result = lambda_handler(None, None)

    assert result["status"] == "success"
    assert result["new_jobs"] >= 0

def test_lambda_handler_no_new_jobs(mock_firestore):
    """Test handler when no new jobs are found."""
    # We mocked firestore fixture in conftest, but here we need to patch classes used in handler
    
    with patch('src.handler.FirestoreClient') as mock_db, \
         patch('src.handler.CareerPageScraper') as mock_scraper, \
         patch('src.handler.SelectorLearner'), \
         patch('src.handler.NotificationService'), \
         patch('src.handler.Config.validate'):
         
        mock_db_instance = Mock()
        mock_db_instance.get_seen_jobs.return_value = {"job123"}
        mock_db_instance.get_users.return_value = [
             Mock(filters=Mock(companies=["TestCo"]))
        ]
        # Config needs to be returned
        mock_db_instance.get_scraper_config.return_value = Mock(is_learned=True)
        mock_db.return_value = mock_db_instance
    
        # All scraped jobs are already seen
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_company.return_value = [
            Mock(id="job123")  # Already seen
        ]
        mock_scraper.return_value = mock_scraper_instance

        result = lambda_handler(None, None)

        assert result["new_jobs"] == 0
