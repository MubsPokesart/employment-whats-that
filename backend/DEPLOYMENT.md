# Deployment Guide

## Prerequisites
- AWS CLI configured
- Docker installed
- Firebase project created
- Anthropic API key

## First-Time Setup

### 1. Firebase Setup
1. Create Firebase project at https://console.firebase.google.com
2. Enable Firestore Database
3. Generate service account key (Project Settings > Service Accounts)
4. Save JSON credentials

### 2. AWS Lambda Setup
Run the deployment script:
```bash
cd backend
./deploy.sh
```

### 3. Configure Environment Variables
In AWS Lambda Console:
- Add `FIREBASE_CREDENTIALS_JSON` (paste full JSON)
- Add `FIREBASE_PROJECT_ID`
- Add `ANTHROPIC_API_KEY`

### 4. Set up EventBridge Trigger
1. Go to Amazon EventBridge > Schedules
2. Create schedule
3. Name: `career-scraper-15min`
4. Cron expression: `0/15 * * * ? *` (every 15 minutes)
5. Target: Lambda function `career-scraper`
6. Create
