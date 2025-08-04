#!/usr/bin/env python3

import json
import sqlite3
from datetime import datetime, timedelta

def create_story_driven_data():
    # Jennifer's company journey
    jennifer_account = {
        "id": 1,
        "name": "DataTech Solutions",
        "industry": "Technology", 
        "revenue": 50000000,
        "employees": 200,
        "email": "jennifer.smith@datatech.com",
        "pain_points": "Manual CRM processes, 3 hours daily per rep",
        "decision_maker": "Jennifer Smith - VP Sales",
        "created_date": datetime.now().isoformat()
    }

    # Deal progression following the story
    jennifer_deals = [
        {
            "id": 1,
            "title": "DataTech Enterprise Platform",
            "account_id": 1,
            "value": 1000000,
            "stage": "Closed Won",
            "probability": 1.0,
            "close_date": datetime.now().isoformat(),
            "created_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "notes": "Discovery → Technical → Closing. Quarterly billing preferred.",
            "source": "AI Transcript Processing",
            "rep_name": "Sarah Johnson"
        }
    ]

    # Supporting accounts and deals for dashboard richness
    additional_accounts = [
        {
            "id": 2,
            "name": "HealthCare Innovations",
            "industry": "Healthcare",
            "revenue": 30000000,
            "employees": 150,
            "email": "procurement@healthinnovate.com",
            "pain_points": "Compliance tracking, manual reporting",
            "decision_maker": "Dr. Michael Chen - CTO"
        },
        {
            "id": 3, 
            "name": "Global Finance Corp",
            "industry": "Financial Services",
            "revenue": 100000000,
            "employees": 500,
            "email": "it@globalfinance.com",
            "pain_points": "Data silos, regulatory reporting",
            "decision_maker": "Lisa Rodriguez - Head of Operations"
        }
    ]

    additional_deals = [
        {
            "id": 2,
            "title": "HealthCare Compliance Suite",
            "account_id": 2,
            "value": 450000,
            "stage": "Proposal",
            "probability": 0.75,
            "close_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "notes": "Technical demo completed, pricing under review",
            "source": "Inbound Lead",
            "rep_name": "Mike Thompson"
        },
        {
            "id": 3,
            "title": "Global Finance Analytics",
            "account_id": 3,
            "value": 850000,
            "stage": "Negotiation",
            "probability": 0.80,
            "close_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "notes": "Contract under legal review, quarterly billing agreed",
            "source": "Referral",
            "rep_name": "Jennifer Davis"
        }
    ]

    # Combine all data
    all_accounts = [jennifer_account] + additional_accounts
    all_deals = jennifer_deals + additional_deals

    # Create transcripts that tell the Jennifer story
    transcripts = [
        {
            "id": 1,
            "title": "DataTech Discovery Call",
            "account_id": 1,
            "deal_id": 1,
            "date": (datetime.now() - timedelta(days=30)).isoformat(),
            "stage": "discovery",
            "content": '''Rep: Hi Jennifer, thanks for taking the call. What's driving your interest?

Jennifer: We're drowning in manual processes. Our 200 sales reps spend hours updating Salesforce.

Rep: How much time per rep daily?

Jennifer: At least 2-3 hours. We need something before Q4 - within 90 days.

Rep: Budget range?

Jennifer: For the right solution, $800,000 to $1.2M annually.

Rep: That's $10.4M in productivity gains. Can we schedule a technical demo?

Jennifer: Absolutely.''',
            "ai_extraction": {
                "entities": {
                    "contact_name": "Jennifer",
                    "company_size": "200 sales reps",
                    "timeline": "90 days",
                    "budget_min": 800000,
                    "budget_max": 1200000
                },
                "deal_score": 92,
                "stage": "qualification",
                "probability": 0.85
            }
        }
    ]

    return {
        "accounts": all_accounts,
        "deals": all_deals, 
        "transcripts": transcripts,
        "story_summary": {
            "total_pipeline_value": sum(d["value"] for d in all_deals),
            "weighted_forecast": sum(d["value"] * d["probability"] for d in all_deals),
            "win_rate": len([d for d in all_deals if d["stage"] == "Closed Won"]) / len(all_deals),
            "avg_deal_size": sum(d["value"] for d in all_deals) / len(all_deals)
        }
    }

if __name__ == "__main__":
    print("📖 Generating story-driven demo data...")
    data = create_story_driven_data()

    with open("story_demo_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Generated complete story data:")
    print(f"   - {len(data['accounts'])} accounts")
    print(f"   - {len(data['deals'])} deals")
    print(f"   - Pipeline: ${data['story_summary']['total_pipeline_value']:,}")
    print(f"   - Forecast: ${data['story_summary']['weighted_forecast']:,.0f}")
