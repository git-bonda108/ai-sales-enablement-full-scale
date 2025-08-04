import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import uvicorn
import uuid
import time

app = FastAPI(title="AI Sales Platform API Gateway")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== PYDANTIC MODELS ==========

class Account(BaseModel):
    name: str
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employees: Optional[int] = None

class Deal(BaseModel):
    name: str
    amount: float
    stage: str
    account_id: int
    contact_id: Optional[int] = None
    close_date: Optional[str] = None

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    account_id: Optional[int] = None

# ========== CHAT MODELS FOR BATCH 9 ==========
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

# ========== MCP CLIENT SETUP ==========

class MCPClient:
    def __init__(self, server_name: str, command: List[str]):
        self.server_name = server_name
        self.server_params = StdioServerParameters(
            command=command[0],
            args=command[1:] if len(command) > 1 else []
        )
        self.session = None
        self.context = None

    async def connect(self):
        # CORRECT WAY - stdio_client returns a context manager
        self.context = stdio_client(self.server_params)
        self.session = await self.context.__aenter__()
        
    async def call_tool(self, tool_name: str, arguments: dict):
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(tool_name, arguments)
        return result.content
        
    async def close(self):
        if self.context:
            await self.context.__aexit__(None, None, None)

# Initialize MCP clients
mcp_crm = MCPClient("crm-server", ["python", "-m", "servers.crm_server"])
mcp_analytics = MCPClient("analytics-server", ["python", "-m", "servers.analytics_server"])

# ========== ENDPOINTS ==========

@app.on_event("startup")
async def startup_event():
    """Connect to MCP servers on startup"""
    await mcp_crm.connect()
    await mcp_analytics.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MCP servers on shutdown"""
    await mcp_crm.close()
    await mcp_analytics.close()

@app.get("/")
async def root():
    return {"message": "AI Sales Platform API Gateway", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "crm": "connected" if mcp_crm.session else "disconnected",
            "analytics": "connected" if mcp_analytics.session else "disconnected"
        }
    }

# ========== CHAT ENDPOINTS FOR BATCH 9 ==========

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat endpoint that uses MCP servers"""

    user_message = request.messages[-1].content.lower()

    try:
        # Route to appropriate MCP server based on query
        if "account" in user_message or "tell me about" in user_message:
            # Extract company name (simple approach)
            if "techcorp" in user_message:
                # Use mock data for now
                response_content = """I found information about TechCorp in our CRM:

**Account: TechCorp Solutions**
- Industry: Technology
- Annual Revenue: $50,000,000
- Employees: 250

**Active Opportunities:**
- Enterprise Platform Upgrade - $750,000 (Proposal)
- Cloud Migration Project - $450,000 (Qualification)
- AI Integration Services - $300,000 (Discovery)

**Recent Activity:**
- Demo scheduled for next week
- Proposal sent 3 days ago
- Follow-up call completed yesterday"""
            else:
                response_content = "I couldn't find that account. Try 'TechCorp' or 'Acme Corp'."

        elif "forecast" in user_message or "pipeline" in user_message:
            # Use mock data for now
            response_content = """Here's your sales forecast:

**Q1 2024 Forecast:**
- Expected Revenue: $850,000
- Confidence: 80%
- Pipeline Value: $2,500,000

**Top Opportunities:**
1. TechCorp - $750K (85% probability)
2. Acme Corp - $450K (72% probability)
3. Global Dynamics - $300K (65% probability)

**Pipeline Stages:**
- Prospecting: 15 deals ($750K)
- Qualification: 10 deals ($800K)
- Proposal: 5 deals ($950K)

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

# ========== CRM ENDPOINTS ==========

@app.get("/crm/accounts/search")
async def search_accounts(query: str):
    """Search for accounts"""
    result = await mcp_crm.call_tool("search_accounts", {"query": query})
    return {"accounts": result}

@app.post("/crm/accounts")
async def create_account(account: Account):
    """Create a new account"""
    result = await mcp_crm.call_tool("create_account", account.dict())
    return {"account": result}

@app.get("/crm/deals")
async def get_deals(account_id: Optional[int] = None):
    """Get deals, optionally filtered by account"""
    result = await mcp_crm.call_tool("get_deals", {"account_id": account_id})
    return {"deals": result}

@app.post("/crm/deals")
async def create_deal(deal: Deal):
    """Create a new deal"""
    result = await mcp_crm.call_tool("create_deal", deal.dict())
    return {"deal": result}

# ========== ANALYTICS ENDPOINTS ==========

@app.get("/analytics/forecast")
async def get_forecast(period: str = "current_quarter"):
    """Get revenue forecast"""
    result = await mcp_analytics.call_tool("forecast_revenue", {"period": period})
    return result

@app.post("/analytics/score-deal")
async def score_deal(deal_id: int):
    """Score a deal's probability"""
    result = await mcp_analytics.call_tool("score_deal", {"deal_id": deal_id})
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
