#!/usr/bin/env python3
"""
Generate comprehensive test data for AI Sales Platform
Includes accounts, deals, transcripts, and emails
"""

import json
import random
from datetime import datetime, timedelta

def generate_test_data():
    """Generate all test data needed for demo"""

    # Sample accounts
    accounts = [
        {
            "id": 1,
            "name": "TechCorp Industries",
            "industry": "Technology",
            "revenue": 50000000,
            "employees": 500,
            "email": "sales@techcorp.example",
            "tags": ["enterprise", "high-value", "tech-savvy"]
        },
        {
            "id": 2,
            "name": "Global Finance Solutions",
            "industry": "Financial Services",
            "revenue": 100000000,
            "employees": 1200,
            "email": "procurement@globalfinance.example",
            "tags": ["fortune-500", "compliance-focused"]
        },
        {
            "id": 3,
            "name": "Healthcare Innovations",
            "industry": "Healthcare",
            "revenue": 30000000,
            "employees": 300,
            "email": "it@healthinnovate.example",
            "tags": ["mid-market", "growth-stage"]
        },
        {
            "id": 4,
            "name": "Retail Masters",
            "industry": "Retail",
            "revenue": 75000000,
            "employees": 800,
            "email": "ops@retailmasters.example",
            "tags": ["multi-location", "seasonal"]
        },
        {
            "id": 5,
            "name": "Manufacturing Plus",
            "industry": "Manufacturing",
            "revenue": 40000000,
            "employees": 400,
            "email": "purchasing@mfgplus.example",
            "tags": ["traditional", "cost-conscious"]
        }
    ]

    # Sample deals with different stages
    deals = [
        {
            "id": 1,
            "title": "TechCorp Enterprise Platform",
            "account_id": 1,
            "value": 500000,
            "stage": "Proposal",
            "probability": 0.75,
            "close_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "notes": "Decision maker engaged, security review pending"
        },
        {
            "id": 2,
            "title": "Global Finance Compliance Suite",
            "account_id": 2,
            "value": 1200000,
            "stage": "Negotiation",
            "probability": 0.85,
            "close_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "notes": "Contract under legal review, pricing agreed"
        },
        {
            "id": 3,
            "title": "Healthcare Analytics Package",
            "account_id": 3,
            "value": 250000,
            "stage": "Qualification",
            "probability": 0.40,
            "close_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "notes": "Initial interest, budget confirmation needed"
        },
        {
            "id": 4,
            "title": "Retail POS Integration",
            "account_id": 4,
            "value": 150000,
            "stage": "Discovery",
            "probability": 0.50,
            "close_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "notes": "Technical requirements gathering"
        },
        {
            "id": 5,
            "title": "Manufacturing Automation",
            "account_id": 5,
            "value": 300000,
            "stage": "Closed Won",
            "probability": 1.0,
            "close_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "notes": "Implementation starting next week"
        }
    ]

    # Sample transcripts for testing
    transcripts = [
        {
            "id": 1,
            "title": "TechCorp Discovery Call",
            "date": datetime.now().isoformat(),
            "content": """
Rep: Thanks for joining, Sarah. Can you tell me about your current challenges?
Sarah: Our sales team has grown from 75 to 150 reps, and our CRM can't keep up.
Rep: What specific pain points are you experiencing?
Sarah: Reps spend 3 hours daily on data entry. We need automation badly.
Rep: What's your budget for a solution?
Sarah: We've allocated $400,000 to $600,000 annually.
Rep: And your timeline?
Sarah: We need implementation before Q3 - within 60 days.
Rep: Perfect. Let me show you how our AI can save 20 hours per rep weekly.
            """,
            "expected_extraction": {
                "company_size": "150 reps",
                "pain_points": ["3 hours daily data entry", "CRM can't keep up"],
                "budget_range": [400000, 600000],
                "timeline": "60 days",
                "value_prop": "save 20 hours per rep weekly"
            }
        },
        {
            "id": 2,
            "title": "Global Finance Technical Call",
            "date": datetime.now().isoformat(),
            "content": """
Tech Lead: We need to understand your security posture.
Rep: We're SOC 2 Type II certified with AES-256 encryption.
Tech Lead: What about API capabilities?
Rep: Full REST API with webhook support. Most integrations done in a week.
Tech Lead: Can you guarantee US data residency?
Rep: Absolutely. We offer US-only hosting and private cloud deployment.
Tech Lead: Good. Send over your architecture docs and we'll do a security review.
Rep: I'll have those to you by end of day.
            """,
            "expected_extraction": {
                "requirements": ["SOC 2 Type II", "API", "US data residency"],
                "next_steps": ["Send architecture docs", "Security review"],
                "technical_fit": "high"
            }
        },
        {
            "id": 3,
            "title": "Healthcare Closing Call",
            "date": datetime.now().isoformat(),
            "content": """
Decision Maker: We've made our decision - you're our choice.
Rep: Fantastic! What sealed the deal?
Decision Maker: The ROI is compelling - 20 hours saved per rep at $50/hour is $1000 weekly.
Rep: That's exactly right. With 50 reps, you're saving $2.6M annually.
Decision Maker: We need the contract by month end for budget approval.
Rep: I'll send it today. Do you prefer annual or quarterly payments?
Decision Maker: Quarterly works better for our cash flow.
Rep: Perfect. I'll include our implementation timeline - typically 2-3 weeks.
            """,
            "expected_extraction": {
                "stage": "Closed Won",
                "contract_terms": "Quarterly payments",
                "timeline": "month end",
                "roi_calculation": "$2.6M annual savings",
                "implementation": "2-3 weeks"
            }
        }
    ]

    # Save test data
    test_data = {
        "accounts": accounts,
        "deals": deals,
        "transcripts": transcripts,
        "generated_at": datetime.now().isoformat()
    }

    with open("test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)

    print("✅ Generated test data:")
    print(f"   - {len(accounts)} accounts")
    print(f"   - {len(deals)} deals")
    print(f"   - {len(transcripts)} transcripts")
    print("\n📁 Saved to test_data.json")

    return test_data

if __name__ == "__main__":
    generate_test_data()
