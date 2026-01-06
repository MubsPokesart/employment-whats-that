# Career Scraper Notification System

A serverless job notification system that monitors company career pages for new grad positions and sends real-time push notifications to iOS/Android devices.

## Architecture

- **Backend**: AWS Lambda (Python + Playwright)
- **Database**: Google Cloud Firestore
- **AI**: Anthropic Claude Haiku (for CSS selector learning)
- **Mobile**: React Native (Expo)
- **Notifications**: Expo Push API

## Project Structure

```
backend/
├── src/
│   ├── scraper/     # Playwright scraping logic
│   ├── llm/         # CSS selector learning
│   ├── database/    # Firestore client
│   ├── notifier/    # Push notification dispatch
│   └── handler.py   # Lambda entry point
└── tests/           # Unit and Integration tests

mobile/              # React Native Expo app
```

## Setup

### Backend

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   playwright install --with-deps chromium
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and fill in:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_CREDENTIALS_JSON`
   - `ANTHROPIC_API_KEY`

3. **Run Tests**
   ```bash
   pytest tests/
   ```

4. **Deploy**
   ```bash
   ./deploy.sh
   ```

### Mobile App

1. **Install Dependencies**
   ```bash
   cd mobile
   npm install
   ```

2. **Run App**
   ```bash
   npx expo start
   ```
   Scan the QR code with Expo Go.

## Usage

1. Open the mobile app.
2. Enter companies to monitor (comma-separated, e.g., "Google, Microsoft").
3. Enter keywords (e.g., "new grad").
4. Tap "Subscribe".
5. The backend will run every 15 minutes (via EventBridge) and notify you of new matches.

## License

MIT