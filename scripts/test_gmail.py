#!/usr/bin/env python3
"""
Test script for Gmail integration
Run this to verify Gmail OAuth and basic functionality
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gmail_client import GmailClient
from email_analyzer import EmailAnalyzer

def test_gmail_auth():
    """Test Gmail authentication"""
    print("🔐 Testing Gmail Authentication...")
    print("-" * 50)

    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            print("❌ Error: credentials.json not found!")
            print("Please ensure credentials.json is in the current directory")
            return False

        # Initialize Gmail client
        gmail = GmailClient()
        print("✅ Gmail client initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False

def test_read_emails():
    """Test reading emails"""
    print("\n📧 Testing Email Reading...")
    print("-" * 50)

    try:
        gmail = GmailClient()
        emails = gmail.get_unread_emails(max_results=5)

        if not emails:
            print("No unread emails found.")
            print("Send a test email to your Gmail account and try again.")
        else:
            print(f"Found {len(emails)} unread emails:\n")

            for i, email in enumerate(emails, 1):
                print(f"Email {i}:")
                print(f"  From: {email['from']}")
                print(f"  Subject: {email['subject']}")
                print(f"  Preview: {email['body'][:100]}...")
                print()

        return True

    except Exception as e:
        print(f"❌ Failed to read emails: {str(e)}")
        return False

def test_email_analysis():
    """Test email analysis for buying signals"""
    print("\n🤖 Testing Email Analysis...")
    print("-" * 50)

    # Test with sample emails
    test_emails = [
        {
            'id': 'test1',
            'from': 'john@techcorp.com',
            'subject': 'Interested in your sales platform',
            'body': 'Hi, We are looking to buy a sales enablement solution for our team of 50 reps. Can you send pricing information and schedule a demo? We need to make a decision by end of month.'
        },
        {
            'id': 'test2',
            'from': 'sarah@startup.com',
            'subject': 'Following up on our conversation',
            'body': 'Thanks for the call yesterday. We are exploring options but the pricing seems too expensive for our small team. We might need to think about it more.'
        }
    ]

    analyzer = EmailAnalyzer()

    for email in test_emails:
        print(f"\nAnalyzing email from {email['from']}...")
        analysis = analyzer.analyze_email(email)

        print(f"  Intent Level: {analysis['intent_level']} (Score: {analysis['signal_score']})")
        print(f"  Key Points: {', '.join(analysis['key_points'][:3])}")

        if analysis['questions']:
            print(f"  Questions Detected: {len(analysis['questions'])}")

        if analysis['objections']:
            print(f"  Objections: {', '.join(analysis['objections'])}")

        print(f"\n  Suggested Response:")
        print(f"  {analysis['response_suggestion'][:150]}...")

        print(f"\n  Next Steps:")
        for step in analysis['next_steps'][:3]:
            print(f"    • {step}")

    return True

def test_response_generation():
    """Test AI response generation"""
    print("\n✍️  Testing Response Generation...")
    print("-" * 50)

    analyzer = EmailAnalyzer()

    # High intent email
    high_intent_email = {
        'id': 'test_high',
        'from': 'buyer@enterprise.com',
        'subject': 'Ready to purchase your solution',
        'body': 'We have budget approved and need to implement a sales platform by Q1. Can we schedule a demo this week? Also need pricing for 100 users.'
    }

    analysis = analyzer.analyze_email(high_intent_email)
    response = analyzer.generate_email_response(analysis)

    print("Generated Response for High Intent Email:")
    print("-" * 30)
    print(response)
    print("-" * 30)

    return True

def main():
    """Run all tests"""
    print("\n🚀 Gmail Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Authentication", test_gmail_auth),
        ("Read Emails", test_read_emails),
        ("Email Analysis", test_email_analysis),
        ("Response Generation", test_response_generation)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 50)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Gmail integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
