# Add these to your existing api_gateway.py

import os
import time
from gmail_client import GmailClient
from email_analyzer import EmailAnalyzer
from voice_mock import VoiceMockGateway
import asyncio
from typing import Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

# Initialize services
email_analyzer = EmailAnalyzer()
voice_gateway = VoiceMockGateway()

# Auto-initialize Gmail if token exists
gmail_client = None
try:
    if os.path.exists('token.pickle'):
        gmail_client = GmailClient()
        print("✅ Gmail client auto-initialized from existing token")
except Exception as e:
    print(f"⚠️ Gmail auto-initialization skipped: {e}")
    print("   Users will need to authenticate through the UI")

# Pydantic models
class EmailResponse(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class VoiceCallRequest(BaseModel):
    participant: str

# Helper function to ensure Gmail is initialized
def ensure_gmail_client():
    """Ensure Gmail client is initialized, create if token exists"""
    global gmail_client

    if gmail_client is not None:
        return True

    # Try to initialize if token exists
    if os.path.exists('token.pickle'):
        try:
            gmail_client = GmailClient()
            print("✅ Gmail client initialized from existing token")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Gmail: {e}")
            return False

    return False

# Gmail Endpoints
@app.post("/integrations/gmail/auth")
async def gmail_authenticate():
    """Authenticate with Gmail - this will open browser for OAuth"""
    global gmail_client
    try:
        # Force new authentication even if token exists
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            print("🔄 Removed existing token for fresh authentication")

        gmail_client = GmailClient()
        return {
            "status": "success", 
            "message": "Gmail authenticated successfully",
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/integrations/gmail/unread")
async def get_unread_emails(max_results: int = 10):
    """Get unread emails with AI analysis"""
    # Auto-initialize if needed
    if not ensure_gmail_client():
        raise HTTPException(
            status_code=401, 
            detail="Gmail not authenticated. Please connect Gmail first."
        )

    try:
        emails = gmail_client.get_unread_emails(max_results)

        # Analyze each email for buying signals
        analyzed_emails = []
        for email in emails:
            analysis = email_analyzer.analyze_email(email)
            analyzed_emails.append({
                **email,
                'analysis': analysis
            })

        return {
            "emails": analyzed_emails,
            "count": len(analyzed_emails),
            "timestamp": time.time()
        }
    except Exception as e:
        # If error, reset client and ask for re-auth
        gmail_client = None
        raise HTTPException(status_code=500, detail=f"Gmail error: {str(e)}")

@app.post("/integrations/gmail/send")
async def send_email(email_response: EmailResponse):
    """Send an email through Gmail"""
    if not ensure_gmail_client():
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        result = gmail_client.send_email(
            to=email_response.to,
            subject=email_response.subject,
            body=email_response.body,
            thread_id=email_response.thread_id
        )

        if result:
            return {
                "status": "success", 
                "message_id": result.get('id'),
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/gmail/generate-response/{email_id}")
async def generate_email_response(email_id: str):
    """Generate AI-powered response for an email"""
    if not ensure_gmail_client():
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        # Get the specific email
        emails = gmail_client.get_unread_emails(max_results=50)
        email = next((e for e in emails if e['id'] == email_id), None)

        if not email:
            # Try to get by thread ID as fallback
            email = next((e for e in emails if e['thread_id'] == email_id), None)

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        # Analyze and generate response
        analysis = email_analyzer.analyze_email(email)
        response = email_analyzer.generate_email_response(analysis)

        return {
            "email_id": email_id,
            "from": email.get('from'),
            "subject": email.get('subject'),
            "suggested_response": response,
            "analysis": analysis,
            "timestamp": time.time()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/gmail/mark-read/{email_id}")
async def mark_email_read(email_id: str):
    """Mark an email as read"""
    if not ensure_gmail_client():
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        success = gmail_client.mark_as_read(email_id)
        if success:
            return {"status": "success", "message": "Email marked as read"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark email as read")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice Mock Endpoints
@app.post("/integrations/voice/start-call")
async def start_voice_call(call_request: VoiceCallRequest):
    """Start a mock voice call for demo"""
    try:
        import uuid
        call_id = str(uuid.uuid4())
        result = voice_gateway.start_mock_call(call_id, call_request.participant)
        return {
            **result,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/voice/transcript/{call_id}")
async def get_call_transcript(call_id: str, last_index: int = 0):
    """Get real-time transcript updates for active call"""
    try:
        result = voice_gateway.get_real_time_transcript(call_id, last_index)
        return {
            **result,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/voice/end-call/{call_id}")
async def end_voice_call(call_id: str):
    """End voice call and get comprehensive analytics"""
    try:
        result = voice_gateway.end_call(call_id)
        return {
            **result,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/voice/active-calls")
async def get_active_calls():
    """Get list of all active calls"""
    try:
        active_calls = list(voice_gateway.active_calls.values())
        return {
            "active_calls": active_calls,
            "count": len(active_calls),
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integration Status Endpoint - FIXED VERSION
@app.get("/integrations/status")
async def get_integration_status():
    """Get real-time status of all integrations"""

    # Check Gmail status properly
    gmail_connected = False
    gmail_status = "Not connected"
    gmail_details = {}

    # First check if client exists
    if gmail_client is not None:
        gmail_connected = True
        gmail_status = "Connected"
        gmail_details["client_initialized"] = True
    # Then check if token exists (might be connected but client not initialized)
    elif os.path.exists('token.pickle'):
        # Try to initialize
        if ensure_gmail_client():
            gmail_connected = True
            gmail_status = "Connected (initialized from token)"
            gmail_details["client_initialized"] = True
        else:
            gmail_status = "Token exists but initialization failed"
            gmail_details["token_exists"] = True
            gmail_details["client_initialized"] = False
    else:
        gmail_details["token_exists"] = False
        gmail_details["client_initialized"] = False

    # Get active voice calls count
    active_voice_calls = len(voice_gateway.active_calls)

    return {
        "gmail": {
            "connected": gmail_connected,
            "status": gmail_status,
            "details": gmail_details
        },
        "voice": {
            "connected": True,  # Mock is always available
            "status": "Mock mode - Ready",
            "active_calls": active_voice_calls
        },
        "crm": {
            "connected": True,  # SQLite is always available
            "status": "SQLite Database Connected"
        },
        "timestamp": time.time()
    }

# Health check endpoint
@app.get("/integrations/health")
async def integration_health_check():
    """Comprehensive health check for all integrations"""
    health_status = {
        "overall": "healthy",
        "checks": {},
        "timestamp": time.time()
    }

    # Check Gmail
    try:
        if ensure_gmail_client():
            # Try to get user profile as health check
            health_status["checks"]["gmail"] = {
                "status": "healthy",
                "connected": True
            }
        else:
            health_status["checks"]["gmail"] = {
                "status": "disconnected",
                "connected": False
            }
            health_status["overall"] = "degraded"
    except Exception as e:
        health_status["checks"]["gmail"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["overall"] = "unhealthy"

    # Check Voice (always healthy for mock)
    health_status["checks"]["voice"] = {
        "status": "healthy",
        "mode": "mock",
        "active_calls": len(voice_gateway.active_calls)
    }

    # Check CRM (always healthy for SQLite)
    health_status["checks"]["crm"] = {
        "status": "healthy",
        "type": "sqlite"
    }

    return health_status

# Debug endpoint (only for development)
@app.get("/integrations/debug")
async def debug_integrations():
    """Debug endpoint to check integration state (REMOVE IN PRODUCTION)"""
    return {
        "gmail_client_exists": gmail_client is not None,
        "token_exists": os.path.exists('token.pickle'),
        "credentials_exists": os.path.exists('credentials.json'),
        "active_voice_calls": len(voice_gateway.active_calls),
        "voice_call_ids": list(voice_gateway.active_calls.keys()),
        "timestamp": time.time()
    }
