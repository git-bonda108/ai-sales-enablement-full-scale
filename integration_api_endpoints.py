# Add these endpoints to your api_gateway.py

from gmail_client import GmailClient
from email_analyzer import EmailAnalyzer
from voice_mock import VoiceMockGateway
import asyncio
from typing import Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

# Initialize services
gmail_client = None
email_analyzer = EmailAnalyzer()
voice_gateway = VoiceMockGateway()

# Pydantic models
class EmailResponse(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class VoiceCallRequest(BaseModel):
    participant: str

# Gmail Endpoints
@app.post("/integrations/gmail/auth")
async def gmail_authenticate():
    '''Authenticate with Gmail'''
    global gmail_client
    try:
        gmail_client = GmailClient()
        return {"status": "success", "message": "Gmail authenticated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/integrations/gmail/unread")
async def get_unread_emails(max_results: int = 10):
    '''Get unread emails with analysis'''
    if not gmail_client:
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        emails = gmail_client.get_unread_emails(max_results)

        # Analyze each email
        analyzed_emails = []
        for email in emails:
            analysis = email_analyzer.analyze_email(email)
            analyzed_emails.append({
                **email,
                'analysis': analysis
            })

        return {"emails": analyzed_emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/gmail/send")
async def send_email(email_response: EmailResponse):
    '''Send an email'''
    if not gmail_client:
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        result = gmail_client.send_email(
            to=email_response.to,
            subject=email_response.subject,
            body=email_response.body,
            thread_id=email_response.thread_id
        )
        return {"status": "success", "message_id": result.get('id')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/gmail/generate-response/{email_id}")
async def generate_email_response(email_id: str):
    '''Generate AI response for an email'''
    if not gmail_client:
        raise HTTPException(status_code=401, detail="Gmail not authenticated")

    try:
        # Get the email
        emails = gmail_client.get_unread_emails(max_results=20)
        email = next((e for e in emails if e['id'] == email_id), None)

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        # Analyze and generate response
        analysis = email_analyzer.analyze_email(email)
        response = email_analyzer.generate_email_response(analysis)

        return {
            "email_id": email_id,
            "suggested_response": response,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice Mock Endpoints
@app.post("/integrations/voice/start-call")
async def start_voice_call(call_request: VoiceCallRequest):
    '''Start a mock voice call'''
    try:
        import uuid
        call_id = str(uuid.uuid4())
        result = voice_gateway.start_mock_call(call_id, call_request.participant)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/voice/transcript/{call_id}")
async def get_call_transcript(call_id: str, last_index: int = 0):
    '''Get real-time transcript for a call'''
    try:
        result = voice_gateway.get_real_time_transcript(call_id, last_index)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/voice/end-call/{call_id}")
async def end_voice_call(call_id: str):
    '''End a voice call and get analytics'''
    try:
        result = voice_gateway.end_call(call_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integration Status Endpoint
@app.get("/integrations/status")
async def get_integration_status():
    '''Get status of all integrations'''
    return {
        "gmail": {
            "connected": gmail_client is not None,
            "status": "Connected" if gmail_client else "Not connected"
        },
        "voice": {
            "connected": True,  # Mock is always available
            "status": "Mock mode - Ready"
        },
        "crm": {
            "connected": True,  # SQLite is always available
            "status": "SQLite Database Connected"
        }
    }
