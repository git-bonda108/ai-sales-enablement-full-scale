# Gmail & Voice Integration Setup Guide

## Prerequisites
- Python 3.8+
- Google Cloud Project with Gmail API enabled
- `credentials.json` file from Google Cloud Console

## Step 1: Install Dependencies

```bash
cd batch8_integration
pip install -r requirements.txt
```

## Step 2: Gmail Setup

### 2.1 Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json`

### 2.2 First-time Authentication
```bash
python test_gmail.py
```

This will:
1. Check for `credentials.json`
2. Open browser for authentication
3. Create `token.pickle` for future use
4. Test email reading and analysis

## Step 3: Integration with Main App

### 3.1 Add to API Gateway (`api_gateway.py`):
```python
# Copy the code from integration_api_endpoints.py
# Add the imports at the top
# Add the endpoints to your FastAPI app
```

### 3.2 Add to Streamlit UI (`streamlit_app.py`):
```python
# Copy the code from ui_integrations_code.py
# Add "Integrations" to your navigation menu
```

## Step 4: Test Everything

1. Start all servers:
```bash
# Terminal 1: CRM Server
cd mcp-crm-server
python crm_server.py

# Terminal 2: Analytics Server
cd mcp-analytics-server
python analytics_server.py

# Terminal 3: API Gateway
python api_gateway.py

# Terminal 4: Streamlit
streamlit run streamlit_app.py
```

2. Navigate to Integrations page
3. Connect Gmail
4. Test email analysis
5. Test voice mock

## Troubleshooting

### Gmail Issues:
- **"Credentials not found"**: Ensure `credentials.json` is in the correct directory
- **"Access blocked"**: Check OAuth consent screen settings
- **"Scope error"**: Delete `token.pickle` and re-authenticate

### Integration Issues:
- Ensure all servers are running
- Check API_URL in Streamlit matches your API Gateway
- Verify port numbers are correct

## Demo Script

### Email Intelligence Demo:
1. Show unread emails being fetched
2. Point out intent levels and scores
3. Generate AI response
4. Show recommended next steps

### Voice Coaching Demo:
1. Start a mock call
2. Show real-time transcript
3. Point out AI suggestions
4. End call and review analytics

## Production Notes

For production deployment:
- Store credentials securely (not in repo)
- Use environment variables
- Implement proper error handling
- Add rate limiting
- Consider using Celery for background tasks
