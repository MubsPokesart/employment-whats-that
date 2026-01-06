import json
from typing import Any, Dict

from config import Config
from src.database.firestore_client import FirestoreClient
from src.scraper.playwright_scraper import CareerPageScraper
from src.llm.selector_learner import SelectorLearner
from src.notifier.expo_push import NotificationService

def lambda_handler(event: Any, context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for career page scraping.

    Triggered by EventBridge on a schedule (every 15 minutes).

    Flow:
    1. Fetch list of companies to monitor from Firestore (from user subscriptions)
    2. For each company:
        a. Check if we have learned selectors
        b. If not, use LLM to learn them
        c. Scrape career page using selectors
    3. Diff against seen jobs
    4. Send notifications to matching users
    5. Update seen jobs

    Args:
        event: EventBridge event (unused)
        context: Lambda context (unused)

    Returns:
        Dict with status and metrics
    """
    print("Starting career page scan cycle...")

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return {"status": "error", "message": str(e)}

    # Initialize services
    # We catch errors during init to be safe, especially DB init
    try:
        db = FirestoreClient()
        scraper = CareerPageScraper()
        learner = SelectorLearner()
        notifier = NotificationService()
    except Exception as e:
        print(f"Initialization error: {e}")
        return {"status": "error", "message": str(e)}

    # 1. Get state
    seen_job_ids = db.get_seen_jobs()
    print(f"Loaded {len(seen_job_ids)} previously seen jobs")

    users = db.get_users()
    print(f"Found {len(users)} active users")

    if not users:
        print("No active users, skipping scrape")
        return {"status": "success", "new_jobs": 0}

    # 2. Determine companies to scrape (from user filters)
    companies_to_scrape = set()
    for user in users:
        companies_to_scrape.update(user.filters.companies)

    print(f"Monitoring {len(companies_to_scrape)} companies: {companies_to_scrape}")

    all_new_jobs = []

    # 3. Scrape each company
    for company in companies_to_scrape:
        try:
            print(f"Processing {company}...")

            # Check for learned selectors
            config = db.get_scraper_config(company)

            if not config or not config.is_learned:
                print(f"  No learned config for {company}, learning now...")

                # Fetch HTML for learning
                # Note: In production, you'd want users to provide the career URL
                # For MVP, we'll require it to be set during user registration or somehow known
                # Since we don't have URL in UserFilters (only company name), we might miss it.
                # The plan implies config might exist but !is_learned, OR we need to know the URL.
                # If config doesn't exist at all, we can't scrape because we don't know the URL.
                
                if config and config.career_url:
                    # Retry learning
                     try:
                        html = scraper.fetch_html_for_learning(config.career_url)
                        new_config = learner.learn_selectors(company, config.career_url, html)
                        db.save_scraper_config(new_config)
                        config = new_config
                     except Exception as learn_error:
                         print(f"  Failed to learn selectors for {company}: {learn_error}")
                         continue
                else:
                    print(f"  Skipping {company} - no config/URL found")
                    continue

            # Scrape using learned config
            jobs = scraper.scrape_company(config)
            print(f"  Found {len(jobs)} jobs on page")

            # Filter for new jobs
            for job in jobs:
                if job.id not in seen_job_ids:
                    all_new_jobs.append(job)
                    seen_job_ids.add(job.id)

        except Exception as e:
            print(f"  Error scraping {company}: {e}")

            # Mark config for re-learning if scrape failed
            if config:
                db.mark_config_needs_relearning(company)
            continue

    if not all_new_jobs:
        print("No new jobs detected")
        return {"status": "success", "new_jobs": 0}

    print(f"Detected {len(all_new_jobs)} new jobs")

    # 4. Send notifications
    notifier.dispatch(all_new_jobs, users)

    # 5. Update seen jobs
    new_job_ids = [job.id for job in all_new_jobs]
    db.add_seen_jobs(new_job_ids)

    print(f"Cycle complete. Processed {len(new_job_ids)} new jobs")
    return {
        "status": "success",
        "new_jobs": len(new_job_ids),
        "companies_scraped": len(companies_to_scrape)
    }

# Local testing entry point
if __name__ == "__main__":
    result = lambda_handler(None, None)
    print(json.dumps(result, indent=2))
