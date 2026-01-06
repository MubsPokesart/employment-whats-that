import pytest
from unittest.mock import Mock, patch
from src.handler import lambda_handler

@patch('src.handler.FirestoreClient')
@patch('src.handler.SelectorLearner')
@patch('src.handler.CareerPageScraper')
@patch('src.handler.NotificationService')
@patch('src.handler.Config.validate')
def test_end_to_end_flow(
    mock_validate, mock_notifier, mock_scraper_cls, mock_learner_cls, mock_db_cls
):
    """
    Simulate a full run of the system.
    
    Scenario:
    1. User subscribes to "TechCorp"
    2. System has no learned config for TechCorp
    3. System learns selectors via LLM
    4. System scrapes TechCorp
    5. System finds new job
    6. System sends notification
    7. System updates seen jobs
    """
    
    # Setup Mocks
    mock_db = mock_db_cls.return_value
    mock_scraper = mock_scraper_cls.return_value
    mock_learner = mock_learner_cls.return_value
    mock_notify = mock_notifier.return_value
    
    # 1. DB State: One user, TechCorp, no seen jobs
    mock_db.get_seen_jobs.return_value = set()
    mock_db.get_users.return_value = [
        Mock(
            push_token="token123",
            filters=Mock(companies=["TechCorp"], matches=Mock(return_value=True))
        )
    ]
    
    # Config: Exists but not learned, or just missing. 
    # Handler logic: if not config or not config.is_learned -> learn.
    # Let's say config exists but needs learning, and has URL.
    mock_config = Mock(is_learned=False, career_url="http://techcorp.com/jobs")
    mock_db.get_scraper_config.return_value = mock_config
    
    # 2. Scraper fetches HTML for learning
    mock_scraper.fetch_html_for_learning.return_value = "<html>...</html>"
    
    # 3. Learner returns new config
    learned_config = Mock(company="TechCorp", is_learned=True, career_url="http://techcorp.com/jobs")
    mock_learner.learn_selectors.return_value = learned_config
    
    # 4. Scraper uses new config to find jobs
    job = Mock(id="job1", company="TechCorp", role="Dev", location="Remote", link="http://job1")
    mock_scraper.scrape_company.return_value = [job]
    
    # Run Handler
    result = lambda_handler({}, {})
    
    # Verifications
    
    # Should have tried to learn
    mock_scraper.fetch_html_for_learning.assert_called_with("http://techcorp.com/jobs")
    mock_learner.learn_selectors.assert_called()
    mock_db.save_scraper_config.assert_called_with(learned_config)
    
    # Should have scraped with new config
    # Note: handler updates local variable 'config' after learning
    mock_scraper.scrape_company.assert_called()
    
    # Should have sent notification
    mock_notify.dispatch.assert_called()
    call_args = mock_notify.dispatch.call_args
    assert len(call_args[0][0]) == 1 # 1 new job
    assert call_args[0][0][0].id == "job1"
    
    # Should have updated seen jobs
    mock_db.add_seen_jobs.assert_called_with(["job1"])
    
    assert result["status"] == "success"
    assert result["new_jobs"] == 1
