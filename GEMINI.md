# Career Scraper Notification System - Project Context

## Project Overview
You are implementing a serverless job notification system that monitors company career pages for new grad positions and sends real-time push notifications to iOS/Android devices.

**Architecture**: LLM-powered CSS selector learning + Playwright scraping on AWS Lambda + Firestore + Expo Push notifications

**Tech Stack**: Python 3.12, Playwright, AWS Lambda (Docker), Firestore, React Native (Expo), Claude Haiku API

**Cost Target**: ~$0.00/month leveraging free tiers (AWS Lambda 400K GB-s, Firestore 50K reads/day, Expo unlimited)

## Implementation Plan
The detailed implementation plan is located at: `docs/plans/2026-01-05-career-scraper-notification-system.md`

This plan contains 11 phases with step-by-step TDD approach:
1. Project structure & dependencies
2. Data models (Pydantic)
3. Firestore database layer
4. LLM CSS selector learner (Anthropic API)
5. Playwright scraper engine
6. Expo push notifications
7. Lambda handler & orchestration
8. React Native mobile app
9. AWS deployment automation
10. E2E testing
11. Documentation

## Execution Instructions

### Task-by-Task Execution
Each task in the plan follows TDD methodology:
1. **Write failing test first** - Implement the test that verifies expected behavior
2. **Run test to confirm failure** - Execute pytest to see the expected failure
3. **Write minimal implementation** - Add just enough code to make test pass
4. **Run test to confirm pass** - Verify the implementation works
5. **Commit** - Save progress with descriptive commit message

### Code Quality Standards
- **DRY**: Don't repeat yourself - extract common logic
- **YAGNI**: You aren't gonna need it - no premature optimization
- **Type hints**: Use Pydantic models and Python type annotations
- **Error handling**: Graceful degradation, never crash Lambda
- **Testing**: Minimum 80% coverage for core modules

### File Organization
```
backend/
├── src/
│   ├── database/firestore_client.py
│   ├── scraper/playwright_scraper.py
│   ├── llm/selector_learner.py
│   ├── notifier/expo_push.py
│   ├── models.py
│   └── handler.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── Dockerfile

mobile/
├── App.js
├── firebase.config.js
└── package.json
```

### Key Implementation Notes

**Playwright Optimization for Lambda**:
- Use webkit browser (lighter than Chromium)
- Launch args: `["--disable-gpu", "--single-process"]`
- Wait strategy: `wait_until="domcontentloaded"` (faster)
- Memory allocation: 2048 MB recommended

**LLM Cost Optimization**:
- Use Claude Haiku (not Sonnet/Opus) - $0.0003/page
- Truncate HTML to 15,000 chars before sending
- Cache learned selectors in Firestore
- Only re-learn on parse failure

**Firestore Schema**:
- `seen_jobs/{job_hash}`: Track processed jobs
- `users/{user_id}`: Store push tokens and filters
- `scraper_configs/{company}`: Cache learned CSS selectors

### When You Encounter Issues
- **Import errors**: Verify `__init__.py` files exist in all packages
- **Playwright timeout**: Increase timeout or use simpler wait strategy
- **LLM parsing fails**: Check JSON extraction logic (handle markdown code blocks)
- **Docker build fails**: Ensure using `mcr.microsoft.com/playwright/python:v1.48.0-jammy` base

## Commands Reference
- **Run tests**: `pytest backend/tests/unit -v`
- **Run specific test**: `pytest backend/tests/unit/test_models.py::test_job_posting_creation -v`
- **Build Docker**: `docker build -t career-scraper backend/`
- **Deploy Lambda**: `cd backend && ./deploy.sh`
- **Start mobile app**: `cd mobile && npx expo start`

## Success Criteria
- All unit tests passing (pytest)
- Docker image builds successfully
- Lambda executes within 3-minute timeout
- Mobile app receives push notifications
- Total cost remains under $1/month for 50 users
