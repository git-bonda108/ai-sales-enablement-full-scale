#!/usr/bin/env python3
"""
Quick API Gateway Fix
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for testing
MOCK_METRICS = {
    "sales_performance": {
        "total_revenue": 1250000,
        "deals_closed": 47,
        "conversion_rate": 24.5,
        "average_deal_size": 26595
    },
    "activity_metrics": {
        "calls_made": 342,
        "emails_sent": 1058,
        "meetings_scheduled": 89,
        "proposals_sent": 34
    },
    "ai_insights": {
        "sentiment_score": 78.5,
        "engagement_level": "High",
        "recommended_actions": 12,
        "risk_alerts": 3
    }
}

MOCK_ACCOUNTS = [
    {
        "id": "acc_001",
        "name": "Acme Corp",
        "industry": "Technology",
        "revenue": 50000,
        "status": "Active",
        "health_score": 85
    },
    {
        "id": "acc_002", 
        "name": "Global Dynamics",
        "industry": "Manufacturing",
        "revenue": 100000,
        "status": "Active",
        "health_score": 72
    }
]

MOCK_DEALS = [
    {
        "id": "deal_001",
        "name": "Enterprise Software License",
        "account": "Acme Corp",
        "value": 125000,
        "stage": "Negotiation",
        "probability": 75,
        "close_date": "2024-09-15"
    }
]

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/metrics")
async def get_metrics():
    return MOCK_METRICS

@app.get("/api/accounts")
async def get_accounts():
    return {"accounts": MOCK_ACCOUNTS}

@app.get("/api/deals")
async def get_deals():
    return {"deals": MOCK_DEALS}

@app.get("/api/activities")
async def get_activities():
    return {"activities": []}

@app.get("/api/analytics/dashboard")
async def get_dashboard():
    return {
        "pipeline": {
            "stages": ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won"],
            "counts": [100, 75, 50, 25, 15]
        },
        "forecast": {
            "total_projected": 2500000,
            "growth_rate": 12.5,
            "confidence": 85.0
        },
        "metrics": {
            "total_revenue": 1250000,
            "active_deals": 45,
            "win_rate": 68.5,
            "avg_deal_size": 27500
        }
    }

@app.get("/crm/accounts")
async def get_crm_accounts():
    return MOCK_ACCOUNTS

@app.get("/crm/deals")
async def get_crm_deals():
    return MOCK_DEALS

@app.post("/crm/accounts")
async def create_crm_account(account: dict):
    return {
        "id": f"acc_{len(MOCK_ACCOUNTS) + 1:03d}",
        "name": account.get("name", "New Account"),
        "industry": account.get("industry", "Technology"),
        "revenue": 0,
        "status": "Active",
        "health_score": 75
    }

@app.post("/crm/deals")
async def create_crm_deal(deal: dict):
    return {
        "id": f"deal_{len(MOCK_DEALS) + 1:03d}",
        "name": deal.get("name", "New Deal"),
        "account": deal.get("account_name", "Unknown Account"),
        "value": deal.get("amount", 50000),
        "stage": deal.get("stage", "Prospecting"),
        "probability": 50,
        "close_date": "2024-12-31"
    }

@app.post("/ai/process-transcript")
async def process_transcript(request: dict):
    content = request.get("content", "")
    return {
        "entities": [
            {"type": "Company", "value": "TechCorp Inc"},
            {"type": "Person", "value": "John Smith"},
            {"type": "Amount", "value": "$50,000"},
            {"type": "Date", "value": "Q2 2024"}
        ],
        "sentiment": {
            "label": "Positive",
            "confidence": 85.5,
            "score": 0.8
        },
        "key_topics": [
            "Product demonstration",
            "Pricing discussion",
            "Implementation timeline",
            "Technical requirements"
        ],
        "summary": "The call was positive with the prospect showing strong interest in our solution. Key discussion points included product features, pricing structure, and implementation timeline. The prospect is ready to move forward with a $50,000 deal.",
        "confidence": 94
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    messages = request.get("messages", [])
    user_message = ""
    if messages:
        user_message = messages[-1].get("content", "")
    
    # Generate contextual response based on user message
    response_content = generate_ai_response(user_message)
    
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": "sales-ai-v1",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

def generate_ai_response(user_message: str) -> str:
    """Generate contextual AI response based on user message"""
    message_lower = user_message.lower()
    
    if "opportunity" in message_lower or "deal" in message_lower or "top" in message_lower:
        return """Based on our analytics, here are your top 3 opportunities:

**1. GlobalTech Expansion** - $1.2M
- 85% win probability
- Decision expected by Q2 2024
- Similar to 3 successful deals last year

**2. Enterprise Corp Platform** - $750K  
- 78% win probability
- Strong technical fit confirmed
- Budget approved by CFO

**3. TechCorp Upgrade** - $450K
- 92% win probability  
- Existing customer expansion
- Competing against internal solution

Would you like detailed insights on any of these opportunities?"""
    
    elif "revenue" in message_lower or "sales" in message_lower:
        return """📊 **Sales Performance Summary:**

**Current Quarter:**
- Total Revenue: $1,250,000
- Growth Rate: +12.5% vs last quarter
- Active Deals: 45
- Win Rate: 68.5%

**Key Insights:**
- Enterprise deals are driving 70% of revenue
- Average deal size increased by 15%
- Sales cycle shortened by 8 days
- Top performing region: West Coast

**Recommendations:**
1. Focus on high-value enterprise opportunities
2. Leverage existing customer relationships
3. Invest in sales enablement tools
4. Expand into new vertical markets"""
    
    elif "account" in message_lower or "customer" in message_lower:
        return """🏢 **Account Management Overview:**

**Top Accounts by Revenue:**
1. **Acme Corp** - $500K (Technology)
2. **Global Dynamics** - $100K (Manufacturing)
3. **TechFlow Solutions** - $75K (Technology)

**Account Health Metrics:**
- Average Account Health Score: 78/100
- Customer Satisfaction: 4.2/5.0
- Renewal Rate: 92%
- Expansion Rate: 15%

**Recent Activities:**
- 12 new accounts created this month
- 8 accounts upgraded their plans
- 3 accounts at risk (being monitored)

Would you like to see specific account details or create a new account?"""
    
    elif "pipeline" in message_lower or "forecast" in message_lower:
        return """🎯 **Sales Pipeline Analysis:**

**Pipeline Stages:**
- **Prospecting:** 100 deals ($2.5M)
- **Qualification:** 75 deals ($1.8M)
- **Proposal:** 50 deals ($1.2M)
- **Negotiation:** 25 deals ($600K)
- **Closed Won:** 15 deals ($350K)

**Forecast for Next Quarter:**
- Projected Revenue: $2.5M
- Confidence Level: 85%
- Growth Rate: 15%

**Pipeline Health:**
- Weighted Pipeline Value: $6.7M
- Average Deal Size: $45K
- Sales Velocity: 45 days
- Conversion Rates: 15% (Prospecting → Won)"""
    
    elif "help" in message_lower or "what can you do" in message_lower:
        return """🤖 **I'm your AI Sales Assistant! Here's what I can help you with:**

**📊 Analytics & Insights:**
- Sales performance analysis
- Revenue forecasting
- Pipeline optimization
- Deal scoring and prioritization

**🏢 Account Management:**
- Account health monitoring
- Customer relationship insights
- Account creation and updates
- Activity tracking

**💼 Deal Management:**
- Deal pipeline analysis
- Win probability assessment
- Deal creation and updates
- Competitive intelligence

**📧 Communication:**
- Email response generation
- Meeting scheduling assistance
- Follow-up reminders
- Proposal creation

**📝 Process Automation:**
- Transcript analysis
- Entity extraction
- Sentiment analysis
- Action item identification

Just ask me anything about your sales data, accounts, deals, or processes!"""
    
    else:
        return """I'm here to help with your sales questions! I can provide insights on:

• Sales performance and analytics
• Account and customer management  
• Deal pipeline and forecasting
• Revenue optimization
• Process automation

What would you like to know about today?"""

@app.post("/integrations/gmail/auth")
async def gmail_auth():
    return {"status": "authenticated", "message": "Gmail authentication successful"}

@app.get("/integrations/gmail/unread")
async def get_unread_emails(max_results: int = 10):
    return {
        "emails": [
            {
                "id": "email_001",
                "subject": "Follow up on proposal",
                "from": "client@example.com",
                "snippet": "Hi, I wanted to follow up on the proposal you sent...",
                "date": "2024-08-04T10:30:00Z"
            }
        ]
    }

@app.post("/integrations/gmail/generate-response/{email_id}")
async def generate_email_response(email_id: str):
    return {
        "response": "Thank you for your email. I'll review the proposal and get back to you shortly.",
        "email_id": email_id
    }

@app.post("/integrations/gmail/send")
async def send_email(email_data: dict):
    """Send email via Gmail API"""
    to_email = email_data.get("to", "")
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    email_id = email_data.get("email_id", "")
    
    # Mock email sending (in real implementation, this would use Gmail API)
    return {
        "status": "sent",
        "message": f"Email sent successfully to {to_email}",
        "email_id": email_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/integrations/status")
async def get_integrations_status():
    return {
        "gmail": {"status": "connected", "last_sync": "2024-08-04T10:30:00Z"},
        "crm": {"status": "connected", "last_sync": "2024-08-04T10:30:00Z"},
        "analytics": {"status": "connected", "last_sync": "2024-08-04T10:30:00Z"}
    }

@app.get("/api/transcripts")
async def get_transcripts():
    return {
        "transcripts": [
            {
                "id": "trans_001",
                "account": "Acme Corp",
                "sentiment": 0.8,
                "summary": "Discussed expansion plans",
                "timestamp": "2024-08-04T10:30:00"
            }
        ]
    }

@app.get("/api/emails")
async def get_emails():
    return {
        "emails": [
            {
                "id": "email_001",
                "subject": "Follow-up: Product Demo",
                "account": "Global Dynamics",
                "sentiment": 0.75,
                "timestamp": "2024-08-04T14:20:00"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Quick Fix API Gateway on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
