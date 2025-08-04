"""
FastAPI Gateway - REST API for MCP Sales Platform
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
import os
import time
import uuid
from datetime import datetime

# Import our MCP client (would be in client/ folder)
# from client.mcp_client import get_client, MCPSalesClient

# For demo, include client code inline
from mcp import ClientSession, StdioServerParameters
import json

# Import integration modules
try:
    from gmail_client import GmailClient
    from email_analyzer import EmailAnalyzer
    from voice_mock import VoiceMockGateway
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    print("⚠️  Integration modules not available - using mock data")

# Auto-initialize Gmail if token exists
gmail_client = None
if INTEGRATIONS_AVAILABLE:
    try:
        import os
        if os.path.exists('token.pickle'):
            gmail_client = GmailClient()
            print("✅ Gmail client auto-initialized from existing token")
    except Exception as e:
        print(f"⚠️ Gmail auto-initialization skipped: {e}")
        print("   Users will need to authenticate through the UI")

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Sales MCP Platform API",
    description="REST API Gateway for AI-powered Sales Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class DealCreate(BaseModel):
    account_id: int
    name: str
    amount: float
    stage: str = "Prospecting"
    close_date: Optional[str] = None

class DealStageUpdate(BaseModel):
    new_stage: str
    probability: Optional[int] = None
    notes: Optional[str] = None

# Integration models
class EmailResponse(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class VoiceCallRequest(BaseModel):
    participant: str

# Chat Models
class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "sales-ai-v1"
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = 500
    stream: bool = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]

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

# Simple client manager (in production, use the full client)
class SimpleClient:
    def __init__(self):
        self.connected = False

    async def connect(self):
        self.connected = True
        return True

    async def mock_response(self, endpoint: str):
        """Return mock responses for demo"""
        if endpoint == "accounts":
            return [
                {"id": 1, "name": "Acme Corp", "industry": "Technology", "annual_revenue": 50000000},
                {"id": 2, "name": "Global Dynamics", "industry": "Manufacturing", "annual_revenue": 100000000}
            ]
        elif endpoint == "pipeline":
            return {
                "total_pipeline_value": 2500000,
                "weighted_pipeline_value": 850000,
                "win_rate": 28.5,
                "pipeline_stages": [
                    {"stage": "Prospecting", "deal_count": 15, "total_value": 750000},
                    {"stage": "Qualification", "deal_count": 10, "total_value": 800000},
                    {"stage": "Proposal", "deal_count": 5, "total_value": 950000}
                ]
            }
        elif endpoint == "forecast":
            return {
                "period": "next_quarter",
                "forecast": {
                    "expected": 850000,
                    "low": 680000,
                    "high": 1020000,
                    "confidence": "80%"
                }
            }
        elif endpoint == "metrics":
            return {
                "revenue_metrics": {
                    "closed_revenue": 450000,
                    "pipeline_value": 2500000,
                    "avg_deal_size": 75000
                },
                "conversion_metrics": {
                    "win_rate": 28.5,
                    "avg_sales_cycle_days": 45
                }
            }
        elif endpoint == "hot_deals":
            return [
                {
                    "deal_id": 1,
                    "account_name": "Acme Corp",
                    "amount": 150000,
                    "score": 85,
                    "priority": "🔥 Hot",
                    "recommended_action": "Schedule demo this week"
                },
                {
                    "deal_id": 2,
                    "account_name": "TechStart",
                    "amount": 75000,
                    "score": 72,
                    "priority": "🟡 Warm",
                    "recommended_action": "Send proposal follow-up"
                }
            ]
        return {}

# Global client instance
client = SimpleClient()

@app.on_event("startup")
async def startup_event():
    """Connect to MCP servers on startup"""
    await client.connect()
    logger.info("🚀 API Gateway started")

# Health check
@app.get("/health")
async def health_check():
    """Check if API and MCP servers are healthy"""
    return {
        "status": "healthy",
        "connected": client.connected,
        "timestamp": datetime.now().isoformat()
    }

# CRM Endpoints
@app.get("/api/accounts")
async def list_accounts(
    query: Optional[str] = None,
    industry: Optional[str] = None
):
    """List all accounts with optional filters"""
    try:
        accounts = await client.mock_response("accounts")
        return {"accounts": accounts, "count": len(accounts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts/{account_id}")
async def get_account(account_id: int):
    """Get detailed account information"""
    try:
        # Mock detailed response
        return {
            "account": {
                "id": account_id,
                "name": "Acme Corp",
                "industry": "Technology",
                "annual_revenue": 50000000
            },
            "contacts": [
                {"id": 1, "name": "John Doe", "title": "CEO", "email": "john@acme.com"}
            ],
            "deals": [
                {"id": 1, "name": "Q4 Enterprise Deal", "amount": 150000, "stage": "Proposal"}
            ],
            "total_deal_value": 150000
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deals")
async def create_deal(deal: DealCreate):
    """Create a new deal with AI scoring"""
    try:
        return {
            "deal": {
                "deal_id": 123,
                "account_id": deal.account_id,
                "name": deal.name,
                "amount": deal.amount,
                "stage": deal.stage
            },
            "score": {
                "score": 75,
                "priority": "🟡 Warm",
                "recommended_action": "Schedule follow-up within 3 days"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/deals/{deal_id}/stage")
async def update_deal_stage(deal_id: int, update: DealStageUpdate):
    """Update deal stage"""
    try:
        return {
            "deal_id": deal_id,
            "new_stage": update.new_stage,
            "probability": update.probability or 40,
            "message": f"Deal moved to {update.new_stage}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/api/analytics/dashboard")
async def get_dashboard():
    """Get complete sales dashboard"""
    try:
        pipeline = await client.mock_response("pipeline")
        forecast = await client.mock_response("forecast")
        metrics = await client.mock_response("metrics")

        return {
            "pipeline": pipeline,
            "forecast": forecast,
            "metrics": metrics,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/forecast")
async def get_forecast(
    period: str = "next_quarter",
    method: str = "hybrid"
):
    """Get AI-powered sales forecast"""
    try:
        forecast = await client.mock_response("forecast")
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/hot-deals")
async def get_hot_deals():
    """Get AI-scored hot deals requiring attention"""
    try:
        deals = await client.mock_response("hot_deals")
        return {"deals": deals, "count": len(deals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/conversions")
async def get_conversion_analytics(time_period: str = "last_quarter"):
    """Get funnel conversion analytics"""
    try:
        return {
            "time_period": time_period,
            "overall_metrics": {
                "win_rate": 28.5,
                "deals_won": 12,
                "deals_lost": 30
            },
            "funnel_stages": [
                {
                    "from_stage": "Prospecting",
                    "to_stage": "Qualification",
                    "conversion_rate": 65.0
                },
                {
                    "from_stage": "Qualification",
                    "to_stage": "Proposal",
                    "conversion_rate": 50.0
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/activities")
async def get_activity_analytics(
    time_period: str = "last_30_days",
    group_by: str = "activity_type"
):
    """Get sales activity analytics"""
    try:
        return {
            "time_period": time_period,
            "summary": {
                "total_activities": 245,
                "accounts_touched": 48,
                "activities_per_day": 8.2
            },
            "insights": [
                "Most activities occur on Tuesdays",
                "Email is most common activity type",
                "Top accounts get 80% of activities"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat endpoint that uses MCP servers"""
    
    user_message = request.messages[-1].content.lower()
    
    try:
        # Route to appropriate MCP server based on query
        if "account" in user_message or "tell me about" in user_message:
            # Extract company name (simple approach)
            if "techcorp" in user_message:
                # Call MCP CRM server
                crm_result = await mcp_crm.call_tool(
                    "search_accounts",
                    {"query": "TechCorp"}
                )
                
                # Format the response
                if crm_result and len(crm_result) > 0:
                    account = crm_result[0]
                    response_content = f"""I found information about TechCorp in our CRM:

**Account: {account.get('name', 'TechCorp')}**
- Industry: {account.get('industry', 'Technology')}
- Annual Revenue: ${account.get('annual_revenue', 0):,}
- Employees: {account.get('employees', 0)}

**Active Opportunities:**"""
                    
                    # Get deals for this account
                    deals_result = await mcp_crm.call_tool(
                        "get_deals",
                        {"account_id": account.get('id', 1)}
                    )
                    
                    for deal in deals_result[:3]:
                        response_content += f"\n- {deal['name']} - ${deal['amount']:,} ({deal['stage']})"
                else:
                    response_content = "I couldn't find that account. Try 'TechCorp' or 'Acme Corp'."
                    
        elif "forecast" in user_message or "pipeline" in user_message:
            # Call MCP Analytics server
            forecast_result = await mcp_analytics.call_tool(
                "forecast_revenue",
                {"period": "current_quarter"}
            )
            
            response_content = f"""Here's your sales forecast:

**Q1 2024 Forecast:**
- Expected Revenue: ${forecast_result.get('forecast', 0):,}
- Confidence: {forecast_result.get('confidence', 0)}%
- Pipeline Value: ${forecast_result.get('pipeline_value', 0):,}

**Top Opportunities:**
1. TechCorp - $750K (85% probability)
2. Acme Corp - $450K (72% probability)

Would you like me to analyze specific deals?"""
            
        elif "email" in user_message and "draft" in user_message:
            response_content = """I'll draft an email for you:

**Subject:** Following up on our AI Sales Platform discussion

**Email Draft:**

Hi [Contact Name],

I wanted to follow up on our conversation about transforming your sales operations with our AI platform.

Based on your team's challenges with manual CRM updates, our solution can:
• Save 3 hours per rep daily on admin tasks
• Increase email response rates by 40%
• Provide real-time coaching during calls

Would you be available for a 15-minute call this week to discuss implementation?

Best regards,
[Your Name]

Would you like me to personalize this for a specific contact?"""
            
        else:
            response_content = """I'm your AI Sales Assistant. I can help with:

🔍 **CRM Lookups**: "Tell me about TechCorp"
📊 **Forecasting**: "What's my pipeline forecast?"
📧 **Email Drafts**: "Draft a follow-up email"
💰 **Deal Analysis**: "Analyze my top deals"

What would you like help with?"""
            
    except Exception as e:
        response_content = f"I encountered an error: {str(e)}. Please try again."
    
    # Return OpenAI-compatible response
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4()}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response_content),
                finish_reason="stop"
            )
        ],
        usage={
            "prompt_tokens": len(str(request.messages)),
            "completion_tokens": len(response_content),
            "total_tokens": len(str(request.messages)) + len(response_content)
        }
    )

# Models endpoint for OpenAI compatibility
@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "sales-ai-v1",
                "object": "model",
                "created": 1677610602,
                "owned_by": "salesai",
                "permission": [],
                "root": "sales-ai-v1",
                "parent": None
            }
        ]
    }

# Integration endpoints
if INTEGRATIONS_AVAILABLE:
    # Initialize integration services
    email_analyzer = EmailAnalyzer()
    voice_gateway = VoiceMockGateway()

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

else:
    # Mock integration endpoints
    @app.post("/integrations/gmail/auth")
    async def gmail_authenticate():
        return {"status": "success", "message": "Mock Gmail authentication"}

    @app.get("/integrations/gmail/unread")
    async def get_unread_emails(max_results: int = 10):
        return {
            "emails": [
                {
                    "id": "mock_1",
                    "from": "prospect@company.com",
                    "subject": "Interested in your solution",
                    "snippet": "We're looking for a sales platform...",
                    "analysis": {
                        "intent": "buying",
                        "urgency": "medium",
                        "score": 75
                    }
                }
            ]
        }

    @app.post("/integrations/voice/start-call")
    async def start_voice_call(call_request: VoiceCallRequest):
        return {"call_id": "mock_call_123", "status": "started"}

    @app.get("/integrations/status")
    async def get_integration_status():
        return {
            "gmail": False,
            "voice": False,
            "available": False,
            "note": "Using mock data"
        }

# Run the server
if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting AI Sales MCP API Gateway")
    print("📍 API Docs: http://localhost:8000/docs")
    print("🔗 Endpoints:")
    print("   - GET  /api/accounts")
    print("   - GET  /api/accounts/{id}")
    print("   - POST /api/deals")
    print("   - PUT  /api/deals/{id}/stage")
    print("   - GET  /api/analytics/dashboard")
    print("   - GET  /api/analytics/forecast")
    print("   - GET  /api/analytics/hot-deals")
    print("   - GET  /api/analytics/conversions")
    print("   - GET  /api/analytics/activities")
    print("   - POST /integrations/gmail/auth")
    print("   - GET  /integrations/gmail/unread")
    print("   - POST /integrations/voice/start-call")

    uvicorn.run(app, host="0.0.0.0", port=8000)
