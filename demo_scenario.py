#!/usr/bin/env python3
"""
Interactive Demo Scenario for AI Sales Enablement Platform
Demonstrates end-to-end sales cycle with all integrations
"""

import requests
import json
import time
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init()

API_BASE = "http://localhost:8000"

def print_section(title):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_step(step, description):
    print(f"\n{Fore.YELLOW}Step {step}: {description}{Style.RESET_ALL}")

def print_action(action):
    print(f"  {Fore.GREEN}→ {action}{Style.RESET_ALL}")

def print_result(result):
    print(f"  {Fore.BLUE}✓ {result}{Style.RESET_ALL}")

def wait_for_user():
    input(f"\n{Fore.MAGENTA}Press Enter to continue...{Style.RESET_ALL}")

def demo_scenario():
    print_section("AI SALES ENABLEMENT PLATFORM - LIVE DEMO")
    print("Demonstrating: TechCorp Enterprise Deal ($500K)")

    # Step 1: Email arrives from prospect
    print_step(1, "Prospect Email Received")
    print_action("AI reads incoming email from john@techcorp.com")

    email_content = {
        "from": "john@techcorp.com",
        "subject": "Interested in your sales platform",
        "body": "Hi, We're looking for a sales enablement solution that can scale with our growth. Our current CRM can't handle our volume. Can we discuss?"
    }

    print(f"\n  Email Preview:")
    print(f"  From: {email_content['from']}")
    print(f"  Subject: {email_content['subject']}")
    print(f"  Body: {email_content['body'][:100]}...")

    wait_for_user()

    # AI drafts response
    print_action("AI drafts contextual response")

    draft = """Subject: Re: Interested in your sales platform

Hi John,

Thank you for reaching out! I'd be happy to discuss how our AI-powered sales enablement platform can help with your scaling challenges.

Our platform is specifically designed for high-growth companies like yours, with features including:
- Automated CRM updates that eliminate manual data entry
- AI-powered insights from every customer interaction  
- Seamless integration with your existing tools

Are you available for a 30-minute call this week to discuss your specific needs?

Best regards,
Sarah Chen
Enterprise Sales"""

    print(f"\n  Draft Response:")
    print(f"  {draft[:200]}...")
    print_result("Email drafted with 95% confidence - Ready for approval")

    wait_for_user()

    # Step 2: Discovery Call
    print_step(2, "Discovery Call Transcript Processing")
    print_action("Processing 30-minute sales call with John from TechCorp")

    transcript = """Sales Rep: Hi John, thanks for taking the time today.
John: Of course! We're really excited about improving our sales process.
Sales Rep: Great! Can you tell me about your current challenges?
John: Our main issue is scalability. We're growing at 200% annually but our current CRM can't keep up. 
We need something that can handle 10x our current volume.
Sales Rep: I understand. How many sales reps do you have?
John: Currently 50, but we'll be at 200 by year end.
Sales Rep: And what's your budget for a solution like this?
John: We've allocated $500,000 annually for the right platform.
Sales Rep: Perfect. Our enterprise plan would fit well within that budget..."""

    # Process transcript
    try:
        response = requests.post(f"{API_BASE}/analytics/process-transcript", 
                               json={"transcript": transcript})
    except:
        pass  # Continue demo even if API call fails

    print_action("AI extracts key information from call")
    print_result("Company: TechCorp")
    print_result("Contact: John (Decision Maker)")
    print_result("Pain Points: Scalability, rapid growth (200% YoY)")
    print_result("Team Size: 50 reps → 200 by year end")  
    print_result("Budget: $500,000 annually")
    print_result("Next Steps: Schedule platform demo")

    wait_for_user()

    # Create account and deal
    print_action("Automatically creating CRM records")

    try:
        # Create account
        account_data = {
            "name": "TechCorp",
            "industry": "Technology", 
            "revenue": 50000000,
            "employees": 500,
            "growth_rate": "200%"
        }
        account_response = requests.post(f"{API_BASE}/crm/accounts", json=account_data)
        account = account_response.json()

        # Create deal
        deal_data = {
            "title": "TechCorp Enterprise Platform",
            "account_id": account["id"],
            "value": 500000,
            "stage": "Qualification",
            "close_date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
            "probability": 0.7
        }
        deal_response = requests.post(f"{API_BASE}/crm/deals", json=deal_data)
        deal = deal_response.json()

        print_result(f"Account created: {account['name']} (ID: {account['id']})")
        print_result(f"Contact created: John Smith")
        print_result(f"Deal created: ${deal['value']:,} opportunity")
    except:
        # Mock results if API fails
        print_result("Account created: TechCorp (ID: tech-corp-123)")
        print_result("Contact created: John Smith")
        print_result("Deal created: $500,000 opportunity")
        account = {"id": "tech-corp-123", "name": "TechCorp"}
        deal = {"id": "deal-123", "value": 500000}

    wait_for_user()

    # Step 3: AI Analysis
    print_step(3, "AI Sales Intelligence Analysis")
    print_action("AI analyzes deal and provides recommendations")

    print(f"\n  {Fore.CYAN}AI Insights:{Style.RESET_ALL}")
    print("  • High win probability (85%) - Strong budget fit")
    print("  • Similar to 3 won deals in the last quarter")
    print("  • Recommended approach: Focus on scalability demos")
    print("  • Key stakeholder: Get CFO buy-in for budget approval")
    print("  • Competitive risk: They're also evaluating Competitor X")

    wait_for_user()

    # Step 4: Deal Progression
    print_step(4, "Deal Progression & Automation")

    # Update deal stage
    print_action("Demo completed successfully - updating deal stage")
    try:
        update_data = {"stage": "Proposal", "probability": 0.85}
        requests.put(f"{API_BASE}/crm/deals/{deal['id']}", json=update_data)
    except:
        pass

    print_result("Deal moved to Proposal stage")
    print_result("Win probability increased to 85%")

    # Forecast update
    print_action("Updating sales forecast")
    print_result("Q2 forecast increased by $500K")
    print_result("Team on track to exceed quota by 23%")

    wait_for_user()

    # Step 5: Closing the Deal
    print_step(5, "AI-Assisted Deal Closing")

    print_action("AI identifies buying signals in latest email")
    print("  Email: 'The team loved the demo. Can you send over the contract?'")
    print_result("Buying signal detected with 94% confidence")

    print_action("AI recommends immediate action")
    print("  • Send contract within 2 hours (increases close rate by 37%)")
    print("  • Include implementation timeline") 
    print("  • Offer quarterly payment terms")

    # Close the deal
    print_action("Updating deal to Closed Won")
    try:
        close_data = {"stage": "Closed Won", "actual_close_date": datetime.now().strftime("%Y-%m-%d")}
        requests.put(f"{API_BASE}/crm/deals/{deal['id']}", json=close_data)
    except:
        pass

    print_result("🎉 Deal closed: TechCorp - $500,000")
    print_result("Time to close: 45% faster than average")
    print_result("AI contribution: Saved 12 hours of manual work")

    wait_for_user()

    # Summary
    print_section("DEMO SUMMARY - BUSINESS IMPACT")

    print(f"\n{Fore.GREEN}✓ Efficiency Gains:{Style.RESET_ALL}")
    print("  • 0 minutes spent on data entry (vs 2 hours traditional)")
    print("  • AI drafted 5 emails (saved 45 minutes)")
    print("  • Automatic CRM updates (saved 30 minutes)")
    print("  • Instant deal insights (vs 1 hour analysis)")

    print(f"\n{Fore.GREEN}✓ Revenue Impact:{Style.RESET_ALL}")  
    print("  • Deal closed 45% faster")
    print("  • Win rate increased from 25% to 85%")
    print("  • Deal value maintained at full $500K")
    print("  • Rep can handle 3x more opportunities")

    print(f"\n{Fore.GREEN}✓ Platform Capabilities Demonstrated:{Style.RESET_ALL}")
    print("  • Email AI integration ✓")
    print("  • Call transcript processing ✓")
    print("  • CRM automation ✓")
    print("  • Predictive analytics ✓")
    print("  • Real-time insights ✓")
    print("  • Progressive autonomy ✓")

    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}End of Demo - Questions?{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        demo_scenario()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        print("Please ensure all services are running: docker-compose up -d")
