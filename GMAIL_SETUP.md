# Gmail Integration Setup Guide

## Overview
The AI Sales Platform includes Gmail integration for email automation and analysis.

## Current Status
✅ Gmail service is initialized and ready
⚠️ Gmail credentials need to be configured

## Setup Steps

### 1. Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the credentials file as `credentials.json`

### 3. Place Credentials
Put the `credentials.json` file in your project root directory.

### 4. First-time Authorization
Run this command to authorize the application:
```bash
uv run python -c "
from part6_business_logic import EmailService
email_service = EmailService()
print('Gmail integration ready!')
"
```

### 5. Test Gmail Integration
After setup, you can test:
- Email sending
- Email fetching
- Email analysis

## Features Available
- ✅ Send emails via Gmail API
- ✅ Fetch and analyze emails
- ✅ Email sentiment analysis
- ✅ Email thread tracking
- ✅ Automated email responses

## Troubleshooting
- If you get authentication errors, delete `token.json` and re-authorize
- Make sure `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console

## Security Notes
- Keep `credentials.json` and `token.json` secure
- Don't commit these files to version control
- Use environment variables for production 