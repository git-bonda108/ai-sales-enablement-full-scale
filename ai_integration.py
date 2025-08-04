"""
AI Integration Module - OpenAI GPT-3.5-turbo Integration
Provides intelligent chat responses, transcript processing, and email generation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum

# OpenAI imports
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available. Install with: pip install openai")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class AIStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FALLBACK = "fallback"

@dataclass
class AIResponse:
    content: str
    status: AIStatus
    model_used: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

class AIIntegration:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.status = AIStatus.UNAVAILABLE
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Initialize OpenAI client
        self._initialize_client()
        
        # CRM data cache for context
        self.crm_context = {
            "accounts": [],
            "deals": [],
            "contacts": [],
            "activities": []
        }
        
    def _initialize_client(self):
        """Initialize OpenAI client with proper error handling"""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI package not available")
            self.status = AIStatus.UNAVAILABLE
            return
            
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
            self.status = AIStatus.UNAVAILABLE
            return
            
        try:
            self.client = OpenAI(api_key=self.api_key)
            # Test the connection
            self._test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.status = AIStatus.UNAVAILABLE
            
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            self.status = AIStatus.AVAILABLE
            logger.info("OpenAI API connection successful")
        except Exception as e:
            logger.error(f"OpenAI API connection failed: {e}")
            self.status = AIStatus.UNAVAILABLE
            
    def update_crm_context(self, context_data: Dict[str, Any]):
        """Update CRM context for AI responses"""
        self.crm_context.update(context_data)
        logger.info("Updated CRM context for AI integration")
        
    def _build_system_prompt(self, context_type: str = "general") -> str:
        """Build context-aware system prompts"""
        base_prompt = """You are an AI sales assistant for a CRM platform. 
        You help with deal analysis, account management, and sales activities.
        Provide concise, actionable responses."""
        
        if context_type == "deal_analysis":
            deals_info = "\n".join([
                f"Deal: {deal.get('name', 'Unknown')} - Stage: {deal.get('stage', 'Unknown')} - Amount: ${deal.get('amount', 0):,.0f}"
                for deal in self.crm_context.get("deals", [])
            ])
            return f"{base_prompt}\n\nCurrent deals:\n{deals_info}\n\nAnalyze deals and provide insights."
            
        elif context_type == "email_generation":
            return f"{base_prompt}\n\nGenerate professional, context-aware emails for sales activities."
            
        elif context_type == "transcript_analysis":
            return f"{base_prompt}\n\nExtract key information from sales calls and identify opportunities."
            
        return base_prompt
        
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        context_type: str = "general"
    ) -> AIResponse:
        """Generate chat completion with OpenAI"""
        
        if self.status != AIStatus.AVAILABLE:
            return self._fallback_response(messages)
            
        try:
            # Add system prompt
            system_prompt = self._build_system_prompt(context_type)
            enhanced_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=enhanced_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost estimate (approximate)
            cost_estimate = self._calculate_cost(usage.total_tokens)
            
            return AIResponse(
                content=content,
                status=AIStatus.AVAILABLE,
                model_used=self.model,
                tokens_used=usage.total_tokens,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response(messages)
            
    def _fallback_response(self, messages: List[Dict[str, str]]) -> AIResponse:
        """Provide fallback responses when OpenAI is unavailable"""
        last_message = messages[-1]["content"].lower() if messages else ""
        
        # Simple keyword-based responses
        if "deal" in last_message and "attention" in last_message:
            response = "Based on your CRM data, I'd recommend focusing on deals in the 'Proposal' stage. Consider following up with prospects who haven't responded in the last 7 days."
        elif "create" in last_message and "account" in last_message:
            response = "I can help you create a new account. Please provide the company name, industry, and any additional details you'd like to include."
        elif "draft" in last_message and "email" in last_message:
            response = "I can help draft a follow-up email. Please specify the prospect name and what type of follow-up you need (proposal, meeting request, etc.)."
        elif "analyze" in last_message and "deals" in last_message:
            response = "I can analyze your deals. Please specify what aspect you'd like me to focus on: pipeline health, conversion rates, or specific deal stages."
        else:
            response = "I'm currently in fallback mode. I can help with deal analysis, account creation, email drafting, and transcript processing. What would you like to do?"
            
        return AIResponse(
            content=response,
            status=AIStatus.FALLBACK,
            model_used="fallback",
            tokens_used=0,
            cost_estimate=0.0
        )
        
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate approximate cost for GPT-3.5-turbo"""
        # GPT-3.5-turbo pricing: $0.0015 per 1K input tokens, $0.002 per 1K output tokens
        # This is a rough estimate
        return (tokens * 0.0015) / 1000
        
    async def process_transcript(self, transcript: str) -> Dict[str, Any]:
        """Process sales call transcript with AI"""
        
        system_prompt = """Analyze this sales call transcript and extract:
        1. Key entities (companies, people, amounts, dates)
        2. Opportunities and deal potential
        3. Next actions and follow-ups
        4. Risk factors or concerns
        5. Budget and timeline information
        
        Return as JSON with these fields:
        - entities: list of key entities found
        - opportunities: list of opportunities with scores (1-10)
        - next_actions: list of specific next actions
        - risk_factors: list of potential risks
        - budget_info: budget and timeline details
        - overall_score: overall opportunity score (1-10)
        """
        
        messages = [
            {"role": "user", "content": f"Analyze this transcript:\n\n{transcript}"}
        ]
        
        response = await self.chat_completion(messages, "transcript_analysis")
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback parsing
            analysis = {
                "entities": [],
                "opportunities": [{"description": "Opportunity found", "score": 5}],
                "next_actions": ["Follow up with prospect"],
                "risk_factors": [],
                "budget_info": "Budget information not clearly specified",
                "overall_score": 5
            }
            
        return {
            "analysis": analysis,
            "status": response.status.value,
            "model_used": response.model_used,
            "tokens_used": response.tokens_used,
            "cost_estimate": response.cost_estimate
        }
        
    async def generate_email(
        self, 
        prospect_name: str, 
        email_type: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate context-aware professional emails"""
        
        email_prompts = {
            "follow_up": f"Generate a professional follow-up email for {prospect_name} after our recent conversation. Include specific next steps and a clear call to action.",
            "proposal": f"Generate a professional email to {prospect_name} introducing our proposal. Include key benefits and next steps.",
            "meeting_request": f"Generate a professional email to {prospect_name} requesting a meeting to discuss their needs and how we can help.",
            "thank_you": f"Generate a professional thank you email to {prospect_name} for their time and interest."
        }
        
        prompt = email_prompts.get(email_type, email_prompts["follow_up"])
        
        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, "email_generation")
        
        return {
            "email_content": response.content,
            "status": response.status.value,
            "model_used": response.model_used,
            "tokens_used": response.tokens_used,
            "cost_estimate": response.cost_estimate
        }
        
    async def analyze_deals(self, query: str = "Analyze my deals") -> Dict[str, Any]:
        """Analyze deals using AI"""
        
        deals_info = "\n".join([
            f"Deal: {deal.get('name', 'Unknown')} - Stage: {deal.get('stage', 'Unknown')} - Amount: ${deal.get('amount', 0):,.0f} - Close Date: {deal.get('close_date', 'Not set')}"
            for deal in self.crm_context.get("deals", [])
        ])
        
        messages = [
            {"role": "user", "content": f"{query}\n\nDeals data:\n{deals_info}"}
        ]
        
        response = await self.chat_completion(messages, "deal_analysis")
        
        return {
            "analysis": response.content,
            "status": response.status.value,
            "model_used": response.model_used,
            "tokens_used": response.tokens_used,
            "cost_estimate": response.cost_estimate
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get AI integration status"""
        return {
            "status": self.status.value,
            "model": self.model,
            "api_available": self.status == AIStatus.AVAILABLE,
            "fallback_mode": self.status == AIStatus.FALLBACK
        }

# Global AI integration instance
ai_integration = AIIntegration() 